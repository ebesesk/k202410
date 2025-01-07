import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		hmr: {
		  overlay: false  // HMR 경고 끄기
		}
	  },
	  optimizeDeps: {
		include: ['lightweight-charts']  // 사전 번들링에 포함
	  },
	  build: {
		rollupOptions: {
		  output: {
			manualChunks: {
			  'lightweight-charts': ['lightweight-charts']
			}
		  }
		}
	  }
});


