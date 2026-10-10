# Collect evidence for an internal Video-to-Audio Windows licensing/build audit.
# Writes only to the repository's ignored dist/audit directory.
# Does not modify dependencies, source videos, converted audio or WhisperX.
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$bundle = Join-Path $root 'dist\Video-to-Audio'
$setup = Join-Path $root 'dist\installer\Video-to-Audio-Setup-0.3.1.exe'
$python = Join-Path $root '.venv-build\Scripts\python.exe'
$destination = Join-Path $root 'dist\audit'

foreach ($file in @($bundle, $setup, $python)) {
    if (-not (Test-Path -LiteralPath $file)) {
        throw "Missing local build prerequisite: $file"
    }
}

New-Item -ItemType Directory -Path $destination -Force | Out-Null
$bundlePath = (Resolve-Path -LiteralPath $bundle).Path.TrimEnd('\')
$files = @(Get-ChildItem -LiteralPath $bundlePath -Recurse -File)
$records = foreach ($file in $files) {
    $relativePath = $file.FullName.Substring($bundlePath.Length).TrimStart('\')
    [pscustomobject]@{
        RelativePath = $relativePath
        SizeBytes = $file.Length
        SHA256 = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    }
}
$records | Sort-Object RelativePath | Export-Csv -Path (Join-Path $destination 'bundled-files.csv') -NoTypeInformation -Encoding UTF8

$ffmpegs = @($files | Where-Object { $_.Name -like 'ffmpeg*.exe' })
if ($ffmpegs.Count -eq 0) {
    throw 'No bundled FFmpeg executable found. Abort distribution audit.'
}
$ffmpegSummary = @()
for ($i = 0; $i -lt $ffmpegs.Count; $i++) {
    $file = $ffmpegs[$i]
    $versionPath = Join-Path $destination ("ffmpeg-{0}-version.txt" -f $i)
    $configPath = Join-Path $destination ("ffmpeg-{0}-buildconf.txt" -f $i)
    $licensePath = Join-Path $destination ("ffmpeg-{0}-license.txt" -f $i)
    & $file.FullName -version 2>&1 | Out-File -LiteralPath $versionPath -Encoding UTF8
    if ($LASTEXITCODE -ne 0) { throw "Bundled FFmpeg -version failed: $($file.Name)" }
    & $file.FullName -buildconf 2>&1 | Out-File -LiteralPath $configPath -Encoding UTF8
    if ($LASTEXITCODE -ne 0) { throw "Bundled FFmpeg -buildconf failed: $($file.Name)" }
    & $file.FullName -L 2>&1 | Out-File -LiteralPath $licensePath -Encoding UTF8
    if ($LASTEXITCODE -ne 0) { throw "Bundled FFmpeg -L failed: $($file.Name)" }
    $relativePath = $file.FullName.Substring($bundlePath.Length).TrimStart('\')
    $ffmpegSummary += [pscustomobject]@{
        RelativePath = $relativePath
        SizeBytes = $file.Length
        SHA256 = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    }
}
$ffmpegSummary | ConvertTo-Json -Depth 4 | Out-File -LiteralPath (Join-Path $destination 'ffmpeg-inventory.json') -Encoding UTF8

& $python -m pip freeze 2>&1 | Out-File -LiteralPath (Join-Path $destination 'python-dependencies.txt') -Encoding UTF8
if ($LASTEXITCODE -ne 0) { throw 'Could not obtain exact build Python dependencies.' }

# A local test run is independent of GitHub Actions.
$env:QT_QPA_PLATFORM = 'offscreen'
# Use separate native stdout/stderr logs. Qt font warnings may be emitted to
# stderr even when tests pass; do not treat those warnings as PowerShell errors.
$testStdout = Join-Path $destination 'test-stdout.txt'
$testStderr = Join-Path $destination 'test-stderr.txt'
$testProcess = Start-Process -FilePath $python -ArgumentList @(
    '-m', 'unittest', 'discover', '-s', 'tests', '-v'
) -WorkingDirectory $root -NoNewWindow -Wait -PassThru -RedirectStandardOutput $testStdout -RedirectStandardError $testStderr
if ($testProcess.ExitCode -ne 0) { throw 'Local tests failed. Check test-stderr.txt and test-stdout.txt.' }

$revision = (& git -C $root rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0) { throw 'Could not identify the audited Git revision.' }
$setupHash = (Get-FileHash -LiteralPath $setup -Algorithm SHA256).Hash.ToLowerInvariant()

[pscustomobject]@{
    GitCommit = $revision
    InstallerName = (Split-Path $setup -Leaf)
    InstallerSHA256 = $setupHash
    BundleFileCount = $files.Count
    FFmpegExecutables = $ffmpegs.Count
    AuditCreatedUTC = (Get-Date).ToUniversalTime().ToString('o')
    Important = 'Evidence only; NOT a license-compliance certification.'
} | ConvertTo-Json -Depth 4 | Out-File -LiteralPath (Join-Path $destination 'audit-summary.json') -Encoding UTF8

Write-Host ''
Write-Host 'Local audit evidence created:' -ForegroundColor Green
Write-Host $destination
Write-Host "Installer SHA256: $setupHash"
Write-Host 'Review license texts, FFmpeg configure flags, source obligations and private paths before any public distribution.'
