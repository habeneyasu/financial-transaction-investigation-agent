from unittest.mock import AsyncMock, patch

import pytest
from google.genai.errors import ClientError

from evaluation.agent.run_evaluation import investigate_with_retries


def _client_error(code: int) -> ClientError:
    return ClientError(
        code,
        {"error": {"code": code, "message": "temporary"}},
        None,
    )


@pytest.mark.asyncio
async def test_investigate_with_retries_transient_error():
    agent = AsyncMock()
    expected = object()
    agent.investigate.side_effect = [_client_error(503), expected]

    with patch("evaluation.agent.run_evaluation.asyncio.sleep") as sleep:
        result = await investigate_with_retries(agent, "CASE-001", 3)

    assert result is expected
    assert agent.investigate.await_count == 2
    sleep.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_investigate_with_retries_does_not_retry_bad_request():
    agent = AsyncMock()
    agent.investigate.side_effect = _client_error(400)

    with pytest.raises(ClientError):
        await investigate_with_retries(agent, "CASE-001", 3)

    agent.investigate.assert_awaited_once_with("CASE-001")