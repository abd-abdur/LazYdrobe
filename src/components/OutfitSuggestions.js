// OutfitSuggestions.js
import React from 'react';
import './OutfitSuggestions.css';

const OutfitSuggestions = ({ outfits }) => {
  return (
    <div className="outfit-suggestions">
      <h2>Outfit Suggestions</h2>
      <div className="outfit-list">
        {outfits.map(outfit => (
          <div key={outfit.id} className="outfit-card">
            <h3>{outfit.name}</h3>
            <p>Weather: {outfit.weather}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default OutfitSuggestions;
