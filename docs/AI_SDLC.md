# AI trong SDLC — bản nguồn đã duyệt, chat không lưu

## Kiến trúc hiện tại

FastAPI/SQLAlchemy/PostgreSQL + React/Vite + Gemini. Chat giữ tối đa 12 tin nhắn gần nhất trong bộ nhớ giao diện để hỏi tiếp, không ghi hội thoại vào database, không tạo tiêu đề, không có sidebar mở lại lịch sử. Làm mới/rời trang/tải lại trang sẽ mất phiên chat. Các bảng chat của bản cũ được giữ nguyên để không phá dữ liệu, nhưng không còn API truy cập. Đánh giá 👍/👎 chỉ ở phiên hiện tại.

Thông tin mô tả thuốc phải được quản lý/dược sĩ xác nhận tại Thuốc → Kiểm tra nguồn AI. Xác nhận kiểm tra revision SHA-256 và khóa dòng; nếu nội dung thay đổi trong lúc duyệt, API trả 409. Sửa thuốc hủy duyệt. Công cụ medicine_search và API tóm tắt cũ chỉ đọc mô tả đã duyệt. Công cụ tồn kho vẫn đọc số liệu nghiệp vụ của thuốc chưa duyệt; Dynamic Query không có cột information/source nên không dùng để đọc vòng qua mô tả chưa duyệt.

Agent chọn nhiều công cụ, giữ medicine_search khi tóm tắt thuốc xác định, có tối đa hai vòng chọn công cụ, tổng cộng 6 tool calls. RAG chọn các đoạn tài liệu thật rồi dùng Gemini chọn theo ngữ nghĩa. Gemini sinh câu trả lời bằng streaming; dữ liệu nguồn là dữ liệu không phải chỉ dẫn. Fallback phải nói rõ chưa có phân tích AI.

## Minh chứng có trong gói

- Source frontend/backend, bộ test, hướng dẫn cập nhật và nghiệm thu.
- Test dùng dữ liệu giả, chặn HTTP ngoài; kết quả cụ thể xem AI_V4_TEST_REPORT.md.
- Script verify_gemini.py chỉ gửi fixture tổng hợp, không đọc database. Chưa chạy bằng khóa của nhóm trong môi trường bàn giao.
- Test PostgreSQL dùng schema ngẫu nhiên trên database kiểm thử riêng; không dùng dữ liệu production.

## Nhật ký nhóm cần điền bằng hoạt động thật

| Giai đoạn | Minh chứng cần lưu |
| --- | --- |
| Phân tích | Đề 14, prompt yêu cầu, quyết định giới hạn AI |
| Thiết kế | ERD, quyền quản lý/dược sĩ/thu ngân, cơ chế duyệt nguồn, transaction hóa đơn |
| Lập trình | Prompt nguyên văn, phản hồi AI, diff/commit thực tế, các chỉnh sửa thủ công |
| Kiểm thử | Log pytest/vitest, kết quả PostgreSQL, file Gemini live, ảnh UI và nhận xét |
| Triển khai | Cách chạy local/Render, ngày thực hiện, lỗi gặp và cách xử lý |

Không dùng prompt mẫu làm bằng chứng rằng đã chạy model. Không tự điền ngày, người thực hiện, kết quả đạt hoặc commit chưa tồn tại.

## Prompt nghiệm thu mẫu

“Đối chiếu yêu cầu đề 14 với source đính kèm. Kiểm tra chỉ nội dung thuốc đã duyệt được gửi cho Gemini, sửa thuốc phải hủy duyệt, thu ngân không có quyền duyệt, câu tóm tắt thuốc lấy mô tả chứ không chỉ lấy tồn. Kiểm tra chat không lưu và không đặt tên; nút mắt không submit form. Nêu lỗi có bằng chứng, không coi test giả lập là kiểm thử Gemini/PostgreSQL thật.”
