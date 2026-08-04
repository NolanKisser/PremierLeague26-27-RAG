// Removed getTeamBadge as we now use actual PNG logos from the backend
document.addEventListener('DOMContentLoaded', async () => {
  const loadingContainer = document.getElementById('loading-container');
  const resultsContainer = document.getElementById('results-container');
  const standingsList = document.getElementById('standings-list');
  const errorContent = document.getElementById('error-content');
  const loadingText = document.getElementById('loading-text');

  // We run the prediction immediately on page load
  const query = "Predict the final 20-team Premier League table considering the latest FPL stats, player xG, and team Elo ratings.";
  
  try {
    const response = await fetch('http://localhost:8000/api/predict', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query })
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    const data = await response.json();
    
    if (data.error) {
       throw new Error(data.error);
    }

    // Hide loader
    loadingContainer.classList.add('hidden');
    
    // Sort just in case the LLM returned them out of order, though the prompt implies 1-20
    const standings = data.standings || [];
    standings.sort((a, b) => a.position - b.position);

    // Build Table
    standingsList.innerHTML = ''; // Clear previous

    if (standings.length === 0) {
      errorContent.textContent = "No standings were returned. The LLM might have failed to format as JSON.";
      errorContent.classList.remove('hidden');
    } else {
      standings.forEach(item => {
        const row = document.createElement('div');
        row.className = 'standing-row';

        const safeName = item.team.replace(/ /g, '_').toLowerCase();
        const badgeHtml = `<img src="http://localhost:8000/media/teamlogos/${safeName}.png" alt="${item.team} logo" class="team-logo-img">`;

        row.innerHTML = `
          <div class="standing-header">
            <span class="position">${item.position}</span>
            ${badgeHtml}
            <span class="team-name">${item.team}</span>
            <span class="chevron">▼</span>
          </div>
          <div class="standing-explanation">
            <p>${item.explanation}</p>
          </div>
        `;

        // Toggle explanation on click
        row.querySelector('.standing-header').addEventListener('click', () => {
          const explanation = row.querySelector('.standing-explanation');
          const chevron = row.querySelector('.chevron');
          
          if (explanation.style.maxHeight) {
            explanation.style.maxHeight = null;
            chevron.style.transform = 'rotate(0deg)';
          } else {
            explanation.style.maxHeight = explanation.scrollHeight + "px";
            chevron.style.transform = 'rotate(180deg)';
          }
        });

        standingsList.appendChild(row);
      });
    }
    resultsContainer.classList.remove('hidden');

  } catch (error) {
    console.error("Prediction Error:", error);
    loadingContainer.classList.add('hidden');
    errorContent.textContent = "Error generating prediction: " + error.message + "\nMake sure the FastAPI backend (uvicorn api:app) and Ollama are running.";
    errorContent.classList.remove('hidden');
    resultsContainer.classList.remove('hidden');
  }
});
