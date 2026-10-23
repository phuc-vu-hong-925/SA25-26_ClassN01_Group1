/*
 * test_order_safe.c
 * BAN AN TOAN (SAFE / CLEAN VERSION) - Luong goi mon F1 -> F6
 * 
 * Tat ca cac loi da duoc sua va kiem soat bang Guard:
 *   - F1: Kiem tra table_id trong [1, 50], kiem tra malloc != NULL
 *   - F2: Dung strncpy gioi han 31 ky tu, kiem tra item_count < MAX_ITEMS (20)
 *   - F3: Kiem tra tran so truoc khi nhan (price <= INT_MAX / qty)
 *   - F3: Kiem tra n_guests > 0 truoc khi chia bill
 *   - F6: Giai phong bo nho free(order) tren MOI nhanh va dat con tro ve NULL
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>

#define MAX_ITEMS 20
#define MAX_NAME_LEN 32
#define MIN_TABLE_ID 1
#define MAX_TABLE_ID 50

typedef struct {
    char name[MAX_NAME_LEN];
    int qty;
    int price;
} OrderItem;

typedef struct {
    int table_id;
    int item_count;
    OrderItem items[MAX_ITEMS];
    int total_price;
    int is_paid;
} Order;

/* F1 (Safe): Kiem tra input hop le */
Order* safe_open_session(int table_id) {
    if (table_id < MIN_TABLE_ID || table_id > MAX_TABLE_ID) {
        printf("    [GUARD AN TOAN] Tu choi mo ban: table_id = %d nam ngoai khoang [1, 50]!\n", table_id);
        return NULL;
    }
    Order* order = (Order*)malloc(sizeof(Order));
    if (!order) return NULL;
    
    order->table_id = table_id;
    order->item_count = 0;
    order->total_price = 0;
    order->is_paid = 0;
    return order;
}

/* F2 (Safe): Kiem tra gioi han mang va cat chuoi an toan */
int safe_add_item(Order* order, const char* name, int qty, int price) {
    if (!order) return -1;
    
    /* Guard 1: Kiem tra mảng đầy */
    if (order->item_count >= MAX_ITEMS) {
        printf("    [GUARD AN TOAN] Tu choi them mon: Mang da dat gioi han MAX_ITEMS = %d!\n", MAX_ITEMS);
        return -2;
    }
    /* Guard 2: Kiem tra so luong va gia hop le */
    if (qty < 1 || qty > 99 || price < 0 || !name) {
        return -3;
    }

    /* Guard 3: Cat chuoi an toan, khong gay Buffer Overflow */
    strncpy(order->items[order->item_count].name, name, MAX_NAME_LEN - 1);
    order->items[order->item_count].name[MAX_NAME_LEN - 1] = '\0';
    order->items[order->item_count].qty = qty;
    order->items[order->item_count].price = price;
    order->item_count++;
    return 0;
}

/* F3 (Safe): Kiem tra tran so truoc khi tinh tong */
int safe_calc_total(Order* order) {
    if (!order) return -1;
    long long total = 0;

    for (int i = 0; i < order->item_count; i++) {
        long long q = order->items[i].qty;
        long long p = order->items[i].price;
        
        /* Guard: Phat hien nguy co tran int32 truoc khi nhan */
        if (p > 0 && q > INT_MAX / p) {
            printf("    [GUARD AN TOAN] Phat hien tran so hoc: %lld * %lld > INT_MAX! Tu choi tinh.\n", q, p);
            return -1;
        }
        long long subtotal = q * p;
        if (total + subtotal > INT_MAX) {
            printf("    [GUARD AN TOAN] Tong don vuot qua INT_MAX!\n");
            return -1;
        }
        total += subtotal;
    }
    order->total_price = (int)total;
    return order->total_price;
}

/* F3 (Safe): Kiem tra chia cho 0 */
int safe_split_bill(int total, int n_guests) {
    if (n_guests <= 0) {
        printf("    [GUARD AN TOAN] n_guests = %d <= 0! Tu choi thuc hien de tranh Divide-by-zero!\n", n_guests);
        return -1;
    }
    return total / n_guests;
}

