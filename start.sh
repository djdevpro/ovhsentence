#!/bin/bash

# Lancer la première application
uvicorn app:app --host 0.0.0.0 --port 8080 &

# Lancer la deuxième application
echo "START LLM"
