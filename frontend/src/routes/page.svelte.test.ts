import { page } from '@vitest/browser/context';
import { describe, expect, it } from 'vitest';
import { render } from 'vitest-browser-svelte';
import Page from './+page.svelte';
import { TABLE_COUNT } from '$lib/state.svelte';

describe('/+page.svelte', () => {
	it('should have a heading', async () => {
		render(Page);
		const heading = page.getByRole('heading', { level: 1 });
		await expect.element(heading).toBeInTheDocument();
	});
	it('should render all the tables', async () => {
		render(Page);
		const tables = page.getByTestId('table-component').all()
		expect(tables).toHaveLength(TABLE_COUNT)
	});
});

