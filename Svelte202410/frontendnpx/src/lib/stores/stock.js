import { writable } from 'svelte/store';
import { persistStore } from '$lib/persistStore';
import { browser } from '$app/environment';
// localStorage에서 key 값 가져오기
const storedKey = browser ? localStorage.getItem('stock_key') : null;

// store 생성
export const accno_list = writable([]);
export const accno_codes = writable([]);
export const key = writable(storedKey || '');
export const selectedStocks = writable({})
export const investInfoMap = writable({})
export const interestStocks = writable({})
export const accnoStocks = writable({})
export const candleStore = writable({}) // 종목 옆 캔들 데이터
export const chartDataStore = writable({})
export const sortedCodes = writable([])

// key 값이 변경될 때마다 localStorage에 저장
if (browser) {
    key.subscribe(value => {
        if (value) {
            localStorage.setItem('stock_key', value);
        } else {
            localStorage.removeItem('stock_key');
        }
    });
}

persistStore('accno_list', accno_list);
persistStore('accno_codes', accno_codes);
persistStore('selectedStocks', selectedStocks);
persistStore('investInfoMap', investInfoMap);
persistStore('interestStocks', interestStocks);
persistStore('accnoStocks', accnoStocks);
persistStore('candleStore', candleStore);
persistStore('chartDataStore', chartDataStore);
persistStore('sortedCodes', sortedCodes);