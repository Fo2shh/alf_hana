// Driver app implementation

let locationWatchId = null;
let locationSendInterval = null;
let latestLocation = null;
let lastLocationSentAt = 0;
let map;
let driverMarker = null;
let customerMarkers = {};
let routeLayers = [];
let currentMapProvider = localStorage.getItem('driverMapProvider') || 'leaflet';
const mapboxAccessToken = typeof mapbox_access_token !== 'undefined' ? mapbox_access_token : '';
let ordersData = [];

// Request location permission
function requestLocationPermission() {
    if ('geolocation' in navigator) {
        if (locationWatchId !== null) return;

        locationWatchId = navigator.geolocation.watchPosition(position => {
            latestLocation = {
                latitude: position.coords.latitude,
                longitude: position.coords.longitude,
                accuracy: position.coords.accuracy
            };
            document.getElementById('trackingStatus').className = 'badge bg-success';
            document.getElementById('trackingStatus').textContent = 'نشط';
            sendLocation();
            updateDriverMarker();
        }, handleLocationError, {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 10000
            });
    } else {
        document.getElementById('trackingStatus').className = 'badge bg-danger';
        document.getElementById('trackingStatus').textContent = 'المتصفح لا يدعم الموقع';
    }
}

// Send location to server
async function sendLocation() {
    if (!latestLocation || Date.now() - lastLocationSentAt < 15000) return;
    lastLocationSentAt = Date.now();

    fetch('/api/driver-location/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(latestLocation)
    })
    .then(async response => {
        const result = await response.json();
        if (response.ok && result.status === 'success') {
            document.getElementById('trackingStatus').className = 'badge bg-success';
            document.getElementById('trackingStatus').textContent = 'الموقع ظاهر على الخريطة';
            const [time, meridiem] = new Date().toLocaleTimeString('en-US', {
                hour: 'numeric',
                minute: '2-digit',
                hour12: true
            }).trim().split(/\s+/);
            const updateTime = `${time} ${meridiem}`;
            document.getElementById('lastUpdate').textContent = updateTime;
        } else {
            throw new Error(`تعذر تحديث الموقع: ${response.status}`);
        }
    })
    .catch(error => {
        console.error('فشل إرسال موقع المندوب:', error);
        document.getElementById('trackingStatus').className = 'badge bg-danger';
        document.getElementById('trackingStatus').textContent = 'تعذر إرسال الموقع';
    });
}

// Handle location errors
function handleLocationError(error) {
    console.error('خطأ في تحديد الموقع:', error);
    document.getElementById('trackingStatus').className = 'badge bg-danger';
    document.getElementById('trackingStatus').textContent = error.code === 1
        ? 'اسمح بالوصول إلى الموقع'
        : 'تعذر تحديد الموقع';
}

// Start tracking
function startTracking() {
    requestLocationPermission();
    if (locationSendInterval === null) {
        locationSendInterval = setInterval(sendLocation, 15000);
    }
}

// Update order status
async function updateOrderStatus(button) {
    button.disabled = true;
    const form = new FormData();
    form.append('status', button.dataset.status);
    form.append('csrfmiddlewaretoken', getCookie('csrftoken'));

    try {
        const response = await fetch(button.dataset.url, {
            method: 'POST',
            body: form
        });
        const result = await response.json();
        if (!response.ok || result.status !== 'success') {
            throw new Error('تعذر تحديث حالة الطلب');
        }
        location.reload();
    } catch (error) {
        alert(error.message);
        button.disabled = false;
    }
}

// Switch map provider
function switchMapProvider(provider) {
    if (currentMapProvider === provider) return;

    currentMapProvider = provider;
    localStorage.setItem('driverMapProvider', provider);

    document.getElementById('leafletBtn').classList.toggle('active', provider === 'leaflet');
    document.getElementById('osrmBtn').classList.toggle('active', provider === 'osrm');
    document.getElementById('mapboxBtn').classList.toggle('active', provider === 'mapbox');

    if (map) {
        // Clear old markers
        if (currentMapProvider === 'leaflet' || currentMapProvider === 'osrm') {
            if (driverMarker) {
                map.removeLayer(driverMarker);
                driverMarker = null;
            }
            Object.values(customerMarkers).forEach(marker => {
                map.removeLayer(marker);
            });
            customerMarkers = {};
            routeLayers.forEach(layer => map.removeLayer(layer));
            routeLayers = [];
        } else {
            clearMapboxMarkers();
        }

        map.remove();
        initMap();
        updateDriverMarker();
        addCustomerMarkers();
        updateAllDistanceTimes();
    }
}

