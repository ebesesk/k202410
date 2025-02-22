<script>
    import { formatNumber } from '$lib/util';
    import { investmentStore, loadPeriodicReturns } from '$lib/components/stock/investment/js/investmentStores';
    import { onMount } from 'svelte';
    import { get } from 'svelte/store';
    import fastapi from '$lib/api'

    let periodicReturns = [];

    // async function getPeriodicReturns() {
    //     let url = '/stock/investments/v2/transactions/get-periodic-returns-v2'
    //     fastapi('get', url, {}, 
    //     (json) => {
    //         console.log('json', json)
    //         $investmentStore.setPeriodicReturns(json)
    //     },
    //     (error) => {
    //         console.log('error', error)
    //     })    
    // }
    let toggleBalance = false;
    let toggleIncomeStatement = false;
    function viewBalance() {
        toggleBalance = !toggleBalance;
    }
    function viewIncomeStatement() {
        toggleIncomeStatement = !toggleIncomeStatement;
    }
    onMount(() => {
        loadPeriodicReturns()
        periodicReturns = get(investmentStore).periodicReturns
        console.log('periodicReturns:', periodicReturns);
    })

    $: periodicReturns = get(investmentStore).periodicReturns

</script>
<div class="button-group">
    <button class="button-simple" on:click={loadPeriodicReturns}>주기별 수익률 조회</button>
    <button 
        class="button-simple {toggleBalance ? 'active' : ''}" 
        on:click={viewBalance}
    >
        재무제표 조회
    </button>
    <button 
        class="button-simple {toggleIncomeStatement ? 'active' : ''}" 
        on:click={viewIncomeStatement}
    >
        손익계산서 조회
    </button>
