import time

import pytest

from app.pipeline.timeout import StatementTimeoutError, run_with_timeout


def test_run_with_timeout_returns_result_when_fast_enough():
    result = run_with_timeout(lambda: 1 + 1, timeout_seconds=2)
    assert result == 2


def test_run_with_timeout_raises_when_too_slow():
    def slow():
        time.sleep(2)
        return "done"

    with pytest.raises(StatementTimeoutError):
        run_with_timeout(slow, timeout_seconds=0.1)
