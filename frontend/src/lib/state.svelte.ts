import { getContext, setContext } from "svelte";
import { FoodHandler } from "./food_handler";
import { type ReceivedOrders } from "./types";

export const TABLE_COUNT = 4

export const receivedOrders: ReceivedOrders = $state({})

type FoodHandlerFunction = () => FoodHandler | undefined

export function setFoodHandlerContext(handler: FoodHandlerFunction) {
    setContext('food-handler', handler)
}

export function getFoodHandlerContext(): FoodHandlerFunction {
    return getContext('food-handler')
}

