# Thiết kế bản v4

## Nghiệp vụ và quyền

| Chức năng | Quản lý | Dược sĩ | Thu ngân |
| --- | --- | --- | --- |
| Xem thuốc/lô/cảnh báo/hóa đơn | Có | Có | Có |
| Tạo/sửa thuốc, nhập lô, sửa giá, kiểm kê | Có | Có | Không |
| Duyệt mô tả thuốc cho AI | Có | Có | Không |
| Quản lý nhóm/đơn vị/tài khoản/quy trình | Có | Không | Không |
| Quản lý nhà cung cấp | Có | Xem | Không qua API danh mục |
| Xem báo cáo toàn nhà thuốc | Có | Không | Không |
| Bán hàng | Có | Có | Có, không bán thuốc kê đơn |
| Hủy hóa đơn | Có | Không | Không |
| Chat AI đọc nghiệp vụ | Có | Có | Có, giữ phạm vi đọc như source đầu vào |

AI có phạm vi đọc riêng như bản trước, gồm số liệu doanh thu/nhà cung cấp dù UI một số vai trò không có tab tương ứng. Nếu muốn AI kế thừa chính xác quyền đọc từng API, cần thay policy này riêng. AI không được thực hiện cập nhật nghiệp vụ.

## CSDL và giao dịch

models.py là nguồn schema hiện hành. Thuốc liên kết nhóm/đơn vị; mỗi lô liên kết thuốc và nhà cung cấp, giữ số dư và giá. invoice_items chụp tên/đơn vị/giá tại lúc bán, liên kết lô thực tế. inventory_movements ghi biến động. Không coi toàn schema là 3NF thuần túy vì có snapshot hóa đơn và số dư lưu sẵn.

Bán hàng khóa các dòng lô theo thứ tự ID, kiểm tra giá/tồn/hạn/thuốc hoạt động, ghi hóa đơn và biến động trong transaction. Màn hình chọn lô theo thứ tự hạn; backend kiểm tra lô được gửi lên. Không tuyên bố backend tự phân bổ FEFO tuyệt đối cho mọi request tùy ý. Lô có hạn hôm nay cũng không được bán.

## Duyệt nguồn thuốc

Medicine giữ approved và approved_by. Thuốc mới mặc định chưa duyệt. Chỉ manager/pharmacist gọi endpoint duyệt. API khóa dòng, so sánh revision của nội dung người duyệt đã xem; nội dung trống bị từ chối. Sửa trường thuốc sẽ hủy duyệt; thu hồi duyệt được hỗ trợ. Migration một lần hủy các cờ duyệt cũ vì phiên bản trước không kiểm soát chúng.

medicine_search chỉ lấy thuốc approved=true; API tóm tắt cũ trả 422 nếu chưa duyệt. Agent giữ công cụ medicine_search cho yêu cầu tóm tắt thuốc xác định. Tồn/hạn/giá là số liệu nghiệp vụ, không bị chặn bởi trạng thái duyệt mô tả. Dynamic Query không có cột mô tả hoặc nguồn, không đọc mật khẩu/token/API key.

## AI và dữ liệu phiên

React giữ tối đa 12 tin gần nhất gửi lại backend, mỗi tin cắt tối đa 4.000 ký tự. Backend chọn công cụ rồi tổng hợp trên kết quả hiện tại; history chỉ để hiểu ngữ cảnh. Không sidebar lịch sử, không tiêu đề tự động, không ghi chat mới. API hội thoại cũ bị gỡ; các bảng/dữ liệu cũ giữ để tránh tự phá dữ liệu. API AI legacy và nhật ký legacy còn tương thích; chat phiên mới không ghi vào đó.

RAG: chia quy trình thành đoạn, shortlist có giới hạn + Gemini chọn ID nguồn theo ngữ nghĩa, chỉ chấp nhận ID thật. Gemini đọc đoạn thật để tổng hợp. Khi model lỗi, lexical fallback không giả nhận là phân tích AI. Không dùng vector database.

Dynamic Query: backend lấy bản chiếu từ PostgreSQL READ ONLY/REPEATABLE READ vào SQLite RAM. Model chỉ SELECT/JOIN/GROUP BY/WHERE/ORDER BY/LIMIT và SUM/AVG/COUNT/MIN/MAX. SQLite authorizer và query_only từ chối ghi, nhiều lệnh, bảng hệ thống, hàm khác. Tối đa 10.000 dòng/bảng, 200 dòng đầu ra, thời gian chạy SQL 2 giây. Tiền trên bản chiếu có thể có sai số số thực; báo cáo nghiệp vụ vẫn dùng Decimal.

Cancellation dùng UUID + user ID + Event trong RAM; frontend abort ngay, backend dừng khi tới ranh giới xử lý tiếp theo. Một worker như cấu hình mặc định; nếu chạy nhiều workers cần shared cancellation store. Stop không bảo đảm nhà cung cấp hoàn trả hạn mức. Đánh giá chỉ giữ trong RAM frontend.

## Giới hạn kiểm chứng

Bộ lọc prompt không là bảo đảm tuyệt đối. Thông tin đã duyệt vẫn cần người có chuyên môn kiểm tra. Test SQLite/mock không chứng minh concurrency PostgreSQL hoặc độ đúng Gemini live. Xem báo cáo v4 và ma trận nghiệm thu.
