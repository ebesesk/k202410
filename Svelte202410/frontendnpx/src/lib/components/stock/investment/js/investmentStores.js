import { writable } from 'svelte/store';
import fastapi from '$lib/api';
import { get } from 'svelte/store';
import { key } from "$lib/stores/stock";

const API_BASE_URL = import.meta.env.VITE_API_URL?.replace('http://', 'https://') || 'https://api2410.ebesesk.synology.me';
function createInvestmentStore() {
    const defaultState = {
        quarterBalanceSheet: {},
        periodicReturns: {
            balance: {},
            income_statement: {}
        },
        exchangeRate: {},
        transactions: [],
        assets: [],
        accounts: [],
        toggles: [],
        positions: [],
        pagination: {
            transactions: {
                currentPage: 1,
                totalItems: 0,
                itemsPerPage: 20,
                totalPages: 0
            },
            assets: {
                currentPage: 1,
                totalItems: 0,
                itemsPerPage: 10,
                totalPages: 0
            },
            accounts: {
                currentPage: 1,
                totalItems: 0,
                itemsPerPage: 10,
                totalPages: 0
            },
            positions: {
                currentPage: 1,
                totalItems: 0,
                itemsPerPage: 10,
                totalPages: 0
            }
        }
    };

    const { subscribe, set, update } = writable(defaultState);

    return {
        subscribe,
        setPeriodicReturns: (periodicReturns) => update(state => ({
            ...state,
            periodicReturns: {
                balance: periodicReturns.balance,
                income_statement: periodicReturns.income_statement
            }
        })),
        // 재무제표 관련
        setQuarterBalanceSheet: (data) => update(state => ({
            ...state,
            quarterBalanceSheet: data
        })),
        
        // 환율 관련
        setExchangeRate: (exchangeRate) => update(state => ({
            ...state,
            exchangeRate
        })),
        addExchangeRate: (exchangeRate) => update(state => ({
            ...state,
            exchangeRate: [...state.exchangeRate, exchangeRate]
        })),
        resetExchangeRate: () => update(state => ({
            ...state,
            exchangeRate: {}
        })),
        
        // 거래 관련
        setTransactions: (transactions) => update(state => ({
            ...state,
            transactions
        })),
        

        // 자산 관련
        setAssets: (assets) => {
            // console.log('setAssets:', assets);  // 디버깅용 로그
            update(state => ({
                ...state,
                assets
            }));
        },
        addAsset: (asset) => update(state => ({
            ...state,
            assets: [...state.assets, asset]
        })),
        updateAsset: (updatedAsset) => update(state => ({
            ...state,
            assets: state.assets.map(asset => 
                asset.id === updatedAsset.id ? updatedAsset : asset
            )
        })),

        // 자산 선택
        setPositions: (positions) => update(state => ({
            ...state,
            positions
        })),

        // 계정 관련
        setAccounts: (accounts) => update(state => ({
            ...state,
            accounts
        })),
        addAccount: (account) => update(state => ({
            ...state,
            accounts: [...state.accounts, account]
        })),
        updateAccount: (updatedAccount) => update(state => ({
            ...state,
            accounts: state.accounts.map(account => 
                account.id === updatedAccount.id ? updatedAccount : account
            )
        })),

        // 페이지네이션 관련    
        resetAllPagination: () => update(state => ({     // 모든 페이지네이션 초기화
            ...state,
            pagination: defaultState.pagination
        })),
        resetPagination: (type) => update(state => ({   // 페이지네이션 초기화 함수 추가
            ...state,
            pagination: {
                ...state.pagination,
                [type]: {
                    currentPage: 1,
                    totalItems: 0,
                    itemsPerPage: 10,
                    totalPages: 0
                }
            }
        })),
        setPage: (type, page) => update(state => ({
            ...state,
            pagination: {
                ...state.pagination,
                [type]: {
                    ...state.pagination[type],
                    currentPage: page
                }
            }
        })),
        setTotalItems: (type, total) => update(state => ({
            ...state,
            pagination: {
                ...state.pagination,
                [type]: {
                    ...state.pagination[type],
                    totalItems: total,
                    totalPages: Math.ceil(total / state.pagination[type].itemsPerPage)
                }
            } 
        })),
        setItemsPerPage: (type,itemsPerPage) => update(state => ({
            ...state,
            pagination: {
                ...state.pagination,
                itemsPerPage,
                totalPages: Math.ceil(state.pagination[type].totalItems / itemsPerPage)
            }
        })),

        // 토글 관련
        setToggles: (type) => update(state => {
            const currentToggles = Array.isArray(state.toggles) ? state.toggles : [];
            
            // type이 이미 있으면 제거, 없으면 추가
            if (currentToggles.includes(type)) {
                return {
                    ...state,
                    toggles: currentToggles.filter(t => t !== type)
                };
            } else {
                return {
                    ...state,
                    toggles: [...currentToggles, type]
                };
            }
        }),
        addToggle: (type) => update(state => ({
            ...state,
            toggles: [...state.toggles, type]
        })),
        
        removeToggle: (type) => update(state => ({
            ...state,
            toggles: state.toggles.filter(t => t !== type)
        })),

        // 스토어 초기화
        reset: () => set(defaultState)
    };
}

