import { writable } from 'svelte/store';

export const persistStore = (key, initial) => {
    // 브라우저 환경인지 확인
    const isBrowser = typeof window !== 'undefined';

    // 저장된 값 가져오기
    const storedValue = isBrowser ? localStorage.getItem(key) : null;

    // 초기값 설정
    let value = initial;

    try {
        // 저장된 값이 있으면 파싱 시도
        if (storedValue !== null) {
            value = storedValue;
            // JSON 형식인 경우에만 파싱
            if (storedValue.startsWith('{') || storedValue.startsWith('[')) {
                value = JSON.parse(storedValue);
            }
        }
    } catch (e) {
        console.warn(`Failed to parse stored value for ${key}:`, e);
    }

    // store 생성
    const store = writable(value);

    // 브라우저 환경에서만 localStorage 사용
    if (isBrowser) {
        store.subscribe(value => {
            try {
                // 객체나 배열인 경우 JSON으로 직렬화
                const saveValue = typeof value === 'object' 
                    ? JSON.stringify(value)
                    : value;
                localStorage.setItem(key, saveValue);
            } catch (e) {
                console.warn(`Failed to store value for ${key}:`, e);
            }
        });
    }

    return store;
};