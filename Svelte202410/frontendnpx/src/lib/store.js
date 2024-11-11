import { writable } from 'svelte/store'
import { browser } from '$app/environment'

export const access_token = writable('')
export const username = writable('')
export const is_login = writable(false)

// 브라우저에서만 localStorage 초기화 실행
if (browser) {
    access_token.set(localStorage.getItem('access_token') || '')
    username.set(localStorage.getItem('username') || '')
    is_login.set(localStorage.getItem('access_token') ? true : false)
}