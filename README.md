 
21-Day Agent Series: Day 3 AGENT Best-Restaurants-Route-Planner-Agent

Using Google Maps MCP, this agent helps you find the best restaurants in the city you’re exploring during your trip and plans the shortest route to visit them. 🗺️✨

Installation
Prerequisites
Python 3.9 or higher
Git
Virtual environment (recommended)
Steps
Don't forget to download nodejs for mcp
Clone the repository:

git clone <repository-url>
cd <repository-folder>
Install dependencies:

pip install -r requirements.txt
Create a .env file in the root directory and configure it as follows:

AZURE_OPENAI_ENDPOINT="your_azure_openai_endpoint
AZURE_OPENAI_API_VERSION="your_azure_openai_api_version"
AZURE_OPENAI_API_KEY="your_azure_openai_api_key"
GOOGLE_MAPS_API_KEY="YOUR_GOOGLE_MAPS_API_KEY"
Running the Application
Start the FastAPI server:

uvicorn upsonicai:app --reload
Open the UI in your browser:

http://127.0.0.1:8000/
Use the form to input:

GitHub Release URL
Company URL
Product Aim
Click "Generate" to see platform-specific announcements rendered in the UI. Each platform's content will be displayed in separate boxes with a "Copy" button for easy sharing.

API Documentation
Interactive API docs are available at:

Swagger UI: http://127.0.0.1:8000/docs
ReDoc: http://127.0.0.1:8000/redoc
