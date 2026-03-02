"""
範例骨架程式碼 - 供考生參考

這個檔案提供了一個基本的實作骨架。
考生可以參考這個結構來實作自己的版本。

注意：這只是骨架，不是完整實作！
"""
import queue
import threading
import time
from typing import Optional, Dict, List
from models import Task, TaskStatus, TaskType, TaskStep


class CommunicationChannel:
    """
    通訊通道 - 基於 Queue 的實作範例

    TODO: 考生需要完善這個實作
    """

    def __init__(self):
        self.task_queue = queue.Queue()  # System 1 -> System 2
        self.status_store: Dict[str, dict] = {}  # 狀態儲存
        self._lock = threading.Lock()

    def send_task(self, task: Task) -> bool:
        """發送任務到 System 2"""
        try:
            self.task_queue.put(task)
            return True
        except Exception:
            return False

    def receive_task(self, timeout: Optional[float] = None) -> Optional[Task]:
        """System 2 接收任務"""
        try:
            return self.task_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def send_status_update(self, task_id: str, status: TaskStatus, progress: float) -> bool:
        """更新任務狀態"""
        with self._lock:
            self.status_store[task_id] = {
                "status": status,
                "progress": progress,
                "updated_at": time.time()
            }
        return True

    def query_status(self, task_id: str) -> Optional[dict]:
        """查詢任務狀態"""
        with self._lock:
            return self.status_store.get(task_id)


class System1:
    """
    System 1 - 快速回應系統

    TODO: 考生需要完善以下功能：
    1. 判斷使用者意圖（簡單問答 vs 複雜任務）
    2. 分派任務給 System 2
    3. 查詢並回報任務狀態
    """

    def __init__(self, channel: CommunicationChannel = None):
        self.channel = channel or CommunicationChannel()
        self.tasks: Dict[str, Task] = {}

    def process_input(self, user_input: str) -> str:
        """
        處理使用者輸入

        TODO: 實作意圖判斷和對應處理
        """
        # 示例：簡單的關鍵字判斷
        if self._is_complex_task(user_input):
            return self._handle_complex_task(user_input)
        elif self._is_status_query(user_input):
            return self._handle_status_query()
        else:
            return self._handle_simple_query(user_input)

    def _is_complex_task(self, text: str) -> bool:
        """判斷是否為複雜任務"""
        keywords = ["規劃", "路線", "行程", "導航", "找", "搜尋"]
        return any(kw in text for kw in keywords)

    def _is_status_query(self, text: str) -> bool:
        """判斷是否為狀態查詢"""
        keywords = ["進度", "完成", "好了嗎", "狀態", "怎麼樣"]
        return any(kw in text for kw in keywords)

    def _handle_complex_task(self, user_input: str) -> str:
        """處理複雜任務"""
        # TODO: 解析任務並建立步驟
        task = Task(
            type=TaskType.ROUTE_PLANNING,
            description=user_input,
            steps=[
                TaskStep(name="解析目的地", description=""),
                TaskStep(name="查詢位置", description=""),
                TaskStep(name="規劃路線", description=""),
            ]
        )
        task_id = self.dispatch_task(task)
        return f"好的，我來幫您安排。任務編號: {task_id}"

    def _handle_simple_query(self, user_input: str) -> str:
        """處理簡單問答"""
        # TODO: 實作簡單問答邏輯
        return f"收到您的問題：{user_input}"

    def _handle_status_query(self) -> str:
        """處理狀態查詢"""
        # TODO: 查詢所有任務狀態
        if not self.tasks:
            return "目前沒有進行中的任務。"

        status_reports = []
        for task_id, task in self.tasks.items():
            progress = self.get_task_progress(task_id)
            if progress:
                status_reports.append(
                    f"任務 {task_id}: {progress.get('progress', 0)*100:.0f}%"
                )

        return "任務進度：\n" + "\n".join(status_reports)

    def dispatch_task(self, task: Task) -> str:
        """分派任務給 System 2"""
        self.tasks[task.id] = task
        self.channel.send_task(task)
        return task.id

    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """查詢任務狀態"""
        status_info = self.channel.query_status(task_id)
        if status_info:
            return status_info.get("status")
        return None

    def get_task_progress(self, task_id: str) -> Optional[dict]:
        """取得任務詳細進度"""
        return self.channel.query_status(task_id)


class System2:
    """
    System 2 - 背景任務系統

    TODO: 考生需要完善以下功能：
    1. 背景執行多步驟任務
    2. 更新任務進度
    3. 處理任務完成/失敗
    """

    def __init__(self, channel: CommunicationChannel = None):
        self.channel = channel or CommunicationChannel()
        self.tasks: Dict[str, Task] = {}
        self._running = False
        self._executor_thread: Optional[threading.Thread] = None

    def receive_task(self, task: Task) -> bool:
        """接收任務"""
        self.tasks[task.id] = task
        return True

    def start_processing(self):
        """開始處理任務的主迴圈"""
        self._running = True
        while self._running:
            task = self.channel.receive_task(timeout=0.1)
            if task:
                self.receive_task(task)
                self._execute_in_background(task)

    def stop_processing(self):
        """停止處理"""
        self._running = False

    def _execute_in_background(self, task: Task):
        """在背景執行任務"""
        thread = threading.Thread(
            target=self.execute_task,
            args=(task.id,),
            daemon=True
        )
        thread.start()

    def execute_task(self, task_id: str) -> None:
        """執行任務"""
        task = self.tasks.get(task_id)
        if not task:
            return

        task.status = TaskStatus.IN_PROGRESS
        self.channel.send_status_update(task_id, TaskStatus.IN_PROGRESS, 0.0)

        # 執行每個步驟
        for i, step in enumerate(task.steps):
            step.status = TaskStatus.IN_PROGRESS
            progress = i / len(task.steps)
            self.channel.send_status_update(task_id, TaskStatus.IN_PROGRESS, progress)

            # TODO: 實際執行步驟邏輯
            time.sleep(0.5)  # 模擬工作

            step.status = TaskStatus.COMPLETED

        # 任務完成
        task.status = TaskStatus.COMPLETED
        self.channel.send_status_update(task_id, TaskStatus.COMPLETED, 1.0)

    def get_status(self, task_id: str) -> Optional[TaskStatus]:
        """取得任務狀態"""
        task = self.tasks.get(task_id)
        if task:
            return task.status
        return None

    def get_task(self, task_id: str) -> Optional[Task]:
        """取得任務"""
        return self.tasks.get(task_id)

    def get_all_tasks(self) -> List[Task]:
        """取得所有任務"""
        return list(self.tasks.values())


# 如果考生想直接使用這個範例，可以複製這些類別到對應的檔案
# system1.py, system2.py, communication.py
