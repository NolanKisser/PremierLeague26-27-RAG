document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('predict-form');
  const queryInput = document.getElementById('query-input');
  const btnText = document.querySelector('.btn-text');
  const btnLoader = document.getElementById('btn-loader');
  const submitBtn = document.getElementById('submit-btn');
  const resultsContainer = document.getElementById('results-container');
  const resultsContent = document.getElementById('results-content');

  // Hardcoded defaults for a better user experience on load
  queryInput.value = "Predict the final 20-team Premier League table considering the latest FPL stats, player xG, and team Elo ratings.";

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = queryInput.value.trim();
    if (!query) return;

    // UI Loading state
    btnText.textContent = "Processing...";
    btnLoader.classList.remove('hidden');
    submitBtn.disabled = true;
    resultsContainer.classList.add('hidden');
    
    try {
      // Send request to FastAPI backend
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
      
      // Display results
      resultsContent.textContent = data.report;
      resultsContainer.classList.remove('hidden');
      
      // Scroll to results smoothly
      resultsContainer.scrollIntoView({ behavior: 'smooth' });
    } catch (error) {
      console.error("Prediction Error:", error);
      resultsContent.textContent = "Error generating prediction: " + error.message + "\nMake sure the FastAPI backend (uvicorn api:app) and Ollama are running.";
      resultsContainer.classList.remove('hidden');
    } finally {
      // Reset UI state
      btnText.textContent = "Generate Prediction";
      btnLoader.classList.add('hidden');
      submitBtn.disabled = false;
    }
  });
});
