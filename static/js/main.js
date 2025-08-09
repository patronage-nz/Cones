// Pull the path, origin & current
const path = window.CONE_PATH || [];
const origin = path.length ? path[0] : null;
const current = path.length ? path[path.length - 1] : null;

// TAKE ME HOME --> Google Maps directions
const homeBtn = document.getElementById('take-me-home');
if (homeBtn && origin) {
    homeBtn.addEventListener('click', () => {
        // Destructure with aliases:
        const { lat: olat, long: olong } = origin;
        if (!olat || !olong) {
            return alert('Origin coordinates missing.');
        }

        let url;
        if (current) {
            // Destructure current as well
            const { lat: clat, long: clong } = current;
            if (!clat || !clong) {
                // Fallback to origin-only if somehow missing
                url = `https://www.google.com/maps/dir//${olat},${olong}`;
            } else {
                // Directions *from* last known scan *to* origin
                url = `https://www.google.com/maps/dir/${clat},${clong}/${olat},${olong}`;
            }
        } else {
            // No current point, so just origin
            url = `https://www.google.com/maps/dir//${olat},${olong}`;
        }

        // Open in new tab
        window.open(url, '_blank').focus();
    });
}


document.getElementById('update-location').addEventListener('click', () => {
    const UPDATE_URL = window.UPDATE_URL;
    if (!navigator.geolocation) {
        return alert('Geolocation not supported.');
    }
    navigator.geolocation.getCurrentPosition(pos => {
        const payload = {
            lat: pos.coords.latitude,
            long: pos.coords.longitude,
            timestamp: pos.timestamp
        };

        fetch(UPDATE_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
            .then(r => {
                if (!r.ok) return r.json().then(j => Promise.reject(j.error));
                return r.json();
            })
            .then(() => alert('Location updated!'))
            .catch(err => alert(`Update failed for cone ${window.CONE_ID} (${err})`));
    }, () => alert('Unable to fetch your location. Check your location privacy settings.'));
});

