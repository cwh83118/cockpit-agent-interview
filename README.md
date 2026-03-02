# Cockpit Agent System - 面試考題

## 概述

設計並實作一個座艙雙系統 Agent 架構，模擬人類認知的 **System 1**（快思）與 **System 2**（慢想）的協作模式。

```
┌─────────────────────────────────────────────────────────────────┐
│                        Cockpit Agent System                      │
│  ┌─────────────────┐              ┌─────────────────────────┐   │
│  │    System 1     │   dispatch   │       System 2          │   │
│  │  (Fast Response)│ ──────────▶  │   (Background Tasks)    │   │
│  │                 │              │                         │   │
│  │  • 即時對話     │   query      │  • 路線規劃             │   │
│  │  • 簡單問答     │ ◀────────── │  • 任務執行             │   │
│  │  • 任務分派     │   status     │  • 多步驟推理           │   │
│  └────────▲────────┘              └─────────────────────────┘   │
│           │                                                      │
│           │ continuous conversation                              │
│           ▼                                                      │
│  ┌─────────────────┐                                            │
│  │      User       │                                            │
│  │    (Driver)     │                                            │
│  └─────────────────┘                                            │
└─────────────────────────────────────────────────────────────────┘
```

## 背景

這個設計靈感來自 Daniel Kahneman 的《快思慢想》：
- **System 1**：快速、直覺、持續運作，處理簡單對話和任務分派
- **System 2**：緩慢、深思、消耗資源，處理複雜的多步驟任務

在座艙情境中：
- 駕駛可以**隨時與 System 1 對話**（不被阻塞）
- **複雜任務**（路線規劃、行程安排）交由 System 2 在背景執行
- 駕駛可以**隨時詢問進度**，System 1 負責查詢 System 2 的狀態

---

## 考題要求

### Part 1: 核心架構設計 (必做)

實作以下元件：

#### 1.1 System 1 - 對話系統
```python
class System1:
    """
    快速回應系統，負責：
    1. 持續與使用者對話（非阻塞）
    2. 判斷任務類型（簡單問答 vs 複雜任務）
    3. 將複雜任務分派給 System 2
    4. 查詢 System 2 的任務狀態
    """

    def process_input(self, user_input: str) -> str:
        """處理使用者輸入，立即回應"""
        pass

    def dispatch_task(self, task: Task) -> str:
        """將任務發送給 System 2"""
        pass

    def get_task_status(self, task_id: str) -> TaskStatus:
        """查詢 System 2 的任務狀態"""
        pass
```

#### 1.2 System 2 - 任務執行系統
```python
class System2:
    """
    背景任務系統，負責：
    1. 接收 System 1 分派的任務
    2. 執行多步驟的複雜任務（非同步）
    3. 回報任務進度和結果
    """

    def receive_task(self, task: Task) -> str:
        """接收任務並開始執行"""
        pass

    def execute_task(self, task_id: str) -> None:
        """執行任務（背景運行）"""
        pass

    def get_status(self, task_id: str) -> TaskStatus:
        """回報任務狀態"""
        pass
```

#### 1.3 通訊機制
設計 System 1 與 System 2 之間的通訊方式，可選擇：
- Queue-based (推薦)
- Event-based
- Shared State
- 其他你認為適合的方式

### Part 2: 視覺化介面 (必做)

建立一個互動式介面，需包含：

