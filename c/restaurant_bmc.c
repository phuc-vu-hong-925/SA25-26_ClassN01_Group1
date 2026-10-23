/*
 * restaurant_bmc.c
 * Kiem chung hinh thuc Bounded Model Checking (BMC) cho vong lap F2 add_item
 * Su dung cong cu CBMC (C Bounded Model Checker).
 *
 * Cau hoi ly thuyet: Voi mang co kich thuoc MAX_ITEMS = 20, can gia tri --unwind bao nhieu?
 * Dap an: Can --unwind 21 (MAX_ITEMS + 1) de dat "Completeness Threshold".
 *
 * Lenh chay tren Linux / WSL:
 *   cbmc restaurant_bmc.c --function verify_add_item_bounded --unwind 21 --unwinding-assertions --bounds-check
 */

#define MAX_ITEMS 20

typedef struct {
    char name[32];
    int qty;
    int price;
} OrderItem;

typedef struct {
    int item_count;
    OrderItem items[MAX_ITEMS];
} Order;

/* Ham them mon can kiem chung */
int add_item_safe(Order* order, int qty, int price) {
    if (order->item_count >= MAX_ITEMS) {
        return -1; /* Guard ngan chan vuot bien mang */
    }
    order->items[order->item_count].qty = qty;
    order->items[order->item_count].price = price;
    order->item_count++;
    return 0;
}

int verify_add_item_bounded(void) {
    Order order;
    order.item_count = 0;

    int num_items_to_add;
    /* Gioi han so mon khach muon them tu 0 den 20 */
    __CPROVER_assume(num_items_to_add >= 0 && num_items_to_add <= MAX_ITEMS);

    /* Vong lap can unwind 21 buoc */
    for (int i = 0; i < num_items_to_add; i++) {
        add_item_safe(&order, 1, 50000);
        /* Assert bat bien: item_count khong bao gio vuot qua MAX_ITEMS */
        __CPROVER_assert(order.item_count <= MAX_ITEMS, "item_count phai <= MAX_ITEMS");
    }

    return 0;
}

int main(void) {
    verify_add_item_bounded();
    return 0;
}
