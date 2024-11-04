// Navbar.js
import React from 'react';
import { NavLink } from 'react-router-dom';
import './Navbar.css';

const Navbar = () => {
  return (
    <nav className="navbar">
      <NavLink exact to="/" activeClassName="active-link">Home</NavLink>
      <NavLink to="/wardrobe" activeClassName="active-link">Wardrobe</NavLink>
      <NavLink to="/outfits" activeClassName="active-link">Outfit Suggestions</NavLink>
      <NavLink to="/weather" activeClassName="active-link">Weather</NavLink>
      <NavLink to="/profile" activeClassName="active-link">Profile</NavLink>
    </nav>
  );
};

export default Navbar;
