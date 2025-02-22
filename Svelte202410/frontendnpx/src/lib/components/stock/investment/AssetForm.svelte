<script>
    import { loadAssets, investmentStore, handleInvestmentButton } from './js/investmentStores';
    const API_BASE_URL = import.meta.env.VITE_API_URL?.replace('http://', 'https://') || 'https://api2410.ebesesk.synology.me';
    import fastapi from '$lib/api';
    
    export let isEditing = false;
    export let editingAsset = {};
    // 기본값으로 초기화된 asset 객체
    let asset = isEditing ? editingAsset : {
        name: '',
        symbol: '',
        type: 'STOCK',  // 기본값 설정
        currency: 'KRW',
        exchange: '',
        asset_metadata: {
            bank_code: '',
            account_number: '',
            securities_code: '',
            base_currency: ''
        }
    };

    // const assetTypes = [
    //     { value: 'STOCK', label: '주식' },
    //     { value: 'BOND', label: '채권' },
    //     { value: 'FUND', label: '펀드' },
    //     { value: 'ETF', label: 'ETF' },
    //     { value: 'CASH', label: '현금' },
    //     { value: 'BANK', label: '은행' },
    //     { value: 'REAL_ESTATE', label: '부동산' },
    //     { value: 'CRYPTO', label: '가상화폐' },
    //     { value: 'OTHER', label: '기타' }
    // ];

    const currencies = [
        { value: 'KRW', label: '원화 (KRW)' },
        { value: 'USD', label: '미국 달러 (USD)' },
        { value: 'JPY', label: '일본 엔 (JPY)' },
        { value: 'EUR', label: '유로 (EUR)' },
        { value: 'CNY', label: '중국 위안 (CNY)' }
    ];

    // 은행 목록 추가
    const bankList = [
        { code: 'KB', name: '국민은행' },
        { code: 'SH', name: '신한은행' },
        { code: 'WR', name: '우리은행' },
        { code: 'NH', name: '농협은행' },
        { code: 'IBK', name: '기업은행' },
        { code: 'KEB', name: '하나은행' },
        { code: 'SC', name: 'SC제일은행' },
        { code: 'CITI', name: '씨티은행' },
        { code: 'KDB', name: '산업은행' },
        { code: 'KAKAO', name: '카카오뱅크' },
        { code: 'TOSS', name: '토스뱅크' }
    ];
    const assetTypes = [
        { value: 'STOCK', label: '주식' },
        { value: 'BOND', label: '채권' },
        { value: 'FUND', label: '펀드' },
        { value: 'ETF', label: 'ETF' },
        { value: 'CASH', label: '현금' },
        { value: 'BANK', label: '은행' },
        { value: 'SECURITIES', label: '증권' },
        { value: 'SECURITIES_FX', label: '증권 외환' },
        { value: 'REAL_ESTATE', label: '부동산' },
        { value: 'CRYPTO', label: '가상화폐' },
        { value: 'OTHER', label: '기타' }
    ];

    // 증권사 목록 추가
    const securitiesList = [
        { code: 'KIWOOM', name: '키움증권' },
        { code: 'SAMSUNG', name: '삼성증권' },
        { code: 'MIRAEASSET', name: '미래에셋증권' },
        { code: 'KOREA', name: '한국투자증권' },
        { code: 'LS', name: 'LS증권' },
        { code: 'NH', name: 'NH투자증권' },
        { code: 'KB', name: 'KB증권' },
        { code: 'SHINHAN', name: '신한투자증권' },
        { code: 'HANA', name: '하나증권' },
        { code: 'TOSS', name: '토스증권' }
    ];
    async function handleSubmit() {
        console.log('handleSubmit asset:', asset);
        const url = isEditing ? 
                `/stock/investments/assets/${asset.id}` : 
                `/stock/investments/assets`;
        fastapi(isEditing ? 'put' : 'post', url, asset, 
            (json) => {
                console.log(json);
            },
            (error) => {
                console.error(error);
            }
        );
    }
</script>

