<!-- src/lib/components/stock/investment/AccountList.svelte -->
<script>
    import AccountForm from '$lib/components/stock/investment/AccountForm.svelte';
    import { loadAccounts, investmentStore, handleInvestmentButton } from './js/investmentStores';
    import { onMount } from 'svelte';
    
    onMount(async () => {
        await loadAccounts();
        
    });
    
    $: accounts = $investmentStore.accounts;
    let editingAccount = null;

    function handleEdit(account) {
        // 깊은 복사로 변경
        editingAccount = JSON.parse(JSON.stringify(account));
        console.log('editingAccount:', editingAccount);
        // handleInvestmentButton('account_add');
    }

    function handleAccountUpdated(event) {
        const updatedAccount = event.detail;
        loadAccounts();  // 목록 새로고침
        editingAccount = null;
        // handleInvestmentButton('account_add');  // 토글 닫기
    }

    function handleCancel() {
        editingAccount = null;
        // handleInvestmentButton('account_add');  // 토글 닫기
    }
    function handleAdd() {
        editingAccount = {
            code: '',
            name: '',
            category: '',
            type: '',
            is_active: true,
            account_metadata: {
                description: '',
                bank_code: ''
            }
        };
        // handleInvestmentButton('account_add');
    }
</script>
{#if editingAccount}
    <AccountForm 
        account={editingAccount}
        on:accountUpdated={handleAccountUpdated}
        on:cancel={handleCancel}
        />
        <!-- mode={editingAccount.id ? 'edit' : 'add'}
        on:accountUpdated={handleAccountUpdated}
        on:cancel={handleCancel} -->
{/if}
<div class="accounts-list">
    {#if accounts.length > 0}
        <h3>등록된 계정 ({accounts.length}개)</h3>
        <table>
            <thead>
                <tr>
                    <!-- <th>수정</th> -->
                    <th>id</th>
                    <th>코드</th>
                    <th>계정명</th>
                    <th>분류</th>
                    <th>유형</th>
                    <th>설명</th>
                </tr>
            </thead>
            <tbody>
                {#each accounts as account}
                    <tr class="code-{account.code.charAt(0)}">
                        <td>{account.id}</td>
                        <td>
                            <button class="btn-edit" on:click={() => handleEdit(account)}>수정</button>
                            {account.code}</td>
                        <td>{account.name}</td>
                        <td>{account.category}</td>
                        <td>{account.type}</td>
                        <td>{account.account_metadata?.description}</td>
                    </tr>
                {/each}
            </tbody>
        </table>
    {:else}
        <p>등록된 계정이 없습니다.</p>
    {/if}
</div>

<style>
    .accounts-list {
        margin: 0.1rem;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        margin: 0.01rem;
        font-size: 0.7rem;
    }

    th, td {
        padding: 0.1rem 0.2rem;
        font-size: 0.75rem;
        border: 0.5px solid #ddd;  /* 테두리 두께 줄임 */
    }

    th {
        background-color: #f5f5f5;
        font-weight: bold;
    }

    .btn-edit {
        padding: 0.1rem 0.2rem;
        background: #4CAF50;
        color: white;
        border: none;
        cursor: pointer;
        font-size: 0.3rem;
    }

    /* 계정 코드 첫 자리에 따른 색상 */
    .code-1 td {  /* 자산 */
        background-color: #e8f5e9;
    }
    .code-2 td {  /* 부채 */
        background-color: #ffebee;
    }
    .code-3 td {  /* 자본 */
        background-color: #e3f2fd;
    }
    .code-4 td {  /* 수익 */
        background-color: #f3e5f5;
    }
    .code-5 td {  /* 비용 */
        background-color: #fff3e0;
    }

    /* hover 효과 */
    tr:hover td {
        filter: brightness(95%);
    }

    @media (max-width: 768px) {
        th, td {
            padding: 4px 6px;
            font-size: 0.5rem;
            border: 0.5px solid #ddd;  /* 모바일에서도 얇은 테두리 유지 */
        }


        h3 {
            font-size: 0.5rem;
            margin: 8px 0;
        }


    }


</style>