// Initialize map
function initMap() {
    document.getElementById('leafletBtn').classList.toggle('active', currentMapProvider === 'leaflet');
    document.getElementById('osrmBtn').classList.toggle('active', currentMapProvider === 'osrm');
    document.getElementById('mapboxBtn').classList.toggle('active', currentMapProvider === 'mapbox');

    if (currentMapProvider === 'leaflet' || currentMapProvider === 'osrm') {
        map = initLeafletMap('driverMap');
    } else {
        map = initMapboxMap('driverMap', mapboxAccessToken);
    }
}

// Update driver marker
function updateDriverMarker() {
    if (!latestLocation || !map) {
        console.log('Cannot update driver marker - no location or map');
        return;
    }

    console.log('Updating driver marker at:', latestLocation.latitude, latestLocation.longitude);

    if (currentMapProvider === 'leaflet' || currentMapProvider === 'osrm') {
        if (driverMarker) {
            driverMarker.setLatLng([latestLocation.latitude, latestLocation.longitude]);
            console.log('Driver marker updated');
        } else {
            const driverIcon = L.divIcon({
                className: 'driver-marker',
                html: '<span class="driver-triangle"></span>',
                iconSize: [24, 24],
                iconAnchor: [12, 0],
                popupAnchor: [0, -4]
            });
            driverMarker = L.marker([latestLocation.latitude, latestLocation.longitude], { icon: driverIcon })
                .bindPopup('<b>موقعك الحالي</b>')
                .addTo(map);
            map.setView([latestLocation.latitude, latestLocation.longitude], 15);
            console.log('Driver marker created');
        }
    } else {
        // Mapbox implementation
        if (map.loaded()) {
            if (map.getSource('driver')) {
                map.getSource('driver').setData({
                    type: 'Feature',
                    geometry: {
                        type: 'Point',
                        coordinates: [latestLocation.longitude, latestLocation.latitude]
                    }
                });
            } else {
                map.addSource('driver', {
                    type: 'geojson',
                    data: {
                        type: 'Feature',
                        geometry: {
                            type: 'Point',
                            coordinates: [latestLocation.longitude, latestLocation.latitude]
                        }
                    }
                });

                map.addLayer({
                    id: 'driver-marker',
                    type: 'symbol',
                    source: 'driver',
                    layout: {
                        'text-field': '▲',
                        'text-size': 24,
                        'text-rotate': 0,
                        'text-anchor': 'bottom',
                        'text-offset': [0, 0]
                    },
                    paint: {
                        'text-color': '#193b36',
                        'text-halo-color': '#ffffff',
                        'text-halo-width': 2
                    }
                });
            }
            map.flyTo({ center: [latestLocation.longitude, latestLocation.latitude], zoom: 15 });
        } else {
            map.on('load', () => {
                updateDriverMarker();
            });
        }
    }

    updateDistanceTimes();

    if (currentMapProvider === 'osrm') {
        console.log('Triggering OSRM distance update from driver marker');
        updateOSRMDistances();
    }
}

// Update distances and times
function updateDistanceTimes() {
    const ordersElements = document.querySelectorAll('.driver-order');

    ordersElements.forEach(orderEl => {
        const orderId = parseInt(orderEl.dataset.orderId);
        const order = ordersData.find(o => o.pk === orderId);

        if (order && order.customer && order.customer.latitude && order.customer.longitude) {
            const navInfo = orderEl.querySelector('.order-navigation-info');
            let distanceTimeDiv = navInfo.querySelector('.distance-time-info');

            if (distanceTimeDiv) {
                distanceTimeDiv.remove();
            }

            const distance = calculateDistance(
                latestLocation.latitude,
                latestLocation.longitude,
                order.customer.latitude,
                order.customer.longitude
            );
            const time = estimateTime(distance);

            distanceTimeDiv = document.createElement('div');
            distanceTimeDiv.className = 'distance-time-info';
            distanceTimeDiv.innerHTML = `
                <div class="distance-time-item">
                    <i class="bi bi-signpost-2"></i>
                    <span>${formatDistance(distance)}</span>
                </div>
                <div class="distance-time-item">
                    <i class="bi bi-clock"></i>
                    <span>${time}</span>
                </div>
            `;
            navInfo.appendChild(distanceTimeDiv);
        }
    });
}

