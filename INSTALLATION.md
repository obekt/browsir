# Installation Guide - BrowSir API

Complete guide to install and run the BrowSir API on any machine using Docker.

## Prerequisites

### Required Software
- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher

### System Requirements
- **OS**: Linux, macOS, or Windows with WSL2
- **RAM**: Minimum 2GB, recommended 4GB
- **Disk**: 2GB free space
- **Network**: Internet connection for Docker images and API calls

### Get Docker

#### macOS
```bash
# Install Docker Desktop
brew install --cask docker

# Or download from: https://www.docker.com/products/docker-desktop
```

#### Linux (Ubuntu/Debian)
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt-get update
sudo apt-get install docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

#### Windows
1. Install WSL2: https://docs.microsoft.com/en-us/windows/wsl/install
2. Install Docker Desktop: https://www.docker.com/products/docker-desktop
3. Enable WSL2 integration in Docker Desktop settings

### Verify Installation
```bash
docker --version
# Should show: Docker version 20.10.x or higher

docker-compose --version
# Should show: Docker Compose version 2.x.x or higher
```

## Installation Steps

### 1. Get the Code

#### Option A: Clone from Git
```bash
git clone <repository-url>
cd browserAPI
```

#### Option B: Download ZIP
1. Download the project ZIP file
2. Extract to a directory
3. Open terminal in that directory

### 2. Configure OpenAI API Key

#### Get Your API Key
1. Go to: https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)

#### Set the API Key

Edit the `.env` file:
```bash
# Open in your text editor
nano .env
# or
vim .env
# or use any text editor
```

Replace `your-openai-api-key-here` with your actual key:
```bash
OPENAI_API_KEY=sk-proj-abc123...your-actual-key
```

Save and close the file.

**Important**: Never commit this file to Git! It's already in `.gitignore`.

### 3. Build and Start

```bash
# Build the Docker image
docker-compose build

# Start the service
docker-compose up -d
```

The `-d` flag runs it in the background (detached mode).

### 4. Verify It's Running

```bash
# Check container status
docker-compose ps

# Should show:
# NAME                IMAGE               STATUS
# browser-api-1       browserapi-browser-api   Up X seconds

# Test the health endpoint
curl http://localhost:8000/health

# Should return:
# {"status":"healthy","timestamp":"2025-11-04T10:00:00.000000"}
```

### 5. Test Content Extraction

```bash
curl -X POST http://localhost:8000/extract \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

If you see JSON with `"success": true`, it's working! 🎉

## Configuration Options

### Environment Variables

All configuration is in the `.env` file:

```bash
# Required - Your OpenAI API key
OPENAI_API_KEY=sk-your-key-here

# Optional - AI model to use (default: gpt-4o-mini)
OPENAI_MODEL=gpt-4o-mini

# Optional - Page load timeout in seconds (default: 30)
SELENIUM_TIMEOUT=30

# Optional - Max popup dismissal attempts (default: 3)
MAX_POPUP_RETRIES=3

# Optional - Run browser in background (default: true)
CHROME_HEADLESS=true

# Optional - Logging level (default: INFO)
LOG_LEVEL=INFO
```

### Change Port

Edit `docker-compose.yml`:
```yaml
ports:
  - "8080:8000"  # Change 8080 to your preferred port
```

Then restart:
```bash
docker-compose down
docker-compose up -d
```

## Common Installation Issues

### Issue: "Cannot connect to Docker daemon"

**Solution:**
```bash
# Start Docker service
sudo systemctl start docker

# Or on macOS, start Docker Desktop application
```

### Issue: "Port 8000 already in use"

**Solution:**
```bash
# Find what's using the port
lsof -i :8000

# Kill the process or change the port in docker-compose.yml
```

### Issue: "Permission denied" on Linux

**Solution:**
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Log out and back in, or run:
newgrp docker
```

### Issue: "OpenAI API key not found"

**Solution:**
```bash
# Verify .env file exists
ls -la .env

# Check the key is set
cat .env | grep OPENAI_API_KEY

# Make sure there are no spaces around the =
# Correct:   OPENAI_API_KEY=sk-abc123
# Incorrect: OPENAI_API_KEY = sk-abc123
```

### Issue: Build fails with "No space left on device"

**Solution:**
```bash
# Clean up Docker
docker system prune -a

# Remove unused images
docker image prune -a
```

## Management Commands

### View Logs
```bash
# Follow logs in real-time
docker-compose logs -f

# View last 100 lines
docker-compose logs --tail=100

# View logs for specific time
docker-compose logs --since 10m
```

### Stop Service
```bash
# Stop but keep containers
docker-compose stop

# Stop and remove containers
docker-compose down
```

### Restart Service
```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart browser-api
```

### Update Code
```bash
# After making changes to code
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Check Resource Usage
```bash
# See CPU and memory usage
docker stats

