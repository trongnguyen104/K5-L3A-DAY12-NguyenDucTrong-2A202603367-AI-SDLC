# Bảng Giả định Kỹ thuật (Assumptions) — Phase 1

> **Dự án:** Đảo Đèn Lồng (Màn 1: Đêm 1 – Đảo Bến)  
> **Nguyên tắc:** Do PRD-0 Phase 1 không quy định các con số cụ thể, toàn bộ các chỉ số dưới đây là **giả định tự đặt hợp lý** để đảm bảo game chơi được và đáp ứng Test Contract. Khi có yêu cầu thay đổi ở các phase sau, ta sẽ cập nhật tại đây và trong `core/rules.py`.

---

## 1. Máu & Sinh tồn của Mây (Player)
| Thông số | Giá trị | Đơn vị | Lý do giả định |
|---|---|---|---|
| `PLAYER_MAX_HP` | 100 | Máu (HP) | Mức chuẩn cơ bản cho game hành động/sinh tồn |
| `DAMAGE_PER_HIT` | 10 | HP/lần chạm | Đủ cho người chơi chịu được 10 lần va chạm trước khi thua |
| `HIT_COOLDOWN` | 1.0 | Giây (s) | Thời gian bất tử tạm thời sau khi va chạm để tránh bị trừ liên tục trong mỗi tick |

## 2. Ánh sáng & Đom Đóm (Fireflies & Lanterns)
| Thông số | Giá trị | Đơn vị | Lý do giả định |
|---|---|---|---|
| `FIREFLY_PICKUP_RADIUS` | 1.5 | Đơn vị tọa độ | Bán kính hợp lý để nhân vật đi ngang qua là nhặt được |
| `LANTERN_LIGHT_RADIUS` | 2.0 | Đơn vị tọa độ | Khoảng cách đủ gần để tương tác thắp sáng đèn lồng |
| `LIGHT_COST_PER_LANTERN` | 1 | Đom đóm / đèn | 1 đom đóm thắp sáng được 1 đèn lồng lớn |
| `NUM_LANTERNS` | 5 | Đèn | Cố định theo mô tả PRD-0 (5 Đèn Lồng Lớn) |

## 3. Kỹ năng Tỏa sáng (Glow)
| Thông số | Giá trị | Đơn vị | Lý do giả định |
|---|---|---|---|
| `GLOW_COST` | 1 | Đom đóm | Tiêu hao 1 đom đóm trong kho để kích hoạt ánh sáng phòng vệ |
| `GLOW_RADIUS` | 5.0 | Đơn vị tọa độ | Bán kính đẩy lùi/xua đuổi Bóng Mực |
| `GLOW_COOLDOWN` | 3.0 | Giây (s) | Tránh spam kỹ năng liên tục |

## 4. Quái vật Bóng Mực (Ink Shadow)
| Thông số | Giá trị | Đơn vị | Lý do giả định |
|---|---|---|---|
| `SHADOW_SPEED` | 2.0 | Đơn vị/giây | Tốc độ di chuyển chậm hơn người chơi (người chơi ~5.0) để có thể né |
| `SHADOW_RETREAT_TIME` | 4.0 | Giây (s) | Thời gian Bóng Mực lùi lại/dừng đuổi khi bị xua bởi ánh sáng |

## 5. Điểm số (Score) & Giả định Headless
| Thông số | Giá trị | Ghi chú |
|---|---|---|
| `SCORE_PER_FIREFLY` | +10 | Thưởng khi nhặt được 1 đom đóm |
| `SCORE_PER_LANTERN` | +50 | Thưởng khi thắp sáng được 1 đèn lồng |
| `DT_PER_STEP` | 0.1s | Mỗi bước (step) trong Headless Runner tương đương $0.1$ giây mô phỏng |
| `ISLAND_RADIUS` | 20.0 | Bán kính đảo tròn mô phỏng địa hình |
