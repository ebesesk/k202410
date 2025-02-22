<!-- src/components/AccountForm.svelte -->
<script>
    import { onMount } from 'svelte';
    import fastapi from '$lib/api';


//   import fastapi from '$lib/api';

  let message = '';
  let messageType = 'success';
  let loading = false;

  const categories = [
      { id: 'common', name: '공통 계정' },
      { id: 'stocks', name: '주식 계정' },
      { id: 'crypto', name: '암호화폐 계정' }
  ];
  const API_BASE_URL = import.meta.env.VITE_API_URL?.replace('http://', 'https://') || 'https://api2410.ebesesk.synology.me';  
  async function initializeCategory(category) {
		loading = true;
		const url = '/stock/investments/accounts/initialize/'+category;
		try {
				fastapi('post', url, {}, (json) => {
						console.log('/accounts/initialize:', json);
					console.log('category:', category);
					message = `${category} 계정이 성공적으로 초기화되었습니다.`;
					messageType = 'success';
					loading = false;
				}, () => {
					// 에러 콜백
					message = '초기화 중 오류가 발생했습니다.';
					messageType = 'error';
					loading = false;
				});
		} catch (error) {
				console.error('초기화 실패:', error);
				message = '초기화 중 오류가 발생했습니다.';
				messageType = 'error';
				loading = false;
		}
	}

	async function initializeAllAccounts() {
		loading = true;
		const url = '/stock/investments/accounts/initialize-all';
		try {
				fastapi('post', url, {}, (json) => {
						console.log('/accounts/initialize-all:', json);
						message = `모든 계정이 성공적으로 초기화되었습니다.`;
						messageType = 'success';
						loading = false;
				}, () => {
						// 에러 콜백
						message = '초기화 중 오류가 발생했습니다.';
						messageType = 'error';
						loading = false;
				});
		} catch (error) {
				console.error('초기화 실패:', error);
				message = '초기화 중 오류가 발생했습니다.';
				messageType = 'error';
				loading = false;
		}
	}

</script>

<div class="account-initialize">
  <h2>계정 초기화</h2>
  
  <div class="button-group">
      {#each categories as category}
          <button 
              class="category-btn"
              on:click={() => initializeCategory(category.id)}
              disabled={loading}
          >
              {category.name} 초기화
          </button>
      {/each}
      
      <button 
          class="all-btn"
          on:click={initializeAllAccounts}
          disabled={loading}
      >
          전체 계정 초기화
      </button>
  </div>

  {#if loading}
      <div class="loading">초기화 중...</div>
  {/if}

  {#if message}
      <div class="alert {messageType}">
          {message}
      </div>
  {/if}
</div>




  




  <style>
    .account-initialize {
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
    }

    .button-group {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 10px;
        margin: 20px 0;
    }

    button {
        padding: 12px 20px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-weight: bold;
        transition: all 0.3s ease;
    }

    button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    .category-btn {
        background-color: #4CAF50;
        color: white;
    }

    .all-btn {
        background-color: #2196F3;
        color: white;
        grid-column: 1 / -1;
    }

    .loading {
        text-align: center;
        margin: 10px 0;
        color: #666;
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

    /* 계정 추가 버튼 그룹 */
    .setup.input-container {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    .input-group {
        display: flex;
        gap: 0.5rem;
    }


    .input-field {
        height: 15px;  /* 높이 축소 */
        font-size: 10px;  /* 폰트 크기 축소 */
        padding: 0 4px;  /* 패딩 축소 */
        width: 80px;
    }

    .key-input {
        width: 80px;  /* 키 입력 필드 너비 */
        height: 15px;
        font-size: 10px;
        padding: 0 4px;
        width: 80px;
    }
    .action-button {
        flex: 1;
        padding: 8px 12px;
        font-size: 13px;
        border: none;
        border-radius: 4px;
        background-color: #f0f0f0;
        color: #333;
        cursor: pointer;
        transition: all 0.2s;
        min-width: 0;
        white-space: nowrap;
    }

    .active-wss {
        background-color: #4CAF50;
        color: white;
    }

    .action-button:hover {
        opacity: 0.9;
    }

    .action-button:disabled {
        background-color: #ccc;
        cursor: not-allowed;
    }

    .clear-button {
        position: absolute;
        right: 5px;
        background: none;
        border: none;
        color: #666;
        font-size: 18px;
        padding: 0 8px;
    }
    .setup.input-container {
        display: flex;
        flex-direction: column;  /* 수직 배열 */
        gap: 0.3rem;  /* 요소 간 간격 */
        width: 100%;
        padding: 0.3rem;
    }

    .setup.input-group {
        display: flex;
        flex-direction: row;  /* 입력 필드는 가로로 유지 */
        gap: 0.3rem;
        width: 100%;
    }

    .setup.button-group {
        display: flex;
        flex-direction: row;
        gap: 0.3rem;
        width: 100%;
    }
    /* 테이블 스크롤 처리 */
    .transaction-list {
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
    }
    @media (max-width: 768px) {
        

        .transaction-form, .summary-card {
            padding: 12px;
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