// Update all distances when switching providers
function updateAllDistanceTimes() {
    const ordersElements = document.querySelectorAll('.driver-order');

    ordersElements.forEach(orderEl => {
        const orderId = parseInt(orderEl.dataset.orderId);
        const order = ordersData.find(o => o.pk === orderId);

        if (order && order.customer && order.customer.latitude && order.customer.longitude && latestLocation) {
            const navInfo = orderEl.querySelector('.order-navigation-info');
            let distanceTimeDiv = navInfo.querySelector('.distance-time-info');

            if (distanceTimeDiv) {
                distanceTimeDiv.remove();
            }

            const distance = calculateDistance(
                latestLocation.latitude,
                latestLocation.longitude,
                order.customer.latitude,
                order.customer.longitude
            );
            const time = estimateTime(distance);

            distanceTimeDiv = document.createElement('div');
            distanceTimeDiv.className = 'distance-time-info';
            distanceTimeDiv.innerHTML = `
                <div class="distance-time-item">
                    <i class="bi bi-signpost-2"></i>
                    <span>${formatDistance(distance)}</span>
                </div>
                <div class="distance-time-item">
                    <i class="bi bi-clock"></i>
                    <span>${time}</span>
                </div>
            `;
            navInfo.appendChild(distanceTimeDiv);
        }
    });
}

// Update OSRM distances
async function updateOSRMDistances() {
    if (currentMapProvider !== 'osrm') {
        console.log('Skipping OSRM update - not OSRM provider');
        return;
    }

    console.log('Updating OSRM distances...');
    const ordersElements = document.querySelectorAll('.driver-order');

    const driverLat = latestLocation ? latestLocation.latitude : 31.2001;
    const driverLng = latestLocation ? latestLocation.longitude : 29.9187;

    console.log('Driver location:', driverLat, driverLng);

    for (const orderEl of ordersElements) {
        const orderId = parseInt(orderEl.dataset.orderId);
        const order = ordersData.find(o => o.pk === orderId);

        if (order && order.customer && order.customer.latitude && order.customer.longitude) {
            const navInfo = orderEl.querySelector('.order-navigation-info');
            let distanceTimeDiv = navInfo.querySelector('.distance-time-info');

            if (distanceTimeDiv) {
                distanceTimeDiv.remove();
            }

            const routeData = await fetchOSRMRoute(
                driverLat,
                driverLng,
                order.customer.latitude,
                order.customer.longitude
            );

            if (routeData) {
                drawOSRMRoute(routeData, map);

                distanceTimeDiv = document.createElement('div');
                distanceTimeDiv.className = 'distance-time-info';
                distanceTimeDiv.innerHTML = `
                    <div class="distance-time-item">
                        <i class="bi bi-signpost-2"></i>
                        <span>${formatDistance(routeData.distance)}</span>
                    </div>
                    <div class="distance-time-item">
                        <i class="bi bi-clock"></i>
                        <span>${Math.round(routeData.duration)} دقيقة</span>
                    </div>
                `;
                navInfo.appendChild(distanceTimeDiv);
            } else {
                const distance = calculateDistance(
                    driverLat,
                    driverLng,
                    order.customer.latitude,
                    order.customer.longitude
                );
                const time = estimateTime(distance);

                distanceTimeDiv = document.createElement('div');
                distanceTimeDiv.className = 'distance-time-info';
                distanceTimeDiv.innerHTML = `
                    <div class="distance-time-item">
                        <i class="bi bi-signpost-2"></i>
                        <span>${formatDistance(distance)}</span>
                    </div>
                    <div class="distance-time-item">
                        <i class="bi bi-clock"></i>
                        <span>${time}</span>
                    </div>
                `;
                navInfo.appendChild(distanceTimeDiv);
            }
        }
    }
}

