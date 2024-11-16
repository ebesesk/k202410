<script>
    import { onMount } from 'svelte';
    import { slide } from 'svelte/transition';
    import fastapi from '$lib/api';

    let questions = [];
    let total = 0;
    let page = 1;
    let size = 10;
    let keyword = '';
    let isLoading = false;
    let expandedId = null;
    let showModal = false;
    let showCreateModal = false;
    let editingQuestion = null;
    let editSubject = '';
    let editContent = '';
    let newSubject = '';
    let newContent = '';

    // 본문 토글
    function toggleContent(questionId) {
        expandedId = expandedId === questionId ? null : questionId;
    }

    // 질문 목록 조회
    async function fetchQuestions(resetPage = false) {
        if (resetPage) page = 1;
        isLoading = true;

        const params = {
            page: page - 1,
            size: size,
            keyword: keyword
        };

        fastapi('get', '/question/list', params,
            (json) => {
                questions = json.question_list;
                total = json.total;
                isLoading = false;
            },
            (err) => {
                console.error('질문 목록 조회 실패:', err);
                isLoading = false;
            }
        );
    }

    // 질문 삭제
    async function deleteQuestion(id) {
        if (!confirm('정말로 삭제하시겠습니까?')) return;

        const params = { question_id: id };
        fastapi('delete', '/question/delete', params,
            () => {
                fetchQuestions();
                alert('삭제되었습니다.');
            },
            (err) => {
                console.error('삭제 실패:', err);
                alert('삭제에 실패했습니다.');
            }
        );
    }

    // 질문 수정
    async function handleEdit() {
        if (!editSubject.trim() || !editContent.trim()) {
            alert('제목과 내용을 모두 입력해주세요.');
            return;
        }

        const params = {
            question_id: editingQuestion.id,
            subject: editSubject,
            content: editContent
        };

        fastapi('put', '/question/update', params,
            () => {
                fetchQuestions();
                closeModal();
                alert('수정되었습니다.');
            },
            (err) => {
                console.error('수정 실패:', err);
                alert('수정에 실패했습니다.');
            }
        );
    }

    // 새 질문 작성
    async function handleCreate() {
        if (!newSubject.trim() || !newContent.trim()) {
            alert('제목과 내용을 모두 입력해주세요.');
            return;
        }

        const params = {
            subject: newSubject,
            content: newContent
        };

        fastapi('post', '/question/create', params,
            () => {
                fetchQuestions();
                closeCreateModal();
                alert('작성되었습니다.');
            },
            (err) => {
                console.error('작성 실패:', err);
                alert('작성에 실패했습니다.');
            }
        );
    }


        // 페이지네이션 처리
    function changePage(newPage) {
        page = newPage;
        expandedId = null; // 페이지 변경시 펼쳐진 내용 접기
        fetchQuestions(); // API 호출로 해당 페이지 데이터 가져오기
    }

    // 모달 관련 함수들
    function openEditModal(question) {
        editingQuestion = question;
        editSubject = question.subject;
        editContent = question.content;
        showModal = true;
    }

    function closeModal() {
        showModal = false;
        editingQuestion = null;
        editSubject = '';
        editContent = '';
    }

    function openCreateModal() {
        showCreateModal = true;
    }

    function closeCreateModal() {
        showCreateModal = false;
        newSubject = '';
        newContent = '';
    }

    $: totalPages = Math.ceil(total / size);

    onMount(() => {
        fetchQuestions();
    });
</script>

