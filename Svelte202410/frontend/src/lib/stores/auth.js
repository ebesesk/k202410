import { writable } from 'svelte/store';

export const isAuthenticated = writable(false);
export const user = writable(null);

// src/lib/stores/manga.js
import { writable } from 'svelte/store';

export const mangas = writable([]);
export const currentPage = writable(1);
export const totalPages = writable(1);
export const loading = writable(false);
