document.addEventListener('DOMContentLoaded', () => {
    // Calorie range slider display update
    const calRange = document.getElementById('calories');
    const calVal = document.getElementById('cal-val');
    if (calRange && calVal) {
        calRange.addEventListener('input', (e) => {
            calVal.textContent = e.target.value;
        });
    }

    // Recommendation Query Form Submission
    const recommendForm = document.getElementById('recommend-form');
    if (recommendForm) {
        recommendForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const submitBtn = recommendForm.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn.textContent;
            submitBtn.textContent = 'Running Rules Engine...';
            submitBtn.disabled = true;

            const diet = document.querySelector('input[name="diet"]:checked').value;
            const cuisine = document.querySelector('input[name="cuisine"]:checked').value;
            const taste = document.querySelector('input[name="taste"]:checked').value;
            const goal = document.querySelector('input[name="goal"]:checked').value;
            const calories = calRange.value;

            try {
                const response = await fetch('/api/recommend', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ diet, cuisine, taste, goal, calories })
                });

                if (!response.ok) throw new Error('Failed to fetch recommendations');

                const data = await response.json();
                renderLogs(data.logs);
                renderRecommendations(data.recommendations);

            } catch (error) {
                console.error(error);
                alert('Error running inference rule engine. Please try again.');
            } finally {
                submitBtn.textContent = originalBtnText;
                submitBtn.disabled = false;
            }
        });
    }

    // Admin Recipe Table Management
    const recipeForm = document.getElementById('recipe-form');
    const adminTableBody = document.getElementById('admin-table-body');
    
    if (adminTableBody) {
        // Fetch and render recipes in admin
        const fetchAdminRecipes = async () => {
            try {
                const response = await fetch('/api/admin/recipes');
                if (!response.ok) throw new Error('Failed to fetch recipes');
                const recipes = await response.json();
                
                adminTableBody.innerHTML = '';
                if (recipes.length === 0) {
                    adminTableBody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-muted);">No recipes in database. Add one on the left.</td></tr>`;
                    return;
                }
                
                recipes.forEach(recipe => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td><strong>${escapeHtml(recipe.name)}</strong></td>
                        <td><span class="recipe-diet-tag ${recipe.diet.toLowerCase() === 'veg' ? 'veg' : 'non-veg'}" style="font-size: 0.7rem; padding: 0.2rem 0.5rem;">${recipe.diet}</span></td>
                        <td>${escapeHtml(recipe.cuisine)}</td>
                        <td><span style="color: var(--amber-orange); font-weight: 600;">${recipe.calories} kcal</span></td>
                        <td>${escapeHtml(recipe.taste)}</td>
                        <td>
                            <button class="btn-danger btn-delete-recipe" data-id="${recipe.id}">Delete</button>
                        </td>
                    `;
                    adminTableBody.appendChild(row);
                });

                // Attach delete listeners
                document.querySelectorAll('.btn-delete-recipe').forEach(btn => {
                    btn.addEventListener('click', async (e) => {
                        const id = e.target.getAttribute('data-id');
                        if (confirm('Are you sure you want to delete this recipe?')) {
                            try {
                                const delRes = await fetch(`/api/admin/delete/${id}`, {
                                    method: 'DELETE'
                                });
                                const delData = await delRes.json();
                                if (delData.success) {
                                    fetchAdminRecipes();
                                } else {
                                    alert(delData.error || 'Failed to delete recipe');
                                }
                            } catch (err) {
                                console.error(err);
                                alert('Error deleting recipe.');
                            }
                        }
                    });
                });

            } catch (error) {
                console.error(error);
                adminTableBody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--color-danger);">Error loading database.</td></tr>`;
            }
        };

        // Initial load of admin recipes
        fetchAdminRecipes();

        // Handle Add Recipe Form Submission
        if (recipeForm) {
            recipeForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const name = document.getElementById('name').value;
                const diet = document.getElementById('diet').value;
                const cuisine = document.getElementById('cuisine').value;
                const calories = document.getElementById('calories-input').value;
                const taste = document.getElementById('taste').value;
                const protein = document.getElementById('protein').value;
                const fiber = document.getElementById('fiber').value;
                const carbs = document.getElementById('carbs').value;
                const fat = document.getElementById('fat').value;
                const health_goals = document.getElementById('health_goals').value;
                const image_url = document.getElementById('image_url').value;
                const ingredients = document.getElementById('ingredients').value;
                const instructions = document.getElementById('instructions').value;
                const scientific_backing = document.getElementById('scientific_backing').value;

                try {
                    const response = await fetch('/api/admin/add', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            name, diet, cuisine, calories, taste, ingredients, instructions, scientific_backing, image_url,
                            protein, fiber, carbs, fat, health_goals
                        })
                    });

                    const data = await response.json();
                    if (data.success) {
                        recipeForm.reset();
                        fetchAdminRecipes();
                    } else {
                        alert(data.error || 'Failed to add recipe');
                    }
                } catch (err) {
                    console.error(err);
                    alert('Error adding recipe.');
                }
            });
        }
    }
});

