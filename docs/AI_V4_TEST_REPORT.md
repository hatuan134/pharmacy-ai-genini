# Báo cáo kiểm thử bản bàn giao v4

## Kết quả đã thực hiện

| Hạng mục | Kết quả |
| --- | --- |
| Backend `python -m pytest -q` | 48 passed, 1 skipped |
| Frontend `npm test` | 19 passed |
| Frontend `npm run build` | Thành công |
| Python compile app | Thành công |

Backend có một cảnh báo deprecation từ Starlette/AnyIO. Không ảnh hưởng kết quả kiểm thử.

## Phạm vi được xác nhận bằng test

- Chỉ manager/pharmacist duyệt mô tả; cashier bị chặn 403.
- Duyệt bằng revision cũ bị 409; sửa thuốc hủy duyệt.
- Medicine search không lấy mô tả chưa duyệt; API summary cũ chặn 422.
- Agent giữ công cụ medicine_search khi tóm tắt thuốc xác định, lấy mô tả đã duyệt thay vì chỉ tồn kho.
- Migration hủy cờ duyệt cũ đúng một lần; chạy lại giữ các duyệt mới.
- Chat phiên không ghi AI logs/messages/conversations, không có title event; URL lịch sử trả 404.
- Stop giới hạn theo chủ yêu cầu, dọn registry sau hoàn tất.
- Nút mắt đổi trạng thái từng ô và không submit form; nút mắt đăng nhập hoạt động.
- UI duyệt gửi đúng revision của bản ghi đã xem; chat không gọi endpoint lưu lịch sử và Làm mới xóa ngữ cảnh phiên.
- Các kiểm thử nghiệp vụ bán hàng, tồn, hạn dùng, phân quyền, truy vấn chỉ đọc, calendar/RAG đã có tiếp tục chạy.

## Chưa xác nhận

- PostgreSQL tích hợp bị skip: môi trường không có PostgreSQL/Docker; cài PostgreSQL không thành công do giới hạn quyền hệ thống. Chưa tuyên bố transaction/khóa dòng trên PostgreSQL thật đã được nghiệm thu. Test PostgreSQL kèm theo còn kiểm tra đọc snapshot từ DB thật, cần chạy với TEST_POSTGRES_URL trên database riêng của nhóm.
- Không gọi Gemini live bằng key/dữ liệu người dùng. Các test chặn HTTP ngoài. Script verify_gemini.py kèm theo chỉ gửi fixture tổng hợp khi người dùng tự chạy; chưa có kết quả live được điền sẵn.
- UI test dùng jsdom, chưa kiểm tra bằng trình duyệt thật/ảnh chụp của phiên bản này.
- Script CMD được rà soát nhưng chưa thực thi trên Windows trong môi trường bàn giao.

Đọc `NGHIEM_THU_V4.md` để chạy phần còn lại và lưu minh chứng thật. Báo cáo này không đồng nghĩa đề tài đã được nghiệm thu 100%.
