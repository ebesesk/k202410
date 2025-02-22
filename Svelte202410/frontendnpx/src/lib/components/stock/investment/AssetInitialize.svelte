<!-- src/lib/components/stock/investment/AssetInitialize.svelte -->
<script>
    import { onMount } from 'svelte';
    import { createEventDispatcher } from 'svelte';
    import fastapi from '$lib/api';
    import { investmentStore, loadAssets, handleInvestmentButton } from './js/investmentStores';
    const dispatch = createEventDispatcher();
    const API_BASE_URL = import.meta.env.VITE_API_URL?.replace('http://', 'https://') || 'https://api2410.ebesesk.synology.me';

    let message = '';
    let messageType = 'success';
    let loading = false;

    const assetTypes = [
        { id: 'stock_kr', name: '국내주식' },
        { id: 'stock_us', name: '미국주식' },
        { id: 'crypto', name: '암호화폐' },
        { id: 'custom', name: '직접입력' }
    ];

    let newAsset = {
        code: '',
        name: '',
        type: 'stock_kr',
        currency: 'KRW',
        description: ''
    };

    async function initializeCommonStocks() {
        loading = true;
        try {
            const url = '/stock/investments/assets/initialize/stocks';
            fastapi('post', url, {}, (json) => {
                console.log('json:', json);
                message = `주요 주식 종목이 성공적으로 초기화되었습니다. (${json.length}개)`;
                messageType = 'success';
                loading = false;
                loadAssets();
            }, (error) => {
                console.log('error:', error);
                message = error.message;
                messageType = 'error';
                loading = false;
            });

        } catch (error) {
            message = error.message;
            messageType = 'error';
            loading = false;
        }
        
        // try {
        //     const response = await fetch(API_BASE_URL + '/stock/investments/assets/initialize/stocks', {
        //         method: 'POST'
        //     });

        //     if (!response.ok) {
        //         throw new Error('주식 초기화 실패');
        //     }

        //     const assets = await response.json();
        //     message = `주식 종목이 성공적으로 초기화되었습니다. (${assets.length}개)`;
        //     messageType = 'success';
        //     dispatch('assetsInitialized', assets);
        // } catch (error) {
        //     message = error.message;
        //     messageType = 'error';
        // } finally {
        //     loading = false;
        // }
    }

    async function addCustomAsset() {
        loading = true;
        try {
            const response = await fetch(API_BASE_URL + '/stock/investments/assets', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(newAsset)
            });

            if (!response.ok) {
                throw new Error('자산 추가 실패');
            }

            const asset = await response.json();
            message = '자산이 성공적으로 추가되었습니다.';
            messageType = 'success';
            // dispatch('assetAdded', asset);
            resetForm();
        } catch (error) {
            message = error.message;
            messageType = 'error';
        } finally {
            loading = false;
        }
    }

    function resetForm() {
        newAsset = {
            code: '',
            name: '',
            type: 'stock_kr',
            currency: 'KRW',
            description: ''
        };
    }
</script>

<div class="asset-initialize">
    <h3>자산 등록</h3>
    
    <div class="button-group">
        <button 
            class="initialize-btn"
            on:click={initializeCommonStocks}
            disabled={loading}
        >
            주요 주식 종목 초기화
        </button>
    </div>

    <div class="custom-asset-form">
        <h4>직접 자산 등록</h4>
        <form on:submit|preventDefault={addCustomAsset}>
            <div class="form-group">
                <label for="type">자산 유형</label>
                <select id="type" bind:value={newAsset.type}>
                    {#each assetTypes as type}
                        <option value={type.id}>{type.name}</option>
                    {/each}
                </select>
            </div>

            <div class="form-group">
                <label for="code">코드</label>
                <input 
                    type="text" 
                    id="code"
                    bind:value={newAsset.code}
                    placeholder="예: 005930"
                    required
                />
            </div>

            <div class="form-group">
                <label for="name">이름</label>
                <input 
                    type="text" 
                    id="name"
                    bind:value={newAsset.name}
                    placeholder="예: 삼성전자"
                    required
                />
            </div>

            <div class="form-group">
                <label for="currency">통화</label>
                <select id="currency" bind:value={newAsset.currency}>
                    <option value="KRW">KRW</option>
                    <option value="USD">USD</option>
                    <option value="BTC">BTC</option>
                </select>
            </div>

            <div class="form-group">
                <label for="description">설명</label>
                <textarea 
                    id="description"
                    bind:value={newAsset.description}
                    rows="2"
                ></textarea>
            </div>

            <div class="form-actions">
                <button type="submit" disabled={loading}>등록</button>
                <button type="button" on:click={resetForm}>초기화</button>
                <button type="button" on:click={()=>handleInvestmentButton('asset_init')}>닫기</button>
            </div>
        </form>
    </div>

    {#if loading}
        <div class="loading">처리 중...</div>
    {/if}

    {#if message}
        <div class="alert {messageType}">
            {message}
        </div>
    {/if}
</div>

<style>
    .asset-initialize {
        padding: 20px;
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .button-group {
        margin: 20px 0;
    }

    .form-group {
        margin-bottom: 15px;
    }

    label {
        display: block;
        margin-bottom: 5px;
        font-weight: bold;
    }

    input, select, textarea {
        width: 100%;
        padding: 8px;
        border: 1px solid #ddd;
        border-radius: 4px;
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
        background: #4CAF50;
        color: white;
    }

    button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    .alert {
        margin-top: 15px;
        padding: 10px;
        border-radius: 4px;
    }

    .success {
        background: #e8f5e9;
        color: #2e7d32;
    }

    .error {
        background: #ffebee;
        color: #c62828;
    }

    @media (max-width: 768px) {
        .asset-initialize {
            padding: 15px;
        }

        button {
            padding: 6px 12px;
            font-size: 0.9rem;
        }

        .form-group {
            margin-bottom: 10px;
        }

        label {
            font-size: 0.9rem;
        }

        input, select, textarea {
            padding: 6px;
            font-size: 0.9rem;
        }
    }
</style>