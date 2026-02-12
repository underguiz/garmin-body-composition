#!/usr/bin/env python3
"""Mobile-friendly web application for submitting body composition data to Garmin Connect."""

import logging
import os
from datetime import date, datetime
from pathlib import Path

from flask import Flask, render_template, request, jsonify, session
from garth.exc import GarthHTTPError
from garminconnect import (
    Garmin,
    GarminConnectAuthenticationError,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "your-secret-key-change-this")

# Configuration
GARMIN_EMAIL = os.environ.get("EMAIL")
GARMIN_PASSWORD = os.environ.get("PASSWORD")
TOKEN_STORE = Path(os.environ.get("GARMINTOKENS", "~/.garminconnect")).expanduser()

# Global Garmin API instance
api = None


def init_api():
    """Initialize Garmin API with authentication."""
    global api
    
    try:
        if api is not None:
            return api
            
        logger.info("Initializing Garmin API...")
        
        # Try to load existing tokens
        if TOKEN_STORE.exists():
            logger.info("Loading existing tokens...")
            api = Garmin()
            api.login(str(TOKEN_STORE))
            logger.info("Successfully logged in with existing tokens")
            return api
        
        # If no tokens, authenticate with credentials
        if not GARMIN_EMAIL or not GARMIN_PASSWORD:
            raise ValueError(
                "No stored tokens found and EMAIL/PASSWORD environment variables not set. "
                "Please set EMAIL and PASSWORD environment variables."
            )
        
        logger.info("Authenticating with credentials...")
        api = Garmin(GARMIN_EMAIL, GARMIN_PASSWORD)
        api.login()
        
        # Save tokens for future use
        TOKEN_STORE.parent.mkdir(parents=True, exist_ok=True)
        api.garth.dump(str(TOKEN_STORE))
        logger.info(f"Tokens saved to {TOKEN_STORE}")
        
        return api
        
    except GarminConnectAuthenticationError as e:
        logger.error(f"Authentication failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Error initializing API: {e}")
        raise


@app.route("/")
def index():
    """Render the main form page."""
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit_body_composition():
    """Handle form submission and send data to Garmin Connect."""
    try:
        # Get form data
        data = request.get_json()
        weight = float(data.get("weight"))
        bmi = float(data.get("bmi"))
        body_fat = float(data.get("bodyFat"))
        
        # Validate input
        if not (30 <= weight <= 300):
            return jsonify({
                "success": False,
                "error": "Weight must be between 30 and 300 kg"
            }), 400
            
        if not (10 <= bmi <= 60):
            return jsonify({
                "success": False,
                "error": "BMI must be between 10 and 60"
            }), 400
            
        if not (3 <= body_fat <= 60):
            return jsonify({
                "success": False,
                "error": "Body fat percentage must be between 3 and 60"
            }), 400
        
        # Initialize API if needed
        garmin_api = init_api()
        
        # Get today's date
        today = date.today().isoformat()
        
        logger.info(f"Submitting body composition: weight={weight}, BMI={bmi}, body_fat={body_fat}%")
        
        # Submit to Garmin Connect
        result = garmin_api.add_body_composition(
            today,
            weight=weight,
            percent_fat=body_fat,
            bmi=bmi,
        )
        
        logger.info("Body composition data submitted successfully")
        
        return jsonify({
            "success": True,
            "message": "Body composition data submitted successfully!",
            "data": {
                "date": today,
                "weight": weight,
                "bmi": bmi,
                "bodyFat": body_fat
            }
        })
        
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        return jsonify({
            "success": False,
            "error": f"Invalid input: {str(e)}"
        }), 400
        
    except GarminConnectAuthenticationError as e:
        logger.error(f"Authentication error: {e}")
        return jsonify({
            "success": False,
            "error": "Authentication failed. Please check your credentials."
        }), 401
        
    except GarminConnectConnectionError as e:
        logger.error(f"Connection error: {e}")
        return jsonify({
            "success": False,
            "error": "Connection error. Please check your internet connection."
        }), 503
        
    except GarminConnectTooManyRequestsError as e:
        logger.error(f"Rate limit error: {e}")
        return jsonify({
            "success": False,
            "error": "Too many requests. Please wait a moment and try again."
        }), 429
        
    except GarthHTTPError as e:
        logger.error(f"Garmin API error: {e}")
        return jsonify({
            "success": False,
            "error": f"Garmin API error: {str(e)}"
        }), 500
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({
            "success": False,
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500


@app.route("/health")
def health():
    """Health check endpoint."""
    try:
        garmin_api = init_api()
        return jsonify({
            "status": "healthy",
            "garmin_connected": garmin_api is not None
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500


if __name__ == "__main__":
    # Initialize API on startup
    try:
        init_api()
        logger.info("Garmin API initialized successfully")
    except Exception as e:
        logger.warning(f"Could not initialize API on startup: {e}")
        logger.info("Will retry on first request")
    
    # Run the Flask app
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
