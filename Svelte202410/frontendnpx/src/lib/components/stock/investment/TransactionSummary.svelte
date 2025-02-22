<!-- src/lib/components/stock/investment/TransactionSummary.svelte -->
<script>
    // export let transactions = [];
    import { investmentStore } from './js/investmentStores';
    $: transactions = $investmentStore.transactions;
    
    $: totalAmount = transactions?.reduce((sum, t) => sum + t.amount, 0) ?? 0;
    $: totalBuy = transactions?.filter(t => t.type === 'BUY')
        .reduce((sum, t) => sum + t.amount, 0) ?? 0;
    $: totalSell = transactions?.filter(t => t.type === 'SELL')
        .reduce((sum, t) => sum + t.amount, 0) ?? 0;
    console.log('transactions:', transactions);
</script>

<div class="summary-card">
    <h3>거래 요약</h3>
    <div class="summary-grid">
        <div class="summary-item">
            <span class="label">총 거래금액</span>
            <span class="value">{totalAmount.toLocaleString()}원</span>
        </div>
        <div class="summary-item">
            <span class="label">총 매수금액</span>
            <span class="value buy">{totalBuy.toLocaleString()}원</span>
        </div>
        <div class="summary-item">
            <span class="label">총 매도금액</span>
            <span class="value sell">{totalSell.toLocaleString()}원</span>
        </div>
        <div class="summary-item">
            <span class="label">거래건수</span>
            <span class="value">{transactions?.length ?? 0}건</span>
        </div>
    </div>
</div>

<style>
    .summary-card {
        background: #fff;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }

    .summary-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin-top: 15px;
    }

    .summary-item {
        display: flex;
        flex-direction: column;
        gap: 5px;
    }

    .label {
        font-size: 0.9em;
        color: #666;
    }

    .value {
        font-size: 1.2em;
        font-weight: bold;
    }

    .buy {
        color: #d32f2f;
    }

    .sell {
        color: #1976d2;
    }
    @media (max-width: 768px) {
        
        h3 {
            font-size: 1rem;
            margin: 8px 0;
        }

        .summary-grid {
            gap: 10px;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        }

        .summary-item {
            gap: 3px;
        }

        .label {
            font-size: 0.8rem;
        }

        .value {
            font-size: 1rem;
        }

        
    }

</style>