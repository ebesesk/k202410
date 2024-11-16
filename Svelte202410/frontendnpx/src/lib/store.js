import { writable } from 'svelte/store'
import { browser } from '$app/environment'
import { persistStore } from '$lib/persistStore';

export const access_token = writable('')
export const username = writable('')
export const is_login = writable(false)
export const userpoints = writable(0)  // 초기값을 0으로 설정

// 브라우저 환경에서만 persistStore 초기화
if (browser) {
    persistStore('access_token', access_token);
    persistStore('username', username);
    persistStore('is_login', is_login);
    persistStore('userpoints', userpoints);
}