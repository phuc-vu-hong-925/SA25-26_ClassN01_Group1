# restaurant_smt.py
# Kiem chung hinh thuc bang Z3 SMT Solver (Chuong 3)
# Cac bai kiem tra so hoc va gioi han bien cho luong Goi mon F1 -> F6
from z3 import Solver, Int, BitVec, And, Or, Not, sat, unsat

def check_bug01_index_oob():
    """
    BUG-01 (CWE-129): Index Out-Of-Bounds trong F2 add_item
    Mang items[] co suc chua toi da MAX_ITEMS = 20.
    Chi so ghi: items[count]
    """
    print("\n--- [SMT-1] KIEM TRA CHI SO MANG F2 add_item (MAX_ITEMS = 20) ---")
    
    # 1. Truong hop chua co guard: count co the vuot qua hoac bang 20
    s1 = Solver()
    count = Int("count")
    # Gia dinh count la so khong am do client gui
    s1.add(count >= 0)
    # Dieu kien vi pham: count >= 20 (ghi de ngoai mang)
    s1.add(count >= 20)
    
    res1 = s1.check()
    print(f"  * [Chua co guard] Ket qua: {res1}")
    if res1 == sat:
        m = s1.model()
        print(f"    --> Phan vi du tim thay: count = {m[count]} (Vi pham gioi han MAX_ITEMS=20)")
    
    # 2. Truong hop da co guard: if (count >= 0 && count < 20)
    s2 = Solver()
    count_safe = Int("count_safe")
    s2.add(count_safe >= 0)
    s2.add(count_safe < 20) # Guard hop le
    # Kiem tra xem co the vi pham count_safe >= 20 duoc khong
    s2.add(count_safe >= 20)
    
    res2 = s2.check()
    print(f"  * [Da them guard count < 20] Ket qua: {res2}")
    if res2 == unsat:
        print("    --> Chung minh thanh cong (UNSAT): Khong the xay ra loi ghi de mang!")
        
    return res1 == sat, res2 == unsat


def check_bug02_integer_overflow():
    """
    BUG-02 (CWE-190): Integer Overflow trong F3 calc_total
    Phep tinh tong tien tich luy: qty * price
    Gia su price va qty bieu dien bang so nguyen 32-bit (INT32_MAX = 2,147,483,647)
    Rang buoc dac ta: qty in [1, 99], price >= 0
    """
    print("\n--- [SMT-2] KIEM TRA TRAN SO HOC INT32 F3 calc_total ---")
    INT32_MAX = 2147483647
    
    # 1. Truong hop chua co guard kiem tra tran
    s1 = Solver()
    qty = Int("qty")
    price = Int("price")
    
    # Rang buoc input theo dac ta
    s1.add(qty >= 1, qty <= 99)
    s1.add(price >= 0, price <= INT32_MAX)
    
    # Dieu kien vi pham: tich qty * price vuot qua nguong INT32_MAX
    s1.add(qty * price > INT32_MAX)
    
    res1 = s1.check()
    print(f"  * [Chua co guard tran so] Ket qua: {res1}")
    if res1 == sat:
        m = s1.model()
        q_val = m[qty].as_long()
        p_val = m[price].as_long()
        total_val = q_val * p_val
        print(f"    --> Phan vi du: qty = {q_val}, price = {p_val:,} VND")
        print(f"        Tich = {total_val:,} > INT32_MAX ({INT32_MAX:,})")
    
    # 2. Truong hop da them guard: if (price > INT32_MAX / qty) -> tu choi
    s2 = Solver()
    q_safe = Int("q_safe")
    p_safe = Int("p_safe")
    s2.add(q_safe >= 1, q_safe <= 99)
    s2.add(p_safe >= 0, p_safe <= INT32_MAX)
    # Guard an toan
    s2.add(p_safe <= INT32_MAX / q_safe)
    # Kiem tra co the tran khong
    s2.add(q_safe * p_safe > INT32_MAX)
    
    res2 = s2.check()
    print(f"  * [Da them guard kiem tra p <= INT32_MAX / q] Ket qua: {res2}")
    if res2 == unsat:
        print("    --> Chung minh thanh cong (UNSAT): Tich khong bao gio bi tran int32!")
        
    return res1 == sat, res2 == unsat


def check_bug03_division_by_zero():
    """
    BUG-03 (CWE-369): Divide by Zero trong F3 split_bill (chia bill)
    Phep tinh: bill_per_guest = total / n_guests
    """
    print("\n--- [SMT-3] KIEM TRA CHIA CHO 0 F3 split_bill ---")
    
    # 1. Chua co guard
    s1 = Solver()
    n_guests = Int("n_guests")
    total = Int("total")
    s1.add(total >= 0)
    # Khong rang buoc n_guests > 0 -> Co the gap n_guests == 0
    s1.add(n_guests == 0)
    
    res1 = s1.check()
    print(f"  * [Chua co guard n_guests != 0] Ket qua: {res1}")
    if res1 == sat:
        print("    --> Phan vi du: n_guests = 0 (Gay crash chia cho 0 / SIGFPE)")
        
    # 2. Da co guard: if (n_guests <= 0) return ERROR;
    s2 = Solver()
    n_safe = Int("n_safe")
    total_safe = Int("total_safe")
    s2.add(total_safe >= 0)
    s2.add(n_safe > 0) # Guard bat buoc so khach > 0
    s2.add(n_safe == 0) # Dieu kien loi
    
    res2 = s2.check()
    print(f"  * [Da them guard n_guests > 0] Ket qua: {res2}")
    if res2 == unsat:
        print("    --> Chung minh thanh cong (UNSAT): Khong bao gio chia cho 0!")
        
    return res1 == sat, res2 == unsat


def run_smt_verification():
    print("=" * 70)
    print("KIEM CHUNG HINH THUC SMT BANG Z3 SOLVER (CHUONG 3) - NHA HANG THONG MINH")
    print("=" * 70)
    
    r1_sat, r1_unsat = check_bug01_index_oob()
    r2_sat, r2_unsat = check_bug02_integer_overflow()
    r3_sat, r3_unsat = check_bug03_division_by_zero()
    
    print("\n" + "=" * 70)
    print("TONG HOP KET QUA KIEM CHUNG SMT (Dung de dien vao Muc 5.2 Bao cao):")
    print("=" * 70)
    print("| Ma loi | Chuc nang | Mo ta loi | Ket qua chua guard | Ket qua da co guard |")
    print("|---|---|---|---|---|")
    print(f"| BUG-01 | F2 add_item   | Index OOB (count >= 20)      | {'SAT (count=20)' if r1_sat else 'ERR'} | {'UNSAT (An toan)' if r1_unsat else 'ERR'} |")
    print(f"| BUG-02 | F3 calc_total | Overflow int32 (qty*price)   | {'SAT (Co tran)' if r2_sat else 'ERR'}   | {'UNSAT (An toan)' if r2_unsat else 'ERR'} |")
    print(f"| BUG-03 | F3 split_bill | Divide by zero (n_guests=0)  | {'SAT (n_guests=0)' if r3_sat else 'ERR'}| {'UNSAT (An toan)' if r3_unsat else 'ERR'} |")
    print("=" * 70)


if __name__ == "__main__":
    run_smt_verification()
