# Hướng dẫn cấu hình Gmail API

## Bước 1: Chạy script authorize trên máy local

1. Tải thư mục project về máy local của bạn
2. Đảm bảo file `credentials.json` có trong thư mục gốc
3. Cài đặt thư viện cần thiết:
```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

4. Chạy script authorize:
```bash
python3 authorize_gmail.py
```

5. Browser sẽ mở và yêu cầu bạn đăng nhập Gmail
6. Cho phép ứng dụng truy cập Gmail
7. Script sẽ tạo file `backend/token.json`

## Bước 2: Upload token.json lên server

Copy file `backend/token.json` từ máy local lên server:

```bash
scp backend/token.json root@your-server:/root/khampha.online/backend/token.json
```

## Bước 3: Restart container

```bash
cd /root/khampha.online
docker compose restart web
```

## Lưu ý

- Token có thời hạn sử dụng, khi hết hạn cần refresh
- Credentials có refresh_token nên token sẽ tự động refresh
- Nếu gặp lỗi, xóa `token.json` và authorize lại

## Alternative: Chạy authorize trực tiếp trên server (nếu có X11 forwarding)

```bash
# Trên server
cd /root/khampha.online
docker exec -it khampha-web python3 /app/authorize_gmail.py
```

Nhưng cách này cần SSH với X11 forwarding enabled:
```bash
ssh -X root@your-server
```
