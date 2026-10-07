// Driver map implementation for admin view

let map;
let driverMarkers = {};
let driverHistoryPoints = {};
let currentMapProvider = localStorage.getItem('mapProvider') || 'leaflet';
const mapboxAccessToken = typeof mapbox_access_token !== 'undefined' ? mapbox_access_token : '';

// Render driver color legend
function renderDriverColorLegend(drivers) {
    const container = document.getElementById('driverColorLegend');
    if (!container) return;
    container.replaceChildren();

    drivers.forEach(driver => {
        const entry = document.createElement('span');
        entry.className = 'map-driver-color-key';

        const swatch = document.createElement('span');
        swatch.className = 'map-driver-color-swatch';
        swatch.style.backgroundColor = getDriverColor(driver.id);

        const name = document.createElement('span');
        name.textContent = driver.username;

        entry.append(swatch, name);
        container.appendChild(entry);
    });
}

// Switch map provider
function switchMapProvider(provider) {
    if (currentMapProvider === provider) return;

    currentMapProvider = provider;
    localStorage.setItem('mapProvider', provider);

    // Update buttons
    document.getElementById('leafletBtn').classList.toggle('active', provider === 'leaflet');
    document.getElementById('mapboxBtn').classList.toggle('active', provider === 'mapbox');

    // Reinitialize map
    if (map) {
        if (currentMapProvider === 'leaflet') {
            map.remove();
            initLeafletMap('map');
        } else {
            map.remove();
            initMapboxMap('map', mapboxAccessToken);
        }
        loadDriverLocations(true);
    }
}

// Initialize map
function initMap() {
    // Update buttons based on saved selection
    document.getElementById('leafletBtn').classList.toggle('active', currentMapProvider === 'leaflet');
    document.getElementById('mapboxBtn').classList.toggle('active', currentMapProvider === 'mapbox');

    if (currentMapProvider === 'leaflet') {
        map = initLeafletMap('map');
    } else {
        map = initMapboxMap('map', mapboxAccessToken);
    }

    // Load driver locations
    loadDriverLocations(true);

    // Auto-refresh every 15 seconds
    setInterval(() => loadDriverLocations(), 15000);
}

// Load driver locations
async function loadDriverLocations(fitToLocations = false) {
    const selectedDriver = document.getElementById('driverSelect').value;
    const markerPositions = [];
    let selectedPosition = null;

    try {
        const response = await fetch('/api/driver-locations/');
        if (!response.ok) {
            console.error('Failed to fetch driver locations:', response.status);
            return;
        }
        const data = await response.json();
        renderDriverColorLegend(data.drivers || []);

        if (currentMapProvider === 'leaflet') {
            loadDriverLocationsLeaflet(data, selectedDriver, markerPositions, selectedPosition, fitToLocations);
        } else {
            loadDriverLocationsMapbox(data, selectedDriver, markerPositions, selectedPosition, fitToLocations);
        }
    } catch (error) {
        console.error('Error loading driver locations:', error);
    }
}

// Load driver locations with Leaflet
function loadDriverLocationsLeaflet(data, selectedDriver, markerPositions, selectedPosition, fitToLocations) {
    // Clear old markers
    Object.values(driverMarkers).forEach(marker => map.removeLayer(marker));
    Object.values(driverHistoryPoints).flat().forEach(point => map.removeLayer(point));
    driverMarkers = {};
    driverHistoryPoints = {};

    // Add new markers
    if (data.drivers && data.drivers.length > 0) {
        data.drivers.forEach(driver => {
            if (selectedDriver && driver.id != selectedDriver) return;
            const driverColor = getDriverColor(driver.id);

            if (driver.latest_location) {
                const position = [driver.latest_location.latitude, driver.latest_location.longitude];
                markerPositions.push(position);
                if (selectedDriver) selectedPosition = position;

                if (driver.location_is_live) {
                    const liveIcon = L.divIcon({
                        className: 'driver-live-icon',
                        html: `<span class="driver-live-triangle" style="--driver-color:${driverColor}"></span>`,
                        iconSize: [24, 24],
                        iconAnchor: [12, 0],
                        popupAnchor: [0, -4]
                    });
                    const marker = L.marker(position, { icon: liveIcon })
                        .bindPopup(`<b>${driver.username}</b><br>الموقع الحي${driver.latest_location.accuracy_m == null ? '' : `<br>دقة تقديرية ±${Math.round(driver.latest_location.accuracy_m)}م`}<br>آخر تحديث: ${new Date(driver.latest_location.timestamp).toLocaleString('ar-EG')}`)
                        .addTo(map);
                    driverMarkers[driver.id] = marker;
                }
            }

            if (driver.locations && driver.locations.length) {
                driverHistoryPoints[driver.id] = driver.locations.map((location, index) => {
                    const pointPosition = [location.latitude, location.longitude];
                    markerPositions.push(pointPosition);
                    return L.circleMarker(pointPosition, {
                        radius: 5,
                        color: '#ffffff',
                        weight: 1.5,
                        fillColor: driverColor,
                        fillOpacity: 0.95
                    })
                    .bindPopup(`<b>${driver.username}</b><br>نقطة مسار ${index + 1}<br>${new Date(location.timestamp).toLocaleString('ar-EG')}`)
                    .addTo(map);
                });
            }
        });
    } else {
        console.log('No drivers found or no locations available');
    }

    if (fitToLocations && markerPositions.length) {
        if (selectedPosition && markerPositions.length === 1) {
            map.setView(selectedPosition, 15);
        } else {
            map.fitBounds(L.latLngBounds(markerPositions), {
                padding: [40, 40],
                maxZoom: 15
            });
        }
    }
}

