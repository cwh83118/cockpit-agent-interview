"""
整合測試案例

這些測試驗證 System 1 和 System 2 的整合功能，包括：
- 任務分派流程
- 狀態查詢
- 並發處理

使用方式：
    pytest tests/test_integration.py -v
"""
import pytest
import time
import threading
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models import Task, TaskStatus, TaskType, TaskStep

# 嘗試導入考生的實作
try:
    from system1 import System1
    from system2 import System2
    from communication import CommunicationChannel
    IMPLEMENTATION_EXISTS = True
except ImportError:
    IMPLEMENTATION_EXISTS = False


@pytest.mark.skipif(not IMPLEMENTATION_EXISTS, reason="尚未實作 System1/System2")
class TestTaskDispatch:
    """任務分派測試"""

    @pytest.fixture
    def systems(self):
        """建立整合測試環境"""
        channel = CommunicationChannel()
        s1 = System1(channel=channel)
        s2 = System2(channel=channel)
        return s1, s2, channel

    def test_dispatch_complex_task(self, systems):
        """
        測試複雜任務分派

        System 1 應該能識別複雜任務並分派給 System 2。
        """
        s1, s2, channel = systems

        # 啟動 System 2 的任務處理（背景）
        s2_thread = threading.Thread(target=s2.start_processing, daemon=True)
        s2_thread.start()

        # System 1 處理一個複雜請求
        response = s1.process_input("幫我規劃先送小孩上學再去公司的路線")

        # 應該有任務被建立
        time.sleep(0.5)  # 給一點時間讓任務被處理
        tasks = s2.get_all_tasks()
        assert len(tasks) >= 1, "System 2 應該收到至少一個任務"

    def test_status_query_during_execution(self, systems):
        """
        測試執行中的狀態查詢

        在 System 2 執行任務時，System 1 應該能查詢到正確的狀態。
        """
        s1, s2, channel = systems

        # 建立一個有多步驟的任務
        task = Task(
            type=TaskType.ROUTE_PLANNING,
            description="測試任務",
            steps=[
                TaskStep(name="步驟1", description=""),
                TaskStep(name="步驟2", description=""),
                TaskStep(name="步驟3", description=""),
            ]
        )

        # 分派任務
        task_id = s1.dispatch_task(task)

        # 啟動 System 2 處理
        s2_thread = threading.Thread(target=s2.start_processing, daemon=True)
        s2_thread.start()

        # 等待一下讓任務開始執行
        time.sleep(0.5)

        # 查詢狀態
        status = s1.get_task_status(task_id)
        assert status is not None


@pytest.mark.skipif(not IMPLEMENTATION_EXISTS, reason="尚未實作 System1/System2")
class TestConcurrency:
    """並發測試"""

    @pytest.fixture
    def systems(self):
        """建立整合測試環境"""
        channel = CommunicationChannel()
        s1 = System1(channel=channel)
        s2 = System2(channel=channel)
        return s1, s2, channel

    def test_multiple_concurrent_queries(self, systems):
        """
        測試多個並發查詢

        System 1 應該能同時處理多個使用者查詢。
        """
        s1, s2, channel = systems

        results = []
        errors = []

        def make_query(query: str):
            try:
                response = s1.process_input(query)
                results.append(response)
            except Exception as e:
                errors.append(e)

        # 同時發送多個查詢
        threads = []
        queries = [
            "今天天氣如何？",
            "1+1等於多少？",
            "現在幾點？",
            "你好嗎？",
        ]

        for q in queries:
            t = threading.Thread(target=make_query, args=(q,))
            threads.append(t)
            t.start()

        # 等待所有查詢完成
        for t in threads:
            t.join(timeout=5.0)

        # 驗證結果
        assert len(errors) == 0, f"發生錯誤: {errors}"
        assert len(results) == len(queries), "應該收到所有查詢的回應"

    def test_query_during_background_task(self, systems):
        """
        測試背景任務執行時的查詢能力

        這是最核心的測試：當 System 2 在執行複雜任務時，
        System 1 必須仍然能夠回應使用者的簡單問題。
        """
        s1, s2, channel = systems

        # 啟動 System 2
        s2_thread = threading.Thread(target=s2.start_processing, daemon=True)
        s2_thread.start()

        # 1. 先分派一個複雜任務（會在背景執行）
        response1 = s1.process_input("幫我規劃環島旅行路線，包含所有縣市")
        assert response1 is not None

        # 2. 在任務執行期間，進行多次簡單查詢
        response_times = []
        for i in range(5):
            start = time.time()
            response = s1.process_input(f"簡單問題 {i}")
            elapsed = time.time() - start
            response_times.append(elapsed)
            assert response is not None
            assert elapsed < 1.0, f"第 {i} 次查詢回應過慢: {elapsed:.2f}s"

        # 3. 查詢任務狀態
        response3 = s1.process_input("任務進度如何？")
        assert response3 is not None

        avg_response_time = sum(response_times) / len(response_times)
        assert avg_response_time < 0.5, f"平均回應時間過長: {avg_response_time:.2f}s"


@pytest.mark.skipif(not IMPLEMENTATION_EXISTS, reason="尚未實作 System1/System2")
class TestTaskLifecycle:
    """任務生命週期測試"""

    @pytest.fixture
    def systems(self):
        channel = CommunicationChannel()
        s1 = System1(channel=channel)
        s2 = System2(channel=channel)
        return s1, s2, channel

    def test_task_completion(self, systems):
        """
        測試任務完成流程

        任務應該從 PENDING -> IN_PROGRESS -> COMPLETED
        """
        s1, s2, channel = systems

        task = Task(
            type=TaskType.SIMPLE_QUERY,  # 使用簡單任務以便快速完成
            description="快速完成的測試任務",
            steps=[
                TaskStep(name="唯一步驟", description=""),
            ]
        )

        # 分派任務
        task_id = s1.dispatch_task(task)

        # 啟動處理
        s2_thread = threading.Thread(target=s2.start_processing, daemon=True)
        s2_thread.start()

        # 等待任務完成（最多 10 秒）
        for _ in range(100):
            status = s1.get_task_status(task_id)
            if status == TaskStatus.COMPLETED:
                break
            time.sleep(0.1)

        final_status = s1.get_task_status(task_id)
        assert final_status == TaskStatus.COMPLETED, f"任務未完成，狀態: {final_status}"

    def test_task_progress_updates(self, systems):
        """
        測試任務進度更新

        應該能追蹤任務的進度變化。
        """
        s1, s2, channel = systems

        task = Task(
            type=TaskType.ROUTE_PLANNING,
            description="多步驟任務",
            steps=[
                TaskStep(name="步驟1", description=""),
                TaskStep(name="步驟2", description=""),
                TaskStep(name="步驟3", description=""),
                TaskStep(name="步驟4", description=""),
            ]
        )

        task_id = s1.dispatch_task(task)

        # 啟動處理
        s2_thread = threading.Thread(target=s2.start_processing, daemon=True)
        s2_thread.start()

        # 追蹤進度變化
        progress_history = []
        for _ in range(50):
            progress = s1.get_task_progress(task_id)
            if progress:
                progress_history.append(progress.get('progress', 0))
            time.sleep(0.1)

            # 如果完成就跳出
            status = s1.get_task_status(task_id)
            if status == TaskStatus.COMPLETED:
                break

        # 進度應該有增加
        assert len(progress_history) > 0, "應該要有進度記錄"
        if len(progress_history) > 1:
            # 進度應該是遞增的（或至少不會減少）
            for i in range(1, len(progress_history)):
                assert progress_history[i] >= progress_history[i-1], "進度不應該減少"
