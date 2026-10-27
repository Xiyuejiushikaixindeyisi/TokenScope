param([string]$projectRoot)
$ErrorActionPreference = 'Stop'
if (-not $projectRoot) { $projectRoot = Split-Path -Parent $PSScriptRoot }
$renderDir = Join-Path $projectRoot '.build\render'
New-Item -ItemType Directory -Force -Path $renderDir | Out-Null
$stagingDir = Join-Path $env:TEMP 'tokenscope-design-v01-render'
New-Item -ItemType Directory -Force -Path $stagingDir | Out-Null
$sourceFile = Get-ChildItem -LiteralPath $projectRoot -Filter '*.docx' | Select-Object -First 1
$stagingDoc = Join-Path $stagingDir 'TokenScope_design_v01.docx'
$stagingPdf = Join-Path $stagingDir 'TokenScope_design_v01.pdf'
Copy-Item -LiteralPath $sourceFile.FullName -Destination $stagingDoc -Force
$wps = $null
$document = $null
$initialCount = -1
$oldAlerts = $null
try {
    $wps = New-Object -ComObject KWPS.Application
    $initialCount = $wps.Documents.Count
    $oldAlerts = $wps.DisplayAlerts
    $wps.DisplayAlerts = 0
    if ($initialCount -eq 0) { $wps.Visible = $false }
    $document = $wps.Documents.Open($stagingDoc, $false, $true)
    $document.Repaginate()
    $pageCount = $document.ComputeStatistics(2)
    $document.ExportAsFixedFormat($stagingPdf, 17)
    $document.Close(0)
    $document = $null
    Copy-Item -LiteralPath $stagingPdf -Destination (Join-Path $renderDir 'TokenScope_design_v01.pdf') -Force
    Write-Output "Rendered page count: $pageCount"
} finally {
    if ($null -ne $document) { $document.Close(0) }
    if ($null -ne $wps) {
        if ($null -ne $oldAlerts) { $wps.DisplayAlerts = $oldAlerts }
        if ($initialCount -eq 0) { $wps.Quit() }
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($wps) | Out-Null
    }
}
