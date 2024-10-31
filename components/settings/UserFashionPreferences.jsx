import React, { useState, useEffect } from 'react';

const UserFashionPreferences = ({ initialPreferences = {} }) => {
  const [preferences, setPreferences] = useState({
    favoriteStyles: '',
    favoriteColors: '',
    favoriteBrands: '',
    ...initialPreferences, // Prefill if initialPreferences is provided
  });

  useEffect(() => {
    if (initialPreferences) {
      setPreferences((prevPreferences) => ({
        ...prevPreferences,
        ...initialPreferences,
      }));
    }
  }, [initialPreferences]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setPreferences((prevPreferences) => ({
      ...prevPreferences,
      [name]: value,
    }));
  };

  return (
    <div style={{ padding: '10px', border: '1px solid #ddd', borderRadius: '8px', maxWidth: '300px', margin: '0 auto' }}>
      <h3>Fashion Preferences</h3>
      <label>
        Favorite Styles:
        <input
          type="text"
          name="favoriteStyles"
          value={preferences.favoriteStyles}
          onChange={handleChange}
          placeholder="e.g., Casual, Formal"
          style={{ display: 'block', margin: '8px 0', padding: '4px', width: '100%' }}
        />
      </label>
      <label>
        Favorite Colors:
        <input
          type="text"
          name="favoriteColors"
          value={preferences.favoriteColors}
          onChange={handleChange}
          placeholder="e.g., Blue, Black"
          style={{ display: 'block', margin: '8px 0', padding: '4px', width: '100%' }}
        />
      </label>
      <label>
        Favorite Brands:
        <input
          type="text"
          name="favoriteBrands"
          value={preferences.favoriteBrands}
          onChange={handleChange}
          placeholder="e.g., Nike, Gucci"
          style={{ display: 'block', margin: '8px 0', padding: '4px', width: '100%' }}
        />
      </label>
      <div>
        <strong>Favorite Styles:</strong> {preferences.favoriteStyles || 'Not specified'}
      </div>
      <div>
        <strong>Favorite Colors:</strong> {preferences.favoriteColors || 'Not specified'}
      </div>
      <div>
        <strong>Favorite Brands:</strong> {preferences.favoriteBrands || 'Not specified'}
      </div>
    </div>
  );
};

export default UserFashionPreferences;
