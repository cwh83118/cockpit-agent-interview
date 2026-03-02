"""
基礎測試案例

這些測試驗證 System 1 和 System 2 的基本功能。
考生的實作必須通過這些測試。

使用方式：
    cd cockpit-agent-interview
    pytest tests/ -v

或執行單一測試：
    pytest tests/test_basic.py::test_system1_simple_query -v
"""
import pytest
import time
import sys
import os

# 添加 src 到 path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models import Task, TaskStatus, TaskType, TaskStep


class TestModels:
    """測試資料模型"""

    def test_task_creation(self):
        """測試任務建立"""
        task = Task(
            type=TaskType.ROUTE_PLANNING,
            description="規劃從家到公司的路線"
        )
        assert task.id is not None
        assert task.status == TaskStatus.PENDING
        assert task.progress == 0.0

    def test_task_progress_calculation(self):
        """測試任務進度計算"""
        task = Task(
            type=TaskType.ROUTE_PLANNING,
            description="測試任務",
            steps=[
                TaskStep(name="步驟1", description="第一步", status=TaskStatus.COMPLETED),
                TaskStep(name="步驟2", description="第二步", status=TaskStatus.COMPLETED),
                TaskStep(name="步驟3", description="第三步", status=TaskStatus.IN_PROGRESS),
                TaskStep(name="步驟4", description="第四步", status=TaskStatus.PENDING),
            ]
        )
        assert task.progress == 0.5
        assert task.progress_percentage == 50

    def test_task_current_step(self):
        """測試取得當前步驟"""
        task = Task(
            type=TaskType.ROUTE_PLANNING,
            steps=[
                TaskStep(name="步驟1", description="", status=TaskStatus.COMPLETED),
                TaskStep(name="步驟2", description="", status=TaskStatus.IN_PROGRESS),
                TaskStep(name="步驟3", description="", status=TaskStatus.PENDING),
            ]
        )
        assert task.current_step is not None
        assert task.current_step.name == "步驟2"


# ============================================================
# 以下測試需要考生實作 System1 和 System2 後才能執行
# 考生需要在 src/ 目錄下建立 system1.py 和 system2.py
# ============================================================

# 嘗試導入考生的實作
try:
    from system1 import System1
    from system2 import System2
    from communication import CommunicationChannel
    IMPLEMENTATION_EXISTS = True
except ImportError:
    IMPLEMENTATION_EXISTS = False


@pytest.mark.skipif(not IMPLEMENTATION_EXISTS, reason="尚未實作 System1/System2")
class TestSystem1Basic:
    """System 1 基礎測試"""

    @pytest.fixture
    def system1(self):
        """建立 System 1 實例"""
        return System1()

    def test_system1_simple_query(self, system1):
        """
        測試 System 1 可以回答簡單問題

        這個測試驗證 System 1 能夠處理不需要 System 2 的簡單問答。
        """
        # 簡單問題應該立即得到回應
        response = system1.process_input("你好")
        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0

    def test_system1_non_blocking(self, system1):
        """
        測試 System 1 是非阻塞的

        即使分派了複雜任務，System 1 仍然要能夠回應新的輸入。
        """
        # 分派一個複雜任務
        response1 = system1.process_input("幫我規劃從台北到高雄的路線")

        # 立即詢問另一個簡單問題
        start_time = time.time()
        response2 = system1.process_input("1+1等於多少？")
        elapsed = time.time() - start_time

        # 應該在 1 秒內回應（非阻塞）
        assert elapsed < 1.0, f"System 1 回應時間過長: {elapsed:.2f}s"
        assert response2 is not None


@pytest.mark.skipif(not IMPLEMENTATION_EXISTS, reason="尚未實作 System1/System2")
class TestSystem2Basic:
    """System 2 基礎測試"""

    @pytest.fixture
    def system2(self):
        """建立 System 2 實例"""
        return System2()

    def test_system2_receive_task(self, system2):
        """測試 System 2 可以接收任務"""
        task = Task(
            type=TaskType.ROUTE_PLANNING,
            description="測試任務"
        )
        result = system2.receive_task(task)
        assert result is True

    def test_system2_get_status(self, system2):
        """測試 System 2 可以回報任務狀態"""
        task = Task(
            type=TaskType.ROUTE_PLANNING,
            description="測試任務"
        )
        system2.receive_task(task)

        status = system2.get_status(task.id)
        assert status is not None
        assert isinstance(status, TaskStatus)

    def test_system2_nonexistent_task(self, system2):
        """測試查詢不存在的任務"""
        status = system2.get_status("nonexistent_id")
        assert status is None


@pytest.mark.skipif(not IMPLEMENTATION_EXISTS, reason="尚未實作 System1/System2")
class TestCommunication:
    """通訊機制測試"""

    @pytest.fixture
    def channel(self):
        """建立通訊通道"""
        return CommunicationChannel()

    def test_send_and_receive_task(self, channel):
        """測試任務發送與接收"""
        task = Task(
            type=TaskType.ROUTE_PLANNING,
            description="通訊測試任務"
        )

        # 發送任務
        send_result = channel.send_task(task)
        assert send_result is True

        # 接收任務
        received = channel.receive_task(timeout=1.0)
        assert received is not None
        assert received.id == task.id
        assert received.description == task.description

    def test_receive_timeout(self, channel):
        """測試接收超時"""
        # 沒有任務時應該超時
        received = channel.receive_task(timeout=0.1)
        assert received is None
