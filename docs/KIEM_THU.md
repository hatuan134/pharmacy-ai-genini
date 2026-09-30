# Kiểm thử bản hiện hành

Kết quả mới nhất nằm trong `AI_V4_TEST_REPORT.md`. Các số liệu ở báo cáo v3 là lịch sử, không phải bằng chứng cho v4.

Quy trình nghiệm thu chi tiết, lệnh chạy PostgreSQL/Gemini và bảng lưu ảnh/log: `NGHIEM_THU_V4.md`.

Bộ test backend dùng SQLite in-memory và fake provider; chặn HTTP ngoài. Test PostgreSQL chỉ chạy khi đặt TEST_POSTGRES_URL tới database kiểm thử riêng. Test frontend dùng jsdom, không thay thế quan sát bằng trình duyệt thật. Windows CMD cần chạy trên máy Windows của nhóm.
