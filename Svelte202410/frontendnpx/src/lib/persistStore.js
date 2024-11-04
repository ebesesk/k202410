export function persistStore(key, store) {
    // 브라우저 환경인지 확인
    if (typeof window === 'undefined') return;

    // 로컬 스토리지에서 데이터 가져오기
    const storedValue = localStorage.getItem(key);
    
    if (storedValue) {
        try {
            store.set(JSON.parse(storedValue));
        } catch (e) {
            console.warn(`Failed to parse stored value for ${key}:`, e);
            store.set(null);
        }
    }

    // 스토어 값이 변경될 때마다 로컬 스토리지에 저장
    store.subscribe(value => {
        if (value === undefined) return;
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            console.warn(`Failed to store value for ${key}:`, e);
        }
    });
}