from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from upsonic import UpsonicClient, Task, AgentConfiguration, ObjectResponse
import os

print(os.getenv("AZURE_OPENAI_ENDPOINT"))
# Upsonic Client'ı Başlat
client = UpsonicClient("localserver")
client.set_config("AZURE_OPENAI_ENDPOINT", os.getenv("AZURE_OPENAI_ENDPOINT"))
client.set_config("AZURE_OPENAI_API_VERSION", os.getenv("AZURE_OPENAI_API_VERSION"))
client.set_config("AZURE_OPENAI_API_KEY", os.getenv("AZURE_OPENAI_API_KEY"))

client.default_llm_model = "azure/gpt-4o"

# Google Maps MCP Tanımla
@client.mcp()
class GoogleMapsMCP:
    command = "npx"
    args = [
        "-y",
        "@modelcontextprotocol/server-google-maps"
    ]
    env = {
        "GOOGLE_MAPS_API_KEY": os.getenv("GOOGLE_MAPS_API_KEY")
    }

# FastAPI Uygulamasını Başlat
app = FastAPI()

# Kullanıcı Girdisi Modeli
class RestaurantInput(BaseModel):
    city: str

# Yanıt Modelleri
class Restaurant(ObjectResponse):
    name: str
    address: str
    rating: float
    price_level: str
    cuisine: list[str]

class RestaurantListResponse(ObjectResponse):
    restaurants: list[Restaurant]

class RestaurantRouteResponse(ObjectResponse):
    ordered_restaurants: list[Restaurant]
    total_distance: str
    estimated_time: str

@app.post("/find-best-restaurants/")
async def find_best_restaurants(input_data: RestaurantInput):
    # Ajan Tanımı
    restaurant_agent = AgentConfiguration(
        job_title="Food Explorer",
        company_url="https://upsonic.ai",
        company_objective="Find the best restaurants and optimize visit routes.",
        reflection=True
    )

    # 1️⃣ İlk Görev: Popüler Restoranları Bul
    find_restaurants_task = Task(
        description=f"Find the best restaurants in {input_data.city}. Include name, address, rating, cuisine, and price level.",
        tools=[],
        response_format=RestaurantListResponse
    )

    client.call(find_restaurants_task)
    restaurants_data = find_restaurants_task.response
    if not restaurants_data:
        raise HTTPException(status_code=500, detail="Failed to find restaurants.")

    # 2️⃣ Google Maps Kullanarak Restoranları Doğrula
    verify_restaurants_task = Task(
        description=f"Verify the top restaurants in {input_data.city} using Google Maps. Ensure the data is correct.",
        tools=[GoogleMapsMCP],
        response_format=RestaurantListResponse,
        context=[find_restaurants_task]
    )

    client.agent(restaurant_agent, verify_restaurants_task)
    verified_restaurants = verify_restaurants_task.response
    if not verified_restaurants:
        raise HTTPException(status_code=500, detail="Failed to verify restaurants.")

    # 3️⃣ Restoranları En Kısa Rotaya Göre Sırala
    optimize_route_task = Task(
        description="Generate the shortest possible route to visit the best restaurants while minimizing travel distance.",
        tools=[GoogleMapsMCP],
        response_format=RestaurantRouteResponse,
        context=[verified_restaurants]
    )

    client.agent(restaurant_agent, optimize_route_task)
    route_data = optimize_route_task.response
    if not route_data:
        raise HTTPException(status_code=500, detail="Failed to generate an optimized route.")

    return {
        "top_restaurants": verified_restaurants.restaurants,
        "optimized_route": {
            "ordered_restaurants": route_data.ordered_restaurants,
            "total_distance": route_data.total_distance,
            "estimated_time": route_data.estimated_time
        }
    }

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Restaurant Explorer</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 0;
            background: #f9f9f9;
            color: #333;
        }

        header {
            background: #ff5733;
            color: white;
            padding: 15px 20px;
            text-align: center;
            box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.2);
        }

        h1 {
            margin: 0;
        }

        .container {
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            background: white;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
        }

        form {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        label {
            font-weight: bold;
        }

        input, button {
            font-size: 16px;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            width: 100%;
        }

        button {
            background: #ff5733;
            color: white;
            font-weight: bold;
            border: none;
            cursor: pointer;
            transition: background 0.3s ease;
        }

        button:hover {
            background: #c70039;
        }

        #results {
            margin-top: 20px;
            padding: 15px;
            background: #f4f4f4;
            border-radius: 8px;
            white-space: pre-wrap;
            word-wrap: break-word;
        }

        footer {
            text-align: center;
            margin-top: 30px;
            font-size: 0.9em;
            color: #555;
        }

        footer a {
            color: #ff5733;
            text-decoration: none;
        }

        footer a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>

<header>
    <h1>🍽️ Best-Restaurants-Route-Planner-Agent</h1>
</header>

<div class="container">
    <form id="restaurant-form">
        <label for="city">🌍 Enter a City:</label>
        <input type="text" id="city" name="city" placeholder="E.g., New York, Tokyo, Paris" required>

        <button type="button" onclick="submitForm()">Find Best Restaurants</button>
    </form>

    <div id="results" style="display: none;">
        <h2>Results:</h2>
        <pre id="results-content"></pre>
    </div>
</div>

<footer>
    Powered by <a href="https://upsonic.ai" target="_blank">UpsonicAI</a> | © 2025
</footer>

<script>
    async function submitForm() {
        const city = document.getElementById('city').value;

        const button = document.querySelector('button');
        button.disabled = true;
        button.textContent = 'Finding...';

        try {
            const response = await fetch('/find-best-restaurants/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ city })
            });

            if (response.ok) {
                const data = await response.json();
                document.getElementById('results').style.display = 'block';
                document.getElementById('results-content').textContent = JSON.stringify(data, null, 2);
            } else {
                document.getElementById('results').style.display = 'block';
                document.getElementById('results-content').textContent = 'Error: Could not fetch data.';
            }
        } catch (error) {
            document.getElementById('results').style.display = 'block';
            document.getElementById('results-content').textContent = 'Error: Something went wrong.';
        }

        button.disabled = false;
        button.textContent = 'Find Best Restaurants';
    }
</script>

</body>
</html>
    """
