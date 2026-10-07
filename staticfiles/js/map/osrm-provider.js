// OSRM route provider implementation (works with Leaflet)

let routeLayers = [];

// Draw OSRM route on Leaflet map
function drawOSRMRoute(routeData, map) {
    if (!routeData || !routeData.geometry) {
        console.warn('No route geometry to draw');
        return;
    }

    const routeLayer = L.geoJSON(routeData.geometry, {
        style: {
            color: '#193b36',
            weight: 5,
            opacity: 0.7
        }
    }).addTo(map);

    routeLayers.push(routeLayer);
    console.log('Route drawn successfully');
}

// Clear all route layers
function clearOSRMRoutes(map) {
    routeLayers.forEach(layer => map.removeLayer(layer));
    routeLayers = [];
}
