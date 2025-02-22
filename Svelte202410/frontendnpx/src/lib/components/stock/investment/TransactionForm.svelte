<script>
    import TradeForm from './forms/TradeForm.svelte';
    import ExchangeForm from './forms/ExchangeForm.svelte';
    import CashForm from './forms/CashForm.svelte';
    import IncomeForm from './forms/IncomeForm.svelte';
    import ExpenseForm from './forms/ExpenseForm.svelte';
    import TransactionsList from './forms/TransactionsList.svelte';

    let selectedType = 'TRADE';
    $: selectedType;
    
    const transactionTypes = [
        { value: 'TRADE', label: '증권거래' },
        { value: 'EXCHANGE', label: '환전' },
        { value: 'CASH', label: '입출금' },
        { value: 'INCOME', label: '수익' },
        { value: 'EXPENSE', label: '비용' },
        { value: 'TRANSACTIONS', label: '거래내역' }
    ];
</script>

<div class="transaction-form">
    <h3>거래 입력</h3>
    <div class="form-group">
        <label for="type">거래 유형</label>
        <select id="type" bind:value={selectedType}>
            {#each transactionTypes as type}
                <option value={type.value}>{type.label}</option>
            {/each}
        </select>
    </div>

    {#if selectedType === 'TRADE'}
        <TradeForm transactionType={selectedType} />
    {:else if selectedType === 'EXCHANGE'}
        <ExchangeForm transactionType={selectedType} />
    {:else if selectedType === 'CASH'}
        <CashForm transactionType={selectedType} />
    {:else if selectedType === 'INCOME'}
        <IncomeForm transactionType={selectedType} />
    {:else if selectedType === 'EXPENSE'}
        <ExpenseForm transactionType={selectedType} />
    {:else if selectedType === 'TRANSACTIONS'}
        <TransactionsList />
    {/if}
</div>
 
<style>
    .transaction-form {
        padding: 20px;
        background: #fff;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        font-size: 0.7rem;
    }

    .form-group {
        margin-bottom: 15px;
    }

    label {
        display: block;
        margin-bottom: 5px;
        font-weight: bold;
    }

    select {
        width: 100%;
        padding: 8px;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 0.7rem;
    }
</style>