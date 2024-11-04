import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Wardrobe from './components/Wardrobe';
import OutfitSuggestions from './components/OutfitSuggestions';

function App() {
  return (
    <Router>
      <div>
        <Navbar />
        <Switch>
          <Route path="/wardrobe">
            <Wardrobe items={[]} /> {/* Replace with actual items */}
          </Route>
          <Route path="/outfits">
            <OutfitSuggestions outfits={[]} /> {/* Replace with actual outfits */}
          </Route>
          <Route path="/">
            <h1>Welcome to LazyDrobe!</h1>
          </Route>
        </Switch>
        <Footer />
      </div>
    </Router>
  );
}

export default App;
