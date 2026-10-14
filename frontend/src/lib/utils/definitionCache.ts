import type { DictionaryResponse } from '#lib/types.js';

const CACHE_KEY = 'word_definitions_cache';
const CACHE_DURATION = 7 * 24 * 60 * 60 * 1000; // 7 days
const MAX_CACHE_ENTRIES = 200;

interface CacheEntry {
    data: DictionaryResponse;
    timestamp: number;
}

interface Cache {
    [word: string]: CacheEntry;
}

export function pruneDefinitionCache(cache: Cache, now = Date.now()): Cache {
    for (const word of Object.keys(cache)) {
        if (now - cache[word].timestamp >= CACHE_DURATION) delete cache[word];
    }
    const oldest = Object.entries(cache).sort((left, right) => left[1].timestamp - right[1].timestamp);
    while (oldest.length > MAX_CACHE_ENTRIES) {
        const [word] = oldest.shift()!;
        delete cache[word];
    }
    return cache;
}

/**
 * Retrieves a cached word definition from localStorage
 * @param word - The word to look up
 * @returns The cached definition or null if not found or expired
 */
export function getCachedDefinition(word: string): DictionaryResponse | null {
    try {
        const cache = pruneDefinitionCache(JSON.parse(localStorage.getItem(CACHE_KEY) || '{}'));
        try {
            localStorage.setItem(CACHE_KEY, JSON.stringify(cache));
        } catch (error) {
            console.warn('Cache write error:', error);
        }
        const cached = cache[word.toLowerCase()];
        return cached ? cached.data : null;
    } catch (e) {
        console.warn('Cache read error:', e);
    }
    return null;
}

/**
 * Stores a word definition in localStorage cache
 * @param word - The word to cache
 * @param data - The definition data to cache
 */
export function setCachedDefinition(word: string, data: DictionaryResponse): void {
    try {
        const cache = pruneDefinitionCache(JSON.parse(localStorage.getItem(CACHE_KEY) || '{}'));
        cache[word.toLowerCase()] = {
            data,
            timestamp: Date.now()
        };
        pruneDefinitionCache(cache);
        localStorage.setItem(CACHE_KEY, JSON.stringify(cache));
    } catch (e) {
        console.warn('Cache write error:', e);
    }
}

/**
 * Clears all cached definitions
 */
export function clearDefinitionCache(): void {
    try {
        localStorage.removeItem(CACHE_KEY);
    } catch (e) {
        console.warn('Cache clear error:', e);
    }
}

/**
 * Gets the size of the cache (number of entries)
 */
export function getCacheSize(): number {
    try {
        const cache: Cache = JSON.parse(localStorage.getItem(CACHE_KEY) || '{}');
        return Object.keys(cache).length;
    } catch (e) {
        console.warn('Cache size error:', e);
        return 0;
    }
}
