# Garmin Body Composition Web App

A mobile-friendly web application for submitting body composition data to Garmin Connect.

## Setup

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables:**
   ```bash
   export EMAIL="your-garmin-email@example.com"
   export PASSWORD="your-garmin-password"
   ```

   Optional:
   ```bash
   export GARMINTOKENS="~/.garminconnect"  # Token storage location
   export SECRET_KEY="your-secret-key"      # Flask secret key
   export PORT="8080"                        # Server port (default: 8080)
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Open in browser:**
   Navigate to `http://localhost:8080` (or `http://your-ip:8080` on mobile)

## Docker Deployment

### Build and run with Docker:

```bash
# Build the image
docker build -t garmin-body-composition .

# Run the container
docker run -d \
  -p 8080:8080 \
  -e EMAIL="your-email@example.com" \
  -e PASSWORD="your-password" \
  -e SECRET_KEY="your-secret-key" \
  -v garmin-tokens:/app/.garminconnect \
  --name garmin-app \
  garmin-body-composition
```

## Mobile Access

To access from your phone on the same network:

1. Find your computer's IP address:
   - macOS: `ifconfig | grep "inet " | grep -v 127.0.0.1`
   - Linux: `ip addr show | grep "inet " | grep -v 127.0.0.1`
   - Windows: `ipconfig`

2. On your phone, navigate to: `http://YOUR-IP:8080`

## API Endpoints

- `GET /` - Main form page
- `POST /submit` - Submit body composition data
- `GET /health` - Health check endpoint

## Disclaimer

This project was heavily vibecoded. This project uses the garminconnect library, see their documentation for API details.
