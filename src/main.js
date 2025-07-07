import Masonry from 'masonry-layout';
import imagesLoaded from 'imagesloaded';

document.addEventListener('DOMContentLoaded', () => {

  const gallery = document.querySelector('.gallery');
  const scrollTrigger = document.getElementById('scroll-trigger');

  const imageModules = import.meta.glob('./assets/fantasy_images/*.{jpg,jpeg,png}');
  const imageLoaders = Object.values(imageModules);

  let currentIndex = 0;
  const batchSize = 30;
  let msnry;
  let isLoading = false;

  async function loadMoreImages() {
    if (isLoading || currentIndex >= imageLoaders.length) {
      return;
    }
    
    isLoading = true;

    const nextImageLoaders = imageLoaders.slice(currentIndex, currentIndex + batchSize);

    if (!msnry) {
      msnry = new Masonry(gallery, {
        itemSelector: '.image-wrapper',
        columnWidth: '.image-wrapper',
        gutter: 15
      });
    }

    for (const loader of nextImageLoaders) {
      const module = await loader();
      
      const wrapper = document.createElement('div');
      wrapper.classList.add('image-wrapper');
      
      const img = document.createElement('img');
      img.src = module.default;

      const overlay = document.createElement('div');
      overlay.classList.add('overlay');

      const btn = document.createElement('button');
      btn.classList.add('save-btn');
      btn.textContent = 'Save';

      wrapper.appendChild(img);
      wrapper.appendChild(overlay);
      wrapper.appendChild(btn);

      gallery.appendChild(wrapper);

      msnry.appended(wrapper);

      await new Promise(resolve => {
        imagesLoaded(wrapper).on('always', resolve);
      });
      msnry.layout();
    }

    currentIndex += batchSize;
    isLoading = false;

    if (currentIndex >= imageLoaders.length) {
      observer.unobserve(scrollTrigger);
    }
  }

  const observer = new IntersectionObserver((entries) => {
    if (entries[0].isIntersecting) {
      loadMoreImages();
    }
  }, {
    rootMargin: '200px'
  });

  observer.observe(scrollTrigger);
  loadMoreImages();

  window.lucide.createIcons();

  const modal = document.getElementById('image-modal');
  const modalImg = document.getElementById('modal-image');
  const closeBtn = document.querySelector('.close-btn');

  gallery.addEventListener('click', (e) => {
    const wrapper = e.target.closest('.image-wrapper');
    if (wrapper) {
      const img = wrapper.querySelector('img');
      if (img) {
        modal.classList.add('modal--active'); 
        modalImg.src = img.src;
      }
    }
  });

  function closeModal() {
    modal.classList.remove('modal--active');
  }

  closeBtn.addEventListener('click', closeModal);

  modal.addEventListener('click', (e) => {
    if (e.target === modal) {
      closeModal();
    }
  });
});