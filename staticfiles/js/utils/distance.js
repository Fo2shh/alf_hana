// Utility functions for distance and time calculations

// Calculate distance using Haversine formula
function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // Earth's radius in km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
}

// Format distance for display
function formatDistance(km) {
    if (km < 1) {
        return Math.round(km * 1000) + ' م';
    }
    return km.toFixed(1) + ' كم';
}

// Estimate travel time
function estimateTime(km) {
    // Assume average speed of 30 km/h in the city
    const avgSpeed = 30;
    const hours = km / avgSpeed;
    const minutes = Math.round(hours * 60);
    if (minutes < 60) {
        return minutes + ' دقيقة';
    }
    const h = Math.floor(minutes / 60);
    const m = minutes % 60;
    return h + ' ساعة ' + m + ' دقيقة';
}

// Fetch route from OSRM API
async function fetchOSRMRoute(startLat, startLng, endLat, endLng) {
    try {
        const url = `https://router.project-osrm.org/route/v1/driving/${startLng},${startLat};${endLng},${endLat}?overview=full&geometries=geojson`;
        console.log('Fetching OSRM route:', url);
        const response = await fetch(url);
        const data = await response.json();
        console.log('OSRM response:', data);

        if (data.code === 'Ok' && data.routes && data.routes.length > 0) {
            const route = data.routes[0];
            return {
                geometry: route.geometry,
                distance: route.distance / 1000, // Convert to km
                duration: route.duration / 60 // Convert to minutes
            };
        }
        console.warn('OSRM no route found');
        return null;
    } catch (error) {
        console.error('Error fetching OSRM route:', error);
        return null;
    }
}
