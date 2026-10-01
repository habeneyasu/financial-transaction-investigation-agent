
import json

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.agent.investigation_agent import InvestigationAgent
from app.mcp.client import McpClient
from app.services.investigation_service import InvestigationService


@pytest.fixture
def investigation_case():
    """Create a minimal investigation case for agent tests."""

    return SimpleNamespace(
        case_id="CASE-001",
        customer_id="CUST-001",
        account_id="ACC-1001",
        complaint="Customer reported a suspicious transaction.",
        submitted_at="2026-08-30T10:00:00+00:00",
        status="OPEN",
    )


@pytest.fixture
def investigation_service(investigation_case):
    """Create a mocked investigation service."""

    service = AsyncMock(
        spec=InvestigationService,
    )

    service.get_investigation_case = (
        lambda case_id: investigation_case
    )

    return service


@pytest.fixture
def llm_client():
    """Create a mocked LLM client returning a valid result."""

    client = AsyncMock()

    client.provider = "test"

    client.generate.return_value = json.dumps(
        {
            "findings": [
                {
                    "description": (
                        "The available evidence indicates "
                        "that the transaction activity is suspicious."
                    ),
                    "evidence": [
                        "The transaction pattern is inconsistent "
                        "with the customer's normal activity."
                    ],
                }
            ],
            "conclusion": (
                "The available evidence indicates that "
                "the transaction activity is suspicious."
            ),
            "confidence": "HIGH",
            "recommendation": (
                "Review the transaction and account activity."
            ),
        }
    )

    return client


@pytest.fixture
def mcp_client():
    """
    Create a mocked MCP client for agent orchestration tests.

    The real McpClient.set_retry_callback() is synchronous.
    Because this test uses a mock instead of a real McpClient,
    explicitly reproduce the callback-registration behavior.
    """

    client = AsyncMock(
        spec=McpClient,
    )

    client.get_customer.return_value = {
        "customer_id": "CUST-001",
        "name": "Test Customer",
    }

    client.get_account.return_value = {
        "account_id": "ACC-1001",
        "customer_id": "CUST-001",
        "balance": 1000.00,
    }

    client.get_transactions.return_value = [
        {
            "transaction_id": "TXN-001",
            "from_account_id": "ACC-2001",
            "to_account_id": "ACC-1001",
            "amount": 500.00,
        }
    ]

    client.get_ledger_entries.return_value = [
        {
            "ledger_id": "LEDGER-001",
            "account_id": "ACC-1001",
            "amount": 500.00,
        }
    ]

    client.compare_account_balance.return_value = {
        "expected_balance": 1000.00,
        "reported_balance": 1000.00,
        "difference": 0.00,
        "consistent": True,
    }

    def set_retry_callback(callback):
        """
        Simulate the real McpClient.set_retry_callback()
        implementation.
        """
        client._on_retry = callback

    client.set_retry_callback.side_effect = set_retry_callback

    return client


@pytest.fixture
def trajectory_dir(monkeypatch, tmp_path):
    """Redirect trajectory output to the pytest temporary directory."""

    monkeypatch.setattr(
        "app.agent.trajectory.TRAJECTORY_DIR",
        tmp_path,
    )

    return tmp_path


@pytest.mark.asyncio
async def test_successful_investigation_does_not_record_mcp_retry(
    investigation_case,
    investigation_service,
    mcp_client,
    llm_client,
    trajectory_dir,
):
    """
    A successful investigation with no MCP failure must not
    contain an mcp_retry trajectory step.
    """

    agent = InvestigationAgent(
        investigation_service=investigation_service,
        mcp_client=mcp_client,
        llm_client=llm_client,
    )

    result = await agent.investigate(
        "CASE-001",
    )

    assert result.case_id == "CASE-001"

    trajectory_file = (
        trajectory_dir
        / "CASE-001.json"
    )

    assert trajectory_file.exists()

    trajectory = json.loads(
        trajectory_file.read_text(
            encoding="utf-8",
        )
    )

    retry_steps = [
        step
        for step in trajectory["steps"]
        if step["step"] == "mcp_retry"
    ]

    assert retry_steps == []

    mcp_client.get_transactions.assert_awaited_once_with(
        "ACC-1001",
        as_of=investigation_case.submitted_at,
    )
    mcp_client.get_ledger_entries.assert_awaited_once_with(
        "ACC-1001",
        as_of=investigation_case.submitted_at,
    )
    mcp_client.compare_account_balance.assert_awaited_once_with(
        "ACC-1001",
        as_of=investigation_case.submitted_at,
    )

    
