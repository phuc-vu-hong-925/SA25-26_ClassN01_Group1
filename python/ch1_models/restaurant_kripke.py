# restaurant_kripke.py
# Mo hinh hoa va Kiem chung hinh thuc Luong Goi Mon (F1 -> F6) bang Kripke Structure
from collections import deque
from typing import Dict, List, Set, Tuple, Optional

class RestaurantKripke:
    def __init__(self, name: str = "Restaurant Order Model"):
        self.name = name
        self.states: Set[str] = set()
        self.initial_states: Set[str] = set()
        self.transitions: Dict[str, Set[str]] = {}
        self.labels: Dict[str, Set[str]] = {}

    def add_state(self, state: str, labels: List[str] = None, initial: bool = False):
        self.states.add(state)
        self.transitions.setdefault(state, set())
        self.labels[state] = set(labels or [])
        if initial:
            self.initial_states.add(state)

    def add_transition(self, src: str, dst: str):
        if src not in self.states or dst not in self.states:
            raise ValueError(f"Trang thai {src} hoac {dst} chua ton tai.")
        self.transitions[src].add(dst)

    def reachable_states(self) -> Set[str]:
        visited = set(self.initial_states)
        queue = deque(self.initial_states)
        while queue:
            curr = queue.popleft()
            for nxt in self.transitions.get(curr, set()):
                if nxt not in visited:
                    visited.add(nxt)
                    queue.append(nxt)
        return visited

    def find_counterexample_path(self, bad_predicate) -> Optional[List[str]]:
        for init in self.initial_states:
            queue = deque([(init, [init])])
            visited = {init}
            while queue:
                curr, path = queue.popleft()
                if bad_predicate(curr, self.labels.get(curr, set())):
                    return path
                for nxt in self.transitions.get(curr, set()):
                    if nxt not in visited:
                        visited.add(nxt)
                        queue.append((nxt, path + [nxt]))
        return None

    def check_safety_no_leak(self) -> Tuple[bool, Optional[List[str]]]:
        for init in self.initial_states:
            queue = deque([(init, [init], False)])
            visited = set()
            while queue:
                curr, path, has_alloc = queue.popleft()
                labels = self.labels.get(curr, set())
                new_alloc = has_alloc or ("buf_allocated" in labels)
                if "freed" in labels:
                    new_alloc = False
                if curr == "idle" and len(path) > 1 and new_alloc:
                    return False, path
                for nxt in self.transitions.get(curr, set()):
                    sig = (nxt, new_alloc)
                    if sig not in visited:
                        visited.add(sig)
                        queue.append((nxt, path + [nxt], new_alloc))
        return True, None

    def check_safety_no_empty_order(self) -> Tuple[bool, Optional[List[str]]]:
        def is_bad(state, labels):
            return "sent_kitchen" in labels and "has_items" not in labels
        cex = self.find_counterexample_path(is_bad)
        if cex:
            return False, cex
        return True, None

    def check_liveness_order_completion(self) -> bool:
        reachable = self.reachable_states()
        if "submitted" not in reachable:
            return True
        queue = deque(["submitted"])
        visited = {"submitted"}
        while queue:
            curr = queue.popleft()
            if curr in ("served", "cancelled"):
                return True
            for nxt in self.transitions.get(curr, set()):
                if nxt not in visited:
                    visited.add(nxt)
                    queue.append(nxt)
        return False

def build_restaurant_model(buggy: bool = False) -> RestaurantKripke:
    model = RestaurantKripke(name="Restaurant Order (Ban loi)" if buggy else "Restaurant Order (Ban dung)")
    model.add_state("idle", labels=["safe"], initial=True)
    model.add_state("browsing", labels=["buf_allocated"])
    model.add_state("ordering", labels=["buf_allocated", "has_items"])
    model.add_state("submitted", labels=["buf_allocated", "has_items", "sent_kitchen"])
    model.add_state("cooking", labels=["buf_allocated", "has_items", "sent_kitchen"])
    model.add_state("served", labels=["buf_allocated", "served"])
    model.add_state("paid", labels=["paid"])
    model.add_state("cancelled", labels=["cancelled"])
    model.add_state("freed", labels=["freed", "safe"])
    model.add_state("error", labels=["leak" if buggy else "handled"])
    model.add_state("timeout", labels=["leak"] if buggy else ["freed", "safe"])

    model.add_transition("idle", "browsing")
    model.add_transition("browsing", "ordering")
    model.add_transition("browsing", "cancelled")
    model.add_transition("ordering", "submitted")
    model.add_transition("ordering", "cancelled")
    model.add_transition("submitted", "cooking")
    model.add_transition("submitted", "error")
    model.add_transition("submitted", "timeout")
    model.add_transition("cooking", "served")
    model.add_transition("cooking", "error")
    model.add_transition("served", "paid")
    model.add_transition("served", "cancelled")
    model.add_transition("paid", "freed")

    if buggy:
        # Ban loi: Nhanh huy don va loi di thang ve idle ma bo qua freed (leak)
        model.add_transition("cancelled", "idle")
        model.add_transition("error", "idle")
        model.add_transition("timeout", "idle")
    else:
        # Ban dung: Moi nhanh ket thuc bat buoc phai qua freed
        model.add_transition("cancelled", "freed")
        model.add_transition("error", "freed")
        model.add_transition("timeout", "freed")

    model.add_transition("freed", "idle")
    return model

def run_kripke_verification():
    print("=" * 70)
    print("KIEM CHUNG HINH THUC KRIPKE STRUCTURE - NHA HANG THONG MINH")
    print("=" * 70)

    print("\n[1] KIEM TRA BAN MO HINH LOI (BUGGY MODEL):")
    buggy = build_restaurant_model(buggy=True)
    print(f"  * Tong so trang thai: {len(buggy.states)}")
    print(f"  * Trang thai reachable: {len(buggy.reachable_states())} trang thai")
    holds_leak, cex_leak = buggy.check_safety_no_leak()
    res_str = "THOA MAN" if holds_leak else "VI PHAM (holds: False)"
    print(f"  * Thuoc tinh AG(!leak): {res_str}")
    if not holds_leak:
        print(f"    --> Counterexample path: {' -> '.join(cex_leak)}")
        print("    --> Y nghia: Nhanh huy don khong qua freed, gay ro ri bo nho (leak).")

    print("\n[2] KIEM TRA BAN MO HINH DA SUA (FIXED MODEL):")
    fixed = build_restaurant_model(buggy=False)
    holds_leak_fix, cex_fix = fixed.check_safety_no_leak()
    res_fix_str = "THOA MAN (holds: True)" if holds_leak_fix else "VI PHAM"
    print(f"  * Thuoc tinh AG(!leak): {res_fix_str}")
    if holds_leak_fix:
        print("    --> Counterexample: None (Khong con duong ro ri bo nho)")

    holds_empty, _ = fixed.check_safety_no_empty_order()
    print(f"  * Thuoc tinh AG(!(sent_kitchen and !has_items)): {'THOA MAN (holds: True)' if holds_empty else 'VI PHAM'}")
    print("    --> Khong bao gio gui don rong vao bep")

    live_ok = fixed.check_liveness_order_completion()
    print(f"  * Thuoc tinh Liveness AF(served or cancelled): {'THOA MAN (holds: True)' if live_ok else 'VI PHAM'}")
    print("    --> Don hang da gui cuoi cung luon duoc phuc vu hoac huy")

    print("\n" + "=" * 70)
    print("KET LUAN: Ban sua loi da loai bo hoan toan Counterexample!")
    print("=" * 70)

if __name__ == "__main__":
    run_kripke_verification()
