## Setting Up a Python Virtual Environment (.venv)

Before launching the project, it is recommended to create a virtual environment to isolate dependencies.

### Steps:

1. **Open a terminal in the project root directory.**

2. **Create a virtual environment:**
	 ```powershell
	 python -m venv .venv
	 ```

3. **Activate the virtual environment:**
	 - On Windows (PowerShell):
		 ```powershell
		 .venv\Scripts\Activate.ps1
		 ```
	 - On Windows (Command Prompt):
		 ```cmd
		 .venv\Scripts\activate.bat
		 ```
	 - On macOS/Linux:
		 ```bash
		 source .venv/bin/activate
		 ```

4. **Install project dependencies:**
	 ```powershell
	 pip install -r requirements.txt
	 ```

5. **Set the SECRET_KEY environment variable before launching the backend:**
	 - The Flask backend requires an environment variable called `SECRET_KEY` for JWT authentication and session security.
	 - Choose a strong, random secret key. Example: `PCNsflZmB8cPjuLgBBjsUqBIIqKDxZVC`
	 - On Windows (PowerShell):
		 ```powershell
		 $env:SECRET_KEY = "your_secret_key_here"
		 ```
	 - On Windows (Command Prompt):
		 ```cmd
		 set SECRET_KEY=your_secret_key_here
		 ```
	 - On macOS/Linux:
		 ```bash
		 export SECRET_KEY=your_secret_key_here
		 ```

## Running Frontend and Backend Servers

To run the frontend and backend servers simultaneously, use two separate terminal windows:

### 1. Start the Backend (API)
Open a terminal in the `/api` directory and run:
```powershell
py api.py
```

### 2. Start the Frontend (Static Web Server)
Open a separate terminal in the `/web` directory and run:
```powershell
py serve_web.py
```

### 3. Access the Application
- Frontend: Visit `http://localhost:8080/` in your browser for the static site.
- Backend: The API will be available at `http://localhost:5000/`.