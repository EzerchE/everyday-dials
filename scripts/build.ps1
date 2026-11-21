$ErrorActionPreference = 'Stop'
$releaseRoot = Split-Path $PSScriptRoot -Parent
Push-Location $releaseRoot
try {
    $env:DOTNET_CLI_HOME = Join-Path $releaseRoot 'tools/dotnet-home'
    $env:DOTNET_CLI_TELEMETRY_OPTOUT = '1'
    $env:DOTNET_SKIP_FIRST_TIME_EXPERIENCE = '1'
    $pluginName = 'com.ezerche.everydaydials.sdPlugin'
    $candidate = Join-Path $releaseRoot "build/$pluginName"
    New-Item -ItemType Directory -Force -Path $candidate, 'artifacts', 'verification' | Out-Null
    foreach ($profile in Get-ChildItem -LiteralPath 'profiles' -Directory -Filter '*.sdProfile') {
        $profileManifest = Get-Content -LiteralPath (Join-Path $profile.FullName 'manifest.json') -Raw | ConvertFrom-Json
        $label = $profileManifest.Name.Replace('Everyday Dials - ','').ToLower().Replace(' ','-')
        $profileTarget = Join-Path $releaseRoot "artifacts/$label.streamDeckProfile"
        $stream = [IO.File]::Open($profileTarget,[IO.FileMode]::Create,[IO.FileAccess]::ReadWrite)
        $archive = [IO.Compression.ZipArchive]::new($stream,[IO.Compression.ZipArchiveMode]::Create,$false)
        try {
            [IO.Compression.ZipFileExtensions]::CreateEntryFromFile($archive,(Join-Path $releaseRoot 'profiles/package.json'),'package.json',[IO.Compression.CompressionLevel]::Optimal) | Out-Null
            foreach ($file in Get-ChildItem -LiteralPath $profile.FullName -Recurse -File) {
                $relative = [IO.Path]::GetRelativePath($profile.FullName,$file.FullName).Replace('\','/')
                [IO.Compression.ZipFileExtensions]::CreateEntryFromFile($archive,$file.FullName,"Profiles/$($profile.Name)/$relative",[IO.Compression.CompressionLevel]::Optimal) | Out-Null
            }
        } finally { $archive.Dispose();$stream.Dispose() }
    }
    Copy-Item -Path "plugin/$pluginName/*" -Destination $candidate -Recurse -Force
    # V6 uses stable SVG editor symbols. Prune the eight known V4 directional
    # derivatives so an incremental build cannot repackage obsolete artwork.
    foreach ($stem in @('volume','seek','speed','frame')) {
        foreach ($direction in @('left','right')) {
            $retired = Join-Path $candidate "images/youtube-encoders/dial-$stem-$direction.png"
            if (Test-Path -LiteralPath $retired) { Remove-Item -LiteralPath $retired -Force }
        }
    }
    dotnet build src/EverydayDials.csproj -c Release --no-restore -v minimal 2>&1 | ForEach-Object { "$($_)".Replace($releaseRoot,'.') } | Tee-Object -FilePath verification/build.txt
    if ($LASTEXITCODE -ne 0) { throw 'Build failed. Run dotnet restore first.' }
    $binaryRoot = 'src/bin/Release/net8.0-windows10.0.19041.0'
    $binaryTarget = Join-Path $candidate 'bin'
    New-Item -ItemType Directory -Force -Path $binaryTarget | Out-Null
    foreach ($name in @('EverydayDials.exe','EverydayDials.dll','EverydayDials.deps.json','EverydayDials.runtimeconfig.json','Microsoft.Windows.SDK.NET.dll','Microsoft.Windows.UI.Xaml.dll','WinRT.Runtime.dll')) {
        Copy-Item -LiteralPath (Join-Path $binaryRoot $name) -Destination (Join-Path $binaryTarget $name) -Force
    }
    dotnet (Join-Path $binaryTarget 'EverydayDials.dll') --self-test | Set-Content verification/self-test.txt
    if ($LASTEXITCODE -ne 0) { throw 'Self-test failed.' }
    $cli = Join-Path $releaseRoot 'tools/node_modules/.bin/streamdeck.cmd'
    if (!(Test-Path -LiteralPath $cli)) { throw 'Run npm.cmd ci --prefix tools to install the pinned local CLI.' }
    & $cli validate $candidate --no-update-check 2>&1 | ForEach-Object { "$($_)".Replace($releaseRoot,'.') } | Tee-Object -FilePath verification/cli-validate.txt
    if ($LASTEXITCODE -ne 0) { throw 'Official CLI validation failed.' }
    & $cli pack $candidate --no-update-check --force --no-file-list -o artifacts 2>&1 | ForEach-Object { "$($_)".Replace($releaseRoot,'.') } | Tee-Object -FilePath verification/cli-pack.txt
    if ($LASTEXITCODE -ne 0) { throw 'Official CLI packaging failed.' }
    Write-Output 'Built, self-tested, validated and packaged. No live plugin was installed.'
} finally { Pop-Location }