/* F6 (Safe): Giai phong bo nho tren ca nhanh thanh toan va nhanh huy */
void safe_close_order(Order** order_ptr, int is_paid) {
    if (!order_ptr || !*order_ptr) return;
    
    if (is_paid) {
        printf("    [GIAI PHONG] Don hang thanh toan thanh cong. Thu hoi bo nho heap %p.\n", (void*)*order_ptr);
    } else {
        printf("    [GIAI PHONG] Khach huy don hang. Thu hoi an toan bo nho heap %p (KHONG LEAK)!\n", (void*)*order_ptr);
    }
    free(*order_ptr);
    *order_ptr = NULL; /* Dat ve NULL de tranh Dangling Pointer */
}

int main() {
    printf("=================================================================\n");
    printf("DEMO BAN AN TOAN (SAFE VERSION) - HE THONG NHA HANG THONG MINH\n");
    printf("=================================================================\n");

    /* 1. Test F1: Mo ban voi table_id bat hop le */
    printf("\n[1] TEST F1 - Thu nhap table_id = 999:\n");
    Order* invalid_order = safe_open_session(999);
    if (!invalid_order) {
        printf("    --> Ket qua: He thong da chan thanh cong input khong hop le!\n");
    }

    /* Mo ban hop le */
    printf("\n[1b] Mo ban hop le table_id = 15:\n");
    Order* order = safe_open_session(15);
    printf("    --> Mo ban 15 thanh cong tai dia chi: %p\n", (void*)order);

    /* 2. Test F2: Them chuoi dai (cat an toan) */
    printf("\n[2] TEST F2 - Thu them mon ten dai 60 ky tu:\n");
    const char* long_name = "Mon_An_Co_Ten_Cuc_Ky_Dai_Vuot_Qua_32_Ky_Tu_Buffer_Overflow";
    safe_add_item(order, long_name, 2, 65000);
    printf("    --> Ten mon sau khi cat an toan: \"%s\" (Chieu dai = %zu byte, KHONG TRAN!)\n", 
           order->items[0].name, strlen(order->items[0].name));

    /* 3. Test F2: Thu them qua 20 mon */
    printf("\n[3] TEST F2 - Thu them tong cong 25 mon (vuot MAX_ITEMS = 20):\n");
    for (int i = 1; i < 25; i++) {
        safe_add_item(order, "Mon an kem", 1, 10000);
    }
    printf("    --> So mon thuc te duoc luu: %d mon (Dung bang MAX_ITEMS, khong vuot bien!)\n", order->item_count);

    /* 4. Test F3: Tinh tien voi gia tri gay tran so */
    printf("\n[4] TEST F3 - Thu tinh tong tien voi mat hang gia cuc lon (138 ty):\n");
    Order* overflow_order = safe_open_session(2);
    safe_add_item(overflow_order, "Yen Sao", 80, 1736074747);
    int total_err = safe_calc_total(overflow_order);
    if (total_err == -1) {
        printf("    --> Ket qua: He thong phat hien nguy co tran so va tu choi an toan!\n");
    }
    safe_close_order(&overflow_order, 0);

    /* 5. Test F3: Chia bill cho 0 nguoi */
    printf("\n[5] TEST F3 - Thu chia bill cho n_guests = 0:\n");
    int split_err = safe_split_bill(100000, 0);
    if (split_err == -1) {
        printf("    --> Ket qua: Chan chia cho 0 thanh cong, khong gay crash chuong trinh!\n");
    }

    /* 6. Test F6: Huy don va giai phong bo nho */
    printf("\n[6] TEST F6 - Huy don ban 15 va kiem tra giai phong bo nho:\n");
    safe_close_order(&order, 0);
    printf("    --> Con tro order sau khi giai phong: %p (Da set NULL an toan, khong UAF)!\n", (void*)order);

    printf("\n=================================================================\n");
    printf("KET LUAN BAN AN TOAN: Tat ca cac ca tan cong/loi deu da bi chan dung!\n");
    printf("=================================================================\n");
    return 0;
}
