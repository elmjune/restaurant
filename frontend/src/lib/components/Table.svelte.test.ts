import { page } from '@vitest/browser/context';
import { describe, expect, it } from 'vitest';
import { render } from 'vitest-browser-svelte';
import Table from './Table.svelte';
import { TABLE_COUNT } from '$lib/state.svelte';

import Aedes from 'aedes'
import { createServer } from 'net'

describe('/+page.svelte', () => {
    it('should have a heading', async () => {
        render(Table);
        const heading = page.getByRole('heading');
        await expect.element(heading).toBeInTheDocument();
    });

    it('should render all the tables', async () => {
        const port = 1883

        const aedes = new Aedes()
        const server = createServer(aedes.handle)

        server.listen(port, function () {
            console.log('server started and listening on port ', port)
        })

        render(Table);
        const tables = page.getByTestId('table-component').element()
        expect(tables).toHaveLength(TABLE_COUNT)
    });
});
