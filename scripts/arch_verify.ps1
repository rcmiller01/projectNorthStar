#!/usr/bin/env pwsh
# PowerShell script to verify architecture diagrams are in sync with .mmd source
# Alternative to `make arch-verify` for Windows users

param(
    [switch]$Help
)

if ($Help) {
    Write-Host "Usage: scripts/arch_verify.ps1"
    Write-Host ""
    Write-Host "Verifies that docs/architecture.png and docs/architecture.svg are in sync"
    Write-Host "with docs/architecture.mmd source file."
    Write-Host ""
    Write-Host "Requires: npm i -g @mermaid-js/mermaid-cli"
    exit 0
}

$ErrorActionPreference = "Stop"

# Check for mmdc
try {
    mmdc --version | Out-Null
} catch {
    Write-Error "mermaid-cli (mmdc) not found. Install with: npm i -g @mermaid-js/mermaid-cli"
    exit 127
}

$ARCH_SRC = "docs/architecture.mmd"
$ARCH_PNG = "docs/architecture.png"
$ARCH_SVG = "docs/architecture.svg"
$TMP_ARCH_DIR = ".tmp_arch"

# Check source exists
if (-not (Test-Path $ARCH_SRC)) {
    Write-Error "Source file not found: $ARCH_SRC"
    exit 1
}

Write-Host "[arch-verify] Checking diagram sync..."

# Clean and create temp directory
if (Test-Path $TMP_ARCH_DIR) {
    Remove-Item $TMP_ARCH_DIR -Recurse -Force
}
New-Item -ItemType Directory -Name $TMP_ARCH_DIR -Force | Out-Null

try {
    # Generate fresh diagrams in temp directory
    mmdc -i $ARCH_SRC -o "$TMP_ARCH_DIR/architecture.png" -b transparent
    mmdc -i $ARCH_SRC -o "$TMP_ARCH_DIR/architecture.svg"

    # Compare PNG
    if (Test-Path $ARCH_PNG) {
        $currentPng = Get-FileHash $ARCH_PNG -Algorithm SHA256
        $tempPng = Get-FileHash "$TMP_ARCH_DIR/architecture.png" -Algorithm SHA256
        if ($currentPng.Hash -ne $tempPng.Hash) {
            Write-Error "[arch-verify] PNG out of date. Rebuild with 'make arch' or regenerate manually."
            exit 1
        }
    } else {
        Write-Error "[arch-verify] PNG not found: $ARCH_PNG. Run 'make arch' to generate."
        exit 1
    }

    # Compare SVG
    if (Test-Path $ARCH_SVG) {
        $currentSvg = Get-FileHash $ARCH_SVG -Algorithm SHA256
        $tempSvg = Get-FileHash "$TMP_ARCH_DIR/architecture.svg" -Algorithm SHA256
        if ($currentSvg.Hash -ne $tempSvg.Hash) {
            Write-Error "[arch-verify] SVG out of date. Rebuild with 'make arch' or regenerate manually."
            exit 1
        }
    } else {
        Write-Error "[arch-verify] SVG not found: $ARCH_SVG. Run 'make arch' to generate."
        exit 1
    }

    Write-Host "[arch-verify] ✅ diagrams are up to date"

} finally {
    # Cleanup
    if (Test-Path $TMP_ARCH_DIR) {
        Remove-Item $TMP_ARCH_DIR -Recurse -Force
    }
}