export const investmentStore = createInvestmentStore();
export { loadAssets, loadAccounts, loadTransactions, loadPositions, loadExchangeRate, loadPeriodicReturns };


async function loadPeriodicReturns() {
    const url = '/stock/investments/v2/transactions/get-periodic-returns-v2';
    fastapi('get', url, {}, 
        (json) => {
            investmentStore.setPeriodicReturns(json);
            // console.log('investmentStore.periodicReturns:', investmentStore);
        },
        (error) => {
            console.error('Error loading periodic returns:', error);
        });
}

async function loadTransactions(page = 1, date = new Date().getFullYear(), keyword = null) {
        // store의 현재 상태 가져오기
        let currentState;
        investmentStore.subscribe(state => {
            currentState = state;
        })();

        const url = '/stock/investments/v2/transactions/get-transactions-all';
        const params = {
            key: get(key),
            keyword: keyword,
            date: date.toString(), // 문자열로 변환
            skip: (page - 1) * currentState.pagination.transactions.itemsPerPage,
            limit: currentState.pagination.transactions.itemsPerPage
        }
        fastapi('get', url, params, (json) => {
            try {
                console.log('loadTransactions store json:', json);
                investmentStore.setTransactions(json.items);
                investmentStore.setTotalItems('transactions', json.pagination.total_items);
                investmentStore.setPage('transactions', json.pagination.current_page);
            } catch (error) {
                console.error('Error loading transactions:', error);
            }
            
        });
}

// 환율 읽어오기
async function loadExchangeRate() {
    const url = '/stock/investments/v2/exchange/latest';
    fastapi('get', url, {}, 
        (json) => {
            console.log('loadExchangeRate store json:', json);
            
            // 데이터 구조 변환
            // const formattedData = {};
            
            // latest_rates 객체 처리
            // if (json) {
            //     Object.entries(json).forEach(([fromCurrency, rateInfo]) => {
            //         if (!formattedData[fromCurrency]) {
            //             formattedData[fromCurrency] = {};
            //         }
            //         console.log('fromCurrency:', fromCurrency);
            //         console.log('rateInfo:', rateInfo);
            //         formattedData[fromCurrency] = {

            //             'to_currency': rateInfo.to_currency,
            //             'rate': rateInfo.rate,
            //             'date': rateInfo.date
            //         };
            //     });
            // }

            // console.log('변환된 환율 데이터:', formattedData);
            investmentStore.setExchangeRate(json);
            
            // store 업데이트 확인
            investmentStore.subscribe(state => {
                console.log('업데이트된 store 상태:', state.exchangeRate);
            })();
        },
        (error) => {
            console.error('Error loading exchange rate:', error);
        });
}
// 자산 관련
async function loadAssets() {
  
    const url = '/stock/investments/assets';
    fastapi('get', url, {}, 
        (json) => {
            // console.log('investmentStore.setAssets store json:', json);
            investmentStore.setAssets(json.items);
            investmentStore.setTotalItems('assets', json.pagination.total_count);
            investmentStore.setPage('assets', json.pagination.current_page);
            console.log('investmentStore.assets:', investmentStore.assets);
            },
        (error) => {
            console.error('Error loading assets:', error);
        });

}

// 계정 관련
async function loadAccounts() {
    const url = '/stock/investments/accounts';
    fastapi('get', url, {}, 
        (json) => {
            console.log('loadAccounts store json:', json);
            investmentStore.setAccounts(json.items);
            investmentStore.setTotalItems('accounts', json.pagination.total_count);
            investmentStore.setPage('accounts', json.pagination.current_page);
            console.log('investmentStore.accounts:', investmentStore.accounts);
        },
        (error) => {
            console.error('Error loading accounts:', error);
        });
}

// 자산 선택
async function loadPositions(page = 1, limit = 10) {
    const url = '/stock/investments/v2/positions';
    const params = {
        page: page,
        limit: limit
        }
    fastapi('get', url, params, 
        (json) => {
            console.log('loadPositions store json:', json);
            investmentStore.setPositions(json.items);
            investmentStore.setTotalItems('positions', json.pagination.total_count);
            investmentStore.setPage('positions', json.pagination.current_page);
        },
        (error) => {
            console.error('Error loading positions:', error);
        });
}
// handleInvestmentButton 함수도 단순화
export function handleInvestmentButton(type) {
    if (type) {
        investmentStore.setToggles(type);
    }
}




