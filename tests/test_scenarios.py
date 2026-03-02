"""
情境測試案例

這些測試模擬真實的座艙使用情境，驗證系統的整體行為。

使用方式：
    pytest tests/test_scenarios.py -v
"""
import pytest
import time
import threading
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models import Task, TaskStatus, TaskType

# 嘗試導入考生的實作
try:
    from system1 import System1
    from system2 import System2
    from communication import CommunicationChannel
    IMPLEMENTATION_EXISTS = True
except ImportError:
    IMPLEMENTATION_EXISTS = False


@pytest.mark.skipif(not IMPLEMENTATION_EXISTS, reason="尚未實作 System1/System2")
class TestCockpitScenarios:
    """座艙情境測試"""

    @pytest.fixture
    def cockpit(self):
        """建立座艙環境"""
        channel = CommunicationChannel()
        s1 = System1(channel=channel)
        s2 = System2(channel=channel)

        # 啟動 System 2
        s2_thread = threading.Thread(target=s2.start_processing, daemon=True)
        s2_thread.start()

        return s1, s2

    def test_scenario_morning_commute(self, cockpit):
        """
        情境：早晨通勤

        模擬駕駛在早晨的典型對話：
        1. 請求規劃行程（送小孩上學 + 上班 + 買咖啡）
        2. 在等待時詢問天氣
        3. 查詢任務進度
        """
        s1, s2 = cockpit

        # Step 1: 請求複雜行程
        response1 = s1.process_input(
            "我想要先送小孩上學，再去上班，順路幫我買杯咖啡"
        )
        assert response1 is not None
        assert any(keyword in response1 for keyword in ["好的", "安排", "規劃", "OK", "收到"])

        # Step 2: 詢問簡單問題（應該立即回應）
        start_time = time.time()
        response2 = s1.process_input("今天會下雨嗎？")
        elapsed = time.time() - start_time

        assert response2 is not None
        assert elapsed < 1.0, "簡單問題應該快速回應"

        # Step 3: 查詢任務進度
        response3 = s1.process_input("行程規劃好了嗎？")
        assert response3 is not None
        # 回應應該包含進度相關資訊
        assert any(keyword in response3 for keyword in
                   ["進度", "處理中", "完成", "執行", "%", "步驟"])

    def test_scenario_multiple_tasks(self, cockpit):
        """
        情境：多任務處理

        測試系統能否處理多個背景任務。
        """
        s1, s2 = cockpit

        # 分派第一個任務
        response1 = s1.process_input("幫我找最近的加油站")

        # 分派第二個任務
        response2 = s1.process_input("規劃去機場的路線")

        # 兩個任務都應該被接受
        assert response1 is not None
        assert response2 is not None

        # 查詢狀態
        time.sleep(0.5)
        response3 = s1.process_input("有哪些任務在執行？")
        assert response3 is not None

    def test_scenario_interrupt_and_resume(self, cockpit):
        """
        情境：中斷與恢復

        駕駛在任務執行中有緊急問題，然後繼續追蹤原任務。
        """
        s1, s2 = cockpit

        # 開始一個複雜任務
        s1.process_input("規劃從台北到高雄的最佳路線")

        # 緊急問題
        emergency_response = s1.process_input("最近的休息站在哪？")
        assert emergency_response is not None

        # 閒聊
        chat_response = s1.process_input("你覺得今天適合出遊嗎？")
        assert chat_response is not None

        # 回到原任務
        status_response = s1.process_input("路線規劃得怎麼樣了？")
        assert status_response is not None

    def test_scenario_rapid_fire_questions(self, cockpit):
        """
        情境：快速連續問題

        測試系統能否處理快速連續的輸入。
        """
        s1, s2 = cockpit

        questions = [
            "現在幾點？",
            "今天星期幾？",
            "外面溫度多少？",
            "電量還有多少？",
            "下一個交流道多遠？",
        ]

        responses = []
        for q in questions:
            response = s1.process_input(q)
            responses.append(response)

        # 所有問題都應該得到回應
        assert all(r is not None for r in responses)
        assert len(responses) == len(questions)


@pytest.mark.skipif(not IMPLEMENTATION_EXISTS, reason="尚未實作 System1/System2")
class TestEdgeCases:
    """邊界情況測試"""

    @pytest.fixture
    def cockpit(self):
        channel = CommunicationChannel()
        s1 = System1(channel=channel)
        s2 = System2(channel=channel)
        s2_thread = threading.Thread(target=s2.start_processing, daemon=True)
        s2_thread.start()
        return s1, s2

    def test_empty_input(self, cockpit):
        """測試空輸入處理"""
        s1, s2 = cockpit
        response = s1.process_input("")
        # 應該要有某種回應，不應該崩潰
        assert response is not None

    def test_very_long_input(self, cockpit):
        """測試超長輸入處理"""
        s1, s2 = cockpit
        long_input = "請幫我規劃路線" + "，包含很多地點" * 100
        response = s1.process_input(long_input)
        assert response is not None

    def test_special_characters(self, cockpit):
        """測試特殊字元處理"""
        s1, s2 = cockpit
        special_input = "我要去 @#$%^&*() 這個地方！？"
        response = s1.process_input(special_input)
        assert response is not None

    def test_query_nonexistent_task(self, cockpit):
        """測試查詢不存在的任務"""
        s1, s2 = cockpit
        status = s1.get_task_status("nonexistent_task_12345")
        assert status is None

    def test_system_under_load(self, cockpit):
        """測試高負載情況"""
        s1, s2 = cockpit

        # 快速分派多個任務
        for i in range(10):
            s1.process_input(f"任務 {i}: 規劃路線")

        # 系統應該仍然能回應
        response = s1.process_input("你還好嗎？")
        assert response is not None
