$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$VendorPath = Join-Path $ProjectRoot ".vendor"
$BundledPython = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

Set-Location $ProjectRoot

if (Test-Path $VendorPath) {
    $env:PYTHONPATH = "$VendorPath;$env:PYTHONPATH"
}

if (Test-Path $BundledPython) {
    & $BundledPython -m streamlit run app.py --global.developmentMode false --server.headless true --browser.gatherUsageStats false
} else {
    python -m streamlit run app.py --global.developmentMode false --server.headless true --browser.gatherUsageStats false
}