// Add customer markers
function addCustomerMarkers() {
    console.log('Adding customer markers...');
    const ordersElements = document.querySelectorAll('.driver-order');
    console.log('Orders found:', ordersElements.length);

    ordersElements.forEach(orderEl => {
        const orderId = parseInt(orderEl.dataset.orderId);
        const order = ordersData.find(o => o.pk === orderId);

        const navInfo = orderEl.querySelector('.order-navigation-info');

        if (order && order.customer) {
            const customerLat = order.customer.latitude;
            const customerLng = order.customer.longitude;
            const customerName = order.customer.name;
            const customerAddress = order.customer.address;
            const googleMapsLink = order.customer.google_maps_link;

            console.log('Processing order:', orderId, 'Customer has coords:', !!customerLat, !!customerLng);

            if (customerLat && customerLng) {
                if (currentMapProvider === 'leaflet' || currentMapProvider === 'osrm') {
                    const customerIcon = L.divIcon({
                        className: 'customer-marker',
                        html: '<span class="customer-circle"></span>',
                        iconSize: [16, 16],
                        iconAnchor: [8, 8]
                    });

                    const marker = L.marker([customerLat, customerLng], { icon: customerIcon })
                        .bindPopup(`<b>${customerName}</b><br>${customerAddress}`)
                        .addTo(map);

                    customerMarkers[orderId] = marker;
                    console.log('Customer marker added for order:', orderId);

                    if (latestLocation) {
                        if (currentMapProvider === 'osrm') {
                            console.log('Will use OSRM for distance');
                        } else {
                            const distance = calculateDistance(
                                latestLocation.latitude,
                                latestLocation.longitude,
                                customerLat,
                                customerLng
                            );
                            const time = estimateTime(distance);

                            const distanceTimeDiv = document.createElement('div');
                            distanceTimeDiv.className = 'distance-time-info';
                            distanceTimeDiv.innerHTML = `
                                <div class="distance-time-item">
                                    <i class="bi bi-signpost-2"></i>
                                    <span>${formatDistance(distance)}</span>
                                </div>
                                <div class="distance-time-item">
                                    <i class="bi bi-clock"></i>
                                    <span>${time}</span>
                                </div>
                            `;
                            navInfo.appendChild(distanceTimeDiv);
                        }
                    }

                    const navBtn = document.createElement('a');
                    navBtn.className = 'btn btn-outline-primary nav-btn';
                    navBtn.href = `https://www.google.com/maps/dir/?api=1&destination=${customerLat},${customerLng}`;
                    navBtn.target = '_blank';
                    navBtn.innerHTML = '<i class="bi bi-navigation"></i> التنقل للعميل';
                    navInfo.appendChild(navBtn);
                } else {
                    if (map.loaded()) {
                        addMapboxCustomerMarker(orderId, customerLat, customerLng, customerName, customerAddress, orderEl);
                    } else {
                        map.on('load', () => {
                            addMapboxCustomerMarker(orderId, customerLat, customerLng, customerName, customerAddress, orderEl);
                        });
                    }
                }
            } else if (googleMapsLink) {
                const navBtn = document.createElement('a');
                navBtn.className = 'btn btn-outline-primary nav-btn';
                navBtn.href = googleMapsLink;
                navBtn.target = '_blank';
                navBtn.innerHTML = '<i class="bi bi-navigation"></i> فتح موقع العميل';
                navInfo.appendChild(navBtn);
            } else {
                const navBtn = document.createElement('a');
                navBtn.className = 'btn btn-outline-primary nav-btn';
                navBtn.href = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(customerAddress)}`;
                navBtn.target = '_blank';
                navBtn.innerHTML = '<i class="bi bi-navigation"></i> البحث عن العميل على الخريطة';
                navInfo.appendChild(navBtn);
            }
        }
    });

    if (currentMapProvider === 'osrm') {
        console.log('Triggering OSRM distance update');
        updateOSRMDistances();
    }
}

// Add Mapbox customer marker
function addMapboxCustomerMarker(orderId, lat, lng, name, address, orderEl) {
    const sourceId = `customer-${orderId}`;

    if (!map.getSource(sourceId)) {
        map.addSource(sourceId, {
            type: 'geojson',
            data: {
                type: 'Feature',
                geometry: {
                    type: 'Point',
                    coordinates: [lng, lat]
                },
                properties: {
                    name: name,
                    address: address
                }
            }
        });

        map.addLayer({
            id: `customer-marker-${orderId}`,
            type: 'circle',
            source: sourceId,
            paint: {
                'circle-radius': 8,
                'circle-color': '#bd503b',
                'circle-stroke-width': 2,
                'circle-stroke-color': '#ffffff'
            }
        });

        map.addLayer({
            id: `customer-label-${orderId}`,
            type: 'symbol',
            source: sourceId,
            layout: {
                'text-field': ['get', 'name'],
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

    const navInfo = orderEl.querySelector('.order-navigation-info');

    if (latestLocation) {
        const distance = calculateDistance(
            latestLocation.latitude,
            latestLocation.longitude,
            lat,
            lng
        );
        const time = estimateTime(distance);

        const distanceTimeDiv = document.createElement('div');
        distanceTimeDiv.className = 'distance-time-info';
        distanceTimeDiv.innerHTML = `
            <div class="distance-time-item">
                <i class="bi bi-signpost-2"></i>
                <span>${formatDistance(distance)}</span>
            </div>
            <div class="distance-time-item">
                <i class="bi bi-clock"></i>
                <span>${time}</span>
            </div>
        `;
        navInfo.appendChild(distanceTimeDiv);
    }

    const navBtn = document.createElement('a');
    navBtn.className = 'btn btn-outline-primary nav-btn';
    navBtn.href = `https://www.google.com/maps/dir/?api=1&destination=${lat},${lng}`;
    navBtn.target = '_blank';
    navBtn.innerHTML = '<i class="bi bi-navigation"></i> التنقل للعميل';
    navInfo.appendChild(navBtn);
}

// Clear Mapbox markers
function clearMapboxMarkers() {
    if (!map || !map.getStyle()) return;

    const layersToRemove = [];
    const sourcesToRemove = [];

    map.getStyle().layers.forEach(layer => {
        if (layer.id.startsWith('customer-') || layer.id.startsWith('driver-')) {
            layersToRemove.push(layer.id);
        }
    });

    layersToRemove.forEach(layerId => {
        if (map.getLayer(layerId)) {
            map.removeLayer(layerId);
        }
    });

    Object.keys(map.getStyle().sources).forEach(sourceId => {
        if (sourceId.startsWith('customer-') || sourceId === 'driver') {
            sourcesToRemove.push(sourceId);
        }
    });

    sourcesToRemove.forEach(sourceId => {
        if (map.getSource(sourceId)) {
            map.removeSource(sourceId);
        }
    });
}

// Focus on customer
function focusOnCustomer(orderId) {
    const order = ordersData.find(o => o.pk === orderId);
    if (order && order.customer && order.customer.latitude && order.customer.longitude) {
        const customerLat = order.customer.latitude;
        const customerLng = order.customer.longitude;

        console.log('Focusing on customer:', orderId, 'at', customerLat, customerLng);

        if (currentMapProvider === 'leaflet' || currentMapProvider === 'osrm') {
            map.setView([customerLat, customerLng], 16);

            if (currentMapProvider === 'osrm') {
                routeLayers.forEach(layer => map.removeLayer(layer));
                routeLayers = [];

                const driverLat = latestLocation ? latestLocation.latitude : 31.2001;
                const driverLng = latestLocation ? latestLocation.longitude : 29.9187;

                fetchOSRMRoute(
                    driverLat,
                    driverLng,
                    customerLat,
                    customerLng
                ).then(routeData => {
                    if (routeData) {
                        drawOSRMRoute(routeData, map);
                    }
                });
            }
        }
    }
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    const ordersDataElement = document.getElementById('ordersData');
    if (ordersDataElement && ordersDataElement.textContent) {
        try {
            ordersData = JSON.parse(ordersDataElement.textContent);
            console.log('Orders data loaded:', ordersData.length, 'orders');
        } catch (e) {
            console.error('Error parsing orders data:', e);
            ordersData = [];
        }
    }

    startTracking();
    initMap();

    if (currentMapProvider === 'leaflet' || currentMapProvider === 'osrm') {
        setTimeout(() => {
            console.log('Adding customer markers after delay...');
            addCustomerMarkers();
        }, 500);
    } else {
        map.on('load', () => {
            setTimeout(() => {
                console.log('Adding customer markers after map load...');
                addCustomerMarkers();
            }, 500);
        });
    }
});

window.addEventListener('online', sendLocation);
