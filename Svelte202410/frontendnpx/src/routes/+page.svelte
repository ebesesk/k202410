<script>
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';
	import { createClient } from '@supabase/supabase-js';
	import { goto } from '$app/navigation';  // 이 줄을 상단에 추가

	let isAuthenticated = false;
	const supabase = createClient(import.meta.env.VITE_SUPABASE_URL, import.meta.env.VITE_SUPABASE_ANON_KEY);
	onMount(() => {
        // 브라우저 환경에서만 localStorage 접근
        if (browser) {
            const token = localStorage.getItem('accessToken');
            isAuthenticated = !!token;
        }
    });
	// 폼 데이터를 저장할 변수들
	let id = '';
	let password = '';
	let errorMsg = '';

	// 로그인 처리 함수
	// ... existing code ...

async function handleLogin() {
    try {
        const formData = new URLSearchParams();
        formData.append('username', id);
        formData.append('password', password);

        const response = await fetch('https://api2410.ebesesk.synology.me/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: formData
        });

        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.detail || '로그인 실패');
        }

        // 로그인 성공 처리
        const accessToken = result.access_token;
        localStorage.setItem('accessToken', accessToken);
        isAuthenticated = true;
        console.log('accessToken: ', accessToken);
        // 로그인 성공 후 리다이렉트
        // window.location.href = '/';
			  // window.location.href 대신 goto 사용
				await goto('/main');
    } catch (error) {
        console.error('로그인 에러:', error);
        errorMsg = error.message;
    }
}

// ... existing code ...
</script>

<div class="login-container">
    <h1>Login</h1>
    
    <form on:submit|preventDefault={handleLogin}>
        <div class="form-group">
            <label for="id">아이디</label>
            <input 
                type="text" 
                id="id"
                bind:value={id}
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
        max-width: 400px;
        margin: 0 auto;
        padding: 20px;
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
    