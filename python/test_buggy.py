# test_buggy.py
# KICH BAN KIEM THU BAN CO LOI (BUGGY VERSION)
# Chung minh cac cong cu phat hien duoc loi that (Counterexample & SAT Models)
import sys
sys.stdout.reconfigure(encoding="utf-8")

from ch1_models.restaurant_kripke import build_restaurant_model
from z3 import Solver, Int, sat

def test_kripke_buggy_detects_counterexample():
    print("=" * 70)
    print("1. KIEM CHUNG KRIPKE - BAN CO LOI (BUGGY MODEL)")
    print("=" * 70)
    buggy_model = build_restaurant_model(buggy=True)
    holds_leak, cex_leak = buggy_model.check_safety_no_leak()
    
    print(f"  * Thuoc tinh AG(!leak): {'THOA MAN' if holds_leak else 'VI PHAM (holds: False)'}")
    assert holds_leak is False
    print(f"  * Phao chung (Counterexample path): {' -> '.join(cex_leak)}")
    print("  * Ket luan: Mo hinh Kripke da bat dung loi huy don gay leak bo nho!\n")

def test_smt_buggy_finds_vulnerabilities():
    print("=" * 70)
    print("2. KIEM CHUNG SMT Z3 - BAN CHUA CO GUARD (TIM PHAN VI DU)")
    print("=" * 70)
    
    # Bug 1: Index OOB
    s1 = Solver()
    count = Int("count")
    s1.add(count >= 0, count >= 20)
    assert s1.check() == sat
    print(f"  * [BUG-01 Index OOB]: SAT -> Phan vi du count = {s1.model()[count]}")

    # Bug 2: Integer Overflow
    INT32_MAX = 2147483647
    s2 = Solver()
    qty = Int("qty")
    price = Int("price")
    s2.add(qty >= 1, qty <= 99, price >= 0, price <= INT32_MAX)
    s2.add(qty * price > INT32_MAX)
    assert s2.check() == sat
    m = s2.model()
    print(f"  * [BUG-02 Overflow]:  SAT -> Phan vi du qty = {m[qty]}, price = {m[price]}")

    # Bug 3: Divide by zero
    s3 = Solver()
    n_guests = Int("n_guests")
    s3.add(n_guests == 0)
    assert s3.check() == sat
    print(f"  * [BUG-03 Div-by-zero]: SAT -> Phan vi du n_guests = {s3.model()[n_guests]}")
    print("  * Ket luan: Z3 da giai thanh cong tat ca cac gia tri tan cong gay loi!\n")

if __name__ == "__main__":
    test_kripke_buggy_detects_counterexample()
    test_smt_buggy_finds_vulnerabilities()
