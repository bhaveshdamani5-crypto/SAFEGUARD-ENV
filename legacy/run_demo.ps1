Write-Host "Starting SafeGuard-Env (DevSecOps Framework)..."
# Start the server in the background
$serverProcess = Start-Process -FilePath "python" -ArgumentList "-m uvicorn main:app --host 0.0.0.0 --port 7860" -PassThru -NoNewWindow -RedirectStandardOutput "uvicorn_out.txt" -RedirectStandardError "uvicorn_err.txt"

Write-Host "Waiting for server to boot..."
Start-Sleep -Seconds 6

Write-Host "Running Zero-Friction Demo Evaluation..."
python inference.py

Write-Host "Cleaning up..."
Stop-Process -Id $serverProcess.Id -Force
Write-Host "Done! The run was successful."
