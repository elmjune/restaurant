export interface Order {
    table: number
    food: string
}

export interface ReceivedOrders {
    [tableNumber: number]: Array<Order>
}
