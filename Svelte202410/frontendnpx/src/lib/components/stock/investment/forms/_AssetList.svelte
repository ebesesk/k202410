<script>
    import fastapi from '$lib/api'
    import { get } from 'svelte/store';
    import { key } from "$lib/stores/stock";
    import { access_token, username, userpoints } from '$lib/store'
    import { investmentStore, loadTransactions } from '$lib/components/stock/investment/js/investmentStores';
    import { onMount } from 'svelte';
    // import { get } from 'svelte/store'; 

    onMount(async () => {
        await loadTransactions();
        console.log('investmentStores.transactions:', $investmentStore.transactions)
        console.log('investmentStore.pagination:', $investmentStore.pagination)
    });
    $: investmentStore.subscribe(state => {
        console.log('investmentStore.transactions:', state.transactions)
    })
    $: filteredTransactions = $investmentStore?.transactions?.transactions?.filter(transaction => {
        if (!isUpdate) return true;
        return !['SELL_FEE', 'SELL_LOSS', 'SELL_PROFIT'].some(type => 
            transaction.type.includes(type)
        );
    });
    
    // 숫자 포맷팅 함수
    function formatNumber(num, decimals = 0) {
        return new Intl.NumberFormat('ko-KR', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }).format(num);
    }
    // 숫자 포맷팅 함수
    function formatNumber_digit(num) {
        return new Intl.NumberFormat('ko-KR', {
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(num);
    }


    // 이전 거래 데이터 가져오기
    async function getOldTradeLog() {
        // 사용자에게 확인
        const isConfirmed = confirm('이전 거래 데이터를 가져오시겠습니까?')
        
        if (isConfirmed) {
            let url = '/stock/investments/v2/transactions/get-old-trade-log'
            fastapi('get', url, {}, 
            (json) => {
                console.log('json', json)
                alert('데이터를 성공적으로 가져왔습니다.')
            },
            (error) => {
                console.log('error', error)
                alert('데이터 가져오기에 실패했습니다.')
            })
        }
    }

    // 전체 거래 내역 조회
    async function getTransactionsAll() {
        let url = '/stock/investments/v2/transactions/get-transactions-all'
        let params = {
            key: $key,
            
        }
        fastapi('get', url, params, 
        (json) => {
            console.log('json', json)
            alert('데이터를 성공적으로 가져왔습니다.')
        },
        (error) => {
            console.log('error', error)
            alert('데이터 가져오기에 실패했습니다.')
        })
    }


    // 계정 카테고리별 배경색 지정
    function getCategoryColor(category) {
        switch(category) {
            case '자산':
                return 'bg-asset';
            case '비용':
                return 'bg-expense'; 
            case '수익':
                return 'bg-income';
            case '자본':
                return 'bg-capital';
            case '부채':
                return 'bg-liability';
            default:
                return '';
        }
    }

    // 계정 분류 함수
    function isDebitAccount(category) {
        return ['자산', '비용'].includes(category);
    }


    let isUpdate = false;
    // let isDelete = false;
    let showModal = false;
    let editingTransaction = null;

    function toggleUpdate() {
        isUpdate = !isUpdate;
        console.log('toggleUpdate', isUpdate)
    }
    function toggleDelete() {
        isDelete = !isDelete;
        console.log('toggleDelete', isDelete)
    }

   

    

    // 수정 모달 열기
    const openEditModal = (transaction) => {
        // 깊은 복사로 객체 생성
        editingTransaction = JSON.parse(JSON.stringify(transaction));
        // 날짜 형식 보정
        if (editingTransaction.date) {
            // 단순히 T 이후 부분을 제거
            editingTransaction.date = editingTransaction.date.split('T')[0];
        }
        showModal = true;
    };
    const handleSubmit = () => {
        // 저장 시 날짜 형식 다시 변환
        const updatedTransaction = {
            ...editingTransaction,
            date: `${editingTransaction.date}T00:00:00`
        };
        // 저장 로직
        updateTransaction(updatedTransaction);
    };

    const closeModal = () => {
        showModal = false;
        editingTransaction = null;
    };

    const handleEdit = async () => {
        console.log('editingTransaction:', editingTransaction);
        // if (editingTransaction.date) {
        //     editingTransaction.date = toDatetime(editingTransaction.date);
        // }
        let url = '/stock/investments/v2/transactions/update-transaction'

        fastapi('post', url, editingTransaction, 
        (json) => {
            console.log('json', json)
            loadTransactions();
            closeModal();
        },
        (error) => {
            console.log('error', error)
        })
        // try {
        //     console.log('editingTransaction:', editingTransaction);
        //     closeModal();
        //     // 성공 메시지 또는 새로고침
        // } catch (error) {
        //     // 에러 처리
        //     console.error(error);
        // }
    };
    // let fees = [
    //     fee_1, fee_2, fee_3, fee_4, fee_5
    // ]
    
    let fee_1 = {id: 0,name: '',currency: '',amount: 0,code: ''}
    let fee_2 = {id: 0,name: '',currency: '',amount: 0,code: ''}
    let fee_3 = {id: 0,name: '',currency: '',amount: 0,code: ''}
    let fee_4 = {id: 0,name: '',currency: '',amount: 0,code: ''}
    let fee_5 = {id: 0,name: '',currency: '',amount: 0,code: ''}


    // type 변수 정의
    let type = 'transactions';  // 기본값 설정
    
    // 페이지네이션 관련 상태
    $: pagination = $investmentStore.pagination[type] || {
        currentPage: 1,
        totalItems: 0,
        itemsPerPage: 10
    };
    
    // totalPages 계산 시 숫자 확인
    $: totalPages = Math.max(1, Math.ceil(
        Number(pagination.totalItems) / Number(pagination.itemsPerPage)
    ));
    
    // 페이지 변경 핸들러
    function handlePageChange(page, currentKeyword) {
        // 숫자로 변환하여 확인
        const newPage = Number(page);
        if (!isNaN(newPage) && newPage >= 1 && newPage <= totalPages) {
            // 현재 keyword 값을 유지
            loadTransactions(newPage, currentKeyword || keyword);
        }
    }
    let keyword = 'asset'
    function setKeyword(page, newKeyword) {
        keyword = newKeyword;
        loadTransactions(page, newKeyword);
    }
</script>

<button class="get-old-trade-log" on:click={getOldTradeLog}>
    이전 거래 데이터 가져오기
</button>
<!-- {#if $investmentStore?.transactions?.analyze_currency?.by_currency} -->





<!-- 1. 거래 내역 -->
<div class="transaction-section">
    <div class="sort-container">
        <span>정렬</span>
        <button class="get-transactions-all" on:click={() => setKeyword(1, 'asset')}>asset</button>
        <button class="get-transactions-all" on:click={() => setKeyword(1, 'type')}>type</button>
        <button class="get-transactions-all" on:click={() => setKeyword(1, 'account')}>account</button>
        <button class="get-transactions-all" on:click={() => setKeyword(1, 'date')}>date</button>
        <button class="get-transactions-all" on:click={toggleUpdate}>update</button>
        <!-- <button class="get-transactions-all" on:click={toggleDelete}>delete</button> -->
    </div>
    <!-- <h2>거래 내역</h2> -->
    {#if $investmentStore.transactions.transactions}
        <div class="tables-container transaction-tables">
            <!-- 차변 계정 (자산, 비용) -->
            <div class="debit-accounts transaction-table">
                <div class="table-wrapper transaction-table">
                    {#each filteredTransactions as transaction}
                        <div class="list-item transaction-table">
                            <span class="date">{transaction.id}</span> 
                            <span class="date">{transaction.date.split('T')[0].slice(5, 10).replace('-', '.')}</span> 
                            {#if transaction.type === 'DEPOSIT' || transaction.type === 'WITHDRAWAL'}
                                <span class="type text-gradient">{transaction.type}</span> 
                                <span class="amount">{formatNumber(transaction.amount, 0)}</span> 
                                <span class="currency text-gradient">{transaction.currency}</span> 
                                {#if transaction.type === 'DEPOSIT'}    
                                    <span class="debit-account">{transaction.debit_account.name}</span>
                                {:else}
                                    <span class="credit-account">{transaction.debit_account.name}</span>
                                {/if}
                            {:else if transaction.type === 'EXCHANGE'}
                                <!-- <span class="date">{transaction.date.split('T')[0]}</span>  -->
                                <span class="type text-gradient">{transaction.type}</span>
                                FROM 
                                <span class="amount">{formatNumber(transaction.amount, 0)}</span> 
                                <span class="currency text-gradient">{transaction.currency}</span>
                                TO 
                                <span class="amount">{formatNumber(transaction.quantity, 0)}</span> 
                                <span class="currency text-gradient">{transaction.note}</span>
                                <span class="amount">{formatNumber(transaction.exchange_rate, 2)}</span>
                            {:else if transaction.type.includes('BUY')}
                                <!-- <span class="date">{transaction.date.split('T')[0]}</span>  -->
                                <span class="asset-name name">{transaction.asset.name}</span>
                                <span class="type text-gradient">{transaction.type.split('_').slice(1).join('_')}</span> 
                                <span class="text-muted">수량</span> 
                                <span class="quantity">{formatNumber(transaction.quantity, 0)}</span> 
                                <span class="text-muted">가격</span> 
                                <span class="quantity">{formatNumber(transaction.price, 0)}</span>
                                <span class="text-muted">금액</span> 
                                <span class="quantity">{formatNumber(transaction.amount, 0)}</span>
                                <span class="currency text-gradient">{transaction.currency}</span> 
                                <span class="debit-account">{transaction.debit_account.name}</span>
                                <span class="amount text-gradient">|</span>
                                <span class="debit-account">{transaction.credit_account.name}</span>
                                <span class="amount text-gradient">{transaction.transaction_metadata['fifo']['quantity']}</span>
                            {:else if transaction.type.includes('SELL')}
                                <!-- <span class="date">{transaction.date.split('T')[0]}</span>  -->
                                <span class="asset-name name">{transaction.asset.name}</span>
                                <span class="type text-gradient">{transaction.type.split('_').slice(1).join('_')}</span> 
                                {#if !['FEE', 'PROFIT', 'LOSS'].some(type => transaction.type.includes(type))}
                                    <!-- 일반 매도 거래 -->
                                    <span class="text-muted">수량</span> 
                                    <span class="quantity">{formatNumber(transaction.quantity)}</span> 
                                    <span class="text-muted">가격</span> 
                                    <span class="quantity">{formatNumber(transaction.price, 0)}</span>
                                    <span class="text-muted">금액</span> 
                                    <span class="quantity">{formatNumber(transaction.amount, 0)}</span>
                                {:else if transaction.type.includes('PROFIT')}
                                    <!-- 매도 이익 -->
                                    <span class="text-muted">실현이익</span>
                                    <span class="quantity profit">{formatNumber(transaction.amount, 0)}</span>
                                {:else if transaction.type.includes('LOSS')}
                                    <!-- 매도 손실 -->
                                    <span class="text-muted">실현손실</span>
                                    <span class="quantity loss">{formatNumber(transaction.amount, 0)}</span>
                                {:else if transaction.type.includes('FEE')}
                                    <!-- 매도 수수료 -->
                                    <span class="text-muted">수수료</span>
                                    <span class="quantity">{formatNumber(transaction.amount, 0)}</span>
                                {/if}
                                <span class="currency text-gradient">{transaction.currency}</span> 
                                <span class="debit-account">{transaction.debit_account.name}</span>
                                <span class="amount text-gradient">|</span>
                                <span class="debit-account">{transaction.credit_account.name}</span>
                                
                            {:else}
                                <span class="asset-name name">{transaction.asset.name}</span>
                                <span class="type text-gradient">{transaction.type.split('_').slice(1).join('_')}</span> 
                                {#if transaction.type.includes('FEE')}    
                                    <span class="quantity">{formatNumber(transaction.amount, 2)}</span> 
                                {:else}
                                    <span class="quantity">{formatNumber(transaction.amount)}</span> 
                                {/if}
                                <span class="currency text-gradient">{transaction.currency}</span> 
                                <span class="debit-account">{transaction.debit_account.name}</span>
                                <span class="amount text-gradient">|</span>
                                <span class="debit-account">{transaction.credit_account.name}</span>
                            {/if}
                            {#if isUpdate}
                                <div class="action-buttons">
                                    <button 
                                        class="edit-btn"
                                        on:click|stopPropagation={(e) => {
                                            e.preventDefault();
                                            openEditModal(transaction, e);
                                        }}
                                    >
                                        수정
                                    </button>
                                    <button 
                                        class="delete-btn"
                                        on:click|stopPropagation={(e) => {
                                            e.preventDefault();
                                            handleDelete(transaction);
                                        }}
                                    >
                                        삭제
                                    </button>
                                </div>
                            {/if}
                        </div>
                    {/each}
                </div>
            </div>
        </div>
    {/if}
</div>
<!-- 정렬 버튼들 -->
<div class="sort-container">
    <span>정렬</span>
    <button class="get-transactions-all" on:click={() => setKeyword(1, 'asset')}>asset</button>
    <button class="get-transactions-all" on:click={() => setKeyword(1, 'type')}>type</button>
    <button class="get-transactions-all" on:click={() => setKeyword(1, 'account')}>account</button>
    <button class="get-transactions-all" on:click={() => setKeyword(1, 'date')}>date</button>
</div>

<div class="pagination">
    <button 
        class="page-btn"
        disabled={pagination.currentPage <= 1}
        on:click={() => handlePageChange(Number(pagination.currentPage) - 1, keyword)}
    >
        이전
    </button>
    
    {#if totalPages <= 7}
        {#each Array(totalPages) as _, i}
            <button 
                class="page-btn {Number(pagination.currentPage) === i + 1 ? 'active' : ''}"
                on:click={() => handlePageChange(i + 1, keyword)}
            >
                {i + 1}
            </button>
        {/each}
    {:else}
        <!-- 첫 페이지 -->
        <button 
            class="page-btn {Number(pagination.currentPage) === 1 ? 'active' : ''}"
            on:click={() => handlePageChange(1, keyword)}
        >1</button>
        
        <!-- 왼쪽 생략 -->
        {#if Number(pagination.currentPage) > 3}
            <span class="ellipsis">...</span>
        {/if}
        
        <!-- 중간 페이지 -->
        {#each Array.from(
            {length: 3}, 
            (_, i) => Math.min(
                Math.max(Number(pagination.currentPage) - 1 + i, 2), 
                totalPages - 1
            )
        ) as page}
            {#if page > 1 && page < totalPages}
                <button 
                    class="page-btn {Number(pagination.currentPage) === page ? 'active' : ''}"
                    on:click={() => handlePageChange(page, keyword)}
                >
                    {page}
                </button>
            {/if}
        {/each}
        
        <!-- 오른쪽 생략 -->
        {#if Number(pagination.currentPage) < totalPages - 2}
            <span class="ellipsis">...</span>
        {/if}
        
        <!-- 마지막 페이지 -->
        {#if totalPages > 1}
            <button 
                class="page-btn {Number(pagination.currentPage) === totalPages ? 'active' : ''}"
                on:click={() => handlePageChange(totalPages, keyword)}
            >{totalPages}</button>
        {/if}
    {/if}
    
    <button 
        class="page-btn"
        disabled={Number(pagination.currentPage) >= totalPages}
        on:click={() => handlePageChange(Number(pagination.currentPage) + 1, keyword)}
    >
        다음
    </button>
</div>



<!-- FIFO 데이터 섹션 -->
{#if $investmentStore?.transactions?.fifo_summary}
    <div class="fifo-section">
        <h2>FIFO 실현 손익</h2>
        <div class="year-selector">
            <span>연도 선택:</span>
            {#each $investmentStore.transactions.fifo_summary.years as year}
                <button 
                    class="year-btn {year === $investmentStore.transactions.fifo_summary.selected_year ? 'active' : ''}"
                    on:click={() => loadTransactions(1, year)}
                >
                    {year}
                </button>
            {/each}
        </div>
        
        {#each Object.entries($investmentStore.transactions.fifo_summary) as [currency, data]}
            {#if currency !== 'years' && currency !== 'selected_year'}
                <div class="currency-group">
                    <h3>{currency}</h3>
                    <div class="total-pl">
                        총 실현 손익: <span class={data.total_pl >= 0 ? 'profit' : 'loss'}>
                            {formatNumber(data.total_pl)}
                        </span>
                    </div>
                    <table class="fifo-table">
                        <thead>
                            <tr>
                                <th>날짜</th>
                                <th>종목</th>
                                <th>코드</th>
                                <th>매수가</th>
                                <th>매도가</th>
                                <th>수량</th>
                                <th>실현손익</th>
                            </tr>
                        </thead>
                        <tbody>
                            {#each data.list as fifo}
                                <tr>
                                    <td>{fifo.date}</td>
                                    <td>{fifo.asset_name}</td>
                                    <td>{fifo.code}</td>
                                    <td class="number">{formatNumber(fifo.bought_price)}</td>
                                    <td class="number">{formatNumber(fifo.sell_price)}</td>
                                    <td class="number">{formatNumber(fifo.sell_quantity)}</td>
                                    <td class={`number ${fifo.realized_pl >= 0 ? 'profit' : 'loss'}`}>
                                        {formatNumber(fifo.realized_pl)}
                                    </td>
                                </tr>
                            {/each}
                        </tbody>
                    </table>
                </div>
            {/if}
        {/each}
    </div>
{/if}





<!-- 데이터가 있을 때만 렌더링 -->
{#if $investmentStore?.transactions}
<!-- 1. 통화별 원본 데이터 -->
<div class="currency-section">
    <h2>통화별 원본 데이터</h2>
    {#if $investmentStore?.transactions?.analyze_currency?.by_currency}
        {#each Object.entries($investmentStore.transactions.analyze_currency.by_currency) as [currency, data]}
            <div class="currency-group">
                <h4>{currency}</h4>
                <div class="tables-container">
                    <!-- 차변 계정 (자산, 비용) -->
                    <div class="debit-accounts">
                        <h4>자산, 비용 계정</h4>
                        <div class="table-wrapper">
                            <table>
                                <thead>
                                    <tr>
                                        <th>계정명</th>
                                        <th>구분</th>
                                        <th>금액</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {#each data.accounts.filter(acc => ['자산', '비용'].includes(acc.category)) as account}
                                        {#if account.balance !== 0}
                                        <tr class={getCategoryColor(account.category)}>
                                            <td>{account.name}</td>
                                            <td>{account.category}</td>
                                            <td class="amount">{formatNumber(account.balance)}</td>
                                        </tr>
                                        {/if}
                                    {/each}
                                </tbody>
                                <tfoot>
                                    <tr>
                                        <td colspan="2">차변 합계</td>
                                        <td class="amount">
                                            {formatNumber(data.accounts
                                                .filter(acc => ['자산', '비용'].includes(acc.category))
                                                .reduce((sum, acc) => sum + acc.balance, 0))}
                                        </td>
                                    </tr>
                                </tfoot>
                            </table>
                        </div>
                    </div>
                
                    <!-- 대변 계정 (부채, 자본, 수익) -->
                    <div class="credit-accounts">
                        <h4>부채, 자본, 수익 계정</h4>
                        <div class="table-wrapper">
                            <table>
                                <thead>
                                    <tr>
                                        <th>계정명</th>
                                        <th>구분</th>
                                        <th>금액</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {#each data.accounts.filter(acc => ['부채', '자본', '수익'].includes(acc.category)) as account}
                                        {#if account.balance !== 0}
                                            <tr class={getCategoryColor(account.category)}>
                                                <td>{account.name}</td>
                                                <td>{account.category}</td>
                                                <td class="amount">{formatNumber(account.balance)}</td>
                                            </tr>
                                        {/if}
                                    {/each}
                                </tbody>
                                <tfoot>
                                    <tr>
                                        <td colspan="2">대변 합계</td>
                                        <td class="amount">
                                            {formatNumber(data.accounts
                                                .filter(acc => ['부채', '자본', '수익'].includes(acc.category))
                                                .reduce((sum, acc) => sum + acc.balance, 0))}
                                        </td>
                                    </tr>
                                </tfoot>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        {/each}
    {/if}
</div>
{/if}




<!-- 모달 -->
{#if showModal}
    <div class="modal-backdrop" on:click={closeModal} role="dialog">
        <div class="modal-content" on:click|stopPropagation>
            {#if editingTransaction.asset_id}
                <h4>{editingTransaction.asset.name}</h4> 
            {/if}
            {editingTransaction.type} {editingTransaction.currency} {editingTransaction.id}
            <form on:submit|preventDefault={handleEdit} role="form">
                {#if editingTransaction.type.includes('DEPOSIT') || 
                     editingTransaction.type.includes('WITHDRAWAL') || 
                     editingTransaction.type.includes('EXPENSE') || 
                     editingTransaction.type.includes('INCOME')}
                    <!-- 수정 폼 필드들 -->
                    <div class="form-group">
                        <label for="date">날짜</label>
                        <input 
                            type="date" 
                            id="date"
                            bind:value={editingTransaction.date}
                        />
                    </div>
                    <div class="form-group">
                        <label for="currency">통화</label>
                        <input 
                            type="text" 
                            id="currency"
                            bind:value={editingTransaction.currency}
                        />
                    </div>
                    <div class="form-group">
                        <label for="amount">금액</label>
                        <input 
                            type="number" 
                            id="amount"
                            step="any"
                            bind:value={editingTransaction.amount}
                        />
                    </div>
                    <div class="form-group">
                        <label for="debit_account_id">차변 계정 (받는 계정)</label>
                        <select 
                            id="debit_account_id"
                            bind:value={editingTransaction.debit_account_id}
                            
                            class="amount-select"
                        >
                        {#each $investmentStore.accounts as account}
                            <option value={account.id}>
                                {account.name}
                            </option>
                        {/each}
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="credit_account_id">대변 계정 (주는 계정)</label>
                        <select 
                            id="credit_account_id"
                            bind:value={editingTransaction.credit_account_id}
                            
                            class="amount-select"
                        >
                        {#each $investmentStore.accounts as account}
                            <option value={account.id}>
                                {account.name}
                            </option>
                        {/each}
                        </select>
                    </div>
                {:else if editingTransaction.type === 'EXCHANGE'}
                    <!-- 수정 폼 필드들 -->
                    <div class="form-group">
                        <label for="date">날짜</label>
                        <input 
                            type="date" 
                            id="date"
                            bind:value={editingTransaction.date}
                        />
                    </div>
                    <div class="form-group">
                        <label for="currency">보내는 통화</label>
                        <input 
                            type="text" 
                            id="currency"
                            bind:value={editingTransaction.currency}
                        />
                    </div>
                    <div class="form-group">
                        <label for="amount">보내는 금액</label>
                        <input 
                            type="number" 
                            id="amount"
                            step="any"
                            bind:value={editingTransaction.amount}
                        />
                    </div>
                    <div class="form-group">
                        <label for="note">받을 통화</label>
                        <input 
                            type="text" 
                            id="note"
                            bind:value={editingTransaction.note}
                        />
                    </div>
                    <div class="form-group">
                        <label for="quantity">받을 금액</label>
                        <input 
                            type="number" 
                            id="quantity"
                            step="any"
                            bind:value={editingTransaction.quantity}
                        />
                    </div>
                    <div class="form-group">
                        <label for="exchange_rate">환율</label>
                        <input 
                            type="number" 
                            id="exchange_rate"
                            step="any"
                            bind:value={editingTransaction.exchange_rate}
                        />
                    </div>
                    <div class="form-group">
                        <label for="debit_account_id">차변 계정 (받는 계정)</label>
                        <select 
                            id="debit_account_id"
                            bind:value={editingTransaction.debit_account_id}
                            
                            class="amount-select"
                        >
                        {#each $investmentStore.accounts as account}
                            <option value={account.id}>
                                {account.name}
                            </option>
                        {/each}
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="credit_account_id">대변 계정 (주는 계정)</label>
                        <select 
                            id="credit_account_id"
                            bind:value={editingTransaction.credit_account_id}
                            
                            class="amount-select"
                        >
                        {#each $investmentStore.accounts as account}
                            <option value={account.id}>
                                {account.name}
                            </option>
                        {/each}
                        </select>
                    </div>
                {:else}
                    <!-- 수정 폼 필드들 -->
                    <div class="form-group">
                        <label for="date">날짜</label>
                        <input 
                            type="date" 
                            id="date"
                            bind:value={editingTransaction.date}
                        />
                    </div>
                    <div class="form-group">
                        <label for="price">가격</label>
                        <input 
                            type="number" 
                            id="price"
                            bind:value={editingTransaction.price}
                            step="any"
                        />
                    </div>
                    <div class="form-group">
                        <label for="quantity">수량</label>
                        <input 
                            type="number" 
                            id="quantity"
                            bind:value={editingTransaction.quantity}
                            step="any"
                        />
                    </div>
                    <div class="form-group">
                        <label for="amount">금액</label>
                        <input 
                            type="number" 
                            id="amount"
                            bind:value={editingTransaction.amount}
                            step="any"
                        />
                    </div>
                    <div class="form-group">
                        <label for="debit_account_id">차변 계정 (받는 계정)</label>
                        <select 
                            id="debit_account_id"
                            bind:value={editingTransaction.debit_account_id}
                            
                            class="amount-select"
                        >
                        {#each $investmentStore.accounts as account}
                            <option value={account.id}>
                                {account.name}
                            </option>
                        {/each}
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="credit_account_id">대변 계정 (주는 계정)</label>
                        <select 
                            id="credit_account_id"
                            bind:value={editingTransaction.credit_account_id}
                            class="amount-select"
                            >
                            {#each $investmentStore.accounts as account}
                            <option value={account.id}>
                                {account.name}
                                </option>
                                {/each}
                        </select>
                    </div>
                {/if}
                    {#if editingTransaction.fees}
                        <h4>수수료</h4>
                        {#each Object.entries(editingTransaction.fees) as [code, value]}
                            <div class="form-group">
                                <label for="amount">{code} {value.currency}</label>
                                <input 
                                    class="amount-input fee-input"
                                    type="number" 
                                    id="amount"
                                    bind:value={value.amount}
                                    step="any"
                                />
                                <select 
                                    id="credit_account_id"
                                    bind:value={value.id}
                                    class="amount-select"
                                >
                                {#each $investmentStore.accounts.filter(account => {
                                        return String(account.code).startsWith('4');
                                    }) as account}
                                        <option value={account.id}>
                                            {account.name} ({account.code})
                                        </option>
                                {/each}
                                </select>
                            </div>
                        {/each}
                    {/if}
                    <div class="form-group">
                        <label for="credit_account_id">{fee_1.name}</label>
                        <input 
                            class="amount-input fee-input"
                            type="number" 
                            step="any"
                            bind:value={fee_1.amount}
                            placeholder="금액"
                        />
                        <select 
                            id="fee_1_id"
                          
                            on:change={(e) => {
                                fee_1.id = e.target.value;
                                // 선택된 계정 찾기
                                const selectedAccount = $investmentStore.accounts.find(
                                    account => account.id === Number(fee_1.id)
                                );
                                
                                if (selectedAccount) {
                                    fee_1.name = selectedAccount.name;
                                    fee_1.code = selectedAccount.code;
                                    fee_1.currency = editingTransaction.currency;
                                    
                                    if (fee_1.amount) {
                                        
                                        if (!editingTransaction.fees) {
                                            editingTransaction.fees = {};
                                        }
                                        if (!editingTransaction.fees[fee_1.code]) {
                                            editingTransaction.fees[fee_1.code] = {};
                                        }
                                        editingTransaction.fees[fee_1.code] = {
                                            amount: fee_1.amount,
                                            id: Number(fee_1.id),
                                            currency: fee_1.currency,
                                            code: fee_1.code,
                                            name: fee_1.name  // name 추가
                                        };
                                    }
                                }
                            }}
                            class="amount-select"
                        >
                        {#each $investmentStore.accounts.filter(account => {
                            return String(account.code).startsWith('4');
                        }) as account}
                            <option value={account.id}>
                                {account.name} ({account.code})
                            </option>
                        {/each}
                        </select>
                    </div>
                    <!-- 추가 필드들 -->
                    
                    <div class="modal-actions">
                        <button type="submit" class="save-btn">저장</button>
                        <button type="button" class="cancel-btn" on:click={closeModal}>
                            취소
                        </button>
                    </div>
                </form>
        </div>
    </div>
{/if}



<style>
    .currency-section {
        margin: 0.1rem 0;
    }

    h2 {
        color: #333;
        margin-bottom: 1rem;
        font-size: 1.2rem;
    }

    /* h3 {
        color: #666;
        margin: 1rem 0;
        font-size: 1rem;
    } */

    .currency-group {
        margin-bottom: 2rem;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.8rem;
    }

    th, td {
        padding: 0.5rem;
        text-align: left;
        border-bottom: 1px solid #ddd;
    }

    th {
        background-color: #f5f5f5;
        font-weight: bold;
    }



    tfoot td {
        font-weight: bold;
        border-top: 2px solid #000;
    }

    /* 계정 카테고리별 배경색 */
    .bg-asset {
        background-color: rgba(200, 230, 201, 0.3);
    }
    
    .bg-expense {
        background-color: rgba(255, 205, 210, 0.3);
    }
    
    .bg-income {
        background-color: rgba(179, 229, 252, 0.3);
    }
    
    .bg-capital {
        background-color: rgba(225, 190, 231, 0.3);
    }

    .bg-liability {
        background-color: rgba(255, 224, 178, 0.3);
    }

    tr:hover {
        filter: brightness(0.95);
    }
    /* tr:nth-child(even) {
        background-color: rgba(0, 0, 0, 0.02);
    } */


    .sort-container {
        display: flex;
        flex-direction: row;
        gap: 1rem;
        margin: 0.1rem;
        padding: 0.1rem;
        background-color: #f5f5f5;
        border-radius: 0.1rem;
        font-size: 0.5rem;
        font-weight: 500;
        color: #333;
        justify-content: flex-start;
        align-items: center;
    }
    .table-wrapper {
        overflow-x: auto;
        width: 100%;
    }
    .tables-container {
        display: flex;  /* 가로 배열 */
        gap: 0.01rem;     /* 테이블 간 간격 */
        margin: 0.1rem;
        padding: 0.1rem;
    }


    .debit-accounts, .credit-accounts {
        flex: 1;       /* 동일한 너비로 분할 */
        min-width: 0;  /* 테이블 오버플로우 방지 */
        padding: 0.1rem;
        margin: 0.1rem 0;
        font-size: 0.4rem;
    }

    h4 {
        color: #444;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
        padding: 0.1rem;
        margin: 0.1rem 0;
    }



    .holdings-summary {
        padding: 0.1rem;
    }

    

    /* .amount {
        text-align: right;
        font-family: 'Courier New', monospace;
    } */

    .profit-positive {
        color: #d63031;
    }

    .profit-negative {
        color: #0984e3;
    }

    tr:hover {
        background-color: rgba(0, 0, 0, 0.02);
    }


    .transaction-section {
        margin: 0.1rem 0;
        display: flex;
        flex-direction: column;  /* 상하 배열 */
        gap: 0.1rem;              /* 섹션 간 간격 */
    }

    .tables-container.transaction-tables {
        display: flex;
        flex-direction: column;  /* 상하 배열 */
        /* gap: 0.01rem;   */
    }

    .table-wrapper.transaction-table {
        display: flex;
        flex-direction: column;
        overflow-x: auto;
        max-width: 100%;
    }
    .transaction-table {
        display: flex;
        flex-direction: column;
        overflow-x: auto;
        max-width: 100%;
        margin: 0.1rem 0;
        /* padding: 0.1rem; */
    }
    

    .list-item:hover {
        background-color: #f8f9fa;  /* 호버 시 배경색 변경 */
    }

    /* 짝수/홀수 행 구분을 위한 스타일 (선택사항) */
    .list-item:nth-child(even) {
        background-color: #f8f9fa;
    }

    .list-item:nth-child(even):hover {
        background-color: #f1f3f5;
    }

    /* 마지막 아이템의 구분선 제거 (선택사항) */
    .list-item:last-child {
        border-bottom: none;
    }

    .date {
        /* width: 10%; */
        font-size: 0.3rem;
    }
    .type {
        /* color: #4370a3; */
        /* width: 10%; */
        font-size: 0.5rem;
    }
    .amount, .quantity, .name {
        text-align: right;
        font-size: 0.7rem;
        font-weight: 500;
    }
    .text-gradient {
        color: #3f51b5;  /* Google Blue */
        font-weight: 500;
        text-shadow: 1px 1px 1px rgba(0,0,0,0.1);
    }
    .currency {
        font-weight: 500;
        font-size: 0.2rem;
    }
    .text-muted {
        color: #6c757d;  /* 연한 회색 */
        /* font-size: 0.8rem; */
    }
    .list-item {
        display: flex;  /* Flexbox 사용 */
        flex-direction: row;  /* 좌우 정렬 */
        align-items: center;  /* 세로 중앙 정렬 */
        justify-content: flex-start;  /* 좌측 정렬 */
        padding: 0.1rem;
        margin: 0.1rem 0;
        border-bottom: 1px solid #eee;
        background-color: #fff;
        transition: background-color 0.2s;
        gap: 0.1rem;  /* 항목 간 간격 */
    }
    /* 삭제 모드일 때의 스타일 */
    .list-item.transaction-table {
        /* position: relative; */
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: flex-start;  /* 좌측 정렬 */
        padding: 0.1rem 0.1rem;
        transition: all 0.2s ease;
        gap: 0.1rem;  /* 항목 간 간격 */
    }

    .clickable {
        cursor: pointer;
    }

    .clickable:hover {
        background-color: #f5f5f5;
    }

    .editable {
        background-color: #f8f9fa;
        border-left: 3px solid #4dabf7;  /* 수정 모드일 때 파란색 테두리 */
    }

    .editable:hover {
        background-color: #e9ecef;
    }

    .content {
        flex: 1;
    }

    .action-buttons {
        display: flex;
        gap: 0.1rem;
        margin-left: 0.1rem;
    }

    .edit-btn, .delete-btn {
        padding: 0.1rem 0.9rem;
        border: none;
        border-radius: 4px;
        font-size: 0.4rem;
        cursor: pointer;
        transition: all 0.2s;
    }

    .edit-btn {
        background-color: #4dabf7;
        color: white;
    }

    .edit-btn:hover {
        background-color: #339af0;
    }

    .delete-btn {
        background-color: #ff6b6b;
        color: white;
    }

    .delete-btn:hover {
        background-color: #fa5252;
    }

    

    /* 버튼 비활성화 스타일 */
    .edit-btn:disabled, .delete-btn:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    /* 버튼 로딩 상태 */
    .btn-loading {
        position: relative;
        color: transparent;
    }

    .btn-loading::after {
        content: "";
        position: absolute;
        width: 1em;
        height: 1em;
        border: 2px solid white;
        border-radius: 50%;
        border-top-color: transparent;
        animation: spin 1s linear infinite;
    }
    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    
    .get-transactions-all {
        margin: 0.1rem 0;
        padding: 0.1rem;
        font-size: 0.5rem;
        font-weight: 500;
        color: #333;
    }

    .modal-backdrop {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    }

    .modal-content {
        background-color: white;
        padding: 0.1rem;
        border-radius: 8px;
        min-width: 300px;
        max-width: 500px;
        width: 90%;
        max-height: 90vh;
        overflow-y: auto;
        font-size: 0.5rem;
    }

    .form-group {
        margin-bottom: 0.5rem;
        display: flex;
        flex-direction: row;
        gap: 0.1rem;
        align-items: center;
        justify-content: flex-end;
    }

    .form-group label {
        display: block;
        margin-bottom: 0.5rem;
        font-weight: bold;
    }

    .form-group input {
        width: 70%;
        padding: 0.1rem;
        border: 1px solid #ddd;
        border-radius: 4px;
        text-align: right;
    }

    .modal-actions {
        display: flex;
        justify-content: flex-end;
        gap: 1rem;
        margin-top: 2rem;
    }

    .save-btn, .cancel-btn {
        padding: 0.5rem 1rem;
        border: none;
        border-radius: 4px;
        cursor: pointer;
    }

    .save-btn {
        background-color: #4dabf7;
        color: white;
    }

    .cancel-btn {
        background-color: #868e96;
        color: white;
    }

    /* 애니메이션 */
    .modal-backdrop {
        animation: fadeIn 0.2s ease;
    }

    .modal-content {
        background-color: white;
        padding: 0.8rem;  /* 패딩 감소 */
        border-radius: 4px;
        min-width: 200px;  /* 최소 너비 감소 */
        max-width: 400px;  /* 최대 너비 감소 */
        width: 80%;
        max-height: 80vh;  /* 최대 높이 제한 */
        overflow-y: auto;
        font-size: 0.8rem;  /* 폰트 크기 축소 */
    }
    .amount-select {
        width: 50%;
        padding: 0.3rem;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 0.8rem;
        height: 1.8rem;
        margin-bottom: 0.3rem;
    }
    .fee-input {
        width: 40%;
        padding: 0.3rem;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 0.5rem;
        height: 1rem;
    }
    .custom-amount {
        width: 70%;
        padding: 0.3rem;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 0.8rem;
        height: 1.8rem;
    }




    .pagination {
        display: flex;
        gap: 0.3rem;
        align-items: center;
        justify-content: center;
        margin: 0.3rem 0;
    }
    
    .page-btn {
        padding: 0.3rem 0.5rem;
        border: 1px solid #ddd;
        background: white;
        cursor: pointer;
        border-radius: 4px;
        min-width: 1.5rem;
        font-size: 0.5rem;
    }
    
    .page-btn:disabled {
        background: #f5f5f5;
        cursor: not-allowed;
    }
    
    .page-btn.active {
        background: #007bff;
        color: white;
        border-color: #007bff;
    }
    
    .ellipsis {
        padding: 0 0.5rem;
    }
    /* 셀렉트 화살표 커스텀 */
    .amount-select {
        appearance: none;
        background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
        background-repeat: no-repeat;
        background-position: right 0.5rem center;
        background-size: 1em;
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    @keyframes slideIn {
        from { transform: translateY(-20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }


    .fifo-section {
        margin: 2rem 0;
        padding: 1rem;
        background-color: var(--background-color);
        border-radius: 8px;
    }

    .year-selector {
        margin: 1rem 0;
    }

    .year-btn {
        margin: 0 0.5rem;
        padding: 0.2rem 0.5rem;
        border: 1px solid #ddd;
        border-radius: 4px;
        background: #f8f9fa;
        cursor: pointer;
        font-size: 0.9rem;
        font-weight: 500;
        color: #495057;
        transition: all 0.2s ease;
    }

    .year-btn:hover {
        background-color: #e9ecef;
        border-color: #adb5bd;
    }

    .year-btn.active {
        background-color: #4dabf7;  /* 밝은 파란색 */
        color: #fff;
        font-weight: 700;
        border-color: #339af0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        transform: translateY(-1px);
    }

    .year-btn.active:hover {
        background-color: #339af0;
        border-color: #228be6;
    }

    .currency-group {
        margin: 2rem 0;
    }

    .fifo-table {
        width: 100%;
        border-collapse: collapse;
        margin: 1rem 0;
    }

    .fifo-table th,
    .fifo-table td {
        padding: 0.5rem;
        border: 1px solid var(--border-color);
        text-align: left;
        font-size: 0.5rem;
    }

    .number {
        text-align: right;
    }

    .profit {
        color: var(--profit-color, #4caf50);
    }

    .loss {
        color: var(--loss-color, #f44336);
    }

    .total-pl {
        font-size: 0.9rem;
        font-weight: bold;
        margin: 1rem 0;
    }


    
    /* 반응형 디자인을 위한 스타일 */
    @media (max-width: 768px) {
        table {
            font-size: 0.5rem;
        }

        th, td {
            padding: 0.1rem;
        }
        .list-item {
            padding: 0.1rem 0.1rem;
            font-size: 0.5rem;
        }
        .action-buttons {
            gap: 0.3rem;
        }

        .edit-btn, .delete-btn {
            padding: 0.1rem 0.1rem;
            font-size: 0.3rem;
        }
        .amount-select, .custom-amount {
            font-size: 0.5rem;
            height: 1.6rem;
        }
        .modal-content, .fee-input {
            padding: 0.1rem;
            font-size: 0.5rem;
        }
    }
</style>

