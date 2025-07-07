<script lang="ts">
	import Table from '$lib/components/Table.svelte';
	import { FoodHandler, createFoodHandler } from '$lib/food_handler';
	import { setFoodHandlerContext, TABLE_COUNT } from '$lib/state.svelte';
	import { onDestroy, onMount } from 'svelte';

	let foodHandler: FoodHandler | undefined;

	setFoodHandlerContext(() => foodHandler);

	onMount(async () => {
		foodHandler = await createFoodHandler();
	});

	onDestroy(async () => {
		foodHandler?.close();
	});
</script>

<h1>Restaurant Simulator</h1>
<div class="table-container">
	{#each { length: TABLE_COUNT }, tableNumber}
		<Table tableNumber={tableNumber + 1} />
	{/each}
</div>
<p style="margin-left: 1em;">Waiting time: 3 to 9 seconds</p>

<style>
	:global(body) {
		font-family: sans-serif;
	}

	.table-container {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
	}

	h1 {
		margin: 1rem;
	}
</style>
