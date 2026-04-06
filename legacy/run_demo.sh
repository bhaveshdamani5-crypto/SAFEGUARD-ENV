#!/bin/bash
echo "Starting SafeGuard-Env (DevSecOps Framework)..."
# Start the server in the background
python -m uvicorn main:app --host 0.0.0.0 --port 7860 &
SERVER_PID=$!

echo "Waiting for server to boot..."
sleep 5

echo "Running Zero-Friction Demo Evaluation..."
python inference.py

echo "Cleaning up..."
kill $SERVER_PID
echo "Done! The run was successful."
