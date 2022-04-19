# CS411 Group 3 Project - Weatherify
This project aims to make a spotify playlist based on your liked songs based on the weather outside!

## Requirements
<ul>
    <li>Python 3.10 (Backend)</li>
    <li>Node.js with npm (Frontend)</li>
    <li>creds.py (Contains API Keys)</li>
    <ul>
        <li>Please email one of us for the file or ask to join our trello</li>
    </ul>
</ul>

## Running Weatherify
There is no environment included in this repo, so having your own install of python and node.js are crucial. 
<ol>
    <li>Put creds.py file in backend folder</li>
    <li>Create python virutal enviornment (or use base) and install from requirements.txt</li>
    <ul>
        <li>(Create Virtual Environment) python3 -m venv name_of_venv</li>
        <li>(Activate Virtual Environment) name_of_venv\Scripts\activate.bat</li>
        <li>(Install packages from Requirements.txt) pip install -r /path/to/requirements.txt</li>
    </ul>
    <li>Run App.py to start the backend</li>
    <li>Make sure to install node.js and npm</li>
    <ul>
        <li>Check installs with node -v and npm -v in terminal</li>
        <li>This project works with node version 16.14.2 and npm version 8.5.0</li>
    </ul>
    <li>cd to frontend folder in terminal</li>
    <li>Run npm install in terminal</li>
    <li>Run npm run dev in terminal</li>
    <li>Lastly, go to localhost:3000</li>
</ol>

## Backend Contents
<ul>
    <li>app.py - Main flask program for backend (only necessary file to run)</li>
    <li>weather_access.py - Contains methods for interacting with openweather api</li>
    <li>user_remover.py - Currently does not run. Will remove users from database after an hour of inactivity</li>
</ul>

## Frontend Contents
<ul>
    <li>public/ - Contains title icon</li> 
    <li>src/index.html - Our main html page metadata and frame to put our template in</li>
    <li>src/assets/ - (Empty) Contains images and css used by our website</li>
    <li>src/components/ - (Empty) Contains different router components</li>
    <li>src/App.vue - Contains our main frontend template html and javascript</li>
    <li>src/main.js - Runs and sets up App.vue</li>
    <li>src/vite.config.js - Contains options for our vite app (honestly I don't know if anything in there is useful, we may test getting rid of it later)</li>
    <li>src/package.json - Contains info for npm install like dependencies</li>
</ul>

## Docs Contents
<ul>
    <li>UserStories/ - Contains 5 user stories for our app</li>
    <li>Project_Proposal.pdf - a pdf containing our original project proposal</li>
</ul>


