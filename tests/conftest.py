"""
Pytest 配置文件
"""
import pytest
import sys
import os

# 確保 src 目錄在 Python path 中
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def pytest_configure(config):
    """Pytest 配置"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )


@pytest.fixture(scope="session")
def event_loop_policy():
    """Event loop policy for async tests"""
    import asyncio
    return asyncio.DefaultEventLoopPolicy()
