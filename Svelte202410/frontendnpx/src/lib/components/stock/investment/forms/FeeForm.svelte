<script>
    import { createEventDispatcher } from 'svelte';
    import { investmentStore } from '../js/investmentStores';
    import { formatNumber } from '$lib/util';
    import {onMount} from 'svelte';
    const dispatch = createEventDispatcher();
    
    export let totalFee=0;
    export let transaction;  // 부모로부터 전달받는 transaction
    export let resetFees;
    $: if (resetFees) {
        resetFees = false;
        resetFeeForm();
    }
    
    export let fees = {};  // 부모로부터 전달받는 fees
    export let defaultCurrency = 'KRW';
    
    
    export let transactionType = 'CASH'; // 부모로부터 전달받는 transactionType  
    // console.log('transactionType', transactionType);
    
    const currencies = ['KRW', 'USD', 'EUR', 'JPY', 'CNY'];
    
    onMount(() => {
        // loadAccounts();
        // console.log('investmentStore feeform', $investmentStore);
    });

    // 고정 수수료 타입
    const initialFixedFeeTypes = [
        { 'id':18, 'code': '4101', 'name': '거래 수수료', 'amount':0, 'currency':defaultCurrency},
        { 'id':19, 'code': '4102', 'name': '증권거래세', 'amount':0, 'currency':defaultCurrency},
        { 'id':11, 'code': '4003', 'name': '수수료비용', 'amount':0, 'currency':defaultCurrency},
        { 'id':39, 'code': '4106', 'name': '인지세', 'amount':0, 'currency':defaultCurrency}
    ];
    // 거래 유형별 수수료 옵션
    const feeTypesByTransaction = {
        'TRADE': [
            { 'id':18, 'code': '4101', 'name': '거래 수수료', 'amount':0, 'currency':defaultCurrency},
            { 'id':19, 'code': '4102', 'name': '증권거래세', 'amount':0, 'currency':defaultCurrency},
            { 'id':11, 'code': '4003', 'name': '수수료비용', 'amount':0, 'currency':defaultCurrency},
            { 'id':39, 'code': '4106', 'name': '인지세', 'amount':0, 'currency':defaultCurrency}
        ],
        'EXCHANGE': [
            { 'id':10, 'code': '4002', 'name': '환차손', 'amount':0, 'currency':defaultCurrency},
        ],
        'CASH': [
            { 'id':11, 'code': '4003', 'name': '수수료비용', 'amount':0, 'currency':defaultCurrency},
        ],
        'INCOME': [
            { 'id':11, 'code': '4003', 'name': '수수료비용', 'amount':0, 'currency':defaultCurrency},
            { 'id':42, 'code': '4107', 'name': '배당세', 'amount':0, 'currency':defaultCurrency},
        ],
        'EXPENSE': [
            { 'id':11, 'code': '4003', 'name': '수수료비용', 'amount':0, 'currency':defaultCurrency},
        ]
    };

    
    // 기타 수수료용 선택 필드 (2개)
    let initialOtherFees = [
        { 'id':'', 'code': '', 'name': '', 'amount': 0, 'currency': defaultCurrency },
        { 'id':'', 'code': '', 'name': '', 'amount': 0, 'currency': defaultCurrency }
    ];
    
    let otherFees = [...initialOtherFees];
    


    // 현재 거래 유형에 맞는 수수료 옵션 선택
    $: fixedFeeTypes = feeTypesByTransaction[transactionType] || [];
    
    // fees가 변경될 때마다 실행
    $: {
        if (Object.keys(fees).length === 0) {
            resetFeeForm();
        }
    }

    $: if (transaction) {
        defaultCurrency = transaction.currency;
        if (!transaction.fees) {
            resetFeeForm();
        }
        // console.log('defaultCurrency', defaultCurrency);
    }
    // 비용 계정 필터링
    $: feeAccounts = ($investmentStore.accounts).filter(account => 
        account.code.startsWith('4')
    );
    // 통화별 수수료 합계 계산
    $: totalFeesByCurrency = Object.values(fees).reduce((acc, fee) => {
        const currency = fee.currency || defaultCurrency;
        acc[currency] = (acc[currency] || 0) + (fee.amount || 0);
        return acc;
    }, {});

    // console.log('fixedFeeTypes', fixedFeeTypes);
    
    // resetFees 이벤트 리스너 추가
    export function handleResetFees() {
        resetFeeForm();
    }
    
    
    function resetFeeForm() {
        // fees = {};
        // console.log('resetFeeForm', fees);
        fixedFeeTypes = [ ...initialFixedFeeTypes ];
        otherFees = [...initialOtherFees];

        for (let fee of fixedFeeTypes) {
            fee.amount = 0;
        }
        for (let fee of otherFees) {
            fee.amount = 0;
            fee.id = '';
            fee.code = '';
            fee.name = '';
            fee.currency = defaultCurrency;
        }
    }

    function handleFeeChange() {
        // console.log('otherFees', otherFees);
        totalFee = 0;
        let _fees = [...fixedFeeTypes, ...otherFees];

        _fees.forEach((feeType) => {
            if (feeType.code !== '' && feeType.amount > 0) {
                fees[feeType.code] = {};
                fees[feeType.code].amount = 0;
                fees[feeType.code].currency = defaultCurrency;
                fees[feeType.code].id = feeType.id;
                fees[feeType.code].name = feeType.name;
                fees[feeType.code].code = feeType.code;
                fees[feeType.code].amount = feeType.amount;
                fees[feeType.code].currency = feeType.currency;
                totalFee += feeType.amount;
            }else{
                delete fees[feeType.code];
            }
        });
        
        console.log('handleFeeChange', fees);
        dispatch('feeUpdate', { fees });
    }

    function handleFeeOtherChange(index, accountId) {
        for(let feeAccount of feeAccounts){
            // console.log('feeAccount', feeAccount, accountId);
            if(feeAccount.id == accountId){
                otherFees[index].id = feeAccount.id;
                otherFees[index].code = feeAccount.code;
                otherFees[index].name = feeAccount.name;
            }
        }
        // console.log('otherFees', otherFees);
        handleFeeChange();
    }

