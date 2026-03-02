.PHONY: install test test-basic test-integration test-scenarios grade clean

# 安裝依賴
install:
	pip install -r requirements.txt

# 執行所有測試
test:
	pytest -v

# 只執行基礎測試
test-basic:
	pytest tests/test_basic.py -v

# 只執行整合測試
test-integration:
	pytest tests/test_integration.py -v

# 只執行情境測試
test-scenarios:
	pytest tests/test_scenarios.py -v

# 執行評分
grade:
	python scripts/grade.py

# 清理
clean:
	rm -rf __pycache__ .pytest_cache
	rm -rf src/__pycache__ tests/__pycache__
	rm -f test_report.json
	find . -name "*.pyc" -delete
