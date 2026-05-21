# Repository name
$REPO = "ghcr.io/pilamrocky/vr_score_keeper"

# Function to display usage instructions
function Show-Usage {
    Write-Host "Usage: .\build_and_push.ps1 <version_number>" -ForegroundColor Yellow
    Write-Host "Example: .\build_and_push.ps1 1.3" -ForegroundColor Yellow
    Exit 1
}

# Check if a version number was provided
if ($args.Count -lt 1 -or [string]::IsNullOrWhiteSpace($args[0])) {
    Show-Usage
}

$VERSION = $args[0]
$VERSION_TAG = "${REPO}:${VERSION}"
$LATEST_TAG = "${REPO}:latest"

# Build the Docker image with both the version tag and the "latest" tag
Write-Host "Building Docker image with tags: ${VERSION_TAG} and ${LATEST_TAG}" -ForegroundColor Cyan
docker build -t "${VERSION_TAG}" -t "${LATEST_TAG}" .

# Check if the build was successful
if ($LASTEXITCODE -ne 0) {
    Write-Error "Docker build failed. Exiting."
    Exit 1
}

# Push the newly created version tag
Write-Host "Pushing version tag: ${VERSION_TAG}" -ForegroundColor Cyan
docker push "${VERSION_TAG}"

# Check if the push was successful
if ($LASTEXITCODE -ne 0) {
    Write-Error "Docker push of version tag failed. Exiting."
    Exit 1
}

# Push the newly created latest tag
Write-Host "Pushing latest tag: ${LATEST_TAG}" -ForegroundColor Cyan
docker push "${LATEST_TAG}"

# Check if the push was successful
if ($LASTEXITCODE -ne 0) {
    Write-Error "Docker push of latest tag failed. Exiting."
    Exit 1
}

Write-Host "Image successfully built and pushed with tags: ${VERSION} and latest." -ForegroundColor Green
