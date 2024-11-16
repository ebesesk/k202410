export function persistStore(key, store) {
    if (typeof window === 'undefined') return;

    // 초기값 설정
    const storedValue = localStorage.getItem(key);
    if (storedValue) {
        try {
            const parsedValue = JSON.parse(storedValue);
            if (parsedValue !== null && parsedValue !== undefined) {
                store.set(parsedValue);
            }
        } catch (e) {
            console.warn(`Failed to parse stored value for ${key}:`, e);
        }
    }

    // 구독 설정
    return store.subscribe(value => {
        if (value === undefined) return;
        try {
            if (value === null || value === '') {
                localStorage.removeItem(key);
            } else {
                localStorage.setItem(key, JSON.stringify(value));
            }
            // console.log(`Persisted ${key}:`, value); // 디버깅용
        } catch (e) {
            console.warn(`Failed to store value for ${key}:`, e);
        }
    });
}