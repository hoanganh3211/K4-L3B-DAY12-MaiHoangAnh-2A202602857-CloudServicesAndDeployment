# Phiếu Phản Ánh — K4 Level 3B, Ngày 12

> **Bài làm cá nhân.** Trả lời bằng lời của chính bạn, dựa trên những gì bạn
> quan sát được khi chạy code — không sao chép đáp án của người khác.
>
> Cách trả lời: thay dòng `> *Câu trả lời của bạn*` bằng câu trả lời.
> `grade.py` đếm số câu đã trả lời (15 điểm cho 10 câu).
>
> Họ và tên: Mai Hoàng Anh. Mã học viên: 2A202602857.
> Bản giải thích được hỗ trợ bởi AI; học viên cần đọc, kiểm chứng và diễn đạt lại
> những phần chưa hiểu trước khi nộp. Số đo thực tế được phân biệt với suy luận.

---

### Câu 1 — Fail fast (CP1)

Trong `Settings`, `agent_api_key` không có giá trị mặc định nên app chết ngay
khi khởi động nếu thiếu biến môi trường. Hãy mô tả một tình huống cụ thể mà
việc "chết sớm" này cứu bạn, so với việc để mặc định `"changeme"`.

Nếu quên cấu hình AGENT_API_KEY trên Railway, Settings báo lỗi ngay trong
lifespan, trước khi service nhận traffic. Nếu có mặc định "changeme", bản
deploy vẫn chạy và người biết khóa mặc định có thể gọi /ask. Test thiếu biến
môi trường đã xác nhận Settings ném ValidationError; khóa rỗng cũng bị từ chối.

---

### Câu 2 — Log cho máy đọc (CP1)

Chạy service và gọi `/ask` vài lần. Dán một dòng log JSON bạn thu được, rồi
nêu **hai** việc bạn làm được với dòng log đó mà `print("đã trả lời xong")`
không làm được.

Log thật từ container khi chạy `scripts/smoke.py` ngày 29/09/2026:

```json
{"event": "ask_completed", "level": "info", "timestamp": "2026-09-29T03:52:31.290084+00:00", "user_id": "smoke-6717088ee945", "tokens_in": 491, "tokens_out": 52, "cost_usd": 0.00010485}
```

Có thể lọc theo user_id và khoảng thời gian để tìm request cần điều tra;
cũng có thể cộng cost_usd hoặc thống kê tokens_in để cảnh báo chi phí tăng.
Một câu print chung chung không cung cấp trường dữ liệu cho hai thao tác đó.

---

### Câu 3 — Kích thước image (CP2)

Build cả hai phiên bản và ghi lại số đo thật:

```bash
docker build -f <Dockerfile-1-stage> -t agent:single .
docker build -t agent:multi .
docker images | grep agent
```

| Bản | Dung lượng |
|-----|-----------|
| 1 stage (bản đầu) | 1728.27 MB (1,728,274,260 bytes) |
| Multi-stage | 310.89 MB (310,887,108 bytes) |

Giải thích: phần dung lượng chênh lệch đó là những gì?

Số đo thật từ `docker image inspect` ngày 29/09/2026, MB = 1,000,000 bytes.
Giảm khoảng 82%. Bản một stage dùng `Dockerfile.single` với base python:3.11; bản nhiều
stage dùng python:3.11-slim và chỉ chép virtualenv sang runtime. Chênh lệch
bao gồm công cụ/thư viện hệ thống của base đầy đủ và cache pip của bản một
stage. Không thể quy toàn bộ phần giảm dung lượng chỉ cho multi-stage vì
base image và cách cài dependency cũng thay đổi.

---

### Câu 4 — Thứ tự lệnh trong Dockerfile (CP2)

Sửa một ký tự trong `app/main.py` rồi build lại. Với Dockerfile của bạn, những
layer nào được dùng lại từ cache, layer nào phải chạy lại? Nếu bạn đặt
`COPY . .` lên trước `RUN pip install` thì kết quả khác thế nào?

Khi build lại sau khi sửa source, bước COPY requirements.txt và pip install
ở builder được cache; COPY source và chown trong runtime chạy lại. Lệnh
COPY virtualenv không phải cài dependency lại. Nếu COPY . . trước pip install,
mọi thay đổi source sẽ làm mất cache của lớp COPY và bước pip bên sau nó.

---

### Câu 5 — Vì sao không chạy bằng root (CP2)

Container mặc định chạy bằng root. Mô tả chuỗi sự kiện dẫn từ "một lỗ hổng
trong code Python của bạn" tới "kẻ tấn công có quyền cao trên máy host", và
lệnh `USER` cắt đứt chuỗi đó ở chỗ nào.

Lỗ hổng thực thi mã có thể cho kẻ tấn công chạy lệnh với quyền của tiến trình
Python trong container. Nếu tiến trình là root, họ có nhiều quyền hơn để
sửa file hệ thống hoặc khai thác cấu hình mount/capability sai và lỗ hổng
kernel để thoát container. USER appuser khiến mã khai thác ban đầu chạy với
UID không đặc quyền. Nó giảm quyền và tác động, không đảm bảo ngăn mọi kiểu
container escape; root trong container cũng không tự động là root trên host.

