# MMORPG Project

A simple MMORPG game built with Python, Pygame, and WebSockets.

## Project Structure

```
mmorpg/
├── src/
│   ├── client/       # Client-side code
│   ├── server/       # Server-side code
│   ├── common/       # Shared code and constants
│   └── assets/       # Game assets
│       ├── images/
│       ├── sounds/
│       └── maps/
├── docs/            # Documentation
├── tests/          # Test files
└── venv/           # Virtual environment (created during setup)
```

## Setup

1. Create and activate a virtual environment:
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate on macOS/Linux
   source venv/bin/activate
   
   # Activate on Windows
   .\venv\Scripts\activate
   ```

2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the server:
   ```bash
   python src/server/main.py
   ```

4. Start the client:
   ```bash
   python src/client/main.py
   ```

## Features

- Basic client-server architecture
- Real-time networking with WebSockets
- 2D graphics with Pygame

## Development

This project is under active development.

## Virtual Environment

The project uses a virtual environment to manage dependencies. Always make sure the virtual environment is activated before running or developing the game:

- The virtual environment is stored in the `venv/` directory
- Activate it using the commands in the Setup section
- To deactivate when you're done:
  ```bash
  deactivate
  ```
- If you install new packages, update requirements.txt:
  ```bash
  pip freeze > requirements.txt
  ```