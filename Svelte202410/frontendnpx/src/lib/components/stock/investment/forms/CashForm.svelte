<script>
    import { createEventDispatcher } from 'svelte';
    const dispatch = createEventDispatcher();
    import { investmentStore } from '../js/investmentStores';
    import { formatNumber } from '$lib/util';
    import fastapi from '$lib/api';
    import FeeForm from './FeeForm.svelte';

    
    // 부모로부터 전달받는 transactionType
    export let transactionType;
    $: transactionType;

    let transaction = {
        date: new Date().toISOString(),
        type: 'DEPOSIT',  // DEPOSIT or WITHDRAWAL
        currency: 'KRW',
        amount: 0,
        debit_account_id: '',
        credit_account_id: '',
        note: '',
        fees: {}
    };

    $: accounts = $investmentStore.accounts;

    const currencies = ['KRW', 'USD', 'EUR', 'JPY', 'CNY'];

    async function handleSubmit() {
        try {
            const submitData = {
                ...transaction,
                debit_account_id: parseInt(transaction.debit_account_id),
                credit_account_id: parseInt(transaction.credit_account_id),
                amount: parseFloat(transaction.amount)
            };

            const url = '/stock/investments/v2/cash';
            console.log('submitData', submitData);

            fastapi('post', url, submitData,
                (json) => {
                    console.log('Success:', json);
                    resetForm();
                    dispatch('transactionCreated');
                },
                (error) => {
                    console.error('Error:', error);
                    alert(error.detail?.[0]?.msg || '오류가 발생했습니다.');
                }
            );
        } catch (error) {
            console.error('Submit error:', error);
        }
    }

    function resetForm() {
        transaction = {
            date: new Date().toISOString().split('T')[0],
            type: 'DEPOSIT',
            currency: 'KRW',
            amount: 0,
            debit_account_id: '',
            credit_account_id: '',
            note: '',
            fees: {}
        };
        dispatch('resetFees');
    }
</script>

<form on:submit|preventDefault={handleSubmit}>
    <div class="form-group">
        <label for="date">거래일자</label>
        <input type="date" id="date" bind:value={transaction.date} required />
    </div>

    <div class="form-group">
        <label for="type">거래유형</label>
        <select id="type" bind:value={transaction.type} required>
            <option value="DEPOSIT">입금</option>
            <option value="WITHDRAWAL">출금</option>
        </select>
    </div>

    <div class="form-row">
        <div class="form-group">
            <label for="currency">통화</label>
            <select id="currency" bind:value={transaction.currency} required>
                {#each currencies as currency}
                    <option value={currency}>{currency}</option>
                {/each}
            </select>
        </div>

        <div class="form-group">
            <label for="amount">금액</label>
            <input 
                type="number" 
                id="amount" 
                bind:value={transaction.amount}
                step="any"
                required
            />
            {formatNumber(transaction.amount)}
        </div>
    </div>

    <div class="form-row">
        <div class="form-group">
            <label for="debit">차변계정</label>
            <select id="debit" bind:value={transaction.debit_account_id} required>
                <option value="">선택하세요</option>
                {#each accounts as account}
                    <option value={account.id}>{account.name}</option>
                {/each}
            </select>
        </div>

        <div class="form-group">
            <label for="credit">대변계정</label>
            <select id="credit" bind:value={transaction.credit_account_id} required>
                <option value="">선택하세요</option>
                {#each accounts as account}
                    <option value={account.id}>{account.name}</option>
                {/each}
            </select>
        </div>
    </div>

    <FeeForm 
        {transaction}
        bind:fees={transaction.fees} 
        {transactionType}
        on:resetFees={() => transaction.fees = {}}
    />
    
    <div class="form-group">
        <label for="note">메모</label>
        <textarea 
            id="note" 
            bind:value={transaction.note}
            rows="3"
        ></textarea>
    </div>

    <div class="form-actions">
        <button type="submit" class="btn-primary">저장</button>
        <button type="button" class="btn-secondary" on:click={resetForm}>초기화</button>
    </div>
</form>

<style>
    .form-row {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 15px;
    }

    .form-group {
        margin-bottom: 15px;
    }

    label {
        display: block;
        margin-bottom: 5px;
        font-weight: bold;
        font-size: 0.7rem;
    }

    input, select, textarea {
        width: 100%;
        padding: 8px;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 0.7rem;
    }

    .form-actions {
        display: flex;
        gap: 10px;
        margin-top: 20px;
    }

    button {
        padding: 8px 16px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 0.7rem;
    }

    .btn-primary {
        background: #4CAF50;
        color: white;
    }

    .btn-secondary {
        background: #f0f0f0;
        color: #333;
    }
</style>