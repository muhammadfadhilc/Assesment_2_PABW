[CmdletBinding()]
param([switch]$SkipSeed, [switch]$SkipNpm)

$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot

function Run-Checked {
    param([string]$Command, [string[]]$Arguments)
    & $Command @Arguments
    if ($LASTEXITCODE -ne 0) { throw "$Command gagal (exit $LASTEXITCODE). Setup dihentikan." }
}

foreach ($tool in @('php', 'composer')) {
    if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) { throw "$tool belum ada di PATH. Gunakan terminal Laragon atau perbaiki PATH." }
}
if (-not (Test-Path -LiteralPath '.env')) { Copy-Item -LiteralPath '.env.example' -Destination '.env' }
Write-Host 'Memakai konfigurasi MySQL di .env. Ubah .env lebih dahulu bila password/port MySQL berbeda.'
Run-Checked 'composer' @('install', '--no-interaction', '--prefer-dist')
Run-Checked 'php' @('artisan', 'config:clear')
$envText = Get-Content -LiteralPath '.env' -Raw
if ($envText -notmatch '(?m)^APP_KEY=.+') { Run-Checked 'php' @('artisan', 'key:generate') }
Run-Checked 'php' @('scripts/create-database.php')
Run-Checked 'php' @('artisan', 'migrate', '--force')
if (-not $SkipSeed) { Run-Checked 'php' @('artisan', 'db:seed', '--force') }
Run-Checked 'php' @('artisan', 'storage:link')
Run-Checked 'php' @('artisan', 'wayfinder:generate', '--with-form')
if (-not $SkipNpm) {
    Run-Checked 'npm.cmd' @('ci', '--no-audit', '--no-fund')
    Run-Checked 'npm.cmd' @('run', 'types')
    Run-Checked 'npm.cmd' @('run', 'build')
}
Run-Checked 'php' @('artisan', 'module:list')
Run-Checked 'php' @('artisan', 'route:list', '--except-vendor')
Write-Host 'Setup selesai. Jalankan: php artisan serve'
Write-Host 'Buka http://127.0.0.1:8000. Akun: admin@recyclehub.test, nasabah1@recyclehub.test, nasabah2@recyclehub.test. Password uji: Recycle123!'
