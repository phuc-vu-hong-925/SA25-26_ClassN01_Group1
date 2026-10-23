# BÀI TẬP LỚN AN TOÀN PHẦN MỀM
## Mô hình hóa và Kiểm chứng hình thức Hệ thống Nhà hàng Thông minh

**Học phần:** CSE703093 – An toàn phần mềm | **Giảng viên:** ThS. Vũ Quang Dũng
**Sinh viên:** Đặng Ngọc Đức (23010803) – Vũ Hồng Phúc (23010639) 

---

## Cấu trúc thư mục

```
CodeATPM/
├── python/
│   ├── ch1_models/restaurant_kripke.py     # Kripke model Ch1
│   ├── ch3_verify/restaurant_smt.py        # Z3 SMT Ch3
│   ├── ch3_verify/restaurant_bmc_z3.py     # BMC Ch3
│   ├── test_restaurant.py                  # Pytest tổng hợp
│   ├── test_buggy.py                       # Test bản lỗi
│   └── test_safe.py                        # Test bản an toàn
└── c/
    ├── restaurant_order.h / .c             # 6 hàm F1→F6
    ├── test_order_buggy.c                  # Demo lỗi + ASan
    └── test_order_safe.c                   # Demo an toàn
```

---

## Cài đặt

```bash
pip install z3-solver pytest
```

---

## Quy trình chạy

### Bước 1 — Kripke model (Ch1)

```powershell
cd D:\CodeATPM\python
python ch1_models/restaurant_kripke.py
```

Kết quả mong đợi:
- Bản lỗi: `holds: False` → counterexample `browsing → cancelled → idle`
- Bản đúng: `holds: True` → không còn đường leak

---

### Bước 2 — Z3 SMT (Ch3)

```powershell
python ch3_verify/restaurant_smt.py
```

Kết quả mong đợi:
- BUG-01: SAT (`count=20`) → UNSAT sau guard
- BUG-02: SAT (`qty=80, price=1,736,074,747`) → UNSAT sau guard
- BUG-03: SAT (`n_guests=0`) → UNSAT sau guard

---

### Bước 3 — BMC Completeness Threshold (Ch3)

```powershell
python ch3_verify/restaurant_bmc_z3.py
```

Kết quả mong đợi:
- `k=10`: SAT → chưa đủ, bỏ sót trường hợp
- `k=21`: UNSAT → đạt completeness threshold 100%

---

### Bước 4 — Pytest tổng hợp

```powershell
python -m pytest test_restaurant.py -v
```

Kết quả mong đợi: `6 passed in 0.13s`

---

### Bước 5 — ASan bản lỗi (WSL)

```bash
cd /mnt/d/CodeATPM/c
gcc -fsanitize=address,undefined -g -o run_test_buggy test_order_buggy.c
./run_test_buggy 2>&1
```

Kết quả mong đợi:
- `heap-buffer-overflow` tại `buggy_add_item` → CWE-129
- `signed integer overflow: 80 * 1736074747` → CWE-190
- Memory leak tại `pay_or_cancel` → CWE-401

---

### Bước 6 — ASan bản an toàn (WSL)

```bash
gcc -fsanitize=address,undefined -g -o run_test_safe test_order_safe.c
./run_test_safe 2>&1
```

Kết quả mong đợi: Chạy sạch, không có lỗi ASan nào.

---

### Bước 7 — Render đồ thị Kripke (tuỳ chọn)

```bash
# Cai graphviz neu chua co
sudo apt install graphviz

dot -Tpng python/ch1_models/restaurant_kripke_buggy.dot -o kripke_buggy.png
dot -Tpng python/ch1_models/restaurant_kripke_fixed.dot -o kripke_fixed.png
```

Hoặc paste nội dung file `.dot` vào https://dreampuf.github.io/GraphvizOnline/

---

## Xử lý sự cố

| Lỗi | Cách sửa |
|---|---|
| Chữ tiếng Việt bị lỗi trên PowerShell | Chạy `chcp 65001` trước |
| `pytest: command not found` | Dùng `python -m pytest -v` |
| Không có gcc trên Windows | Dùng WSL hoặc chạy file `.exe` có sẵn trong `c/` |
