<script>
	import Table from '$lib/components/Table.svelte';
	import { foodHandler } from '$lib/food_handler';
	import { onDestroy } from 'svelte';

	const TABLE_COUNT = 4;

	onDestroy(async () => {
		await foodHandler.close();
	});
</script>

<h1>Restaurant Simulator</h1>
<div class="table-container">
	{#each { length: TABLE_COUNT }, tableNumber}
		<Table tableNumber={tableNumber + 1} />
	{/each}
</div>

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
