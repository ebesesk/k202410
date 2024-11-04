<script>
    export let value = 0;
    export let onChange = () => {};
    
    let stars = [1, 2, 3, 4, 5];
    let hoverValue = 0;
    
    function handleClick(rating) {
        value = rating;
        onChange(rating);
    }

    function handleKeyDown(event, rating) {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            handleClick(rating);
        }
    }
</script>

<div 
    class="star-rating"
    role="group"
    aria-label="별점 평가"
    on:mouseleave={() => (hoverValue = 0)}
    on:focusout={() => (hoverValue = 0)}
>
    {#each stars as star}
        <button
            type="button"
            class="star"
            class:filled={star <= (hoverValue || value)}
            on:click={() => handleClick(star)}
            on:mouseover={() => (hoverValue = star)}
            on:focus={() => (hoverValue = star)}
            on:keydown={(e) => handleKeyDown(e, star)}
            aria-label="{star}점"
            aria-pressed={star <= value}
        >
            ★
        </button>
    {/each}
</div>

<style>
    .star-rating {
        display: flex;
        gap: 2px;
    }

    .star {
        background: none;
        border: none;
        font-size: 1.5em;
        cursor: pointer;
        color: #ddd;
        transition: color 0.2s;
        padding: 0;
        line-height: 1;
    }

    .star.filled {
        color: #ffd700;
    }

    .star:hover,
    .star:focus {
        transform: scale(1.1);
        outline: none;
    }

    .star:focus-visible {
        box-shadow: 0 0 0 2px #4a90e2;
        border-radius: 4px;
    }
</style>