{#if asset}
<form on:submit|preventDefault={handleSubmit}>
    <div class="form-group">
        <label for="type">자산유형</label>
        <select id="type" bind:value={asset.type} required>
            {#each assetTypes as type}
                <option value={type.value}>{type.label}</option>
            {/each}
        </select>
    </div>
    <div class="form-group">
        <label for="name">자산명</label>
        <input 
            type="text" 
            id="name" 
            bind:value={asset.name}
            required
        />
    </div>
    {#if asset.type==='stock_us' || asset.type==='stock_kr' || asset.type === 'CRYPTO' || asset.type === 'STOCK' || asset.type === 'ETF' || asset.type === 'FUND' || asset.type === 'BOND'}
    <div class="form-group">
        <label for="code">Symbol & code</label>
        <input 
            type="text" 
            id="symbol" 
            bind:value={asset.symbol}
            required
        />
    </div>
    <div class="form-group">
        <label for="type">시장</label>
        <input 
            type="text" 
            id="exchange" 
            bind:value={asset.exchange}
            placeholder="NASDAQ, NYSE, KOSDAQ, KOSPI, etc."
            required
        />
    </div>
    {/if}

    

    <div class="form-group">
        <label for="currency">통화</label>
        <select id="currency" bind:value={asset.currency} required>
            {#each currencies as currency}
                <option value={currency.value}>{currency.label}</option>
            {/each}
        </select>
    </div>

    {#if asset.type === 'BANK'}
        <div class="form-group">
            <label for="bank">은행</label>
            <select 
                id="bank" 
                bind:value={asset.asset_metadata.bank_code}
                required
            >
                <option value="">선택하세요</option>
                {#each bankList as bank}
                    <option value={bank.code}>{bank.name}</option>
                {/each}
            </select>
        </div>

        <div class="form-group">
            <label for="account_number">계좌번호</label>
            <input 
                type="text" 
                id="account_number"
                bind:value={asset.asset_metadata.account_number}
                placeholder="'-' 없이 입력"
                required
            />
        </div>
    {:else if asset.type === 'SECURITIES' || asset.type === 'SECURITIES_FX'}
        <div class="form-group">
            <label for="securities">증권사</label>
            <select 
                id="securities" 
                bind:value={asset.asset_metadata.securities_code}
                required
            >
                <option value="">선택하세요</option>
                {#each securitiesList as securities}
                    <option value={securities.code}>{securities.name}</option>
                {/each}
            </select>
        </div>

        <div class="form-group">
            <label for="account_number">계좌번호</label>
            <input 
                type="text" 
                id="account_number"
                bind:value={asset.asset_metadata.account_number}
                placeholder="'-' 없이 입력"
                required
            />
        </div>

        {#if asset.type === 'SECURITIES_FX'}
            <div class="form-group">
                <label for="base_currency">기준 통화</label>
                <select 
                    id="base_currency" 
                    bind:value={asset.asset_metadata.base_currency}
                    required
                >
                    {#each currencies as currency}
                        <option value={currency.value}>{currency.label}</option>
                    {/each}
                </select>
            </div>
        {/if}
    {/if}

    <div class="form-actions">
        <button type="submit" class="btn-primary">
            {isEditing ? '수정' : '등록'} 
        </button>
        {#if !isEditing}
        <button 
            on:click={() => handleInvestmentButton('asset_add')}
            type="submit" class="btn-primary">
             닫기
        </button>
        {/if}
    </div>
</form>
{/if}

<style>
    .form-group {
        margin-bottom: 1rem;
    }

    label {
        display: block;
        margin-bottom: 0.5rem;
        font-weight: bold;
    }

    input, select {
        width: 100%;
        padding: 0.5rem;
        border: 1px solid #ddd;
        border-radius: 4px;
    }

    .form-actions {
        margin-top: 1rem;
        display: flex;
        justify-content: space-between;
    }

    .btn-primary {
        background: #4CAF50;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        cursor: pointer;
    }

    .btn-primary:hover {
        background: #45a049;
    }
</style>