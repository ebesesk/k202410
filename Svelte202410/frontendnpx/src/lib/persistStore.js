import { writable } from 'svelte/store';

export const persistStore = (key, initial) => {
    // 브라우저 환경인지 확인
    const isBrowser = typeof window !== 'undefined';
    
    // localStorage는 브라우저에서만 접근
    const stored = isBrowser ? localStorage.getItem(key) : null;
    const initial_value = stored ? JSON.parse(stored) : initial;
    
    const store = writable(initial_value);
    
    // 브라우저에서만 localStorage 저장
    if (isBrowser) {
        store.subscribe(value => {
            localStorage.setItem(key, JSON.stringify(value));
        });
    }
    
    return store;
}