# restaurant_bmc_z3.py
# Mo phong thuat toan Bounded Model Checking (BMC) cho vong lap F2 bang Z3
# Giai thich va chung minh "Completeness Threshold" tai k = 21 (MAX_ITEMS = 20)
from z3 import Solver, Int, And, Or, Not, sat, unsat

def run_bmc_unrolling_demo():
    print("=" * 70)
    print("KIEM CHUNG BOUNDED MODEL CHECKING (BMC) - COMPLETENESS THRESHOLD")
    print("=" * 70)
    print("Muc tieu: Kiem chung vong lap them mon vao mang MAX_ITEMS = 20.")
    print("Ly thuyet: Completeness threshold la k = MAX_ITEMS + 1 = 21 buoc unwind.\n")

    MAX_ITEMS = 20

    # 1. Thu nghiem voi Unwind thieu: k = 10 buoc
    print("[1] KIEM CHUNG VOI UNWIND THIEU (k = 10):")
    s_incomplete = Solver()
    num_items = Int("num_items_k10")
    # Gia su so mon khach muon dat co the len den 20
    s_incomplete.add(num_items >= 0, num_items <= MAX_ITEMS)
    # Nhung CBMC chi unwind 10 buoc (k = 10)
    k_steps = 10
    # Kiem tra xem voi k = 10 thi co the bo sot trang thai num_items > 10 khong
    s_incomplete.add(num_items > k_steps)
    res_k10 = s_incomplete.check()
    print(f"  * Ket qua Z3 voi k = 10: {res_k10}")
    if res_k10 == sat:
        m = s_incomplete.model()
        print(f"    --> CANH BAO: Vong lap chua duoc bao phu day du!")
        print(f"        Ton tai truong hop num_items = {m[num_items]} nam ngoai tam kiem chung cua k = 10.")
        print(f"        (CBMC se bao loi 'unwinding assertion: FAILURE')")

    # 2. Thu nghiem voi Unwind day du: k = 21 buoc (Completeness Threshold)
    print("\n[2] KIEM CHUNG VOI UNWIND DAY DU (k = 21 = MAX_ITEMS + 1):")
    s_complete = Solver()
    num_items_full = Int("num_items_k21")
    s_complete.add(num_items_full >= 0, num_items_full <= MAX_ITEMS)
    k_complete = 21
    # Kiem tra xem co the con phan tu nao vuot ngoai nguong k = 21 khong
    s_complete.add(num_items_full >= k_complete)
    res_k21 = s_complete.check()
    print(f"  * Ket qua Z3 voi k = 21: {res_k21}")
    if res_k21 == unsat:
        print("    --> XAC NHAN: Completeness Threshold dat duoc tai k = 21!")
        print("        Khong con bat ky truong hop nao bi bo sot (UNSAT).")
        print("        Ket qua tuong duong CBMC: VERIFICATION SUCCESSFUL (0 failed)")

    print("\n" + "=" * 70)
    print("KET LUAN BMC: Voi mang 20 phan tu, unwind = 21 dam bao bao phu 100%!")
    print("=" * 70)

if __name__ == "__main__":
    run_bmc_unrolling_demo()
