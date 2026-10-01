import asyncio
from datetime import datetime
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import uuid

import bcrypt
import httpx2
from pydantic import SecretStr
import pytest
import yaml

from app.config.settings import settings
from app.data.database import Database
from app.mcp.client import McpClient, McpClientRequestError
from app.mcp.server import create_mcp_server


pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_GATEWAY_TESTS") != "1",
    reason="Set RUN_GATEWAY_TESTS=1 to run the real Docker gateway integration test",
)

ROOT = Path(__file__).resolve().parents[2]
IMAGE = "ghcr.io/agentgateway/agentgateway:v1.5.0"


def unused_port():
    with socket.socket() as connection:
        connection.bind(("127.0.0.1", 0))
        return connection.getsockname()[1]


@pytest.fixture
def gateway(tmp_path, monkeypatch):
    backend_port = unused_port()
    gateway_port = unused_port()
    database = Database(str(tmp_path / "synthetic.db"))
    database.initialize_schema()
    database.seed_data()
    database.close()
    password = uuid.uuid4().hex
    htpasswd = tmp_path / "htpasswd"
    htpasswd.write_text(
        "investigation:" + bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode() + "\n"
    )
    htpasswd.chmod(0o644)
    config = yaml.safe_load((ROOT / "agentgateway.yaml").read_text())
    config["gateways"]["financial"]["port"] = gateway_port
    config["mcp"]["targets"][0]["mcp"]["host"] = f"http://127.0.0.1:{backend_port}/mcp"
    config_path = tmp_path / "gateway.yaml"
    config_path.write_text(yaml.safe_dump(config))
    config_path.chmod(0o644)
    container = "financial-mcp-test-" + uuid.uuid4().hex
    environment = {
        **os.environ,
        "DATABASE_PATH": database.db_path,
        "MCP_TRANSPORT": "in-process",
        "MCP_SERVER_HOST": "127.0.0.1",
        "MCP_SERVER_PORT": str(backend_port),
    }
    backend = subprocess.Popen(
        [sys.executable, "-c", """
from app.mcp.server import create_mcp_server
from app.config.settings import settings
server = create_mcp_server()
@server.tool()
async def policy_probe() -> dict[str, bool]:
    return {"available": True}
server.run(transport="streamable-http", host=settings.mcp_server_host, port=settings.mcp_server_port)
"""],
        cwd=ROOT,
        env=environment,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        subprocess.run(
            [
                "docker", "run", "--detach", "--rm", "--network", "host",
                "--name", container,
                "--mount", f"type=bind,src={config_path},dst=/etc/gateway.yaml,readonly",
                "--mount", f"type=bind,src={htpasswd},dst=/run/secrets/agentgateway_htpasswd,readonly",
                IMAGE, "-f", "/etc/gateway.yaml",
            ],
            check=True, capture_output=True, text=True, timeout=60,
        )
        monkeypatch.setattr(settings, "mcp_transport", "gateway")
        monkeypatch.setattr(settings, "mcp_gateway_url", f"http://127.0.0.1:{gateway_port}/mcp")
        monkeypatch.setattr(settings, "mcp_gateway_username", "investigation")
        monkeypatch.setattr(settings, "mcp_gateway_password", SecretStr(password))
        yield database, container, backend_port
    finally:
        subprocess.run(
            ["docker", "rm", "--force", container],
            capture_output=True, timeout=30,
        )
        backend.terminate()
        try:
            backend.wait(timeout=10)
        except subprocess.TimeoutExpired:
            backend.kill()
            backend.wait(timeout=10)
        database.close()


@pytest.mark.asyncio
async def test_gateway_evidence_auth_and_outage(gateway, monkeypatch):
    database, container, backend_port = gateway
    deadline = time.monotonic() + 30
    async with httpx2.AsyncClient(timeout=1, trust_env=False) as http_client:
        while True:
            try:
                response = await http_client.get(str(settings.mcp_gateway_url))
                backend_response = await http_client.get(f"http://127.0.0.1:{backend_port}/mcp")
                if response.status_code == 401 and backend_response.status_code < 500:
                    break
            except httpx2.HTTPError:
                pass
            if time.monotonic() >= deadline:
                pytest.fail("Gateway/backend did not become ready within 30 seconds")
            await asyncio.sleep(0.1)

        response = await http_client.get(
            str(settings.mcp_gateway_url), auth=("investigation", "invalid-test-password")
        )
        assert response.status_code == 401

    as_of = datetime(2025, 1, 1)
    async with McpClient(f"http://127.0.0.1:{backend_port}/mcp") as backend_client:
        assert await backend_client.call_tool("policy_probe", {}) == {"available": True}
    calls = [
        ("get_customer", {"customer_id": "CUST-001"}),
        ("get_account", {"account_id": "ACC-1001"}),
        ("get_transactions", {"account_id": "ACC-1001", "as_of": as_of.isoformat()}),
        ("get_ledger_entries", {"account_id": "ACC-1001", "as_of": as_of.isoformat()}),
        ("compare_account_balance", {"account_id": "ACC-1001", "as_of": as_of.isoformat()}),
    ]
    async with McpClient(create_mcp_server(database)) as direct:
        expected = [await direct.call_tool(name, arguments) for name, arguments in calls]
    retries = []
    async with McpClient(on_retry=lambda *event: retries.append(event)) as proxied:
        assert {tool["name"] for tool in await proxied.list_tools()} == {
            name for name, _ in calls
        }
        for (name, arguments), result in zip(calls, expected):
            assert await proxied.call_tool(name, arguments) == result
        with pytest.raises(McpClientRequestError):
            await proxied.call_tool("policy_probe", {})
        assert retries == []

    subprocess.run(["docker", "stop", container], check=True, capture_output=True, timeout=30)

    def unexpected_local_server():
        pytest.fail("Gateway outage triggered local fallback")

    monkeypatch.setattr("app.mcp.client.create_mcp_server", unexpected_local_server)
    with pytest.raises(BaseExceptionGroup) as failure:
        async with McpClient(max_retries=0, read_timeout_seconds=2):
            pytest.fail("Unavailable gateway unexpectedly connected")
    assert failure.value.subgroup(httpx2.ConnectError) is not None


@pytest.mark.skipif(
    os.environ.get("RUN_COMPOSE_TESTS") != "1",
    reason="Set RUN_COMPOSE_TESTS=1 after building the application image",
)
def test_compose_private_backend_and_read_only_database(tmp_path):
    project = "financial-compose-test-" + uuid.uuid4().hex
    password = uuid.uuid4().hex
    htpasswd = tmp_path / "htpasswd"
    htpasswd.write_text(
        "investigation:" + bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode() + "\n"
    )
    htpasswd.chmod(0o644)
    config = yaml.safe_load((ROOT / "docker-compose.yml").read_text())
    del config["services"]["frontend"]
    for service in config["services"].values():
        service.pop("build", None)
        service.pop("container_name", None)
        service.pop("env_file", None)
        service.pop("ports", None)
        service["restart"] = "no"
    config["services"]["api"]["environment"]["MCP_GATEWAY_PASSWORD"] = password
    config["services"]["agentgateway"]["volumes"] = [
        f"{ROOT / 'agentgateway.yaml'}:/etc/agentgateway/config.yaml:ro"
    ]
    config["secrets"]["agentgateway_htpasswd"]["file"] = str(htpasswd)
    config["volumes"]["banking-data"]["name"] = project + "-data"
    config_path = tmp_path / "compose.yaml"
    config_path.write_text(yaml.safe_dump(config))
    config_path.chmod(0o600)
    compose = ["docker", "compose", "--project-name", project, "--file", str(config_path)]
    try:
        startup = subprocess.run(
            [*compose, "up", "--detach", "--wait", "--wait-timeout", "90", "--no-build"],
            capture_output=True, text=True, timeout=150,
        )
        assert startup.returncode == 0, startup.stderr
        result = subprocess.run(
            [*compose, "exec", "-T", "api", "python", "-c", """
import asyncio
from app.mcp.client import McpClient
async def verify():
    async with McpClient() as client:
        assert len(await client.list_tools()) == 5
        assert (await client.get_account('ACC-1001'))['account_id'] == 'ACC-1001'
asyncio.run(verify())
print('Compose gateway discovery and account evidence passed')
"""],
            capture_output=True, text=True, timeout=45,
        )
        if result.returncode != 0:
            backend_logs = subprocess.run(
                [*compose, "logs", "--no-color", "--tail", "60", "mcp"],
                capture_output=True, text=True, timeout=15,
            )
            pytest.fail(result.stderr + backend_logs.stdout)
        result = subprocess.run(
            [*compose, "exec", "-T", "mcp", "python", "-c", """
import sqlite3
from app.data.database import db
try:
    db.connect().execute('CREATE TABLE forbidden_write (value TEXT)')
except sqlite3.OperationalError as error:
    assert 'readonly' in str(error).lower()
else:
    raise AssertionError('MCP database mount is writable')
print('Read-only database mount enforced')
"""],
            capture_output=True, text=True, timeout=15,
        )
        assert result.returncode == 0, result.stderr
        api_networks = set(config["services"]["api"]["networks"])
        backend_networks = set(config["services"]["mcp"]["networks"])
        assert api_networks.isdisjoint(backend_networks)
        assert config["networks"]["mcp-backend"]["internal"] is True
    finally:
        subprocess.run(
            [*compose, "down", "--volumes", "--remove-orphans"],
            capture_output=True, timeout=60,
        )