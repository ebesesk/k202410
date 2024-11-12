<script>
    import { onMount } from 'svelte';
    import { browser } from '$app/environment';
    import { createClient } from '@supabase/supabase-js';
    import { goto } from '$app/navigation';
    import { redirect } from '@sveltejs/kit';
    import Navbar from '$lib/components/Navbar.svelte';
    import fastapi from "$lib/api"
    let isAuthenticated = false;
    // const supabase = createClient(import.meta.env.VITE_SUPABASE_URL, import.meta.env.VITE_SUPABASE_ANON_KEY);

    // JWT 토큰 검증 함수
    function checkTokenExpiration() {
        if (!browser) return false;

        const token = localStorage.getItem('accessToken');
        if (!token) return false;

        try {
            // JWT 토큰 디코딩 (Base64)
            const payload = JSON.parse(atob(token.split('.')[1]));
            const expirationTime = payload.exp * 1000; // JWT exp는 초 단위, JS는 밀리초 단위
            const currentTime = Date.now();

            // 만료 10분 전부터는 토큰 갱신 필요
            const refreshThreshold = 10 * 60 * 1000; // 10분
            
            if (currentTime >= expirationTime) {
                // 토큰이 만료된 경우
                localStorage.removeItem('accessToken');
                isAuthenticated = false;
                return false;
            } else if (expirationTime - currentTime <= refreshThreshold) {
                // 만료 10분 전이면 토큰 갱신 시도
                refreshToken();
            }

            return true;
        } catch (error) {
            console.error('Token validation error:', error);
            localStorage.removeItem('accessToken');
            isAuthenticated = false;
            return false;
        }
    }

    // 토큰 갱신 함수
    async function refreshToken() {
        try {
            const response = await fetch('https://api2410.ebesesk.synology.me/auth/refresh', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
                }
            });

            if (response.ok) {
                const result = await response.json();
                localStorage.setItem('accessToken', result.access_token);
                isAuthenticated = true;
            } else {
                throw new Error('Token refresh failed');
            }
        } catch (error) {
            console.error('Token refresh error:', error);
            localStorage.removeItem('accessToken');
            isAuthenticated = false;
            goto('/');
        }
    }

    // 주기적으로 토큰 상태 확인 (1분마다)
    let tokenCheckInterval;

    onMount(() => {
        if (browser) {
            // 초기 토큰 확인
            isAuthenticated = checkTokenExpiration();

            if (isAuthenticated) {
                goto('/about');
            }

            // 주기적 토큰 확인 설정
            tokenCheckInterval = setInterval(() => {
                isAuthenticated = checkTokenExpiration();
                if (!isAuthenticated) {
                    goto('/login');
                }
            }, 60000); // 1분마다 체크
        }

        // 컴포넌트 언마운트 시 인터벌 정리
        return () => {
            if (tokenCheckInterval) {
                clearInterval(tokenCheckInterval);
            }
        };
    });

    let id = '';
    let password = '';
    let errorMsg = '';

    async function handleLogin() {
        try {
            const formData = new URLSearchParams();
            formData.append('username', id);
            formData.append('password', password);
            console.log('Form Data:', formData.toString());
            fastapi('login', '/auth/login', formData, 
                (response) => {
                    if (response.access_token) {
                        localStorage.setItem('accessToken', response.access_token);
                        isAuthenticated = true;
                        
                        // 토큰 유효성 확인 시작
                        checkTokenExpiration();
                        goto('/about');
                    }
                },
                (error) => {
                    console.error('로그인 에러:', error);
                    errorMsg = '로그인에 실패했습니다.';
                }
            );
        } catch (error) {
            console.error('로그인 에러:', error);
            errorMsg = error.message;
        }
    }
</script>

<Navbar />

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