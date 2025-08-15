# PowerShell script to run router training (equivalent to make router-train)
param(
    [string]$ProjectId = $env:PROJECT_ID,
    [string]$Dataset = $env:DATASET
)

if (-not $ProjectId -or -not $Dataset) {
    Write-Host "Error: PROJECT_ID and DATASET must be set"
    exit 1
}

Write-Host "Training router model for $ProjectId.$Dataset..."

# Read and substitute variables in router training DDL
$ddlContent = Get-Content "sql\router_training_ddl.sql" -Raw
$ddlContent = $ddlContent -replace '\$\{PROJECT_ID\}', $ProjectId
$ddlContent = $ddlContent -replace '\$\{DATASET\}', $Dataset

# Read and substitute variables in seed training data
$seedContent = Get-Content "sql\router_seed_training.sql" -Raw
$seedContent = $seedContent -replace '\$\{PROJECT_ID\}', $ProjectId
$seedContent = $seedContent -replace '\$\{DATASET\}', $Dataset

# Read and substitute variables in router training SQL
$trainContent = Get-Content "sql\router_train.sql" -Raw
$trainContent = $trainContent -replace '\$\{PROJECT_ID\}', $ProjectId
$trainContent = $trainContent -replace '\$\{DATASET\}', $Dataset

# Execute each SQL step
Write-Host "1. Creating router training table..."
$ddlContent | bq query --use_legacy_sql=false
if ($LASTEXITCODE -ne 0) { 
    Write-Host "Error creating training table"
    exit 1 
}

Write-Host "2. Inserting seed training data..."
$seedContent | bq query --use_legacy_sql=false
# Don't fail on duplicate inserts - that's expected

Write-Host "3. Training BQML model..."
$trainContent | bq query --use_legacy_sql=false
if ($LASTEXITCODE -eq 0) { 
    Write-Host "[router] trained (or updated) $ProjectId.$Dataset.router_m"
} else { 
    Write-Host "Error training router model"
    exit 1 
}
