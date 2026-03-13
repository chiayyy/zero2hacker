#!/bin/bash
echo "Downloading AI models for challenge generation..."
docker exec zero2hacker-ctf-ollama-1 ollama pull llama3
docker exec zero2hacker-ctf-ollama-1 ollama pull mistral
docker exec zero2hacker-ctf-ollama-1 ollama pull codellama
echo "AI models downloaded successfully!"