```
┌────────────────────────────────────────────────────────────┐
│  Cockpit Agent System                                       │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  [System 1 - Conversation]                                  │
│  ┌────────────────────────────────────────────────────────┐│
│  │ User: 我想要先送小孩上學，再去上班，順路買杯咖啡      ││
│  │ S1: 好的，我來幫您安排。已將行程規劃交給背景處理...   ││
│  │ User: 法國的首都在哪？                                 ││
│  │ S1: 法國的首都是巴黎。                                 ││
│  │ User: 任務完成了嗎？                                   ││
│  │ S1: 目前進度：路線規劃中 (2/4 步驟完成)               ││
│  └────────────────────────────────────────────────────────┘│
│                                                             │
│  [System 2 - Background Tasks]                              │
│  ┌────────────────────────────────────────────────────────┐│
│  │ Task #1: 行程規劃                    [████████░░] 80%  ││
│  │   ├─ [✓] 解析目的地：學校、公司、咖啡店               ││
│  │   ├─ [✓] 查詢學校位置                                 ││
│  │   ├─ [✓] 查詢公司位置                                 ││
│  │   ├─ [►] 規劃最佳路線...                              ││
│  │   └─ [ ] 尋找順路的咖啡店                             ││
│  └────────────────────────────────────────────────────────┘│
│                                                             │
│  > 輸入訊息: _                                              │
└────────────────────────────────────────────────────────────┘
```

介面要求：
1. **即時更新**：System 2 的任務進度需即時反映
2. **非阻塞輸入**：使用者可隨時輸入，不需等待任務完成
3. **清楚區分**：明確顯示哪個系統正在處理什麼

可使用的技術：
- Terminal UI: `rich`, `textual`, `curses`
- Web UI: `gradio`, `streamlit`, `fastapi + websocket`
- 其他你熟悉的方式

### Part 3: 情境模擬 (必做)

實作以下 Mock 工具，模擬座艙場景：

```python
# 模擬工具（不需真實 API，用 sleep 模擬延遲）
tools = {
    "get_location": lambda place: {"lat": 25.0, "lng": 121.5},  # 模擬查詢地點
    "plan_route": lambda points: {"distance": "15km", "time": "25min"},  # 模擬路線規劃
    "find_nearby": lambda category, location: [{"name": "星巴克", "distance": "500m"}],  # 模擬搜尋附近
    "get_traffic": lambda: {"status": "moderate", "delay": "5min"},  # 模擬交通狀況
}
```

---

## 評分標準

### 架構設計 (40%)

| 項目 | 優秀 (10) | 良好 (7) | 及格 (5) | 不及格 (0-4) |
|------|----------|---------|---------|-------------|
| 系統解耦 | 兩系統完全獨立，介面清晰 | 大致獨立，有少量耦合 | 耦合較多但能運作 | 高度耦合 |
| 通訊設計 | 設計合理、可擴展、有錯誤處理 | 設計合理、基本可用 | 能通訊但設計不佳 | 無法正常通訊 |
| 並發處理 | 正確處理並發、無 race condition | 基本正確，邊界情況有問題 | 有明顯並發問題 | 無法並發 |
| 狀態管理 | 狀態清晰、可追蹤、可恢復 | 狀態可追蹤 | 狀態混亂但能用 | 狀態管理失敗 |

### 功能實作 (30%)

| 項目 | 配分 |
|------|------|
| System 1 能即時回應簡單問題 | 5% |
| System 1 能正確分派複雜任務 | 5% |
| System 2 能背景執行多步驟任務 | 10% |
| 任務狀態查詢正確 | 5% |
| 通過所有測試案例 | 5% |

### 視覺化介面 (20%)

| 項目 | 配分 |
|------|------|
| 對話區域正常運作 | 5% |
| 任務進度即時更新 | 10% |
| 使用者體驗流暢 | 5% |

### 程式碼品質 (10%)

| 項目 | 配分 |
|------|------|
| 程式碼可讀性 | 3% |
| 錯誤處理 | 3% |
| 文件與註解 | 2% |
| 型別標註 | 2% |

---

## 時間限制

- **建議時間**：3-4 小時
- **允許使用**：AI 輔助工具 (Claude, Copilot 等)
- **重點考核**：架構設計決策、系統整合能力、問題解決思路

---

## 提交要求

