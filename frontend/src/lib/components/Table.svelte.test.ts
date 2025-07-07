import { page } from '@vitest/browser/context';
import { describe, expect, it } from 'vitest';
import { render } from 'vitest-browser-svelte';
import Table from './Table.svelte';


describe('/+page.svelte', () => {
    it('should have the correct table heading', async () => {
        render(Table, { tableNumber: 1 });
        const heading = page.getByRole('heading');
        await expect.element(heading).toHaveTextContent("Table 1");
    });
});
