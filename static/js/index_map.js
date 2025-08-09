// static/js/index_map.js
(function () {
  if (!window.INDEX_CONES || !Array.isArray(window.INDEX_CONES)) return;

  // Filter cones that have coordinates
  const cones = window.INDEX_CONES.filter(c => c && c.lat !== null && c.long !== null);

  // Create map only if we have at least one valid coordinate; otherwise create a small placeholder
  const mapEl = document.getElementById('index-map');
  if (!mapEl) return;

  if (cones.length === 0) {
    // No coordinates - show an informative placeholder
    mapEl.innerHTML = '<div style="padding:1rem; text-align:center; color:#555;">No cone locations available yet.</div>';
    return;
  }

  // Initialize Leaflet map; center will be adjusted to fit markers
  const first = cones[0];
  const map = L.map('index-map').setView([first.lat, first.long], 12);

  // Add OSM tiles
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);

  // Custom cone icon (uses your PNG). Adjust size to taste.
  const coneIcon = L.icon({
    iconUrl: '/static/images/traffic_cone.png',
    iconSize: [28, 28], // width, height (px)
    iconAnchor: [14, 28], // point at which the icon corresponds to marker lat/lng
    popupAnchor: [0, -28]
  });

  // Keep markers so we can fit bounds
  const markers = [];

  cones.forEach(c => {
    const lat = c.lat;
    const lon = c.long;
    if (lat == null || lon == null) return;

    const marker = L.marker([lat, lon], { icon: coneIcon })
      .addTo(map);

    const popupHtml = `
      <div style="font-weight:700; margin-bottom:4px;">Cone ${c.display_id}</div>
      <div style="font-size:0.9rem; color:#555;">Last update: ${c.last_update}</div>
      <div style="margin-top:6px;">
        <a href="/cones/${c.id}" style="color:#111; text-decoration:none; font-weight:600;">View cone</a>
      </div>
    `;
    marker.bindPopup(popupHtml);

    // Click on marker to go to cone page
    marker.on('click', function () {
      // Open popup first, then navigate after short delay for the user to see it
      this.openPopup();
      // navigate immediately (no delay) so UX is consistent
      window.location.href = `/cones/${c.id}`;
    });

    markers.push(marker);
  });

  // Fit map to show all markers nicely
  const group = new L.featureGroup(markers);
  map.fitBounds(group.getBounds().pad(0.15));
})();
