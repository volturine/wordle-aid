import { writable } from 'svelte/store';
import { browser } from '$app/environment';

type Theme = 'light' | 'dark';

const defaultValue: Theme = 'light';
const initialValue = browser ? (window.localStorage.getItem('theme') as Theme) ?? defaultValue : defaultValue;

const theme = writable<Theme>(initialValue);

theme.subscribe((value) => {
    if (browser) {
        window.localStorage.setItem('theme', value);
        document.documentElement.classList.toggle('dark', value === 'dark');
    }
});

export default theme;
