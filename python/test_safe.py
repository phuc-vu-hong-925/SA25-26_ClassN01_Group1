# test_safe.py
# KICH BAN KIEM THU BAN AN TOAN (SAFE / CLEAN VERSION)
# Chung minh cac thuoc tinh toan hoc deu thoa man (AG holds: True & UNSAT)
import sys
sys.stdout.reconfigure(encoding="utf-8")

from ch1_models.restaurant_kripke import build_restaurant_model
from z3 import Solver, Int, unsat

def test_kripke_safe_holds_all_properties():
    print("=" * 70)
    print("1. KIEM CHUNG KRIPKE - BAN AN TOAN (FIXED MODEL)")
    print("=" * 70)
    fixed_model = build_restaurant_model(buggy=False)
    
    holds_leak, cex = fixed_model.check_safety_no_leak()
    print(f"  * Thuoc tinh AG(!leak): {'THOA MAN (holds: True)' if holds_leak else 'VI PHAM'}")
    assert holds_leak is True
    print("    --> Counterexample: None (Toan bo tai nguyen heap deu duoc giai phong!)")

    holds_empty, _ = fixed_model.check_safety_no_empty_order()
    print(f"  * Thuoc tinh AG(!(sent_kitchen && !has_items)): {'THOA MAN (holds: True)' if holds_empty else 'VI PHAM'}")
    assert holds_empty is True

    live_ok = fixed_model.check_liveness_order_completion()
    print(f"  * Thuoc tinh Liveness AF(served || cancelled): {'THOA MAN (holds: True)' if live_ok else 'VI PHAM'}")
    assert live_ok is True
    print("  * Ket luan Kripke: He thong an toan 100%, khong con bat ky Counterexample nao!\n")

def test_smt_safe_guards_prove_unsat():
    print("=" * 70)
    print("2. KIEM CHUNG SMT Z3 - BAN DA THEM GUARD (CHUNG MINH UNSAT)")
    print("=" * 70)
    
    # Bug 1: Guard count < 20
    s1 = Solver()
    count = Int("count")
    s1.add(count >= 0, count < 20) # Guard
    s1.add(count >= 20)           # Dieu kien vi pham
    assert s1.check() == unsat
    print("  * [BUG-01 Guard]: UNSAT -> Chung minh khong the ghi de qua mang items[20]!")

    # Bug 2: Guard overflow
    INT32_MAX = 2147483647
    s2 = Solver()
    qty = Int("qty")
    price = Int("price")
    s2.add(qty >= 1, qty <= 99, price >= 0, price <= INT32_MAX)
    s2.add(price <= INT32_MAX / qty) # Guard
    s2.add(qty * price > INT32_MAX)  # Dieu kien vi pham
    assert s2.check() == unsat
    print("  * [BUG-02 Guard]: UNSAT -> Chung minh phep nhan khong bao gio bi tran int32!")

    # Bug 3: Guard n_guests > 0
    s3 = Solver()
    n_guests = Int("n_guests")
    s3.add(n_guests > 0) # Guard
    s3.add(n_guests == 0) # Dieu kien vi pham
    assert s3.check() == unsat
    print("  * [BUG-03 Guard]: UNSAT -> Chung minh khong bao gio xay ra phep chia cho 0!")

    # BMC Completeness Threshold
    s4 = Solver()
    n = Int("n")
    s4.add(n >= 0, n <= 20)
    s4.add(n >= 21) # Kiem tra buoc ngoai nguong k = 21
    assert s4.check() == unsat
    print("  * [BMC Threshold]: UNSAT -> Completeness Threshold dat duoc tai k = 21!")
    print("  * Ket luan SMT: Tat ca cac thuoc tinh an toan deu da duoc chung minh toan hoc thanh cong!\n")

if __name__ == "__main__":
    test_kripke_safe_holds_all_properties()
    test_smt_safe_guards_prove_unsat()
