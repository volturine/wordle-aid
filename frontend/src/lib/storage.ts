type KeyValueStore = Pick<Storage, 'getItem' | 'setItem' | 'removeItem'>;

function browserStorage(): KeyValueStore | null {
	try {
		if (typeof localStorage === 'undefined') return null;
		return localStorage;
	} catch {
		return null;
	}
}

export function readStorage(key: string, store: KeyValueStore | null = browserStorage()): string | null {
	if (!store) return null;
	try {
		return store.getItem(key);
	} catch {
		return null;
	}
}

export function writeStorage(key: string, value: string, store: KeyValueStore | null = browserStorage()): void {
	if (!store) return;
	try {
		store.setItem(key, value);
	} catch {
		// Storage can be disabled or full. The board still works in memory.
	}
}

export function removeStorage(key: string, store: KeyValueStore | null = browserStorage()): void {
	if (!store) return;
	try {
		store.removeItem(key);
	} catch {
		// Ignore a storage backend that refuses the cleanup.
	}
}
