<script>
    import { onMount } from 'svelte';
    import { browser } from '$app/environment';
    import { goto } from '$app/navigation';
    import { access_token, is_login } from '$lib/store';
    import { get } from 'svelte/store';
    
    let isAuthenticated = $is_login;
    onMount(() => {
        if (browser) {
            const token = get(access_token);
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