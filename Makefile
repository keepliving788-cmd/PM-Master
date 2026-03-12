.PHONY: help install setup index sync search test clean

help:
	@echo "Feishu PKB Skill - Makefile Commands"
	@echo ""
	@echo "  make install    - 安装依赖"
	@echo "  make setup      - 初始化环境"
	@echo "  make index      - 构建全量索引"
	@echo "  make sync       - 增量同步"
	@echo "  make search     - 测试检索"
	@echo "  make test       - 运行测试"
	@echo "  make clean      - 清理数据"

install:
	pip install -r requirements.txt

setup:
	@echo "初始化环境..."
	mkdir -p data/{raw,processed,chromadb}
	mkdir -p logs
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "已创建 .env 文件，请填入配置"; \
	fi

index:
	python src/main.py index --full

sync:
	python src/main.py sync

search:
	@read -p "输入查询: " query; \
	python src/main.py search "$$query"

test:
	pytest tests/ -v

clean:
	@echo "清理数据..."
	rm -rf data/
	rm -rf logs/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