# See disk usage
docker system df
```

## Deployment Options

### Development (Local Machine)
```bash
# Run with logs visible
docker-compose up

# Stop with Ctrl+C
```

### Production (Server)
```bash
# Run in background
docker-compose up -d

# Enable auto-restart
# Already configured in docker-compose.yml:
# restart: unless-stopped
```

### Multiple Instances
```bash
# Run on different ports
# Copy docker-compose.yml to docker-compose-2.yml
# Change port: "8001:8000"
docker-compose -f docker-compose-2.yml up -d
```

## Security Considerations

### API Key Security
- ✅ Never commit `.env` to Git (already in `.gitignore`)
- ✅ Use environment variables, not hardcoded keys
- ✅ Rotate keys periodically
- ✅ Restrict API key permissions if possible

### Network Security
```bash
# Run on localhost only (default)
ports:
  - "127.0.0.1:8000:8000"

# Or expose to network
ports:
  - "0.0.0.0:8000:8000"
```

### Add Authentication (Optional)
Consider adding API key authentication:
```python
# In app/main.py
from fastapi import Header, HTTPException

@app.post("/extract")
async def extract_content(
    request: ExtractRequest,
    x_api_key: str = Header(...)
):
    if x_api_key != "your-secret-key":
        raise HTTPException(401, "Invalid API key")
    # ... rest of code
```

## Monitoring

### Health Checks
```bash
# Manual check
curl http://localhost:8000/health

# Automated monitoring (cron job)
*/5 * * * * curl -f http://localhost:8000/health || echo "Service down"
```

### Log Monitoring
```bash
# Watch for errors
docker-compose logs -f | grep ERROR

# Count requests
docker-compose logs | grep "POST /extract" | wc -l
```

### Resource Monitoring
```bash
# Install monitoring tools
docker run -d \
  --name=cadvisor \
  -p 8080:8080 \
  -v /:/rootfs:ro \
  -v /var/run:/var/run:ro \
  -v /sys:/sys:ro \
  -v /var/lib/docker/:/var/lib/docker:ro \
  google/cadvisor:latest
```

## Backup and Restore

### Backup Configuration
```bash
# Backup .env file
cp .env .env.backup

# Or backup entire directory
tar -czf browserapi-backup.tar.gz .
```

### Restore
```bash
# Restore .env
cp .env.backup .env

# Or restore entire directory
tar -xzf browserapi-backup.tar.gz
```

## Uninstallation

### Remove Service
```bash
# Stop and remove containers
docker-compose down

# Remove images
docker rmi browserapi-browser-api

# Remove volumes (if any)
docker volume prune
```

### Complete Cleanup
```bash
# Remove everything
docker-compose down -v --rmi all

# Remove project directory
cd ..
rm -rf browserAPI
```

## Troubleshooting

### Service Won't Start
```bash
# Check Docker is running
docker ps

# Check logs for errors
docker-compose logs

# Rebuild from scratch
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### Slow Performance
```bash
# Increase Docker resources
# Docker Desktop → Settings → Resources
# Increase CPU and Memory

# Or reduce concurrent requests
# Add rate limiting in code
```

### API Errors
```bash
# Check OpenAI API status
curl https://status.openai.com/

# Verify API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Check usage and limits
# Visit: https://platform.openai.com/usage
```

## Getting Help

### Check Documentation
- `README.md` - Overview and quick start
- `TESTING_GUIDE.md` - Testing and debugging
- `DYNAMIC_CONTENT_FIX.md` - Technical details
- `ARCHITECTURE.md` - System architecture

### Debug Mode
```bash
# Enable debug logging
# Edit .env:
LOG_LEVEL=DEBUG

# Restart
docker-compose restart

# View detailed logs
docker-compose logs -f
```

### Report Issues
When reporting issues, include:
1. Docker version: `docker --version`
2. OS and version
3. Error logs: `docker-compose logs`
4. URL being tested
5. Expected vs actual behavior

## Next Steps

After installation:
1. ✅ Read `README.md` for usage examples
2. ✅ Try `TESTING_GUIDE.md` test cases
3. ✅ Configure settings in `.env` as needed
4. ✅ Set up monitoring for production use
5. ✅ Consider adding authentication for security

## Success Checklist

- [ ] Docker and Docker Compose installed
- [ ] OpenAI API key obtained and set in `.env`
- [ ] Service built: `docker-compose build`
- [ ] Service started: `docker-compose up -d`
- [ ] Health check passes: `curl http://localhost:8000/health`
- [ ] Test extraction works: `curl -X POST http://localhost:8000/extract ...`
- [ ] Logs are accessible: `docker-compose logs`
- [ ] Configuration understood: `.env` file reviewed

If all checked, you're ready to use the BrowSir API! 🚀