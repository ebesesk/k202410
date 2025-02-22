<script>
    import { createEventDispatcher } from 'svelte';
    import { onMount } from 'svelte';
    import { investmentStore, loadPositions, loadAssets, loadAccounts } from '../js/investmentStores';
    import { formatNumber } from '$lib/util';
    import fastapi from '$lib/api';
    import FeeForm from './FeeForm.svelte';
    const dispatch = createEventDispatcher();

    onMount(() => {
        loadPositions();
        loadAssets();
        loadAccounts();
        console.log('investmentStore', $investmentStore);
    });
    let asset = [];
    let assets = [];
    let accounts = [];
    let positions = [];
    
    export let totalFee = 0;
    export let transactionType; // 부모로부터 전달받는 transactionType  
    const currencies = ['KRW', 'USD', 'EUR', 'JPY', 'CNY'];
    
    let transaction = {
        date: new Date().toISOString().split('T')[0],
        type: 'STOCK_BUY',  // STOCK_BUY, STOCK_SELL, CRYPTO_BUY, CRYPTO_SELL
        currency: 'KRW',
        amount: 0,
        note: '',
        username: null,  // API에서 처리될 것임
        debit_account_id: '',
        credit_account_id: '',
        fees: {},
        // SecurityTransactionCreate 추가 필드
        asset_id: '',
        quantity: 0,
        price: 0,
        exchange_rate: null,  // Optional
        transaction_metadata: null  // Optional
    };

    // 수량과 가격이 변경될 때 총액 계산
    console.log('$investmentStore', $investmentStore);
    $: {
        
        assets = $investmentStore.assets;           // 자산 데이터 가져오기
        accounts = $investmentStore.accounts;       // 계정 데이터 가져오기
        positions = $investmentStore.positions;     // 자산 데이터 가져오기
        
        totalFee
        
        // loadPositions(transaction.asset_id);
        if (transaction.quantity && transaction.price) {
            transaction.amount = transaction.quantity * transaction.price;
            calculateEstimatedFIFOPL();
        }
    }

    // export let fees = {};
    
    // console.log('transactionType', transactionType);


    

    function calculateAmount() {
        if (transaction.quantity > selectedPosition.quantity) {
            transaction.quantity = selectedPosition.quantity;
        }
        transaction.amount = transaction.quantity * transaction.price;
    }

    async function handleSubmit() {
        try {
            const submitData = {
                ...transaction,
                asset_id: parseInt(transaction.asset_id),
                debit_account_id: parseInt(transaction.debit_account_id),
                credit_account_id: parseInt(transaction.credit_account_id),
                quantity: parseFloat(transaction.quantity),
                price: parseFloat(transaction.price),
                amount: parseFloat(transaction.amount),
                exchange_rate: parseFloat(transaction.exchange_rate),
                fees: transaction.fees,
            };
            console.log('submitData', submitData);
            const url = '/stock/investments/v2/security';
            
            fastapi('post', url, submitData,
                (json) => {
                    console.log('Success:', json);
                    resetFees = true;
                    console.log('resetFees', resetFees);
                    resetForm();
                    dispatch('transactionCreated');
                },
                (error) => {
                    console.error('Error:', error);
                    alert(error.detail || '오류가 발생했습니다.');
                }
            );
        } catch (error) {
            console.error('Submit error:', error);
        }
    }
    export let resetFees = false;
    function resetForm() {
        resetFees = true;
        let transaction = {
            date: new Date().toISOString(),
            type: 'STOCK_BUY',  // STOCK_BUY, STOCK_SELL, CRYPTO_BUY, CRYPTO_SELL
            currency: 'KRW',
            amount: 0,
            note: '',
            username: null,  // API에서 처리될 것임
            debit_account_id: '',
            credit_account_id: '',
            fees: {},
            // SecurityTransactionCreate 추가 필드
            asset_id: '',
            quantity: 0,
            price: 0,
            exchange_rate: null,  // Optional
            transaction_metadata: null  // Optional
        };
        dispatch('resetFees');
    }
    // 자산 선택 시 통화 설정
    let selectedAsset = {};
    let selectedPosition = {};
    function handleAssetChange(assetId) {
        selectedAsset = $investmentStore.assets.find(
            asset => asset.id === parseInt(assetId)
        );
        selectedPosition = $investmentStore.positions.find(
            position => position.asset_id === parseInt(assetId)
        );
        console.log('selectedPosition', selectedPosition);
        if (selectedAsset) {
            transaction.currency = selectedAsset.currency || 'KRW';
            // 자산 유형에 따라 거래 유형 설정
            // transaction.type = selectedAsset.type === 'CRYPTO' 
            //     ? 'CRYPTO_BUY' 
            //     : 'STOCK_BUY';
        }
    }
    // let assetType = '';
    

    function calculateTotal() {
        // 주식 거래 금액 계산
        let tradeAmount = transaction.quantity * transaction.price;

        // 수수료 합계 계산
        let feesTotal = 0;
        if (transaction.fees) {
            // 고정 수수료
            Object.values(transaction.fees).forEach(fee => {
                if (fee.currency === transaction.currency) {
                    feesTotal += parseFloat(fee.amount) || 0;
                }
                // 다른 통화의 수수료는 환율 적용 필요
            });

            // 기타 수수료
            if (transaction.fees.otherFees) {
                transaction.fees.otherFees.forEach(fee => {
                    if (fee.currency === transaction.currency) {
                        feesTotal += parseFloat(fee.amount) || 0;
                    }
                    // 다른 통화의 수수료는 환율 적용 필요
                });
            }
        }

        
        
        // 매수인 경우 수수료를 더하고, 매도인 경우 수수료를 뺌
        transaction.amount = transaction.type === 'BUY' 
            ? tradeAmount + feesTotal 
            : tradeAmount - feesTotal;
    }
    

    let estimatedPL = null;
    async function calculateEstimatedFIFOPL() {
        console.log('transaction', transaction.type);
        const submitData = {
            ...transaction,
            asset_id: parseInt(transaction.asset_id),
            debit_account_id: 1,
            credit_account_id: 2,
            quantity: parseFloat(transaction.quantity),
            price: parseFloat(transaction.price),
            amount: parseFloat(transaction.amount),
            exchange_rate: parseFloat(transaction.exchange_rate),
            // fees: transaction.fees,
            get_info: true,
        };

        const url = '/stock/investments/v2/security/get-info';
        
        fastapi('post', url, submitData,
            (json) => {
                console.log('Success:', json);
                estimatedPL = json[0];
                console.log('estimatedPL', estimatedPL);
            },
            (error) => {
                console.error('Error:', error);
                alert(error.detail || '오류가 발생했습니다.');
            }
        );
    }



    
    
