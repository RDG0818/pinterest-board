const gallery = document.querySelector('.gallery');

const images = import.meta.glob('./assets/fantasy_images/*.{jpg,jpeg,png}', { eager: true });

Object.values(images).forEach((mod) => {
  const wrapper = document.createElement('div');
  wrapper.classList.add('image-wrapper');

  const img = document.createElement('img');
  img.src = mod.default;

  const overlay = document.createElement('div');
  overlay.classList.add('overlay');

  const btn = document.createElement('button');
  btn.classList.add('save-btn');
  btn.textContent = 'Save';

  wrapper.appendChild(img);
  wrapper.appendChild(overlay);
  wrapper.appendChild(btn);
  gallery.appendChild(wrapper);
});

window.lucide.createIcons();