</div>
{#if toggleIncomeStatement}    
    <div>
        {#if $investmentStore.periodicReturns.income_statement}
            <h3>손익계산서</h3>
            <div class="income-statement">
                {#each Object.entries($investmentStore.periodicReturns.income_statement) as [date, data]}
                    <div class="income-statement-row">
                        <h4>{date}</h4>
                        {#each Object.entries(data) as [currency, value]}
                            <span>{currency}</span>
                            {#each Object.entries(value) as [_key, value]}
                                {#if _key === 'revenues'}
                                    <span class="revenues">매출: {formatNumber(value.sales.total, 0)}</span>
                                    <span class="revenues details">회전율: {formatNumber(value.sales.turnover_rate, 2)} %</span>
                                    <!-- 매출 상세 -->
                                    {#each Object.entries(value.sales) as [_key, value]}
                                        {#if _key != 'total' && _key != 'turnover_rate'}
                                            <span class="revenues details">{_key}</span>
                                            {#each Object.entries(value) as [_key, value]}
                                                {#if _key != 'total' && _key != 'turnover_rate'}
                                                    <span class="revenues details-2">{_key}: {formatNumber(value, 0)}</span>
                                                {/if}
                                            {/each}
                                        {/if}
                                    {/each}
                                    <!-- 매출 상세 끝 -->
                                    <!-- 수익 상세 시작 -->
                                    <span class="revenues">수익: {formatNumber(value.total, 0)}</span>
                                    <!-- 매매차익 상세 시작  -->
                                    {#if value.매매차익?.total > 0}
                                        <span class="revenues details text-gradient">매매차익: {formatNumber(value.매매차익.total, 0)}</span>
                                        {#each Object.entries(value.매매차익) as [_key, value]}
                                            {#if _key != 'total' && _key != 'turnover_rate'}
                                                <span class="revenues details-2 text-gradient">{_key}: {formatNumber(value, 0)}</span>
                                            {/if}
                                        {/each}
                                    {/if}
                                    <!-- 매매차익 상세 끝 --> 
                                    <!-- 기타이이익 상세 시작 -->
                                    {#each Object.entries(value) as [_key, value]}
                                        {#if _key !== 'sales' && _key !== '매매차익' && _key !== 'total' && _key !== '평가차익' && _key !== 'valuation'}
                                            {#if value.total != 0}
                                                <span class="revenues details text-gradient">{_key}: {formatNumber(value.total, 0)}</span>
                                            {/if}
                                        {/if}
                                    {/each}
                                    <!-- 기타이이익 상세 끝 -->
                                    <!-- 평가차익 상세 시작 -->
                                    {#if value.평가차익 > 0}
                                        <span class="revenues details text-gradient">평가차익: {formatNumber(value.평가차익, 0)}</span>
                                        {#each Object.entries(value.평가차익) as [_key, value]}
                                            {#if _key != 'total' && _key != 'turnover_rate'}
                                                <span class="revenues details-2 text-gradient">{_key}: {formatNumber(value, 0)}</span>
                                            {/if}
                                        {/each}
                                    {/if}
                                    <!-- 평가차익 상세 끝 -->   
                                {/if}
                                <!-- 수익 상세 끝 -->

                                <!-- 비용 상세 시작 -->
                                {#if _key === 'expenses'}
                                <span class="expenses">비용: {formatNumber(value.total, 0)}</span>
                                    {#if value.매매차손?.total > 0}
                                        <span class="revenues details text-gradient">매매차손: {formatNumber(value.매매차손.total, 0)}</span>
                                        {#each Object.entries(value.매매차손) as [_key, value]}
                                            {#if _key != 'total' && _key != 'turnover_rate'}
                                                <span class="revenues details-2 text-gradient">{_key}: {formatNumber(value, 0)}</span>
                                            {/if}
                                        {/each}
                                    {/if}    
                                
                                
                                    {#each Object.entries(value) as [_key, value]}
                                        {#if _key != 'total' && _key != 'turnover_rate' && _key != '매매차손'}
                                            {#if value.total != 0}
                                                <span class="expenses details text-gradient">{_key}: {formatNumber(value.total, 0)}</span>
                                            {/if}
                                        {/if}
                                    {/each}
                                {/if}
                                <!-- 비용 상세 끝 -->
                            {/each}
                        {/each}
                    </div>
                {/each}
            </div>
        {/if}
    </div>
{/if}
    <!-- 재무제표 조회 -->
    {#if toggleBalance}
        <div>
            {#if $investmentStore.periodicReturns.balance}
            <h3>재무제표</h3>
            <div class="financial-statement">
                {#each Object.entries($investmentStore.periodicReturns.balance) as [date, data]}
                    <div class="financial-statement-row">
                        <h4>{date}</h4>
                        {#each Object.entries(data) as [currency, value]}
                            <span>{currency}</span>
                            {#each Object.entries(value) as [_key, value]}
                                <!-- 자산 -->
                                {#if _key === 'assets'}
                                    <span class="revenues details text-gradient">자산: {formatNumber(value.total, 0)}</span>
                                    {#each Object.entries(value) as [account_name, value]}
                                        {#if account_name != 'total' && value != 0}
                                            <span class="revenues details-2 text-gradient">{account_name}: {formatNumber(value, 0)}</span>
                                        {/if}
                                    {/each}
                                <!-- 보유자산 -->
                                {:else if _key === 'holdings'}
                                    <span class="revenues details text-gradient">보유자산상세</span>
                                    {#each Object.entries(value) as [account_name, value]}
                                        {#if account_name != 'total' && value != 0}
                                            <span class="revenues details-2 text-gradient">{account_name}</span>
                                            {#each Object.entries(value) as [account_name, value]}
                                                {#if account_name != 'total' && value != 0}
                                                    <span class="revenues details-3 text-gradient">{account_name}: {formatNumber(value, 0)}</span>
                                                {/if}
                                            {/each}
                                        {/if}
                                    {/each}
                                <!-- 비용 -->
                                {:else if _key === 'expenses'}
                                    <span class="revenues details">비용: {formatNumber(value.total, 0)}</span>
                                    {#each Object.entries(value) as [_key, value]}
                                        {#if _key != 'total'}
                                            {#if value != 0}
                                                <span class="revenues details-2">{_key}: {formatNumber(value, 0)}</span>
                                            {/if}
                                        {/if}
                                    {/each} 
                                <!-- 부채 -->
                                {:else if _key === 'liabilities'}
                                    {#if value.total != 0}
                                        <span class="revenues details">부채: {formatNumber(value.total, 0)}</span>
                                        {#each Object.entries(value) as [_key, value]}
                                            {#if _key != 'total' && value != 0}
                                                <span class="revenues details-2">{_key}: {formatNumber(value, 0)}</span>
                                            {/if}
                                        {/each}
                                    {/if}
                                <!-- 자본 -->
                                {:else if _key === 'equity'}
                                    <span class="revenues details">자본: {formatNumber(value.total, 0)}</span>
                                    {#each Object.entries(value) as [_key, value]}
                                        {#if _key != 'total'}
                                            <span class="revenues details-2">{_key}: {formatNumber(value, 0)}</span>
                                        {/if}
                                    {/each}
                                <!-- 비용 -->
                                {:else if _key === 'expenses'}
                                    <span class="revenues details">비용: {formatNumber(value.total, 0)}</span>
                                    {#each Object.entries(value) as [_key, value]}
                                        {#if _key != 'total' && value != 0}
                                            <span class="revenues details-2">{_key}: {formatNumber(value, 0)}</span>
                                        {/if}
                                    {/each}
                                <!-- 수익    -->
                                {:else if _key === 'revenues'}
                                    <span class="revenues details">수익: {formatNumber(value.total, 0)}</span>
                                    {#each Object.entries(value) as [_key, value]}
                                        {#if _key != 'total' && value != 0}
                                            <span class="revenues details-2">{_key}: {formatNumber(value, 0)}</span>
                                        {/if}
                                    {/each}
                                {/if}
                            {/each}
                        {/each}
                    </div>
                {/each}
            </div>
        {/if}
    </div>
{/if}


<style>
    .button-group {
        display: flex;
        gap: 10px;
        margin-bottom: 1rem;
    }

    .button-simple {
        padding: 8px 16px;
        border: 1px solid #ddd;
        border-radius: 4px;
        background-color: white;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .button-simple:hover {
        background-color: #f5f5f5;
    }

    .button-simple.active {
        background-color: #4CAF50;
        color: white;
        border-color: #45a049;
    }
    .income-statement {
        margin: 0.1rem;
        padding: 0.1rem;
        border: 1px solid #ddd;
        border-radius: 4px;
        /* 가로방향 가운데 정렬 */
        justify-content: center;
        display: flex;
        flex-direction: row;
        flex-wrap: wrap;
        gap: 1rem;
    }

    .income-statement-row {
        display: flex;
        flex-direction: row;
        flex-wrap: wrap;
        /* 세로방향정렬 */
        flex-direction: column;
        font-size: 0.6rem;
    }

    .revenues, .expenses {
        margin-left: 0.5rem;
    }

    .details {
        margin-left: 1rem;
    }
    .details-2 {
        margin-left: 1.5rem;
    }
    .details-3 {
        margin-left: 2rem;
    }
    .details:hover {
        color: #333;
    }

    h3, h4 {
        color: #333;
        margin: 0.1rem;
    }


    .financial-statement {
        margin: 0.1rem;
        padding: 0.1rem;
        border: 1px solid #ddd;
        border-radius: 4px;
        /* 가로방향 가운데 정렬 */
        justify-content: center;
        display: flex;
        flex-direction: row;
        flex-wrap: wrap;
        gap: 0.5rem;
    }

    .financial-statement-row {
        display: flex;
        flex-direction: row;
        flex-wrap: wrap;
        /* 세로방향정렬 */
        flex-direction: column;
        font-size: 0.6rem;
    }
    .text-gradient {
        color: #3f51b5;  /* Google Blue */
        font-weight: 500;
        text-shadow: 1px 1px 1px rgba(0,0,0,0.1);
    }
    /* 다크모드 대응 */
    @media (prefers-color-scheme: dark) {
            .button-simple {
            background-color: #2c2c2c;
            border-color: #404040;
            color: #e0e0e0;
        }

        .button-simple:hover {
            background-color: #3c3c3c;
        }

        .button-simple.active {
            background-color: #2e7d32;
            border-color: #1b5e20;
            color: #ffffff;
        }
    }
</style>