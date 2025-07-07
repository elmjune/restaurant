import { type Order } from "./types";

export const receivedOrders: { [tableNumber: number]: Array<Order> } = $state({})
