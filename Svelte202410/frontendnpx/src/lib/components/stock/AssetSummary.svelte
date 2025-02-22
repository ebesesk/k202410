<script>
    export let asset_summary;

    // 섹션별 확장/축소 상태 관리
    let expandedSections = {
        foreign: false,
        foreign_cash: false,
        foreign_stock: false,
        local: false,
        local_cash: false,
        local_stock: false
    };

    // 금액 포맷팅 함수
    const formatAmount = (amount, currency = 'KRW') => {
        return `${new Intl.NumberFormat('ko-KR').format(amount)} ${currency}`;
    };


    // 숫자 색상 클래스 결정 함수
    const getNumberClass = (value) => {
        if (value === 0) return '';
        return value < 0 ? 'negative' : 'positive';
    };


    // 통화별 상세 정보 표시 상태 관리
    let expandedCurrencies = {};
    
    function toggleCurrencyDetails(currency) {
        expandedCurrencies[currency] = !expandedCurrencies[currency];
        expandedCurrencies = expandedCurrencies;
    }

    // 섹션별 상세 정보 표시 상태 관리
    // let expandedSections = {};
    
    function toggleSectionDetails(section) {
        expandedSections[section] = !expandedSections[section];
        expandedSections = expandedSections; // 반응성 트리거
    }
</script>

