# Run the RSS feed processor
$pythonPath = ".\.venv\Scripts\python.exe"
$scriptPath = ".\src\main.py"
$projectRoot = $PSScriptRoot
$srcPath = Join-Path $projectRoot "src"

# Set PYTHONPATH to include the src directory
$env:PYTHONPATH = "$srcPath;$env:PYTHONPATH"

if (Test-Path $pythonPath) {
    & $pythonPath $scriptPath $args
} else {
    Write-Error "Python virtual environment not found. Please run 'python -m venv .venv' and 'pip install -r requirements.txt' first."
    exit 1
}
