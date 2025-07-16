import Masonry from 'masonry-layout';
import imagesLoaded from 'imagesloaded';

document.addEventListener('DOMContentLoaded', () => {
  const gallery = document.getElementById('favorites-gallery');
  const saved = JSON.parse(localStorage.getItem('favorites') || '[]');

  // Initialize Masonry with 3-column layout
  const msnry = new Masonry(gallery, {
    itemSelector: '.image-wrapper',
    columnWidth: '.grid-sizer',
    gutter: '.gutter-sizer',
    percentPosition: true,
  });

  for (const src of saved) {
    const wrapper = document.createElement('div');
    wrapper.classList.add('image-wrapper');

    const img = document.createElement('img');
    img.src = src;

    const overlay = document.createElement('div');
    overlay.classList.add('overlay');

    const removeBtn = document.createElement('button');
    removeBtn.classList.add('remove-btn');
    removeBtn.innerHTML = '<i data-lucide="trash-2"></i>';

    removeBtn.addEventListener('click', (e) => {
        e.stopPropagation(); 

        const currentSaved = JSON.parse(localStorage.getItem('favorites') || '[]');
        const updatedSaved = currentSaved.filter(item => item !== src);

        localStorage.setItem('favorites', JSON.stringify(updatedSaved));

        msnry.remove(wrapper);
        msnry.layout();

        setTimeout(() => {
            console.log("Item removed and layout updated.");
        }, 100);
    });


    wrapper.appendChild(img);
    wrapper.appendChild(overlay);
    wrapper.appendChild(removeBtn);
    gallery.appendChild(wrapper);

    // Wait for image to load, then layout
    imagesLoaded(wrapper, () => {
      msnry.appended(wrapper);
      msnry.layout();
    });
  }

    const modal = document.getElementById('image-modal');
    const modalImg = document.getElementById('modal-image');
    const closeBtn = document.querySelector('.close-btn');

    // Open modal when image is clicked
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

    // Close modal logic
    function closeModal() {
    modal.classList.remove('modal--active');
    }

    closeBtn.addEventListener('click', closeModal);
    modal.addEventListener('click', (e) => {
    if (e.target === modal) {
        closeModal();
    }
    });

    window.lucide.createIcons();
});
