# Nghiệm thu đề 14 — thao tác và minh chứng

## 1. Kiểm thử tự động

Từ thư mục backend, dùng Python trong .venv:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Từ frontend:

```powershell
npm.cmd test
npm.cmd run build
```

## 2. PostgreSQL thật

Dùng DATABASE KIỂM THỬ RIÊNG, không dùng database bán hàng. Tạo database test bằng pgAdmin hoặc PostgreSQL riêng. Từ backend, cấu hình URL của database test rồi chạy:

```powershell
$env:TEST_POSTGRES_URL='postgresql+psycopg://USER:PASSWORD@localhost:5432/pharmacy_test'
.\.venv\Scripts\python.exe -m pytest tests/test_postgres.py -v
Remove-Item Env:TEST_POSTGRES_URL
```

Thay USER/PASSWORD bằng tài khoản database test. Không chụp ảnh chứa URL/mật khẩu. Test tạo schema ngẫu nhiên rồi xóa schema đó trong finally; không xóa các schema khác. Kết quả cần thấy: 2 giao dịch mỗi giao dịch mua 7 trên tồn 10 → một thành công, một bị chặn; tồn còn 3, chỉ 1 hóa đơn. Nếu skip thì chưa nghiệm thu PostgreSQL.

## 3. Gemini thật bằng dữ liệu giả lập

Cấu hình key trong backend/.env; từ thư mục gốc:

```powershell
.\backend\.venv\Scripts\python.exe scripts\verify_gemini.py
```

Script gửi thông tin thuốc mô phỏng, không truy vấn database; lưu `evidence/gemini_live_result.json`. Tốn lượt/hạn mức Gemini. Chỉ kết luận kết nối/streaming hoạt động khi có câu trả lời và không lỗi. Người kiểm thử vẫn phải đọc nội dung và tự ghi đạt/không đạt về độ đúng, nguồn, cảnh báo. Không coi phản hồi dự phòng là Gemini thành công.

## 4. Kiểm thử giao diện/nghiệp vụ

| Mã | Thao tác | Kết quả mong đợi | Minh chứng nhóm tự lưu |
| --- | --- | --- | --- |
| A01 | Thuốc mới có mô tả, chưa duyệt → hỏi tóm tắt | Không lấy mô tả chưa duyệt; thông báo cần xác nhận | Ảnh trạng thái + câu trả lời |
| A02 | Quản lý/dược sĩ mở Kiểm tra nguồn AI, đọc rồi xác nhận | Đã duyệt cho AI | Ảnh dialog và danh mục |
| A03 | Hỏi tóm tắt thuốc đã duyệt | Có nội dung mô tả thật, nguồn Thuốc; không chỉ số liệu tồn | Ảnh + đối chiếu mô tả |
| A04 | Sửa mô tả thuốc | Hủy duyệt; hỏi lại không được dùng mô tả mới | Ảnh trước/sau |
| A05 | Hai cửa sổ: một sửa, một duyệt nội dung cũ | 409 yêu cầu tải lại, không duyệt nhầm phiên bản | Ảnh lỗi |
| A06 | Thu ngân thử duyệt bằng API | 403 | Log không chứa cookie/token |
| A07 | Hỏi lô gần hết hạn + cách xử lý | Dữ liệu lô đúng, nguồn nội bộ, lời nhắc không thay chuyên môn | Ảnh + đối chiếu Cảnh báo |
| A08 | Hỏi “Còn hạn dùng?” sau khi hỏi một thuốc | Giữ đúng thuốc hoặc hỏi chọn mã nếu mơ hồ | Ảnh hai lượt |
| A09 | Nút mắt đăng nhập/đổi mật khẩu/tạo tài khoản | Hiện/ẩn từng ô, không tự submit | Ảnh dùng mật khẩu giả |
| A10 | Chat → tải lại trang | Không có lịch sử cũ; không sidebar, không tự đặt tên | Ảnh trước/sau |
| A11 | Dừng và Tạo lại | Dừng phần hiển thị; tạo lại dùng ngữ cảnh trước câu hỏi | Ảnh |
| A12 | Nhập lô, bán, hết hạn, tồn thấp, báo cáo | Đối chiếu số lượng/giá/hóa đơn giữa UI và DB | Ảnh + log |

## 5. Bảng kết quả thực tế (nhóm tự điền)

| Ngày | Người kiểm thử | Mã ca | Phiên bản/commit | Đạt/Không đạt | Đường dẫn ảnh/log | Ghi chú |
| --- | --- | --- | --- | --- | --- | --- |
| | | | | | | |

Đề có yêu cầu dùng AI trong SDLC: lưu prompt/đầu ra AI/điều chỉnh và commit thật. Tài liệu này không thay thế việc nhóm chạy nghiệm thu.
