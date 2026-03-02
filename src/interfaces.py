"""
介面定義 - 考生需實作這些介面

這個檔案定義了 System 1 和 System 2 必須實作的方法。
考生可以繼承這些 abstract class 或自行實作，但必須符合這些介面規範。
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Callable
from .models import Task, TaskStatus, TaskStep, Message


class System1Interface(ABC):
    """
    System 1 介面定義

    System 1 負責：
    - 與使用者即時對話
    - 判斷任務類型並分派給 System 2
    - 查詢 System 2 的任務狀態
    """

    @abstractmethod
    def process_input(self, user_input: str) -> str:
        """
        處理使用者輸入並回傳回應

        這個方法必須是非阻塞的，即使 System 2 正在執行任務，
        System 1 仍然要能夠回應使用者。

        Args:
            user_input: 使用者的輸入文字

        Returns:
            System 1 的回應文字
        """
        pass

    @abstractmethod
    def dispatch_task(self, task: Task) -> str:
        """
        將任務分派給 System 2

        Args:
            task: 要分派的任務

        Returns:
            任務 ID
        """
        pass

    @abstractmethod
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """
        查詢 System 2 的任務狀態

        Args:
            task_id: 任務 ID

        Returns:
            任務狀態，如果任務不存在則回傳 None
        """
        pass

    @abstractmethod
    def get_task_progress(self, task_id: str) -> Optional[dict]:
        """
        取得任務的詳細進度

        Args:
            task_id: 任務 ID

        Returns:
            包含進度資訊的字典，格式如：
            {
                "task_id": "abc123",
                "status": "in_progress",
                "progress": 0.6,
                "current_step": "規劃路線",
                "completed_steps": ["解析目的地", "查詢位置"],
                "remaining_steps": ["規劃路線", "尋找咖啡店"]
            }
        """
        pass


class System2Interface(ABC):
    """
    System 2 介面定義

    System 2 負責：
    - 接收 System 1 分派的複雜任務
    - 在背景執行多步驟任務
    - 回報任務進度和結果
    """

    @abstractmethod
    def receive_task(self, task: Task) -> bool:
        """
        接收任務

        Args:
            task: 要執行的任務

        Returns:
            是否成功接收任務
        """
        pass

    @abstractmethod
    def execute_task(self, task_id: str) -> None:
        """
        執行任務（背景運行）

        這個方法應該在背景執行，不阻塞調用者。

        Args:
            task_id: 任務 ID
        """
        pass

    @abstractmethod
    def get_status(self, task_id: str) -> Optional[TaskStatus]:
        """
        取得任務狀態

        Args:
            task_id: 任務 ID

        Returns:
            任務狀態，如果任務不存在則回傳 None
        """
        pass

    @abstractmethod
    def get_task(self, task_id: str) -> Optional[Task]:
        """
        取得完整任務資訊

        Args:
            task_id: 任務 ID

        Returns:
            任務物件，如果任務不存在則回傳 None
        """
        pass

    @abstractmethod
    def get_all_tasks(self) -> List[Task]:
        """
        取得所有任務

        Returns:
            所有任務的列表
        """
        pass


class CommunicationInterface(ABC):
    """
    通訊介面定義

    定義 System 1 與 System 2 之間的通訊機制。
    考生可以選擇實作 Queue-based, Event-based, 或其他方式。
    """

    @abstractmethod
    def send_task(self, task: Task) -> bool:
        """
        發送任務 (System 1 -> System 2)

        Args:
            task: 要發送的任務

        Returns:
            是否成功發送
        """
        pass

    @abstractmethod
    def receive_task(self, timeout: Optional[float] = None) -> Optional[Task]:
        """
        接收任務 (System 2 端)

        Args:
            timeout: 超時時間（秒），None 表示阻塞等待

        Returns:
            接收到的任務，超時則回傳 None
        """
        pass

    @abstractmethod
    def send_status_update(self, task_id: str, status: TaskStatus, progress: float) -> bool:
        """
        發送狀態更新 (System 2 -> System 1)

        Args:
            task_id: 任務 ID
            status: 新狀態
            progress: 進度 (0.0 - 1.0)

        Returns:
            是否成功發送
        """
        pass

    @abstractmethod
    def query_status(self, task_id: str) -> Optional[dict]:
        """
        查詢任務狀態 (System 1 端)

        Args:
            task_id: 任務 ID

        Returns:
            狀態資訊字典
        """
        pass
