/*
 * restaurant_order.c
 * Hien thuc 6 ham F1 -> F6 theo luong goi mon
 * Co ho tro chuyen doi giua Ban loi (-DDEMO_BUG) va Ban an toan.
 */
#include "restaurant_order.h"

/* 
 * F1: open_session(table_id)
 * Mo phien ban, cap phat Order struct tren Heap
 */
Order* open_session(int table_id) {
#ifdef DEMO_BUG
    /* Ban loi: Khong kiem tra table_id hop le */
    Order* order = (Order*)malloc(sizeof(Order));
    order->table_id = table_id;
    order->item_count = 0;
    order->total_price = 0;
    order->status = STATUS_BROWSING;
    return order;
#else
    /* Ban an toan: Kiem tra table_id trong [1, 50] va kiem tra malloc */
    if (table_id < MIN_TABLE_ID || table_id > MAX_TABLE_ID) {
        return NULL;
    }
    Order* order = (Order*)malloc(sizeof(Order));
    if (!order) return NULL;
    
    order->table_id = table_id;
    order->item_count = 0;
    order->total_price = 0;
    order->status = STATUS_BROWSING;
    return order;
#endif
}

/* 
 * F2: add_item(order, name, qty, price)
 * Them mon vao don hang
 */
int add_item(Order* order, const char* name, int qty, int price) {
    if (!order) return -1;

#ifdef DEMO_BUG
    /* 
     * Ban loi: 
     * 1. Khong kiem tra item_count < MAX_ITEMS (gay Index Out-Of-Bounds)
     * 2. Dung strcpy gay Buffer Overflow neu strlen(name) >= 32
     */
    strcpy(order->items[order->item_count].name, name);
    order->items[order->item_count].qty = qty;
    order->items[order->item_count].price = price;
    order->item_count++;
    order->status = STATUS_ORDERING;
    return 0;
#else
    /* 
     * Ban an toan: 
     * 1. Kiem tra gioi han mảng MAX_ITEMS (20)
     * 2. Dung strncpy kem dat null-terminator
     * 3. Kiem tra qty in [1, 99], price >= 0
     */
    if (order->item_count >= MAX_ITEMS) {
        return -2; /* Loi: Mang mon da day */
    }
    if (qty < MIN_QTY || qty > MAX_QTY || price < 0 || !name) {
        return -3; /* Loi: Tham so khong hop le */
    }

    strncpy(order->items[order->item_count].name, name, MAX_NAME_LEN - 1);
    order->items[order->item_count].name[MAX_NAME_LEN - 1] = '\0';
    order->items[order->item_count].qty = qty;
    order->items[order->item_count].price = price;
    order->item_count++;
    order->status = STATUS_ORDERING;
    return 0;
#endif
}

/*
 * F3: calc_total(order) & split_bill(total, n_guests)
 * Tinh tong tien va chia hoa don
 */
int calc_total(Order* order) {
    if (!order) return -1;

    order->total_price = 0; /* Reset truoc khi tinh, tranh cong chong neu goi nhieu lan */

#ifdef DEMO_BUG
    /* Ban loi: Nhan truc tiep int32, khong kiem tra tran so.
     * Neu qty * price > INT32_MAX thi bi wrap-around (CWE-190). */
    for (int i = 0; i < order->item_count; i++) {
        order->total_price += order->items[i].qty * order->items[i].price;
    }
#else
    /* Ban an toan: Dung long long de kiem tra tran truoc, sau do moi ghi vao int. */
    long long total = 0;
    for (int i = 0; i < order->item_count; i++) {
        long long subtotal = (long long)order->items[i].qty * order->items[i].price;
        if (subtotal > INT_MAX || total + subtotal > INT_MAX) {
            return -1; /* Bao loi tran so, khong ghi gia tri sai vao order */
        }
        total += subtotal;
    }
    order->total_price = (int)total;
#endif

    return order->total_price;
}

int split_bill(int total, int n_guests) {
#ifdef DEMO_BUG
    /* Ban loi: Chia truc tiep, crash neu n_guests == 0 */
    return total / n_guests;
#else
    /* Ban an toan: Kiem tra chia cho 0 */
    if (n_guests <= 0) return -1;
    return total / n_guests;
#endif
}

