import { type Order } from "./types";

export const TABLE_COUNT = 4

export const receivedOrders: { [tableNumber: number]: Array<Order> } = $state({})