@pytest.mark.asyncio
async def test_workflow_start_is_recorded_in_trajectory(
    investigation_service,
    mcp_client,
    llm_client,
    trajectory_dir,
):
    """
    Every investigation must record its objective and
    execution instructions at the beginning of the trajectory.
    """

    agent = InvestigationAgent(
        investigation_service=investigation_service,
        mcp_client=mcp_client,
        llm_client=llm_client,
    )

    await agent.investigate(
        "CASE-001",
    )

    trajectory_file = (
        trajectory_dir
        / "CASE-001.json"
    )

    assert trajectory_file.exists()

    trajectory = json.loads(
        trajectory_file.read_text(
            encoding="utf-8",
        )
    )

    assert trajectory["steps"]

    workflow_start = trajectory["steps"][0]

    assert workflow_start["step"] == "workflow_start"

    assert workflow_start["action"] == (
        "Start investigation"
    )

    assert workflow_start["details"]["agent"] == (
        agent.trajectory_agent_name
        if hasattr(agent, "trajectory_agent_name")
        else workflow_start["details"]["agent"]
    )

    assert workflow_start["details"]["objective"] == (
        "Investigate the reported financial transaction issue."
    )

    assert workflow_start["details"]["instructions"] == (
        "Collect relevant case, account, transaction and ledger evidence. "
        "Use deterministic checks where available. "
        "Produce an evidence-backed investigation result. "
        "Do not execute consequential actions without human approval."
    )

    assert workflow_start["details"]["evaluation_case"] is True


@pytest.mark.asyncio
async def test_mcp_retry_is_recorded_in_trajectory(
    investigation_service,
    mcp_client,
    llm_client,
    trajectory_dir,
):
    """
    A genuine MCP retry callback must be recorded in the
    investigation trajectory.
    """

    agent = InvestigationAgent(
        investigation_service=investigation_service,
        mcp_client=mcp_client,
        llm_client=llm_client,
    )

    async def get_customer_with_retry(customer_id):
        """
        Simulate the MCP client notifying the agent that
        an actual retry occurred.

        The real McpClient invokes this callback from its
        retry handling code.
        """

        callback = getattr(
            mcp_client,
            "_on_retry",
            None,
        )

        assert callback is not None
        assert callable(callback)

        callback(
            "get_customer",
            1,
            2,
        )

        return {
            "customer_id": "CUST-001",
            "name": "Test Customer",
        }

    mcp_client.get_customer.side_effect = (
        get_customer_with_retry
    )

    result = await agent.investigate(
        "CASE-001",
    )

    assert result.case_id == "CASE-001"

    trajectory_file = (
        trajectory_dir
        / "CASE-001.json"
    )

    assert trajectory_file.exists()

    trajectory = json.loads(
        trajectory_file.read_text(
            encoding="utf-8",
        )
    )

    retry_steps = [
        step
        for step in trajectory["steps"]
        if step["step"] == "mcp_retry"
    ]

    assert len(retry_steps) == 1

    retry_step = retry_steps[0]

    assert retry_step["step"] == "mcp_retry"

    assert retry_step["action"] == (
        "Retry MCP tool call"
    )

    assert retry_step["details"] == {
        "tool": "get_customer",
        "retry_number": 1,
        "max_retries": 2,
    }


@pytest.mark.asyncio
async def test_multiple_mcp_retries_are_recorded_as_separate_steps(
    investigation_service,
    mcp_client,
    llm_client,
    trajectory_dir,
):
    """
    Each genuine MCP retry event must produce one trajectory
    step, preserving the retry order.
    """

    agent = InvestigationAgent(
        investigation_service=investigation_service,
        mcp_client=mcp_client,
        llm_client=llm_client,
    )

    async def get_customer_with_two_retries(customer_id):
        callback = getattr(
            mcp_client,
            "_on_retry",
            None,
        )

        assert callback is not None
        assert callable(callback)

        callback(
            "get_customer",
            1,
            2,
        )

        callback(
            "get_customer",
            2,
            2,
        )

        return {
            "customer_id": "CUST-001",
            "name": "Test Customer",
        }

    mcp_client.get_customer.side_effect = (
        get_customer_with_two_retries
    )

    result = await agent.investigate(
        "CASE-001",
    )

    assert result.case_id == "CASE-001"

    trajectory_file = (
        trajectory_dir
        / "CASE-001.json"
    )

    assert trajectory_file.exists()

    trajectory = json.loads(
        trajectory_file.read_text(
            encoding="utf-8",
        )
    )

    retry_steps = [
        step
        for step in trajectory["steps"]
        if step["step"] == "mcp_retry"
    ]

    assert len(retry_steps) == 2

    assert retry_steps[0]["details"] == {
        "tool": "get_customer",
        "retry_number": 1,
        "max_retries": 2,
    }

    assert retry_steps[1]["details"] == {
        "tool": "get_customer",
        "retry_number": 2,
        "max_retries": 2,
    }


