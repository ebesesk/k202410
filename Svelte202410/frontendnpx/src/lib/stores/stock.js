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
export const trade_keyword = writable({})
export const trade_tag = writable({})
export const account_table_items = writable([])
export const dartData = writable({
    quarterBalance: {}
})
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
persistStore('trade_keyword', trade_keyword);
persistStore('trade_tag', trade_tag);
persistStore('account_table_items', account_table_items);
persistStore('dartData', dartData);
// 투자 일지 관련 스토어 생성
function createInvestmentStore() {
    const { subscribe, set, update } = writable({
        accounts: [],
        assets: [],
        transactions: [],
        selectedAccount: null,
        selectedAsset: null,
        pagination: {
            currentPage: 1,
            totalPages: 1,
            itemsPerPage: 10,
            totalItems: 0
        }
    });

    return {
        subscribe,
        setTransactions: (transactions) => {
            console.log('거래내역 업데이트:', transactions);
            update(state => ({ ...state, transactions }));
        },
        // setAssets 함수 추가
        setAssets: (assets) => {
            console.log('자산 목록 업데이트:', assets);
            update(state => ({ ...state, assets }));
        },
        // setAccounts 함수 추가
        setAccounts: (accounts) => {
            console.log('계정 목록 업데이트:', accounts);
            update(state => ({ ...state, accounts }));
        },
        setPage: (page) => {
            console.log('페이지 변경:', page);
            update(state => ({
                ...state,
                pagination: { ...state.pagination, currentPage: page }
            }));
        },
        setTotalItems: (total) => {
            console.log('전체 아이템 수 업데이트:', total);
            update(state => ({
                ...state,
                pagination: {
                    ...state.pagination,
                    totalItems: total,
                    totalPages: Math.ceil(total / state.pagination.itemsPerPage)
                }
            }));
        },
        resetPagination: () => {
            console.log('페이지네이션 초기화');
            update(state => ({
                ...state,
                pagination: {
                    currentPage: 1,
                    totalPages: 1,
                    itemsPerPage: 10,
                    totalItems: 0
                }
            }));
        }
    };
}

export const investmentStore = createInvestmentStore();