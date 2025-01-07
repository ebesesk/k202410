<script>
    import { browser } from '$app/environment';
    import { WS_BASE_URL } from '$lib/config';
    import { access_token } from '$lib/stores/auth';
    
    let news = [];
    let ws;

    function connectNewsWebSocket() {
        if (!browser) return null;
        
        try {
            const wsUrl = `${WS_BASE_URL}/stock/wss/news?token=${$access_token}`;
            console.log('News WebSocket URL:', wsUrl);
            
            ws = new WebSocket(wsUrl);
            
            ws.onopen = () => {
                console.log('News WebSocket connected');
            };
            
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                console.log('Received news:', data);
                news = [data, ...news];
            };
            
            ws.onerror = (error) => {
                console.error('News WebSocket error:', error);
            };
            
            ws.onclose = () => {
                console.log('News WebSocket closed');
            };
            
            return ws;
        } catch (error) {
            console.error('News WebSocket connection error:', error);
            return null;
        }
    }

    function disconnectWebSocket() {
        if (ws) {
            ws.close();
            ws = null;
        }
    }
</script>

<div class="container">
    <div class="button-group">
        <button on:click={connectNewsWebSocket}>
            WebSocket 연결
        </button>
        <button on:click={disconnectWebSocket}>
            WebSocket 연결 해제
        </button>
    </div>

    <!-- 뉴스 목록 -->
    <div class="news-container-wrapper">
        <div class="news-section">
            <h3 class="news-header">실시간 뉴스</h3>
            <div class="news-list">
                {#each news as item, i}
                    {#if item}
                        <div class="news-item">
                            <button 
                                class="news-accordion-button"
                                on:click={() => openNewsModal(item)}
                            >
                                <span class="news-time">
                                    {item.body.time.slice(0,2)}:{item.body.time.slice(2,4)}
                                </span>
                                <span class="news-title">
                                    {item.body.title}
                                </span>
                            </button>
                        </div>
                    {/if}
                {/each}
            </div>
        </div>
    </div>
</div>

<style>
    .container {
        padding: 20px;
    }

    .button-group {
        margin-bottom: 20px;
    }

    button {
        margin-right: 10px;
        padding: 8px 16px;
        border: 1px solid #ddd;
        border-radius: 4px;
        background-color: #fff;
        cursor: pointer;
    }

    button:hover {
        background-color: #f5f5f5;
    }

    .news-container-wrapper {
        max-width: 800px;
        margin: 0 auto;
    }

    .news-section {
        border: 1px solid #ddd;
        border-radius: 4px;
        overflow: hidden;
    }

    .news-header {
        padding: 15px;
        margin: 0;
        background-color: #f8f9fa;
        border-bottom: 1px solid #ddd;
    }

    .news-list {
        max-height: 500px;
        overflow-y: auto;
    }

    .news-item {
        border-bottom: 1px solid #eee;
    }

    .news-item:last-child {
        border-bottom: none;
    }

    .news-accordion-button {
        width: 100%;
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px;
        border: none;
        background: none;
        text-align: left;
        cursor: pointer;
        transition: background-color 0.2s;
    }

    .news-accordion-button:hover {
        background-color: #f5f5f5;
    }

    .news-time {
        color: #666;
        font-size: 14px;
        white-space: nowrap;
        min-width: 45px;
    }

    .news-title {
        flex: 1;
        font-size: 14px;
        line-height: 1.4;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    @media (max-width: 768px) {
        .news-accordion-button {
            padding: 8px;
            gap: 8px;
        }

        .news-time {
            font-size: 12px;
            min-width: 40px;
        }

        .news-title {
            font-size: 13px;
        }
    }
</style>