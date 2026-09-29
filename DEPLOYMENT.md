# Thông Tin Deploy — Checkpoint 5

## Thông tin học viên

| Mục | Nội dung |
|---|---|
| Họ và tên | Mai Hoàng Anh |
| Mã học viên | 2A202602857 |
| Repo | https://github.com/hoanganh3211/K4-L3B-DAY12-MaiHoangAnh-2A202602857-CloudServicesAndDeployment |

## Service

| Mục | Nội dung |
|---|---|
| Public URL | https://day12-agent-production-5f3e.up.railway.app |
| Platform | Railway |
| Ngày cấu hình | 29/09/2026 |
| Trạng thái | Đang chờ cấu hình API key và xác minh healthcheck |
| Service | day12-agent |
| Redis | day12-redis, trong cùng project và environment production |

## Biến môi trường

Chỉ ghi tên và nguồn, không ghi giá trị secret.

| Biến | Nguồn |
|---|---|
| PORT | Railway cấp tự động; Docker CMD đọc biến này |
| AGENT_API_KEY | Secret do chủ tài khoản nhập trong Railway Variables |
| REDIS_URL | Tham chiếu URL của service day12-redis qua mạng riêng |
| RATE_LIMIT_PER_MINUTE | Railway Variables, hạn mức lab 10 |
| MONTHLY_BUDGET_USD | Railway Variables, ngân sách lab 10.0 |
| LOG_LEVEL | Railway Variables, INFO |

`DEPLOY_API_KEY` là biến chỉ dùng ở máy kiểm thử, lấy cùng giá trị khóa API
của service và lưu trong `.env` không được Git theo dõi. Không phải Railway token.

## Kiểm tra lặp lại

```powershell
.\.venv\Scripts\python scripts/smoke.py --url https://day12-agent-production-5f3e.up.railway.app --output evidence/cloud-smoke.json
.\.venv\Scripts\python -m pytest tests/ -v
.\.venv\Scripts\python grade.py
```

Script smoke đọc khóa từ môi trường, không in khóa. Nó kiểm tra health,
ready, 401, lịch sử hội thoại và 429 với user_id riêng cho mỗi lần chạy.

## Bằng chứng thực tế local

- `evidence/local-smoke.json`: Docker agent + Redis thật; health/ready 200,
  thiếu key 401, 10 request thành công sau đó 5 request bị 429.
- `evidence/scale-smoke.json`: cùng phép thử qua Nginx và ba replica.
- `evidence/scale-logs.txt`: cùng user_id được phục vụ ở agent-1, agent-2,
  agent-3; history_length tăng 0, 2, ..., 18.
- `evidence/compose-ps.txt`: trạng thái stack ba replica.
- CP1–CP4 và ba kiểm tra hồi quy: 73 passed, gồm build Docker thật.
- Runtime chạy với UID 10001 (appuser).
- Restart ba agent cho log `service_stopped`, `Application shutdown complete`
  và `Finished server process [1]`; không cần chờ SIGKILL.

## CI/CD

Workflow `.github/workflows/ci.yml` chạy test và build image cho push/PR.
Job deploy phụ thuộc job test, chỉ chạy push main khi có GitHub variable
`RAILWAY_SERVICE_ID`. Cấu hình GitHub environment `production`, secret
`RAILWAY_TOKEN` (project token) và variable `RAILWAY_SERVICE_ID` trước khi bật
job deploy. Không đặt token vào source hay tài liệu. Nếu dùng GitHub Actions
để deploy, tắt auto deploy độc lập của Railway hoặc bật cơ chế chờ CI để
tránh deploy trước khi test xanh.

Tài liệu tham khảo: [Railway CLI deploying](https://docs.railway.com/cli/deploying),
[Railway healthchecks](https://docs.railway.com/deployments/healthchecks).
Railway dùng `/ready` khi chuyển sang deployment mới; Docker dùng `/health`.

## Ảnh minh chứng

Ảnh dashboard và /health sẽ lưu trong `screenshots/` sau khi bản cloud hoạt động.
Không dùng LOCAL_FALLBACK để thay thế kết quả deploy Railway.

## Lý do sử dụng Local Fallback

Do url https://day12-agent-production-5f3e.up.railway.app/ask báo lỗi 404 Not Found, em sử dụng phương án dự phòng LOCAL_FALLBACK.