<div>
    <!-- Local Account -->
    <div class="local-summary">
        <div class="balance-item">
            <span class="balance-label">{asset_summary.local.account.name}</span>
        </div>

        <!-- Basic Currency Balance (KRW) -->
        <div class="currency-group">
            <div class="balance-item clickable" on:click={() => toggleSectionDetails('local_krw')}>
                <span class="balance-label">
                    <span class="toggle-icon">{expandedSections['local_krw'] ? '▼' : '▶'}</span>
                    KRW
                </span>
                <span class="balance-value {getNumberClass(asset_summary.local.krw.balance)}">
                    {formatAmount(asset_summary.local.krw.balance, 'KRW')}
                </span>
            </div>
            {#if expandedSections['local_krw']}
                <div class="details-container">
                    <div class="balance-item detail">
                        <span class="balance-label">Fee</span>
                        <span class="balance-value {getNumberClass(asset_summary.local.krw.fee)}">
                            {formatAmount(asset_summary.local.krw.fee, 'KRW')}
                        </span>
                    </div>
                    <div class="balance-item detail">
                        <span class="balance-label">Tax</span>
                        <span class="balance-value {getNumberClass(asset_summary.local.krw.tax)}">
                            {formatAmount(asset_summary.local.krw.tax, 'KRW')}
                        </span>
                    </div>
                </div>
            {/if}
        </div>

        <!-- Account Section -->
        <div class="section-group">
            <div class="balance-item clickable" on:click={() => toggleSectionDetails('local_account')}>
                <span class="balance-label">
                    <span class="toggle-icon">{expandedSections['local_account'] ? '▼' : '▶'}</span>
                    Account
                </span>
            </div>
            {#if expandedSections['local_account']}
                <div class="details-container">
                    {#each Object.entries(asset_summary.local.account) as [key, value]}
                        {#if typeof value === 'object' && value !== null && key !== 'name'}
                            <div class="balance-item detail">
                                <span class="balance-label">{key}</span>
                                <span class="balance-value {getNumberClass(value.balance)}">
                                    {formatAmount(value.balance, 'KRW')}
                                </span>
                            </div>
                        {/if}
                    {/each}
                </div>
            {/if}
        </div>

        <!-- Stock Section -->
        <div class="section-group">
            <div class="balance-item clickable" on:click={() => toggleSectionDetails('local_stock')}>
                <span class="balance-label">
                    <span class="toggle-icon">{expandedSections['local_stock'] ? '▼' : '▶'}</span>
                    Stock
                </span>
            </div>
            {#if expandedSections['local_stock'] && asset_summary.local.stock.item}
                <div class="details-container">
                    {#each Object.entries(asset_summary.local.stock.item) as [stockName, stockData]}
                        <div class="section-group">
                            <div class="balance-item clickable" on:click={() => toggleSectionDetails(`local_stock_${stockName}`)}>
                                <span class="balance-label">
                                    <span class="toggle-icon">{expandedSections[`local_stock_${stockName}`] ? '▼' : '▶'}</span>
                                    {stockName} ({stockData.krw.code})
                                </span>
                                <span class="balance-value {getNumberClass(stockData.krw.balance)}">
                                    {formatAmount(stockData.krw.balance, 'KRW')}
                                </span>
                            </div>
                            {#if expandedSections[`local_stock_${stockName}`]}
                                <div class="details-container">
                                    <div class="balance-item detail">
                                        <span class="balance-label">수량</span>
                                        <span class="balance-value">
                                            {stockData.krw.quantity} 주
                                        </span>
                                    </div>
                                    <div class="balance-item detail">
                                        <span class="balance-label">수수료</span>
                                        <span class="balance-value {getNumberClass(stockData.krw.fee)}">
                                            {formatAmount(stockData.krw.fee, 'KRW')}
                                        </span>
                                    </div>
                                    <div class="balance-item detail">
                                        <span class="balance-label">세금</span>
                                        <span class="balance-value {getNumberClass(stockData.krw.tax)}">
                                            {formatAmount(stockData.krw.tax, 'KRW')}
                                        </span>
                                    </div>
                                </div>
                            {/if}
                        </div>
                    {/each}
                </div>
            {/if}
        </div>
    </div>

    <!-- 외화 요약 -->
    <!-- Foreign Account -->
    <div class="foreign-summary">
        <div class="balance-item">
            <span class="balance-label">{asset_summary.foreign.account.name}</span>
        </div>

        <!-- Basic Currency Balances -->
        {#each ['krw', 'usd'] as currency}
            {#if asset_summary.foreign[currency]}
                <div class="currency-group">
                    <div class="balance-item clickable" on:click={() => toggleSectionDetails(`foreign_${currency}`)}>
                        <span class="balance-label">
                            <span class="toggle-icon">{expandedSections[`foreign_${currency}`] ? '▼' : '▶'}</span>
                            {currency.toUpperCase()}
                        </span>
                        <span class="balance-value {getNumberClass(asset_summary.foreign[currency].balance)}">
                            {formatAmount(asset_summary.foreign[currency].balance, currency.toUpperCase())}
                        </span>
                    </div>
                    {#if expandedSections[`foreign_${currency}`]}
                        <div class="details-container">
                            <div class="balance-item detail">
                                <span class="balance-label">Fee</span>
                                <span class="balance-value {getNumberClass(asset_summary.foreign[currency].fee)}">
                                    {formatAmount(asset_summary.foreign[currency].fee, currency.toUpperCase())}
                                </span>
                            </div>
                            <div class="balance-item detail">
                                <span class="balance-label">Tax</span>
                                <span class="balance-value {getNumberClass(asset_summary.foreign[currency].tax)}">
                                    {formatAmount(asset_summary.foreign[currency].tax, currency.toUpperCase())}
                                </span>
                            </div>
                        </div>
                    {/if}
                </div>
            {/if}
        {/each}

        <!-- Account Section -->
        <div class="section-group">
            <div class="balance-item clickable" on:click={() => toggleSectionDetails('foreign_account')}>
                <span class="balance-label">
                    <span class="toggle-icon">{expandedSections['foreign_account'] ? '▼' : '▶'}</span>
                    Account
                </span>
            </div>
            {#if expandedSections['foreign_account']}
                <div class="details-container">
                    {#each Object.entries(asset_summary.foreign.account) as [key, value]}
                        {#if typeof value === 'object'}
                            {#each Object.entries(value) as [currency, data]}
                                <div class="balance-item detail">
                                    <span class="balance-label">{key} ({currency.toUpperCase()})</span>
                                    <span class="balance-value {getNumberClass(data.balance)}">
                                        {formatAmount(data.balance, currency.toUpperCase())}
                                    </span>
                                </div>
                            {/each}
                        {/if}
                    {/each}
                </div>
            {/if}
        </div>

        <!-- Stock Section -->
        <div class="section-group">
            <div class="balance-item clickable" on:click={() => toggleSectionDetails('foreign_stock')}>
                <span class="balance-label">
                    <span class="toggle-icon">{expandedSections['foreign_stock'] ? '▼' : '▶'}</span>
                    Stock
                </span>
            </div>
            {#if expandedSections['foreign_stock']}
                <div class="details-container">
                    <!-- Dividend -->
                    {#if asset_summary.foreign.stock.dividend}
                        <div class="section-group">
                            <div class="balance-item clickable" on:click={() => toggleSectionDetails('foreign_stock_dividend')}>
                                <span class="balance-label">
                                    <span class="toggle-icon">{expandedSections['foreign_stock_dividend'] ? '▼' : '▶'}</span>
                                    Dividend
                                </span>
                            </div>
                            {#if expandedSections['foreign_stock_dividend']}
                                {#each Object.entries(asset_summary.foreign.stock.dividend) as [currency, data]}
                                    <div class="details-container">
                                        <div class="balance-item detail">
                                            <span class="balance-label">{currency.toUpperCase()}</span>
                                            <span class="balance-value {getNumberClass(data.balance)}">
                                                {formatAmount(data.balance, currency.toUpperCase())}
                                            </span>
                                        </div>
                                        <div class="balance-item detail">
                                            <span class="balance-label">Fee</span>
                                            <span class="balance-value {getNumberClass(data.fee)}">
                                                {formatAmount(data.fee, currency.toUpperCase())}
                                            </span>
                                        </div>
                                        <div class="balance-item detail">
                                            <span class="balance-label">Tax</span>
                                            <span class="balance-value {getNumberClass(data.tax)}">
                                                {formatAmount(data.tax, currency.toUpperCase())}
                                            </span>
                                        </div>
                                    </div>
                                {/each}
                            {/if}
                        </div>
                    {/if}

                    <!-- Stock Items -->
                    {#each Object.entries(asset_summary.foreign.stock.item) as [stockName, stockData]}
                        <div class="section-group">
                            <div class="balance-item clickable" on:click={() => toggleSectionDetails(`foreign_stock_${stockName}`)}>
                                <span class="balance-label">
                                    <span class="toggle-icon">{expandedSections[`foreign_stock_${stockName}`] ? '▼' : '▶'}</span>
                                    {stockName} ({stockData.usd.code})
                                </span>
                                <span class="balance-value {getNumberClass(stockData.usd.balance)}">
                                    {formatAmount(stockData.usd.balance, 'USD')}
                                </span>
                            </div>
                            {#if expandedSections[`foreign_stock_${stockName}`]}
                                <div class="details-container">
                                    <div class="balance-item detail">
                                        <span class="balance-label">수량</span>
                                        <span class="balance-value">
                                            {stockData.usd.quantity} 주
                                        </span>
                                    </div>
                                    <div class="balance-item detail">
                                        <span class="balance-label">수수료</span>
                                        <span class="balance-value {getNumberClass(stockData.usd.fee)}">
                                            {formatAmount(stockData.usd.fee, 'USD')}
                                        </span>
                                    </div>
                                    <div class="balance-item detail">
                                        <span class="balance-label">세금</span>
                                        <span class="balance-value {getNumberClass(stockData.usd.tax)}">
                                            {formatAmount(stockData.usd.tax, 'USD')}
                                        </span>
                                    </div>
                                </div>
                            {/if}
                        </div>
                    {/each}
                </div>
            {/if}
        </div>
    </div>
</div>

<style>
    .foreign-summary, .local-summary {
        margin: 0.2rem;
        padding: 0.2rem;
        background-color: #f9f9f9;
        border-radius: 4px;
        font-size: 0.85rem;
    }

    .currency-group, .section-group {
        margin: 0.1rem 0;
        border-radius: 4px;
        overflow: hidden;
    }

    .balance-item {
        display: flex;
        justify-content: space-between;
        padding: 0.1rem 0.3rem;
        align-items: center;
        min-height: 1.4rem;
    }

    .clickable {
        cursor: pointer;
        transition: background-color 0.2s;
    }

    .clickable:hover {
        background-color: #f0f0f0;
    }

    .details-container {
        margin-left: 0.8rem;
        font-size: 0.8rem;
        background-color: #f5f5f5;
        border-radius: 4px;
    }

    .detail {
        padding: 0.1rem 0.3rem;
        color: #666;
        min-height: 1.2rem;
    }

    .balance-label {
        display: flex;
        align-items: center;
        gap: 0.2rem;
    }

    .toggle-icon {
        font-size: 0.6rem;
        width: 0.6rem;
        line-height: 1;
    }

    .negative {
        color: #D92121;
    }

    .positive {
        color: #0047A0;
        font-weight: 500;
    }

    .balance-value {
        font-family: 'Courier New', monospace;
        letter-spacing: -0.5px;
    }

    /* 중첩된 details-container의 크기 조정 */
    .details-container .details-container {
        margin-left: 0.6rem;
        font-size: 0.95em;
    }
</style>