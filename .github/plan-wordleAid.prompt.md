## Plan: Tidy SvelteKit structure and handlers

We’ll align the app with SvelteKit 2/Svelte 5 conventions and clean handler usage.

### Steps

1. Move `src/routes/__layout.svelte` → `src/routes/+layout.svelte` and update markup to use `{@render children()}` with `$app/state` for status handling.
2. In `src/routes/+page.svelte`, replace every `onclick=…` with `on:click=…` (and similar for other events if present), keeping existing logic.
3. Adjust `svelte.config.js` to a single intended `fallback` value (likely `404.html`) and remove the duplicate entry.
4. Ensure prerender is declared at the root (`src/routes/+layout.ts` or `+layout.js`), not just `+page.ts`; add `export const prerender = true` there and keep/remove from `+page.ts` accordingly.

### Further Considerations

1. Do you want a custom `+error.svelte` for nicer error/404 UX? Option A: add now; Option B: leave default.
