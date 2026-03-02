#!/usr/bin/env python3
"""
評分腳本

這個腳本用於自動評分考生的實作。

使用方式：
    python scripts/grade.py

輸出：
    - 各測試類別的通過/失敗數量
    - 總分
    - 詳細報告
"""
import subprocess
import json
import sys
from pathlib import Path


def run_tests():
    """執行所有測試並收集結果"""
    result = subprocess.run(
        ["pytest", "--tb=no", "-q", "--json-report", "--json-report-file=test_report.json"],
        capture_output=True,
        text=True
    )
    return result.returncode


def parse_results():
    """解析測試結果"""
    report_path = Path("test_report.json")
    if not report_path.exists():
        print("錯誤：找不到測試報告。請先安裝 pytest-json-report：")
        print("  pip install pytest-json-report")
        return None

    with open(report_path) as f:
        report = json.load(f)

    return report


def calculate_score(report):
    """計算分數"""
    if not report:
        return 0, {}

    tests = report.get("tests", [])

    # 按檔案分類
    categories = {
        "test_basic.py": {"passed": 0, "failed": 0, "weight": 0.3},
        "test_integration.py": {"passed": 0, "failed": 0, "weight": 0.4},
        "test_scenarios.py": {"passed": 0, "failed": 0, "weight": 0.3},
    }

    for test in tests:
        nodeid = test.get("nodeid", "")
        outcome = test.get("outcome", "")

        for filename in categories:
            if filename in nodeid:
                if outcome == "passed":
                    categories[filename]["passed"] += 1
                else:
                    categories[filename]["failed"] += 1
                break

    # 計算總分
    total_score = 0
    for filename, data in categories.items():
        total = data["passed"] + data["failed"]
        if total > 0:
            category_score = (data["passed"] / total) * data["weight"] * 100
            total_score += category_score
            data["score"] = category_score
        else:
            data["score"] = 0

    return total_score, categories


def print_report(total_score, categories):
    """輸出報告"""
    print("=" * 60)
    print("Cockpit Agent System - 評分報告")
    print("=" * 60)
    print()

    for filename, data in categories.items():
        total = data["passed"] + data["failed"]
        print(f"📁 {filename}")
        print(f"   通過: {data['passed']}/{total}")
        print(f"   分數: {data['score']:.1f} / {data['weight'] * 100:.0f}")
        print()

    print("-" * 60)
    print(f"總分: {total_score:.1f} / 100")
    print("-" * 60)

    if total_score >= 90:
        print("評等: A (優秀)")
    elif total_score >= 80:
        print("評等: B (良好)")
    elif total_score >= 70:
        print("評等: C (及格)")
    elif total_score >= 60:
        print("評等: D (勉強及格)")
    else:
        print("評等: F (不及格)")


def main():
    print("正在執行測試...")
    run_tests()

    report = parse_results()
    if report:
        total_score, categories = calculate_score(report)
        print_report(total_score, categories)
    else:
        # 如果沒有 json report，用簡單方式執行
        print("\n使用簡易模式執行測試：\n")
        subprocess.run(["pytest", "-v", "--tb=short"])


if __name__ == "__main__":
    main()
