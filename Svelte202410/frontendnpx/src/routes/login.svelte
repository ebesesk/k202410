<script>
    import { onMount } from 'svelte';
    import { createClient } from '@supabase/supabase-js';

    const supabase = createClient(import.meta.env.VITE_SUPABASE_URL, import.meta.env.VITE_SUPABASE_ANON_KEY);
    
    // 폼 데이터를 저장할 변수들
    let email = '';
    let password = '';
    let errorMsg = '';

    // 로그인 처리 함수
    async function handleLogin() {
        try {
            const { data, error } = await supabase.auth.signInWithPassword({
                email,
                password
            });
            
            if (error) throw error;
            // 로그인 성공 시 리다이렉트 또는 다른 처리
            window.location.href = '/';
        } catch (error) {
            errorMsg = error.message;
        }
    }
</script>

<div class="login-container">
    <h1>Login</h1>
    
    <form on:submit|preventDefault={handleLogin}>
        <div class="form-group">
            <label for="email">이메일</label>
            <input 
                type="email" 
                id="email"
                bind:value={email}
                required
            />
        </div>

        <div class="form-group">
            <label for="password">비밀번호</label>
            <input 
                type="password" 
                id="password"
                bind:value={password}
                required
            />
        </div>

        {#if errorMsg}
            <p class="error">{errorMsg}</p>
        {/if}

        <button type="submit">로그인</button>
    </form>
</div>

<style>
    .login-container {
        /* max-width: 400px; */
        /* margin: 0 auto; */
        padding: 90px 0 0 0;
        margin: 100px 0 0 0;
        align-items: center;
        justify-content: center;
    }

    .form-group {
        margin-bottom: 15px;
    }

    label {
        display: block;
        margin-bottom: 5px;
    }

    input {
        width: 100%;
        padding: 8px;
        border: 1px solid #ddd;
        border-radius: 4px;
    }

    button {
        width: 100%;
        padding: 10px;
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
    }

    button:hover {
        background-color: #45a049;
    }

    .error {
        color: red;
        margin-top: 10px;
    }
</style>
    