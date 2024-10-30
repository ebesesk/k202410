<script>
	import Navbar from '$lib/components/Navbar.svelte';
	import { navigating } from '$app/stores';
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