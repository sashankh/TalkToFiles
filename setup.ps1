param (
    [switch]$run = $false
)

# Function to check if Python is installed
function Check-Python {
    try {
        $pythonVersion = python --version
        Write-Host "Found $pythonVersion"
        return $true
    } 
    catch {
        Write-Host "Python is not installed or not in PATH"
        return $false
    }
}

# Function to create virtual environment if not exists
function Create-VirtualEnvironment {
    if (-not (Test-Path -Path "env")) {
        Write-Host "Creating virtual environment..."
        python -m venv .venv
    } else {
        Write-Host "Virtual environment already exists"
    }
}

# Function to activate virtual environment
function Activate-VirtualEnvironment {
    Write-Host "Activating virtual environment..."
    & .\.venv\Scripts\Activate.ps1
}

# Function to install requirements
function Install-Requirements {
    Write-Host "Installing requirements..."
    pip install -r requirements.txt
}

# Function to check if .env file exists
function Check-EnvFile {
    if (-not (Test-Path -Path ".env")) {
        Write-Host "Warning: .env file not found. Creating sample .env file..."
        Copy-Item -Path ".env.example" -Destination ".env" -ErrorAction SilentlyContinue
        
        if (-not (Test-Path -Path ".env")) {
            @"
# Azure OpenAI configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_API_VERSION=2023-05-15
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-large
AZURE_OPENAI_COMPLETION_DEPLOYMENT=gpt-4o

# File watching configuration
WATCH_DIRECTORY=$HOME\Documents\TalkToFiles

# API configuration
API_HOST=0.0.0.0
API_PORT=8001
"@ | Out-File -FilePath ".env" -Encoding utf8
        }
        
        Write-Host "Please update the .env file with your Azure OpenAI API keys and configuration"
        Write-Host "Path: $((Get-Item -Path '.').FullName)\.env"
    }
}

# Function to create missing source directories
function Create-MissingDirectories {
    $directories = @(
        "src",
        "src\api",
        "src\database",
        "src\embeddings",
        "src\file_processing",
        "src\models",
        "frontend\static\css",
        "frontend\static\js", 
        "frontend\templates"
    )
    
    foreach ($dir in $directories) {
        if (-not (Test-Path -Path $dir)) {
            Write-Host "Creating directory: $dir"
            New-Item -Path $dir -ItemType Directory -Force | Out-Null
        }
    }
}

# Function to run the application
function Run-Application {
    Write-Host "Starting TalkToFiles application..."
    python -m src.main
}

# Main script execution
Write-Host "=== TalkToFiles Setup ==="

# Check Python installation
if (-not (Check-Python)) {
    Write-Host "Please install Python 3.8+ and add it to your PATH."
    exit 1
}

# Create virtual environment
Create-VirtualEnvironment

# Activate virtual environment
Activate-VirtualEnvironment

# Install requirements
Install-Requirements

# Check .env file
#Check-EnvFile

# Create missing directories
Create-MissingDirectories

# Run the application if -run parameter is provided
if ($run) {
    Run-Application
} else {
    Write-Host "`nSetup completed successfully!"
    Write-Host "To run the application: .\setup.ps1 -run"
}