# Nhật Ký Làm Việc Cùng AI (AI Log & Retro) — Phase 1

## 1. Ước tính Token & Chi phí
- **Model sử dụng:** Claude / Gemini (Hỗ trợ theo từng đầu việc cụ thể)
- **Token ước tính Phase 1:** ~25,000 - 35,000 tokens
- **Cách tối ưu hóa token:**
  - Giữ `AGENTS.md` ngắn gọn, súc tích (< 50 dòng), chỉ ghi rõ quy ước và lệnh build/test.
  - Tách logic thành các file nhỏ (`core/rules.py`, `core/entities.py`, `core/engine.py`), giúp AI chỉ cần đọc và sửa từng module độc lập thay vì đọc cả codebase lớn.
  - Chạy test kiểm chứng cục bộ ngay sau mỗi thay đổi thay vì hỏi AI giải thích dài dòng.

## 2. Phân tích lỗi của AI và cách khắc phục (AI Mistakes & Harness Improvements)
Trong quá trình triển khai Phase 1, đã ghi nhận 3 vấn đề kỹ thuật quan trọng:

1. **Lỗi Logic Win/Lose trong `light_lantern`:**
   - *Phát hiện:* Khi kiểm tra luồng thắp đèn lồng thứ 5, hàm `light_lantern()` ban đầu chỉ gán `l.is_lit = True` mà không gọi kiểm tra điều kiện thắng, dẫn đến việc trạng thái chỉ chuyển sang `WIN` khi bước sang frame `update()` kế tiếp.
   - *Khắc phục:* Bổ sung `self._check_win_lose()` ngay trong `light_lantern()` sau khi đèn cuối cùng được thắp sáng.
   - *Quy tắc rút ra:* Bất kỳ phương thức nào làm thay đổi trạng thái thực thể ảnh hưởng đến điều kiện thắng/thua phải kiểm tra trạng thái ngay lập tức.

2. **Lỗi môi trường ảo bị Git theo dõi:**
   - *Phát hiện:* Do encoding của file `.gitignore` ban đầu lưu dạng UTF-16 trên Windows, Git không nhận diện đúng dòng `.venv/`, dẫn đến thư viện ảo Panda3D/Ursina bị thêm vào commit git.
   - *Khắc phục:* Chuyển `.gitignore` sang định dạng UTF-8 chuẩn và loại bỏ hoàn toàn `.venv` khỏi git index (`git rm -r --cached .venv`).

3. **Lỗi Cháy sáng (White Screen) & Che lấp bản đồ trong Ursina (`render/app.py`):**
   - *Phát hiện:* Màn hình render bị lóa trắng hoàn toàn và không thấy ranh giới đảo. Nguyên nhân do AI nhầm lẫn giữa hệ màu `color.rgb(0.0-1.0)` với dải màu `0-255`, đồng thời đặt `AmbientLight` cường độ 120-150x khiến camera bị cháy sáng; và `model="circle"` trong Ursina là đĩa đặc (ngon) ở `y=0.005` đè bẹp lên toàn bộ mặt đảo.
   - *Khắc phục:* Chuyển sang dùng chuẩn `color.rgb32` / `color.rgba32`, điều chỉnh ánh sáng đêm dịu mắt, đổi viền đảo sang `Circle(mode='line')`, thêm mặt biển đêm bao quanh và 5 đường mòn lát đá định hướng rõ ràng.

## 3. Đánh giá Phase 1 (Evaluation)
- **Yêu cầu đạt được:**
  - [x] Tách biệt 100% Core Logic thuần Python (`core/`) khỏi thư viện render.
  - [x] Chế độ Headless Runner chạy theo Test Contract nhận input JSON và in output JSON từng step.
  - [x] Đầy đủ 3 scenario kiểm thử: Thắng (`scenario_win.json`), Thua (`scenario_lose.json`), Nhặt đồ (`scenario_pickup.json`).
  - [x] Tính tất định (Determinism) được chứng minh thông qua `test_deterministic` trong `_smoke_test.py`.
  - [x] Giao diện 3D chơi được mượt mà trên Ursina Engine (`render/app.py`).
