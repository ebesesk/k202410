<script>
    import { key, accno_list } from "$lib/stores/stock";
    // export let accno_list;
    export let asset_summary = {};
    export let trade_tag;
    export let table_items = {};
    export let accnoCodes;


    const formatNumber = (value) => {
        if (!value) return '0';
        return new Intl.NumberFormat('ko-KR').format(value);
    };

    const getNumberClass = (value) => {
        if (!value || value === 0) return '';
        return value < 0 ? 'negative' : 'positive';
    };
    const getReversedNumberClass = (value) => {
        if (!value || value === 0) return '';
        return value > 0 ? 'negative' : 'positive';  // 반대로 설정
    };

    $: asset_summary = trade_tag?.asset_summary;
    $: table_items = trade_tag?.account_table_items;
    // $: $account_table_items;
    // $: put_fdr_price_to_trade_tag();

</script>



{#if $accno_list.length > 0}
    <div class="accno-tables-container">
        <div class="table-scroll summary-table-container">
            <table class="accno-summary-table">
                <thead>
                    <tr>
                        <th class="accno text-right">추정순자산</th>
                        <th class="accno text-right">평가손익</th>
                        <th class="accno text-right">매입금액</th>
                        <th class="accno text-right">추정D2예수금</th>
                        <th class="accno text-right">평가금액</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        {#each $accno_list[1] as value, i}
                            {#if $accno_list[0][i] !== 'CTS_종목번호'}
                                <td class="accno text-right">{formatNumber(value)}</td>
                            {/if}
                        {/each}
                    </tr>
                </tbody>
            </table>
        </div>

        <div class="table-scroll accno-table-scroll">
            <table class="stock-table accno-table">
                <thead>
                    <tr>
                        <th class="accno stock-name text-right">종목명</th>
                        <th class="accno text-right s-width">잔고</th>
                        <th class="accno text-right">현재가</th>
                        <th class="accno text-right">평가금액</th>
                        <th class="accno text-right">평가손익</th>
                        <th class="accno text-right s-width">수익율</th>
                        <th class="accno text-right s-width">평균단가</th>
                        <th class="accno text-right s-width">매입금액</th>
                        <th class="accno text-right s-width">수수료</th>
                        <th class="accno text-right s-width">제세금</th>
                    </tr>
                </thead>
                <tbody>
                    {#each $accno_list.slice(3) as row}
                        <tr>
                            <td class="accno text-right text-2196f3">{row[18]}</td>
                            <td class="accno text-right s-width">{formatNumber(row[2])}</td>
                            <td class="accno text-right">{formatNumber(row[22])}</td>
                            <td class="accno text-right">{formatNumber(row[23])}</td>
                            <td class="accno text-right" class:positive={row[24] < 0} class:negative={row[24] > 0}>
                                {formatNumber(row[24])}
                            </td>
                            <td class="accno text-right" class:positive={parseFloat(row[25]) < 0} class:negative={parseFloat(row[25]) > 0}>
                                {row[25]}%
                            </td>
                            <td class="accno text-right">{formatNumber(row[4])}</td>
                            <td class="accno text-right">{formatNumber(row[5])}</td>
                            <td class="accno text-right">{formatNumber(row[26])}</td>
                            <td class="accno text-right">{formatNumber(row[27])}</td>
                        </tr>
                    {/each}
                        {#if table_items}  
                            {#each Object.entries(table_items) as [currency, data]}
                                <!-- <tr>
                                    <td colspan="1" class="accno text-right text-2196f3">{currency}</td>
                                    <td colspan="9"></td>
                                </tr> -->
                                {#each data as item}
                                    {#if !accnoCodes.includes(item.code) && item.quantity != 0}
                                        <tr>
                                            <!-- 종목명 -->
                                            <td class="accno text-right text-2196f3">{item.code}</td>
                                            <!-- 잔고 -->
                                            <td class="accno text-right">{formatNumber(item.quantity)}</td>
                                            <!-- 현재가 -->
                                            <td class="accno text-right">{formatNumber(item.price)}</td>
                                            <!-- 평가금액 -->
                                            <td class="accno text-right">{formatNumber(item.amount)}</td>
                                            <!-- 평가손익 -->
                                            <td class="accno text-right" class:positive={item.valuation_gain < 0} class:negative={item.valuation_gain > 0}>
                                                {formatNumber(item.valuation_gain)}
                                            </td>
                                            <!-- 수익율 -->
                                            <td class="accno text-right" class:positive={item.return_rate < 0} class:negative={item.return_rate > 0}>
                                                {formatNumber(item.return_rate)}%
                                            </td>
                                            <!-- 평균단가 -->
                                            <td class="accno text-right">{formatNumber(item.purchases_price)}</td>
                                            <!-- 매입금액 -->
                                            <td class="accno text-right">{formatNumber(item.purchases_amount)}</td>
                                            <!-- 수수료 -->
                                            <td class="accno text-right">{formatNumber(item.fee)}</td>
                                            <!-- 제세금 -->
                                            <td class="accno text-right">{formatNumber(item.tax)}</td>
                                        </tr>
                                    {/if}
                                {/each}
                            {/each}
                        {/if}
                </tbody>
            </table>
        </div>
    </div>
{/if}







<style>
    

    table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.85rem;
    }

    th, td {
        padding: 0.3rem 0.5rem;
        border: 1px solid #ddd;
    }

    th {
        background-color: #f5f5f5;
        font-weight: normal;
    }

    .text-right {
        text-align: right;
    }

    .positive {
        color: #0047A0;
    }

    .negative {
        color: #D92121;
    }

    .accno-tables-container {
        display: flex;
        flex-direction: column;
        gap: 0;
        width: 100%;
        min-width: 0; /* 필수: 스크롤 작동을 위해 */
    }

    .table-scroll {
        overflow-x: auto;
        width: 100%;
        margin: 0;
        padding: 0;
        -webkit-overflow-scrolling: touch; /* iOS 스크롤 부드럽게 */
    }

    .accno-table {
        width: 100%;
        min-width: 700px; /* 테이블의 최소 너비 설정 */
        table-layout: fixed;
        border-collapse: collapse;
    }
    .accno-table th:nth-child(1),
    .accno-table td:nth-child(1) {
        position: sticky;
        left: 0;
        background-color: white;
        z-index: 1;
        border-right: 1px solid #eee;
        min-width: 50px;
        width: 50px;  /* 고정 너비 설정 */
    }
    .accno-table tr:hover td:nth-child(1) {
        background-color: #f5f5f5;
        /* width: 95%; 제거 */
    }
    /* 첫 번째 열(종목명) 스타일 수정 */
    .accno-table th:nth-child(1),
    .accno-table td:nth-child(1) {
        position: sticky;
        left: 0;
        background-color: white;
        z-index: 1;
        border-right: 1px solid #eee;
        /* min-width: 60px; */
        width: 30px;
        /* width: 80px; 제거 - 고정 너비 제한 해제 */
    }
    .accno-table th,
    .accno-table td {
        width: auto;
        /* min-width: 15px;  최소 너비 설정 */
        padding: 0 4px;
        /* white-space: nowrap; */
        /* overflow: hidden;
        text-overflow: ellipsis; */
    }
    .accno-tables-container {
        display: flex;
        flex-direction: column;
        gap: 0;  /* 테이블 간 간격 제거 */
    }
    .summary-table-container {
        margin-bottom: 0;  /* 하단 마진 제거 */
    }
    .accno-summary-table {
        margin: 0;
        width: 100%;
        border-bottom: 1px solid #eee;  /* 구분선 추가 */
    }

    .accno-summary-table {
        width: 100%;
        min-width: 300px;
        margin: 0;
        border-bottom: 1px solid #eee;
    }

    .stock-table.accno-table {
    margin: 0;
    border-top: none;  /* 상단 테두리 제거 */
}

    /* 호버 효과 시 배경색 */
    .accno-table tr:hover td:nth-child(1) {
        background-color: #f5f5f5;
        width: 95%;
    }

    /* 각 열의 너비 설정 */
    /* .accno-table th,
    .accno-table td {
        padding: 6px 8px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    } */
    /* 계좌 테이블 스크롤 컨테이너 */
    .accno-table-scroll {
        width: 100%;
        max-width: 100%;
        overflow-x: auto;
        margin: 0;
        padding: 0;
        background: white;
        border-radius: 4px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        -webkit-overflow-scrolling: touch;  /* iOS 스크롤 부드럽게 */
    }
    .accno.stock-name {
        font-size: 9px;
        padding: 0 4px;
        width: 20px;
    }
    th.accno {
        font-size: 9px;
        padding: 0 4px;
        margin: 15px 10px;
        width: 20px;
    }
    td.accno {
        font-size: 10px;
        margin: 15px 10px;
        padding: 0 4px;
        gap: 1px;
    }

    .s-width {
        width: 10px;
    }
    .table-scroll::-webkit-scrollbar {
        height: 8px;
    }

    .table-scroll::-webkit-scrollbar-track {
        background: #f1f1f1;
    }

    .table-scroll::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 4px;
    }

    .table-scroll::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
    /* ... 나머지 스타일 ... */
</style>