# An Tâm — Hệ thống quản lý nhà thuốc có AI (Đề 14)

FastAPI + SQLAlchemy + PostgreSQL, React/Vite, Gemini. Giao diện tiếng Việt, ba vai trò quản lý/dược sĩ/thu ngân.

**Cập nhật từ bản đang chạy:** đọc `DOC_TRUOC_NANG_CAP_AI.md`, copy source đè vào dự án hiện tại, giữ .env/.venv/.git, chạy `NANG_CAP_AI.cmd`, khởi động lại backend/frontend. Lần đầu nâng cấp reset các trạng thái duyệt cũ để kiểm tra lại, không xóa dữ liệu nghiệp vụ.

**Máy mới:** đọc `HUONG_DAN_CHAY.md`. Tóm tắt:

```powershell
py scripts/setup.py
docker compose up -d db
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m app.init_db
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

Terminal khác từ thư mục gốc:

```powershell
cd frontend
npm.cmd ci
npm.cmd run dev
```

Mở localhost:5173, dùng tài khoản admin/mật khẩu tự đặt trong init_db. API localhost:8000/docs. Không commit .env hoặc gửi API key.

## Chức năng

- Thuốc/nhóm/đơn vị, nhà cung cấp, lô, ngày nhập/hạn dùng, giá, tồn, biến động.
- POS và hóa đơn; kiểm tra hết hạn/thiếu tồn/giá thay đổi; khóa lô và transaction bán/hủy, chống tạo hóa đơn trùng khi retry.
- Cảnh báo gần hạn/tồn thấp, báo cáo doanh thu/tồn.
- Quản lý tài khoản và phân quyền; đổi mật khẩu, nút mắt ở mọi ô nhập mật khẩu.
- Duyệt mô tả thuốc cho AI: quản lý/dược sĩ đọc nội dung và xác nhận, sửa thuốc tự hủy duyệt, kiểm tra phiên bản khi xác nhận.
- Chat nhiều lượt trong phiên, multi-tool Agent, RAG, truy vấn tổng hợp read-only, streaming, dừng, tạo lại, sao chép và đánh giá trong phiên.
- **Không có lịch sử hội thoại hay tự đặt tên**. Không lưu chat mới trong database/localStorage. Dữ liệu chat cũ không tự xóa.
- Thông tin thuốc chưa duyệt không được dùng để tóm tắt. Quy trình nội bộ do quản lý nhập; không thêm workflow phê duyệt quy trình.
- Không có workflow duyệt điều chỉnh tồn/giá; quản lý/dược sĩ thực hiện theo quyền hiện tại và ghi biến động kho.

## Gemini

Cấu hình backend/.env:

```dotenv
GEMINI_API_KEY=YOUR_KEY
GEMINI_MODEL=gemini-3.5-flash-lite
GEMINI_FALLBACK_MODELS=gemini-3.1-flash-lite,gemini-2.5-flash-lite
GEMINI_RETRY_ATTEMPTS=1
```

Chat dùng Gemini generateContent để chọn công cụ/đoạn nguồn và streamGenerateContent để trả lời. Các API AI cũ vẫn giữ để tương thích. Khi provider lỗi, hiển thị rõ chưa có phân tích AI và chỉ các dữ liệu truy xuất được. Model có thể sai; xác nhận nguồn không bảo đảm nội dung chuyên môn đúng tuyệt đối.

**AI chỉ hỗ trợ tham khảo, không tư vấn dùng thuốc thay dược sĩ/bác sĩ.**

## Kiểm thử / tài liệu

- `docs/AI_V4_TEST_REPORT.md`: kết quả và giới hạn bàn giao.
- `docs/NGHIEM_THU_V4.md`: chạy test local, PostgreSQL riêng, Gemini fixture và ma trận nghiệm thu.
- `scripts/verify_gemini.py`: kiểm tra live tùy chọn, chỉ gửi dữ liệu mô phỏng; không đọc dữ liệu nhà thuốc.
- `docs/AI_SDLC.md`: cách lưu prompt/code/test/commit làm minh chứng thật.
- `docs/THIET_KE.md`: kiến trúc, quyền và giới hạn.
- `docs/API.md`: API hiện tại.
- `DEPLOY_RENDER.md`: triển khai.
