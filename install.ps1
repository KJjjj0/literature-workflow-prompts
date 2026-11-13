param(
  [ValidateSet("all", "codex", "claude", "opencode", "generic")]
  [string]$Target = "all",
  [ValidateSet("plugin", "project")]
  [string]$Mode = "plugin",
  [string]$ProjectDir = (Get-Location).Path,
  [ValidateSet("user", "project", "local")]
  [string]$Scope = "user",
  [switch]$Force,
  [switch]$DryRun
)

$python = Get-Command python -ErrorAction Stop
$arguments = @(
  (Join-Path $PSScriptRoot "tools\install.py"),
  "--target", $Target,
  "--mode", $Mode,
  "--project-dir", $ProjectDir,
  "--scope", $Scope
)
if ($Force) { $arguments += "--force" }
if ($DryRun) { $arguments += "--dry-run" }

& $python.Source @arguments
exit $LASTEXITCODE
