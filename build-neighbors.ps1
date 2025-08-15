# PowerShell script to build chunk neighbors (equivalent to make build-neighbors)
param(
    [string]$ProjectId = $env:PROJECT_ID,
    [string]$Dataset = $env:DATASET
)

if (-not $ProjectId -or -not $Dataset) {
    Write-Host "Error: PROJECT_ID and DATASET must be set"
    exit 1
}

Write-Host "Building chunk neighbor relationships for $ProjectId.$Dataset..."

# Read and substitute variables in chunk neighbors DDL
$ddlContent = Get-Content "sql\chunk_neighbors_ddl.sql" -Raw
$ddlContent = $ddlContent -replace '\$\{PROJECT_ID\}', $ProjectId
$ddlContent = $ddlContent -replace '\$\{DATASET\}', $Dataset

# Read and substitute variables in build neighbors SQL
$buildContent = Get-Content "sql\build_chunk_neighbors.sql" -Raw
$buildContent = $buildContent -replace '\$\{PROJECT_ID\}', $ProjectId
$buildContent = $buildContent -replace '\$\{DATASET\}', $Dataset

# Execute each SQL step
Write-Host "1. Creating chunk neighbors table..."
$ddlContent | bq query --use_legacy_sql=false
if ($LASTEXITCODE -ne 0) { 
    Write-Host "Error creating chunk neighbors table"
    exit 1 
}

Write-Host "2. Building neighbor relationships..."
$buildContent | bq query --use_legacy_sql=false
if ($LASTEXITCODE -eq 0) { 
    Write-Host "[graph] chunk_neighbors built"
} else { 
    Write-Host "Error building chunk neighbors"
    exit 1 
}
