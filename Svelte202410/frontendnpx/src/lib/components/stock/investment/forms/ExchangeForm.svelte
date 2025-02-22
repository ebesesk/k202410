<script>
    import { createEventDispatcher } from 'svelte';
    const dispatch = createEventDispatcher();
    import { investmentStore } from '../js/investmentStores';
    import { formatNumber } from '$lib/util';
    import fastapi from '$lib/api';
    import FeeForm from './FeeForm.svelte';
    
    export let transactionType;


    // interface DispatchEvents {
    //     transactionCreated: void;
    //     resetFees: void;
    // }
    // const dispatch = createEventDispatcher<DispatchEvents>();


    let transaction = {
        date: new Date().toISOString(),
        type: 'EXCHANGE',                              
        currency: 'KRW',                              // 기준 통화
        amount: null,                              // 지급 금액
        quantity: null,                              // 지급 수량
        exchange_rate: null,                       // 환율
        note: '',                      // 메모
        debit_account_id: null,                          // 차변 계정 (예: USD 현금 계정)
        credit_account_id: null,                         // 대변 계정 (예: KRW 현금 계정)
        fees: {},                                     // 수수료 정보                       // 서버에서 설정
        transaction_metadata: {                       // 추가 정보
            to_currency: 'USD',                       // 수취 통화
            to_amount: null,                        // 수취 금액
            exchange_rate: null                    // 환율
        }
    };

    // // FeeForm에서 전달받은 수수료 처리
    // function handleFeeUpdate(event) {
    //     transaction.fees = event.detail;
    // }
    $: accounts = $investmentStore.accounts;

    // 환율에 따른 금액 계산 함수
    function calculateToAmount() {
        if (transaction.amount && transaction.exchange_rate) {
            transaction.transaction_metadata.to_amount = transaction.amount / transaction.exchange_rate;
        }
    }

    function calculateFromAmount() {
        if (transaction.transaction_metadata.to_amount && transaction.exchange_rate) {
            transaction.amount = transaction.transaction_metadata.to_amount * transaction.exchange_rate;
        }
    }

    // FeeForm에서 전달받은 수수료 처리
    function handleFeeUpdate(event) {
        const updatedFees = event.detail;
        // 수수료 정보를 transaction 객체에 업데이트
        transaction.fees = Object.entries(updatedFees).reduce((acc, [type, feeData]) => {
            if (feeData.amount > 0) {  // 금액이 있는 수수료만 포함
                acc[feeData.account_code] = {
                    amount: parseFloat(feeData.amount),
                    account_name: feeData.account_name,
                    currency: transaction.from_currency  // 기본적으로 지급 통화로 설정
                };
            }
            return acc;
        }, {});
        
        // console.log('Updated fees:', transaction.fees);
    }

    // 폼 제출 처리
    async function handleSubmit() {
        try {
            const submitData = {
                ...transaction,
                note: transaction.transaction_metadata.to_currency,
                quantity: parseFloat(transaction.amount) / parseFloat(transaction.exchange_rate),
                debit_account_id: parseInt(transaction.debit_account_id),
                credit_account_id: parseInt(transaction.credit_account_id),
                amount: parseFloat(transaction.amount)
            };

            console.log('Submitting data:', submitData);

            fastapi('post', '/stock/investments/v2/exchange/transactions', submitData,
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
            type: 'EXCHANGE',
            currency: 'KRW',
            amount: null,
            debit_account_id: null,
            credit_account_id: null,
            fees: {},
            note: null,
            username: null,
            exchange_rate: null,
            transaction_metadata: {
                to_currency: 'USD',
                to_amount: null,
                exchange_rate: null
            }
        };
        dispatch('resetFees');
    }

    const currencies = ['KRW', 'USD', 'EUR', 'JPY', 'CNY'];
</script>

<form on:submit|preventDefault={handleSubmit}>
    <div class="form-group">
        <label for="date">거래일자</label>
        <input type="date" id="date" bind:value={transaction.date} required />
    </div>

    <!-- 지급 통화 및 금액 -->
    <div class="form-row">
        <div class="form-group">
            <label for="from_currency">지급 통화</label>
            <select id="from_currency" bind:value={transaction.currency} required>
                <option value="KRW">KRW</option>
                <option value="USD">USD</option>
                <!-- 다른 통화 옵션들 -->
            </select>
        </div>
        <div class="form-group">
            <label for="from_amount">지급 금액</label>
            <input 
                type="number" 
                id="from_amount" 
                bind:value={transaction.amount}
                on:input={calculateToAmount}
                step="any"
                required 
            />
        </div>
    </div>

    <!-- 환율 -->
    <div class="form-group">
        <label for="exchange_rate">환율</label>
        <input 
            type="number" 
            id="exchange_rate" 
            bind:value={transaction.exchange_rate}
            on:input={calculateToAmount}
            step="any"
            required 
        />
    </div>

    <!-- 수취 통화 및 금액 -->
    <div class="form-row">
        <div class="form-group">
            <label for="to_currency">수취 통화</label>
            <select id="to_currency" bind:value={transaction.transaction_metadata.to_currency} required>
                <option value="USD">USD</option>
                <option value="KRW">KRW</option>
                <!-- 다른 통화 옵션들 -->
            </select>
        </div>
        <div class="form-group">
            <label for="to_amount">수취 금액</label>
            <input 
                type="number" 
                id="to_amount" 
                bind:value={transaction.transaction_metadata.to_amount}
                on:input={calculateFromAmount}
                step="any"
                required 
            />
        </div>
    </div>

    <!-- 계정 선택 -->
    <div class="form-row">
        <div class="form-group">
            <label for="debit">차변계정 (받는 계정)</label>
            <select id="debit" bind:value={transaction.debit_account_id} required>
                <option value="">선택하세요</option>
                {#each accounts as account}
                    <option value={account.id}>{account.name}</option>
                {/each}
            </select>
        </div>
        <div class="form-group">
            <label for="credit">대변계정 (주는 계정)</label>
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

    <!-- 버튼 -->
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