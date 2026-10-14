import { writable } from 'svelte/store';
import { browser } from '$app/env';
import { readStorage, writeStorage } from '#lib/storage.js';

type Theme = 'light' | 'dark';

const defaultValue: Theme = 'light';
const storedTheme = browser ? readStorage('theme') : null;
const initialValue: Theme = storedTheme === 'dark' || storedTheme === 'light' ? storedTheme : defaultValue;

const theme = writable<Theme>(initialValue);

theme.subscribe((value) => {
    if (browser) {
        writeStorage('theme', value);
        document.documentElement.classList.toggle('dark', value === 'dark');
    }
});

export default theme;
