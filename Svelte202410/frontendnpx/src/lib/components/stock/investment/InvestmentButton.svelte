<!-- src/lib/components/stock/investment/InvestmentButton.svelte -->
<script>
    import { createEventDispatcher } from 'svelte';
    const dispatch = createEventDispatcher();
    import { onMount } from 'svelte';
    // import { investmentStore } from '$lib/stores/stock';
    import TransactionsList from './forms/TransactionsList.svelte';
    // import TransactionForm from './TransactionForm.svelte';
    // import TransactionSummary from './TransactionSummary.svelte';
    // import TransactionList from './TransactionList.svelte';
    const API_BASE_URL = import.meta.env.VITE_API_URL?.replace('http://', 'https://') || 'https://api2410.ebesesk.synology.me';

    import { loadAssets, loadAccounts, loadTransactions, investmentStore, handleInvestmentButton } from './js/investmentStores';

    // let togglesInvestment = [];
    onMount(async () => {
        await Promise.all([
            loadTransactions(),
            loadAssets(),
            loadAccounts()
        ]);
        // isLoading = false;
    });


    



    function handleTransactionCreated() {
        loadTransactions($investmentStore.pagination.currentPage);
    }

    function handlePageChange(event) {
        loadTransactions(event.detail);
    }

    function toggleModal() {
        console.log('import.meta.env.VITE_API_URL:', import.meta.env.VITE_API_URL);
        showModal = !showModal;
    }
    
    
    // export let toggles = [];
    // export let togglesInvestment = [];
    // function handleModal(type) {
    //     console.log('toggleSetup:', type);
        
    //     console.log('togglesInvestment:', togglesInvestment);
    //     console.log('toggles:', type);
    //     dispatch('modalEvent', type);
    //     // dispatch('modalEvent', { detail: toggles });
    // }


</script>
<div class="button-group">
    <!-- 거래 관련 버튼 --> 
    <button
        class="button transaction"
        class:active={$investmentStore.toggles.includes('transactionForm')}
        on:click={() => handleInvestmentButton('transactionForm')}
    >거래입력</button>
    <button
        class="button transaction"
        class:active={$investmentStore.toggles.includes('transactionslist')}
        on:click={() => handleInvestmentButton('transactionslist')}
    >거래내역</button>
    <!-- <button
        class="button transaction"
        class:active={$investmentStore.toggles.includes('sell')}
        on:click={() => handleInvestmentButton('sell')}
    >매도</button>
    <button
        class="button transaction"
        class:active={$investmentStore.toggles.includes('dividend')}
        on:click={() => handleInvestmentButton('dividend')}
    >배당</button> -->
    <button
        class="button transaction"
        class:active={$investmentStore.toggles.includes('transaction_list')}
        on:click={() => handleInvestmentButton('transaction_list')}
    >거래 목록</button>
</div>

<div class="button-group">
    <!-- 계정 관련 버튼 -->
    <button
        class="button account"
        class:active={$investmentStore.toggles.includes('account_add')}
        on:click={() => handleInvestmentButton('account_add')}
    >계정 추가</button>
    <button
        class="button account"
        class:active={$investmentStore.toggles.includes('account_init')}
        on:click={() => handleInvestmentButton('account_init')}
    >계정 초기화</button>
    <button
        class="button account"
        class:active={$investmentStore.toggles.includes('account_list')}
        on:click={() => handleInvestmentButton('account_list')}
    >계정 목록</button>
</div>

<div class="button-group">
    <!-- 자산 관련 버튼 -->
    <button
        class="button asset"
        class:active={$investmentStore.toggles.includes('asset_init')}
        on:click={() => handleInvestmentButton('asset_init')}
    >자산초기화</button>
    <button
        class="button asset"
        class:active={$investmentStore.toggles.includes('asset_add')}
        on:click={() => handleInvestmentButton('asset_add')}
    >자산 등록</button>
    <button
        class="button asset"
        class:active={$investmentStore.toggles.includes('asset_list')}
        on:click={() => handleInvestmentButton('asset_list')}
    >자산 목록</button>
</div>

<style>
    .button-group {
        display: flex;
        gap: 0.5rem;
        margin-bottom: 0.2rem;
        margin-top: 0.2rem;
        margin-left: 0.2rem;
        margin-right: 0.2rem;
        font-size: 0.7rem;
    }

    button {
        flex: 1;
        padding: 0.5rem 1rem;
        border: 1px solid #ddd;
        border-radius: 4px;
        background: white;
        cursor: pointer;
        transition: all 0.2s;
        min-width: 0;
        white-space: nowrap;
    }

    /* 거래 버튼 스타일 */
    .transaction {
        border-color: #4CAF50;
        color: #4CAF50;
    }
    .transaction:hover {
        background: #E8F5E9;
    }
    .transaction.active {
        background: #4CAF50;
        color: white;
    }

    /* 계정 버튼 스타일 */
    .account {
        border-color: #2196F3;
        color: #2196F3;
    }
    .account:hover {
        background: #E3F2FD;
    }
    .account.active {
        background: #2196F3;
        color: white;
    }

    /* 자산 버튼 스타일 */
    .asset {
        border-color: #9C27B0;
        color: #9C27B0;
    }
    .asset:hover {
        background: #F3E5F5;
    }
    .asset.active {
        background: #9C27B0;
        color: white;
    }

    @media (max-width: 768px) {
        button {
            padding: 6px 12px;
            font-size: 0.9rem;
        }

        .button-group {
            flex-wrap: wrap;
        }

        button {
            flex: 1 1 calc(50% - 0.25rem);
            min-width: calc(50% - 0.25rem);
        }
    }
</style>