// static/js/index_map.js
(function () {
  if (!window.INDEX_CONES || !Array.isArray(window.INDEX_CONES)) return;

  // Use only cones with at least a last coordinate
  const cones = window.INDEX_CONES.filter(c => c && c.last_lat !== null && c.last_long !== null);

  const mapEl = document.getElementById('index-map');
  if (!mapEl) return;

  if (cones.length === 0) {
    mapEl.innerHTML = '<div style="padding:1rem; text-align:center; color:#555;">No cone locations available yet.</div>';
    return;
  }

  const first = cones[0];
  const map = L.map('index-map').setView([ first.last_lat, first.last_long ], 12);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);

  const coneIcon = L.icon({
    iconUrl: '/static/images/traffic_cone.png',
    iconSize: [28, 28], // width, height (px)
    iconAnchor: [14, 28],
    popupAnchor: [0, -28]
  });

  const markers = [];
  const polylines = [];
  const allLatLngs = [];

  cones.forEach(c => {
    const lastLat = parseFloat(c.last_lat);
    const lastLon = parseFloat(c.last_long);
    const firstLat = c.first_lat != null ? parseFloat(c.first_lat) : null;
    const firstLon = c.first_long != null ? parseFloat(c.first_long) : null;

    if (!Number.isFinite(lastLat) || !Number.isFinite(lastLon)) return;

    if (Number.isFinite(firstLat) && Number.isFinite(firstLon)) {
      const latlngs = [[firstLat, firstLon], [lastLat, lastLon]];

      // Draw the trail line (style similar to single-cone map)
      // const poly = L.polyline(latlngs, { weight: 4, opacity: 0.7 }).addTo(map);
      // polylines.push(poly);

      L.circleMarker([firstLat, firstLon], {
        radius: 3,
        color: 'red',
        fillColor: 'red',
        fillOpacity: 1
      }).bindPopup(`Cone ${c.display_id} - Origin`).addTo(map);

      allLatLngs.push([firstLat, firstLon]);
      allLatLngs.push([lastLat, lastLon]);
    } else {
      allLatLngs.push([lastLat, lastLon]);
    }

    const marker = L.marker([lastLat, lastLon], { icon: coneIcon }).addTo(map);

    const popupHtml = `
      <div style="font-weight:700; margin-bottom:4px;">Cone ${c.display_id}</div>
      <div style="font-size:0.9rem; color:#555;">Last update: ${c.last_update}</div>
      <div style="margin-top:6px;">
        <a href="/cones/${c.id}" style="color:#111; text-decoration:none; font-weight:600;">View cone</a>
      </div>
    `;
    marker.bindPopup(popupHtml);

    marker.on('click', function () {
      window.location.href = `/cones/${c.id}`;
    });

    markers.push(marker);
  });

  if (allLatLngs.length > 0) {
    try {
      const bounds = L.latLngBounds(allLatLngs);
      map.fitBounds(bounds.pad(0.15));
    } catch (err) {
      console.warn('Failed to fit bounds for index map', err);
    }
  }
})();
