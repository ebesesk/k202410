<script>
    import { page } from '$app/stores';  // Svelte의 페이지 스토어 추가
    import { createEventDispatcher } from 'svelte';
    import { searchStore } from '$lib/stores/galleryStore';

    let isOpen = false;
    const dispatch = createEventDispatcher();
    
    function toggleMenu() {
        isOpen = !isOpen;
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

    $: isGalleryPage = $page.url.pathname === '/gallery';
</script>

<nav>
    <div class="nav-container">
        <div class="left-section">
            <div class="logo">
                <a href="/">K2410</a>
            </div>
            
            {#if isGalleryPage}
                <div class="search-container">
                    <input 
                        type="text" 
                        bind:value={searchTerm}
                        on:input={debounceSearch}
                        placeholder="제목 또는 태그로 검색..."
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
                <li><a href="/">홈</a></li>
                <li><a href="/gallery">갤러리</a></li>
                <li><a href="/about">소개</a></li>
                <li><a href="/contact">연락처</a></li>
            </ul>
        </div>
    </div>
</nav>


<style>
    nav {
        background-color: #2c3e50;
        padding: 1rem 0;
        position: fixed;
        width: 100%;
        top: 0;
        z-index: 1000;
    }

    .nav-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .logo a {
        color: white;
        font-size: 1.5rem;
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
        margin-left: 2rem;
    }

    .nav-links a {
        color: white;
        text-decoration: none;
        font-size: 1rem;
        transition: color 0.3s ease;
    }

    .nav-links a:hover {
        color: #3498db;
    }

    .mobile-menu {
        display: none;
        background: none;
        border: none;
        cursor: pointer;
        padding: 0.5rem;
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

    @media (max-width: 768px) {
        .mobile-menu {
            display: block;
        }

        .nav-links {
            display: none;
            position: absolute;
            top: 100%;
            left: 0;
            width: 100%;
            background-color: #2c3e50;
            flex-direction: column;
            padding: 1rem 0;
        }

        .nav-links.active {
            display: flex;
        }

        .nav-links li {
            margin: 1rem 2rem;
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
        font-size: 0.9rem;
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

    @media (max-width: 768px) {
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
    }
</style>