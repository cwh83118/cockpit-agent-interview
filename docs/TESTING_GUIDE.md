# 測試指南

## 快速開始

### 1. 環境設置

```bash
# 進入專案目錄
cd cockpit-agent-interview

# 建立虛擬環境
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 或 venv\Scripts\activate  # Windows

# 安裝依賴
pip install -r requirements.txt
```

### 2. 執行測試

```bash
# 執行所有測試
pytest

# 執行特定測試檔案
pytest tests/test_basic.py

# 執行特定測試類別
pytest tests/test_basic.py::TestModels

# 執行特定測試
pytest tests/test_basic.py::TestModels::test_task_creation

# 顯示詳細輸出
pytest -v

# 顯示 print 輸出
pytest -s

# 組合使用
pytest -vs tests/test_basic.py
```

---

## 測試結構

```
tests/
├── conftest.py           # Pytest 配置
├── test_basic.py         # 基礎測試
│   ├── TestModels        # 資料模型測試
│   ├── TestSystem1Basic  # System 1 基礎測試
│   ├── TestSystem2Basic  # System 2 基礎測試
│   └── TestCommunication # 通訊機制測試
├── test_integration.py   # 整合測試
│   ├── TestTaskDispatch  # 任務分派測試
│   ├── TestConcurrency   # 並發測試
│   └── TestTaskLifecycle # 任務生命週期測試
└── test_scenarios.py     # 情境測試
    ├── TestCockpitScenarios # 座艙情境測試
    └── TestEdgeCases        # 邊界情況測試
```

---

## 測試說明

### 基礎測試 (test_basic.py)

這些測試驗證基本功能是否正確實作。

| 測試 | 說明 | 重點 |
|------|------|------|
| `test_task_creation` | 任務建立 | 資料模型正確 |
| `test_task_progress_calculation` | 進度計算 | 數學運算正確 |
| `test_system1_simple_query` | 簡單問答 | S1 能回應 |
| `test_system1_non_blocking` | 非阻塞 | S1 不會被 S2 阻塞 |
| `test_system2_receive_task` | 接收任務 | S2 能接收任務 |
| `test_send_and_receive_task` | 通訊 | 通道正常運作 |

### 整合測試 (test_integration.py)

這些測試驗證系統間的協作。

| 測試 | 說明 | 重點 |
|------|------|------|
| `test_dispatch_complex_task` | 任務分派 | S1 能分派給 S2 |
| `test_status_query_during_execution` | 狀態查詢 | 執行中可查詢 |
| `test_multiple_concurrent_queries` | 並發查詢 | 多執行緒安全 |
| `test_query_during_background_task` | 背景任務 | 核心非阻塞測試 |
| `test_task_completion` | 任務完成 | 狀態轉換正確 |
| `test_task_progress_updates` | 進度更新 | 進度追蹤正確 |

### 情境測試 (test_scenarios.py)

這些測試模擬真實使用情境。

| 測試 | 說明 | 情境 |
|------|------|------|
| `test_scenario_morning_commute` | 早晨通勤 | 複雜任務 + 簡單問答 + 狀態查詢 |
| `test_scenario_multiple_tasks` | 多任務 | 同時處理多個任務 |
| `test_scenario_interrupt_and_resume` | 中斷恢復 | 緊急問題不影響任務 |
| `test_scenario_rapid_fire_questions` | 快速問答 | 連續問題處理 |
| `test_empty_input` | 空輸入 | 不崩潰 |
| `test_system_under_load` | 高負載 | 壓力測試 |

---

## 考生須知

### 需要實作的檔案

考生需要建立以下檔案，測試才能執行：

```
src/
├── system1.py        # System 1 實作
├── system2.py        # System 2 實作
└── communication.py  # 通訊機制實作
```

### 必須匯出的類別

```python
# system1.py
class System1:
    def __init__(self, channel=None): ...
    def process_input(self, user_input: str) -> str: ...
    def dispatch_task(self, task: Task) -> str: ...
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]: ...
    def get_task_progress(self, task_id: str) -> Optional[dict]: ...

# system2.py
class System2:
    def __init__(self, channel=None): ...
    def receive_task(self, task: Task) -> bool: ...
    def start_processing(self) -> None: ...  # 主迴圈
    def execute_task(self, task_id: str) -> None: ...
    def get_status(self, task_id: str) -> Optional[TaskStatus]: ...
    def get_task(self, task_id: str) -> Optional[Task]: ...
    def get_all_tasks(self) -> List[Task]: ...

# communication.py
class CommunicationChannel:
    def send_task(self, task: Task) -> bool: ...
    def receive_task(self, timeout: float = None) -> Optional[Task]: ...
    def send_status_update(self, task_id: str, status: TaskStatus, progress: float) -> bool: ...
    def query_status(self, task_id: str) -> Optional[dict]: ...
```

### 開始測試

實作完成後，執行：

```bash
# 先測試基礎功能
pytest tests/test_basic.py -v

# 再測試整合功能
pytest tests/test_integration.py -v

# 最後測試情境
pytest tests/test_scenarios.py -v

# 或一次執行全部
pytest -v
```

---

## 常見問題

### Q: 測試顯示 "尚未實作 System1/System2"

A: 你需要建立 `src/system1.py`, `src/system2.py`, `src/communication.py` 並實作對應的類別。

### Q: ImportError: No module named 'models'

A: 確保你在專案根目錄執行 pytest，或者設定 PYTHONPATH：
```bash
export PYTHONPATH=$PYTHONPATH:./src
pytest
```

### Q: 測試超時

A: 檢查你的實作是否有無限迴圈或死鎖。確保 `receive_task` 有 timeout 機制。

### Q: 並發測試失敗

A: 檢查是否有 race condition。建議使用 `threading.Lock` 保護共享狀態。

---

## 評分標準

| 測試類別 | 配分 |
|----------|------|
| test_basic.py (全部通過) | 30% |
| test_integration.py (全部通過) | 40% |
| test_scenarios.py (全部通過) | 30% |

**注意**：部分通過會依比例給分。
