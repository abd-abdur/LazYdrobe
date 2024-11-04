# Frontend Guide - LazyDrobe
This guide provides instructions on how to set up, run, and understand the front-end code for the LazyDrobe application. 
LazyDrobe is a React-based wardrobe management app that allows users to manage their clothing items, receive outfit suggestions, and shop for recommended items.

## Prerequisites
Before running this code, make sure you have the following installed:

Node.js (version 14.x or higher)
npm or yarn (npm is included with Node.js)

## Getting Started
Follow these steps to set up and run the front-end code on your local machine.

### Clone the Repository
Start by cloning the repository to your local machine:
git clone https://github.com/username/lazydrobe.git
Replace username with your GitHub username if you forked the repository.

### Navigate into the Project Directory
Change into the project’s directory:
cd lazydrobe

### Install Dependencies
Install the required dependencies using npm or yarn:
Using npm
npm install

OR 

using yarn
yarn install
This will install all the necessary packages, including react, react-router-dom, and react-modal.

### Start the Application

Using npm
npm start

OR using yarn
yarn start
This command will open a new tab in your browser with the app running at http://localhost:3000. If it doesn’t open automatically, navigate to http://localhost:3000 manually.

## Project Structure
lazydrobe/
├── public/
│   └── index.html               # Main HTML file for the React app
├── src/
│   ├── components/              # All React components and their CSS files
│   │   ├── Navbar.js            # Navigation bar component
│   │   ├── Footer.js            # Footer component
│   │   ├── Wardrobe.js          # Main wardrobe screen
│   │   ├── WardrobeItem.js      # Individual wardrobe item component
│   │   ├── WardrobeModal.js     # Modal component for adding/editing wardrobe items
│   │   ├── OutfitSuggestions.js # Outfit suggestion screen
│   │   ├── Navbar.css           # CSS for Navbar
│   │   ├── Footer.css           # CSS for Footer
│   │   ├── Wardrobe.css         # CSS for Wardrobe screen
│   │   ├── WardrobeItem.css     # CSS for individual wardrobe items
│   │   └── OutfitSuggestions.css# CSS for outfit suggestions
│   ├── App.js                   # Main app component with routes
│   ├── index.js                 # Entry point to render the app
│   └── App.css                  # Global styles
├── .gitignore                   # File to exclude unnecessary files from Git
├── README.md                    # General overview and instructions for the project
├── frontend.md                  # Front-end guide (this file)
├── package.json                 # Lists dependencies and scripts
└── package-lock.json            # Locks dependencies to specific versions

## Key Components
Navbar (Navbar.js): Displays navigation links for the app.
Footer (Footer.js): Displays the footer with copyright information.
Wardrobe (Wardrobe.js): Displays the wardrobe items, with filtering functionality.
WardrobeItem (WardrobeItem.js): Represents individual wardrobe items.
WardrobeModal (WardrobeModal.js): Modal for adding or editing wardrobe items.
OutfitSuggestions (OutfitSuggestions.js): Displays outfit recommendations based on weather.

## Additional Notes
Styling: Each component has its own .css file located in src/components. This keeps styles modular and specific to each component.

Routing: The app uses react-router-dom for client-side routing. Routes are defined in App.js, which manages navigation to different parts of the application.

Modal Library: react-modal is used to create the add/edit modal for wardrobe items. You may need to run npm install react-modal if it’s not installed automatically.

## Available Scripts
In the project directory, you can run:

npm start: Runs the app in development mode.
npm run build: Builds the app for production to the build folder.
npm test: Launches the test runner.

## Troubleshooting
If you encounter issues with npm install, ensure that you have the latest version of Node.js and npm.
If the app doesn’t load in the browser, check if the development server is running on http://localhost:3000 and that no other app is using this port.


