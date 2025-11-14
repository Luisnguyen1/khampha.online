# Database Migration System

Hệ thống tự động chạy migrations khi Docker container khởi động.

## 🔄 Migrations tự động

Mỗi khi bạn build hoặc restart Docker, hệ thống sẽ:

1. ✅ Khởi tạo database schema (nếu chưa có)
2. ✅ Tự động chạy tất cả migrations trong thư mục `backend/database/migrate_*.py`
3. ✅ Log chi tiết quá trình migration
4. ✅ Bắt đầu Flask application

## 📝 Các lệnh Docker

### Sử dụng Docker Compose

```bash
# Build image
docker compose build

# Khởi động (tự động chạy migrations)
docker compose up -d

# Restart (tự động chạy migrations)
docker compose restart

# Rebuild từ đầu
docker compose down
docker compose build --no-cache
docker compose up -d

# Xem logs
docker compose logs -f
docker logs -f khampha-web
```

### Sử dụng Makefile (khuyến nghị)

```bash
# Xem tất cả lệnh có sẵn
make help

# Build Docker image
make build

# Khởi động containers
make up

# Restart containers (tự động chạy migrations)
make restart

# Rebuild hoàn toàn
make rebuild

# Xem logs
make logs
make logs-web

# Chạy migrations thủ công (container đang chạy)
make migrate

# Khởi tạo database thủ công
make db-init

# Mở shell trong container
make shell

# Kiểm tra health
make health

# Backup database
make backup-db

# Restore database
make restore-db FILE=backups/travelmate_20251114_120000.db

# Dọn dẹp
make clean
```

## 🆕 Tạo migration mới

1. Tạo file mới trong `backend/database/` với tên `migrate_<tên_feature>.py`

2. Sử dụng template sau:

```python
"""
Migration: <Mô tả migration>
"""
import sqlite3
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate():
    """<Mô tả chi tiết>"""
    db_path = Path(__file__).parent.parent / 'data' / 'travelmate.db'
    
    logger.info(f"Database path: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Kiểm tra xem migration đã chạy chưa
        cursor.execute("PRAGMA table_info(your_table)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'new_column' not in columns:
            logger.info("Adding new_column to your_table...")
            cursor.execute("""
                ALTER TABLE your_table 
                ADD COLUMN new_column TEXT
            """)
            logger.info("✅ Added new_column")
        else:
            logger.info("new_column already exists, skipping...")
        
        conn.commit()
        logger.info("✅ Migration completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {str(e)}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
```

3. Migration sẽ tự động chạy khi restart Docker

## 📋 Migrations hiện có

- `migrate_add_dates.py` - Thêm start_date và end_date
- `migrate_add_flights.py` - Thêm bảng flights
- `migrate_add_hotels.py` - Thêm bảng hotels
- `migrate_add_location.py` - Thêm location tracking
- `migrate_add_search_sources.py` - Thêm search sources
- `migrate_profile_fields.py` - Cập nhật user profile fields

## 🔍 Kiểm tra migrations

```bash
# Xem logs của quá trình migration
docker logs khampha-web | grep -A 20 "Starting database migrations"

# Hoặc sử dụng make
make logs-web | grep -A 20 "Starting database migrations"

# Chạy migrations thủ công để test
make migrate
```

## 🐛 Troubleshooting

### Migration bị lỗi khi startup

Nếu migration gặp lỗi, container vẫn sẽ tiếp tục chạy. Kiểm tra logs:

```bash
make logs-web
```

### Chạy lại một migration cụ thể

```bash
# Vào container
make shell

# Chạy migration cụ thể
python backend/database/migrate_add_dates.py
```

### Reset database hoàn toàn

```bash
# Backup trước (quan trọng!)
make backup-db

# Dừng containers
make down

# Xóa database file
rm -rf backend/data/travelmate.db

# Khởi động lại (sẽ tạo database mới + chạy migrations)
make up
```

## 📦 Cấu trúc thư mục database

```
backend/database/
├── __init__.py
├── db_manager.py           # Database manager chính
├── models.py               # SQLAlchemy models
├── init_db.py              # Khởi tạo database schema
├── run_migrations.py       # Script tự động chạy migrations (MỚI)
├── migrate_*.py            # Các file migration
└── __pycache__/
```

## 🎯 Best Practices

1. **Luôn kiểm tra trước khi thêm**: Migration phải check xem column/table đã tồn tại chưa
2. **Idempotent**: Migration có thể chạy nhiều lần mà không gây lỗi
3. **Log đầy đủ**: Sử dụng logger để track quá trình
4. **Error handling**: Bắt exceptions và log rõ ràng
5. **Backup trước khi migrate**: Luôn backup database trước khi chạy migration mới
6. **Test local trước**: Test migration locally trước khi deploy
7. **Tên file rõ ràng**: Đặt tên file migration mô tả rõ nội dung

## ⚠️ Lưu ý quan trọng

- Migrations chạy tự động mỗi khi container khởi động
- Nếu migration đã chạy rồi, nó sẽ skip (idempotent)
- Container sẽ tiếp tục chạy ngay cả khi có migration lỗi
- Luôn backup database trước khi thêm migration mới
- Migrations chạy theo thứ tự alphabet (migrate_a.py trước migrate_b.py)