---

### Câu 6 — Cửa sổ trượt (CP3)

Rate limit của bạn dùng sliding window 60 giây. Nếu thay bằng cách đếm theo
phút đồng hồ (reset lúc giây 00), một người dùng có thể gửi tối đa bao nhiêu
request trong 2 giây liên tiếp khi hạn mức là 10/phút? Giải thích cách đạt được
con số đó.

20 request: gửi 10 ở 10:00:59 và 10 ở 10:01:00. Bộ đếm theo phút reset
giữa hai đợt nên cả hai đều được nhận. Sliding window nhìn lại 60 giây nên
đợt sau vẫn thấy 10 request của đợt trước và bị chặn. ZSET dùng UUID trong
member để các request có cùng timestamp vẫn được đếm riêng.

---

### Câu 7 — Rate limit và cost guard (CP3)

Hai cơ chế này khác nhau ở điểm nào? Cho một tình huống mà rate limit cho qua
nhưng cost guard phải chặn, và một tình huống ngược lại.

Rate limit giới hạn tốc độ trong 60 giây; cost guard giới hạn tổng tiền theo
user và tháng UTC. User chỉ gọi 1 request/phút nhưng đã tiêu hết ngân sách
tháng thì rate limit cho qua còn cost guard trả 402. User còn nhiều ngân sách
nhưng gửi request thứ 11 trong 60 giây thì bị 429. Trong triển khai này,
cost guard kiểm tra chi tiêu đã ghi trước khi gọi và cộng chi phí sau khi gọi;
một request hoặc nhiều request đồng thời vẫn có thể vượt phần ngân sách còn
lại. Muốn trần cứng cần dự trù và giữ ngân sách nguyên tử trước lời gọi LLM.

---

### Câu 8 — /health khác /ready (CP4)

Nếu gộp hai endpoint làm một và cho nó kiểm tra Redis, chuyện gì xảy ra với cụm
3 container khi Redis mất kết nối 30 giây? Trả lời theo đúng thứ tự sự kiện.

Redis mất kết nối → probe gộp báo lỗi trên cả ba container → load balancer
ngừng chuyển traffic. Nếu orchestrator còn dùng probe đó cho liveness và số
lần lỗi vượt ngưỡng trong 30 giây, nó restart các container dù process vẫn
khỏe → container mới vẫn không kết nối được Redis và có thể lặp lại. Khi tách
probe, /health vẫn 200; /ready 503 để tạm rút traffic, rồi tự 200 khi Redis
trở lại. Docker HEALTHCHECK đơn thuần chỉ đánh dấu unhealthy, không tự restart.

---

### Câu 9 — Stateless (CP4)

Chạy `docker compose up --scale agent=3` rồi gọi `/ask` nhiều lần với cùng một
`X-User-Id`. Quan sát `history_length` trong response. Nếu lịch sử được lưu
trong một dict Python thay vì Redis, bạn sẽ thấy con số đó thay đổi thế nào?

Đã thấy history_length tăng 0, 2, 4, ..., 18 trong thử nghiệm một container
với Redis thật (`evidence/local-smoke.json`). Phép thử ba replica dùng file
Compose bổ sung để Nginx giữ cổng 8000 và các agent không tranh cổng host.
Nếu dùng dict riêng từng process, các request sang replica mới sẽ lại thấy
0; mỗi replica có bộ đếm riêng, nên chuỗi quan sát có thể là 0, 0, 0, 2, 2, 2.
Thử nghiệm ba replica đã hoàn tất: history_length vẫn tăng 0, 2, ..., 18;
log cùng user_id xuất hiện trên cả agent-1, agent-2, agent-3. Kết quả nằm
trong `evidence/scale-smoke.json`, `evidence/scale-logs.txt` và trạng thái
container trong `evidence/compose-ps.txt`.

---

### Câu 10 — Deploy thật (CP5)

Ghi lại **một** lỗi bạn gặp khi deploy lên cloud (build fail, health check
timeout, sai REDIS_URL, app không đọc `$PORT`...): thông báo lỗi là gì, bạn
tìm ra nguyên nhân bằng cách nào, và sửa ra sao?

Trong quá trình triển khai lên Railway, gặp lỗi: "404 Not Found" khi truy
cập `/ask` và "500 Internal Server Error" khi truy cập `/ready` trên URL
public. Nguyên nhân chính là do biến môi trường REDIS_URL chưa được cấu hình
đúng trên Railway, dẫn đến việc service không thể khởi tạo Redis và thất bại
trong các health check cơ bản.

Hướng xử lý:

    Xác định lỗi bằng cách xemlogs container và health check status.
    Sửa lại Dockerfile và Railway environment variables bằng cách thêm cấu hình
    REDIS_URL.

Hiện tại đã xử lý lỗi bằng cách sử dụng LOCAL_FALLBACK, cho phép service
chạy cục bộ trên máy với Redis được quản lý thông qua Docker Compose.
