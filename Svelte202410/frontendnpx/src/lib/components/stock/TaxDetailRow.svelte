<script>
    export let gain;
    export let isOpen = false;

    function formatNumber(num) {
        return new Intl.NumberFormat('ko-KR').format(num);
    }

    function formatDate(dateStr) {
        return new Date(dateStr).toLocaleDateString('ko-KR');
    }
</script>

<tr class="main-row" on:click={() => isOpen = !isOpen}>
    <td>{formatDate(gain.sell_date)}</td>
    <td>{formatNumber(gain.quantity)}</td>
    <td class="text-right">{formatNumber(gain.buy_price)}</td>
    <td class="text-right">{formatNumber(gain.sell_price)}</td>
    <td class="text-right">{formatNumber(gain.sell_price * gain.quantity)}</td>
</tr>

{#if isOpen}
<tr class="detail-row">
    <td colspan="4">
        <div class="tax-detail">
            <div class="tax-row">
                <div class="tax-label">매도일:</div>
                <div class="tax-value">{formatDate(gain.sell_date)}</div>
            </div>
            <div class="tax-row">
                <div class="tax-label">매수일:</div>
                <div class="tax-value">{formatDate(gain.buy_date)}</div>
            </div>
            <div class="tax-row">
                <div class="tax-label">수량:</div>
                <div class="tax-value">{formatNumber(gain.quantity)}주</div>
            </div>
            <div class="tax-row">
                <div class="tax-label">매수가:</div>
                <div class="tax-value">{formatNumber(gain.buy_price)}원</div>
            </div>
            <div class="tax-row">
                <div class="tax-label">매도가:</div>
                <div class="tax-value">{formatNumber(gain.sell_price)}원</div>
            </div>
            <div class="tax-row">
                <div class="tax-label">매수수수료:</div>
                <div class="tax-value">{formatNumber(gain.buy_fee)}원</div>
            </div>
            <div class="tax-row">
                <div class="tax-label">매도수수료:</div>
                <div class="tax-value">{formatNumber(gain.sell_fee)}원</div>
            </div>
            <div class="tax-row">
                <div class="tax-label">양도소득세:</div>
                <div class="tax-value">{formatNumber(gain.sell_tax)}원</div>
            </div>
            <div class="tax-row">
                <div class="tax-label">보유기간:</div>
                <div class="tax-value">{gain.holding_days}일</div>
            </div>
            <div class="tax-row">
                <div class="tax-label">순손익:</div>
                <div class="tax-value" class:profit={gain.sell_price > gain.buy_price} class:loss={gain.sell_price < gain.buy_price}>
                    {formatNumber((gain.sell_price - gain.buy_price) * gain.quantity - gain.total_fee)}원
                </div>
            </div>
        </div>
    </td>
</tr>
{/if}

<style>
    .main-row {
        cursor: pointer;
    }
    .main-row:hover {
        background-color: #f5f5f5;
        padding: 0.2rem;
    }
    .detail-row {
        background-color: #f8f9fa;
    }
    .tax-detail {
        padding: 0.2rem;  /* 1rem -> 0.5rem */
        border: 1px solid #eee;
        border-radius: 4px;
        margin-bottom: 0.2rem;  /* 1rem -> 0.5rem */
        background: white;
        font-size: 0.7rem;  /* 글자 크기 축소 */
    }
    .tax-row {
        display: flex;
        padding: 0.2rem 0;  /* 0.5rem -> 0.2rem */
        border-bottom: 1px solid #f0f0f0;
        line-height: 1.2;  /* 줄 간격 축소 */
    }
    .tax-row:last-child {
        border-bottom: none;
    }
    .tax-label {
        width: 80px;  /* 100px -> 80px */
        color: #666;
        font-weight: 500;
    }
    .tax-value {
        flex: 1;
        font-weight: 600;
    }
    .profit { color: #28a745; }
    .loss { color: #dc3545; }
    .text-right {
        text-align: right;
    }
</style>