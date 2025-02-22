<script>
    import { page } from '$app/stores';  // Svelte의 페이지 스토어 추가
    import { onMount } from 'svelte';
    import { searchStore } from '$lib/stores/galleryStore';
    import fastapi from '$lib/api'
    import { goto } from '$app/navigation';
    import { access_token, username, userpoints } from '$lib/store'
    import { get } from 'svelte/store'; 
    let isOpen = false;
    // import { clearLoginData } from '$lib/store';
    // const dispatch = createEventDispatcher();


    

    function toggleMenu() {
        isOpen = !isOpen;
    }

    function closeMenu() {
        isOpen = false;
    }
    
    function handleSearch(event) {
        dispatch('search', { term: searchTerm });
    }

    
    let searchTerm = '';
    let searchTimeout;
    let isGalleryPage = true; // 또는 현재 페이지 확인 로직

    function debounceSearch() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            searchStore.set(searchTerm);
        }, 300);
    }

    function handleLogout() {
        fastapi('post', '/auth/logout', {}, 
            (json) => {
                // 로그아웃 성공
                access_token.set('');
                username.set('');
                userpoints.set(0);
                is_login.set(false);
                localStorage.removeItem('accessToken');
                localStorage.removeItem('username');
                localStorage.removeItem('userpoints');
                goto('/');
            },
            (err) => {
                // 로그아웃 실패
                console.error('로그아웃 실패:', err);
                // 실패해도 로컬 상태는 초기화
                access_token.set('');
                username.set('');
                userpoints.set(0);
                is_login.set(false);
                localStorage.clear();
                goto('/');
            }
        );
    }

    let prevScrollPos = 0;
    let visible = true;
    
    onMount(() => {
        window.addEventListener('scroll', handleScroll);
        return () => {
            window.removeEventListener('scroll', handleScroll);
        };
    });

    function handleScroll() {
        const currentScrollPos = window.pageYOffset;
        visible = prevScrollPos > currentScrollPos || currentScrollPos < 10;
        prevScrollPos = currentScrollPos;
    }
    $: isGalleryPage = $page.url.pathname === '/gallery';
