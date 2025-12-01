#!/bin/bash

API_URL="http://localhost:8000"

echo "Testing AI Emergency Dispatch Assistant API"
echo "==========================================="

# Test health endpoint
echo -e "\n1. Testing Health Endpoint..."
curl -s "$API_URL/api/health" | python3 -m json.tool

# Test root endpoint
echo -e "\n2. Testing Root Endpoint..."
curl -s "$API_URL/" | python3 -m json.tool

echo -e "\nAPI tests complete!"
echo "For full testing, upload an audio file using:"
echo "curl -X POST \"$API_URL/api/analyze-audio\" -F \"audio_file=@your_audio.wav\""
