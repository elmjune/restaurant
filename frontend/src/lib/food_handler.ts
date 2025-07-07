import mqtt from "mqtt"
import { receivedOrders } from "./state.svelte"
import { PUBLIC_MQTT_BROKER_URL } from "$env/static/public"
import type { Order, ReceivedOrders } from "./types"

/**
 * A class for publishing food orders and handling their deliveries.
 */
export class FoodHandler {
    client: mqtt.MqttClient;
    received: ReceivedOrders;

    /**
     * Create a new `FoodHandler` instance.
     * @param client the MQTT.js client to use for broker communications.
     * @param the `ReceivedOrders` object in which all received orders will be put
     */
    constructor(client: mqtt.MqttClient, received: ReceivedOrders = {}) {
        this.client = client
        this.onMessageReceive = this.onMessageReceive.bind(this)
        this.client.on('message', this.onMessageReceive);
        this.received = received
    }

    /**
     * Subscribe to all appropriate topics. This should be done before any other functions are called.
     */
    async subscribe() {
        await this.client.subscribeAsync({ "restaurant/deliver": { qos: 2 } });
    }

    /**
     * Send a new food order.
     * @param order the new food order to send.
     */
    async sendOrder(order: Order) {
        const msg = JSON.stringify(order);
        await this.client.publishAsync("restaurant/order", msg, { qos: 2 });
    }

    /**
     * Close this client's connection with the broker.
     * This `FoodHandler` will no longer be usable.
     */
    public async close() {
        await this.client.endAsync()
    }

    /**
     * Handle an incoming restaurant delivery PUBLISH message
     * @param _topic topic name
     * @param message order JSON
     */
    onMessageReceive(_topic: string, message: Buffer) {
        let order: Order;
        try {
            order = JSON.parse(message.toString("utf-8"));
        } catch (e) {
            console.error("Failed to parse order: ", e);
            return;
        }
        if (order.table in this.received) {
            this.received[order.table].push(order);
        } else {
            this.received[order.table] = [order];
        }
    }
}

/**
 * Create a new `FoodHandler` with a new MQTT client.
 */
async function createFoodHandler(): Promise<FoodHandler> {
    const client = await mqtt.connectAsync(PUBLIC_MQTT_BROKER_URL);
    return new FoodHandler(client, receivedOrders)
}

export let foodHandler: FoodHandler;
try {
    foodHandler = await createFoodHandler()
    await foodHandler.subscribe()
} catch (e) {
    console.error("Failed to initialize MQTT food handler: ", e);
}