/* 
 * F4: submit_order(kq, order)
 * Gui don vao hang doi bep
 */
int submit_order(KitchenQueue* kq, Order* order) {
    if (!kq || !order) return -1;

#ifdef DEMO_BUG
    /* Ban loi: Cho phep gui ca don rong chua co mon */
    kq->orders[kq->tail] = order;
    kq->tail = (kq->tail + 1) % MAX_QUEUE;
    kq->count++;
    order->status = STATUS_SUBMITTED;
    return 0;
#else
    /* Ban an toan: Bat buoc phai co mon (item_count > 0) va hang doi chua day */
    if (order->item_count <= 0) {
        return -2; /* Khong the gui don rong len bep */
    }
    if (kq->count >= MAX_QUEUE) {
        return -3; /* Hang doi bep da day */
    }

    kq->orders[kq->tail] = order;
    kq->tail = (kq->tail + 1) % MAX_QUEUE;
    kq->count++;
    order->status = STATUS_SUBMITTED;
    return 0;
#endif
}

/* 
 * F5: kitchen_process(kq)
 * Bep lay don tu hang doi de che bien va phuc vu
 */
Order* kitchen_process(KitchenQueue* kq) {
    if (!kq || kq->count == 0) return NULL;

    Order* order = kq->orders[kq->head];
    kq->head = (kq->head + 1) % MAX_QUEUE;
    kq->count--;

    order->status = STATUS_COOKING;
    /* Mo phong nau va phuc vu */
    order->status = STATUS_SERVED;
    return order;
}

/* 
 * F6: pay_or_cancel(order_ptr, is_paid)
 * Thanh toan hoac huy, giai phong tai nguyen
 */
void pay_or_cancel(Order** order_ptr, int is_paid) {
    if (!order_ptr || !*order_ptr) return;

#ifdef DEMO_BUG
    /* Ban loi: Neu khach huy (is_paid == 0), quen free(order) -> Memory Leak! */
    if (is_paid) {
        (*order_ptr)->status = STATUS_PAID;
        free(*order_ptr);
        *order_ptr = NULL;
    } else {
        (*order_ptr)->status = STATUS_CANCELLED;
        /* LEAK: Thieu free(*order_ptr) o day */
    }
#else
    /* Ban an toan: Giai phong bo nho tren MOI nhanh va dat con tro ve NULL */
    if (is_paid) {
        (*order_ptr)->status = STATUS_PAID;
    } else {
        (*order_ptr)->status = STATUS_CANCELLED;
    }
    free(*order_ptr);
    *order_ptr = NULL;
#endif
}

/* Ham main de test luong 6 ham hoat dong dong bo */
int main() {
    printf("--- DEMO CHAY LUONG GOI MON F1 -> F6 ---\n");
    
    /* F1: Mo phien */
    Order* order = open_session(10);
    if (!order) {
        printf("Loi mo ban!\n");
        return 1;
    }
    printf("[F1] Mo ban 10 thanh cong.\n");

    /* F2: Them 3 mon */
    add_item(order, "Pho Bo Dac Biet", 2, 65000);
    add_item(order, "Tra Chanh", 2, 15000);
    add_item(order, "Quay Gion", 4, 5000);
    printf("[F2] Da them %d mon vao don.\n", order->item_count);

    /* F3: Tinh tien */
    int total = calc_total(order);
    printf("[F3] Tong tien don hang: %d VND\n", total);
    printf("     Chia deu 2 nguoi: %d VND/nguoi\n", split_bill(total, 2));

    /* F4: Gui bep */
    KitchenQueue kq = {0};
    submit_order(&kq, order);
    printf("[F4] Da gui don vao bep, trang thai: %d\n", order->status);

    /* F5: Bep che bien */
    Order* processed = kitchen_process(&kq);
    printf("[F5] Bep da phuc vu mon, trang thai: %d\n", processed->status);

    /* F6: Thanh toan va giai phong */
    pay_or_cancel(&order, 1);
    printf("[F6] Da thanh toan va giai phong bo nho. Con tro order = %p\n", (void*)order);

    printf("--- HOAN TAT LUONG 6 HAM AN TOAN! ---\n");
    return 0;
}