// Load driver locations with Mapbox
function loadDriverLocationsMapbox(data, selectedDriver, markerPositions, selectedPosition, fitToLocations) {
    // Clear old layers
    const layersToRemove = [];
    if (map.getStyle()) {
        map.getStyle().layers.forEach(layer => {
            if (layer.id.startsWith('driver-')) {
                layersToRemove.push(layer.id);
            }
        });
    }
    layersToRemove.forEach(layerId => {
        if (map.getLayer(layerId)) map.removeLayer(layerId);
    });

    // Clear old sources
    ['drivers', 'driver-history'].forEach(sourceId => {
        if (map.getSource(sourceId)) map.removeSource(sourceId);
    });

    // Add new data
    const features = [];
    const historyFeatures = [];

    if (data.drivers && data.drivers.length > 0) {
        data.drivers.forEach(driver => {
            if (selectedDriver && driver.id != selectedDriver) return;
            const driverColor = getDriverColor(driver.id);

            if (driver.latest_location) {
                const position = [driver.latest_location.longitude, driver.latest_location.latitude];
                markerPositions.push(position);
                if (selectedDriver) selectedPosition = position;

                if (driver.location_is_live) {
                    features.push({
                        type: 'Feature',
                        geometry: {
                            type: 'Point',
                            coordinates: position
                        },
                        properties: {
                            id: driver.id,
                            username: driver.username,
                            color: driverColor,
                            accuracy: driver.latest_location.accuracy_m,
                            timestamp: driver.latest_location.timestamp
                        }
                    });
                }
            }

            if (driver.locations && driver.locations.length) {
                driver.locations.forEach((location, index) => {
                    const pointPosition = [location.longitude, location.latitude];
                    markerPositions.push(pointPosition);
                    historyFeatures.push({
                        type: 'Feature',
                        geometry: {
                            type: 'Point',
                            coordinates: pointPosition
                        },
                        properties: {
                            id: driver.id,
                            username: driver.username,
                            color: driverColor,
                            index: index,
                            timestamp: location.timestamp
                        }
                    });
                });
            }
        });
    }

    // Add layers to map
    if (map.loaded()) {
        addMapboxLayers(features, historyFeatures);
    } else {
        map.on('load', () => addMapboxLayers(features, historyFeatures));
    }

    // Move camera
    if (fitToLocations && markerPositions.length) {
        if (selectedPosition && markerPositions.length === 1) {
            map.flyTo({ center: selectedPosition, zoom: 15 });
        } else {
            const bounds = markerPositions.reduce((bounds, coord) => {
                return bounds.extend(coord);
            }, new mapboxgl.LngLatBounds(markerPositions[0], markerPositions[0]));

            map.fitBounds(bounds, {
                padding: 40,
                maxZoom: 15
            });
        }
    }
}

// Add Mapbox layers
function addMapboxLayers(features, historyFeatures) {
    // Add live location markers
    if (features.length > 0) {
        map.addSource('drivers', {
            type: 'geojson',
            data: {
                type: 'FeatureCollection',
                features: features
            }
        });

        map.addLayer({
            id: 'driver-markers',
            type: 'circle',
            source: 'drivers',
            paint: {
                'circle-radius': 10,
                'circle-color': ['get', 'color'],
                'circle-stroke-width': 2,
                'circle-stroke-color': '#ffffff'
            }
        });

        map.addLayer({
            id: 'driver-labels',
            type: 'symbol',
            source: 'drivers',
            layout: {
                'text-field': ['get', 'username'],
                'text-offset': [0, 1.5],
                'text-anchor': 'top',
                'text-size': 12
            },
            paint: {
                'text-color': '#000000',
                'text-halo-color': '#ffffff',
                'text-halo-width': 2
            }
        });
    }

    // Add route points
    if (historyFeatures.length > 0) {
        map.addSource('driver-history', {
            type: 'geojson',
            data: {
                type: 'FeatureCollection',
                features: historyFeatures
            }
        });

        map.addLayer({
            id: 'driver-history-points',
            type: 'circle',
            source: 'driver-history',
            paint: {
                'circle-radius': 5,
                'circle-color': ['get', 'color'],
                'circle-stroke-width': 1.5,
                'circle-stroke-color': '#ffffff',
                'circle-opacity': 0.8
            }
        });
    }
}

// Refresh map
function refreshMap() {
    loadDriverLocations(true);
}

// Change selected driver
document.getElementById('driverSelect').addEventListener('change', () => loadDriverLocations(true));

// Initialize map on load
document.addEventListener('DOMContentLoaded', initMap);