</script>

<form on:submit|preventDefault={handleSubmit}>
    <div class="form-group">
        <label for="date">거래일자</label>
        <input type="date" id="date" bind:value={transaction.date} required />
    </div>
    <div class="form-group">
        <label for="currency">통화</label>
        <select id="currency" bind:value={transaction.currency} required>
            {#each currencies as currency}
                <option value={currency}>{currency}</option>
            {/each}
        </select>
    </div>
    <div class="form-group">
        <label for="type">매수/매도</label>
        <select id="type" bind:value={transaction.type} required>
            <option value="SECURITY_BUY">매수</option>
            <option value="SECURITY_SELL">매도</option>
        </select>
    </div>

    <div class="form-group">
        <label for="asset">종목</label>
        <select 
            id="asset" 
            bind:value={transaction.asset_id} 
            on:change={() => handleAssetChange(transaction.asset_id)}
            required
        >
            <option value="">선택하세요</option>
            {#each assets as asset}
                <option value={asset.id}>{asset.name}</option>
            {/each}
        </select>
    </div>
    {#if selectedPosition.quantity > 0}
        <div class="form-group position-info">    
            id: {selectedPosition.asset_id} {selectedPosition.asset.name} 보유수량: {selectedPosition.quantity}  평단가: {Math.round(selectedPosition.avg_price*100)/100}
        </div>
    {/if}

    <div class="form-row">
        <div class="form-group quantity">
            <label for="quantity">수량</label>
            <input 
                type="number" 
                id="quantity" 
                bind:value={transaction.quantity}
                on:input={calculateAmount}
                max={selectedPosition.quantity}
                step="any"
                required
            />
            
        </div>

        <div class="form-group price">
            <label for="price">단가 ({transaction.currency})</label>
            <input 
                type="number" 
                id="price" 
                bind:value={transaction.price}
                on:input={calculateAmount}
                step="any"
                required
            />
            
        </div>

        <div class="form-group amount">
            <label for="amount">총액 ({transaction.currency})</label>
            <input 
                type="number" 
                id="amount" 
                bind:value={transaction.amount}
                readonly
            />
            
        </div>
        <div class="form-group result-code">
            {formatNumber(transaction.quantity)} {formatNumber(transaction.price)} {formatNumber(transaction.amount)}
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

    {#if transaction.type === 'SECURITY_SELL' && estimatedPL}
    <!-- {#if transaction.type === 'STOCK_SELL' && estimatedPL} -->
        <div class="form-group realized-pl-section">
            <span class="pl-label">예상 실현 손익 ({transaction.currency})</span>
            <div class="estimated-pl {estimatedPL.profit_loss >= 0 ? 'profit' : 'loss'}">
                {formatNumber(estimatedPL.profit_loss-estimatedPL.total_fee)} {transaction.currency}   
            </div>
            <div class="estimated-pl-detail-row">
                비용: {Math.round(estimatedPL.total_fee * 10) / 10} {transaction.currency}, 
                수익율: {Math.round(estimatedPL.profit_loss_rate * 100) / 100}%
            </div>
            <div class="pl-details">
                <h5>매수 이력별 실현 손익</h5>
                {#each estimatedPL.summary as summary}
                    <div class="pl-detail-item">
                        <div class="detail-row">
                            <span class="date">매수일: {new Date(summary.date).toLocaleDateString()}</span>
                            <span class="holding-period">보유기간: {summary.holding_days}일</span>
                        </div>
                        <div class="detail-row">
                            <span class="price">매수가: {formatNumber(summary.bought_price)} {transaction.currency}</span>
                            <span class="quantity">수량: {formatNumber(summary.quantity)}/{formatNumber(summary.bought_quantity)}</span>
                            <span class="realized-pl {summary.realized_pl >= 0 ? 'profit' : 'loss'}">
                                손익: {formatNumber(summary.realized_pl)} {transaction.currency} 
                                ({Math.round(summary.realized_pl_rate * 100) / 100}%)
                            </span>
                        </div>
                    </div>
                {/each}
            </div>
        </div>
    {/if}

    
    <FeeForm 
        bind:fees={transaction.fees} 
        {resetFees}
        {transaction}
        {transactionType}
        bind:totalFee={totalFee}
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
    .position-info {
        margin-bottom: 15px;
        font-size: 0.7rem;
        color: #495057;
        font-weight: 600;
        /* 자간 너비 조절 */
        letter-spacing: 0.05rem;
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
    
    
    .realized-pl-section {
        background-color: #f8f9fa;
        padding: 12px;
        border-radius: 6px;
        border: 1px solid #e9ecef;
    }

    .pl-label {
        font-size: 0.65rem;
        color: #495057;
        font-weight: 600;
        margin-bottom: 8px;
    }

    .estimated-pl {
        font-size: 0.9rem;
        font-weight: bold;
        padding: 8px 12px;
        border-radius: 4px;
        text-align: right;
        margin-bottom: 10px;
    }

    .estimated-pl-detail-row {
        font-size: 0.65rem;
        text-align: right;
        color: #495057;
        margin-bottom: 10px;
    }

    .profit {
        color: #d63031;
        background-color: rgba(214, 48, 49, 0.1);
    }

    .loss {
        color: #0984e3;
        background-color: rgba(9, 132, 227, 0.1);
    }

    .pl-details {
        margin-top: 8px;
        font-size: 0.7rem;
    }

    h5 {
        font-size: 0.75rem;
        color: #495057;
        margin: 8px 0;
        padding-bottom: 4px;
        border-bottom: 1px solid #dee2e6;
    }

    .pl-detail-item {
        background-color: white;
        padding: 8px;
        border-radius: 4px;
        margin-bottom: 6px;
        border: 1px solid #e9ecef;
    }

    .detail-row {
        display: flex;
        justify-content: space-between;
        gap: 8px;
        margin-bottom: 4px;
    }

    .detail-row:last-child {
        margin-bottom: 0;
    }

    .date, .holding-period {
        color: #6c757d;
        font-size: 0.65rem;
    }

    .price, .quantity {
        color: #495057;
        font-size: 0.7rem;
    }

    .realized-pl {
        font-weight: 600;
        font-size: 0.7rem;
        padding: 2px 6px;
        border-radius: 3px;
    }

    .realized-pl.profit {
        color: #d63031;
        background-color: rgba(214, 48, 49, 0.1);
    }

    .realized-pl.loss {
        color: #0984e3;
        background-color: rgba(9, 132, 227, 0.1);
    }
</style>