# LazYdrobe API Documentation

## API Overview

The **LazYdrobe API** is a RESTful interface designed to interact with the LazYdrobe wardrobe management system. It enables users and developers to perform essential CRUD (Create, Read, Update, Delete) operations on clothing items within the application. By leveraging this API, users can manage their wardrobe effectively allowing the application to generate personalized outfit suggestions based on weather conditions, current fashion trends, and user preferences.

## Prerequisites

Before setting up **LazYdrobe**, ensure that you have the following tools installed:

- **MySQL** or a MySQL-compatible database management system (DBMS), such as MariaDB.
- **Python** (version 3.7 or higher).
- **Git** (optional, for cloning the repository).
- **A MySQL Query Editor** (e.g., MySQL Workbench, phpMyAdmin, or DBeaver).
- **Pip** (to manage Python package installations).

## Installation

Follow these steps to set up the LazYdrobe project locally:


### Step 1: Clone the Repository
First, clone the repository where the SQL script is stored. This will allow you to access the SQL file required to set up the database.
git clone https://github.com/abd-abdur/LazYdrobe.git

### Step 2: Navigate to the Project Directory
After cloning the repository, navigate to the directory containing the project.
cd path/to/LazYdrobe

### Step 3: Set Up a Virtual Environment
For Python-based projects, it's recommended to use a virtual environment to isolate project dependencies.
```python -m venv .venv```

Activate the virtual environment:
On Windows: 
```.\.venv\Scripts\activate```
On macOS/Linux: source 
```.venv/bin/activate```

### Step 4: Install Required Dependencies
Install the required packages from the requirements.txt file.
```pip install -r requirements.txt```

### Step 5: Configure Database Connection
Ensure that the database credentials in main.py (or a separate configuration file) match your local database setup.


## Running the API Application


To run the FastAPI application, follow these steps:

1. Open your terminal or command prompt.
2. Navigate to the directory where your `main.py` file is located.
3. Use the following command to start the application:

   ```bash
   uvicorn main:app --reload
   ```

4. Once the server is running, you can access the application locally at: http://127.0.0.1:8000

## Using Postman to Interact with the API

You can use Postman to test the API endpoints. Here’s how to set it up:

### Step 1: Open Postman
Launch the Postman application or access it through the web.

### Step 2: Create a New Collection
1. Click on the **Collections** tab.
2. Create a new collection named **"LazYdrobe API Tests"**.

### Step 3: Add Requests
Follow the structure below for each request:

#### 1. Retrieve All Clothing Users
- **Method**: `GET`
- **Endpoint**: `http://127.0.0.1:8000/users/`
- **Expected Output**: JSON array of users

#### 2. Retrieve a Specific User by ID
- **Method**: `GET`
- **Endpoint**: `http://127.0.0.1:8000/users/{user_id}`
- **Expected Output**: JSON object of user

#### 3. Create a New User
- **Method**: `POST`
- **Endpoint**: `http://127.0.0.1:8000/users/`
- **JSON Input**:
    ```json
    {
    "username": "john_doe",
    "email": "john.doe@example.com",
    "password": "SecurePass123",
    "location": "New York",
    "preferences": ["casual", "summer"]
}
    ```
- **Expected Output**: JSON object of the created user.

#### 4. Update an Existing User
- **Method**: `PUT`
- **Endpoint**: `http://127.0.0.1:8000/users/{user_id}`
- **JSON Input**:
    ```json
    {
    "username": "john_updated",
    "email": "john_updated@example.com",
    "location": "San Francisco",
    "preferences": ["Sporty", "Casual"]
}
    ```
- **Expected Output**: JSON object of the updated user.

#### 5. Delete a User by ID
- **Method**: `DELETE`
- **Endpoint**: `http://127.0.0.1:8000/users/{user_id}`
- **Expected Output**:
    ```
    204 No Content
    ```
For reference, you can find all the API tests in the [Postman_Tests.txt](Postman_Tests.txt) file. This file contains descriptions of each API endpoint including method types, expected inputs, and outputs.

## Conclusion

The **LazYdrobe API** provides a robust and flexible interface for interacting with the wardrobe management application enabling users to perform essential CRUD operations on clothing items. By following the steps outlined above, you can easily set up, test, and utilize the API to meet your wardrobe management needs. This API is designed for developers looking to integrate personalized outfit suggestions based on user preferences and weather data into their applications.