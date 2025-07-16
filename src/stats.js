function stringToColor(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }

  // Use the hash to generate a hue (a degree on the color wheel)
  const hue = (Math.abs(hash) * 137.5) % 360;

  // Return an HSL color with a fixed saturation and lightness
  // Saturation: 75% (vibrant but not neon)
  // Lightness:  30% (dark enough for white text)
  return `hsl(${hue}, 75%, 30%)`;
}

async function fetchAndDisplayTags(imageId, container) {
  // Clear previous tags and show a loading state
  container.innerHTML = '<span class="tag-pill">Loading tags...</span>';

  try {
    // Call your FastAPI backend
    // Make sure the port (e.g., 8000) matches your running server
    const response = await fetch(`http://127.0.0.1:8000/get-tags/?image_id=${imageId}`);
    if (!response.ok) {
        throw new Error('Network response was not ok');
    }
    const data = await response.json();

    // Clear the loading message
    container.innerHTML = '';

    // Create and display each tag pill
    data.tags.forEach(tag => {
      const tagElement = document.createElement('span');
      tagElement.className = 'tag-pill';
      tagElement.textContent = `🏷️ ${tag}`;
      tagElement.style.backgroundColor = stringToColor(tag);
      container.appendChild(tagElement);
    });
  } catch (error) {
    console.error('Failed to fetch tags:', error);
    container.innerHTML = '<span class="tag-pill" style="background-color: #581b1b;">Error loading tags</span>';
  }
}


document.addEventListener('DOMContentLoaded', async () => {
  const imagePlaceholder = document.getElementById('image-placeholder');
  const styleColors = {
    watercolor: 'rgba(30, 144, 255, 0.6)',   // Dodger Blue
    digital:    'rgba(255, 99, 132, 0.6)',   // Soft Red
    oil:        'rgba(255, 206, 86, 0.6)',   // Yellow
    sketch:     'rgba(75, 192, 192, 0.6)',   // Teal
    pixel:      'rgba(153, 102, 255, 0.6)',  // Purple
  };

  const styles = Object.keys(styleColors);
  const favoriteImages = JSON.parse(localStorage.getItem('favorites') || '[]');

  if (favoriteImages.length === 0) {
    const chartArea = document.querySelector('.chart-section');
    chartArea.innerHTML = `<p style="color: #ccc; text-align: center;">You have no favorite images to analyze. Go save some!</p>`;
    document.querySelector('.preview-panel').style.display = 'none'; // Hide the right panel
    return; // Stop the script
  }

  try {
    // 2. Send the list to the backend using a POST request
    const response = await fetch('http://127.0.0.1:8000/get-chart-data/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      // Send the list of favorites in the request body
      body: JSON.stringify({ image_sources: favoriteImages }),
    });

    if (!response.ok) {
      throw new Error('Failed to fetch chart data from backend.');
    }
    const rawData = await response.json();

    const dataPoints = rawData.map(d => ({
        x: d.x,
        y: d.y,
        r: d.r,
        label: d.label,
        imageSrc: d.imageSrc
    }));

    const bgColors = rawData.map(d => styleColors[d.style]);
    const brColors = rawData.map(d => styleColors[d.style].replace('0.6', '1'));

    const bubbleData = {
        datasets: [{
        label: 'Image Embeddings',
        data: dataPoints,
        backgroundColor: bgColors,
        borderColor: brColors,
        borderWidth: 1,
        }]
    };

    const bubbleCtx = document.getElementById('bubble-chart').getContext('2d');
    const chartSection = document.querySelector('.chart-section');
    const previewPanel = document.querySelector('.preview-panel');
    const tagContainer = document.getElementById('tag-container');

    const bubbleOptions = {
        responsive: true,
        animation: {
        onComplete: () => {
            const chartHeight = chartSection.offsetHeight;
            previewPanel.style.height = `${chartHeight}px`;
        },
        },
        onClick: (e, elements) => {
        if (elements.length > 0) {
            imagePlaceholder.style.display = 'none';
            const index = elements[0].index;
            const imgData = rawData[index];
            const imgEl = document.getElementById('selected-image');
            imgEl.src = imgData.imageSrc;
            imgEl.alt = imgData.label;
            imgEl.classList.add('visible');
            fetchAndDisplayTags(imgData.label, tagContainer);
            
        }
        },
        plugins: {
        tooltip: {
            callbacks: {
            label: context => {
                const { x, y, r, label } = context.raw;
                return `${label} (Tone: ${x}, Realism: ${y}, Scale: ${r})`;
            }
            }
        },
        title: {
            display: true,
            text: 'Fantasy Image Bubble Chart',
            color: '#fff',
            font: { size: 18 }
        },
        legend: {
            display: false
        }
        },
        scales: {
        x: {
            title: {
            display: true,
            text: 'Fantasy Tone (Dark → Light)',
            color: '#fff'
            },
            min: -100,
            max: 100,
            ticks: { color: '#ccc' },
            grid: { color: '#333' }
        },
        y: {
            title: {
            display: true,
            text: 'Realism (Realistic → Magical)',
            color: '#fff'
            },
            min: 0,
            max: 100,
            ticks: { color: '#ccc' },
            grid: { color: '#333' }
        }
        }
    };

    new Chart(bubbleCtx, {
        type: 'bubble',
        data: bubbleData,
        options: bubbleOptions
    });

  // Render legend
    const legendContainer = document.getElementById('bubble-legend');
    Object.entries(styleColors).forEach(([style, color]) => {
        const item = document.createElement('div');
        item.classList.add('legend-item');
        const swatch = document.createElement('span');
        swatch.classList.add('legend-swatch');
        swatch.style.backgroundColor = color;
        const label = document.createElement('span');
        label.textContent = style.charAt(0).toUpperCase() + style.slice(1);
        item.appendChild(swatch);
        item.appendChild(label);
        legendContainer.appendChild(item);
    });
    } catch (error) {
        console.error("Could not initialize chart:", error);
        const chartArea = document.querySelector('.chart-section');
        chartArea.innerHTML = `<p style="color: #ff8a80; text-align: center;">Could not load chart data. Please ensure the backend server is running and accessible.</p>`;
    }
});
