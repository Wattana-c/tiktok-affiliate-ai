#!/bin/bash
echo "Starting TikTok Affiliate AI Auto Content Machine..."
docker-compose up --build -d
echo "Application started!"
echo "Backend API: http://localhost:8000"
echo "Frontend Dashboard: http://localhost:5173"
