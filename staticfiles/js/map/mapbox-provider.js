// Mapbox map provider implementation

let mapboxMap = null;

// Initialize Mapbox map
function initMapboxMap(containerId, accessToken, center = [29.9187, 31.2001], zoom = 14) {
    if (!accessToken) {
        console.error('Mapbox access token is required');
        return null;
    }

    mapboxgl.accessToken = accessToken;
    mapboxMap = new mapboxgl.Map({
        container: containerId,
        style: 'mapbox://styles/mapbox/streets-v12',
        center: center,
        zoom: zoom
    });

    mapboxMap.addControl(new mapboxgl.NavigationControl(), 'topright');
    mapboxMap.addControl(new mapboxgl.ScaleControl({ maxWidth: 100, unit: 'metric' }));

    return mapboxMap;
}

// Get the Mapbox map instance
function getMapboxMap() {
    return mapboxMap;
}

// Remove Mapbox map
function removeMapboxMap() {
    if (mapboxMap) {
        mapboxMap.remove();
        mapboxMap = null;
    }
}
