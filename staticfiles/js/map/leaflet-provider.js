// Leaflet map provider implementation

let leafletMap = null;

// Initialize Leaflet map
function initLeafletMap(containerId, center = [31.2001, 29.9187], zoom = 14) {
    leafletMap = L.map(containerId).setView(center, zoom);

    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors, Tiles style by Humanitarian OpenStreetMap Team hosted by OpenStreetMap France',
        maxZoom: 19
    }).addTo(leafletMap);

    // Add controls
    L.control.scale({
        imperial: false,
        metric: true
    }).addTo(leafletMap);

    L.control.zoom({
        position: 'topright'
    }).addTo(leafletMap);

    return leafletMap;
}

// Get the Leaflet map instance
function getLeafletMap() {
    return leafletMap;
}

// Remove Leaflet map
function removeLeafletMap() {
    if (leafletMap) {
        leafletMap.remove();
        leafletMap = null;
    }
}
