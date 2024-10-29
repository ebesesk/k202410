<script>
    import { onMount } from 'svelte';
    import { browser } from '$app/environment';
    import { goto } from '$app/navigation';

    let isAuthenticated = false;

    onMount(() => {
        if (browser) {
            const token = localStorage.getItem('accessToken');
            if (!token) {
                goto('/');
            }
            isAuthenticated = !!token;
        }
    });



    
</script>

<div class="main-container">
    <h1>메인 페이지</h1>
    {#if isAuthenticated}
        <p>환영합니다!</p>
    {:else}
        <p>로딩중...</p>
    {/if}
</div>

<style>
    .main-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
    }
</style>