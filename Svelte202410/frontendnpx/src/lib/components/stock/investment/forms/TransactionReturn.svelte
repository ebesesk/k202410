<script>
    import { slide } from 'svelte/transition';
    import fastapi from '$lib/api'
    import { get } from 'svelte/store';
    import { key, investInfoMap, accno_list } from "$lib/stores/stock";
    import { access_token, username, userpoints } from '$lib/store' 
    import { investmentStore, loadTransactions } from '$lib/components/stock/investment/js/investmentStores';
    import { onMount } from 'svelte';
    
    
    import TransactionPeriodicReturn from '$lib/components/stock/investment/forms/TransactionPeriodicReturn.svelte';
    
    // import { get } from 'svelte/store'; 

    onMount(async () => {
        await loadTransactions();
        console.log('investmentStores.transactions:', $investmentStore.transactions)
        console.log('investmentStore.pagination:', $investmentStore.pagination)
    });
    $: investmentStore.subscribe(state => {
        console.log('investmentStore.transactions:', state.transactions)
    })
    // $: filteredTransactions = $investmentStore?.transactions?.transactions?.filter(transaction => {
    //     if (!isUpdate) return true;
    //     return !['SELL_FEE', 'SELL_LOSS', 'SELL_PROFIT'].some(type => 
    //         transaction.type.includes(type)
    //     );
    // });
    
    // 숫자 포맷팅 함수
    function formatNumber(num, decimals = 0) {
        return new Intl.NumberFormat('ko-KR', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }).format(num);
    }



    // 계정 카테고리별 배경색 지정
    function getCategoryColor(category) {
        switch(category) {
            case '자산':
                return 'bg-asset';
            case '비용':
                return 'bg-expense'; 
            case '수익':
                return 'bg-income';
            case '자본':
                return 'bg-capital';
            case '부채':
                return 'bg-liability';
            default:
                return '';
        }
    }


    let showModal = false;
    let editingTransaction = null;

   

    const closeModal = () => {
        showModal = false;
        editingTransaction = null;
    };


    // type 변수 정의
    let type = 'transactions';  // 기본값 설정
    
    // 페이지네이션 관련 상태
    $: pagination = $investmentStore.pagination[type] || {
        currentPage: 1,
        totalItems: 0,
        itemsPerPage: 10
    };
    
    // totalPages 계산 시 숫자 확인
    $: totalPages = Math.max(1, Math.ceil(
        Number(pagination.totalItems) / Number(pagination.itemsPerPage)
    ));
    
    // 페이지 변경 핸들러
    function handlePageChange(page, currentKeyword) {
        // 숫자로 변환하여 확인
        const newPage = Number(page);
        if (!isNaN(newPage) && newPage >= 1 && newPage <= totalPages) {
            // 현재 keyword 값을 유지
            loadTransactions(newPage, currentKeyword || keyword);
        }
    }
    let keyword = 'asset'
    function setKeyword(page, newKeyword) {
        keyword = newKeyword;
        loadTransactions(page, newKeyword);
    }


    // 아코디언 상태를 저장할 객체 추가
    let expandedAssets = {};

    // 아코디언 토글 함수
    function toggleAsset(symbol) {
        expandedAssets[symbol] = !expandedAssets[symbol];
    }


    let assetRealAmountKRW = 0
    let assetRealAmountKRW_pl = 0
    let assetRealAmountUSD = 0
    let assetRealAmountUSD_pl = 0

    let assetRealAmount = {
        'KRW': {
            'amount': 0,
            'pl': 0
        },
    }
    $: {
    if ($investmentStore?.transactions?.assetRealAmount && $investInfoMap) {
        // 초기화
        assetRealAmountKRW = 0;
        assetRealAmountKRW_pl = 0;
        assetRealAmountUSD = 0;
        assetRealAmountUSD_pl = 0;
        
        // 임시 객체 생성 및 초기화
        let tempAssetRealAmount = {};
        
        tempAssetRealAmount['KRW'] = {
            amount: 0,
            pl: 0
        };
        tempAssetRealAmount['USD'] = {
            amount: 0,
            pl: 0
        };
        // 1. 먼저 모든 통화별 객체 초기화
        Object.values($investmentStore.transactions.assetRealAmount).forEach(account => {
            console.log('account(1. 먼저 모든 통화별 객체 초기화):', account);
            if (!tempAssetRealAmount[account.currency]) {
                tempAssetRealAmount[account.currency] = {
                    amount: 0,
                    pl: 0
                };
            }
        });

        // 2. 현재가 기준 금액 계산 (주식)
        Object.entries($investmentStore.transactions.assetRealAmount).forEach(([_key, _value]) => {
            const matchingKey = Object.keys($investInfoMap).find(key => _key.includes(key));
            if (matchingKey) {
                const currency = _value.currency;
                const price = $investInfoMap[matchingKey]?.t8407OutBlock1?.현재가;
                const quantity = _value.quantity;
                const amount = price * quantity;
                console.log('price krewkrwkrw:', price, quantity, amount);

                if (currency === 'KRW') {
                    assetRealAmountKRW += amount;
                    assetRealAmountKRW_pl += amount;
                    tempAssetRealAmount['KRW'].amount += amount;
                    tempAssetRealAmount['KRW'].pl += amount;
                } else if (currency === 'USD') {
                    assetRealAmountUSD += amount;
                    assetRealAmountUSD_pl += amount;
                    tempAssetRealAmount['USD'].amount += amount;
                    tempAssetRealAmount['USD'].pl += amount;
                }
            }
        });

        // 3. 기타 자산 금액 추가
        Object.entries($investmentStore.transactions.assetRealAmount).forEach(([_key, account]) => {
            if (!Object.keys($investInfoMap).some(key => _key.includes(key))) {
                tempAssetRealAmount[account.currency].amount += account.amount;
                tempAssetRealAmount[account.currency].pl += account.amount;
            }
        });

        Object.entries($investmentStore.transactions.analyze_currency.by_currency).forEach(([symbol, transaction]) => {
            // console.log('symbol:', symbol);
            // console.log('transaction:', transaction);
            // console.log('tempAssetRealAmount:', tempAssetRealAmount);
            for (let account of transaction.accounts) {
                // console.log('krwkrw account:', account);
                if (account.name === "LS증권주식" ) {
                    tempAssetRealAmount['KRW'].pl -= account.balance;
                } else if (account.name === "LS증권외환주식" ) {
                    tempAssetRealAmount['USD'].pl -= account.balance;
                }
            }
            
        });

        // 4. 최종 객체 할당
        assetRealAmount = tempAssetRealAmount;

        console.log('Updated assetRealAmount:', assetRealAmount);
        console.log('KRW totals:', assetRealAmountKRW, assetRealAmountKRW_pl);
        console.log('USD totals:', assetRealAmountUSD, assetRealAmountUSD_pl);
    }
}
let toggleTransactionReturn = false;
function viewTransactionReturn() {
    toggleTransactionReturn = !toggleTransactionReturn;
}

