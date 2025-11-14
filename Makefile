.PHONY: help build up down restart logs clean migrate test

help: ## Hiển thị trợ giúp
	@echo "Các lệnh có sẵn:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Build Docker image
	@echo "🔨 Building Docker image..."
	docker compose build

up: ## Khởi động containers
	@echo "🚀 Starting containers..."
	docker compose up -d
	@echo "✅ Containers started!"
	@echo "📊 View logs: make logs"

down: ## Dừng containers
	@echo "🛑 Stopping containers..."
	docker compose down
	@echo "✅ Containers stopped!"

restart: ## Restart containers (sẽ tự động chạy migrations)
	@echo "🔄 Restarting containers..."
	docker compose restart
	@echo "✅ Containers restarted!"
	@echo "📊 View logs: make logs"

rebuild: ## Rebuild và restart (build mới từ đầu)
	@echo "🔄 Rebuilding and restarting..."
	docker compose down
	docker compose build --no-cache
	docker compose up -d
	@echo "✅ Rebuild completed!"
	@echo "📊 View logs: make logs"

logs: ## Xem logs
	docker compose logs -f

logs-web: ## Xem logs của web service
	docker logs -f khampha-web

logs-tunnel: ## Xem logs của cloudflare tunnel
	docker logs -f khampha-tunnel

clean: ## Xóa containers, volumes và images
	@echo "🗑️  Cleaning up..."
	docker compose down -v
	docker image prune -f
	@echo "✅ Cleanup completed!"

migrate: ## Chạy migrations thủ công trong container đang chạy
	@echo "🔄 Running migrations..."
	docker exec khampha-web python backend/database/run_migrations.py
	@echo "✅ Migrations completed!"

db-init: ## Khởi tạo database thủ công
	@echo "🗄️  Initializing database..."
	docker exec khampha-web python backend/database/init_db.py
	@echo "✅ Database initialized!"

shell: ## Mở shell trong container
	docker exec -it khampha-web /bin/bash

ps: ## Xem trạng thái containers
	docker compose ps

status: ## Xem chi tiết trạng thái
	@echo "📊 Container Status:"
	@docker compose ps
	@echo ""
	@echo "💾 Volume Status:"
	@docker volume ls | grep khampha || echo "No volumes found"
	@echo ""
	@echo "🌐 Network Status:"
	@docker network ls | grep khampha || echo "No networks found"

health: ## Kiểm tra health của ứng dụng
	@echo "🏥 Checking application health..."
	@curl -s http://localhost:5002/api/health | python -m json.tool || echo "❌ Application not responding"

backup-db: ## Backup database
	@echo "💾 Backing up database..."
	@mkdir -p backups
	@docker exec khampha-web cp /app/backend/data/travelmate.db /app/backend/data/backups/travelmate_$$(date +%Y%m%d_%H%M%S).db
	@docker cp khampha-web:/app/backend/data/backups/. ./backups/
	@echo "✅ Database backed up to ./backups/"

restore-db: ## Restore database (usage: make restore-db FILE=backup_file.db)
	@if [ -z "$(FILE)" ]; then \
		echo "❌ Please specify FILE parameter. Usage: make restore-db FILE=backup_file.db"; \
		exit 1; \
	fi
	@echo "📥 Restoring database from $(FILE)..."
	@docker cp $(FILE) khampha-web:/app/backend/data/travelmate.db
	@docker compose restart web
	@echo "✅ Database restored!"
