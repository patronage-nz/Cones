// static/js/map.js
(function() {
    if (!window.CONE_PATH || !window.CONE_PATH.length) return;
  
    // 1) Initialize Leaflet map centered on the first point
    const origin = window.CONE_PATH[0];
    const current = window.CONE_PATH[window.CONE_PATH.length - 1];
    const map = L.map('map').setView(
      [ origin.lat, origin.long ],
      13
    );
  
    // 2) Add OSM tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);
  
    // 3) Build LatLng array for the polyline
    const latlngs = window.CONE_PATH.map(pt => [ pt.lat, pt.long ]);
  
    // 4) Draw the “trail” polyline
    L.polyline(latlngs, { weight: 4, opacity: 0.7 }).addTo(map);
  
    // 5) Mark start & end with distinct colors
    // Start: green; End: red
    L.circleMarker([ origin.lat, origin.long ], {
      radius: 6,
      color: 'red',
      fillColor: 'red',
      fillOpacity: 1
    }).bindPopup('Origin').addTo(map);
  
    const coneIcon = L.icon({
      iconUrl: '/static/images/traffic_cone.png',
      iconSize: [24, 24],     
      iconAnchor: [12, 24],   
      popupAnchor: [0, -22]
    });

    L.marker([ current.lat, current.long ], { icon: coneIcon })
      .bindPopup('Current Location')
      .addTo(map);

  
    // 6) Fit map to show whole path
    const bounds = L.latLngBounds(latlngs);
    map.fitBounds(bounds.pad(0.2));
  })();
  