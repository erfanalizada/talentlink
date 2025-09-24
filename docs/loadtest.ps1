# Simple Load Test Script
# Save as: loadtest.ps1

param(
    [string]$Url = "https://talentlink-erfan.nl/",
    [int]$Requests = 100
)

Write-Host "Starting load test..." -ForegroundColor Green
Write-Host "URL: $Url" -ForegroundColor Yellow
Write-Host "Requests: $Requests" -ForegroundColor Yellow
Write-Host "=" * 40

$start = Get-Date
$success = 0
$fail = 0
$responseTimes = @()

for ($i = 1; $i -le $Requests; $i++) {
    $requestStart = Get-Date
    
    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 10
        $requestEnd = Get-Date
        $responseTime = ($requestEnd - $requestStart).TotalMilliseconds
        
        if ($response.StatusCode -eq 200) {
            $success++
            $responseTimes += $responseTime
        } else {
            $fail++
        }
    }
    catch {
        $fail++
        Write-Host "x" -NoNewline -ForegroundColor Red
    }
    
    # Show progress every 10 requests
    if ($i % 10 -eq 0) {
        Write-Host "." -NoNewline -ForegroundColor Green
    }
}

$end = Get-Date
$totalDuration = ($end - $start).TotalSeconds

# Calculate stats
$avgResponseTime = if ($responseTimes.Count -gt 0) { 
    ($responseTimes | Measure-Object -Average).Average 
} else { 0 }

$minResponseTime = if ($responseTimes.Count -gt 0) { 
    ($responseTimes | Measure-Object -Minimum).Minimum 
} else { 0 }

$maxResponseTime = if ($responseTimes.Count -gt 0) { 
    ($responseTimes | Measure-Object -Maximum).Maximum 
} else { 0 }

$rps = if ($totalDuration -gt 0) { $success / $totalDuration } else { 0 }

# Display results
Write-Host "`n"
Write-Host "=" * 40 -ForegroundColor Green
Write-Host "RESULTS" -ForegroundColor Green
Write-Host "=" * 40 -ForegroundColor Green
Write-Host "Successful requests: $success" -ForegroundColor Green
Write-Host "Failed requests: $fail" -ForegroundColor Red
Write-Host "Total time: $([math]::Round($totalDuration, 2)) seconds" -ForegroundColor White
Write-Host "Requests per second: $([math]::Round($rps, 2)) RPS" -ForegroundColor Cyan
Write-Host "Average response time: $([math]::Round($avgResponseTime, 2)) ms" -ForegroundColor White
Write-Host "Min response time: $([math]::Round($minResponseTime, 2)) ms" -ForegroundColor White
Write-Host "Max response time: $([math]::Round($maxResponseTime, 2)) ms" -ForegroundColor White
Write-Host "Success rate: $([math]::Round(($success / $Requests) * 100, 2))%" -ForegroundColor White

Write-Host "`nTest completed!" -ForegroundColor Green