<!-- src/components/AccountForm.svelte -->
<script>
    import { createEventDispatcher } from 'svelte';
    const dispatch = createEventDispatcher();
    import { onMount } from 'svelte';
    import { loadAccounts, investmentStore, handleInvestmentButton } from './js/investmentStores';
    import fastapi from '$lib/api';
    
    export let account;
    // export let mode = 'edit'
    let message = '';
    let messageType = 'success';
    
    onMount(async () => {
      await loadAccounts();
      console.log('account', account);
    });
    
    $: currentAccount = account || {
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
  
    // $: isEditMode = mode === false;
    $: formTitle = currentAccount?.id ? '계정 수정' : '계정 추가';
    $: submitButtonText = currentAccount?.id ? '수정' : '추가';

    const categories = [
      { value: '자산', label: '자산' },
      { value: '부채', label: '부채' },
      { value: '자본', label: '자본' },
      { value: '수익', label: '수익' },
      { value: '비용', label: '비용' }
    ];
    const API_BASE_URL = import.meta.env.VITE_API_URL?.replace('http://', 'https://') || 'https://api2410.ebesesk.synology.me';

    async function submitAccount() {
      try {
        console.log('currentAccount:', currentAccount);
        
        // const url = isEditMode 
        const url = currentAccount?.id 
          ? `/stock/investments/accounts/${currentAccount.id}`  // API_BASE_URL 제거
          : `/stock/investments/accounts`;
      
        // method를 isEditMode에 따라 다르게 설정
        const method = currentAccount?.id ? 'put' : 'post';
        
        fastapi(method, url, currentAccount, 
          (json) => {
            console.log('json:', json);
            const updatedAccount = json.account_update;
            message = `계정이 성공적으로 ${currentAccount?.id ? '수정' : '추가'}되었습니다.`;
            messageType = 'success';
            if (currentAccount?.id) {
              loadAccounts();  // 목록 새로고침
            } else {
              // 성공 시 이벤트 디스패치 추가
              dispatch('accountUpdated', updatedAccount);
            }
          }, 
          (error) => {
            // 에러 콜백
            console.log('error:', error);
            message = `계정 ${currentAccount?.id ? '수정' : '추가'} 실패: ${error.detail || error}`;
            messageType = 'error';
          }
        );
      } catch (error) {
        console.error('fastapi error:', error);
        message = error.message;
        messageType = 'error';
      }
    }
    function resetForm() {
      account = {
        code: '',
        name: '',
        category: '',
        type: '',
        is_active: true,
        account_metadata: {
          description: ''
        }
      };
    }
    
  </script>
  
  <div class="account-form">
    <h2>{formTitle}</h2>
    <form on:submit|preventDefault={submitAccount} class="form-container">
      <div class="form-group">
        <label for="code">계정코드:</label>
        <input 
          id="code"
          bind:value={currentAccount.code}
          type="text"
          required
          placeholder="예: 101"
        >
      </div>
  
      <div class="form-group">
        <label for="name">계정명:</label>
        <input 
          id="name"
          bind:value={currentAccount.name}
          type="text"
          required
          placeholder="예: 현금"
        >
      </div>
  
      <div class="form-group">
        <label for="category">분류:</label>
        <select 
          id="category" 
          bind:value={currentAccount.category}
          required
        >
          <option value="">선택하세요</option>
          {#each categories as category}
            <option value={category.value}>{category.label}</option>
          {/each}
        </select>
      </div>
  
      <div class="form-group">
        <label for="type">세부유형:</label>
        <input 
          id="type"
          bind:value={currentAccount.type}
          type="text"
          required
          placeholder="예: 유동자산"
        >
      </div>
  
      <div class="form-group">
        <label for="description">설명:</label>
        <textarea 
          id="description"
          bind:value={currentAccount.account_metadata.description}
          placeholder="계정에 대한 설명을 입력하세요"
        ></textarea>
      </div>
  
      <div class="form-group checkbox">
        <label>
          <input 
            type="checkbox"
            bind:checked={currentAccount.is_active}
          >
          활성화
        </label>
      </div>
  
      <div class="button-group">
        <button type="submit" class="submit-btn">{submitButtonText}</button>
        <button type="button" on:click={resetForm} class="cancel-btn">지우기</button>
        {#if currentAccount?.id}
          <button type="button" on:click={()=>dispatch('cancel')} class="cancel-btn">닫기</button>
        {:else}
          <button type="button" on:click={()=>handleInvestmentButton('account_add')} class="cancel-btn">닫기</button>
        {/if}
      </div>
    </form>
  
    {#if message}
      <div class="alert {messageType}">
        {message}
      </div>
    {/if}
  </div>
  
  <style>
    .account-form {
      max-width: 600px;
      margin: 0 auto;
      padding: 20px;
    }
  
    .form-container {
      background: #f5f5f5;
      padding: 20px;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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
      box-sizing: border-box;
    }
  
    textarea {
      height: 100px;
      resize: vertical;
    }
  
    .checkbox {
      display: flex;
      align-items: center;
    }
  
    .checkbox input {
      width: auto;
      margin-right: 8px;
    }
  
    .button-group {
      display: flex;
      gap: 10px;
      margin-top: 20px;
    }
  
    button {
      padding: 10px 20px;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-weight: bold;
    }
  
    .submit-btn {
      background-color: #4CAF50;
      color: white;
    }
  
    .reset-btn {
      background-color: #f44336;
      color: white;
    }
  
    .alert {
      margin-top: 20px;
      padding: 10px;
      border-radius: 4px;
    }
  
    .success {
      background-color: #dff0d8;
      color: #3c763d;
      border: 1px solid #d6e9c6;
    }
  
    .error {
      background-color: #f2dede;
      color: #a94442;
      border: 1px solid #ebccd1;
    }



    @media (max-width: 768px) {


        .transaction-form, .summary-card {
            padding: 12px;
        }


        label {
            font-size: 0.9rem;
            margin-bottom: 3px;
        }

        input, select, textarea {
            padding: 6px;
            font-size: 0.9rem;
        }

        button {
            padding: 6px 12px;
            font-size: 0.9rem;
        }

        .form-group {
            margin-bottom: 8px;
        }

        .form-row {
            gap: 8px;
        }

        .summary-grid {
            gap: 10px;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        }

        .summary-item {
            gap: 3px;
        }

        .label {
            font-size: 0.8rem;
        }

        .value {
            font-size: 1rem;
        }

        .pagination {
            padding: 10px;
            gap: 5px;
        }


        .btn-edit, .btn-delete {
            padding: 2px 6px;
            font-size: 0.8rem;
        }
    }

    /* 테이블 스크롤 처리 */
    .transaction-list {
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
    }

    /* 모달 크기 조정 */
    @media (max-width: 768px) {
        .modal-content {
            width: 95%;
            padding: 10px;
            margin: 10px;
        }

        .close-button {
            padding: 4px 8px;
            font-size: 0.8rem;
        }
    }

    /* AccountInitialize 컴포넌트 버튼 크기 조정 */
    @media (max-width: 768px) {
        .button-group {
            gap: 5px;
        }

        .category-btn, .all-btn {
            padding: 8px 12px;
            font-size: 0.9rem;
        }

        .alert {
            padding: 8px;
            font-size: 0.9rem;
            margin-top: 10px;
        }
    }
  </style>