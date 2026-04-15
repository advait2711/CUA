param (

    # "change the status of jane smith to active"
    # "disable the account for alice johnson"
    # "reset the password for frank wilson"
    # "add a new user named Tom Clark with email tom.clark@company.com in the IT department"
    # "delete john doe from the system"
    [string]$task = "set the status to acitve for  the account for Hank Pym"
)

# Activate venv
. .\.venv\Scripts\Activate.ps1

# Setup MySQL database and seed dummy data
Write-Host "Setting up MySQL database..."
python setup_db.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Database setup failed. Check MySQL is running and credentials in .env are correct."
    exit 1
}

# Start Flask server in a separate window
Write-Host "Starting Flask app... waiting 3 seconds"
Start-Process -FilePath "powershell" -ArgumentList "-Command `"cd '$PWD'; .\.venv\Scripts\Activate.ps1; python admin_panel/app.py`""

Start-Sleep -Seconds 3

Write-Host "Running Agent task: $task"
python agent.py "$task"
