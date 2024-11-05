# Frontend Guide - LazyDrobe
This guide provides instructions on how to set up, run, and understand the front-end code for the LazyDrobe application. LazyDrobe is a React-based wardrobe management app that allows users to manage clothing items, receive outfit suggestions, and shop for recommended items.

## Prerequisites
Before running this code, ensure you have the following installed:

Node.js (version 14.x or higher)
npm (included with Node.js) or yarn

## Getting Started
Follow these steps to set up and run the front-end code on your local machine.

### 1. Clone the Repository
Clone the repository to your local machine:

bash
Copy code
git clone https://github.com/username/lazydrobe.git
Note: Replace username with your GitHub username if you forked the repository.

### 2. Navigate into the Project Directory
Change to the project’s directory:


cd lazydrobe

### 3. Install Dependencies
Install the necessary packages using npm or yarn:


#### Using npm
npm install

#### OR using yarn
yarn install
This will install all required packages, including react, react-router-dom, and react-modal.

### 4. Start the Application
Start the development server:

#### Using npm
npm start

#### OR using yarn
yarn start
After starting, the app should open automatically in your browser at http://localhost:3000. If it doesn’t, open the link manually.

## Project Structure
Here's an overview of the project directory structure:

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
│   │   └── OutfitSuggestions.css # CSS for outfit suggestions
│   ├── App.js                   # Main app component with routes
│   ├── index.js                 # Entry point to render the app
│   └── App.css                  # Global styles
├── .gitignore                   # Excludes unnecessary files from Git
├── README.md                    # General project overview and instructions
├── frontend.md                  # Front-end setup guide (this file)
├── package.json                 # Lists dependencies and scripts
└── package-lock.json            # Locks dependencies to specific versions

## Key Components
Here are the main components and their purposes:

Navbar (Navbar.js): Displays the navigation links for the app.
Footer (Footer.js): Shows copyright information.
Wardrobe (Wardrobe.js): Displays wardrobe items with filtering functionality.
WardrobeItem (WardrobeItem.js): Represents individual wardrobe items.
WardrobeModal (WardrobeModal.js): Modal for adding/editing wardrobe items.
OutfitSuggestions (OutfitSuggestions.js): Displays outfit recommendations based on weather.

## Additional Notes
Styling: Each component has its own .css file in the src/components folder, keeping styles modular and specific to each component.
Routing: The app uses react-router-dom for client-side routing. Routes are defined in App.js, which manages navigation between different parts of the application.
Modal Library: react-modal is used to create the add/edit modal for wardrobe items. If it’s not installed automatically, run npm install react-modal.

## Available Scripts
In the project directory, you can run:

npm start: Runs the app in development mode.
npm run build: Builds the app for production to the build folder.
npm test: Launches the test runner.

## Troubleshooting
Dependency Issues: If you encounter issues during npm install, make sure you have the latest version of Node.js and npm installed.
Development Server: If the app doesn’t load in the browser, confirm that the development server is running on http://localhost:3000 and that no other app is using this port.

## Contributing
To contribute to LazyDrobe, follow these steps:

Fork the repository.
Create a new branch (git checkout -b feature-branch).
Make your changes.
Commit your changes (git commit -m "Add new feature").
Push to the branch (git push origin feature-branch).
Open a pull request.