@pytest.mark.asyncio
async def test_retry_trajectory_step_contains_timestamp(
    investigation_service,
    mcp_client,
    llm_client,
    trajectory_dir,
):
    """
    A retry trajectory event must contain the standard
    trajectory timestamp.
    """

    agent = InvestigationAgent(
        investigation_service=investigation_service,
        mcp_client=mcp_client,
        llm_client=llm_client,
    )

    async def get_customer_with_retry(customer_id):
        callback = getattr(
            mcp_client,
            "_on_retry",
            None,
        )

        assert callback is not None
        assert callable(callback)

        callback(
            "get_customer",
            1,
            2,
        )

        return {
            "customer_id": "CUST-001",
            "name": "Test Customer",
        }

    mcp_client.get_customer.side_effect = (
        get_customer_with_retry
    )

    await agent.investigate(
        "CASE-001",
    )

    trajectory_file = (
        trajectory_dir
        / "CASE-001.json"
    )

    assert trajectory_file.exists()

    trajectory = json.loads(
        trajectory_file.read_text(
            encoding="utf-8",
        )
    )

    retry_steps = [
        step
        for step in trajectory["steps"]
        if step["step"] == "mcp_retry"
    ]

    assert len(retry_steps) == 1

    assert "timestamp" in retry_steps[0]
    assert retry_steps[0]["timestamp"]


@pytest.mark.asyncio
async def test_investigation_requires_mandatory_human_review(
    investigation_service,
    mcp_client,
    llm_client,
    trajectory_dir,
):
    """
    Every completed investigation must require human review
    before any consequential action.
    """

    agent = InvestigationAgent(
        investigation_service=investigation_service,
        mcp_client=mcp_client,
        llm_client=llm_client,
    )

    result = await agent.investigate(
        "CASE-001",
    )

    assert result.requires_human_review is True
    assert result.status == "PENDING_REVIEW"


@pytest.mark.asyncio
async def test_llm_cannot_disable_mandatory_human_review(
    investigation_service,
    mcp_client,
    llm_client,
    trajectory_dir,
):
    """
    Human review is an application-enforced invariant.
    The LLM must not be able to disable it through its output.
    """

    llm_client.generate.return_value = json.dumps(
        {
            "findings": [
                {
                    "description": (
                        "Transaction evidence reviewed."
                    ),
                    "evidence": [
                        "Transaction and ledger records were retrieved."
                    ],
                }
            ],
            "conclusion": (
                "Evidence was reviewed."
            ),
            "confidence": "HIGH",
            "recommendation": (
                "No further action required."
            ),
            "requires_human_review": False,
            "status": "PENDING_REVIEW",
        }
    )

    agent = InvestigationAgent(
        investigation_service=investigation_service,
        mcp_client=mcp_client,
        llm_client=llm_client,
    )

    result = await agent.investigate(
        "CASE-001",
    )

    assert result.requires_human_review is True
    assert result.status == "PENDING_REVIEW"


@pytest.mark.asyncio
async def test_human_checkpoint_is_recorded(
    investigation_service,
    mcp_client,
    llm_client,
    trajectory_dir,
):
    """
    A completed investigation must record a human checkpoint
    before the result is finalized.
    """

    agent = InvestigationAgent(
        investigation_service=investigation_service,
        mcp_client=mcp_client,
        llm_client=llm_client,
    )

    result = await agent.investigate(
        "CASE-001",
    )

    assert result.requires_human_review is True
    assert result.status == "PENDING_REVIEW"

    trajectory_file = (
        trajectory_dir
        / "CASE-001.json"
    )

    assert trajectory_file.exists()

    trajectory = json.loads(
        trajectory_file.read_text(
            encoding="utf-8",
        )
    )

    checkpoint_steps = [
        step
        for step in trajectory["steps"]
        if step["step"] == "human_checkpoint"
    ]

    assert len(checkpoint_steps) == 1

    checkpoint = checkpoint_steps[0]

    assert checkpoint["action"] == (
        "Require mandatory human review"
    )

    assert checkpoint["details"] == {
        "status": "PENDING_REVIEW",
        "requires_human_review": True,
        "approval_received": False,
        "consequential_action_executed": False,
        "message": (
            "Investigation recommendation requires qualified human review "
            "before any consequential action."
        ),
    }

