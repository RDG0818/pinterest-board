const descriptiveColorMap = {
  "Ash Grey": "#B2BEB5",
  "Auburn": "#A52A2A",
  "Beige": "#F5F5DC",
  "Black": "#000000",
  "Blood Orange": "#D1001C",
  "Bright Blue": "#0096FF",
  "Bronze": "#CD7F32",
  "Brown": "#8B4513",
  "Burning Orange": "#FF7034",
  "Burnt Orange": "#CC5500",
  "Burnt Sienna": "#E97451",
  "Burnt Umber": "#8A3324",
  "Cerulean Blue": "#2A52BE",
  "Charcoal Black": "#101010",
  "Charcoal Gray": "#36454F",
  "Cream": "#FFFDD0",
  "Creamy White": "#FDF4DC",
  "Crimson Red": "#DC143C",
  "Dark Blue": "#00008B",
  "Dark Brown": "#5C4033",
  "Dark Gray": "#A9A9A9",
  "Dark Green": "#006400",
  "Dark Grey": "#A9A9A9",
  "Dark Orange": "#FF8C00",
  "Dark Purple": "#301934",
  "Dark Red": "#8B0000",
  "Dark Teal": "#014D4D",
  "Deep Black": "#0B0B0B",
  "Deep Blue": "#001F54",
  "Deep Brown": "#3B1F1F",
  "Deep Burgundy": "#770737",
  "Deep Crimson": "#6A0D27",
  "Deep Crimson Red": "#8A0303",
  "Deep Gray": "#505050",
  "Deep Green": "#004225",
  "Deep Ocean Blue": "#003366",
  "Deep Orange": "#FF5722",
  "Deep Purple": "#4B0082",
  "Deep Red": "#7C0A02",
  "Deep Teal": "#004B49",
  "Desert Brown": "#C19A6B",
  "Dusky Red": "#87413F",
  "Dusty Blue": "#5A798A",
  "Dusty Brown": "#AC8A65",
  "Dusty Gold": "#C5B358",
  "Dusty Grey": "#999999",
  "Dusty Orange": "#D4915D",
  "Dusty Purple": "#A3989D",
  "Dusty Red": "#B74C43",
  "Dusty Rose": "#C08081",
  "Dusty Teal": "#669999",
  "Earthy Brown": "#8B5E3C",
  "Electric Blue": "#7DF9FF",
  "Fiery Orange": "#FF4500",
  "Forest Green": "#228B22",
  "Gold": "#FFD700",
  "Golden Brown": "#996515",
  "Golden Yellow": "#FFDF00",
  "Grass Green": "#7CFC00",
  "Gray": "#808080",
  "Grayish Green": "#A9BA9D",
  "Green": "#008000",
  "Grey": "#808080",
  "Greyish Blue": "#A9B4C2",
  "Ice Blue": "#D6FFFF",
  "Ice White": "#F4FDFF",
  "Icy Blue": "#AFEEEE",
  "Indigo": "#4B0082",
  "Ivory": "#FFFFF0",
  "Jade Green": "#00A86B",
  "Lavender Purple": "#967BB6",
  "Light Beige": "#FAF0E6",
  "Light Blue": "#ADD8E6",
  "Maroon": "#800000",
  "Moss Green": "#8A9A5B",
  "Murky Green": "#698B69",
  "Muted Brown": "#A0522D",
  "Obsidian Black": "#0C0C0C",
  "Ocean Blue": "#4F42B5",
  "Ochre": "#CC7722",
  "Off-White": "#FAF9F6",
  "Olive Gold": "#B5A642",
  "Olive Green": "#708238",
  "Orange": "#FFA500",
  "Orange Red": "#FF4500",
  "Pale Blue": "#AFEEEE",
  "Pale Gold": "#E6BE8A",
  "Pale Gray": "#D3D3D3",
  "Pale Grey": "#D3D3D3",
  "Pale Lavender": "#E6E6FA",
  "Pale Orange": "#FFDAB9",
  "Pale Pink": "#FADADD",
  "Pale Skin Tone": "#FFE0BD",
  "Pale Stone": "#DDD6CC",
  "Pale Teal": "#98FFEC",
  "Pale White": "#FFFFFB",
  "Pale Yellow": "#FFFFE0",
  "Pastel Purple": "#C3B1E1",
  "Pink": "#FFC0CB",
  "Platinum Blonde": "#FAF7E3",
  "Red": "#FF0000",
  "Reddish-Brown": "#A52A2A",
  "Rose Gold": "#B76E79",
  "Royal Blue": "#4169E1",
  "Royal Gold": "#FADA5E",
  "Russet Brown": "#80461B",
  "Rust Red": "#B7410E",
  "Rusty Brown": "#8B4000",
  "Sandy Beige": "#F4A460",
  "Sandy Brown": "#F4A460",
  "Sandy Yellow": "#F1C27D",
  "Silver": "#C0C0C0",
  "Sky Blue": "#87CEEB",
  "Slate Grey": "#708090",
  "Smoky Gray": "#726E6D",
  "Smoky Grey": "#726E6D",
  "Steel Grey": "#71797E",
  "Sunny Yellow": "#FFFD37",
  "Sunset Orange": "#FD5E53",
  "Swamp Green": "#748500",
  "Teal": "#008080",
  "Teal Blue": "#367588",
  "Terracotta": "#E2725B",
  "Turquoise": "#40E0D0",
  "Vermilion Red": "#E34234",
  "Violet": "#8F00FF",
  "Violet Purple": "#9F5F9F",
  "Warm Brown": "#A0522D",
  "Warm Gold": "#DAA520",
  "Warm Orange": "#FFB347",
  "White": "#FFFFFF"
};

