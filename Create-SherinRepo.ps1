# Create-SherinRepo.ps1

param(
    [string]$RepoName = "sherin-ai-financial-intelligence",
    [string]$Description = "AI Financial Intelligence Platform - Live News Map + Knowledge Graph + Probabilistic Trading",
    [switch]$Private = $false
)

# ────────────────────────────────────────────────
# CONFIG – CHANGE THESE
# ────────────────────────────────────────────────
$GitHubUsername   = "rafeez1819"
$Pat              = "ghp_11BLQ3YHA0ezCWXQACUnjy_AMr3P4Q7KBquIAX1tuBavYowsMu40htS9NFkQGmv9co2YIGTZSVxVrItWCg"          # ← YOUR PAT HERE
$LocalParentDir   = "C:\Projects\Sherin"                               # Where to create the folder
# ────────────────────────────────────────────────

$headers = @{
    Authorization = "token $Pat"
    Accept        = "application/vnd.github.v3+json"
}

$body = @{
    name        = $RepoName
    description = $Description
    private     = $Private
    auto_init   = $true          # creates initial commit with README
} | ConvertTo-Json

Write-Host "Creating repository https://github.com/$GitHubUsername/$RepoName ..." -ForegroundColor Cyan

try {
    $response = Invoke-RestMethod -Uri "https://api.github.com/user/repos" `
                                  -Method Post `
                                  -Headers $headers `
                                  -Body $body `
                                  -ContentType "application/json"
    Write-Host "Repository created successfully!" -ForegroundColor Green
} catch {
    Write-Host "Error creating repo: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $err = $reader.ReadToEnd()
        Write-Host $err -ForegroundColor DarkRed
    }
    exit
}

# ────────────────────────────────────────────────
# Create local folder structure
# ────────────────────────────────────────────────
$RepoPath = Join-Path $LocalParentDir $RepoName
New-Item -Path $RepoPath -ItemType Directory -Force | Out-Null
Set-Location $RepoPath

# Minimal realistic structure (you can expand later)
$structure = @(
    "README.md",
    "ROADMAP.md",
    ".gitignore",
    "LICENSE",
    "docs/architecture.md",
    "infrastructure/docker-compose.yml",
    "src/phase1/news-ingestion/reuters_ingestor.py",
    "src/phase2/kg-consumer.py"
)

foreach ($file in $structure) {
    $dir = Split-Path $file -Parent
    if ($dir) { New-Item -Path $dir -ItemType Directory -Force | Out-Null }
    if (-not (Test-Path $file)) {
        Set-Content -Path $file -Value "# Placeholder for $file`nCreated $(Get-Date -Format 'yyyy-MM-dd')" -Encoding UTF8
    }
}

# Quick useful .gitignore for AI/fintech project
Set-Content -Path ".gitignore" -Value @"
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/

# Data & large files
data/
models/*.pth
models/*.h5
*.csv
*.parquet

# IDE
.vscode/
.idea/

# Misc
.DS_Store
Thumbs.db
"@

# Simple README starter
Set-Content -Path "README.md" -Value @"
# Sherin AI Financial Intelligence

Live News Map + Knowledge Graph + Probabilistic Trading Signals

## Status
Phase 1 – Data Foundation: In progress

## Structure
See ROADMAP.md for phased plan
"@

# ────────────────────────────────────────────────
# Initialize git & push
# ────────────────────────────────────────────────
git init
git add .
git commit -m "Initial commit – folder structure & Phase 1 skeleton"

$remoteUrl = "https://$GitHubUsername`:$Pat@github.com/$GitHubUsername/$RepoName.git"

git remote add origin $remoteUrl
git branch -M main
git push -u origin main --force   # --force only needed if auto_init created conflicting README

Write-Host "`nDone! Repository should now be live at:" -ForegroundColor Green
Write-Host "https://github.com/$GitHubUsername/$RepoName" -ForegroundColor Yellow