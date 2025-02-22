<script>
    import { investmentStore, loadExchangeRate } from '$lib/components/stock/investment/js/investmentStores';
    import { formatNumber } from '$lib/util';
    import fastapi from '$lib/api';
    import { onMount } from 'svelte';   

    onMount(async () => {
        await loadExchangeRate();
    });

    let exchangeRateForm = {
        from_currency: 'USD',
        to_currency: 'KRW',
        rate: $investmentStore.exchangeRate?.USD?.to_currency === 'KRW' 
              ? $investmentStore.exchangeRate.USD.rate 
              : 1300.00,  // 기본값
        date: new Date().toISOString().split('T')[0]
    };

    const currencies = ['KRW', 'USD', 'JPY', 'EUR', 'CNY'];

    async function handleSubmit() {
        if (!exchangeRateForm.rate || !exchangeRateForm.date) {
            alert('모든 필드를 입력해주세요.');
            return;
        }
        let params = {
            from_currency: exchangeRateForm.from_currency,
            to_currency: exchangeRateForm.to_currency,
            rate: exchangeRateForm.rate,
            date: exchangeRateForm.date
        }
        let url = '/stock/investments/v2/exchange'
        fastapi('post', url, params,
        (json) => {
            console.log('json', json)
            alert('환율이 등록되었습니다.')
        },
        (error) => {
            console.log('error', error)
            alert('환율 등록에 실패했습니다.')
        })
        // try {
        //     investmentStore.setExchangeRate({
        //         ...($investmentStore.exchangeRate || {}),
        //         [exchangeRateForm.from_currency]: {
        //             ...($investmentStore.exchangeRate?.[exchangeRateForm.from_currency] || {}),
        //             [exchangeRateForm.to_currency]: {
        //                 rate: parseFloat(exchangeRateForm.rate),
        //                 date: exchangeRateForm.date
        //             }
        //         }
        //         // investmentStore.exchangeRate = {
        //         //     from_currency: {
        //         //         to_currency: {
        //         //             rate: parseFloat(exchangeRateForm.rate),
        //         //             date: exchangeRateForm.date
        //         //         }
        //         //     }
        //         // }
        //     });

        //     console.log('investmentStore.exchangeRate:', $investmentStore);
        //     alert('환율이 등록되었습니다.');
            
        // } catch (error) {
        //     console.error('환율 등록 오류:', error);
        //     alert('환율 등록에 실패했습니다.');
        // }
    }

    // 환율 읽어오기
    // function loadExchangeRate() {
    //     exchangeRateForm = {
    //         from_currency: 'USD',
    //         to_currency: 'KRW',
    //         rate: '',
    //         date: new Date().toISOString().split('T')[0]    
    //     };
    // }
    // 통화 변경시 해당 환율 정보 업데이트
    $: {
        if (exchangeRateForm.from_currency && exchangeRateForm.to_currency) {
            const storedRate = $investmentStore.exchangeRate?.[exchangeRateForm.from_currency]?.[exchangeRateForm.to_currency];
            if (storedRate) {
                exchangeRateForm.rate = storedRate.rate;
                exchangeRateForm.date = storedRate.date;
            }
        }
    }
</script>

<div class="exchange-rate-form">
    <form on:submit|preventDefault={handleSubmit}>
        <div class="form-header">
            <h3>환율 등록</h3>
            <div class="form-actions">
                <button type="submit" class="submit-btn">등록</button>
                <button type="button" class="reset-btn" on:click={() => {
                    exchangeRateForm = {
                        from_currency: 'USD',
                        to_currency: 'KRW',
                        rate: '',
                        date: new Date().toISOString().split('T')[0]
                    };
                }}>초기화</button>
                <button type="button" class="reset-btn" on:click={() => {
                    loadExchangeRate();
                }}>읽어오기</button>
            </div>
        </div>
        {#each Object.entries($investmentStore.exchangeRate) as [currency, rate]}
        <div class="form-row">
            <div class="form-group">
                {$investmentStore.exchangeRate?.[exchangeRateForm.from_currency]?.[exchangeRateForm.to_currency]?.date.split('T')[0]}
            </div>
            <div class="form-group">
                {currency}
            </div>

            <div class="form-group">
                <select id="to_currency" bind:value={exchangeRateForm.to_currency}>
                    {#each Object.keys(rate) as to_currency}
                        <option value={to_currency}>{to_currency}</option>
                    {/each}
                </select>
            </div>
            <div class="form-group">
                <input 
                    type="number" 
                    id="rate" 
                    bind:value={exchangeRateForm.rate}
                    step="0.01"
                    min="0"
                    placeholder="예: 1300.00"
                >
            </div>

            <!-- <div class="form-group">
                <input 
                    type="date" 
                    id="date" 
                    bind:value={exchangeRateForm.date}
                >
            </div> -->
        </div>
        {/each}
    </form>
</div>

<style>
    .exchange-rate-form {
        background: var(--background-color);
        padding: 0.5rem;
        border-radius: 4px;
        border: 1px solid var(--border-color);
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);  /* 그림자 효과 추가 */
        width: 95%;
    }

    h3 {
        margin: 0 0 0.3rem 0;
        color: var(--text-color);
        font-size: 0.7rem;
    }

    .form-row {
        display: flex;
        gap: 0.5rem;
        margin-bottom: 0.5rem;
    }

    .form-group {
        flex: 1;
        min-width: 0;  /* flex-basis 오버플로우 방지 */
        white-space: nowrap;  /* 텍스트 줄바꿈 방지 */
    }

    label {
        display: block;
        margin-bottom: 0.3rem;
        font-size: 0.8rem;
        color: var(--text-muted);
        font-size: 0.7rem;
    }

    input, select {
        width: 100%;
        padding: 0.1rem;
        border: 1px solid var(--border-color);
        border-radius: 4px;
        font-size: 0.7rem;
    }

    .form-actions {
        display: flex;
        gap: 0.5rem;
        justify-content: flex-end;
    }

    button {
        padding: 0.1rem 0.5rem;
        border: none;
        border-radius: 4px;
        font-size: 0.7rem;
        cursor: pointer;
    }

    .submit-btn {
        background: var(--primary-color, #4dabf7);  /* 밝은 파란색 기본값 추가 */
        color: white;
        font-weight: 500;
        border: 1px solid var(--primary-dark, #339af0);
    }

    .reset-btn {
        background: var(--background-color, #f8f9fa);  /* 밝은 회색 기본값 추가 */
        color: var(--text-color, #495057);  /* 텍스트 색상 추가 */
        border: 1px solid var(--border-color, #dee2e6);
        font-weight: 500;
    }

    button:hover {
        opacity: 0.9;
    }
    .form-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }

    .form-actions {
        display: flex;
        gap: 0.5rem;
    }
</style>