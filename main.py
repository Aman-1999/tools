import asyncio
import time
from typing import Dict, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from loguru import logger

from config import settings
from models import (
    RankingRequest, RankingResults, SuccessResponse, ErrorResponse,
    APIStatus, RankingSummary, BulkRankingRequest
)
from services.dataforseo_client import DataForSEOClient
from services.geocoding_client import GeocodingClient

# Initialize FastAPI app
app = FastAPI(
    title="Rank Tracker Prototype",
    description="A prototype rank tracking tool using DataForSEO API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize clients
geocoding_client = GeocodingClient()

# Configure logging
logger.add(
    "logs/rank_tracker_{time}.log", 
    rotation="1 day", 
    retention="7 days",
    level="INFO"
)

@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info("Rank Tracker Prototype starting up...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"DataForSEO URL: {settings.dataforseo_url}")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML interface"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Rank Tracker Prototype</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * { box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                max-width: 1200px; 
                margin: 0 auto; 
                padding: 20px;
                background: #f8f9fa;
                color: #333;
            }
            .header {
                text-align: center;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 15px;
                margin-bottom: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            }
            .header h1 { margin: 0; font-size: 2.5em; font-weight: 300; }
            .header p { margin: 10px 0 0 0; opacity: 0.9; }
            .container { 
                background: white; 
                padding: 30px; 
                border-radius: 15px; 
                margin: 20px 0;
                box-shadow: 0 5px 20px rgba(0,0,0,0.08);
                border: 1px solid #e9ecef;
            }
            .form-group { 
                margin-bottom: 20px; 
            }
            label { 
                display: block; 
                margin-bottom: 8px; 
                font-weight: 600;
                color: #495057;
            }
            input, select, textarea { 
                width: 100%; 
                padding: 12px 15px; 
                border: 2px solid #e9ecef; 
                border-radius: 8px; 
                font-size: 16px;
                transition: border-color 0.3s ease;
            }
            input:focus, select:focus, textarea:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }
            .btn { 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; 
                padding: 15px 30px; 
                border: none; 
                border-radius: 8px; 
                cursor: pointer; 
                font-size: 16px;
                font-weight: 600;
                transition: transform 0.2s ease, box-shadow 0.2s ease;
                width: 100%;
            }
            .btn:hover { 
                transform: translateY(-2px);
                box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
            }
            .btn:disabled {
                opacity: 0.6;
                transform: none;
                cursor: not-allowed;
            }
            .results { 
                margin-top: 30px;
                display: none;
            }
            .loading {
                text-align: center;
                padding: 40px;
                display: none;
            }
            .spinner {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #667eea;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                animation: spin 1s linear infinite;
                margin: 0 auto 20px;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .result-section {
                margin: 20px 0;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 10px;
                border-left: 5px solid #667eea;
            }
            .result-item {
                background: white;
                margin: 10px 0;
                padding: 15px;
                border-radius: 8px;
                border: 1px solid #e9ecef;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            }
            .position {
                display: inline-block;
                background: #667eea;
                color: white;
                padding: 5px 10px;
                border-radius: 20px;
                font-weight: bold;
                font-size: 14px;
                margin-right: 10px;
            }
            .domain {
                color: #28a745;
                font-weight: 600;
            }
            .title {
                font-weight: 600;
                color: #495057;
                margin: 5px 0;
            }
            .description {
                color: #6c757d;
                font-size: 14px;
                line-height: 1.4;
            }
            .error {
                background: #f8d7da;
                border: 1px solid #f5c6cb;
                color: #721c24;
                padding: 15px;
                border-radius: 8px;
                margin: 20px 0;
            }
            .success {
                background: #d4edda;
                border: 1px solid #c3e6cb;
                color: #155724;
                padding: 15px;
                border-radius: 8px;
                margin: 20px 0;
            }
            .info-box {
                background: #e3f2fd;
                border: 1px solid #bbdefb;
                color: #1565c0;
                padding: 15px;
                border-radius: 8px;
                margin: 20px 0;
            }
            .row {
                display: flex;
                gap: 20px;
                flex-wrap: wrap;
            }
            .col {
                flex: 1;
                min-width: 300px;
            }
            @media (max-width: 768px) {
                body { padding: 10px; }
                .header { padding: 20px; }
                .header h1 { font-size: 2em; }
                .container { padding: 20px; }
                .row { flex-direction: column; }
                .col { min-width: unset; }
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🎯 Rank Tracker Prototype</h1>
            <p>Track organic and Google Maps rankings with precision</p>
        </div>

        <div class="container">
            <div class="info-box">
                <strong>🚀 Ready to track rankings!</strong><br>
                Enter a keyword and location below to check both organic search results and Google Maps rankings.
                The system supports addresses, PIN codes, cities, and will automatically geocode your location.
            </div>

            <form id="rankingForm">
                <div class="row">
                    <div class="col">
                        <div class="form-group">
                            <label for="keyword">🔍 Keyword to Track</label>
                            <input type="text" id="keyword" name="keyword" 
                                   placeholder="e.g., pizza restaurant, dentist near me" required>
                        </div>

                        <div class="form-group">
                            <label for="location">📍 Location (Address/City)</label>
                            <input type="text" id="location" name="location" 
                                   placeholder="e.g., New York, NY or 123 Main St, Boston" required>
                        </div>

                        <div class="form-group">
                            <label for="pincode">📮 PIN Code/Postal Code (Optional)</label>
                            <input type="text" id="pincode" name="pincode" 
                                   placeholder="e.g., 10001, 90210">
                        </div>
                    </div>

                    <div class="col">
                        <div class="form-group">
                            <label for="device">📱 Device Type</label>
                            <select id="device" name="device">
                                <option value="desktop">🖥️ Desktop</option>
                                <option value="mobile">📱 Mobile</option>
                            </select>
                        </div>

                        <div class="form-group">
                            <label for="language">🌍 Language</label>
                            <select id="language" name="language">
                                <option value="en">🇺🇸 English</option>
                                <option value="es">🇪🇸 Spanish</option>
                                <option value="fr">🇫🇷 French</option>
                                <option value="de">🇩🇪 German</option>
                                <option value="it">🇮🇹 Italian</option>
                            </select>
                        </div>

                        <div class="form-group">
                            <label for="depth">📊 Results Depth</label>
                            <select id="depth" name="depth">
                                <option value="20">Top 20 Results</option>
                                <option value="40" selected>Top 40 Results</option>
                                <option value="60">Top 60 Results</option>
                                <option value="100">Top 100 Results</option>
                            </select>
                        </div>
                    </div>
                </div>

                <button type="submit" class="btn" id="submitBtn">
                    🚀 Check Rankings Now
                </button>
            </form>
        </div>

        <div class="loading" id="loading">
            <div class="spinner"></div>
            <h3>🔍 Checking Rankings...</h3>
            <p>This may take 10-30 seconds depending on the depth requested.</p>
        </div>

        <div class="results" id="results"></div>

        <script>
            document.getElementById('rankingForm').addEventListener('submit', async function(e) {
                e.preventDefault();

                const formData = {
                    keyword: document.getElementById('keyword').value,
                    location: {
                        address: document.getElementById('location').value,
                        pincode: document.getElementById('pincode').value || null
                    },
                    device: document.getElementById('device').value,
                    language_code: document.getElementById('language').value,
                    depth: parseInt(document.getElementById('depth').value)
                };

                // Show loading state
                document.getElementById('loading').style.display = 'block';
                document.getElementById('results').style.display = 'none';
                document.getElementById('submitBtn').disabled = true;

                try {
                    const response = await fetch('/api/check-rankings', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(formData)
                    });

                    const data = await response.json();

                    if (response.ok) {
                        displayResults(data);
                    } else {
                        displayError(data.detail || 'An error occurred');
                    }
                } catch (error) {
                    displayError('Network error: ' + error.message);
                } finally {
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('submitBtn').disabled = false;
                }
            });

            function displayResults(data) {
                const resultsDiv = document.getElementById('results');

                let html = `
                    <div class="container">
                        <h2>📊 Ranking Results</h2>
                        <div class="success">
                            ✅ Successfully checked rankings for "<strong>${data.keyword}</strong>" 
                            at location: <strong>${data.location.address}</strong>
                        </div>
                `;

                // Location info
                html += `
                    <div class="result-section">
                        <h3>📍 Location Information</h3>
                        <div class="result-item">
                            <strong>📌 Geocoded Address:</strong> ${data.location.address}<br>
                            <strong>🗺️ Coordinates:</strong> ${data.location.latitude}, ${data.location.longitude}<br>
                            <strong>🏙️ City:</strong> ${data.location.city || 'N/A'}<br>
                            <strong>🌍 Country:</strong> ${data.location.country || 'N/A'}
                        </div>
                    </div>
                `;

                // Organic results
                if (data.organic_results && data.organic_results.length > 0) {
                    html += `
                        <div class="result-section">
                            <h3>🔍 Organic Search Results (${data.organic_results.length} found)</h3>
                    `;

                    data.organic_results.forEach(result => {
                        html += `
                            <div class="result-item">
                                <span class="position">#${result.position}</span>
                                <div class="domain">${result.domain || result.url}</div>
                                <div class="title">${result.title || 'No title'}</div>
                                <div class="description">${result.description || 'No description available'}</div>
                            </div>
                        `;
                    });

                    html += '</div>';
                } else {
                    html += `
                        <div class="result-section">
                            <h3>🔍 Organic Search Results</h3>
                            <div class="result-item">
                                ℹ️ No organic results found or unable to fetch data.
                            </div>
                        </div>
                    `;
                }

                // Maps results
                if (data.maps_results && data.maps_results.length > 0) {
                    html += `
                        <div class="result-section">
                            <h3>📍 Google Maps Results (${data.maps_results.length} found)</h3>
                    `;

                    data.maps_results.forEach(result => {
                        html += `
                            <div class="result-item">
                                <span class="position">#${result.position}</span>
                                <div class="title">${result.title || 'Business Name'}</div>
                                <div class="description">
                                    📍 ${result.address || 'Address not available'}<br>
                                    ${result.phone ? `📞 ${result.phone}<br>` : ''}
                                    ${result.rating ? `⭐ ${result.rating} (${result.reviews_count || 0} reviews)<br>` : ''}
                                    ${result.website ? `🌐 ${result.website}` : ''}
                                </div>
                            </div>
                        `;
                    });

                    html += '</div>';
                } else {
                    html += `
                        <div class="result-section">
                            <h3>📍 Google Maps Results</h3>
                            <div class="result-item">
                                ℹ️ No maps results found or unable to fetch data.
                            </div>
                        </div>
                    `;
                }

                // Metadata
                html += `
                    <div class="result-section">
                        <h3>📋 Check Details</h3>
                        <div class="result-item">
                            <strong>🕐 Check Time:</strong> ${new Date(data.check_date).toLocaleString()}<br>
                            <strong>📱 Device:</strong> ${data.device}<br>
                            <strong>🌍 Language:</strong> ${data.language_code}<br>
                            <strong>📊 Depth:</strong> Top ${data.depth} results requested
                        </div>
                    </div>
                `;

                html += '</div>';

                resultsDiv.innerHTML = html;
                resultsDiv.style.display = 'block';
                resultsDiv.scrollIntoView({ behavior: 'smooth' });
            }

            function displayError(message) {
                const resultsDiv = document.getElementById('results');
                resultsDiv.innerHTML = `
                    <div class="container">
                        <div class="error">
                            ❌ <strong>Error:</strong> ${message}
                        </div>
                    </div>
                `;
                resultsDiv.style.display = 'block';
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.get("/api/status")
async def api_status():
    """Check API status and connectivity"""
    status = {
        "dataforseo": {"status": "unknown", "url": settings.dataforseo_url},
        "geocoding": {"status": "unknown", "providers": []}
    }

    # Check DataForSEO connection
    try:
        async with DataForSEOClient() as client:
            test_result = await client.test_connection()
            status["dataforseo"]["status"] = "connected" if test_result else "error"
    except Exception as e:
        status["dataforseo"]["status"] = f"error: {str(e)}"

    # Check geocoding services
    try:
        geocoding_status = await geocoding_client.get_status()
        status["geocoding"] = geocoding_status
    except Exception as e:
        status["geocoding"]["status"] = f"error: {str(e)}"

    return status

@app.post("/api/check-rankings", response_model=RankingResults)
async def check_rankings(request: RankingRequest):
    """Main endpoint to check rankings"""
    start_time = time.time()

    try:
        logger.info(f"Processing ranking request for keyword: {request.keyword}")

        # Step 1: Geocode the location
        logger.info("Geocoding location...")
        location_data = await geocoding_client.geocode_location(request.location)
        logger.info(f"Geocoded to: {location_data.latitude}, {location_data.longitude}")

        # Step 2: Get rankings from DataForSEO
        logger.info("Fetching ranking data...")
        async with DataForSEOClient() as client:
            organic_results, maps_results = await asyncio.gather(
                client.get_organic_rankings(request, location_data),
                client.get_maps_rankings(request, location_data),
                return_exceptions=True
            )

            # Handle exceptions in results
            if isinstance(organic_results, Exception):
                logger.error(f"Organic rankings error: {organic_results}")
                organic_results = []

            if isinstance(maps_results, Exception):
                logger.error(f"Maps rankings error: {maps_results}")
                maps_results = []

        # Step 3: Create response
        processing_time = time.time() - start_time

        response = RankingResults(
            keyword=request.keyword,
            location=location_data,
            device=request.device,
            language_code=request.language_code,
            depth=request.depth,
            organic_results=organic_results,
            maps_results=maps_results,
            check_date=datetime.utcnow(),
            processing_time_seconds=round(processing_time, 2)
        )

        logger.info(f"Request completed in {processing_time:.2f}s")
        return response

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    import os

    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)

    # Run the server
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level="info"
    )