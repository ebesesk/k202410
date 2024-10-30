<script>
    let isOpen = false;
    
    function toggleMenu() {
        isOpen = !isOpen;
    }
</script>

<nav>
    <div class="nav-container">
        <div class="logo">
            <a href="/">K2410</a>
        </div>
        
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
        max-width: 1200px;
        margin: 0 auto;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 2rem;
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
</style>