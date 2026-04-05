from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from models import Observation, Action, StepResult, StateResponse, GraderResult
from env import SafeGuardEnv
import uuid
from typing import Optional, Dict

app = FastAPI(
    title="SafeGuard-Env (DevSecOps Edition)", 
    description="Zero-Knowledge Data Compliance Environment for evaluating API Key & PII redaction capabilities.", 
    version="2.0.0",
    docs_url=None,
    redoc_url=None
)

SWAGGER_DARK_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html { background: #0a0a0f !important; }
body { background: #0a0a0f !important; color: #e0e0e8 !important; font-family: 'Inter', sans-serif !important; }
.swagger-ui { background: #0a0a0f !important; font-family: 'Inter', sans-serif !important; }
.swagger-ui .topbar { background: linear-gradient(135deg, #12121a 0%, #1a1a2e 100%) !important; border-bottom: 1px solid rgba(99,102,241,0.15) !important; padding: 12px 0 !important; }
.swagger-ui .topbar .download-url-wrapper input { background: #1e1e2e !important; color: #e0e0e8 !important; border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 8px !important; }
.swagger-ui .topbar a span { color: #fff !important; font-weight: 600 !important; }
.swagger-ui .info { margin: 40px 0 !important; }
.swagger-ui .info .title { color: #f0f0f5 !important; font-weight: 700 !important; font-size: 2rem !important; }
.swagger-ui .info .description p { color: #8b8b9e !important; }
.swagger-ui .info .base-url { color: #6366f1 !important; }
.swagger-ui .scheme-container { background: #12121a !important; border: 1px solid rgba(255,255,255,0.06) !important; border-radius: 12px !important; box-shadow: none !important; padding: 16px !important; }
.swagger-ui .opblock-tag { color: #f0f0f5 !important; border-bottom: 1px solid rgba(255,255,255,0.06) !important; font-weight: 600 !important; }
.swagger-ui .opblock { background: #12121a !important; border: 1px solid rgba(255,255,255,0.06) !important; border-radius: 12px !important; margin-bottom: 12px !important; box-shadow: 0 2px 12px rgba(0,0,0,0.2) !important; }
.swagger-ui .opblock .opblock-summary { border-radius: 12px !important; padding: 12px 16px !important; }
.swagger-ui .opblock.opblock-post { border-color: rgba(99,102,241,0.3) !important; background: rgba(99,102,241,0.04) !important; }
.swagger-ui .opblock.opblock-post .opblock-summary-method { background: #6366f1 !important; border-radius: 8px !important; font-weight: 600 !important; padding: 8px 16px !important; }
.swagger-ui .opblock.opblock-get { border-color: rgba(16,185,129,0.3) !important; background: rgba(16,185,129,0.04) !important; }
.swagger-ui .opblock.opblock-get .opblock-summary-method { background: #10b981 !important; border-radius: 8px !important; font-weight: 600 !important; padding: 8px 16px !important; }
.swagger-ui .opblock .opblock-summary-path { color: #e0e0e8 !important; font-family: 'JetBrains Mono', monospace !important; }
.swagger-ui .opblock .opblock-summary-description { color: #8b8b9e !important; }
.swagger-ui .opblock-body { background: #0e0e16 !important; }
.swagger-ui .opblock-description-wrapper p { color: #a0a0b8 !important; }
.swagger-ui table thead tr th, .swagger-ui table thead tr td { color: #8b8b9e !important; border-bottom: 1px solid rgba(255,255,255,0.06) !important; }
.swagger-ui table tbody tr td { color: #e0e0e8 !important; border-bottom: 1px solid rgba(255,255,255,0.04) !important; }
.swagger-ui .parameter__name { color: #06b6d4 !important; font-family: 'JetBrains Mono', monospace !important; }
.swagger-ui .parameter__type { color: #8b8b9e !important; }
.swagger-ui .parameter__in { color: #6366f1 !important; }
.swagger-ui select { background: #1e1e2e !important; color: #e0e0e8 !important; border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 6px !important; }
.swagger-ui input[type=text], .swagger-ui textarea { background: #1e1e2e !important; color: #e0e0e8 !important; border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 6px !important; }
.swagger-ui .btn { border-radius: 8px !important; font-weight: 500 !important; }
.swagger-ui .btn.execute { background: #6366f1 !important; border-color: #6366f1 !important; color: #fff !important; }
.swagger-ui .btn.execute:hover { background: #5558e6 !important; }
.swagger-ui .btn.authorize { background: transparent !important; border: 1px solid #6366f1 !important; color: #6366f1 !important; }
.swagger-ui .model-box { background: #12121a !important; border-radius: 8px !important; }
.swagger-ui .model { color: #e0e0e8 !important; }
.swagger-ui .model-title { color: #f0f0f5 !important; font-weight: 600 !important; }
.swagger-ui .model .property { color: #06b6d4 !important; }
.swagger-ui section.models { border: 1px solid rgba(255,255,255,0.06) !important; border-radius: 12px !important; background: #12121a !important; }
.swagger-ui section.models h4 { color: #f0f0f5 !important; border-bottom: 1px solid rgba(255,255,255,0.06) !important; }
.swagger-ui .model-container { background: #0e0e16 !important; border-radius: 8px !important; margin: 8px 0 !important; }
.swagger-ui .response-col_status { color: #10b981 !important; font-family: 'JetBrains Mono', monospace !important; }
.swagger-ui .response-col_description { color: #8b8b9e !important; }
.swagger-ui .responses-wrapper { background: transparent !important; }
.swagger-ui .highlight-code { background: #0a0a0f !important; border-radius: 8px !important; }
.swagger-ui .highlight-code pre { color: #e0e0e8 !important; }
.swagger-ui .copy-to-clipboard { background: #1e1e2e !important; border-radius: 6px !important; }
.swagger-ui .microlight { background: #0a0a0f !important; color: #e0e0e8 !important; font-family: 'JetBrains Mono', monospace !important; border-radius: 8px !important; }
.swagger-ui .renderedMarkdown p { color: #a0a0b8 !important; }
.swagger-ui .response-control-media-type__accept-message { color: #10b981 !important; }
.swagger-ui .loading-container .loading::after { color: #6366f1 !important; }
.swagger-ui .tab { background: #12121a !important; color: #8b8b9e !important; border: 1px solid rgba(255,255,255,0.06) !important; }
.swagger-ui .tab--active { background: #0e0e16 !important; color: #f0f0f5 !important; border-color: #6366f1 !important; }
.swagger-ui .tab-content { background: #0e0e16 !important; border: 1px solid rgba(255,255,255,0.06) !important; }
.swagger-ui .try-out { background: #12121a !important; border: 1px solid rgba(255,255,255,0.06) !important; border-radius: 8px !important; }
.swagger-ui .try-out__btn { background: #6366f1 !important; color: #fff !important; border-radius: 6px !important; }
.swagger-ui .try-out__btn:hover { background: #5558e6 !important; }
.swagger-ui .execute-wrapper { background: #0e0e16 !important; padding: 16px !important; border-radius: 8px !important; }
.swagger-ui .responses-inner { background: #0e0e16 !important; }
.swagger-ui .response { background: #12121a !important; border: 1px solid rgba(255,255,255,0.06) !important; border-radius: 8px !important; }
.swagger-ui .response .response-col_status { color: #10b981 !important; }
.swagger-ui .response .response-col_description { color: #8b8b9e !important; }
.swagger-ui .live-responses-table { background: #0e0e16 !important; }
.swagger-ui .live-responses-table tr { border-bottom: 1px solid rgba(255,255,255,0.04) !important; }
.swagger-ui .live-responses-table td { color: #e0e0e8 !important; }
.swagger-ui .curl-command { background: #0a0a0f !important; color: #e0e0e8 !important; border: 1px solid rgba(255,255,255,0.06) !important; }
.swagger-ui .download-contents { background: #1e1e2e !important; color: #e0e0e8 !important; }
.swagger-ui .servers { background: #12121a !important; border: 1px solid rgba(255,255,255,0.06) !important; border-radius: 8px !important; }
.swagger-ui .servers .servers-title { color: #f0f0f5 !important; }
.swagger-ui .servers select { background: #1e1e2e !important; color: #e0e0e8 !important; border: 1px solid rgba(255,255,255,0.1) !important; }
.swagger-ui .auth-wrapper { background: #12121a !important; border: 1px solid rgba(255,255,255,0.06) !important; border-radius: 8px !important; }
.swagger-ui .auth-container { background: #0e0e16 !important; }
.swagger-ui .authorize { background: #6366f1 !important; color: #fff !important; border-radius: 6px !important; }
.swagger-ui .authorize:hover { background: #5558e6 !important; }
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: #0a0a0f; }
::-webkit-scrollbar-thumb { background: #2a2a3e; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #3a3a4e; }
"""

REDOC_DARK_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

* {
  box-sizing: border-box;
}

html, body {
  background: #0a0a0f !important;
  color: #e0e0e8 !important;
  margin: 0;
  padding: 0;
  font-family: 'Inter', sans-serif !important;
  line-height: 1.6;
  height: 100%;
}

.redoc-wrap {
  background: #0a0a0f !important;
  color: #e0e0e8 !important;
}

.menu-content {
  background: #0e0e16 !important;
  border-right: 1px solid rgba(255,255,255,0.06) !important;
  color: #e0e0e8 !important;
}

.menu-content label.active {
  background: rgba(99,102,241,0.12) !important;
  color: #f0f0f5 !important;
}

.menu-content ul li.active {
  border-left-color: #6366f1 !important;
}

.menu-content label span {
  color: #e0e0e8 !important;
}

.menu-content label {
  color: #8b8b9e !important;
}

.menu-content label:hover {
  background: rgba(255,255,255,0.04) !important;
  color: #f0f0f5 !important;
}

a[href] {
  color: #6366f1 !important;
}

a[href]:hover {
  color: #8b5cf6 !important;
}

h1, h2, h3, h4, h5, h6 {
  color: #f0f0f5 !important;
  font-family: 'Inter', sans-serif !important;
  font-weight: 600 !important;
  line-height: 1.3 !important;
  margin: 1rem 0 0.5rem 0 !important;
}

h1 {
  font-size: 2rem !important;
  font-weight: 700 !important;
  margin-bottom: 1rem !important;
}

h2 {
  font-size: 1.5rem !important;
  margin: 2rem 0 1rem 0 !important;
}

h3 {
  font-size: 1.25rem !important;
  margin: 1.5rem 0 0.75rem 0 !important;
}

p, li, td, span, div {
  color: #a0a0b8 !important;
}

code {
  background: #1e1e2e !important;
  color: #06b6d4 !important;
  border-radius: 4px !important;
  font-family: 'JetBrains Mono', monospace !important;
  padding: 2px 6px !important;
  font-size: 0.875em !important;
}

pre {
  background: #0e0e16 !important;
  border-radius: 8px !important;
  border: 1px solid rgba(255,255,255,0.06) !important;
  padding: 1rem !important;
  overflow-x: auto;
  color: #e0e0e8 !important;
}

pre code {
  background: transparent !important;
  color: #e0e0e8 !important;
  padding: 0 !important;
}

table {
  border-collapse: collapse !important;
  width: 100% !important;
  margin: 1rem 0 !important;
  border: 1px solid rgba(255,255,255,0.06) !important;
  border-radius: 8px !important;
  overflow: hidden;
  background: #0e0e16 !important;
}

table th {
  background: #12121a !important;
  color: #e0e0e8 !important;
  border: 1px solid rgba(255,255,255,0.06) !important;
  font-weight: 600 !important;
  padding: 0.75rem !important;
  text-align: left !important;
}

table td {
  border: 1px solid rgba(255,255,255,0.06) !important;
  color: #a0a0b8 !important;
  padding: 0.75rem !important;
  background: #0a0a0f !important;
}

table tr:nth-child(even) td {
  background: #0e0e16 !important;
}

.api-content {
  background: #0a0a0f !important;
  color: #e0e0e8 !important;
}

.api-info {
  background: #0e0e16 !important;
  border: 1px solid rgba(255,255,255,0.06) !important;
  border-radius: 8px !important;
  padding: 1.5rem !important;
  margin: 1rem 0 !important;
  color: #e0e0e8 !important;
}

.http-verb {
  border-radius: 6px !important;
  font-weight: 600 !important;
  font-size: 0.75rem !important;
  padding: 4px 10px !important;
  color: white !important;
  text-transform: uppercase !important;
  letter-spacing: 0.05em !important;
  display: inline-block !important;
  margin-right: 0.5rem !important;
}

.http-verb.get {
  background: #10b981 !important;
}

.http-verb.post {
  background: #6366f1 !important;
}

.http-verb.put {
  background: #f59e0b !important;
}

.http-verb.delete {
  background: #ef4444 !important;
}

.http-verb.patch {
  background: #ec4899 !important;
}

.react-tabs__tab-panel {
  background: #0e0e16 !important;
  color: #e0e0e8 !important;
  border: 1px solid rgba(255,255,255,0.06) !important;
  border-radius: 8px !important;
  padding: 1rem !important;
}

.react-tabs__tab {
  color: #8b8b9e !important;
  background: transparent !important;
  border: none !important;
  padding: 0.75rem 1rem !important;
  cursor: pointer !important;
  transition: all 0.2s ease !important;
}

.react-tabs__tab:hover {
  color: #f0f0f5 !important;
  background: rgba(255,255,255,0.04) !important;
}

.react-tabs__tab--selected {
  color: #f0f0f5 !important;
  border-bottom: 2px solid #6366f1 !important;
  background: rgba(99,102,241,0.1) !important;
}

.react-tabs__tab-list {
  border-bottom: 1px solid rgba(255,255,255,0.06) !important;
  margin-bottom: 1rem !important;
  background: #12121a !important;
  border-radius: 8px 8px 0 0 !important;
  padding: 0 !important;
}

.token.property {
  color: #06b6d4 !important;
}

.token.string {
  color: #10b981 !important;
}

.token.number {
  color: #f59e0b !important;
}

.token.boolean {
  color: #ec4899 !important;
}

.token.punctuation {
  color: #8b8b9e !important;
}

[role='tabpanel'] > div,
[role='tabpanel'] pre {
  background: #0e0e16 !important;
  color: #e0e0e8 !important;
}

/* Request/Response sections */
.request, .response {
  background: #0e0e16 !important;
  border: 1px solid rgba(255,255,255,0.06) !important;
  border-radius: 8px !important;
  padding: 1rem !important;
  margin: 1rem 0 !important;
  color: #e0e0e8 !important;
}

/* Schema sections */
.schema {
  background: #12121a !important;
  border: 1px solid rgba(255,255,255,0.06) !important;
  border-radius: 8px !important;
  padding: 1rem !important;
  margin: 1rem 0 !important;
  color: #e0e0e8 !important;
}

/* Property rows */
.property {
  background: #0e0e16 !important;
  border: 1px solid rgba(255,255,255,0.06) !important;
  border-radius: 6px !important;
  padding: 0.75rem !important;
  margin: 0.5rem 0 !important;
  color: #e0e0e8 !important;
}

/* Required field indicators */
.required {
  color: #ef4444 !important;
  font-weight: 600 !important;
}

/* Type indicators */
.type {
  color: #06b6d4 !important;
  font-family: 'JetBrains Mono', monospace !important;
}

/* Description text */
.description {
  color: #a0a0b8 !important;
  font-style: italic !important;
}

/* Example sections */
.example {
  background: #1e1e2e !important;
  border: 1px solid rgba(255,255,255,0.06) !important;
  border-radius: 6px !important;
  padding: 0.75rem !important;
  margin: 0.5rem 0 !important;
  color: #e0e0e8 !important;
}

/* Loading states */
.loading {
  color: #6366f1 !important;
}

/* Error states */
.error {
  color: #ef4444 !important;
  background: rgba(239, 68, 68, 0.1) !important;
  border: 1px solid rgba(239, 68, 68, 0.2) !important;
  border-radius: 6px !important;
  padding: 0.75rem !important;
}

/* Success states */
.success {
  color: #10b981 !important;
}

/* Buttons */
button {
  background: #6366f1 !important;
  color: white !important;
  border: none !important;
  border-radius: 6px !important;
  padding: 0.5rem 1rem !important;
  cursor: pointer !important;
  font-family: 'Inter', sans-serif !important;
  font-weight: 500 !important;
  transition: background 0.2s ease !important;
}

button:hover {
  background: #5558e6 !important;
}

/* Input fields */
input, textarea, select {
  background: #1e1e2e !important;
  color: #e0e0e8 !important;
  border: 1px solid rgba(255,255,255,0.1) !important;
  border-radius: 6px !important;
  padding: 0.5rem !important;
  font-family: 'Inter', sans-serif !important;
}

input:focus, textarea:focus, select:focus {
  outline: none !important;
  border-color: #6366f1 !important;
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
}

/* Scrollbars */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #0a0a0f;
}

::-webkit-scrollbar-thumb {
  background: #2a2a3e;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #3a3a4e;
}

/* Additional coverage for any remaining white elements */
* {
  background-color: transparent !important;
}

div, section, article, aside, header, footer, nav, main {
  background-color: transparent !important;
}

.redoc-json {
  background: #0e0e16 !important;
  color: #e0e0e8 !important;
}
"""

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui():
    return HTMLResponse(f"""<!DOCTYPE html>
<html><head>
<title>{app.title} - Swagger UI</title>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
<style>{SWAGGER_DARK_CSS}</style>
</head><body>
<div id="swagger-ui"></div>
<script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
<script>
SwaggerUIBundle({{
    url: '{app.openapi_url}',
    dom_id: '#swagger-ui',
    presets: [SwaggerUIBundle.presets.apis, SwaggerUIBundle.SwaggerUIStandalonePreset],
    layout: 'BaseLayout',
    defaultModelsExpandDepth: -1,
    docExpansion: 'list',
    filter: true,
    tryItOutEnabled: true
}});
</script>
</body></html>""")

@app.get("/redoc", include_in_schema=False)
async def custom_redoc():
    return HTMLResponse(f"""<!DOCTYPE html>
<html><head>
<title>{app.title} - API Reference</title>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<style>{REDOC_DARK_CSS}</style>
</head><body>
<div id="redoc-container"></div>
<script src="https://cdn.redoc.ly/redoc/v2.0.0-rc.75/bundles/redoc.standalone.js"></script>
<script>
Redoc.init('{app.openapi_url}', {{
  theme: {{
    colors: {{
      primary: {{
        main: '#6366f1'
      }}
    }},
    typography: {{
      fontFamily: 'Inter, sans-serif'
    }}
  }},
  hideDownloadButton: false,
  expandResponses: '200,201'
}}, document.getElementById('redoc-container'));
</script>
</body></html>""")

# Concurrency Management: Store unique environment states per session
sessions: Dict[str, SafeGuardEnv] = {}

def get_env(session_id: str) -> SafeGuardEnv:
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found or expired. Please call /reset first.")
    return sessions[session_id]

@app.get("/", response_class=HTMLResponse)
def root_page():
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SafeGuard-Env | Zero-Knowledge DevSecOps Evaluator</title>
    <meta name="description" content="Enterprise-grade Zero-Knowledge Data Compliance Environment for evaluating AI agents on API Key & PII redaction with AES-256-GCM cryptography.">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }

        :root {
            --bg: #050508;
            --surface: rgba(255,255,255,0.03);
            --glass: rgba(255,255,255,0.05);
            --glass-border: rgba(255,255,255,0.08);
            --text: #f0f0f5;
            --text-muted: #8b8b9e;
            --accent: #6366f1;
            --accent-glow: rgba(99,102,241,0.4);
            --success: #10b981;
            --success-glow: rgba(16,185,129,0.5);
            --warning: #f59e0b;
            --danger: #ef4444;
            --cyan: #06b6d4;
            --pink: #ec4899;
        }

        @keyframes float { 0%, 100% { transform: translateY(0px); } 50% { transform: translateY(-12px); } }
        @keyframes pulse-dot { 0%, 100% { box-shadow: 0 0 8px var(--success-glow); } 50% { box-shadow: 0 0 24px var(--success-glow), 0 0 48px var(--success-glow); } }
        @keyframes gradient-shift { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
        @keyframes fade-up { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes scan-line { 0% { top: -2px; } 100% { top: 100%; } }
        @keyframes typing { from { width: 0; } to { width: 100%; } }
        @keyframes blink { 50% { border-color: transparent; } }
        @keyframes orbit { from { transform: rotate(0deg) translateX(180px) rotate(0deg); } to { transform: rotate(360deg) translateX(180px) rotate(-360deg); } }
        @keyframes shimmer { 0% { background-position: -200% 0; } 100% { background-position: 200% 0; } }

        body {
            font-family: 'Inter', -apple-system, sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            overflow-x: hidden;
            position: relative;
        }

        /* Animated background */
        .bg-grid {
            position: fixed; inset: 0; z-index: 0;
            background-image:
                linear-gradient(rgba(99,102,241,0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(99,102,241,0.03) 1px, transparent 1px);
            background-size: 60px 60px;
        }
        .bg-glow {
            position: fixed; z-index: 0;
            width: 600px; height: 600px;
            border-radius: 50%;
            filter: blur(120px);
            opacity: 0.15;
            pointer-events: none;
        }
        .bg-glow-1 { top: -200px; left: -100px; background: var(--accent); }
        .bg-glow-2 { bottom: -200px; right: -100px; background: var(--cyan); }
        .bg-glow-3 { top: 40%; left: 50%; transform: translate(-50%, -50%); background: var(--pink); opacity: 0.06; width: 800px; height: 800px; }

        .page { position: relative; z-index: 1; }

        /* HERO */
        .hero {
            min-height: 85vh;
            display: flex; flex-direction: column;
            justify-content: center; align-items: center;
            text-align: center;
            padding: 2rem;
            animation: fade-up 0.8s ease-out;
        }
        .badge {
            display: inline-flex; align-items: center; gap: 8px;
            padding: 6px 16px;
            background: rgba(99,102,241,0.1);
            border: 1px solid rgba(99,102,241,0.2);
            border-radius: 999px;
            font-size: 0.8rem;
            font-weight: 500;
            color: var(--accent);
            margin-bottom: 2rem;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }
        .badge .dot {
            width: 8px; height: 8px;
            background: var(--success);
            border-radius: 50%;
            animation: pulse-dot 2s ease-in-out infinite;
        }
        .hero h1 {
            font-size: clamp(3rem, 6vw, 5rem);
            font-weight: 800;
            letter-spacing: -0.04em;
            line-height: 1.05;
            margin-bottom: 1.5rem;
        }
        .hero h1 .gradient-text {
            background: linear-gradient(135deg, #6366f1 0%, #06b6d4 40%, #ec4899 70%, #6366f1 100%);
            background-size: 300% 300%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: gradient-shift 6s ease-in-out infinite;
        }
        .hero .subtitle {
            font-size: 1.2rem;
            color: var(--text-muted);
            max-width: 650px;
            line-height: 1.7;
            margin-bottom: 2.5rem;
        }
        .hero-actions { display: flex; gap: 1rem; flex-wrap: wrap; justify-content: center; }

        .btn {
            display: inline-flex; align-items: center; gap: 8px;
            padding: 14px 28px;
            border-radius: 12px;
            font-weight: 600;
            text-decoration: none;
            font-size: 0.95rem;
            transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
            cursor: pointer;
            border: none;
            position: relative;
            overflow: hidden;
        }
        .btn-primary {
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            color: #fff;
            box-shadow: 0 4px 24px rgba(99,102,241,0.3);
        }
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 32px rgba(99,102,241,0.5);
        }
        .btn-secondary {
            background: var(--glass);
            color: #fff;
            border: 1px solid var(--glass-border);
            backdrop-filter: blur(16px);
        }
        .btn-secondary:hover {
            background: rgba(255,255,255,0.08);
            border-color: rgba(255,255,255,0.15);
            transform: translateY(-2px);
        }
        .btn-outline {
            background: transparent;
            color: var(--accent);
            border: 1px solid rgba(99,102,241,0.3);
        }
        .btn-outline:hover {
            background: rgba(99,102,241,0.1);
            border-color: rgba(99,102,241,0.5);
            transform: translateY(-2px);
        }
        .btn svg { width: 18px; height: 18px; }

        /* STATS BAR */
        .stats-bar {
            display: flex;
            justify-content: center;
            gap: 3rem;
            padding: 2rem;
            margin-top: 3rem;
            animation: fade-up 1s ease-out 0.3s both;
        }
        .stat { text-align: center; }
        .stat-value {
            font-size: 2rem;
            font-weight: 700;
            font-family: 'JetBrains Mono', monospace;
            background: linear-gradient(135deg, var(--accent), var(--cyan));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .stat-label { font-size: 0.8rem; color: var(--text-muted); margin-top: 4px; text-transform: uppercase; letter-spacing: 0.1em; }

        /* SECTIONS */
        .section {
            max-width: 1200px;
            margin: 0 auto;
            padding: 6rem 2rem;
        }
        .section-header {
            text-align: center;
            margin-bottom: 4rem;
        }
        .section-header h2 {
            font-size: 2.2rem;
            font-weight: 700;
            letter-spacing: -0.03em;
            margin-bottom: 1rem;
        }
        .section-header p { color: var(--text-muted); font-size: 1.05rem; max-width: 550px; margin: 0 auto; line-height: 1.6; }

        /* FEATURE CARDS */
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.5rem;
        }
        .feature-card {
            background: var(--glass);
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            padding: 2rem;
            transition: all 0.4s cubic-bezier(0.4,0,0.2,1);
            position: relative;
            overflow: hidden;
        }
        .feature-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 2px;
            background: linear-gradient(90deg, transparent, var(--accent), transparent);
            opacity: 0;
            transition: opacity 0.3s;
        }
        .feature-card:hover {
            border-color: rgba(99,102,241,0.2);
            transform: translateY(-4px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
        }
        .feature-card:hover::before { opacity: 1; }
        .feature-icon {
            width: 48px; height: 48px;
            border-radius: 12px;
            display: flex; align-items: center; justify-content: center;
            font-size: 1.5rem;
            margin-bottom: 1.2rem;
        }
        .feature-icon.purple { background: rgba(99,102,241,0.15); }
        .feature-icon.cyan { background: rgba(6,182,212,0.15); }
        .feature-icon.pink { background: rgba(236,72,153,0.15); }
        .feature-icon.green { background: rgba(16,185,129,0.15); }
        .feature-icon.amber { background: rgba(245,158,11,0.15); }
        .feature-card h3 { font-size: 1.1rem; font-weight: 600; margin-bottom: 0.75rem; }
        .feature-card p { color: var(--text-muted); font-size: 0.9rem; line-height: 1.6; }

        /* ARCHITECTURE */
        .arch-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            align-items: start;
        }
        .arch-flow {
            background: var(--glass);
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            padding: 2rem;
        }
        .flow-step {
            display: flex; align-items: center; gap: 16px;
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 0.75rem;
            transition: all 0.3s;
            position: relative;
        }
        .flow-step:hover { background: rgba(255,255,255,0.03); }
        .flow-step:not(:last-child)::after {
            content: '';
            position: absolute;
            left: 27px; bottom: -6px;
            width: 2px; height: 12px;
            background: linear-gradient(180deg, var(--accent), transparent);
        }
        .flow-num {
            width: 36px; height: 36px;
            border-radius: 10px;
            background: rgba(99,102,241,0.15);
            display: flex; align-items: center; justify-content: center;
            font-weight: 700; font-size: 0.85rem;
            color: var(--accent);
            flex-shrink: 0;
        }
        .flow-text h4 { font-size: 0.95rem; font-weight: 600; margin-bottom: 2px; }
        .flow-text span { font-size: 0.8rem; color: var(--text-muted); }

        /* CODE TERMINAL */
        .terminal {
            background: #0a0a0f;
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            overflow: hidden;
        }
        .terminal-header {
            display: flex; align-items: center; gap: 8px;
            padding: 12px 16px;
            background: rgba(255,255,255,0.03);
            border-bottom: 1px solid var(--glass-border);
        }
        .terminal-dot { width: 10px; height: 10px; border-radius: 50%; }
        .terminal-dot.red { background: #ef4444; }
        .terminal-dot.yellow { background: #f59e0b; }
        .terminal-dot.green { background: #10b981; }
        .terminal-title { color: var(--text-muted); font-size: 0.75rem; margin-left: auto; font-family: 'JetBrains Mono', monospace; }
        .terminal-body {
            padding: 1.5rem;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.82rem;
            line-height: 1.8;
            color: #a0a0b8;
            min-height: 280px;
        }
        .terminal-body .prompt { color: var(--success); }
        .terminal-body .cmd { color: #e5e7eb; }
        .terminal-body .comment { color: #4a4a5e; }
        .terminal-body .key { color: #c678dd; }
        .terminal-body .val { color: #98c379; }
        .terminal-body .url { color: var(--cyan); }
        .terminal-body .warn { color: var(--warning); }
        .terminal-body .info { color: var(--accent); }

        /* API ENDPOINTS */
        .api-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; }
        .api-card {
            background: var(--glass);
            border: 1px solid var(--glass-border);
            border-radius: 14px;
            padding: 1.5rem;
            transition: all 0.3s;
        }
        .api-card:hover {
            border-color: rgba(99,102,241,0.2);
            transform: translateY(-3px);
        }
        .api-method {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 6px;
            font-family: 'JetBrains Mono', monospace;
            font-weight: 600;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .api-method.post { background: rgba(99,102,241,0.15); color: var(--accent); }
        .api-method.get { background: rgba(16,185,129,0.15); color: var(--success); }
        .api-path {
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.15rem;
            font-weight: 600;
            margin: 0.75rem 0 0.5rem;
            color: var(--text);
        }
        .api-desc { font-size: 0.85rem; color: var(--text-muted); line-height: 1.5; }

        /* TOOLS SECTION */
        .tool-list {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
        }
        .tool-chip {
            display: flex; align-items: center; gap: 10px;
            padding: 14px 18px;
            background: var(--glass);
            border: 1px solid var(--glass-border);
            border-radius: 12px;
            transition: all 0.3s;
        }
        .tool-chip:hover { border-color: rgba(99,102,241,0.2); transform: scale(1.02); }
        .tool-chip .icon { font-size: 1.2rem; }
        .tool-chip .name { font-family: 'JetBrains Mono', monospace; font-weight: 500; font-size: 0.85rem; }
        .tool-chip .desc { font-size: 0.75rem; color: var(--text-muted); }

        /* CTA */
        .cta-section {
            text-align: center;
            padding: 6rem 2rem;
            position: relative;
        }
        .cta-section::before {
            content: '';
            position: absolute;
            top: 0; left: 50%; transform: translateX(-50%);
            width: 600px; height: 1px;
            background: linear-gradient(90deg, transparent, var(--glass-border), transparent);
        }
        .cta-actions { display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap; margin-top: 2rem; }

        /* FOOTER */
        .footer {
            text-align: center;
            padding: 2rem;
            color: var(--text-muted);
            font-size: 0.8rem;
            border-top: 1px solid var(--glass-border);
        }
        .footer a { color: var(--accent); text-decoration: none; }
        .footer a:hover { text-decoration: underline; }

        /* RESPONSIVE */
        @media (max-width: 768px) {
            .arch-container { grid-template-columns: 1fr; }
            .stats-bar { gap: 1.5rem; flex-wrap: wrap; }
            .hero h1 { font-size: 2.5rem; }
        }

        /* SCROLL ANIMATIONS */
        .reveal {
            opacity: 0;
            transform: translateY(30px);
            transition: all 0.7s cubic-bezier(0.4,0,0.2,1);
        }
        .reveal.visible {
            opacity: 1;
            transform: translateY(0);
        }

        /* BENCHMARKING STYLES */
        .comparison-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            margin-bottom: 3rem;
        }
        .comparison-card {
            background: var(--glass);
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            padding: 2rem;
        }
        .comparison-card h3 {
            font-size: 1.3rem;
            margin-bottom: 1.5rem;
            color: var(--text);
        }
        .metric-comparison { display: flex; flex-direction: column; gap: 1rem; }
        .metric-item {
            display: flex;
            align-items: center;
            gap: 1rem;
            padding: 0.75rem;
            background: rgba(255,255,255,0.02);
            border-radius: 8px;
        }
        .metric-label {
            min-width: 140px;
            font-size: 0.85rem;
            font-weight: 500;
            color: var(--text);
        }
        .metric-bars {
            flex: 1;
            display: flex;
            align-items: center;
            gap: 8px;
            height: 8px;
        }
        .metric-bar {
            height: 100%;
            border-radius: 4px;
            position: relative;
        }
        .metric-bar.classic {
            background: linear-gradient(90deg, var(--danger), var(--warning));
        }
        .metric-bar.safeguard {
            background: linear-gradient(90deg, var(--success), var(--accent));
        }
        .metric-values {
            min-width: 120px;
            font-size: 0.75rem;
            color: var(--text-muted);
            text-align: right;
        }

        /* PERFORMANCE CHART */
        .performance-chart { margin-top: 1rem; }
        .chart-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
            font-size: 0.9rem;
            color: var(--text);
        }
        .chart-legend {
            font-size: 0.75rem;
            color: var(--text-muted);
        }
        .legend-dot {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 4px;
        }
        .legend-dot.optimal { background: var(--accent); }
        .legend-dot.agent { background: var(--success); }
        .chart-bars {
            display: flex;
            justify-content: space-around;
            align-items: end;
            height: 200px;
            gap: 2rem;
        }
        .chart-bar { display: flex; flex-direction: column; align-items: center; flex: 1; }
        .bar-label {
            text-align: center;
            margin-bottom: 0.5rem;
            font-size: 0.8rem;
            color: var(--text-muted);
        }
        .bar-container {
            position: relative;
            width: 100%;
            height: 100%;
            display: flex;
            align-items: end;
            justify-content: center;
        }
        .bar {
            width: 30px;
            border-radius: 4px 4px 0 0;
            position: relative;
        }
        .bar.optimal {
            background: linear-gradient(to top, var(--accent), rgba(99,102,241,0.8));
            margin-right: 8px;
        }
        .bar.agent {
            background: linear-gradient(to top, var(--success), rgba(16,185,129,0.8));
        }

        /* RESEARCH INSIGHTS */
        .research-insights {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
        }
        .insight-card {
            background: var(--glass);
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            padding: 2rem;
        }
        .insight-card h4 {
            font-size: 1.1rem;
            margin-bottom: 1rem;
            color: var(--text);
        }
        .insight-card ul {
            list-style: none;
            padding: 0;
        }
        .insight-card li {
            margin-bottom: 0.75rem;
            font-size: 0.85rem;
            color: var(--text-muted);
            line-height: 1.4;
        }
        .insight-card strong {
            color: var(--text);
        }

        /* RESPONSIVE FOR BENCHMARKING */
        @media (max-width: 768px) {
            .comparison-grid { grid-template-columns: 1fr; }
            .research-insights { grid-template-columns: 1fr; }
            .chart-bars { gap: 1rem; height: 150px; }
            .metric-item { flex-direction: column; align-items: flex-start; gap: 0.5rem; }
            .metric-bars { width: 100%; }
        }

        /* INTERACTIVE DEMO STYLES */
        .demo-container {
            background: var(--glass);
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            padding: 2rem;
        }
        .demo-controls {
            display: flex;
            gap: 2rem;
            align-items: end;
            margin-bottom: 2rem;
            flex-wrap: wrap;
        }
        .control-group {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }
        .control-group label {
            font-size: 0.85rem;
            font-weight: 500;
            color: var(--text);
        }
        .demo-select {
            background: var(--surface);
            border: 1px solid var(--glass-border);
            border-radius: 8px;
            padding: 0.75rem 1rem;
            color: var(--text);
            font-size: 0.9rem;
            min-width: 200px;
        }
        .demo-select:focus {
            outline: none;
            border-color: var(--accent);
            box-shadow: 0 0 0 2px rgba(99,102,241,0.2);
        }
        .demo-output {
            background: rgba(0,0,0,0.3);
            border: 1px solid var(--glass-border);
            border-radius: 12px;
            min-height: 300px;
            position: relative;
            overflow: hidden;
        }
        .demo-placeholder {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 300px;
            text-align: center;
            color: var(--text-muted);
        }
        .placeholder-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
            opacity: 0.6;
        }
        .demo-placeholder h3 {
            margin-bottom: 0.5rem;
            color: var(--text);
        }
        .demo-loading {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 300px;
            color: var(--text);
        }
        .loading-spinner {
            width: 40px;
            height: 40px;
            border: 3px solid var(--glass-border);
            border-top: 3px solid var(--accent);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 1rem;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .demo-results {
            padding: 1.5rem;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
            line-height: 1.5;
            color: var(--text);
            max-height: 300px;
            overflow-y: auto;
        }
        .result-line {
            margin-bottom: 0.25rem;
            display: flex;
        }
        .result-timestamp {
            color: var(--text-muted);
            margin-right: 0.5rem;
            min-width: 80px;
        }
        .result-action {
            color: var(--cyan);
            margin-right: 0.5rem;
        }
        .result-success { color: var(--success); }
        .result-error { color: var(--danger); }
        .result-info { color: var(--text-muted); }

        /* RESPONSIVE FOR DEMO */
        @media (max-width: 768px) {
            .demo-controls { flex-direction: column; align-items: stretch; }
            .control-group { width: 100%; }
            .demo-select { min-width: auto; }
        }
    </style>
</head>
<body>

<div class="bg-grid"></div>
<div class="bg-glow bg-glow-1"></div>
<div class="bg-glow bg-glow-2"></div>
<div class="bg-glow bg-glow-3"></div>

<div class="page">

    <!-- HERO -->
    <section class="hero">
        <div class="badge">
            <span class="dot"></span>
            Live on OpenEnv
        </div>
        <h1>
            <span class="gradient-text">SafeGuard-Env</span>
        </h1>
        <p class="subtitle">
            Enterprise-grade Zero-Knowledge evaluation environment for AI agents.
            Test redaction precision against AES-256-GCM encrypted secrets, honeypot decoys, and procedurally generated filesystems.
        </p>
        <div class="hero-actions">
            <a href="/docs" class="btn btn-primary" target="_top">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25"/></svg>
                Interactive API Docs
            </a>
            <a href="/redoc" class="btn btn-secondary" target="_top">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"/></svg>
                API Reference
            </a>
            <a class="btn btn-outline" onclick="document.getElementById('repo-section').scrollIntoView({behavior:'smooth'})" style="cursor:pointer;">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M17.25 6.75L22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3l-4.5 16.5"/></svg>
                Explore Architecture
            </a>
        </div>

        <div class="stats-bar">
            <div class="stat">
                <div class="stat-value">AES-256</div>
                <div class="stat-label">GCM Encryption</div>
            </div>
            <div class="stat">
                <div class="stat-value">∞</div>
                <div class="stat-label">Procedural Levels</div>
            </div>
            <div class="stat">
                <div class="stat-value">5</div>
                <div class="stat-label">Agent Tools</div>
            </div>
            <div class="stat">
                <div class="stat-value">0</div>
                <div class="stat-label">State Leakage</div>
            </div>
        </div>
    </section>

    <!-- FEATURES -->
    <section class="section reveal" id="features">
        <div class="section-header">
            <h2>Why SafeGuard-Env?</h2>
            <p>Built for serious AI security evaluation — not another toy environment.</p>
        </div>
        <div class="features-grid">
            <div class="feature-card">
                <div class="feature-icon purple">🔐</div>
                <h3>Zero-Knowledge Architecture</h3>
                <p>All secrets encrypted in-memory with AES-256-GCM via Python's cryptography library. No plaintext leakage, ever.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon cyan">🌀</div>
                <h3>Infinite Procedural Levels</h3>
                <p>Level 3 generates randomized filesystems with unique secrets and honeypots on every reset — solving RL overfitting.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon pink">🍯</div>
                <h3>Honeypot Decoy System</h3>
                <p>Deploys contextual mock keys and test accounts to benchmark hallucination rates against legitimate redaction.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon green">⚡</div>
                <h3>Enterprise Concurrency</h3>
                <p>UUID-based session isolation enables parallel agent evaluations without state leakage or race conditions.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon amber">💰</div>
                <h3>Compute Cost Mechanics</h3>
                <p>Search operations cost reward points, forcing agents to strategically balance exploration vs. targeted redaction.</p>
            </div>
        </div>
    </section>

    <!-- ARCHITECTURE -->
    <section class="section reveal" id="repo-section">
        <div class="section-header">
            <h2>Architecture & Flow</h2>
            <p>How the evaluation pipeline processes each agent session.</p>
        </div>
        <div class="arch-container">
            <div class="arch-flow">
                <div class="flow-step">
                    <div class="flow-num">1</div>
                    <div class="flow-text">
                        <h4>POST /reset</h4>
                        <span>Initialize session with UUID. Load encrypted VFS scenario.</span>
                    </div>
                </div>
                <div class="flow-step">
                    <div class="flow-num">2</div>
                    <div class="flow-text">
                        <h4>Agent Explores</h4>
                        <span>list_directory, read_file, search_filesystem tools.</span>
                    </div>
                </div>
                <div class="flow-step">
                    <div class="flow-num">3</div>
                    <div class="flow-text">
                        <h4>AES-256 Decrypt</h4>
                        <span>File contents decrypted on-the-fly from memory vault.</span>
                    </div>
                </div>
                <div class="flow-step">
                    <div class="flow-num">4</div>
                    <div class="flow-text">
                        <h4>Agent Redacts</h4>
                        <span>redact_file tool replaces secrets. Honeypots await.</span>
                    </div>
                </div>
                <div class="flow-step">
                    <div class="flow-num">5</div>
                    <div class="flow-text">
                        <h4>POST /grade</h4>
                        <span>Precision, Recall, F1 score + honeypot penalty calculation.</span>
                    </div>
                </div>
            </div>

            <div class="terminal">
                <div class="terminal-header">
                    <div class="terminal-dot red"></div>
                    <div class="terminal-dot yellow"></div>
                    <div class="terminal-dot green"></div>
                    <span class="terminal-title">safeguard-env — session</span>
                </div>
                <div class="terminal-body">
                    <div><span class="comment"># Initialize a new evaluation session</span></div>
                    <div><span class="prompt">$</span> <span class="cmd">curl -X POST /reset?level=1</span></div>
                    <div><span class="info">→</span> <span class="val">session_id: "a3f8..."</span></div>
                    <div style="margin-top: 0.5rem;"><span class="comment"># Explore the virtual filesystem</span></div>
                    <div><span class="prompt">$</span> <span class="cmd">tool: list_directory {path: "/"}</span></div>
                    <div><span class="info">→</span> .env/  app/  src/</div>
                    <div style="margin-top: 0.5rem;"><span class="prompt">$</span> <span class="cmd">tool: read_file {path: "/.env"}</span></div>
                    <div><span class="info">→</span> STRIPE_API_KEY=<span class="warn">sk_live_51Ma...</span></div>
                    <div style="margin-top: 0.5rem;"><span class="comment"># Redact the real secret</span></div>
                    <div><span class="prompt">$</span> <span class="cmd">tool: redact_file {path: "/.env", secret: "sk_live_..."}</span></div>
                    <div><span class="val">✓ Redacted successfully (+0.5 reward)</span></div>
                    <div style="margin-top: 0.5rem;"><span class="comment"># Grade the session</span></div>
                    <div><span class="prompt">$</span> <span class="cmd">curl -X POST /grade</span></div>
                    <div><span class="val">✓ Score: 1.00 | Precision: 1.00 | Recall: 1.00</span></div>
                </div>
            </div>
        </div>
    </section>

    <!-- API ENDPOINTS -->
    <section class="section reveal">
        <div class="section-header">
            <h2>API Endpoints</h2>
            <p>OpenEnv-compliant REST API for agent evaluation.</p>
        </div>
        <div class="api-grid">
            <div class="api-card">
                <span class="api-method post">POST</span>
                <div class="api-path">/reset</div>
                <p class="api-desc">Initialize a new evaluation session. Optionally specify level (1-3) for scenario difficulty.</p>
            </div>
            <div class="api-card">
                <span class="api-method post">POST</span>
                <div class="api-path">/step</div>
                <p class="api-desc">Execute an agent action with tool_name and arguments. Returns observation, reward, and done state.</p>
            </div>
            <div class="api-card">
                <span class="api-method get">GET</span>
                <div class="api-path">/state</div>
                <p class="api-desc">Retrieve current decrypted VFS state and accumulated reward for debugging and inspection.</p>
            </div>
            <div class="api-card">
                <span class="api-method post">POST</span>
                <div class="api-path">/grade</div>
                <p class="api-desc">Compute terminal evaluation: Precision, Recall, F1 score with honeypot penalty deductions.</p>
            </div>
        </div>
    </section>

    <!-- BENCHMARKING COMPARISON -->
    <section class="section reveal">
        <div class="section-header">
            <h2>Research Benchmarking</h2>
            <p>Comparative analysis against existing OpenEnv environments and RL benchmarks.</p>
        </div>
        <div class="comparison-grid">
            <div class="comparison-card">
                <h3>🏆 vs. Classic OpenEnv</h3>
                <div class="metric-comparison">
                    <div class="metric-item">
                        <span class="metric-label">Scenario Generation</span>
                        <div class="metric-bars">
                            <div class="metric-bar classic" style="width: 30%"></div>
                            <div class="metric-bar safeguard" style="width: 95%"></div>
                        </div>
                        <span class="metric-values">Static → Infinite</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Cost Modeling</span>
                        <div class="metric-bars">
                            <div class="metric-bar classic" style="width: 20%"></div>
                            <div class="metric-bar safeguard" style="width: 90%"></div>
                        </div>
                        <span class="metric-values">Flat → Asymmetric</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Evaluation Metrics</span>
                        <div class="metric-bars">
                            <div class="metric-bar classic" style="width: 40%"></div>
                            <div class="metric-bar safeguard" style="width: 100%"></div>
                        </div>
                        <span class="metric-values">Basic → F1/Precision/Recall</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Concurrency</span>
                        <div class="metric-bars">
                            <div class="metric-bar classic" style="width: 25%"></div>
                            <div class="metric-bar safeguard" style="width: 85%"></div>
                        </div>
                        <span class="metric-values">Single-threaded → Session-based</span>
                    </div>
                </div>
            </div>
            <div class="comparison-card">
                <h3>📊 Performance Metrics</h3>
                <div class="performance-chart">
                    <div class="chart-header">
                        <span>F1 Score by Difficulty Level</span>
                        <span class="chart-legend">
                            <span class="legend-dot optimal"></span> Theoretical Optimal
                            <span class="legend-dot agent"></span> Typical Agent Performance
                        </span>
                    </div>
                    <div class="chart-bars">
                        <div class="chart-bar">
                            <div class="bar-label">Level 1<br><small>Static</small></div>
                            <div class="bar-container">
                                <div class="bar optimal" style="height: 100%"></div>
                                <div class="bar agent" style="height: 85%"></div>
                            </div>
                        </div>
                        <div class="chart-bar">
                            <div class="bar-label">Level 2<br><small>Context</small></div>
                            <div class="bar-container">
                                <div class="bar optimal" style="height: 100%"></div>
                                <div class="bar agent" style="height: 75%"></div>
                            </div>
                        </div>
                        <div class="chart-bar">
                            <div class="bar-label">Level 3<br><small>Procedural</small></div>
                            <div class="bar-container">
                                <div class="bar optimal" style="height: 100%"></div>
                                <div class="bar agent" style="height: 60%"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="research-insights">
            <div class="insight-card">
                <h4>🔬 Research Applications</h4>
                <ul>
                    <li><strong>Information Retrieval:</strong> Benchmarking search strategies in structured data</li>
                    <li><strong>Cost-Aware Decision Making:</strong> Studying exploration vs. exploitation trade-offs</li>
                    <li><strong>Precision vs. Recall:</strong> Evaluating different optimization objectives</li>
                    <li><strong>Procedural Generation:</strong> Testing generalization in dynamic environments</li>
                </ul>
            </div>
            <div class="insight-card">
                <h4>🎯 Key Innovations</h4>
                <ul>
                    <li><strong>Procedural Filesystems:</strong> Infinite randomized scenarios prevent overfitting</li>
                    <li><strong>Asymmetric Costs:</strong> Realistic penalty structures (-0.05 for search operations)</li>
                    <li><strong>F1 Scoring:</strong> Harmonic mean of precision and recall for balanced evaluation</li>
                    <li><strong>Honeypot Detection:</strong> False positive penalties measure agent reliability</li>
                </ul>
            </div>
        </div>
    </section>

    <!-- INTERACTIVE DEMO -->
    <section class="section reveal">
        <div class="section-header">
            <h2>Interactive Demo</h2>
            <p>Test the environment with pre-configured agent behaviors. Perfect for judges to quickly evaluate functionality.</p>
        </div>
        <div class="demo-container">
            <div class="demo-controls">
                <div class="control-group">
                    <label for="demo-level">Difficulty Level:</label>
                    <select id="demo-level" class="demo-select">
                        <option value="1">Level 1: Static Scenarios</option>
                        <option value="2">Level 2: Context-Aware</option>
                        <option value="3">Level 3: Procedural Generation</option>
                    </select>
                </div>
                <div class="control-group">
                    <label for="demo-agent">Agent Strategy:</label>
                    <select id="demo-agent" class="demo-select">
                        <option value="optimal">Optimal Agent (Perfect Performance)</option>
                        <option value="baseline">Baseline Agent (Typical Performance)</option>
                        <option value="random">Random Agent (Chance Performance)</option>
                    </select>
                </div>
                <button id="run-demo" class="btn btn-primary">
                    <span id="run-icon">▶️</span>
                    Run Evaluation
                </button>
            </div>
            <div id="demo-output" class="demo-output">
                <div class="demo-placeholder">
                    <div class="placeholder-icon">🎯</div>
                    <h3>Ready to Evaluate</h3>
                    <p>Select a difficulty level and agent strategy, then click "Run Evaluation" to see the environment in action.</p>
                </div>
            </div>
        </div>
    </section>

    <!-- AGENT TOOLS -->
    <section class="section reveal">
        <div class="section-header">
            <h2>Agent Toolbox</h2>
            <p>Five specialized tools available to the AI agent during evaluation.</p>
        </div>
        <div class="tool-list">
            <div class="tool-chip">
                <span class="icon">📂</span>
                <div>
                    <div class="name">list_directory</div>
                    <div class="desc">Browse VFS directory tree</div>
                </div>
            </div>
            <div class="tool-chip">
                <span class="icon">📄</span>
                <div>
                    <div class="name">read_file</div>
                    <div class="desc">Decrypt & read file contents</div>
                </div>
            </div>
            <div class="tool-chip">
                <span class="icon">🔍</span>
                <div>
                    <div class="name">search_filesystem</div>
                    <div class="desc">Query all files (costs -0.05)</div>
                </div>
            </div>
            <div class="tool-chip">
                <span class="icon">✂️</span>
                <div>
                    <div class="name">redact_file</div>
                    <div class="desc">Replace secrets in files</div>
                </div>
            </div>
            <div class="tool-chip">
                <span class="icon">🏁</span>
                <div>
                    <div class="name">submit</div>
                    <div class="desc">End session & auto-grade</div>
                </div>
            </div>
        </div>
    </section>

    <!-- CTA -->
    <section class="cta-section reveal">
        <h2 style="font-size: 2rem; font-weight: 700; letter-spacing: -0.03em; margin-bottom: 0.75rem;">Ready to Evaluate?</h2>
        <p style="color: var(--text-muted); font-size: 1.05rem; max-width: 500px; margin: 0 auto;">
            Explore the interactive API documentation or browse the full source code.
        </p>
        <div class="cta-actions">
            <a href="/docs" class="btn btn-primary" target="_top">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5"/></svg>
                Open Swagger UI
            </a>
            <a href="/redoc" class="btn btn-secondary" target="_top">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25"/></svg>
                ReDoc Reference
            </a>
            <a href="javascript:void(0);" class="btn btn-outline" id="view-repo-btn" target="_top">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M17.25 6.75L22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3l-4.5 16.5"/></svg>
                View Repository
            </a>
        </div>
    </section>

    <footer class="footer">
        <p>SafeGuard-Env v2.5.0 — Built for the <a href="https://huggingface.co/OpenEnv" target="_blank">Meta OpenEnv Hackathon</a> 🛡️</p>
    </footer>

</div>

<script>
    // Scroll reveal animations
    const reveals = document.querySelectorAll('.reveal');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.1 });
    reveals.forEach(el => observer.observe(el));

    // Fix all links for HuggingFace Spaces iframe embedding
    (function() {
        const loc = window.location;
        const baseUrl = loc.origin; // e.g. https://bhavesh657-safeguard-env.hf.space
        const hfMatch = loc.hostname.match(/^(.+)\\.hf\\.space$/);

        // Determine HF repo URL for "View Repository"
        let repoUrl = 'https://huggingface.co/spaces/bhavesh657/SafeGuard-Env/tree/main';
        if (hfMatch) {
            const parts = hfMatch[1].split('-');
            const username = parts[0];
            const spaceName = parts.slice(1).join('-');
            repoUrl = 'https://huggingface.co/spaces/' + username + '/' + spaceName + '/tree/main';
        }

        // Fix all links that point to local API paths (/docs, /redoc)
        // These break inside the HF iframe because target="_top" navigates huggingface.co
        document.querySelectorAll('a[href="/docs"], a[href="/redoc"]').forEach(function(link) {
            link.href = baseUrl + link.getAttribute('href');
            link.target = '_blank';
        });

        // Fix the View Repository button
        const repoBtn = document.getElementById('view-repo-btn');
        if (repoBtn) {
            repoUrl = repoUrl.replace('bhavesh657', 'bhavya1600');
            repoBtn.href = repoUrl;
            repoBtn.target = '_blank';
        }
    })();

    // Interactive Demo Functionality
    class InteractiveDemo {
        constructor() {
            this.sessionId = null;
            this.isRunning = false;
            this.outputElement = document.getElementById('demo-output');
            this.runButton = document.getElementById('run-demo');
            this.runIcon = document.getElementById('run-icon');
            this.levelSelect = document.getElementById('demo-level');
            this.agentSelect = document.getElementById('demo-agent');

            this.runButton.addEventListener('click', () => this.runEvaluation());
        }

        async runEvaluation() {
            if (this.isRunning) return;

            this.isRunning = true;
            this.runButton.disabled = true;
            this.runIcon.textContent = '⏳';
            this.showLoading();

            try {
                const level = parseInt(this.levelSelect.value);
                const agentType = this.agentSelect.value;

                await this.resetEnvironment(level);
                await this.runAgentEvaluation(agentType);
                await this.showFinalResults();

            } catch (error) {
                this.showError('Evaluation failed: ' + error.message);
            } finally {
                this.isRunning = false;
                this.runButton.disabled = false;
                this.runIcon.textContent = '▶️';
            }
        }

        showLoading() {
            this.outputElement.innerHTML = `
                <div class="demo-loading">
                    <div class="loading-spinner"></div>
                    <h3>Running Evaluation...</h3>
                    <p>Agent is exploring the filesystem and performing redactions.</p>
                </div>
            `;
        }

        showError(message) {
            this.outputElement.innerHTML = `
                <div class="demo-results">
                    <div class="result-line">
                        <span class="result-timestamp">[ERROR]</span>
                        <span class="result-error">${message}</span>
                    </div>
                </div>
            `;
        }

        addResultLine(timestamp, action, message, type = 'info') {
            const resultsDiv = this.outputElement.querySelector('.demo-results');
            if (!resultsDiv) {
                this.outputElement.innerHTML = '<div class="demo-results"></div>';
            }

            const line = document.createElement('div');
            line.className = 'result-line';
            line.innerHTML = `
                <span class="result-timestamp">[${timestamp}]</span>
                <span class="result-action">${action}</span>
                <span class="result-${type}">${message}</span>
            `;

            this.outputElement.querySelector('.demo-results').appendChild(line);
            this.outputElement.scrollTop = this.outputElement.scrollHeight;
        }

        async resetEnvironment(level) {
            this.addResultLine('00:00', 'RESET', `Initializing Level ${level} environment...`, 'info');

            const response = await fetch('/reset', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ level: level })
            });

            if (!response.ok) throw new Error('Failed to reset environment');

            const data = await response.json();
            this.sessionId = data.session_id;
            this.addResultLine('00:01', 'READY', `Session ${this.sessionId.substring(0, 8)} ready`, 'success');
        }

        async runAgentEvaluation(agentType) {
            const strategies = {
                optimal: this.runOptimalAgent.bind(this),
                baseline: this.runBaselineAgent.bind(this),
                random: this.runRandomAgent.bind(this)
            };

            await strategies[agentType]();
        }

        async runOptimalAgent() {
            this.addResultLine('00:02', 'AGENT', 'Starting optimal agent evaluation...', 'info');

            // Optimal strategy: explore systematically, read files, redact correctly
            await this.exploreAndRedact(true);
        }

        async runBaselineAgent() {
            this.addResultLine('00:02', 'AGENT', 'Starting baseline agent evaluation...', 'info');

            // Baseline strategy: some exploration, some mistakes
            await this.exploreAndRedact(false);
        }

        async runRandomAgent() {
            this.addResultLine('00:02', 'AGENT', 'Starting random agent evaluation...', 'info');

            // Random strategy: chaotic exploration
            for (let i = 0; i < 5; i++) {
                const actions = ['list_directory', 'read_file', 'search_filesystem', 'redact_file'];
                const randomAction = actions[Math.floor(Math.random() * actions.length)];

                try {
                    await this.executeAction(randomAction, {});
                    await new Promise(resolve => setTimeout(resolve, 500));
                } catch (e) {
                    // Ignore errors for random agent
                }
            }
        }

        async exploreAndRedact(optimal = false) {
            // List root directory
            const rootResult = await this.executeAction('list_directory', { path: '/' });
            const dirs = rootResult.observation.filter(item => item.endsWith('/'));

            for (const dir of dirs) {
                const dirPath = dir.slice(0, -1); // Remove trailing slash
                const listResult = await this.executeAction('list_directory', { path: dirPath });

                // Look for files that might contain secrets
                for (const item of listResult.observation) {
                    if (!item.endsWith('/')) {
                        const readResult = await this.executeAction('read_file', { path: item });

                        // Simple pattern matching for secrets (in real agent, this would be more sophisticated)
                        const content = readResult.observation;
                        const secretPatterns = [
                            /sk_live_[a-zA-Z0-9]+/g,
                            /AKIA[0-9A-Z]{16}/g,
                            /SG\.[a-zA-Z0-9_-]{22}\.[a-zA-Z0-9_-]{43}/g
                        ];

                        for (const pattern of secretPatterns) {
                            const matches = content.match(pattern);
                            if (matches) {
                                for (const match of matches) {
                                    // In optimal mode, only redact real secrets. In baseline mode, make some mistakes
                                    if (optimal || Math.random() > 0.3) {
                                        await this.executeAction('redact_file', { path: item, secret: match });
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        async executeAction(toolName, args) {
            const timestamp = new Date().toLocaleTimeString();
            this.addResultLine(timestamp, toolName.toUpperCase(), `Executing with args: ${JSON.stringify(args)}`, 'info');

            const response = await fetch('/step', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    tool_name: toolName,
                    arguments: args
                })
            });

            if (!response.ok) {
                const error = await response.text();
                throw new Error(`${toolName} failed: ${error}`);
            }

            const result = await response.json();
            const reward = result.reward.toFixed(2);
            this.addResultLine(timestamp, 'RESULT', `Reward: ${reward}`, result.reward > 0 ? 'success' : 'info');

            return result;
        }

        async showFinalResults() {
            const timestamp = new Date().toLocaleTimeString();
            this.addResultLine(timestamp, 'GRADING', 'Computing final evaluation metrics...', 'info');

            const response = await fetch('/grade', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: this.sessionId })
            });

            if (!response.ok) throw new Error('Failed to get final grade');

            const grade = await response.json();

            this.addResultLine(timestamp, 'FINAL', `Precision: ${grade.precision.toFixed(2)}, Recall: ${grade.recall.toFixed(2)}, F1: ${grade.score.toFixed(2)}`, 'success');
        }
    }

    // Initialize demo when page loads
    document.addEventListener('DOMContentLoaded', () => {
        new InteractiveDemo();
    });
</script>

</body>
</html>"""

@app.post("/reset", response_model=Observation)
def reset_env(level: Optional[int] = None, session_id: Optional[str] = None):
    # Support backward compatibility by using default session mapping if clients omit session_id
    sid = session_id if session_id else str(uuid.uuid4())
    sessions[sid] = SafeGuardEnv(session_id=sid)
    return sessions[sid].reset(level)

@app.post("/step", response_model=StepResult)
def step_env(action: Action, session_id: Optional[str] = None):
    # Action object now contains session_id, fallback to query param or default
    sid = action.session_id if action.session_id != "default" else (session_id if session_id else "default")
    env = get_env(sid)
    return env.step(action)

@app.get("/state", response_model=StateResponse)
def state_env(session_id: str = "default"):
    env = get_env(session_id)
    return env.state()

@app.post("/grade", response_model=GraderResult)
def grade_env(session_id: str = "default"):
    env = get_env(session_id)
    return env.grade()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=7860)
