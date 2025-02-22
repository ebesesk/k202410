import { writable } from 'svelte/store'
import { browser } from '$app/environment'
import { persistStore } from '$lib/persistStore';

export const access_token = persistStore('access_token', '')
export const username = persistStore('username', '')
export const is_login = persistStore('is_login', false)
export const userpoints = persistStore('userpoints', 0)  // 초기값을 0으로 설정
// 객체를 저장할 때는 JSON으로 직렬화
export const user = persistStore('user', JSON.stringify(null));