</script>

<svelte:window on:resetFees={handleResetFees} />

<div class="fees-container">
    <!-- 고정 수수료 입력 필드 -->
    {#each fixedFeeTypes as feeType, index}
    <div class="fee-item fee-inputs">
        <label class="fee-inputs label" for={feeType.code}>{feeType.code} - {feeType.name}</label>
        <span class="fee-inputs number-display">
            {formatNumber(feeType.amount || 0)} {defaultCurrency}
        </span>
        <input 
            class="fee-inputs number"
            type="number" 
            id={feeType.code}
            bind:value={fixedFeeTypes[index].amount}
            on:input={handleFeeChange}
            step="any"
            min="0"
            placeholder="금액"
        />
        <!-- <select 
            class="fee-inputs currency"
            bind:value={fixedFeeTypes[index].currency}
            on:input={handleFeeChange}
        >
            {#each currencies as curr}
                <option value={curr}>{curr}</option>
            {/each}
        </select> -->
    </div>
    {/each}

    <!-- 기타 수수료 선택 필드 -->
    {#each otherFees as otherFee, index}
    <div class="fee-item fee-inputs">
        <select 
            class="fee-inputs label"
            bind:value={otherFees[index]['id']}
            on:change={(e) => handleFeeOtherChange(index, e.target.value)}
        >
            <option value="">계정 선택</option>
            {#each feeAccounts as account}
                <option value={account.id}>
                    {account.code} - {account.name}
                </option>
            {/each}
        </select>
        <span class="fee-inputs number-display">
            {formatNumber(otherFees[index]['amount'])} {defaultCurrency}
        </span>
        <input 
            class="fee-inputs number"
            type="number" 
            bind:value={otherFees[index]['amount']}
            on:input={handleFeeChange}
            step="any"
            min="0"
            placeholder="금액"
        />
        <!-- <select 
            class="fee-inputs currency"
            bind:value={otherFees[index]['currency']}
            on:change={handleFeeChange}
        >
            {#each currencies as curr}
                <option value={curr}>{curr}</option>
            {/each}
        </select> -->
    </div>
    {/each}

    <!-- 통화별 합계 표시 -->
    <div class="fee-total">
        {#each Object.entries(totalFeesByCurrency) as [currency, total]}
            {#if total > 0}
                <div>
                    <strong>{currency}: {formatNumber(total)}</strong>
                </div>
            {/if}
        {/each}
    </div>
</div>

<style>
    .fees-container {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        padding: 0.5rem;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 0.7rem;
        width: 100%;  /* 컨테이너 전체 너비 */
    }

    .fee-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 0.5rem;
        width: 100%;
    }

    .fee-inputs {
        display: flex;
        gap: 0.5rem;
        align-items: center;
    }

    .fee-inputs.label {
        flex: 6;  /* 60% 차지 */
        min-width: 0;  /* flex-basis 오버플로우 방지 */
    }

    .fee-inputs.number-display {
        flex: 2;  /* 20% 차지 */
        min-width: 0;
        text-align: right;
        text-align-last: right;  /* select 박스 내부 텍스트 우측 정렬 */
        direction: rtl;  /* 드롭다운 옵션도 우측 정렬 */
    }

    .fee-inputs.number {
        flex: 2;  /* 20% 차지 */
        min-width: 0;
    }
    

    
    /* 입력 필드들이 너무 작아지는 것 방지 */
    .fee-inputs input,
    .fee-inputs select {
        width: 100%;
        min-width: 4rem;  /* 최소 너비 설정 */
        font-size: 0.7rem;
    }

    .fee-total {
        margin-top: 0.5rem;
        padding-top: 0.5rem;
        border-top: 1px solid #ddd;
        text-align: right;
        font-size: 0.7rem;
    }

    .fee-total > div {
        margin-bottom: 0.2rem;
    }

    label {
        font-size: 0.7rem;
        color: #666;
        min-width: 100px;
    }
</style>