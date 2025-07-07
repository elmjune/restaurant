<!-- 
@component
A component representing a single table at the restaurant.
-->

<script lang="ts">
	import { foodHandler } from '$lib/food_handler';
	import { receivedOrders } from '$lib/state.svelte';
	import Dialog from './Dialog.svelte';

	/** The unique number for this table */
	let { tableNumber }: { tableNumber: number } = $props();

	/** The number of orders sent so far*/
	let sentOrders = $state(0);
	let showConfirmationMessage = $state(false);

	let dialog: Dialog;

	const foods = $derived.by(() => {
		const orders = receivedOrders[tableNumber] ?? [];
		return orders.map((o) => o.food);
	});

	/**
	 * Create a new `Order` and request it be delivered.
	 * @param foodName the name of the new order's food
	 */
	async function orderFood(tableNum: number, foodName: string) {
		const order = { table: tableNum, food: foodName };
		await foodHandler.sendOrder(order);
		sentOrders += 1;
	}

	/**
	 * Show a modal dialog for retrieving information about a new order.
	 */
	function showDialog() {
		dialog.show();
	}

	$effect(() => {
		if (sentOrders > 0) {
			showConfirmationMessage = true;
			setTimeout(() => {
				showConfirmationMessage = false;
			}, 1500);
		}
	});
</script>

<div id="table-container" data-testid="table-component">
	<div class="table-header">
		<h2>Table {tableNumber}</h2>
		<button id="order-button" onclick={showDialog}> Order </button>
	</div>
	<div id="food-list">
		{#if foods.length == 0}
			<p>Nothing ordered so far!</p>
		{/if}
		{#each foods as food, index}
			<p class="food-list-item" style:background-color={index % 2 == 0 ? '#eee' : 'white'}>
				{food}
			</p>
		{/each}
	</div>

	{#if showConfirmationMessage}
		<p class="confirmation-message">Order sent</p>
	{:else}
		<p class="confirmation-message"></p>
	{/if}

	<Dialog bind:this={dialog} onSubmit={(food) => orderFood(tableNumber, food)} />
</div>

<style>
	#table-container {
		padding: 1em;
		margin: 0.5em;
		border: 2px solid black;
		border-radius: 4px;
		width: 20em;
	}

	#food-list {
		height: 10em;
		width: 100%;
		overflow-wrap: break-word;
		overflow-y: auto;
		border: 1px solid black;
		border-radius: 4px;
	}

	#food-list p {
		margin: 0;
		padding: 1rem;
		border-bottom: 1px solid black;
	}

	#order-button {
		padding: 0.5rem;
	}

	.table-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.confirmation-message {
		color: green;
		font-weight: bold;
		height: 0.1em;
	}
</style>
