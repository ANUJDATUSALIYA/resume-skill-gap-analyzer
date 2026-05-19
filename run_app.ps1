$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$BundledPython = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

Set-Location $ProjectRoot

if (Test-Path $VenvPython) {
    & $VenvPython -m streamlit run app.py --global.developmentMode false --server.headless true --browser.gatherUsageStats false
} elseif (Test-Path $BundledPython) {
    & $BundledPython -m streamlit run app.py --global.developmentMode false --server.headless true --browser.gatherUsageStats false
} else {
    python -m streamlit run app.py --global.developmentMode false --server.headless true --browser.gatherUsageStats false
}
