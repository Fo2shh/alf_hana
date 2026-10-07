// Base functions shared between all map providers

// Driver colors for distinguishing different drivers
const driverColors = ['#2563eb', '#c2410c', '#15803d', '#9333ea', '#0891b2', '#be123c', '#a16207', '#475569'];

// Get color for a specific driver
function getDriverColor(driverId) {
    return driverColors[(Number(driverId) - 1) % driverColors.length];
}
