# Kết quả kiểm thử An Tâm AI v3

## Đã chạy

- Backend: `python -m pytest -q` — **45 passed, 1 skipped**. Có một cảnh báo deprecation từ Starlette/AnyIO; không ảnh hưởng kết quả test.
- Frontend: `npm test` — **15 passed**.
- Frontend production: `npm run build` — thành công.
- Python: `python -m compileall -q backend/app` — thành công.

## Phạm vi mới đã kiểm tra

- Calendar Việt Nam: hôm qua, tuần này/trước, tháng trước, quý này, 30 ngày qua, 90 ngày tới, ngày cụ thể và ngày không hợp lệ.
- SELECT tổng hợp chênh giá nhập; từ chối DELETE, nhiều câu SQL, bảng users/sqlite_master, hàm load_extension/randomblob, CTE/UNION và cột không có trong schema.
- Tra tên gần đúng/alias/mã lô; giữ thuốc qua câu “Còn hạn dùng?” và “Nhà cung cấp của nó”; hỏi lại khi không có ngữ cảnh.
- Semantic RAG chỉ chấp nhận ID đoạn nguồn có thật; bỏ ID do model tự tạo.
- Agent gọi nhiều công cụ, gồm truy vấn động, rồi kết thúc sau review.
- Lưu tin nhắn/nguồn/model/tiêu đề; phân tách lịch sử theo người dùng; kiểm tra truy cập chéo bị 404.
- Tạo lại trong nhánh riêng và giữ nội dung gốc; lưu đánh giá.
- Dừng giữ phần trả lời đã nhận và giải phóng trạng thái đang chạy.
- Fallback khi thiếu Gemini key thể hiện rõ không có phân tích AI.
- UI nhận streaming, AbortSignal, bảng Markdown, và không thực thi script trong câu trả lời.
- Bộ test nghiệp vụ cũ được cập nhật ở những chỗ vẫn yêu cầu các luồng phê duyệt/nhật ký đã không tồn tại trong source đầu vào. Không khôi phục các luồng đã bỏ để làm test xanh.

## Chưa xác nhận trực tiếp

- Không chạy Gemini bằng khóa/dữ liệu thật. Automatic approval review chặn lời gọi live trong lần kiểm thử ban đầu; bộ test sau đó ép key rỗng và chặn HTTPTransport, dùng model giả lập. Vì vậy chưa xác nhận quota/model availability và chất lượng câu trả lời thực tế của tài khoản.
- Test PostgreSQL tích hợp bị skip vì không có database PostgreSQL kiểm thử. Các test tự động chạy SQLite. Nhánh READ ONLY/REPEATABLE READ cần kiểm tra thêm trên PostgreSQL thực tế khi chạy local.
- Không hoàn tất chụp màn hình bằng Chromium: môi trường thiếu executable và tải trình duyệt không thành công. Đã kiểm tra component bằng jsdom và build; chưa coi đó là kiểm thử bố cục bằng trình duyệt thật.
- Script Windows đã được rà soát nội dung, chưa thực thi trên Windows ở môi trường này.

Các bước demo/kiểm thử với dữ liệu thực nằm trong `DOC_TRUOC_NANG_CAP_AI.md`.
