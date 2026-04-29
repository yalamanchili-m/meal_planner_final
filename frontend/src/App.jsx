import React, { useEffect, useState } from 'react';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8002';

const emptyRecipe = {
  name: '',
  minutes: '',
  ingredients: '',
  steps: '',
  tags: '',
  calories: '',
};

function App() {
  const [recipes, setRecipes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [newRecipe, setNewRecipe] = useState(emptyRecipe);

  useEffect(() => {
    fetchRecipes();
  }, []);

  const fetchRecipes = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE}/recipes`);
      setRecipes(response.data || []);
    } catch (error) {
      console.error('Error fetching recipes:', error);
      alert('Could not load recipes. Check that the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const updateRecipeField = (field, value) => {
    setNewRecipe((current) => ({ ...current, [field]: value }));
  };

  const addRecipe = async () => {
    if (!newRecipe.name.trim()) {
      alert('Please enter a recipe name');
      return;
    }

    const recipeData = {
      name: newRecipe.name.trim(),
      minutes: Number.parseInt(newRecipe.minutes, 10) || 30,
      ingredients: newRecipe.ingredients.split('\n').map((item) => item.trim()).filter(Boolean),
      steps: newRecipe.steps.split('\n').map((step) => step.trim()).filter(Boolean),
      tags: newRecipe.tags.split(',').map((tag) => tag.trim().toLowerCase()).filter(Boolean),
      calories: Number.parseFloat(newRecipe.calories) || null,
    };

    try {
      await axios.post(`${API_BASE}/recipes`, recipeData);
      setNewRecipe(emptyRecipe);
      setShowForm(false);
      await fetchRecipes();
      alert('Recipe added successfully.');
    } catch (error) {
      console.error('Error adding recipe:', error);
      alert('Failed to add recipe.');
    }
  };

  const deleteRecipe = async (id) => {
    if (!window.confirm('Delete this recipe?')) {
      return;
    }

    try {
      await axios.delete(`${API_BASE}/recipes/${id}`);
      await fetchRecipes();
      alert('Recipe deleted successfully.');
    } catch (error) {
      console.error('Error deleting recipe:', error);
      alert('Failed to delete recipe.');
    }
  };

  return (
    <div style={{ minHeight: '100vh', background: '#f8fafc', padding: '20px' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px', flexWrap: 'wrap', gap: '15px' }}>
          <div>
            <h1 style={{ fontSize: '28px', fontWeight: '500', color: '#1e293b', marginBottom: '5px' }}>Meal Planner</h1>
            <p style={{ color: '#64748b', fontSize: '14px' }}>Manage your recipes and meal plans</p>
          </div>
          <button
            onClick={() => setShowForm((visible) => !visible)}
            style={{
              background: '#1e293b',
              color: 'white',
              border: 'none',
              padding: '10px 20px',
              borderRadius: '40px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '500',
            }}
          >
            {showForm ? 'Cancel' : '+ Add recipe'}
          </button>
        </header>

        {showForm ? (
          <section style={{
            background: 'white',
            borderRadius: '24px',
            padding: '24px',
            marginBottom: '30px',
            boxShadow: '0 4px 6px -1px rgba(0,0,0,0.05)',
            border: '1px solid #e2e8f0',
          }}>
            <h2 style={{ fontSize: '18px', fontWeight: '500', marginBottom: '20px', color: '#1e293b' }}>New Recipe</h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '16px' }}>
              <input type="text" placeholder="Recipe name *" value={newRecipe.name} onChange={(event) => updateRecipeField('name', event.target.value)} style={inputStyle} />
              <input type="number" placeholder="Minutes to cook" value={newRecipe.minutes} onChange={(event) => updateRecipeField('minutes', event.target.value)} style={inputStyle} />
              <input type="text" placeholder="Tags, comma separated" value={newRecipe.tags} onChange={(event) => updateRecipeField('tags', event.target.value)} style={inputStyle} />
              <input type="number" placeholder="Calories, optional" value={newRecipe.calories} onChange={(event) => updateRecipeField('calories', event.target.value)} style={inputStyle} />
            </div>
            <textarea placeholder="Ingredients, one per line" value={newRecipe.ingredients} onChange={(event) => updateRecipeField('ingredients', event.target.value)} rows="4" style={textAreaStyle} />
            <textarea placeholder="Steps, one per line" value={newRecipe.steps} onChange={(event) => updateRecipeField('steps', event.target.value)} rows="4" style={textAreaStyle} />
            <button onClick={addRecipe} style={saveButtonStyle}>Save recipe</button>
          </section>
        ) : null}

        {loading ? (
          <div style={{ textAlign: 'center', padding: '60px', color: '#64748b' }}>Loading recipes...</div>
        ) : recipes.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '60px', background: 'white', borderRadius: '24px', border: '1px solid #e2e8f0' }}>
            <p style={{ color: '#64748b' }}>No recipes yet. Click "Add recipe" to get started.</p>
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '20px' }}>
            {recipes.map((recipe) => (
              <article key={recipe.id} style={{ background: 'white', borderRadius: '20px', padding: '20px', border: '1px solid #e2e8f0' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '12px', marginBottom: '12px' }}>
                  <h3 style={{ fontSize: '18px', fontWeight: '500', color: '#1e293b', margin: 0 }}>{recipe.name}</h3>
                  <button onClick={() => deleteRecipe(recipe.id)} style={deleteButtonStyle}>Delete</button>
                </div>

                {recipe.minutes ? <p style={metaStyle}>{recipe.minutes} minutes</p> : null}
                {recipe.calories ? <p style={metaStyle}>{recipe.calories} calories</p> : null}

                {recipe.tags?.length ? (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '12px' }}>
                    {recipe.tags.slice(0, 3).map((tag) => (
                      <span key={tag} style={{ background: '#f1f5f9', padding: '4px 10px', borderRadius: '20px', fontSize: '11px', color: '#475569' }}>#{tag}</span>
                    ))}
                  </div>
                ) : null}

                <details style={{ marginTop: '12px' }}>
                  <summary style={{ cursor: 'pointer', fontSize: '13px', color: '#3b82f6' }}>View details</summary>
                  <RecipeDetails recipe={recipe} />
                </details>
              </article>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function RecipeDetails({ recipe }) {
  return (
    <div style={{ marginTop: '12px' }}>
      {recipe.ingredients?.length ? (
        <div style={{ marginBottom: '12px' }}>
          <strong style={{ fontSize: '12px', color: '#475569' }}>Ingredients:</strong>
          <ul style={{ marginTop: '6px', marginLeft: '20px', color: '#64748b', fontSize: '13px' }}>
            {recipe.ingredients.slice(0, 5).map((ingredient) => <li key={ingredient}>{ingredient}</li>)}
            {recipe.ingredients.length > 5 ? <li>+{recipe.ingredients.length - 5} more</li> : null}
          </ul>
        </div>
      ) : null}

      {recipe.steps?.length ? (
        <div>
          <strong style={{ fontSize: '12px', color: '#475569' }}>Steps:</strong>
          <ol style={{ marginTop: '6px', marginLeft: '20px', color: '#64748b', fontSize: '13px' }}>
            {recipe.steps.slice(0, 3).map((step) => <li key={step}>{step}</li>)}
            {recipe.steps.length > 3 ? <li>+{recipe.steps.length - 3} more</li> : null}
          </ol>
        </div>
      ) : null}
    </div>
  );
}

const inputStyle = {
  padding: '12px',
  borderRadius: '12px',
  border: '1px solid #e2e8f0',
  fontSize: '14px',
};

const textAreaStyle = {
  width: '100%',
  marginTop: '16px',
  padding: '12px',
  borderRadius: '12px',
  border: '1px solid #e2e8f0',
  fontSize: '14px',
  fontFamily: 'inherit',
};

const saveButtonStyle = {
  marginTop: '20px',
  background: '#059669',
  color: 'white',
  border: 'none',
  padding: '12px 24px',
  borderRadius: '40px',
  cursor: 'pointer',
  fontSize: '14px',
  fontWeight: '500',
  width: '100%',
};

const deleteButtonStyle = {
  background: '#fee2e2',
  border: 'none',
  borderRadius: '30px',
  padding: '6px 12px',
  cursor: 'pointer',
  fontSize: '12px',
  color: '#dc2626',
};

const metaStyle = {
  color: '#64748b',
  fontSize: '13px',
  marginBottom: '8px',
};

export default App;