```
your-submission/
├── README.md           # 說明文件（含執行方式）
├── src/
│   ├── system1.py      # System 1 實作
│   ├── system2.py      # System 2 實作
│   ├── communication.py # 通訊機制
│   ├── models.py       # 資料模型
│   └── ui.py           # 視覺化介面
├── tests/
│   └── ...             # 確保通過提供的測試
├── design.md           # 設計說明（見下方）
└── requirements.txt    # 依賴套件
```

### design.md 需包含

1. **架構圖**：System 1 與 System 2 的交互方式
2. **設計決策**：為什麼選擇這種通訊方式？優缺點？
3. **並發策略**：如何處理多任務並發？
4. **擴展性**：如果要加入 System 3（如安全監控），架構如何調整？
5. **Trade-offs**：你做了哪些取捨？為什麼？

---

## 範例對話流程

```
[00:00] User: 我想要先送小孩上學，再去上班，對了順路幫我買杯咖啡
[00:01] S1: 好的，我來幫您安排行程。已經開始規劃路線了。
        → [S2 收到任務: task_001 - 行程規劃]
        → [S2 開始執行: 解析目的地]

[00:03] User: 今天天氣如何？
[00:03] S1: 讓我查一下... 今天台北晴天，氣溫 25-30 度。
        → [S2 背景執行中: 查詢學校位置]

[00:05] User: 行程規劃好了嗎？
[00:05] S1: 還在處理中，目前進度 60%。已完成：解析目的地、查詢位置。
             正在進行：路線規劃。
        → [S2 背景執行中: 規劃最佳路線]

[00:08] → [S2 任務完成: task_001]
[00:08] S1: 行程規劃完成！建議路線：
             1. 8:00 出發 → 8:15 到達學校
             2. 8:20 出發 → 8:45 到達公司
             順路咖啡店：星巴克（學校附近 500m）
```

---

## 加分項目 (Optional)

- [ ] 實作任務取消功能
- [ ] 實作任務優先級
- [ ] 支援多個並發任務
- [ ] 實作任務依賴關係
- [ ] 添加任務重試機制
- [ ] 實作對話歷史記憶
- [ ] 使用真實 LLM API 處理自然語言

---

## 提示

1. 先確保核心架構正確，再處理邊界情況
2. 使用 `asyncio` 或 `threading` 處理並發
3. 考慮使用 `queue.Queue` 或 `asyncio.Queue` 作為通訊管道
4. 測試案例會驗證並發正確性，注意 race condition
5. 不需要實作真正的 AI/LLM，可以用規則或 mock 模擬

---

## 測試案例使用方式

### 環境設置

```bash
# 1. Fork 這個 repo 並 clone 到本地
git clone https://github.com/YOUR_USERNAME/cockpit-agent-interview.git
cd cockpit-agent-interview

# 2. 建立虛擬環境
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 或 venv\Scripts\activate  # Windows

# 3. 安裝依賴
pip install -r requirements.txt
```

### 執行測試

```bash
# 執行所有測試
make test

# 或使用 pytest 直接執行
pytest -v

# 分類執行
make test-basic        # 基礎功能測試 (30%)
make test-integration  # 整合測試 (40%)
make test-scenarios    # 情境模擬測試 (30%)
```

### 測試結構說明

```
tests/
├── test_basic.py         # 基礎測試
│   ├── TestModels        # 資料模型測試（已提供，應該先通過）
│   ├── TestSystem1Basic  # System 1 基本功能
│   ├── TestSystem2Basic  # System 2 基本功能
│   └── TestCommunication # 通訊機制測試
│
├── test_integration.py   # 整合測試
│   ├── TestTaskDispatch  # 任務分派流程
│   ├── TestConcurrency   # 並發處理（重要！）
│   └── TestTaskLifecycle # 任務生命週期
│
└── test_scenarios.py     # 情境測試
    ├── TestCockpitScenarios # 模擬真實座艙對話
    └── TestEdgeCases        # 邊界情況處理
```

