(() => {
    const weather = window.__WEATHER__ || {};
    const config = window.__APP_CONFIG__ || {};

    const elements = {
        clockDate: document.querySelector('[data-role="clock-date"]'),
        clockTime: document.querySelector('[data-role="clock-time"]'),
        sunrise: document.querySelector('[data-role="sunrise"]'),
        sunset: document.querySelector('[data-role="sunset"]'),
        locationName: document.querySelector('[data-role="location-name"]'),
        currentTemp: document.querySelector('[data-role="current-temp"]'),
        currentIcon: document.querySelector('[data-role="current-icon"]'),
        currentCondition: document.querySelector('[data-role="current-condition"]'),
        currentPrecip: document.querySelector('[data-role="current-precip"]'),
        currentCloud: document.querySelector('[data-role="current-cloud"]'),
        currentWind: document.querySelector('[data-role="current-wind"]'),
        currentHumidity: document.querySelector('[data-role="current-humidity"]'),
        dailyForecast: document.querySelector('[data-role="daily-forecast"]'),
        mapStatus: document.getElementById("map-status"),
        refreshButton: document.querySelector('[data-action="refresh"]'),
        recenterButton: document.querySelector('[data-action="recenter"]'),
    };

    let currentLat = weather.location ? weather.location.lat : null;
    let currentLon = weather.location ? weather.location.lon : null;
    let mapInstance = null;
    let mapMarker = null;

    const mapboxToken = (config.mapboxToken || "").trim();
    const mapZoom = config.mapZoom || 8;

    const fallbackValue = (value, fallback) => {
        if (value === null || value === undefined || value === "") {
            return fallback;
        }
        return value;
    };

    const formatClockDate = (date) => {
        return date
            .toLocaleDateString("en-US", {
                weekday: "long",
                month: "long",
                day: "numeric",
            })
            .toUpperCase();
    };

    const formatClockTime = (date) => {
        return date.toLocaleTimeString("en-US", {
            hour: "numeric",
            minute: "2-digit",
        });
    };

    const setMapStatus = (message) => {
        if (!elements.mapStatus) {
            return;
        }
        if (!message) {
            elements.mapStatus.hidden = true;
            elements.mapStatus.textContent = "";
            return;
        }
        elements.mapStatus.textContent = message;
        elements.mapStatus.hidden = false;
    };

    const updateClock = () => {
        const now = new Date();
        if (elements.clockDate) {
            elements.clockDate.textContent = formatClockDate(now);
        }
        if (elements.clockTime) {
            elements.clockTime.textContent = formatClockTime(now);
        }
    };

    const updateCurrentWeather = (data) => {
        if (!data || !data.current) {
            return;
        }
        const current = data.current;
        if (elements.currentTemp) {
            elements.currentTemp.textContent = fallbackValue(current.temp, "n/a");
        }
        if (elements.currentCondition) {
            elements.currentCondition.textContent = fallbackValue(current.condition, "Unknown");
        }
        if (elements.currentIcon) {
            const icon = fallbackValue(current.icon, "fa-cloud");
            elements.currentIcon.className = `fa-solid ${icon}`;
        }
        if (elements.currentPrecip) {
            elements.currentPrecip.textContent =
                current.precip_probability !== null && current.precip_probability !== undefined
                    ? `${current.precip_probability}%`
                    : "n/a";
        }
        if (elements.currentCloud) {
            elements.currentCloud.textContent =
                current.cloud_cover !== null && current.cloud_cover !== undefined
                    ? `${current.cloud_cover}%`
                    : "n/a";
        }
        if (elements.currentWind) {
            elements.currentWind.textContent =
                current.wind_speed !== null && current.wind_speed !== undefined
                    ? `${current.wind_speed} ${fallbackValue(current.wind_unit, "")}`.trim()
                    : "n/a";
        }
        if (elements.currentHumidity) {
            elements.currentHumidity.textContent =
                current.humidity !== null && current.humidity !== undefined
                    ? `${current.humidity}%`
                    : "n/a";
        }
    };

    const updateSunTimes = (data) => {
        if (!data || !data.sun) {
            return;
        }
        if (elements.sunrise) {
            elements.sunrise.textContent = fallbackValue(data.sun.sunrise, "n/a");
        }
        if (elements.sunset) {
            elements.sunset.textContent = fallbackValue(data.sun.sunset, "n/a");
        }
    };

    const createForecastCard = (day) => {
        const card = document.createElement("div");
        card.className = "forecast-card";

        const dayLabel = document.createElement("div");
        dayLabel.className = "forecast-day";
        dayLabel.textContent = fallbackValue(day.day, "");

        const temp = document.createElement("div");
        temp.className = "forecast-temp";
        const high = document.createElement("span");
        high.className = "high";
        high.textContent = day.high !== null && day.high !== undefined ? `${day.high}\u00B0` : "n/a";
        const low = document.createElement("span");
        low.className = "low";
        low.textContent = day.low !== null && day.low !== undefined ? `${day.low}\u00B0` : "n/a";
        temp.appendChild(high);
        temp.appendChild(low);

        const condition = document.createElement("div");
        condition.className = "forecast-condition";
        const icon = document.createElement("i");
        icon.className = `fa-solid ${fallbackValue(day.icon, "fa-cloud")}`;
        icon.setAttribute("aria-hidden", "true");
        const text = document.createElement("span");
        text.textContent = fallbackValue(day.condition, "");
        condition.appendChild(icon);
        condition.appendChild(text);

        const sun = document.createElement("div");
        sun.className = "forecast-sun";
        const sunrise = document.createElement("span");
        sunrise.innerHTML = `<i class="fa-solid fa-sun" aria-hidden="true"></i> ${fallbackValue(
            day.sunrise,
            "n/a"
        )}`;
        const sunset = document.createElement("span");
        sunset.innerHTML = `<i class="fa-solid fa-moon" aria-hidden="true"></i> ${fallbackValue(
            day.sunset,
            "n/a"
        )}`;
        sun.appendChild(sunrise);
        sun.appendChild(sunset);

        card.appendChild(dayLabel);
        card.appendChild(temp);
        card.appendChild(condition);
        card.appendChild(sun);
        return card;
    };

    const updateDailyForecast = (data) => {
        if (!elements.dailyForecast || !data || !Array.isArray(data.daily)) {
            return;
        }
        elements.dailyForecast.innerHTML = "";
        data.daily.forEach((day) => {
            elements.dailyForecast.appendChild(createForecastCard(day));
        });
    };

    const updateLocation = (data) => {
        if (!data || !data.location) {
            return;
        }
        if (elements.locationName) {
            elements.locationName.textContent = fallbackValue(data.location.name, "");
        }
        currentLat = data.location.lat;
        currentLon = data.location.lon;
    };

    const updateAll = (data) => {
        updateLocation(data);
        updateCurrentWeather(data);
        updateSunTimes(data);
        updateDailyForecast(data);
    };

    const fetchWeather = (lat, lon) => {
        if (lat === null || lon === null) {
            return;
        }
        setMapStatus("Updating weather...");
        fetch(`/api/weather?lat=${lat}&lon=${lon}`)
            .then((response) => response.json())
            .then((data) => {
                updateAll(data);
                setMapStatus("");
                if (mapMarker) {
                    mapMarker.setLatLng([lat, lon]);
                }
            })
            .catch(() => {
                setMapStatus("Unable to load weather data.");
            });
    };

    const initMap = () => {
        if (!window.L || !document.getElementById("map")) {
            setMapStatus("Map library failed to load.");
            return;
        }
        const initialLat = currentLat || 0;
        const initialLon = currentLon || 0;
        mapInstance = window.L.map("map", {
            zoomControl: false,
            attributionControl: true,
        }).setView([initialLat, initialLon], mapZoom);

        const useMapbox = mapboxToken.length > 0;
        const tileUrl = useMapbox
            ? `https://api.mapbox.com/styles/v1/mapbox/dark-v11/tiles/{z}/{x}/{y}?access_token=${mapboxToken}`
            : "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png";

        const tileOptions = useMapbox
            ? {
                  attribution: "© Mapbox © OpenStreetMap",
                  maxZoom: 18,
                  tileSize: 512,
                  zoomOffset: -1,
              }
            : {
                  attribution: "© OpenStreetMap © CARTO",
                  maxZoom: 18,
              };

        window.L.tileLayer(tileUrl, tileOptions).addTo(mapInstance);
        mapMarker = window.L.marker([initialLat, initialLon], { opacity: 0.8 }).addTo(mapInstance);

        mapInstance.on("click", (event) => {
            const { lat, lng } = event.latlng;
            fetchWeather(lat, lng);
        });
    };

    const bindControls = () => {
        if (elements.refreshButton) {
            elements.refreshButton.addEventListener("click", () => {
                fetchWeather(currentLat, currentLon);
            });
        }
        if (elements.recenterButton) {
            elements.recenterButton.addEventListener("click", () => {
                if (mapInstance && currentLat !== null && currentLon !== null) {
                    mapInstance.setView([currentLat, currentLon], mapZoom);
                }
                fetchWeather(currentLat, currentLon);
            });
        }
    };

    document.addEventListener("DOMContentLoaded", () => {
        updateClock();
        setInterval(updateClock, 1000);
        updateAll(weather);
        initMap();
        bindControls();
    });
})();
