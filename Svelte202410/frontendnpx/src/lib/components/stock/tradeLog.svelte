<script>
    import { onMount } from 'svelte';
    import { writable } from 'svelte/store';
    import { browser } from '$app/environment';
    import {onDestroy} from 'svelte';    
    import { slide } from 'svelte/transition';  // slide 트랜지션 추가
    import fastapi from '$lib/api';
    import { username } from '$lib/store';
    import { key, trade_keyword } from "$lib/stores/stock";
    import { get } from 'svelte/store';
    import { access_token } from '$lib/store';
    import Pagination from '$lib/components/stock/Pagination.svelte';
    import { createChart } from 'lightweight-charts';
    import { numberToKorean, formatNumber } from '$lib/util';
    const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));
    
  
    onMount(async () => {
        
    });
 

// 매매일지 시작 /////////////////////////////////////////////////////////////////////////////////////////
    // 선택 가능한 항목 정의
    const detailOptions = [
        { value: '', label: '코드' },
        { value: '시가총액', label: '시총' },
        { value: '외국인', label: '외인' },
        { value: '배당수익율', label: '배당' },
        { value: 'PER', label: 'PER' },
        { value: 'ROE', label: 'ROE' },
        { value: 'tag', label: '태그' },
        { value: '업종구분명', label: '업종' }
    ];

    
    // 입력 폼 상태 관리
    let isTradeLog = false; // 매매일지 토글
    let isEditTrade = false; // 편집 토글
    let date = new Date().toISOString().split('T')[0];
    let assetCategory = '';  // stock, crypto, cash
    let market = '';  // KOSPI, KOSDAQ, NASDAQ, USD, KRW, 암호화폐
    let code = '';      // 종목코드 042700 AAPL, BTC, USD, KRW
    let name = '';
    let price = null;
    let quantity = null;
    let amount = null;
    let action = '';  // in, out
    let memo = '';
    let trade_id = null;
    // let username = '';

    // 태그 조회
    let trade_tag = {};
    // let assetCategories = [];   // stock, crypto, cash
    let assetCategories = [
        { value: 'stock', label: '주식,기타', trades: []},
        { value: 'cash', label: '현금', trades: [] },
        { value: 'exchange', label: '환전', trades: [] },
    ];  
    
    
    // 매매일지 토글
    function toggleTradeLog() {
        fastapi('get', '/stock/trades/all_tags', {}, (json) => {
            trade_tag = json;
            console.log('trade_tag:', trade_tag);
            // allTrades();
            // for (let i = 0; i < trade_tag.trade_asset_category.length; i++) {
            //     assetCategories[i].trades = fetchTrades(assetCategories[i].value);
            // }
            // console.log('assetCategories:', assetCategories);
        });
            // { value: 'crypto', label: '가상화폐'},
        isTradeLog = !isTradeLog;
    }
    // 편집 토글
    function toggleEditTrade() {
        
        if (isEditTrade) {
            clearTradeLog();
        }
        isEditTrade = !isEditTrade;
    }
    
    // let actualTradeType = '';
    $: {
        // 수량과 가격이 변경될 때 금액 자동 계산
        if (quantity && price) {
            // 소수점 두번째 자리 절삭
            amount = Math.floor(quantity * price * 100) / 100;
        }

    }
    function validateTradeLog() {
        const errors = [];
        // 공통 검증
        if (!date) errors.push('날짜를 입력하세요');
        if (!action) errors.push('거래 유형을 선택하세요');
        if (!assetCategory) errors.push('자산 구분을 선택하세요');
        // 주식, 가상화폐 검증
        if (assetCategory != 'cash' && assetCategory != 'exchange') {
            if (!code) errors.push('종목코드를 입력하세요');
            if (!market) errors.push('시장을 선택하세요');
            if (!name) errors.push('종목명을 입력하세요');
            if (!price) errors.push('가격을 입력하세요');
            if (!quantity) errors.push('수량을 입력하세요');
            if (!amount) errors.push('금액을 입력하세요');
        }
        else if (assetCategory === 'cash') {
            if (!code) errors.push('통화를 선택하세요');
            if (!amount) errors.push('금액을 입력하세요');
        }
        else if (assetCategory === 'exchange') {
            if (!name) errors.push('외화를 입력하세요');
            if (!code) errors.push('원화를 입력하세요');
            if (!quantity) errors.push('외화 금액을 입력하세요');
            if (!price) errors.push('환율을 입력하세요');
            if (!amount) errors.push('원화 금액을 입력하세요');
        }
        return errors;
    }
    // 거래 추가 함수
    function addTrade() {
        let trade_log = {};
        // 유효성 검사
        const errors = validateTradeLog(assetCategory, trade_log);
        
        if (assetCategory != 'cash' && assetCategory != 'exchange') {
            // 주식 거래 추가
            trade_log = {
                date: date,
                asset_category: assetCategory,  // stock, crypto, cash, exchange
                market: market,  // KOSPI, KOSDAQ, NASDAQ, USD, KRW, 암호화폐
                code: code,
                name: name,
                price: price,
                quantity: quantity,
                amount: amount,
                action: action,
                memo: memo,
            }
            console.log('addTrade trade_log:', trade_log);
            fastapi('post', '/stock/trade_log', trade_log, (json) => {
                console.log('주식 거래 로그:', json);
                // 성공 시에만 폼 초기화
                clearTradeLog();
                assetCategory = 'stock';
                // fetchTrades();
            });
           
        } else if (assetCategory === 'cash') {
            
            // 현금 거래 추가
            let transaction = {
                date: date,
                asset_category: assetCategory,  // stock, crypto, cash, exchange
                code: code,
                amount: amount,
                action: action,
                memo: memo,
            }
            console.log('addTrade transaction:', transaction);
            fastapi('post', '/stock/transaction_log', transaction, (json) => {
                console.log('주식 거래 로그:', json);
                // 성공 시에만 폼 초기화
                clearTradeLog();
                assetCategory = 'cash';
            });
        } else if (assetCategory === 'exchange') {
        
            // 환전 거래 추가
            let exchange = {
                date: date,
                asset_category: assetCategory,  // stock, crypto, cash, exchange
                name: name,   // 환전할 통화
                code: code,   // 환전받을 통화
                quantity: quantity, // 환전할 금액
                price: price,    // 환율
                amount: amount,   // 환전받을 금액
                action: action,
                memo: memo,
            }
            console.log('addTrade exchange:', exchange);
            fastapi('post', '/stock/exchange_log', exchange, (json) => {
                console.log('주식 거래 로그:', json);
                // 성공 시에만 폼 초기화
                clearTradeLog();
                assetCategory = 'exchange';
            });
        }
        
        
        if (errors.length > 0) {
            // 에러 메시지 표시
            alert(errors.join('\n'));
            return;
        }

        

        // 입력 폼 초기화
        name = '';
        code = '';
        action = '';
        memo = '';
        assetCategory = '';
        market = '';
        action = '';        
        quantity = null;
        price = null;
        amount = null;
    }

    // id로 거래 삭제
    function deleteTrade(id) {

        // 경고 메시지 표시
        console.log('deleteTrade id:', id);
        if (confirm('정말로 삭제하시겠습니까?')) {
            fastapi('delete', '/stock/trade_log', {id: id}, (json) => {
                console.log('거래 삭제:', json);
                fetchTrades();
            });
        }
    }

    function tradeEdit(id) {
        console.log('tradeEdit id:', id);
        console.log('tradeEdit trade_log:', trades);
        let edit_trade = trades.find(trade => trade.id === id);
        console.log('edit_trade:', edit_trade);
        trade_id = id;
        date = edit_trade.date;
        name = edit_trade.name;
        code = edit_trade.code;
        assetCategory = edit_trade.asset_category;
        market = edit_trade.market;
        action = edit_trade.action;
        quantity = edit_trade.quantity;
        price = edit_trade.price;
        amount = edit_trade.amount;
        // username = edit_trade.username;
        memo = edit_trade.memo;
    }
    function updateTrade() {
        console.log('updateTrade');
        let trade_log = {
            id: trade_id,
            date: date,
            name: name,
            code: code,
            asset_category: assetCategory,
            market: market,
            action: action,
            quantity: quantity,
            price: price,
            amount: amount,
            username: $username,
            memo: memo,
        }

        fastapi('put', '/stock/trade_log', trade_log, (json) => {
            console.log('거래 수정:', json);
            clearTradeLog();
            isEditTrade = false;
            fetchTrades();
        });
    }

    // 입력 폼 초기화   
    function clearTradeLog() {
        name = '';  // 종목명
        // code = '';  // 종목코드
        memo = '';  // 메모
        // assetCategory = '';  // stock, crypto, cash, exchange
        market = '';  // KOSPI, KOSDAQ, NASDAQ
        action = '';  // in, out
        quantity = null;
        price = null;
        amount = null;
    }
    function resetTradeLog() {
        name = '';  // 종목명
        code = '';  // 종목코드
        market = '';  // KOSPI, KOSDAQ, NASDAQ
        action = '';  // in, out
        quantity = null;
        price = null;
        amount = null;
        if (!assetCategory.includes('cash') && !assetCategory.includes('exchange')) {
            name = '';  // 종목명
            code = '';  // 종목코드
            market = '';  // KOSPI, KOSDAQ, NASDAQ
            action = '';  // in, out
            quantity = null;
            price = null;
            amount = null;
        } else if (assetCategory.includes('cash')) {
            code = 'KRW';  // 통화
            amount = null;  // 금액
            action = '';  // in, out
        } else if (assetCategory.includes('exchange')) {
            name = 'USD';   // 환전할 통화
            code = 'KRW';   // 환전받을 통화
            quantity = null; // 환전할 금액
            price = null;    // 환율
            amount = null;   // 환전받을 금액
            action = '';  // in, out
        }
        $trade_keyword = {};
        fetchTrades();
    }


    
    // 페이지네이션 추가 /////////////////////////////////////////////////////////////////////////////////////////
    // 페이지네이션 변수 선언
    let paginatedTrades = []; // 페이지네이션된 데이터를 저장할 변수 추가
    let currentPage = 1;
    let itemsPerPage = 10;
    let totalItems = 0;
    let totalPages = 0;
    let trades = []; // 전체 거래 데이터
    let startDate = '';
    let endDate = '';
    let tradeAssetCategories = [];
    
    // 거래 데이터 조회
    async function fetchTrades(trade_code = null) {
        console.log('fetchTrades $trade_keyword:', $trade_keyword);
        try {
            let params = {
                skip: (currentPage - 1) * itemsPerPage,
                limit: itemsPerPage,
            };
            if (Object.keys($trade_keyword).length > 0) {
                params = { ...params, ...$trade_keyword };
            }

            
            console.log('fetchTrades params:', params);
            // 선택적 파라미터들은 값이 있을 때만 추가
            // if (trade_code) params.code = trade_code;
            if (startDate) params.start_date = startDate;
            if (endDate) params.end_date = endDate;
            if (assetCategory) params.asset_category = assetCategory;
            // $trade_keyword.set(params);
            // console.log('fetchTrades params:', params);
            fastapi('get', '/stock/trade_log', params, (json) => {
                trades = json.items; // 페이지네이션된 거래 데이터
                console.log('fetchTrades trades:', trades);
                totalItems = json.total; // 전체 거래 수
                totalPages = Math.ceil(totalItems / itemsPerPage); // 전체 페이지 수
            });
        } catch (error) {
            console.error('Error fetching trades:', error);
        }
    }
    function searchByCode(code) {
        $trade_keyword.code = code;
        fetchTrades();
    }

    // assetCategory가 변경될 때마다 데이터 다시 로드
    $: {
        // 수량과 가격이 변경될 때 금액 자동 계산
        if (quantity && price) {
            // 소수점 두번째 자리 절삭
            amount = Math.floor(quantity * price * 100) / 100;
        }
        if (assetCategory) {
            // assetCategory = assetCategory.split(',')[0];
            currentPage = 1;
            console.log('currentPage:', currentPage);
            // fetchTrades();
        }
    }
    

    // 페이지네이션 추가 끝 /////////////////////////////////////////////////////////////////////////////////////////
    


    // 컴포넌트 언마운트 시 연결 종료
    onDestroy(() => {

    
    });
