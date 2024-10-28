<script>
  import { onMount } from 'svelte';
  import ImageModal from './ImageModal.svelte';

  // 더미 이미지 데이터 (실제로는 API에서 받아올 것입니다)
  const images = Array.from({ length: 20 }, (_, i) => ({
    id: i + 1,
    url: `/images/manga${i + 1}.jpg`, // 실제 이미지 경로로 수정 필요
    thumbnail: `/images/manga${i + 1}-thumb.jpg`, // 썸네일 이미지 경로
    title: `Manga ${i + 1}`
  }));

  let selectedImage = null;
  let showModal = false;

  function openModal(image) {
    selectedImage = image;
    showModal = true;
  }

  function closeModal() {
    showModal = false;
    selectedImage = null;
  }
</script>

<div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
  <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
    {#each images as image}
      <div 
        class="aspect-w-3 aspect-h-4 cursor-pointer transform transition-transform hover:scale-105"
        on:click={() => openModal(image)}
      >
        <img
          src={image.thumbnail}
          alt={image.title}
          class="w-full h-full object-cover rounded-lg shadow-md hover:shadow-xl"
          loading="lazy"
        />
      </div>
    {/each}
  </div>
</div>

<ImageModal
  show={showModal}
  image={selectedImage?.url}
  onClose={closeModal}
/>