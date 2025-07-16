import Masonry from 'masonry-layout';
import imagesLoaded from 'imagesloaded';

function shuffleArray(arr) {
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
  }

document.addEventListener('DOMContentLoaded', async () => {
  const gallery = document.querySelector('.gallery');
  const scrollTrigger = document.getElementById('scroll-trigger');

  let allImageUrls = [];
  let currentIndex = 0;
  const batchSize = 30;
  let msnry;
  let isLoading = false;

  async function fetchAllImageUrls() {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/v1/images');
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      const imageUrls = await response.json();
      return imageUrls;
    } catch (error) {
      console.error("Failed to fetch image list:", error);
      gallery.innerHTML = `<p class="error-message">Could not load images. Please ensure the backend is running.</p>`;
      return []; 
    }
  }

  async function loadMoreImages() {
    if (isLoading || currentIndex >= allImageUrls.length) {
      return;
    }
    isLoading = true;

    const nextImageUrls = allImageUrls.slice(currentIndex, currentIndex + batchSize);

    if (!msnry) {
      msnry = new Masonry(gallery, {
        itemSelector: '.image-wrapper',
        columnWidth: '.image-wrapper',
        gutter: 15
      });
    }

    for (const imageUrl of nextImageUrls) {
      const wrapper = document.createElement('div');
      wrapper.classList.add('image-wrapper');
      
      const img = document.createElement('img');
      img.src = imageUrl;

      const overlay = document.createElement('div');
      overlay.classList.add('overlay');

      const btn = document.createElement('button');
      btn.classList.add('save-btn');
      btn.textContent = 'Save';

      const favorites = JSON.parse(localStorage.getItem('favorites') || '[]');
      if (favorites.includes(imageUrl)) {
        btn.textContent = 'Saved';
        btn.classList.add('saved');
      }

      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        let saved = JSON.parse(localStorage.getItem('favorites') || '[]');
        if (!saved.includes(img.src)) {
          saved.push(img.src);
          
          btn.textContent = 'Saved';
          btn.classList.add('saved');
        }
        else {
          saved = saved.filter(s => s !== img.src);
          btn.textContent = 'Save';
          btn.classList.remove('saved');
        }
        localStorage.setItem('favorites', JSON.stringify(saved));

        btn.classList.add('pulse');
        btn.addEventListener('animationend', () => {
          btn.classList.remove('pulse');
        }, {once: true});
      });

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

    if (currentIndex >= allImageUrls.length) {
      observer.unobserve(scrollTrigger);
    }
  }

  // Intialization
  allImageUrls = await fetchAllImageUrls();
  if (allImageUrls.length > 0) {
    shuffleArray(allImageUrls);

    const observer = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting) {
        loadMoreImages();
      }
      }, {
        rootMargin: '200px'
      });

    observer.observe(scrollTrigger);
    loadMoreImages();

  }

  

  window.lucide.createIcons()

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