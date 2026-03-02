"""
資料模型定義 - 供考生參考使用
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Any
from datetime import datetime
import uuid


class TaskStatus(Enum):
    """任務狀態"""
    PENDING = "pending"          # 等待執行
    IN_PROGRESS = "in_progress"  # 執行中
    COMPLETED = "completed"      # 已完成
    FAILED = "failed"            # 失敗
    CANCELLED = "cancelled"      # 已取消


class TaskType(Enum):
    """任務類型"""
    SIMPLE_QUERY = "simple_query"      # 簡單問答 (System 1 直接處理)
    ROUTE_PLANNING = "route_planning"  # 路線規劃 (System 2 處理)
    SCHEDULE = "schedule"              # 行程安排 (System 2 處理)
    SEARCH = "search"                  # 搜尋附近 (System 2 處理)
    STATUS_QUERY = "status_query"      # 查詢任務狀態 (System 1 處理)


@dataclass
class TaskStep:
    """任務步驟"""
    name: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Any] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class Task:
    """任務定義"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    type: TaskType = TaskType.SIMPLE_QUERY
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    steps: List[TaskStep] = field(default_factory=list)
    result: Optional[Any] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None

    @property
    def progress(self) -> float:
        """計算任務進度 (0.0 - 1.0)"""
        if not self.steps:
            if self.status == TaskStatus.COMPLETED:
                return 1.0
            return 0.0
        completed = sum(1 for s in self.steps if s.status == TaskStatus.COMPLETED)
        return completed / len(self.steps)

    @property
    def progress_percentage(self) -> int:
        """計算任務進度百分比"""
        return int(self.progress * 100)

    @property
    def current_step(self) -> Optional[TaskStep]:
        """取得目前執行中的步驟"""
        for step in self.steps:
            if step.status == TaskStatus.IN_PROGRESS:
                return step
        return None


@dataclass
class Message:
    """對話訊息"""
    role: str  # "user" or "system1" or "system2"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    related_task_id: Optional[str] = None


@dataclass
class TaskEvent:
    """任務事件 (用於系統間通訊)"""
    event_type: str  # "task_created", "task_updated", "task_completed", "task_failed"
    task_id: str
    data: Optional[Any] = None
    timestamp: datetime = field(default_factory=datetime.now)
