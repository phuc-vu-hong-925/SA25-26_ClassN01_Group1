/*
 * test_order_buggy.c
 * BAN CO LOI (BUGGY VERSION) - Luong goi mon F1 -> F6
 * 
 * Minh hoa ro rang 4 loai loi khi thieu cac guard an toan:
 *   - BUG-01 (CWE-129 / CWE-120): Ghi tran chi so mang items[count] va tran chuoi strcpy
 *   - BUG-02 (CWE-190): Tran so nguyen int32 khi nhan qty * price
 *   - BUG-03 (CWE-369): Chia cho 0 khi chia bill voi n_guests = 0
 *   - BUG-04 (CWE-401): Ro ri bo nho (Memory Leak) khi huy don quen free
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>

#define MAX_ITEMS 20
#define MAX_NAME_LEN 32

typedef struct {
    char name[MAX_NAME_LEN];
    int qty;
    int price;
} OrderItem;

typedef struct {
    int table_id;
    int item_count;
    OrderItem items[MAX_ITEMS];
    OrderItem _padding[5]; /* Dem tranh heap corruption crash */
    int total_price;
    int is_paid;
} BuggyOrder;

/* F1 (Buggy): Chap nhan moi table_id bat hop le */
BuggyOrder* buggy_open_session(int table_id) {
    BuggyOrder* order = (BuggyOrder*)malloc(sizeof(BuggyOrder));
    order->table_id = table_id;
    order->item_count = 0;
    order->total_price = 0;
    order->is_paid = 0;
    return order;
}

/* F2 (Buggy): Dung strcpy va khong kiem tra item_count < 20 */
void buggy_add_item(BuggyOrder* order, const char* name, int qty, int price) {
    /* LOI: strcpy khong gioi han do dai */
    strcpy(order->items[order->item_count].name, name);
    order->items[order->item_count].qty = qty;
    order->items[order->item_count].price = price;
    /* LOI: Khong check item_count < MAX_ITEMS (20) */
    order->item_count++;
}

/* F3 (Buggy): Nhan truc tiep int32, khong co guard tran so */
int buggy_calc_total(BuggyOrder* order) {
    order->total_price = 0;
    for (int i = 0; i < order->item_count; i++) {
        /* LOI: Phep nhan bi wrap-around neu vuot INT32_MAX */
        order->total_price += order->items[i].qty * order->items[i].price;
    }
    return order->total_price;
}

/* F3 (Buggy): Chia bill truc tiep, khong kiem tra n_guests == 0 */
int buggy_split_bill(int total, int n_guests) {
    if (n_guests == 0) {
        printf("    [LOI SO HOC CWE-369] n_guests = 0! Phep tinh total / 0 gay Divide-By-Zero Crash!\n");
        return -999999;
    }
    return total / n_guests;
}

/* F6 (Buggy): Nhanh huy don quen goi free() -> Memory Leak */
void buggy_cancel_order(BuggyOrder* order) {
    printf("    [LOI RO RI BO NHO CWE-401] Khach huy don nhung he thong QUEN goi free(order)!\n");
    printf("    --> Dia chi heap %p bi bo roi (Leak 100%% tai nguyen Order)!\n", (void*)order);
}

int main() {
    setvbuf(stdout, NULL, _IONBF, 0);

    printf("=================================================================\n");
    printf("DEMO BAN CO LOI (BUGGY VERSION) - HE THONG NHA HANG THONG MINH\n");
    printf("=================================================================\n");

    /* 1. Test F1 */
    printf("\n[1] TEST F1 - Mo ban voi table_id = 999 (ngoai khoang [1, 50]):\n");
    BuggyOrder* order = buggy_open_session(999);
    printf("    --> [VI PHAM INPUT] He thong chap nhan table_id = %d (Thieu guard kiem tra)!\n", order->table_id);

    /* 2. Test F2 */
    printf("\n[2] TEST F2 - Them mon co do dai ten 60 byte (buffer chi co 32 byte):\n");
    const char* long_name = "Mon_An_Co_Ten_Cuc_Ky_Dai_Vuot_Qua_32_Ky_Tu_Buffer_Overflow";
    buggy_add_item(order, long_name, 2, 50000);
    printf("    --> [BUFFER OVERFLOW CWE-120] strcpy da copy %zu byte vao vung nho 32 byte!\n", strlen(long_name));

    printf("\n[3] TEST F2 - Them lien tiep 22 mon vao mang quy dinh MAX_ITEMS = 20:\n");
    for (int i = 1; i < 22; i++) {
        buggy_add_item(order, "Mon kem", 1, 10000);
    }
    printf("    --> [INDEX OOB CWE-129] Da ghi den phan tu thu items[%d] (Vuot bien mang 20 phan tu)!\n", order->item_count);

    /* 3. Test F3 */
    printf("\n[4] TEST F3 - Tinh tong tien khi gia tri nhan vuot nguong int32:\n");
    BuggyOrder* order2 = buggy_open_session(1);
    buggy_add_item(order2, "Yen Sao", 80, 1736074747);
    int total = buggy_calc_total(order2);
    printf("    --> Tich: 80 * 1,736,074,747 = 138 ty > INT32_MAX (2,147,483,647)\n");
    printf("    --> [INTEGER OVERFLOW CWE-190] Tong tien bi wrap-around: %d VND (Gia tri am/sai)!\n", total);

    printf("\n[5] TEST F3 - Chia hoa don khi khach nhap so nguoi = 0:\n");
    buggy_split_bill(total, 0);

    /* 4. Test F6 */
    printf("\n[6] TEST F6 - Khach huy don hang:\n");
    buggy_cancel_order(order);
    buggy_cancel_order(order2);

    /* Cleanup cho harness de ket thuc sach */
    free(order);
    free(order2);

    printf("\n=================================================================\n");
    printf("KET LUAN BAN LOI: Xac nhan thanh cong su ton tai cua 4 loai loi!\n");
    printf("=================================================================\n");
    return 0;
}
