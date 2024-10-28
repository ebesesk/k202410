import { writable } from 'svelte/store';

export const mangas = writable([]);
export const currentPage = writable(1);
export const totalPages = writable(1);
export const loading = writable(false);