from flask import Flask, render_template, abort, request, redirect, jsonify
from repository import Repository
from datetime import datetime
import json 

APP = Flask(__name__)
CONFIG_PATH: str = "config.json"
CONFIG_DATA = None
with open(CONFIG_PATH, 'r') as configf:
    CONFIG_DATA = json.load(configf)

if CONFIG_DATA["test_switch"]:
    print("IN TEST")
    cone_data_dir: str = CONFIG_DATA["test_cone_data_dir"]
else:
    print("IN PROD")
    cone_data_dir: str = CONFIG_DATA["prod_cone_data_dir"]

REPO = Repository(
    cone_data_dir = cone_data_dir,
    update_time_limit_minutes = CONFIG_DATA["update_time_limit_minutes"],
    cone_data_delimiter = CONFIG_DATA["cone_data_delimiter"],
    mailing_list_loc = CONFIG_DATA["mailing_list_loc"],
    mailing_list_time_limit_minutes = CONFIG_DATA["mailing_list_time_limit_minutes"]
)


@APP.route('/')
def index():
    # fetch cones and prepare a JS-friendly list for the index map
    raw_cones = REPO.list_cones()  # each has id, last_update (float|None), last_lat, last_long

    cones_for_map = []
    for c in raw_cones:
        last_ts = c.get("last_update")
        if last_ts:
            last_str = datetime.fromtimestamp(last_ts).strftime("%Y-%m-%d %H:%M:%S")
        else:
            last_str = "Never"
        cones_for_map.append({
            "id": c["id"],
            "display_id": c["id"] + 1,
            "last_update_ts": last_ts,
            "last_update": last_str,
            "lat": c.get("last_lat"),
            "long": c.get("last_long")
        })
    return render_template('index.html', finish_time=CONFIG_DATA["finish_time"], cones_for_map=cones_for_map)

 

@APP.route('/cones')
def cones_base():
    cones = REPO.list_cones()
    cones_display = []
    for c in cones:
        last_ts = c.get("last_update")
        if last_ts:
            # Format as e.g. 2025-08-09 14:32:01
            last_str = datetime.fromtimestamp(last_ts).strftime("%Y-%m-%d %H:%M:%S")
        else:
            last_str = "Never"
        cones_display.append({
            "id": c["id"],
            "display_id": c["id"] + 1,   # user-facing 1-indexed
            "last_update": last_str
        })
    return render_template('cones.html', cones=cones_display)


@APP.route('/cones/<int:cone_id>')
def show_cone(cone_id):
    data = REPO.load_cone(cone_id)
    if not data:
        abort(404)
    return render_template('cone.html', cone=data, cone_id = cone_id)


@APP.route('/subscribe', methods = ['POST'])
def subscribe():
    email = request.form.get('email') 
    client_ip = request.remote_addr
    result: bool = REPO.add_to_mailing_list(email, client_ip)
    return redirect('/')


@APP.route('/cones/<int:cone_id>/update', methods=['POST'])
def update_cone(cone_id):
    print(f"UPDATING: {cone_id}")
    data = request.get_json() or {}
    lat = data.get('lat')
    long = data.get('long')
    client_ip = request.remote_addr

    ok = REPO.update_cone(cone_id, lat, long, client_ip)
    if not ok:
        return jsonify({"error": "Too many updates from this IP recently"}), 429
    return jsonify({"success": True}), 200


@APP.route('/_health')
def health():
    return 'ok', 200


if __name__ == '__main__':
    APP.run(debug=bool(CONFIG_DATA.get("test_switch", False)))
