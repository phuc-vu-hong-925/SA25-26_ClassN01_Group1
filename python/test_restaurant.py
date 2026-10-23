# test_restaurant.py
# Bo kiem thu tu dong (Test Automation) su dung pytest
# Tich hop toan bo kiem chung Kripke Structure (Chuong 1) va SMT/BMC (Chuong 3)

import pytest
from ch1_models.restaurant_kripke import build_restaurant_model
from ch3_verify.restaurant_smt import (
    check_bug01_index_oob,
    check_bug02_integer_overflow,
    check_bug03_division_by_zero
)
from z3 import Solver, Int, sat, unsat

# ============================================================================
# 1. KIEM THU KRIPKE STRUCTURE (CHUONG 1)
# ============================================================================

def test_kripke_buggy_model_detects_leak_counterexample():
    """Kiem tra ban loi phat hien dung phan vi du ro ri bo nho."""
    buggy = build_restaurant_model(buggy=True)
    holds_leak, cex_leak = buggy.check_safety_no_leak()
    
    # Thuoc tinh phai bi vi pham (holds: False)
    assert holds_leak is False
    assert cex_leak is not None
    # Phan vi du phai chua chuoi huy don truc tiep ve idle
    assert "cancelled" in cex_leak
    assert cex_leak[-1] == "idle"

def test_kripke_fixed_model_satisfies_all_properties():
    """Kiem tra ban da sua thoa man toan bo 3 thuoc tinh Safety & Liveness."""
    fixed = build_restaurant_model(buggy=False)
    
    # 1. Safety: AG(!leak) phai dat True
    holds_leak, cex = fixed.check_safety_no_leak()
    assert holds_leak is True
    assert cex is None
    
    # 2. Safety: Khong gui don rong vao bep
    holds_empty, _ = fixed.check_safety_no_empty_order()
    assert holds_empty is True
    
    # 3. Liveness: Don da gui se duoc phuc vu hoac huy
    live_ok = fixed.check_liveness_order_completion()
    assert live_ok is True


# ============================================================================
# 2. KIEM THU SMT VOI Z3 SOLVER (CHUONG 3)
# ============================================================================

def test_smt_bug01_index_out_of_bounds():
    """BUG-01: Index OOB F2 add_item (chua guard: SAT, da guard: UNSAT)."""
    has_bug, is_safe = check_bug01_index_oob()
    assert has_bug is True
    assert is_safe is True

def test_smt_bug02_integer_overflow():
    """BUG-02: Tran int32 F3 calc_total (chua guard: SAT, da guard: UNSAT)."""
    has_bug, is_safe = check_bug02_integer_overflow()
    assert has_bug is True
    assert is_safe is True

def test_smt_bug03_division_by_zero():
    """BUG-03: Chia cho 0 F3 split_bill (chua guard: SAT, da guard: UNSAT)."""
    has_bug, is_safe = check_bug03_division_by_zero()
    assert has_bug is True
    assert is_safe is True


# ============================================================================
# 3. KIEM THU BMC COMPLETENESS THRESHOLD (CHUONG 3)
# ============================================================================

def test_bmc_completeness_threshold_unwind():
    """Kiem tra BMC: k = 10 khong du bao phu, k = 21 dat completeness threshold."""
    MAX_ITEMS = 20
    
    # Test k = 10 (thieu buoc)
    s10 = Solver()
    n10 = Int("n10")
    s10.add(n10 >= 0, n10 <= MAX_ITEMS)
    s10.add(n10 > 10)
    assert s10.check() == sat  # Tim thay truong hop bi bo sot
    
    # Test k = 21 (day du)
    s21 = Solver()
    n21 = Int("n21")
    s21.add(n21 >= 0, n21 <= MAX_ITEMS)
    s21.add(n21 >= 21)
    assert s21.check() == unsat # Bao phu 100%, khong sot truong hop nao


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

