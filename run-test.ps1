# Test script for project_export_visible_tables
$json = Get-Content test-export-visible-tables.json -Raw
$output = $json | node build/index.js 2>$null
Write-Host "=== OUTPUT ===" -ForegroundColor Green
$output | ConvertFrom-Json | ConvertTo-Json -Depth 10
Write-Host "`n=== DONE ===" -ForegroundColor Green