### 你需要實作的檔案

測試會嘗試 import 以下模組，請確保建立這些檔案：

```python
# src/system1.py
from .models import Task, TaskStatus

class System1:
    def __init__(self, channel=None): ...
    def process_input(self, user_input: str) -> str: ...
    def dispatch_task(self, task: Task) -> str: ...
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]: ...
    def get_task_progress(self, task_id: str) -> Optional[dict]: ...

# src/system2.py
class System2:
    def __init__(self, channel=None): ...
    def receive_task(self, task: Task) -> bool: ...
    def start_processing(self) -> None: ...
    def execute_task(self, task_id: str) -> None: ...
    def get_status(self, task_id: str) -> Optional[TaskStatus]: ...
    def get_task(self, task_id: str) -> Optional[Task]: ...
    def get_all_tasks(self) -> List[Task]: ...

# src/communication.py
class CommunicationChannel:
    def send_task(self, task: Task) -> bool: ...
    def receive_task(self, timeout: float = None) -> Optional[Task]: ...
    def send_status_update(self, task_id: str, status: TaskStatus, progress: float) -> bool: ...
    def query_status(self, task_id: str) -> Optional[dict]: ...
```

### 測試開發流程建議

```bash
# Step 1: 先確認 models 測試通過（這些不需要你實作）
pytest tests/test_basic.py::TestModels -v

# Step 2: 實作 communication.py，通過通訊測試
pytest tests/test_basic.py::TestCommunication -v

# Step 3: 實作 system1.py 基本功能
pytest tests/test_basic.py::TestSystem1Basic -v

# Step 4: 實作 system2.py 基本功能
pytest tests/test_basic.py::TestSystem2Basic -v

# Step 5: 通過整合測試（這是核心！）
pytest tests/test_integration.py -v

# Step 6: 通過情境測試
pytest tests/test_scenarios.py -v

# 最後：執行全部測試確認
pytest -v
```

### 常見問題

**Q: 測試顯示 "尚未實作 System1/System2"**
```
SKIPPED [1] test_basic.py: 尚未實作 System1/System2
```
A: 這是正常的！請先建立 `src/system1.py`, `src/system2.py`, `src/communication.py`。

**Q: ImportError: No module named 'models'**

A: 確保在專案根目錄執行測試，或設定 PYTHONPATH：
```bash
export PYTHONPATH=$PYTHONPATH:./src
pytest -v
```

**Q: 並發測試一直失敗**

A: 檢查以下幾點：
- `receive_task()` 是否有 timeout 機制？
- 是否使用 `threading.Lock` 保護共享狀態？
- `start_processing()` 是否會阻塞？應該要能在背景執行

---

## FAQ

**Q: 可以使用 AI 輔助嗎？**
A: 可以，這也是考核的一部分。我們會在面試時詢問設計決策，確保你理解程式碼。

**Q: 需要連接真實的地圖 API 嗎？**
A: 不需要，使用 mock 模擬即可。重點是架構設計。

**Q: 視覺化一定要用特定框架嗎？**
A: 不限制，只要能清楚呈現兩個系統的狀態即可。

**Q: 如果時間不夠，應該優先完成什麼？**
A: 優先順序：核心架構 > 通訊機制 > 測試通過 > 視覺化 > 加分項目

---

## 快速開始 (TL;DR)

```bash
# 1. Fork & Clone
git clone https://github.com/YOUR_USERNAME/cockpit-agent-interview.git
cd cockpit-agent-interview

# 2. 設置環境
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 3. 看看現有的測試（會顯示 SKIPPED，這是正常的）
pytest -v

# 4. 開始實作！建立這三個檔案：
#    - src/system1.py
#    - src/system2.py
#    - src/communication.py

# 5. 邊寫邊測
pytest tests/test_basic.py -v

# 6. 完成後執行全部測試
make test
```

祝你順利！
