# API hiện tại

Prefix `/api`, cookie session HttpOnly. POST/PUT/PATCH/DELETE cần header `X-Requested-With: pharmacy`. Xem `/docs` của server để biết đầy đủ schema và validation.

| Endpoint | Method | Mục đích |
| --- | --- | --- |
| /auth/login, /auth/logout | POST | Đăng nhập/đăng xuất |
| /auth/me | GET | Tài khoản hiện tại |
| /auth/password | POST | Đổi mật khẩu |
| /users | GET, POST | Quản lý xem/tạo tài khoản |
| /users/{id} | PATCH | Quản lý đổi quyền/trạng thái |
| /medicines, /categories, /units, /suppliers, /procedures | GET, POST | Danh mục theo quyền |
| Các danh mục/{id} | PUT, DELETE | Sửa/xóa theo quyền, FK bảo vệ |
| /medicines/{id}/approval | POST | Manager/pharmacist duyệt/thu hồi mô tả thuốc |
| /batches | GET, POST | Tìm/nhập lô |
| /batches/{id}/price | PATCH | Staff sửa giá |
| /batches/{id}/adjust | POST | Staff kiểm kê có kiểm tra số dư cũ |
| /movements | GET | Biến động kho |
| /invoices | GET, POST | Danh sách/tạo hóa đơn |
| /invoices/{id} | GET | Chi tiết |
| /invoices/{id}/cancel | POST | Quản lý hủy |
| /alerts, /dashboard, /reports | GET | Cảnh báo/tổng quan/báo cáo theo quyền |
| /ai/session/{UUID}/stream | POST | Chat mới không lưu, NDJSON streaming |
| /ai/session/{UUID}/stop | POST | Hủy yêu cầu đang chạy của chính tài khoản |
| /ai/ask, /ai/chat, /ai/chat/stream | POST | API cũ tương thích |
| /ai/logs | GET | Nhật ký legacy theo quyền cũ; chat mới không ghi |

Không còn `/ai/conversations` hoặc endpoint tự đặt tên/hội thoại. Không có `/approval-requests` cho duyệt tồn/giá.

## Duyệt thuốc

GET `/medicines` trả `approved`, `approved_by`, `approval_revision`. Sau khi người dùng đọc thông tin, POST:

```json
{"approved":true,"revision":"SHA256_64_KY_TU_TU_BAN_GHI_DA_XEM"}
```

Không tự tính hoặc bỏ revision. 409 nếu nội dung đổi; 403 nếu không có quyền; 422 nếu nội dung trống. Sửa thuốc hủy duyệt, không thể tự gửi approved=true qua PUT để duyệt.

## Chat phiên

```json
{"message":"Tóm tắt thông tin PCT","history":[{"role":"user","content":"Tình hình PCT thế nào?"}],"agent":true}
```

UUID mới cho mỗi lần hỏi; giữ UUID để gửi stop. Event: activity, meta (sources/used_tools/route), model, delta, done, error. Không có title event. History tối đa 12 tin, mỗi tin 4.000 ký tự. Không thực thi HTML từ phản hồi AI.
