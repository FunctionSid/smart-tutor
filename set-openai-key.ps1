param(
    [string]$Model = "gpt-4.1"
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$CatalogPath = Join-Path $Root "data\user\settings\model_catalog.json"

if (-not (Test-Path $CatalogPath)) {
    throw "Missing settings file: $CatalogPath"
}

function Set-JsonProperty {
    param(
        [Parameter(Mandatory = $true)] $Object,
        [Parameter(Mandatory = $true)] [string] $Name,
        [Parameter(Mandatory = $true)] $Value
    )

    if ($Object.PSObject.Properties[$Name]) {
        $Object.$Name = $Value
    }
    else {
        $Object | Add-Member -NotePropertyName $Name -NotePropertyValue $Value
    }
}

Write-Host "This stores your OpenAI key in Smart Tutor's local runtime settings."
Write-Host "The key will not be printed back to the terminal."

$SecureKey = Read-Host "Paste OpenAI API key" -AsSecureString
$Bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($SecureKey)

try {
    $ApiKey = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($Bstr)
}
finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($Bstr)
}

if ([string]::IsNullOrWhiteSpace($ApiKey)) {
    throw "No API key entered."
}

$Catalog = Get-Content -Raw -Path $CatalogPath | ConvertFrom-Json

$LlmProfile = [pscustomobject]@{
    id            = "llm-profile-default"
    name          = "Default LLM Endpoint"
    binding       = "openai"
    base_url      = "https://api.openai.com/v1"
    api_key       = $ApiKey
    api_version   = ""
    extra_headers = [pscustomobject]@{}
    models        = @(
        [pscustomobject]@{
            id    = "llm-model-default"
            name  = $Model
            model = $Model
        }
    )
}

$LlmSettings = [pscustomobject]@{
    active_profile_id = "llm-profile-default"
    active_model_id   = "llm-model-default"
    profiles          = @($LlmProfile)
}

Set-JsonProperty -Object $Catalog.services -Name "llm" -Value $LlmSettings

$Catalog | ConvertTo-Json -Depth 50 | Set-Content -Path $CatalogPath -Encoding UTF8

Write-Host "OpenAI settings saved to data\user\settings\model_catalog.json."