<!-- 템플릿 부분 -->
<div class="question-list">
    <!-- 검색과 작성 버튼 -->
    <div class="controls">
        <div class="search-box">
            <input 
                type="text"
                bind:value={keyword}
                placeholder="검색어를 입력하세요"
                on:keydown={(e) => e.key === 'Enter' && fetchQuestions(true)}
            />
            <button class="search-button" on:click={() => fetchQuestions(true)}>
                검색
            </button>
        </div>
        <button class="create-button" on:click={openCreateModal}>
            질문 작성
        </button>
    </div>

    <!-- 로딩 상태 -->
    {#if isLoading}
        <div class="loading">
            <div class="loading-spinner"></div>
        </div>
    {:else}
        <!-- 질문 목록 -->
        <div class="questions">
            {#each questions as question (question.id)}
                <div class="question-item">
                    <button 
                        class="question-title"
                        on:click={() => toggleContent(question.id)}
                        class:expanded={expandedId === question.id}
                    >
                        <span class="title-text">{question.subject}</span>
                        <span class="arrow" class:expanded={expandedId === question.id}>▼</span>
                    </button>
                    
                    <div class="meta-info">
                        <span>작성자: {question.user?.username || '익명'}</span>
                        <span>작성일: {new Date(question.create_date).toLocaleString()}</span>
                        {#if question.modify_date}
                            <span>수정일: {new Date(question.modify_date).toLocaleString()}</span>
                        {/if}
                        <span>답변 {question.answers?.length || 0}개</span>
                    </div>

                    {#if expandedId === question.id}
                        <div class="question-content" transition:slide>
                            <div class="content-text">
                                {question.content}
                            </div>
                            
                            {#if question.answers?.length > 0}
                                <div class="answers">
                                    <h4>답변 목록</h4>
                                    {#each question.answers as answer}
                                        <div class="answer-item">
                                            <div class="answer-content">{answer.content}</div>
                                            <div class="answer-meta">
                                                <span>{answer.user?.username || '익명'}</span>
                                                <span>{new Date(answer.create_date).toLocaleString()}</span>
                                            </div>
                                        </div>
                                    {/each}
                                </div>
                            {/if}

                            <div class="action-buttons">
                                <button class="edit-button" on:click={() => openEditModal(question)}>
                                    수정
                                </button>
                                <button class="delete-button" on:click={() => deleteQuestion(question.id)}>
                                    삭제
                                </button>
                            </div>
                        </div>
                    {/if}
                </div>
            {/each}
        </div>

        <!-- 페이지네이션 -->
        <div class="pagination">
            <button 
                disabled={page === 1}
                on:click={() => changePage(page - 1)} 
            >
                이전
            </button>
            {#each Array(totalPages) as _, i}
                <button
                    class:active={page === i + 1}
                    on:click={() => changePage(i + 1)} 
                >
                    {i + 1}
                </button>
            {/each}
            <button 
                disabled={page === totalPages}
                on:click={() => changePage(page + 1)} 
            >
                다음
            </button>
        </div>
    {/if}
</div>

<!-- 수정 모달 -->
{#if showModal}
    <div class="modal-backdrop">
        <div class="modal" >
            <div class="modal-header">
                <h2>질문 수정</h2>
                <button type="button" on:click={closeModal} on:keydown={(e) => e.key === 'Enter' && closeModal()}>
                    ×
                </button>
            </div>
            <div class="modal-body">
                <div class="form-group">
                    <label for="edit-subject">제목</label>
                    <input
                        id="edit-subject"
                        type="text"
                        bind:value={editSubject}
                        placeholder="제목을 입력하세요"
                    />
                </div>
                <div class="form-group">
                    <label for="edit-content">내용</label>
                    <textarea
                        id="edit-content"
                        bind:value={editContent}
                        placeholder="내용을 입력하세요"
                        rows="5"
                    ></textarea>
                </div>
            </div>
            <div class="modal-footer">
                <button class="cancel-button" on:click={closeModal} tabindex="0">취소</button>
                <button class="save-button" on:click={handleEdit} tabindex="0">저장</button>
            </div>
        </div>
    </div>
{/if}

<!-- 작성 모달 -->
{#if showCreateModal}
    <div class="modal-backdrop">
        <div class="modal">
            <div class="modal-header">
                <h2>새 질문 작성</h2>
                <button class="close-button" on:click={closeCreateModal}>×</button>
            </div>
            <div class="modal-body">
                <div class="form-group">
                    <label for="new-subject">제목</label>
                    <input
                        id="new-subject"
                        type="text"
                        bind:value={newSubject}
                        placeholder="제목을 입력하세요"
                    />
                </div>
                <div class="form-group">
                    <label for="new-content">내용</label>
                    <textarea
                        id="new-content"
                        bind:value={newContent}
                        placeholder="내용을 입력하세요"
                        rows="5"
                    ></textarea>
                </div>
            </div>
            <div class="modal-footer">
                <button class="cancel-button" on:click={closeCreateModal}>취소</button>
                <button class="save-button" on:click={handleCreate}>작성</button>
            </div>
        </div>
    </div>
{/if}

<style>
    .question-list {
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
    }

    .controls {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
    }

    .search-box {
        display: flex;
        gap: 10px;
    }

    .search-box input {
        width: 300px;
        padding: 8px 12px;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 14px;
    }

    button {
        padding: 8px 16px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
        transition: background-color 0.2s;
    }

    button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    .search-button {
        background-color: #4a90e2;
        color: white;
    }

    .search-button:hover {
        background-color: #357abd;
    }

    .create-button {
        background-color: #2ecc71;
        color: white;
    }

    .create-button:hover {
        background-color: #27ae60;
    }

    .questions {
        margin-bottom: 20px;
    }

    .question-item {
        border: 1px solid #ddd;
        border-radius: 4px;
        margin-bottom: 10px;
        background-color: white;
    }

    .question-title {
        width: 100%;
        padding: 15px;
        text-align: left;
        background: none;
        border: none;
        display: flex;
        justify-content: space-between;
        align-items: center;
        cursor: pointer;
    }

    .question-title:hover {
        background-color: #f8f9fa;
    }

    .title-text {
        font-size: 16px;
        font-weight: 500;
    }

    .arrow {
        font-size: 12px;
        transition: transform 0.2s;
    }

    .arrow.expanded {
        transform: rotate(180deg);
    }

    .meta-info {
        padding: 0 15px 15px;
        font-size: 14px;
        color: #666;
    }

    .meta-info span {
        margin-right: 15px;
    }

    .question-content {
        padding: 15px;
        border-top: 1px solid #eee;
    }

    .content-text {
        white-space: pre-wrap;
        line-height: 1.5;
        margin-bottom: 20px;
    }

    .answers {
        margin-top: 20px;
        padding-top: 20px;
        border-top: 1px solid #eee;
    }

    .answers h4 {
        margin-bottom: 15px;
        font-size: 16px;
        font-weight: 500;
    }

    .answer-item {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 4px;
        margin-bottom: 10px;
    }

    .answer-content {
        margin-bottom: 10px;
        line-height: 1.5;
    }

    .answer-meta {
        font-size: 13px;
        color: #666;
    }

    .answer-meta span {
        margin-right: 15px;
    }

    .action-buttons {
        margin-top: 15px;
        display: flex;
        gap: 10px;
    }

    .edit-button {
        background-color: #4a90e2;
        color: white;
    }

    .edit-button:hover {
        background-color: #357abd;
    }

    .delete-button {
        background-color: #e74c3c;
        color: white;
    }

    .delete-button:hover {
        background-color: #c0392b;
    }

    .pagination {
        display: flex;
        justify-content: center;
        gap: 5px;
        margin-top: 20px;
    }

    .pagination button {
        min-width: 40px;
        height: 40px;
        padding: 0 10px;
        border: 1px solid #ddd;
        background-color: white;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .pagination button.active {
        background-color: #4a90e2;
        color: white;
        border-color: #4a90e2;
    }

    .pagination button:not(:disabled):hover {
        background-color: #f8f9fa;
    }

    /* 로딩 스피너 */
    .loading {
        text-align: center;
        padding: 40px 0;
    }

    .loading-spinner {
        display: inline-block;
        width: 40px;
        height: 40px;
        border: 3px solid #f3f3f3;
        border-radius: 50%;
        border-top: 3px solid #4a90e2;
        animation: spin 1s linear infinite;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    /* 모달 스타일 */
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
        padding: 1rem;
    }

    .modal {
        background: white;
        border-radius: 12px;
        width: 90%;
        max-width: 500px;  /* 최대 너비 줄임 */
        max-height: 85vh;  /* 높이 조정 */
        overflow-y: auto;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        animation: modal-slide-in 0.3s ease-out;
    }

    @keyframes modal-slide-in {
        from {
            transform: translateY(20px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }

    .modal-header {
        padding: 1.5rem;
        border-bottom: 1px solid #eee;
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #f8f9fa;
        border-radius: 12px 12px 0 0;
    }

    .modal-header h2 {
        margin: 0;
        font-size: 1.1rem;  /* 제목 폰트 크기 줄임 */
        color: #333;
    }

    .modal-header button {
        background: none;
        border: none;
        font-size: 1.5rem;
        color: #666;
        cursor: pointer;
        padding: 0.5rem;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: background-color 0.2s;
    }

    .modal-header button:hover {
        background-color: #e9ecef;
    }

    .modal-body {
        padding: 1.5rem;
    }

    .form-group {
        margin-bottom: 1.5rem;
    }

    .form-group label {
        display: block;
        margin-bottom: 0.4rem;
        font-weight: 500;
        color: #333;
        font-size: 0.9rem;  /* 라벨 폰트 크기 줄임 */
    }

    .form-group input,
    .form-group textarea {
        width: 100%;
        padding: 0.6rem 0.8rem;  /* 패딩 줄임 */
        border: 2px solid #e9ecef;
        border-radius: 8px;
        font-size: 0.9rem;  /* 입력 폰트 크기 줄임 */
        transition: border-color 0.2s;
        background-color: #fff;
    }

    .form-group input:focus,
    .form-group textarea:focus {
        outline: none;
        border-color: #4a90e2;
        box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.1);
    }

    .form-group textarea {
        min-height: 100px;  /* 텍스트영역 높이 줄임 */
        resize: vertical;
    }

    .modal-footer {
        padding: 1.5rem;
        border-top: 1px solid #eee;
        display: flex;
        justify-content: flex-end;
        gap: 1rem;
        background-color: #f8f9fa;
        border-radius: 0 0 12px 12px;
    }

    .modal-footer button {
        padding: 0.6rem 1.2rem;  /* 버튼 패딩 줄임 */
        border-radius: 8px;
        font-size: 0.9rem;  /* 버튼 폰트 크기 줄임 */
        font-weight: 500;
    }

    .cancel-button {
        background-color: #fff;
        border: 2px solid #e9ecef;
        color: #666;
    }

    .cancel-button:hover {
        background-color: #f8f9fa;
        border-color: #ddd;
    }

    .save-button {
        background-color: #4a90e2;
        border: none;
        color: white;
    }

    .save-button:hover {
        background-color: #357abd;
    }

    /* 모바일 대응 스타일 */
    @media (max-width: 768px) {
        .modal {
            width: 95%;
            max-height: 80vh;  /* 모바일에서 높이 더 줄임 */
        }

        .modal-header {
            padding: 0.8rem;  /* 패딩 줄임 */
        }

        .modal-body {
            padding: 0.8rem;
        }

        .modal-footer {
            padding: 0.8rem;
        }

        .modal-footer button {
            width: 100%;
            padding: 0.7rem;
        }

        .form-group {
            margin-bottom: 1rem;  /* 간격 줄임 */
        }
    }

    /* 스크롤바 스타일링 */
    .modal::-webkit-scrollbar {
        width: 8px;
    }

    .modal::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 4px;
    }

    .modal::-webkit-scrollbar-thumb {
        background: #ccc;
        border-radius: 4px;
    }

    .modal::-webkit-scrollbar-thumb:hover {
        background: #999;
    }
</style>