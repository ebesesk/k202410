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

<Navbar />
<main>
	<slot />  <!-- 여기에 page 컨텐츠가 들어감 -->
</main>

<style>
	main {
			margin-top: 4rem;
	}
</style>