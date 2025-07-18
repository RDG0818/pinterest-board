// src/music.js
document.addEventListener('DOMContentLoaded', () => {
  const BACKEND_URL = 'http://localhost:8000';
  const selector = document.getElementById('image-selector');
  const btn      = document.getElementById('get-songs-btn');
  const list     = document.getElementById('song-list');
  let selectedSrc = null;

  // 1) Load favorites from localStorage
  const favorites = JSON.parse(localStorage.getItem('favorites') || '[]');

  // 2) Render thumbnails
  for (const src of favorites) {
    const img = document.createElement('img');
    img.src = src;
    img.alt = '';
    img.addEventListener('click', () => {
      // clear previous selection
      selector.querySelectorAll('img').forEach(i => i.classList.remove('selected'));
      img.classList.add('selected');
      selectedSrc = src;
      btn.disabled = false;
      list.innerHTML = ''; // clear old songs
    });
    selector.appendChild(img);
  }

  btn.addEventListener('click', async () => {
    if (!selectedSrc) return;

    try {
      const response = await fetch(`http://localhost:8000/match-music/?image_id=${encodeURIComponent(selectedSrc)}`);
      const jsonData = await response.json(); 

      console.log('Songs received from backend:', jsonData);

      // If your backend returns a list of songs (which it should)
      const songs = jsonData;

      if (!Array.isArray(songs)) {
        console.error('Expected an array, but got:', songs);
        return;
      }

      list.innerHTML = '';

      for (const track of songs) {
        const item = document.createElement('div');
        item.classList.add('song-item');

        item.innerHTML = `
          <h3>${track.song_title}</h3>
          <p>${track.mood}</p>
          <audio controls src="${BACKEND_URL}${track.audio_url}"></audio>
        `;
        list.appendChild(item);
      }
    } catch (err) {
      console.error('Error fetching songs:', err);
    }
  });
});