function hexToHsla(hex, alpha = 1) {
  hex = hex.replace('#', '');

  if (hex.length === 3) {
    hex = hex.split('').map(x => x + x).join('');
  }

  const r = parseInt(hex.substr(0, 2), 16) / 255;
  const g = parseInt(hex.substr(2, 2), 16) / 255;
  const b = parseInt(hex.substr(4, 2), 16) / 255;

  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  let h, s, l;
  l = (max + min) / 2;

  if (max === min) {
    h = s = 0; // achromatic
  } else {
    const d = max - min;
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min);

    switch (max) {
      case r:
        h = ((g - b) / d + (g < b ? 6 : 0));
        break;
      case g:
        h = ((b - r) / d + 2);
        break;
      case b:
        h = ((r - g) / d + 4);
        break;
    }

    h *= 60;
  }

  s = Math.round(s * 100);
  l = Math.round(l * 100);
  h = Math.round(h);

  return `hsla(${h}, ${s}%, ${l}%, ${alpha})`;
}

function resolveColor(colorName) {
  if (descriptiveColorMap[colorName]) {
    return descriptiveColorMap[colorName];
  }

  let hash = 0;
  for (let i = 0; i < colorName.length; i++) {
    hash = colorName.charCodeAt(i) + ((hash << 5) - hash);
  }
  const hue = Math.abs(hash) % 360;
  return `hsla(${hue}, 70%, 55%, 0.7)`;
}

function stringToColor(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }
    const hue = Math.abs(hash) % 360;
    return `hsla(${hue}, 70%, 55%, 0.7)`;
}

function sigmoid(value) {
    const inMin = 1;  
    const inMax = 10;  
    const outMin = 1;  
    const outMax = 25; 

    const noiseAmount = 10;

    const normalized = ((value - inMin) / (inMax - inMin)) * 12 - 6;

    const sigmoid = 1 / (1 + Math.exp(-normalized));
    const noise = (Math.random() - 0.5) * noiseAmount;

    return Math.round(sigmoid * (outMax - outMin) + outMin + noise);
}

async function fetchAndDisplayTags(filename, container) {
  container.innerHTML = '<span class="tag-pill">Loading tags...</span>';

  try {
    const response = await fetch(`http://127.0.0.1:8000/get-tags/?filename=${filename}`);
    if (!response.ok) {
        throw new Error('Network response was not ok');
    }
    const data = await response.json();

    container.innerHTML = '';

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
      body: JSON.stringify({ image_sources: favoriteImages }),
    });

    if (!response.ok) {
      throw new Error('Failed to fetch chart data from backend.');
    }
    const rawData = await response.json();

    const dataPoints = rawData.map(d => ({
        x: +(d.x + (Math.random() - 0.5)).toFixed(2),
        y: +(d.y + (Math.random() - 0.5)).toFixed(2),
        r: sigmoid(d.r),
        label: d.label,
        imageSrc: d.imageSrc,
        color: d.color
    }));

      const bgColors = dataPoints.map(d => {
        const resolved = resolveColor(d.color);
        return resolved.includes('hsla') ? resolved : hexToHsla(resolved, 0.7);
      });

      const brColors = bgColors.map(c => c.replace(/[\d.]+\)$/, '1)')); // alpha to 1

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
            const chart = e.chart; 
            const element = elements[0]; // Get the clicked element

            // Get the data point directly from the chart's internal data. This is the robust way.
            const dataPoint = chart.data.datasets[element.datasetIndex].data[element.index];

            if (dataPoint) {
                // Hide the placeholder text
                imagePlaceholder.style.display = 'none';
                
                // Update the image preview panel with the correct data
                const imgEl = document.getElementById('selected-image');
                imgEl.src = dataPoint.imageSrc;
                imgEl.alt = dataPoint.label;
                imgEl.classList.add('visible'); 

                document.getElementById('image-title').textContent = dataPoint.label;

                const filename = dataPoint.imageSrc.split('/').pop();
                fetchAndDisplayTags(filename, tagContainer);
            }
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
            min: 0,
            max: 10,
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
            max: 10,
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

    } catch (error) {
        console.error("Could not initialize chart:", error);
        const chartArea = document.querySelector('.chart-section');
        chartArea.innerHTML = `<p style="color: #ff8a80; text-align: center;">Could not load chart data. Please ensure the backend server is running and accessible.</p>`;
    }
});