</script>
<div class="navbar-wrapper">
<nav>
    <div class="nav-container">
        <div class="left-section">
            <div class="logo">
                <a href="/" on:click={closeMenu}>K2410</a>
                <button class="logout-button" on:click={handleLogout}>{$username}:{$userpoints} logout</button>
            </div>
            
            {#if isGalleryPage}
                <div class="search-container">
                    <input 
                        type="text" 
                        bind:value={searchTerm}
                        on:input={debounceSearch}
                        on:search={handleSearch}
                        placeholder="제목 또는 태그로 검색... ({$searchStore || ''})"
                        class="search-input"
                    />
                </div>
            {/if}
        </div>

        <div class="right-section">
            <button class="mobile-menu" on:click={toggleMenu} aria-label="메뉴 버튼">
                <span class="hamburger"></span>
            </button>

            <ul class={`nav-links ${isOpen ? 'active' : ''}`}>
                <li><a class="nav-link" href="/" on:click={closeMenu}>홈</a></li>
                <li><a class="nav-link" href="https://asil.kr/asil/index.jsp" target="_blank" rel="noopener noreferrer" on:click={closeMenu}>아실</a></li>
                <li><a class="nav-link" href="/gallery" on:click={closeMenu}>갤러리</a></li>
                <li><a class="nav-link" href="/realestate" on:click={closeMenu}>부동산</a></li>
                <li><a class="nav-link" href="/stock" on:click={closeMenu}>주식</a></li>
                <li><a class="nav-link" href="/movie" on:click={closeMenu}>movie</a></li>
                <li><a class="nav-link" href="/about" on:click={closeMenu}>소개</a></li>
                <li><a class="nav-link" href="/users" on:click={closeMenu}>유저</a></li>
                <li><a class="nav-link" href="/_test" on:click={closeMenu}>test</a></li>
            </ul>
        </div>
    </div>
</nav>
</div>

<style>
    .navbar-wrapper {
        position: absolute;
        width: 100%;
        z-index: 100;        /* 더 높은 z-index로 설정 */
        transition: transform 0.2s ease-out;
    }
    nav {
        background-color: #2c3e50;
        padding: 0 0 0 0;
        width: 100%;
        pointer-events: auto;  /* nav 자체는 클릭 가능하도록 */
        /* height: 50px; */
        z-index: 30;
        /* 가운데 정렬 */
        margin: 0 auto;
    }
    .logout-button {
        text-decoration: none;
        color: #fff;  /* 텍스트 색상을 흰색으로 */
        padding: 8px 16px;
        background-color: #2c3e50;  /* 기본 배경색 */
        border: none;  /* 테두리 제거 */
        border-radius: 0;  /* 모서리 둥글게 제거 */
        transition: background-color 0.2s;  /* 부드러운 색상 전환 */
        }
    .nav-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 95%;
    }

    .logo a {
        color: white;
        font-size: 1rem;
        font-weight: bold;
        text-decoration: none;
    }

    .nav-links {
        display: flex;
        list-style: none;
        margin: 0;
        padding: 0;
    }

    .nav-links li {
        margin-left: 1rem;
    }

    .nav-links a {
        color: white;
        text-decoration: none;
        font-size: 9px;
        transition: color 0.3s ease;
    }

    .nav-links a:hover {
        color: #3498db;
    }
    .nav-links.active {
        z-index: 11;  /* navbar보다 위에 표시 */
    }
    .mobile-menu {
        display: none;
        background: none;
        border: none;
        cursor: pointer;
        padding: 5px;
    }

    .hamburger {
        display: block;
        width: 25px;
        height: 3px;
        background: white;
        position: relative;
        transition: all 0.3s ease-in-out;
        
    }

    .hamburger::before,
    .hamburger::after {
        content: '';
        position: absolute;
        width: 25px;
        height: 3px;
        background: white;
        transition: all 0.3s ease-in-out;
    }

    .hamburger::before {
        transform: translateY(-8px);
    }

    .hamburger::after {
        transform: translateY(8px);
    }
    .right-section {
        /* display: flex; */
        /* justify-content: center; */
        align-items: center;
        /* margin-right: 10px; */
    }
   
   
    @media (max-width: 768px) {
        .mobile-menu {
            display: block;
        }

        .nav-links {
            display: none;
            position: absolute;
            top: 100%;
            right: 0;  /* left: 0 대신 right: 0 사용 */
            width: auto;  /* 전체 너비 대신 자동 너비 */
            min-width: 150px;  /* 최소 너비 설정 */
            background-color: #2c3e50;
            flex-direction: column;
            padding: 0.2rem 0;
            border-radius: 0 0 0 4px;  /* 왼쪽 아래 모서리만 둥글게 */
        }


        .nav-links.active {
            display: flex;
        }
        .nav-links li {
            margin: 0.3rem 1rem;
            text-align: right;  /* 텍스트 오른쪽 정렬 */
        }
        .nav-link {
            padding: 0.2rem 1rem;  /* 오른쪽 패딩 추가 */
            display: block;
        }

    }
    .left-section {
        display: flex;
        align-items: center;
        gap: 2rem;
    }

    .search-container {
        display: flex;
        align-items: center;
    }

    .search-input {
        padding: 0.5rem 1rem;
        border: none;
        border-radius: 4px;
        background: rgba(255, 255, 255, 0.1);
        color: white;
        font-size: 9px;
        width: 300px;
        transition: all 0.3s ease;
    }

    .search-input::placeholder {
        color: rgba(255, 255, 255, 0.6);
    }

    .search-input:focus {
        background: rgba(255, 255, 255, 0.2);
        outline: none;
    }
    
    .left-section {
            flex-direction: column;
            align-items: flex-start;
            gap: 1rem;
        }

        .search-container {
            width: 100%;
            margin-bottom: 0.5rem;
        }

        .search-input {
            width: 100%;
            max-width: none;
        }
    
</style>