// Helper: Escape HTML to prevent XSS
function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, "&amp;")
              .replace(/</g, "&lt;")
              .replace(/>/g, "&gt;")
              .replace(/"/g, "&quot;")
              .replace(/'/g, "&#039;");
}

// Render Rule Engine Trace Log
function renderLogs(logs) {
    const logContainer = document.getElementById('log-entries');
    if (!logContainer) return;
    
    logContainer.innerHTML = '';
    
    logs.forEach(log => {
        const div = document.createElement('div');
        div.className = 'log-entry';
        
        let cleanedLog = log;
        if (log.includes('-> [SUCCESS]')) {
            div.classList.add('success');
            cleanedLog = log.replace('-> [SUCCESS]', '');
        } else if (log.includes('-> [FAILED]')) {
            div.classList.add('failed');
            cleanedLog = log.replace('-> [FAILED]', '');
        } else if (log.includes('Evaluating')) {
            div.classList.add('triggered');
        }
        
        div.textContent = cleanedLog.trim();
        logContainer.appendChild(div);
    });
}

// Render Recommendations list
function renderRecommendations(recipes) {
    const container = document.getElementById('recommendations-container');
    if (!container) return;
    
    container.innerHTML = '';
    
    if (recipes.length === 0) {
        container.innerHTML = `
            <div class="glass-card" style="text-align: center; padding: 3rem;">
                <p style="font-size: 1.2rem; color: var(--text-secondary);">No recommendations found matching even fallback criteria.</p>
                <p style="font-size: 0.95rem; color: var(--text-muted); margin-top: 0.5rem;">Try increasing your calorie limit or selecting a different diet profile.</p>
            </div>
        `;
        return;
    }
    
    recipes.forEach((recipe, index) => {
        const card = document.createElement('div');
        card.className = 'recipe-card';
        card.style.animationDelay = `${index * 0.1}s`;
        
        const dietClass = recipe.diet.toLowerCase() === 'veg' ? 'veg' : 'non-veg';
        
        // Goals rendering helper
        const goalsHtml = recipe.health_goals ? recipe.health_goals.split(',')
            .map(g => `<span class="meta-badge" style="font-size: 0.72rem; border-color: rgba(99,102,241,0.2); color: #818cf8; font-weight: 500;">🏷️ ${escapeHtml(g.trim())}</span>`)
            .join(' ') : '';
        
        card.innerHTML = `
            <img class="recipe-image" src="${escapeHtml(recipe.image_url)}" alt="${escapeHtml(recipe.name)}" onerror="this.src='https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500&auto=format&fit=crop'">
            <div class="recipe-content">
                <div>
                    <div class="recipe-header">
                        <h3 class="recipe-title">${escapeHtml(recipe.name)}</h3>
                        <span class="recipe-diet-tag ${dietClass}">${recipe.diet}</span>
                    </div>
                    <div class="recipe-meta">
                        <span class="meta-badge">Cuisine: <strong>${escapeHtml(recipe.cuisine)}</strong></span>
                        <span class="meta-badge">Calories: <strong style="color: var(--amber-orange);">${recipe.calories} kcal</strong></span>
                        <span class="meta-badge">Taste: <strong>${escapeHtml(recipe.taste)}</strong></span>
                    </div>
                    
                    <div style="display: flex; gap: 0.35rem; flex-wrap: wrap; margin-bottom: 1.2rem;">
                        ${goalsHtml}
                    </div>
                </div>

                <!-- Macronutrients Progress Grid -->
                <div class="macro-grid">
                    <div class="macro-item">
                        <div class="macro-val protein">${recipe.protein}g</div>
                        <div class="macro-label">Protein</div>
                    </div>
                    <div class="macro-item">
                        <div class="macro-val fiber">${recipe.fiber}g</div>
                        <div class="macro-label">Fiber</div>
                    </div>
                    <div class="macro-item">
                        <div class="macro-val carbs">${recipe.carbs}g</div>
                        <div class="macro-label">Carbs</div>
                    </div>
                    <div class="macro-item">
                        <div class="macro-val fat">${recipe.fat}g</div>
                        <div class="macro-label">Fat</div>
                    </div>
                </div>
                
                <div class="scientific-box" style="margin-bottom: 1.2rem;">
                    <strong>Nutritional Backing & Authenticity</strong>
                    ${escapeHtml(recipe.scientific_backing)}
                </div>
                
                <div style="display: flex; gap: 0.75rem; align-items: center;">
                    <button class="detail-btn btn-toggle-details" data-id="${recipe.id}">Show Recipe & Ingredients</button>
                </div>
                
                <div class="recipe-details-expanded" id="details-${recipe.id}">
                    <div class="details-grid">
                        <div>
                            <h4 class="details-title">Ingredients Needed</h4>
                            <ul class="ingredients-list">
                                ${recipe.ingredients.split(',').map(ing => `<li>${escapeHtml(ing.trim())}</li>`).join('')}
                            </ul>
                        </div>
                        <div>
                            <h4 class="details-title">Instructions</h4>
                            <p class="instructions-text">${escapeHtml(recipe.instructions)}</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        container.appendChild(card);
    });

    // Attach Toggle Details listeners
    container.querySelectorAll('.btn-toggle-details').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const id = e.target.getAttribute('data-id');
            const detailsDiv = document.getElementById(`details-${id}`);
            if (detailsDiv.style.display === 'block') {
                detailsDiv.style.display = 'none';
                e.target.textContent = 'Show Recipe & Ingredients';
            } else {
                detailsDiv.style.display = 'block';
                e.target.textContent = 'Hide Recipe & Ingredients';
            }
        });
    });
}
