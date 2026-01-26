# Setup Decisions Log (Detailed)

This log explains the reasoning behind each major setup and architectural
decision made while converting the project into a Flask-based weather station
modeled after the Pi Weather Station UI.

## 1. Framework Choice: Flask

- **Decision:** Use Flask for the backend and server-side rendering.
- **Why:** The request explicitly asked for a Python/Flask build. Flask keeps
  the app lightweight, is easy to deploy, and supports a single-page UI without
  requiring an additional front-end build pipeline.
- **Impact:** Enables simple routing (`/` for UI and `/api/weather` for data)
  and easy environment configuration via `.env`.

## 2. UI Structure: Mirror Pi Weather Station Layout

- **Decision:** Keep the original left-map/right-panel layout with a full
  height grid and a compact information panel.
- **Why:** The primary requirement was to stay visually close to
  `pi-weather-station`.
- **Difference Introduced:** Replaced the chart area with daily forecast
  blocks, each showing high/low, sunrise/sunset, and condition, per the
  request.
- **Impact:** The UI preserves the original look and feel while honoring the
  new daily block requirement.

## 3. Weather Data Provider: Open-Meteo + Sample Fallback

- **Decision:** Use Open-Meteo for live weather data, with a sample-data
  fallback.
- **Why:** Open-Meteo provides a reliable, keyless API for demos and testing,
  avoiding setup friction while still delivering real forecasts.
- **Fallback:** If the API is unavailable (network issues or rate limits), the
  app automatically falls back to built-in sample data to keep the UI working.
- **Impact:** The app is resilient and functional even in offline or CI
  environments.

## 4. Optional API Keys: Mapbox + LocationIQ

- **Decision:** Support optional Mapbox and LocationIQ keys.
- **Why:** The original Pi Weather Station uses Mapbox and reverse geocoding.
  Keeping optional support preserves compatibility without forcing keys.
- **Implementation:**
  - Mapbox token (if provided) upgrades map styling.
  - LocationIQ key (if provided) enables reverse geocoding to city names.
- **Impact:** Users get the premium experience when keys are available, but the
  app still runs without them.

## 5. Map Library Choice: Leaflet

- **Decision:** Use Leaflet for the interactive map.
- **Why:** Leaflet is lightweight, CDN-friendly, and works well in plain HTML
  without bundling. It also makes it easy to swap tile providers.
- **Fallback Tile Provider:** CARTO dark tiles are used when Mapbox is not
  configured. This matches the original dark theme and avoids key dependency.
- **Impact:** The map always renders, and styling improves automatically with
  a token.

## 6. Data Caching Strategy

- **Decision:** Add a simple in-memory cache with a TTL.
- **Why:** Weather calls should not be made on every page refresh or map click
  in quick succession. A TTL reduces API usage and improves responsiveness.
- **Implementation:** Cache is keyed by lat/lon + units with a default TTL of
  10 minutes, configurable via `WEATHER_CACHE_TTL`.
- **Impact:** Efficient API usage and smoother interaction.

## 7. Unified Data Shape for Template + API

- **Decision:** Shape weather data into a single normalized payload that is
  used for both server rendering and `/api/weather`.
- **Why:** Consistent payloads reduce UI complexity and minimize divergence
  between server-rendered HTML and client updates.
- **Impact:** Simpler front-end logic and predictable data handling.

## 8. Front-End Update Strategy

- **Decision:** Use lightweight vanilla JS for UI updates and map interaction.
- **Why:** Keeps the project small and avoids a heavy front-end build process,
  aligning with the Flask-first requirement.
- **Implementation:** The UI uses `data-role` attributes so JS can target
  updates safely and predictably.
- **Impact:** Minimal JavaScript with clear, maintainable selectors.

## 9. Testing Adjustments

- **Decision:** Update Selenium UI tests to match the new weather UI and set
  `WEATHER_MODE=sample` in test fixtures.
- **Why:** Tests should be deterministic and not rely on external services.
- **Impact:** CI remains stable, and tests validate the new layout and daily
  forecast blocks.

## 10. Documentation and Configuration

- **Decision:** Rewrite README and environment templates for weather use cases.
- **Why:** The old docs were Reddit-specific and no longer accurate.
- **Impact:** Clear setup instructions aligned with the new app behavior.

## 11. ASCII-First Content

- **Decision:** Keep all source files ASCII-only (with HTML entities where
  needed).
- **Why:** Matches the project requirement to avoid introducing Unicode unless
  already present.
- **Impact:** Consistent encoding and fewer rendering surprises.

---

If you want deeper customization (for example, swapping Open-Meteo for a
different weather API or adding radar overlays), the current structure keeps
those changes isolated and easy to extend.
