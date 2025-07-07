<!-- 
@component
Component for showing a modal dialog that takes in user input.
Use the `onSubmit` prop to get the value back if the user submits the form.
-->
<script lang="ts">
	let { onSubmit }: { onSubmit: (text: string) => Promise<void> } = $props();

	let value = $state('');
	let dialog: HTMLDialogElement | undefined;

	/**
	 * Show the modal dialog.
	 */
	export function show() {
		dialog?.showModal();
	}

	/**
	 * Reset the form.
	 */
	function reset() {
		value = '';
	}

	/**
	 * Submit the form. Closes the dialog and call the `onSubmit` callback.
	 */
	async function submit() {
		const val = $state.snapshot(value);
		dialog?.close();
		await onSubmit(val);
	}
</script>

<dialog bind:this={dialog} onclose={reset}>
	<div class="dialog-form">
		<h2>Order food</h2>
		<p>Enter the name of the food you would like:</p>
		<input id="food-input" type="text" bind:value />
		<div class="form-buttons">
			<button onclick={submit}>Order</button>
			<button onclick={() => dialog?.close()}>Cancel</button>
		</div>
	</div>
</dialog>

<style>
	.form-buttons {
		display: flex;
		margin-top: 1em;
		gap: 0.5rem;
	}

	#food-input {
		width: 100%;
	}
</style>
