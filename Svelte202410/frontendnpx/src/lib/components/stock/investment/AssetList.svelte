<script>
    import { createEventDispatcher } from 'svelte';
    const dispatch = createEventDispatcher();
    import { loadAssets, investmentStore } from './js/investmentStores';
    import AssetForm from './AssetForm.svelte';
    import { onMount } from 'svelte';
    import fastapi from '$lib/api';
    
    onMount(async () => {
        await loadAssets();
    });

    let isEditing = false;
    let editingAsset = null;
    let assets = [];

    // store에서 assets 가져오기
    $: {
        assets = $investmentStore.assets;
        console.log('AssetList.svelte assets:', $investmentStore.assets);
        console.log('Current assets:', assets);
    }

    function handleEdit(asset) {
        isEditing = true;
        editingAsset = { ...asset };  // 객체 복사
        console.log('editingAsset:', editingAsset);  // 디버깅용
    }

    function handleDelete(asset) {
    // yes or no 확인 창 띄우기
    if (confirm('삭제하시겠습니까?')) {
        const url = `/stock/investments/assets/${asset.id}`;
        fastapi('delete', url, {}, 
            (json) => {
                console.log('json:', json);
                alert('삭제되었습니다.');
                // 삭제 후 자산 목록 새로고침
                loadAssets();
            },
            (error) => {
                console.error('Error:', error);
                alert('삭제 실패: ' + error.message);
            }
        );
    } else {
        // 사용자가 '아니오'를 선택한 경우
        console.log('삭제 취소');
        return;
    }
}
</script>

<div class="asset-list">
    <!-- 폼 표시 조건 수정 -->
    {#if isEditing && editingAsset}
        <AssetForm 
            {isEditing}
            {editingAsset}
        />
    {/if}

    {#if assets && assets.length > 0}
        <table>
            <thead>
                <tr>
                    <th>코드</th>
                    <th>자산명</th>
                    <th>유형</th>
                    <th>통화</th>
                    <th>작업</th>
                </tr>
            </thead>
            <tbody>
                {#each assets as asset}
                    <tr>
                        <td>{asset.code}</td>
                        <td>{asset.name}</td>
                        <td>{asset.type}</td>
                        <td>{asset.currency}</td>
                        <td>
                            <button 
                                class="btn-edit"
                                on:click={() => handleEdit(asset)}
                            >
                                수정
                            </button>
                            <button 
                                class="btn-delete"
                                on:click={() => handleDelete(asset)}
                            >
                                삭제
                            </button>
                        </td>
                    </tr>
                {/each}
            </tbody>
        </table>
    {:else}
        <p>등록된 자산이 없습니다.</p>
    {/if}
</div>

<style>
    .asset-list {
        width: 100%;
        overflow-x: auto;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 1rem;
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

    .btn-edit,
    .btn-delete {
        padding: 0.1rem 0.2rem;
        background: #4CAF50;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 0.5rem;
    }

    .btn-edit:hover {
        background: #45a049;
    }

    .btn-delete:hover {
        background: #f44336;
    }
</style>