</script>

    {#if isTradeLog}
        <div class="setup-trade-log-container">
            
            <!-- 입력 폼 -->
            <div class="trade-log-input-form">
                    
                
                <div class="input-row" style = "padding-bottom: 20px;">
                    {#if !isEditTrade}
                        <button 
                            class="add-trade-button"
                            on:click={addTrade}
                        >
                            추가
                        </button>
                    {/if}
                    {#if isEditTrade}
                        <button 
                            class="add-trade-button update-color"
                            on:click={updateTrade}
                        >
                            수정
                        </button>
                    {/if}
                    
                    <button 
                        class="add-trade-button"
                        class:edit-trade={isEditTrade}
                        on:click={toggleEditTrade}
                    >
                        편집
                    </button>
                    <input 
                        type="date" 
                        bind:value={date}
                        autocomplete="off"
                        autocorrect="off"
                        autocapitalize="off"
                        spellcheck="false"
                        class="trade-input date-input"
                    />
                    {#if !isEditTrade}
                        <select 
                            bind:value={assetCategory}
                            class="category-select trade-input"
                            on:change={() => resetTradeLog()}
                        >
                            <option value="">구분 선택</option>
                            {#each assetCategories as category}
                                <option value={category.value}>{category.label}</option>
                            {/each}
                        </select>
                    {/if}
                    <!-- {#if assetCategory === 'stock' || assetCategory === 'crypto' || assetCategory === 'exchange'} -->
                    {#if !assetCategory.includes('cash')}    
                        <div class="radio-group">
                            <label class="radio-label">
                                <input 
                                    type="radio" 
                                    bind:group={action} 
                                    value="in"
                                    class="trade radio-input"
                                />
                                <span class="radio-text">Buy</span>
                            </label>

                            <label class="radio-label">
                                <input 
                                    type="radio" 
                                    bind:group={action} 
                                    value="out"
                                    class="trade radio-input"
                                />
                                <span class="radio-text">Sell</span>
                            </label>
                        </div>
                    {/if}
                    {#if assetCategory.includes('cash')}
                        <div class="radio-group">
                            <label class="radio-label">
                                <input 
                                    type="radio" 
                                    bind:group={action} 
                                    value="in"
                                    class="trade radio-input"
                                />
                                <span class="radio-text">Deposit</span>
                            </label>
                            <label class="radio-label">
                                <input 
                                    type="radio" 
                                    bind:group={action} 
                                    value="out"
                                    class="trade radio-input"
                                />
                                <span class="radio-text">Withdraw</span>
                            </label>
                        </div>
                    {/if}
                </div>
                
                <!-- 주식, 가상화폐 거래 입력 폼 -->
                <!-- {#if assetCategory.split(',')[0] != 'exchange' && assetCategory.split(',')[0] != 'cash' && action != ''} -->
                {#if !assetCategory.includes('exchange') && !assetCategory.includes('cash') && action != ''}
                <div class="stock input-row">
                        <input 
                            type="text" 
                            bind:value={assetCategory}
                            placeholder="구분"
                            class="trade-input category-input gubun-input"
                        />
                        {#each trade_tag.asset_category as _asset_category}
                            <button 
                                class="tag-button badge"
                                on:click={() => {assetCategory = _asset_category}}
                                tabindex="0"
                            >
                                {_asset_category}
                            </button>
                        {/each}
                        , 콤마로 구분
                    </div>
                    <div class="input-row">
                        <input 
                            type="text" 
                            bind:value={market}
                            placeholder="시장구분"
                            class="trade-input gubun-input"
                        />
                        {#each trade_tag.trade_market as _market}
                            <button 
                                class="tag-button badge"
                                on:click={() => {market = _market}}
                                tabindex="0"
                            >
                                {_market}
                            </button>
                        {/each}
                    </div>

                    <!-- 종목명 검색 입력 폼 -->
                    <div class="input-row">
                        <div class="search-container">
                            <input 
                                type="text" 
                                bind:value={name}
                                placeholder="종목명"
                                autocomplete="off"
                                autocorrect="off"
                                autocapitalize="off"
                                spellcheck="false"
                                
                                class="trade-input gubun-input stock-input"
                                on:input={handleSearchInput}
                                on:keydown={tradeSearch}
                            />
                            {#if searchResults.length > 0}
                                <div class="search-results" transition:slide>
                                    {#each searchResults as result, index}
                                        <button 
                                            class="search-result-item"
                                            class:selected={index === selectedIndex}
                                            on:click={() => {
                                                code = result.shcode; 
                                                name = result.shname;
                                                searchResults = [];
                                                selectedIndex = -1;
                                                if (result.gubun === '1') {
                                                    market = 'KOSPI';
                                                } else if (result.gubun === '2') {
                                                    market = 'KOSDAQ';
                                                }
                                            }}
                                            on:mouseenter={() => selectedIndex = index}
                                        >
                                            <span class="result-code">{result.shcode}</span>
                                            <span class="result-name">{result.shname}</span>
                                        </button>
                                    {/each}
                                </div>
                            {/if}
                        </div>
                        <div class="trade-name-container">
                            {#each trade_tag.trade_name as _name}
                                <button 
                                    class="tag-button small-badge"
                                    on:click={() => {
                                        name = _name.name;
                                        code = _name.code;
                                        market = _name.market;
                                    }}
                                    tabindex="0"
                                >
                                    {_name.name}
                                </button>
                            {/each}
                        </div>
                        {#if _stocks.length > 0}
                            <select 
                                class="trade-input gubun-input"
                                on:change={(e) => {
                                    const stock = _stocks.find(s => s.한글기업명 === e.target.value);
                                    if (stock) {
                                        name = stock.한글기업명;
                                        code = stock.종목코드;
                                        market = stock.시장구분 === '1' ? 'KOSPI' : 'KOSDAQ';
                                    }
                                }}
                            >
                                <option value="">종목 선택</option>
                                {#each _stocks as stock}
                                    <option value={stock.한글기업명}>
                                        {stock.한글기업명}
                                    </option>
                                {/each}
                            </select>
                        {/if}

                    </div>
                    <!-- 종목명 검색 입력 폼 끝-->

                
                    <div class="input-row">
                        <input 
                            type="text" 
                            bind:value={code}
                            placeholder="종목코드"
                            autocomplete="off"
                            autocorrect="off"
                            autocapitalize="off"
                            spellcheck="false"
                            class="trade-input gubun-input"
                        />
                        
                    </div>
                    
                    <div class="input-row">
                        
                        <input 
                            type="number" 
                            bind:value={quantity}
                            placeholder="수량"
                            autocomplete="off"
                            autocorrect="off"
                            autocapitalize="off"
                            spellcheck="false"
                            class="quantity trade-input"
                            class:trade-blue={action === 'out'}
                            class:trade-red={action === 'in'}
                        />
                        <span class="amount-korean">{formatNumber(quantity)}주</span>
                    </div>
                    <div class="input-row">
                        <input 
                            type="number" 
                            bind:value={price}
                            placeholder="가격"
                            autocomplete="off"
                            autocorrect="off"
                            autocapitalize="off"
                            spellcheck="false"
                            class="price trade-input"
                        />
                        <span class="amount-korean">{formatNumber(price)}원</span>
                    </div>
                    <div class="input-row">
                        <input 
                            type="number" 
                            bind:value={amount}
                            placeholder="금액"
                            autocomplete="off"
                            autocorrect="off"
                            autocapitalize="off"
                            spellcheck="false"
                            class="amount trade-input"
                            class:trade-red={action === 'out'}
                            class:trade-blue={action === 'in'}
                            />
                            <!-- readonly -->
                        <span class="amount-korean">{formatNumber(amount)}원</span>
                    </div>
                {/if}
                <!-- 환전 거래 입력 폼 -->
                {#if assetCategory.includes('exchange') && action != ''}
                    <div class="stock input-row">
                        <input 
                        type="text" 
                        bind:value={assetCategory}     
                        placeholder="구분"
                        autocomplete="off"
                        autocorrect="off"
                        autocapitalize="off"
                        spellcheck="false"
                        class="trade-input gubun-input"
                        />
                    </div>
                    <div class="input-row">
                        <!-- 환전할 통화 -->
                        <input 
                            type="text" 
                            bind:value={name}
                            placeholder="외화 USD"
                            autocomplete="off"
                            autocorrect="off"
                            autocapitalize="off"
                            spellcheck="false"
                            class="trade-input gubun-input"
                        />
                        {#each trade_tag.exchange_name as exchange}
                            <button 
                                class="tag-button badge"
                                on:click={() => {name = exchange}}
                                tabindex="0"
                            >
                                {exchange}
                            </button>
                        {/each}
                    </div>
                    <div class="input-row">
                        <!-- 환전받을 통화 -->
                        <input 
                            type="text" 
                            bind:value={code}
                            placeholder="원화 KRW"
                            autocomplete="off"
                            autocorrect="off"
                            autocapitalize="off"
                            spellcheck="false"
                            class="trade-input gubun-input"
                        />
                        {#each trade_tag.exchange_code as exchange}
                            <button 
                                class="tag-button badge"
                                on:click={() => {code = exchange}}
                                tabindex="0"
                            >
                                {exchange}
                            </button>
                        {/each}
                    </div>
                    
                    <div class="input-row">
                        <!-- 환전할 금액 -->
                        <input 
                            type="number" 
                            bind:value={quantity}
                            placeholder="외화금액 USD"
                            autocomplete="off"
                            autocorrect="off"
                            autocapitalize="off"
                            spellcheck="false"
                            class="exchange trade-input"
                            class:trade-blue={action === 'out'}
                            class:trade-red={action === 'in'}
                        />
                        <span class="amount-korean">{formatNumber(quantity)}</span>
                    </div>
                    <div class="input-row">
                        <!-- 환율 -->
                        <input 
                            type="number" 
                            bind:value={price}
                            placeholder="환율"
                            autocomplete="off"
                            autocorrect="off"
                            autocapitalize="off"
                            spellcheck="false"
                            class="exchange trade-input"
                        />
                        <span class="amount-korean">{formatNumber(price)}원</span>
                    </div>
                    <div class="input-row">
                        <!-- 환전받을 금액 -->
                        <input 
                            type="number" 
                            bind:value={amount}
                            placeholder="원화금액 KRW"
                            autocomplete="off"
                            autocorrect="off"
                            autocapitalize="off"
                            spellcheck="false"
                            class="exchange trade-input"
                            class:trade-red={action === 'out'}
                            class:trade-blue={action === 'in'}
                            />
                            <!-- readonly -->
                        <span class="amount-korean">{formatNumber(amount)}원</span>
                    </div>
                {/if}
                {#if assetCategory.includes('cash') && action != ''}
                    <div class="input-row">
                        <input 
                            type="text" 
                            bind:value={assetCategory}
                            placeholder="구분"
                            autocomplete="off"
                            autocorrect="off"
                            autocapitalize="off"
                            spellcheck="false"
                            class="trade-input gubun-input"
                        />
                    </div>
                    <div class="input-row">
                        <input 
                            type="text" 
                            bind:value={code}
                            placeholder="통화"
                            autocomplete="off"
                            autocorrect="off"
                            autocapitalize="off"
                            spellcheck="false"
                            class="trade-input gubun-input"
                        />
                        {#each trade_tag.cash_code as cash}
                            <button 
                                class="tag-button badge"
                                on:click={() => {code = cash}}
                                tabindex="0"
                            >
                                {cash}
                            </button>
                        {/each}
                    </div>
                    <div class="input-row">
                        <input 
                            type="number" 
                            bind:value={amount}
                            placeholder="금액"
                            autocomplete="off"
                            autocorrect="off"
                            autocapitalize="off"
                            spellcheck="false"
                            class="trade-input gubun-input"
                            class:trade-red={action === 'in'}
                            class:trade-blue={action === 'out'}
                        />
                        <span class="amount-korean">{formatNumber(amount)}원</span>
                        <span class="amount-korean">{numberToKorean(amount)}원</span>
                    </div>
                {/if}
                <div class="input-row">
                    <input 
                        type="text" 
                        bind:value={memo}
                        placeholder="메모"
                        class="memo trade-input"
                    />
                </div>
            </div>
            <!-- 입력 폼 끝 -->

            <!-- 테이블 -->
            <!-- 선택 버튼 stock, crypto, cash, exchange -->
            <div class="setup-trade-log-table">
                <div class="input-row">
                    <!-- <button 
                        class="tag-button badge add-trade-button"
                        class:active={assetCategory === ''}
                        on:click={() => {
                            // code='';
                            // startDate = '';
                            // endDate = '';
                            // assetCategory = '';
                            // fetchTrades()
                            allTrades()
                        }}
                        tabindex="0"
                    >
                        전체
                    </button> -->
                    {#each trade_tag.asset_category as _asset_category}
                        <button 
                            class="tag-button badge add-trade-button"
                            class:active={assetCategory === _asset_category}
                            on:click={() => {
                                assetCategory = _asset_category;
                                code = '';
                                startDate = '';
                                endDate = '';
                                $trade_keyword = {};
                                fetchTrades()
                            }}
                            tabindex="0"
                        >
                            {_asset_category}
                        </button>
                    {/each}
                </div>


                <!-- 테이블 시작 -->
                <div class="setup-trade-log-table">

                    {#if !assetCategory.includes('exchange') && !assetCategory.includes('cash') && assetCategory != ''}
                        <!-- 주식, 가상화폐 -->
                        <p class="trade-log-table-title">주식, 가상화폐, 기타</p>
                        <table class="trade-log-table">
                            <thead>
                                <tr>
                                    <th class="text-right">날짜</th>
                                    <!-- <th class="text-right">구분</th> -->
                                    <th class="text-right">시장구분</th>
                                    <th class="text-right">종목명</th>
                                    <th class="text-right">수량</th>
                                    <th class="text-right">가격</th>
                                    <th class="text-right">금액</th>
                                </tr>
                            </thead>
                            <tbody>
                                {#each trades as trade}
                                    <tr>
                                        <td class="trade-date-cell text-right"
                                            class:text-blue={trade.quantity < 0}
                                        >
                                            {#if isEditTrade}
                                            <button 
                                                class="delete-badge"
                                                on:click={() => deleteTrade(trade.id)}
                                            >
                                                ×
                                            </button>
                                            <button 
                                                class="edit-badge"
                                                on:click={() => tradeEdit(trade.id)}
                                            >
                                                ✎
                                            </button>
                                            {/if}
                                            {trade.date}
                                        </td>
                                        <td class="text-right"
                                            class:text-blue={trade.quantity < 0}
                                        >{trade.asset_category}</td>
                                        <!-- <td class="text-right"
                                            class:text-bluet={trade.quantity < 0}
                                        >{trade.market}</td> -->
                                        <td class="text-right"
                                            class:text-blue={trade.quantity < 0}
                                        >
                                            <a 
                                                href="javascript:void(0)" 
                                                class="stock-link"
                                                on:click|preventDefault={() => searchByCode(trade.code)}
                                            >
                                                {trade.name}
                                            </a>
                                        </td>
                                        <td class="text-right"
                                            class:text-blue={trade.quantity < 0}
                                        >{formatNumber(trade.quantity)}</td>
                                        <td class="text-right"
                                            class:text-blue={trade.quantity < 0}
                                        >{formatNumber(trade.price)}</td>
                                        <td class="text-right"
                                            class:text-blue={trade.quantity < 0}
                                        >{formatNumber(trade.amount)}</td>
                                    </tr>
                                {/each}
                            </tbody>
                        </table>
                    {/if}

                    {#if assetCategory.includes('exchange')}
                        <p class="trade-log-table-title">환전, 통화</p>
                        <table class="trade-log-table">
                            <thead>
                                <tr>
                                    <th class="text-right">날짜</th>
                                    <th class="text-right">통화</th>
                                    <th class="text-right">원화</th>
                                    <th class="text-right">외화</th>
                                    <th class="text-right">환율</th>
                                    <th class="text-right">금액</th>
                                </tr>
                            </thead>
                            <tbody>
                                {#each trades as trade}
                                    <tr>
                                        <td class="trade-date-cell text-right"
                                            class:text-blue={trade.quantity < 0}
                                        >
                                            {#if isEditTrade}
                                            <button 
                                                class="delete-badge text-right"
                                                on:click={() => deleteTrade(trade.id)}
                                            >
                                                ×
                                            </button>
                                            {trade.id}
                                            <button 
                                                class="edit-badge"
                                                on:click={() => tradeEdit(trade.id)}
                                            >
                                                ✎
                                            </button>
                                            {/if}
                                            {trade.date}
                                        </td>
                                        <td class="text-right"
                                            class:text-blue={trade.quantity < 0}
                                        >{trade.name}</td>
                                        <td class="text-right"
                                            class:text-blue={trade.quantity < 0}
                                        >{trade.code}</td>
                                        <td class="text-right"
                                            class:text-blue={trade.quantity < 0}
                                        >{formatNumber(trade.quantity)}</td>
                                        <td class="text-right"
                                            class:text-blue={trade.quantity < 0}
                                        >{formatNumber(trade.price)}</td>
                                        <td class="text-right"
                                            class:text-blue={trade.quantity < 0}
                                        >{formatNumber(trade.amount)}</td>
                                    </tr>
                                {/each}
                            </tbody>
                        </table>
                    {/if}

                    {#if assetCategory.includes('cash')}
                        <p class="trade-log-table-title">현금</p>
                        <table class="trade-log-table">
                            <thead>
                                <tr>
                                    <th class="text-right">구분</th>
                                    <th class="text-right">날짜</th>
                                    <th class="text-right">통화</th>
                                    <th class="text-right">금액</th>
                                </tr>
                            </thead>
                            <tbody>
                                {#each trades as trade}
                                    <tr>
                                        <td class="trade-date-cell text-right">
                                            {#if isEditTrade}
                                                <button 
                                                    class="delete-badge"
                                                    on:click={() => deleteTrade(trade.id)}
                                                >
                                                    ×
                                                </button>
                                                <button 
                                                    class="edit-badge"
                                                    on:click={() => tradeEdit(trade.id)}
                                                >
                                                    ✎
                                                </button>
                                            {/if}
                                            {trade.date}
                                        </td>
                                        <td class="text-right">{trade.asset_category}</td>
                                        <td class="text-right">{trade.code}</td>
                                        <td class="text-right">{formatNumber(trade.amount)}</td>
                                    </tr>
                                {/each}
                            </tbody>
                        </table>
                    {/if}

                    
                    <div class="pagination-container">
                        <Pagination 
                            {currentPage}
                            {totalPages}
                            on:pageChange={(e) => {
                                currentPage = e.detail;
                                fetchTrades();  // 여기서 데이터 조회
                            }}
                        />
                    </div>
                </div>
            </div>
        </div>
    {/if}













<style>  
    .stock-input {
        height: 20px;
        width: 90px;
        font-size: 12px;
        padding: 0 4px;
        box-sizing: border-box;
    }
    
    
    input {
        height: 20px;  /* 입력창 높이 */
        box-sizing: border-box;
    }



    input {
        width: 100%;
        padding: 8px 30px 8px 8px;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 14px;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        font-size: 12px;
    }

    th, td {
        padding: 6px 8px;
        border-bottom: 1px solid #eee;
        white-space: nowrap;
    }

    th {
        background-color: #f8f9fa;
        font-weight: bold;
        text-align: center;
        position: sticky;
        top: 0;
        z-index: 1;
    }
    td {
        text-align: right;
    }

    .text-right {
        text-align: right;
    }
    

    button {
        align-self: flex-start;
        padding: 8px 16px;
        border: none;
        border-radius: 4px;
        background-color: #007bff;
        color: white;
        cursor: pointer;
    }

    button:hover {
        background-color: #0056b3;
    }



    
    .search-container {
        position: relative;
        width: 120px;
    }

    .search-results {
        position: absolute;
        top: 100%;
        left: 0;
        width: 100%;
        background: white;
        border: 1px solid #ddd;
        border-radius: 4px;
        max-height: 200px;
        overflow-y: auto;
        z-index: 1000;
        margin-top: 2px;
    }

    .search-result-item {
        width: 100%;
        padding: 4px 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: none;
        background: none;
        cursor: pointer;
        text-align: left;
    }

    .search-result-item:hover {
        background-color: #f5f5f5;
    }

    .result-code {
        color: #666;
        font-size: 11px;
    }

    .result-name {
        color: #333;
        font-size: 11px;
    }
    .search-result-item.selected {
        background-color: #e3f2fd;
    }

    .search-result-item:hover {
        background-color: #f5f5f5;
    }
    
    /* 매매일지 스타일 **************************************************/
    .setup-trade-log-container {
        border: 1px solid #ddd;
        border-radius: 4px;
        padding: 0.5rem;
        margin-top: 0.3rem;
        background-color: #fff;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        max-width: 100%;  /* 최대 너비 설정 */
        overflow: hidden; /* 스크롤 제거 */
    }

    /* 테이블 스타일 개선 */
    .trade-log-table {
        width: 100%;
        border-collapse: collapse;

    }

    .trade-log-table th,
    .trade-log-table td {
        padding: 0.2rem;
        border: 1px solid #eee;
        text-align: center;
        font-size: 6px;  /* 8px에서 7px로 축소 */
        white-space: nowrap;
    }

    .trade-log-table th {
    background-color: #f5f5f5;
    font-weight: 500;
    font-size: 6px;  /* 헤더도 동일하게 축소 */
}

    .trade-log-table tr:hover {
        background-color: #f8f9fa;  /* 행 호버 효과 */
    }
    
    .blue-background {
        background-color: #639bdb;  /* 파스텔 파란색 배경 */
    }
    .amount-korean {
    font-size: 6px;  /* 금액 한글 표시도 축소 */
    white-space: nowrap;
}
    /* 매매일지 입력 폼 스타일 */
    .trade-log-input-form {
        margin-bottom: 0.2rem;
        padding: 0.2rem;
        display: flex;
        flex-direction: column;
    }

    .input-row {
        display: flex;
        gap: 0.1rem;
        align-items: center;
        margin-bottom: 0.1rem;
        height: 1.2rem;  /* 0.8rem -> 1.2rem */
        gap: 0.5rem;  /* 간격 조정 */
        flex-wrap: nowrap;  /* 줄바꿈 방지 */
        width: 100%;  /* 전체 너비 사용 */
    }

    .trade-input {
        padding: 0 0.2rem;
        height: 1.2rem;
        font-size: 0.7rem;
        min-height: 1.2rem;
        line-height: 1.2rem;
        flex: 0 0 auto;  /* 크기 고정 */
    }

    .trade-input.quantity,
    .trade-input.price,
    .trade-input.amount,
    .trade-input.exchange {
        width: 120px;
        gap: 5rem;
    }
    .gubun-input {
        width: 100px;  /* 너비 축소 */
    }
    .amount-korean {
        white-space: nowrap;  /* 텍스트 줄바꿈 방지 */
        font-size: 0.7rem;
        min-width: 80px;  /* 최소 너비 설정 */
    }
    .date-input,
    select.trade-input {
        width: 110px;  /* 날짜 입력 폼 너비 축소 */
        height: 1.2rem;  /* 0.8rem -> 1.2rem */
        padding: 0 0.2rem;
        min-height: 1.2rem;
        font-size: 0.6rem;  /* 0.3rem -> 0.7rem */
    }

    .add-trade-button {
        padding: 0 0.2rem;
        height: 1.2rem;  /* 0.8rem -> 1.2rem */
        font-size: 0.7rem;  /* 0.3rem -> 0.7rem */
        line-height: 1.2rem;
        min-height: 1.2rem;
        width: 3rem;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* 테이블 셀 높이도 조정 */
    .trade-log-table th,
    .trade-log-table td {
        padding: 0.1rem 0.2rem;
        height: 1.2rem;  /* 0.8rem -> 1.2rem */
        line-height: 1.2rem;
        font-size: 0.7rem;  /* 글자 크기 통일 */
        white-space: nowrap;  /* 모든 td에 줄바꿈 방지 */
        text-align: right;
    }
    .trade-log-table td {
        padding: 0.1rem 0.2rem;
        height: 1.2rem;
        line-height: 1.2rem;
        font-size: 0.7rem;
        white-space: nowrap;
        vertical-align: middle;  /* 세로 중앙 정렬 추가 */
    }
    .radio-group {
        display: flex;
        gap: 1rem;
        align-items: center;
        height: 1.2rem;
        justify-content: flex-end;  /* 우측 정렬 추가 */
        margin-left: auto;  /* 왼쪽 여백을 자동으로 설정하여 오른쪽으로 밀기 */
    }

    .radio-label {
        display: flex;
        align-items: center;
        gap: 0.1rem;
        font-size: 0.7rem;
        cursor: pointer;
    }

    .radio-input {
        margin: 0;
        width: 0.8rem;
        height: 0.8rem;
    }

    .radio-text {
        font-size: 0.7rem;
        line-height: 1.2rem;
    }
    .gubun-input {
        width: 120px;
    }
    .trade-red {
        color: #f44336;  /* 입금: 적색 */
    }

    .trade-blue {
        color: #2196f3;  /* 출금: 청색 */
    }

    /* 입력 필드 포커스 시에도 색상 유지 */
    .trade-red:focus {
        color: #f44336;
        border-color: #f44336;
    }

    .trade-blue:focus {
        color: #2196f3;
        border-color: #2196f3;
    }
    .text-blue {
        color: blue;  /* 출금: 청색 */
        font-weight: 500;
    }
    .trade-log-table-title {
        font-size: 11px;
        font-weight: 500;
        color: #2c3e50;
        margin: 0.5rem 0 0.2rem 0;
        padding: 0.2rem 0.5rem;
        background-color: #f5f5f5;
        border: 1px solid #eee;
        border-bottom: none;
        border-radius: 4px 4px 0 0;
    }
    .trade-date-cell {
        position: relative;  /* 변경 */
        padding-left: 12px !important;  /* 삭제 버튼 공간 확보 */
        width: 90px;
        /* font-size: 10px; */
    }

    .delete-badge {
        position: absolute;  /* 변경 */
        left: 2px;          /* 왼쪽 여백 */
        top: 50%;           /* 세로 중앙 정렬 */
        transform: translateY(-50%);  /* 세로 중앙 정렬 보정 */
        min-width: 8px;     /* 크기 더 축소 */
        width: 12px;
        height: 12px;
        font-size: 6px;
        line-height: 1;
        padding: 0;
        border: none;
        border-radius: 50%;
        background-color: #e74c3c;
        color: white;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .small-badge {
        color: black;
        font-size: 8px;
        padding: 1px 3px;
        margin: 0 2px;
        white-space: nowrap;
        overflow: visible;
        text-overflow: clip;
        user-select: none;
        background-color: #f5f5f5;
        border: 1px solid #ddd;
        border-radius: 4px;
        cursor: pointer;
    }
    .small-badge:hover {
        background-color: #e0e0e0;
    }
    .edit-trade {
        background-color: #f44336;
    }
    .edit-badge {
        padding: 2px 6px;
        margin-right: 4px;
        border: none;
        border-radius: 4px;
        background-color: #2196f3;
        color: white;
        font-size: 12px;
        cursor: pointer;
        transition: background-color 0.2s;
    }

    .edit-badge:hover {
        background-color: #1976d2;
    }
    .update-color {
        background-color: #4caf50;
        color: white;
    }
    .stock-link {
        color: inherit;
        text-decoration: none;
        cursor: pointer;
    }

    .stock-link:hover {
        text-decoration: underline;
        color: #2196f3;
    }

    
    .badge {
        display: inline-block;
        padding: 1px 4px;
        font-size: 8px;
        font-weight: 500;
        line-height: 1;
        color: #fff;
        background-color: #2c3e50;
        border-radius: 12px;
        border: none;
        cursor: pointer;
        margin: 0 4px;
        white-space: nowrap;  /* 줄바꿈 방지 */
        overflow: visible;    /* 내용이 넘쳐도 보이게 */
        text-overflow: clip;  /* 텍스트 자르지 않음 */
        user-select: none;  /* 텍스트 선택 방지 */
    }

    .badge:hover {
        background-color: #34495e;
    }
    .badge.active {
        background-color: #f44336;
    }
    
    
    
    /* 전체 폰트 크기 조정 */
    :global(body) {
        font-size: 16px;
    }

    :global(button) {
        font-size: 16px;
        padding: 8px 16px;
    }

    :global(table) {
        font-size: 16px;
    }

    :global(th), :global(td) {
        padding: 12px;
    }
    
    table {
        width: fit-content;  /* 내용에 맞게 테이블 너비 조정 */
        min-width: auto;     /* 최소 너비 제한 해제 */
        border-collapse: collapse;
    }

    
    /* 모바일 대응 */
    @media (max-width: 768px) {
 

        .badge {
            font-size: 8px;
            padding: 1px 3px;
        }

        
    }
</style>