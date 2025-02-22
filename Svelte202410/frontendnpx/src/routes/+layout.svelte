<script>
	import Navbar from '$lib/components/Navbar.svelte';
	import { navigating } from '$app/stores';
	import { access_token, username, userpoints, is_login } from '$lib/store';
	import fastapi from '$lib/api';
	import { get } from 'svelte/store';
	import { onMount } from 'svelte';
    
	// 토큰 유효성 검사 및 사용자 정보 가져오기 새로고침후 사용자정보 지워지는 문제 해결
	onMount(async () => {
        const token = get(access_token);
        if (token) {
            // JWT 토큰에서 username 추출
            try {
                // const base64Url = token.split('.')[1];
                // const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
                // const payload = JSON.parse(window.atob(base64));
                // const username = payload.sub;  // JWT의 sub 클레임에서 username 가져오기

                // 사용자 정보 가져오기
                fastapi('get', `/users/me`, null,
                    (response) => {
                        username.set(response.username);
                        userpoints.set(response.points);
                        is_login.set(true);
                        // console.log('User info refreshed:', response);
                    },
                    (error) => {
                        console.error('Failed to fetch user info:', error);
                        // 토큰이 만료되었거나 유효하지 않은 경우
                        access_token.set('');
                        username.set('');
                        userpoints.set(0);
                        is_login.set(false);
                        localStorage.clear();  // 저장된 데이터 삭제
                    }
                );
            } catch (e) {
                console.error('Error parsing token:', e);
            }
        }
    });

</script>

<div class="layout-container">
    <Navbar />
    <main>
        <slot />
    </main>
</div>

<style>
    .layout-container {
        display: flex;
        flex-direction: column;
        min-height: 100vh;
    }

    main {
        flex: 1;
        width: 100%;
        max-width: 1200px;
        margin: 60px auto 0;  /* navbar 높이만큼 상단 여백 추가 */
        box-sizing: border-box;
        position: relative;
    }

    :global(body) {
        margin: 0;
        padding: 0;
        overflow-x: hidden;
        overflow-y: visible;
        font-size: 14px;
        line-height: 1.5;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    }

    :global(.navbar) {
        position: fixed;  /* fixed로 변경 */
        top: 0;
        left: 0;
        right: 0;
        z-index: 1000;
        background: white;  /* navbar 배경색 추가 */
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);  /* 그림자 효과 추가 */
    }

    @media (max-width: 1200px) {
        main {
            padding: 0 0.1rem;
        }
    }
</style>