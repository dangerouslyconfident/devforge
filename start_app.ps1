Write-Host "Starting Intelligent Speech Dictation Engine..." -ForegroundColor Cyan

# 1. Install Python Dependencies
Write-Host "Installing Python dependencies..."
pip install -r requirements.txt

# 2. Install Node Dependencies
Write-Host "Installing Frontend dependencies..."
Push-Location frontend
npm install
Pop-Location

# 3. Start Backend (New Window)
Write-Host "Starting Backend Server..."
Start-Process -FilePath "python" -ArgumentList "-m uvicorn server:app --reload --host 0.0.0.0 --port 8000"

# 4. Start Frontend (New Window)
Write-Host "Starting Frontend..."
Push-Location frontend
Start-Process -FilePath "npm" -ArgumentList "run dev"
Pop-Location

Write-Host "App is launching in separate windows." -ForegroundColor Green
Write-Host "Backend: http://localhost:8000/docs"
Write-Host "Frontend: http://localhost:5173"
