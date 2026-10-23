/*
 * restaurant_order.h
 * Khai bao cau truc du lieu va 6 ham F1 -> F6
 * Luong goi mon He thong Nha hang thong minh
 */
#ifndef RESTAURANT_ORDER_H
#define RESTAURANT_ORDER_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>

#define MAX_ITEMS 20
#define MAX_NAME_LEN 32
#define MIN_TABLE_ID 1
#define MAX_TABLE_ID 50
#define MIN_QTY 1
#define MAX_QTY 99
#define MAX_QUEUE 50

typedef enum {
    STATUS_IDLE,
    STATUS_BROWSING,
    STATUS_ORDERING,
    STATUS_SUBMITTED,
    STATUS_COOKING,
    STATUS_SERVED,
    STATUS_PAID,
    STATUS_CANCELLED
} OrderStatus;

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
    OrderStatus status;
} Order;

typedef struct {
    Order* orders[MAX_QUEUE];
    int head;
    int tail;
    int count;
} KitchenQueue;

/* Prototype 6 ham F1 -> F6 */
Order* open_session(int table_id);
int add_item(Order* order, const char* name, int qty, int price);
int calc_total(Order* order);
int split_bill(int total, int n_guests);
int submit_order(KitchenQueue* kq, Order* order);
Order* kitchen_process(KitchenQueue* kq);
void pay_or_cancel(Order** order_ptr, int is_paid);

#endif /* RESTAURANT_ORDER_H */
