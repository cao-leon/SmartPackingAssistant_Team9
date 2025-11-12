# Smart Packing Assistant 

# 1. Executive Summary

Der Smart Packing Assistant ist ein kleiner, aber wirkungsvoller Microservice, der Reisenden beim Packen hilft. Statt „Gefühl und Chaos“ kombinieren wir Reiseziel, Zeitraum, Aktivitäten und einfache Wetterbuckets, um eine strukturierte, begründete Packliste zu erzeugen (z. B. „Regenjacke – hohe Regenwahrscheinlichkeit“).
Der Prototyp setzt bewusst auf Dummy-Wetterdaten (eigener Service) und liefert klare JSON-Antworten – ideal für schnelle Demos und spätere Integration in Apps.

# 2. Ziele des Projekts

Viele packen zu viel oder das Falsche. Unser Ziel: Stress rausnehmen, Zeit sparen, smarter packen.
Das System gibt kontextabhängige Vorschläge („Warme Jacke – ØTmax ≤ 10 °C“), reduziert unnötiges Gepäck und indirekt auch Spontankäufe vor Ort – gut für Geldbeutel und Umwelt.

# 3. Anwendung und Nutzung

Die App ist eine FastAPI mit zwei Haupt-Endpunkten:

POST /v1/packlist (bzw. GET-Wrapper): erstellt eine Packliste aus city, start, end, activities, profile.

POST /v1/chat (bzw. GET-Wrapper): erkennt einfache Intents/Slots aus Freitext (z. B. „Packliste für Barcelona, 4 Tage, im Sommer“) und erzeugt bei Bedarf direkt eine Liste.

Antworten sind JSON (Items mit Mengen, Wetterhinweisen, Unsicherheitstext).

# 4. Entwicklungsstand

Funktionierender Prototyp:

2 Container (API + Weather-Mock), orchestriert via Docker Compose

Swagger verfügbar; Health-Checks auf beiden Services

„KI-Anteil“ aktuell: Fuzzy Intent Matching (rapidfuzz) + regelbasierte Empfehlung (Profile, Wetter-Buckets)

Stabil lokal lauffähig und leicht erweiterbar (echte Wetter-API, Web-UI, mehr Regeln)

# 5. Projektdetails

API: FastAPI, Endpunkte

GET /health (API-Health)

POST /v1/packlist / GET /v1/packlist?...

POST /v1/chat / GET /v1/chat?...

Weather-Service: Dummy-Wetterdaten + /health

Logik:

Wetter → Bucket (warm/mild/cold) → beeinflusst Mengen

Profile (minimal, komfort, familie) skalieren Mengen

Aktivitäten fügen Item-Bausteine hinzu (z. B. Hiking)

Keine externen API-Keys nötig – alles lokal & offline nutzbar

# 6. Innovation

Pragmatische Kombination aus einfachen, erklärbaren Regeln und Intent-Erkennung: genau die Faktoren, die Menschen beim Packen wirklich nutzen (Wetter, Dauer, Aktivität, persönlicher Stil).
JSON-First, klare Struktur, leicht weiterzuverarbeiten – von Voice-Assistent bis Mobile-App.

# 7. Wirkung (Impact)

Zeitersparnis & weniger Entscheidungsstress

Weniger Überpacken, gezielte Empfehlungen statt Bauchgefühl

Anschlussfähig für Reise-Apps, Smart Assistants oder E-Commerce („Fehlt noch …?“)

# 8. Technische Exzellenz

Saubere Microservice-Trennung (API vs. Weather)

FastAPI, httpx, pydantic, rapidfuzz

Containerisierung mit Docker, reproduzierbar via docker compose

OpenAPI/Swagger out-of-the-box

# 9. Ethik, Transparenz und Inklusion

Keine personenbezogenen Daten

Nachvollziehbare Regeln (Begründungen in Klartext)

JSON-Schnittstelle → sprachneutral und barrierearm integrierbar

Fällt bei Unsicherheit auf konservative Defaults zurück

# 10. Zukunftsvision

Live-Wetter statt Dummy, User-Profile (z. B. „nur Handgepäck“), Empfehlungen mit CO₂-Hinweisen

Kalender-Integration („3 Tage Konferenz in …“)

Optional: LLM-Chatbot (z. B. OpenAI/Gemini) ist als Zusatz denkbar für kontextreichere Dialoge 

# Setup & Run

# Voraussetzungen:

# Docker Desktop (unter Windows mit WSL2 aktiviert)

Starten
# Im Projekt-Root
docker compose up -d --build

docker compose down 

docker build -t spa/weather:latest -f weather/Dockerfile .

docker build -t spa/api:latest     -f api/Dockerfile .

kind load docker-image spa/weather:latest
kind load docker-image spa/api:latest
kubectl apply -f k8s/namespace.yaml
kubectl create configmap spa-weather-data \
  --from-file=data/weather_dummy.json \
  -n spa
# Status prüfen
docker compose ps

Stoppen
docker compose down

Wichtige URLs

Swagger / API-Doku & Tester:
http://127.0.0.1:8083/docs

Health (API):
http://localhost:8083/health

Health (Weather-Mock):
http://localhost:8090/health

Schnelltest im Browser (GET-Wrapper aktiv)

Packliste (Beispiel):
http://127.0.0.1:8083/v1/packlist?city=Berlin&start=2025-12-20&end=2025-12-24&activities=hiking&profile=familie

Intent/Chat (Beispiel):
http://127.0.0.1:8083/v1/chat?message=Packliste%20f%C3%BCr%20Barcelona,%204%20Tage,%20im%20Sommer&profile=minimal

Alternativ: Tests per PowerShell (POST)
# Packliste
$pack = @{
  city="Berlin"; start="2025-12-20"; end="2025-12-24"
  activities=@("hiking"); profile="familie"
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Uri "http://127.0.0.1:8083/v1/packlist" `
  -Method POST -ContentType "application/json; charset=utf-8" `
  -Body ([Text.Encoding]::UTF8.GetBytes($pack))

# Chat
$chat = @{ message="Packliste für Barcelona, 4 Tage, im Sommer"; profile="minimal" } | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8083/v1/chat" `
  -Method POST -ContentType "application/json; charset=utf-8" `
  -Body ([Text.Encoding]::UTF8.GetBytes($chat))

Alternativ: Tests per curl (eine Zeile)
curl -s -X POST "http://127.0.0.1:8083/v1/packlist" \
  -H "Content-Type: application/json" \
  -d '{"city":"Berlin","start":"2025-12-20","end":"2025-12-24","activities":["hiking"],"profile":"familie"}'

Troubleshooting (kurz)

Method Not Allowed → Du hast GET auf einen POST-Endpoint geschickt → Swagger nutzen oder GET-Wrapper-URL oben.

Port belegt → docker compose down und ggf. docker compose up -d --build erneut.

Docker/WSL läuft nicht → Docker Desktop öffnen, WSL2 aktivieren.
