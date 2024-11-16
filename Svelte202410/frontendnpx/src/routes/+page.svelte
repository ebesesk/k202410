<script>
    import { onMount } from 'svelte';
    import { access_token, username, userpoints, is_login } from "$lib/store"
    import { browser } from '$app/environment';
    import { createClient } from '@supabase/supabase-js';
    import { goto } from '$app/navigation';
    import { get } from 'svelte/store'; 
    import { redirect } from '@sveltejs/kit';
    import Navbar from '$lib/components/Navbar.svelte';
    import fastapi from "$lib/api"
    let isAuthenticated = false;
    // const supabase = createClient(import.meta.env.VITE_SUPABASE_URL, import.meta.env.VITE_SUPABASE_ANON_KEY);

    // JWT 토큰 검증 함수
    function checkTokenExpiration() {
        if (!browser) return false;

        const token = get(access_token);
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
                access_token.set('');
                username.set('');
                userpoints.set(0);
                is_login.set(false);
                return false;
            } else if (expirationTime - currentTime <= refreshThreshold) {
                // 만료 10분 전이면 토큰 갱신 시도
                refreshToken();
            }

            return true;
        } catch (error) {
            console.error('Token validation error:', error);
            access_token.set('');
            username.set('');
            userpoints.set(0);
            is_login.set(false);
            return false;
        }
    }

    // 토큰 갱신 함수
    async function refreshToken() {
        try {
            const response = await fetch('https://api2410.ebesesk.synology.me/auth/refresh', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${get(access_token)}`
                }
            });

            if (response.ok) {
                const result = await response.json();
                access_token.set(result.access_token);
                username.set(result.username);
                userpoints.set(result.userpoints);
                is_login.set(true);
                // console.log('result', result)
            } else {
                throw new Error('Token refresh failed');
            }
        } catch (error) {
            console.error('Token refresh error:', error);
            access_token.set('');
            username.set('');
            userpoints.set(0);
            is_login.set(false);
            goto('/');
        }
    }

    // 주기적으로 토큰 상태 확인 (1분마다)
    let tokenCheckInterval;

    onMount(() => {
        if (browser) {
            // 초기 토큰 확인
            $is_login = checkTokenExpiration();

            if ($is_login) {
                goto('/about');
            }

            // 주기적 토큰 확인 설정
            tokenCheckInterval = setInterval(() => {
                $is_login = checkTokenExpiration();
                if (!$is_login) {
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
            
            fastapi('login', '/auth/login', formData, 
                async (response) => {
                    if (response.access_token) {
                        access_token.set(response.access_token);
                        username.set(response.username);
                        userpoints.set(response.userpoints);
                        is_login.set(true);
                        
                        localStorage.setItem('accessToken', response.access_token);
                        localStorage.setItem('username', response.username);
                        localStorage.setItem('userpoints', response.userpoints);
                        
                        await goto('/about');  // 명시적으로 /about으로 이동
                    }
                },
                (error) => {
                    console.error('로그인 에러:', error);
                    errorMsg = '로그인에 실패했습니다. 아이디와 비밀번호를 확인해주세요.';
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