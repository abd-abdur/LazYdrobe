// Wardrobe.js
import React, { useState } from 'react';
import WardrobeItem from './WardrobeItem';
import './Wardrobe.css';

const Wardrobe = ({ items }) => {
  const [filter, setFilter] = useState('');

  const filteredItems = items.filter(item => 
    item.category.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <div className="wardrobe">
      <input 
        type="text" 
        placeholder="Filter by category" 
        value={filter}
        onChange={(e) => setFilter(e.target.value)}
      />
      <div className="wardrobe-grid">
        {filteredItems.map(item => (
          <WardrobeItem key={item.id} item={item} />
        ))}
      </div>
    </div>
  );
};

export default Wardrobe;
