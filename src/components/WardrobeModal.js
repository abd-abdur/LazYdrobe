// WardrobeModal.js
import React, { useState } from 'react';
import Modal from 'react-modal';

Modal.setAppElement('#root');

const WardrobeModal = ({ isOpen, onRequestClose, onSubmit, item = {} }) => {
  const [name, setName] = useState(item.name || '');
  const [category, setCategory] = useState(item.category || '');
  const [image, setImage] = useState(item.image || '');

  const handleSubmit = () => {
    if (name && category) {
      onSubmit({ ...item, name, category, image });
      onRequestClose();
    }
  };

  return (
    <Modal isOpen={isOpen} onRequestClose={onRequestClose} contentLabel="Wardrobe Item Modal">
      <h2>{item.id ? 'Edit' : 'Add'} Wardrobe Item</h2>
      <form>
        <input type="text" placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} />
        <input type="text" placeholder="Category" value={category} onChange={(e) => setCategory(e.target.value)} />
        <input type="text" placeholder="Image URL" value={image} onChange={(e) => setImage(e.target.value)} />
        <button type="button" onClick={handleSubmit}>Save</button>
      </form>
    </Modal>
  );
};

export default WardrobeModal;
