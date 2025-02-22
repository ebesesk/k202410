<script>
    import fastapi from '$lib/api';
    import { key, accno_list, account_table_items } from "$lib/stores/stock";
    export let isSetupKey;
    export let isLoading;
    export let cname;
    export let appkey;
    export let appsecretkey;
    export let clearKey;
    export let setupLsOpenApiDb;
    export let fetchAccnoList;
    export let toggleTradeLog;
    // export let isTradeLog;
    export let trade_tag;
    
    // let account_table_items = {}
    
    async function put_fdr_price_to_trade_tag() {
        console.log('trade_tag:', trade_tag);
        let ls_accno_codes = [];
        for (let item of $accno_list.slice(3)) {
            ls_accno_codes.push(item[0]);
        }
        console.log('ls_accno_codes:', ls_accno_codes);
        
        let table_items = {};
        for (let _currency of trade_tag.currencies) {
            table_items[_currency] = []
        }
        
        for (let [_key, _value] of Object.entries(trade_tag.asset_summary)) {
            for ([_key, _value] of Object.entries(_value)) {
                if (_key !== 'account' && _key !== 'exchange' && !trade_tag?.currencies.includes(_key)) {
                    for ([_key, _value] of Object.entries(_value)) {
                        for ([_key, _value] of Object.entries(_value)) {
                            for ([_key, _value] of Object.entries(_value)) {
                                if (trade_tag.currencies.includes(_key) && !ls_accno_codes.includes(_value.code)) {
                                    console.log('ls_accno_codes:', ls_accno_codes);
                                    console.log('_key:', _key);
                                    console.log('_value:', _value);
                                    let code = _value.code;     // 종목코드
                                    let quantity = _value.quantity;     // 수량
                                    let purchases_price = _value.purchases_price;     // 매입가
                                    console.log('purchases_price:', purchases_price);
                                    let purchases_amount = purchases_price * quantity;     // 매입금액
                                    console.log('purchases_amount:', purchases_amount);
                                    let price = 0;
                                    // let price = await fastapi('get', '/stock/kis/get_price_by_code', {codes: code}, (json) => {
                                    //     price = json.price[code];
                                    //     console.log('kis_price:', price);
                                    // });
                                    table_items[_key].push({
                                        code: code, // 종목코드
                                        quantity: quantity, // 수량
                                        purchases_price:  _value.purchases_price, // 매입가
                                        purchases_amount: quantity * _value.purchases_price, // 매입금액
                                        price: price, // 현재가
                                        amount: quantity * price // 평가금액
                                    });
                                    console.log('table_items:', table_items);         
                                }
                            }
                        }
                    }
                }
            }
        }
        $account_table_items = table_items;
        // return table_items;
    }
    // }fastapi('get', '/stock/kis/get_price_by_code', {codes: _value.codes}, (json) => { })

$: account_table_items;
// $: put_fdr_price_to_trade_tag();
</script>

<div class="setup input-container">
    <!-- APP KEY 입력 그룹 -->
    <div class="setup input-group">
        {#if isSetupKey}
            <input 
                class="input-group input-field"
                type="text" 
                bind:value={cname} 
                placeholder="증권회사명을 입력하세요"
            >    
            <input 
                class="input-group input-field"
                type="text" 
                bind:value={appkey} 
                placeholder="appkey를 입력하세요"
            >   
            <input 
                class="input-group input-field"
                type="text" 
                bind:value={appsecretkey} 
                placeholder="appsecretkey를 입력하세요"
            >   
            <input 
                class="input-group key-input"
                type="password" 
                bind:value={$key} 
                placeholder="키를 입력하세요"
                disabled={isLoading}
            >
            
            <button 
                class="clear-button" 
                on:click={clearKey}
                title="키 초기화"
            >×</button>
        {/if}
    </div>

    <!-- 설정 계좌조회 버튼 그룹 -->
    <div class="setup button-group">
        <button 
            class="action-button"
            class:active-wss={isSetupKey}
            on:click={setupLsOpenApiDb}
        >
            설정
        </button>
        
        <button 
            class="action-button"
            class:loading={isLoading}
            on:click={fetchAccnoList}
            disabled={!key}
        >
            {#if isLoading}
                조회중...
            {:else}
                계좌조회
            {/if}
        </button>
        <button 
            class="action-button"
            on:click={toggleTradeLog}
        >
            매매일지
        </button>
    </div>
    <div class="setup button-group">
        <button 
            class="action-button"
        >
            주가조회
        </button>
        
        <button 
            class="action-button"
        >
            주가조회
        </button>
        <button 
            class="action-button"
            on:click={put_fdr_price_to_trade_tag}
        >
            주가조회
        </button>
    </div>
</div>

<style>
    .setup.input-container {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    .input-group {
        display: flex;
        gap: 0.5rem;
    }

    /* .input-field {
        padding: 0.5rem;
        border: 1px solid #ddd;
        border-radius: 4px;
    } */
    .input-field {
        height: 15px;  /* 높이 축소 */
        font-size: 10px;  /* 폰트 크기 축소 */
        padding: 0 4px;  /* 패딩 축소 */
        width: 80px;
    }

    .key-input {
        width: 80px;  /* 키 입력 필드 너비 */
        height: 15px;
        font-size: 10px;
        padding: 0 4px;
        width: 80px;
    }
    .action-button {
        flex: 1;
        padding: 8px 12px;
        font-size: 13px;
        border: none;
        border-radius: 4px;
        background-color: #f0f0f0;
        color: #333;
        cursor: pointer;
        transition: all 0.2s;
        min-width: 0;
        white-space: nowrap;
    }

    .active-wss {
        background-color: #4CAF50;
        color: white;
    }

    .action-button:hover {
        opacity: 0.9;
    }

    .action-button:disabled {
        background-color: #ccc;
        cursor: not-allowed;
    }

    .clear-button {
        position: absolute;
        right: 5px;
        background: none;
        border: none;
        color: #666;
        font-size: 18px;
        padding: 0 8px;
    }
    .setup.input-container {
        display: flex;
        flex-direction: column;  /* 수직 배열 */
        gap: 0.3rem;  /* 요소 간 간격 */
        width: 100%;
        padding: 0.3rem;
    }

    .setup.input-group {
        display: flex;
        flex-direction: row;  /* 입력 필드는 가로로 유지 */
        gap: 0.3rem;
        width: 100%;
    }

    .setup.button-group {
        display: flex;
        flex-direction: row;
        gap: 0.3rem;
        width: 100%;
    }
    
    
    
    /* ... 나머지 스타일 ... */
</style>