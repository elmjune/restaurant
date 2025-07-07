import { describe, it, expect, beforeEach, afterEach } from 'vitest';

import Aedes, { type Subscription } from 'aedes'
import { createServer, Server } from 'net'
import mqtt, { MqttClient } from 'mqtt';
import { FoodHandler } from './food_handler';
import type { Order, ReceivedOrders } from './types';

describe('Food handler', () => {
    let client: MqttClient;
    let server: Server
    let aedes: Aedes

    beforeEach(async () => {
        const port = 1883
        aedes = new Aedes()
        server = createServer(aedes.handle)
        server.listen(port)
        client = await mqtt.connectAsync("mqtt://localhost:1883")
    })

    afterEach(async () => {
        await client.endAsync()
        server.close()
    })

    it('subscribes to all appropriate topics', async () => {
        const foodHandler = new FoodHandler(client)

        let subscriptions: Subscription[] = []
        aedes.on('subscribe', (subs, _) => {
            subscriptions = subs
        })

        await foodHandler.subscribe()

        expect(subscriptions).toHaveLength(1)
        expect(subscriptions[0].topic).toBe("restaurant/deliver")
    });

    it('sends an order with a published topic', async () => {
        const foodHandler = new FoodHandler(client)
        const order: Order = { table: 1, food: "pizza" }

        let published: any[][] = []
        aedes.on('publish', (packet, _) => {
            published.push([packet.topic, packet.payload])
        })

        await foodHandler.sendOrder(order)

        expect(published).toHaveLength(1)
        expect(published[0][0]).toBe("restaurant/order")

        const jsonPayload = JSON.parse(published[0][1])
        expect(jsonPayload).toStrictEqual(order)
    })

    it('receives a single delivery', async () => {
        const order: Order = { table: 1, food: "pizza" }

        const received: ReceivedOrders = {}
        const foodHandler = new FoodHandler(client, received)
        await foodHandler.subscribe();

        const secondClient = await mqtt.connectAsync("mqtt://localhost:1883")
        await secondClient.publishAsync('restaurant/deliver', JSON.stringify(order), { qos: 2, retain: true })

        // we have to wait a small amount of time for the message handler to finish
        await new Promise(resolve => setTimeout(resolve, 1000));

        expect(Object.entries(received)).toHaveLength(1)
        expect(received[1]).toHaveLength(1)
        expect(received[1][0]).toStrictEqual(order)
    })

    it('receives multiple deliveries', async () => {
        const NUM_ORDERS = 5

        let orders = []
        for (let i = 0; i < NUM_ORDERS; i++) {
            const order: Order = { table: i, food: "pizza" }
            orders.push(order)
        }

        const received: ReceivedOrders = {}
        const foodHandler = new FoodHandler(client, received)
        await foodHandler.subscribe();

        const secondClient = await mqtt.connectAsync("mqtt://localhost:1883")

        for (const order of orders) {
            await secondClient.publishAsync('restaurant/deliver', JSON.stringify(order), { qos: 2 })
        }

        // we have to wait a small amount of time for the message handler to finish
        await new Promise(resolve => setTimeout(resolve, 1000));

        expect(Object.entries(received)).toHaveLength(NUM_ORDERS)

        for (let i = 0; i < NUM_ORDERS; i++) {
            expect(received[i]).toHaveLength(1)
            expect(received[i][0]).toStrictEqual(orders[i])
        }
    })

    it('closes the MQTT client', async () => {
        const foodHandler = new FoodHandler(client)
        await foodHandler.close()
        expect(client.disconnected).toBeTruthy()
    });
});