</script>

<!-- 1. 통화별 원본 데이터 -->
<!-- 데이터가 있을 때만 렌더링 -->
<button class="button-simple" on:click={viewTransactionReturn}>투자 수익 계산 보기</button>
{#if $investmentStore?.transactions && toggleTransactionReturn}
<div class="currency-section">
    {#if $investmentStore?.transactions?.analyze_currency?.by_currency}
        {#each Object.entries($investmentStore.transactions.analyze_currency.by_currency) as [currency, data]}
            <div class="currency-group">
                <h4>{currency}</h4>
                <div class="tables-container">
                    <!-- 차변 계정 (자산, 비용) -->
                    <div class="debit-accounts">
                        <h4>자산, 비용 계정</h4>
                        <div class="table-wrapper">
                            <table>
                                <thead>
                                    <tr>
                                        <th>계정명</th>
                                        <th>구분</th>
                                        <th>금액</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {#each data.accounts.filter(acc => ['자산', '비용'].includes(acc.category)) as account}
                                        {#if account.balance !== 0 && account.name !== "LS증권주식" && account.name !== "LS증권외환주식"}
                                            <tr class={getCategoryColor(account.category)}>
                                                <td>{account.name}</td>
                                                <td>{account.category}</td>
                                                <td class="amount">{formatNumber(account.balance)}</td>
                                            </tr>
                                        {:else if account.balance !== 0 && account.name == "LS증권주식" && currency == "KRW"}
                                            <tr class={getCategoryColor("자산")}>
                                                <td>{account.name}</td>
                                                <td>{account.category}</td>
                                                <td class="amount">{formatNumber($accno_list[1][5])}</td>
                                            </tr>
                                        {:else if account.balance !== 0 && account.name == "LS증권외환주식" && currency == "USD"}
                                            <tr class={getCategoryColor("자산")}>
                                                <td>{account.name}</td>
                                                <td>{account.category}</td>
                                                <td class="amount">{formatNumber(assetRealAmount['USD'].amount)}</td>
                                            </tr>
                                        {/if}
                                    {/each}
                                    <!-- {#if assetRealAmountKRW_pl < 0 && currency === "KRW"} -->
                                     {#if assetRealAmount['KRW'] && assetRealAmount['KRW'].pl < 0}
                                        <tr class={getCategoryColor("손실")}>
                                            <td>평가손실</td>
                                            <td>손실</td>
                                            <td class="amount">{formatNumber(-1*assetRealAmount['KRW'].pl)}</td>
                                        </tr>
                                    {:else if assetRealAmount['USD'] && assetRealAmount['USD'].pl < 0}
                                        <tr class={getCategoryColor("손실")}>
                                            <td>평가손실</td>
                                            <td>손실</td>
                                            <td class="amount">{formatNumber(-1*assetRealAmount['USD'].pl)}</td>
                                        </tr>
                                    {/if}

                                </tbody>
                                <tfoot>
                                    <tr>
                                        <td colspan="2">차변 합계</td>
                                        {#if assetRealAmount['KRW'] && currency === "KRW"}
                                            <td class="amount">
                                                {formatNumber(data.accounts
                                                    .filter(acc => ['자산', '비용'].includes(acc.category))
                                                    .reduce((sum, acc) => sum + acc.balance, 0) + assetRealAmount['KRW'].pl)}
                                            </td>
                                        {:else if assetRealAmount['USD'] && currency === "USD"}
                                            <td class="amount">
                                                {formatNumber(data.accounts
                                                    .filter(acc => ['자산', '비용'].includes(acc.category))
                                                    .reduce((sum, acc) => sum + acc.balance, 0) + assetRealAmount['USD'].pl)}
                                            </td>
                                        {:else}
                                            <td class="amount">
                                                {formatNumber(data.accounts
                                                    .filter(acc => ['자산', '비용'].includes(acc.category))
                                                    .reduce((sum, acc) => sum + acc.balance, 0))}
                                            </td>
                                        {/if}
                                    </tr>
                                </tfoot>
                            </table>
                        </div>
                    </div>
                
                    <!-- 대변 계정 (부채, 자본, 수익) -->
                    <div class="credit-accounts">
                        <h4>부채, 자본, 수익 계정</h4>
                        <div class="table-wrapper">
                            <table>
                                <thead>
                                    <tr>
                                        <th>계정명</th>
                                        <th>구분</th>
                                        <th>금액</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {#each data.accounts.filter(acc => ['부채', '자본', '수익'].includes(acc.category)) as account}
                                        {#if account.balance !== 0}
                                            <tr class={getCategoryColor(account.category)}>
                                                <td>{account.name}</td>
                                                <td>{account.category}</td>
                                                <td class="amount">{formatNumber(account.balance)}</td>
                                            </tr>
                                        {/if}
                                    {/each}
                                    {#if currency === "KRW"}
                                        <tr class={getCategoryColor("수익")}>
                                            <td>평가이익</td>
                                            <td>수익</td>
                                            <td class="amount">{formatNumber(assetRealAmount['KRW'].pl)}</td>
                                        </tr>
                                    <!-- {/if} -->
                                    {:else if currency === "USD"}
                                        <tr class={getCategoryColor("수익")}>
                                            <td>평가이익</td>
                                            <td>수익</td>
                                            <td class="amount">{formatNumber(assetRealAmount['USD'].pl)}</td>
                                        </tr>
                                    {/if}
                                </tbody>
                                <tfoot>
                                    <tr>
                                        <td colspan="2">대변 합계</td>
                                        {#if assetRealAmount['KRW'] && currency === "KRW" && assetRealAmount['KRW'].pl > 0}
                                            <td class="amount">
                                                {formatNumber(data.accounts
                                                    .filter(acc => ['부채', '자본', '수익'].includes(acc.category))
                                                    .reduce((sum, acc) => sum + acc.balance, 0) + assetRealAmount['KRW'].pl)}
                                            </td>
                                        {:else if assetRealAmount['USD'] && currency === "USD" && assetRealAmount['USD'].pl > 0}
                                            <td class="amount">
                                                {formatNumber(data.accounts
                                                    .filter(acc => ['부채', '자본', '수익'].includes(acc.category))
                                                    .reduce((sum, acc) => sum + acc.balance, 0) + assetRealAmount['USD'].pl)}
                                            </td>
                                        {:else}
                                            <td class="amount">
                                                {formatNumber(data.accounts
                                                    .filter(acc => ['부채', '자본', '수익'].includes(acc.category))
                                                    .reduce((sum, acc) => sum + acc.balance, 0))}
                                            </td>
                                        {/if}
                                    </tr>
                                    {#each $investmentStore?.transactions?.transactions?.EXCHANGE as exchange}
                                        {#if exchange.note == currency}
                                            <tr>
                                                <td class="plain" colspan="3">{exchange.date.split('T')[0]}</td>
                                            </tr>
                                            <tr>
                                                <td class="plain">{formatNumber(exchange.amount)}</td>
                                                <td class="plain">{formatNumber(exchange.exchange_rate, 2)}</td>
                                                <td class="plain">{formatNumber(exchange.quantity)}</td>
                                            </tr>
                                        {/if}
                                    {/each}
                                </tfoot>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        {/each}
    {/if}
</div>
{/if}



<!-- <TransactionPeriodicReturns transactions={$investmentStore.transactions.transactions} /> -->





<style>
    .button-simple {
        background-color: #f5f5f5;
        border: none;
        border-radius: 0.1rem;
        font-size: 0.7rem;
        font-weight: 500;
        color: #333;
    }

    .currency-section {
        margin: 0.1rem;
    }



    /* h3 {
        color: #666;
        margin: 1rem 0;
        font-size: 1rem;
    } */

    .currency-group {
        margin-bottom: 2rem;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.8rem;
    }

    th, td {
        padding: 0.5rem;
        text-align: left;
        border-bottom: 1px solid #ddd;
    }

    th {
        background-color: #f5f5f5;
        font-weight: bold;
    }



    tfoot td {
        font-weight: bold;
        border-top: 2px solid #000;
    }

    /* 계정 카테고리별 배경색 */
    .bg-asset {
        background-color: rgba(200, 230, 201, 0.3);
    }
    
    .bg-expense {
        background-color: rgba(255, 205, 210, 0.3);
    }
    
    .bg-income {
        background-color: rgba(179, 229, 252, 0.3);
    }
    
    .bg-capital {
        background-color: rgba(225, 190, 231, 0.3);
    }

    .bg-liability {
        background-color: rgba(255, 224, 178, 0.3);
    }

    tr:hover {
        filter: brightness(0.95);
    }
    /* tr:nth-child(even) {
        background-color: rgba(0, 0, 0, 0.02);
    } */


    .sort-container {
        display: flex;
        flex-direction: row;
        gap: 1rem;
        margin: 0.1rem;
        padding: 0.1rem;
        background-color: #f5f5f5;
        border-radius: 0.1rem;
        font-size: 0.7rem;
        font-weight: 500;
        color: #333;
        justify-content: flex-start;
        align-items: center;
    }
    .table-wrapper {
        overflow-x: auto;
        width: 100%;
    }
    .tables-container {
        display: flex;  /* 가로 배열 */
        gap: 0.01rem;     /* 테이블 간 간격 */
        margin: 0.1rem;
        padding: 0.1rem;
    }


    .debit-accounts, .credit-accounts {
        flex: 1;       /* 동일한 너비로 분할 */
        min-width: 0;  /* 테이블 오버플로우 방지 */
        padding: 0.1rem;
        margin: 0.1rem 0;
        font-size: 0.7rem;
    }

    h4 {
        color: #444;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
        padding: 0.1rem;
        margin: 0.1rem 0;
    }



    .holdings-summary {
        padding: 0.1rem;
    }

    

    /* .amount {
        text-align: right;
        font-family: 'Courier New', monospace;
    } */

    .profit-positive {
        color: #d63031;
    }

    .profit-negative {
        color: #0984e3;
    }

    tr:hover {
        background-color: rgba(0, 0, 0, 0.02);
    }


    .transaction-section {
        margin: 0.1rem 0;
        display: flex;
        flex-direction: column;  /* 상하 배열 */
        gap: 0.1rem;              /* 섹션 간 간격 */
    }

    .tables-container.transaction-tables {
        display: flex;
        flex-direction: column;  /* 상하 배열 */
        /* gap: 0.01rem;   */
    }

    .table-wrapper.transaction-table {
        display: flex;
        flex-direction: column;
        overflow-x: auto;
        max-width: 100%;
    }
    .transaction-table {
        display: flex;
        flex-direction: column;
        overflow-x: auto;
        max-width: 100%;
        margin: 0.1rem 0;
        /* padding: 0.1rem; */
    }
    

    .list-item:hover {
        background-color: #f8f9fa;  /* 호버 시 배경색 변경 */
    }

    /* 짝수/홀수 행 구분을 위한 스타일 (선택사항) */
    .list-item:nth-child(even) {
        background-color: #f8f9fa;
    }

    .list-item:nth-child(even):hover {
        background-color: #f1f3f5;
    }

    /* 마지막 아이템의 구분선 제거 (선택사항) */
    .list-item:last-child {
        border-bottom: none;
    }

    .date {
        /* width: 10%; */
        font-size: 0.5rem;
    }
    .opacity-0 {
        /* 투명도 조절 */
        opacity: 0;
    }
    .type {
        /* color: #4370a3; */
        /* width: 10%; */
        font-size: 0.6rem;
    }
    .amount, .quantity, .name {
        text-align: right;
        font-size: 0.6rem;
        font-weight: 500;
    }
    .text-gradient {
        color: #3f51b5;  /* Google Blue */
        font-weight: 500;
        text-shadow: 1px 1px 1px rgba(0,0,0,0.1);
    }
    .currency {
        font-weight: 500;
        font-size: 0.5rem;
    }
    .text-muted {
        color: #6c757d;  /* 연한 회색 */
        font-size: 0.5rem;
    }
    .list-item {
        display: flex;  /* Flexbox 사용 */
        flex-direction: row;  /* 좌우 정렬 */
        align-items: center;  /* 세로 중앙 정렬 */
        justify-content: flex-start;  /* 좌측 정렬 */
        padding: 0.1rem;
        margin: 0.1rem 0;
        border-bottom: 1px solid #eee;
        background-color: #fff;
        transition: background-color 0.2s;
        gap: 0.1rem;  /* 항목 간 간격 */
    }
    /* 삭제 모드일 때의 스타일 */
    .list-item.transaction-table {
        /* position: relative; */
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: flex-start;  /* 좌측 정렬 */
        padding: 0.1rem 0.1rem;
        transition: all 0.2s ease;
        gap: 0.1rem;  /* 항목 간 간격 */
    }

    .clickable {
        cursor: pointer;
    }

    .clickable:hover {
        background-color: #f5f5f5;
    }

    .editable {
        background-color: #f8f9fa;
        border-left: 3px solid #4dabf7;  /* 수정 모드일 때 파란색 테두리 */
    }

    .editable:hover {
        background-color: #e9ecef;
    }

    .content {
        flex: 1;
    }

    .action-buttons {
        display: flex;
        gap: 0.1rem;
        margin-left: 0.1rem;
    }

    .edit-btn, .delete-btn {
        padding: 0.1rem 0.9rem;
        border: none;
        border-radius: 4px;
        font-size: 0.4rem;
        cursor: pointer;
        transition: all 0.2s;
    }

    .edit-btn {
        background-color: #4dabf7;
        color: white;
    }

    .edit-btn:hover {
        background-color: #339af0;
    }

    .delete-btn {
        background-color: #ff6b6b;
        color: white;
    }

    .delete-btn:hover {
        background-color: #fa5252;
    }

    

    /* 버튼 비활성화 스타일 */
    .edit-btn:disabled, .delete-btn:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    /* 버튼 로딩 상태 */
    .btn-loading {
        position: relative;
        color: transparent;
    }

    .btn-loading::after {
        content: "";
        position: absolute;
        width: 1em;
        height: 1em;
        border: 2px solid white;
        border-radius: 50%;
        border-top-color: transparent;
        animation: spin 1s linear infinite;
    }
    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    
    .get-transactions-all {
        margin: 0.1rem 0;
        padding: 0.1rem;
        font-size: 0.5rem;
        font-weight: 500;
        color: #333;
    }

    .modal-backdrop {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    }

    .modal-content {
        background-color: white;
        padding: 0.1rem;
        border-radius: 8px;
        min-width: 300px;
        max-width: 500px;
        width: 90%;
        max-height: 90vh;
        overflow-y: auto;
        font-size: 0.5rem;
    }

    .form-group {
        margin-bottom: 0.5rem;
        display: flex;
        flex-direction: row;
        gap: 0.1rem;
        align-items: center;
        justify-content: flex-end;
    }

    .modal-actions {
        display: flex;
        justify-content: flex-end;
        gap: 1rem;
        margin-top: 2rem;
    }

    .save-btn, .cancel-btn {
        padding: 0.5rem 1rem;
        border: none;
        border-radius: 4px;
        cursor: pointer;
    }

    .save-btn {
        background-color: #4dabf7;
        color: white;
    }

    .cancel-btn {
        background-color: #868e96;
        color: white;
    }

    /* 애니메이션 */
    .modal-backdrop {
        animation: fadeIn 0.2s ease;
    }

    .modal-content {
        background-color: white;
        padding: 0.8rem;  /* 패딩 감소 */
        border-radius: 4px;
        min-width: 200px;  /* 최소 너비 감소 */
        max-width: 400px;  /* 최대 너비 감소 */
        width: 80%;
        max-height: 80vh;  /* 최대 높이 제한 */
        overflow-y: auto;
        font-size: 0.8rem;  /* 폰트 크기 축소 */
    }
    .amount-select {
        width: 50%;
        padding: 0.3rem;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 0.8rem;
        height: 1.8rem;
        margin-bottom: 0.3rem;
    }
    .fee-input {
        width: 40%;
        padding: 0.3rem;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 0.5rem;
        height: 1rem;
    }
    .custom-amount {
        width: 70%;
        padding: 0.3rem;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 0.8rem;
        height: 1.8rem;
    }




    .pagination {
        display: flex;
        gap: 0.3rem;
        align-items: center;
        justify-content: center;
        margin: 0.3rem 0;
    }
    
    .page-btn {
        padding: 0.3rem 0.5rem;
        border: 1px solid #ddd;
        background: white;
        cursor: pointer;
        border-radius: 4px;
        min-width: 1.5rem;
        font-size: 0.5rem;
    }
    
    .page-btn:disabled {
        background: #f5f5f5;
        cursor: not-allowed;
    }
    
    .page-btn.active {
        background: #007bff;
        color: white;
        border-color: #007bff;
    }
    
    .ellipsis {
        padding: 0 0.5rem;
    }
    /* 셀렉트 화살표 커스텀 */
    .amount-select {
        appearance: none;
        background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
        background-repeat: no-repeat;
        background-position: right 0.5rem center;
        background-size: 1em;
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    @keyframes slideIn {
        from { transform: translateY(-20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }


    .fifo-section {
        margin: 0.2rem 0;
        padding: 0.2rem;
        background-color: var(--background-color);
        border-radius: 8px;
    }

    .year-selector {
        margin: 0.2rem 0;
        padding: 0.2rem;
    }

    .year-btn {
        margin: 0 0.5rem;
        padding: 0.2rem 0.5rem;
        border: 1px solid #ddd;
        border-radius: 4px;
        background: #f8f9fa;
        cursor: pointer;
        font-size: 0.9rem;
        font-weight: 500;
        color: #495057;
        transition: all 0.2s ease;
    }

    .year-btn:hover {
        background-color: #e9ecef;
        border-color: #adb5bd;
    }

    .year-btn.active {
        background-color: #4dabf7;  /* 밝은 파란색 */
        color: #fff;
        font-weight: 700;
        border-color: #339af0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        transform: translateY(-1px);
    }

    .year-btn.active:hover {
        background-color: #339af0;
        border-color: #228be6;
    }


    .fifo-table {
        width: 100%;
        border-collapse: collapse;
        margin: 1rem 0;
    }


    .number {
        text-align: right;
    }

    .profit {
        color: var(--profit-color, #4caf50);
    }

    .loss {
        color: var(--loss-color, #f44336);
    }

    .total-pl {
        font-size: 0.9rem;
        font-weight: bold;
        margin: 1rem 0;
    }



    .transactions-summary {
        padding: 0.1rem;
    }

    .asset-section {
        margin-bottom: 0.1rem;
    }

    /* .asset-section h2 {
        color: var(--text-color);
        margin-bottom: 0.5rem;
        padding-bottom: 0.3rem;
        border-bottom: 1px solid var(--border-color);
        font-size: 1rem;
    } */

    .asset-card {
        background: var(--background-color);
        border: 1px solid var(--border-color);
        border-radius: 4px;
        /* padding: 0.5rem; */
        margin-bottom: 0.5rem;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
        width: 100%;
    }
    
    .asset-header {
        cursor: pointer;
        user-select: none;
    }
    .header-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem;
    }
    .expand-icon {
        font-size: 0.8rem;
        color: var(--text-muted);
        transition: transform 0.2s ease;
    }

    .transactions-content {
        padding: 0.5rem;
        background: var(--background-color-light);
        border-top: 1px solid var(--border-color);
    }

    /* 호버 효과 */
    .asset-header:hover {
        background-color: var(--hover-color, rgba(0, 0, 0, 0.05));
    }
    .transaction-currency-group {
        padding: 0.3rem 0 0 0;
    }
    .asset-summary {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 0.3rem;
    }

    .summary-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.3rem;
        background: var(--background-color-light);
        border-radius: 3px;
        font-size: 0.8rem;
        width: 100%;
    }

    .label {
        color: var(--text-muted);
        font-size: 0.8rem;
    }

    .value {
        font-weight: 500;
        text-align: right;
        font-size: 0.8rem;
    }

    .profit {
        color: var(--profit-color, #4caf50);
    }

    .loss {
        color: var(--loss-color, #f44336);
    }

    .plain {
        text-decoration: none;
        border: none;
        border-bottom: none;
        background: none;
        font-size: 0.5rem;
        color: black;
        font-weight: 400;
        text-align: right;
    }
    .plain td {
        padding: 0.1rem;
    }
    
    /* 반응형 디자인을 위한 스타일 */
    @media (max-width: 768px) {
        table {
            font-size: 0.5rem;
        }

        th, td {
            padding: 0.1rem;
        }
        .list-item {
            padding: 0.1rem 0.1rem;
            font-size: 0.5rem;
        }
        .action-buttons {
            gap: 0.3rem;
        }

        .edit-btn, .delete-btn {
            padding: 0.1rem 0.1rem;
            font-size: 0.3rem;
        }
        .amount-select, .custom-amount {
            font-size: 0.5rem;
            height: 1.6rem;
        }
        .modal-content, .fee-input {
            padding: 0.1rem;
            font-size: 0.5rem;
        }
        .summary-item {
            font-size: 0.7rem;
        }
        .label {
            font-size: 0.6rem;
        }
        .value {
            font-size: 0.7rem;
        }
    }
</style>

