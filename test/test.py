import json
import os
import time


class Repository:
    def __init__(self, cone_data_dir: str, update_time_limit_minutes: int, cone_data_delimiter: str, mailing_list_loc: str) -> None:
        self._cone_data_dir: str = cone_data_dir
        self._update_time_limit_minutes = update_time_limit_minutes
        self._cone_data_delimiter: str = cone_data_delimiter
        self._mailing_list_loc: str = mailing_list_loc
    

    def _newline_check(self, cone_id) -> None:
        cur_path: str = f"{self._cone_data_dir}/{cone_id}"
        content: str = ""
        with open(cur_path, 'r') as checkf:
            content = checkf.read()
            if content.endswith('\n'):
                return
        with open(cur_path, 'w') as writef:
            writef.write(content + '\n')


    def load_cone(self, cone_id: str | int = 0):
        if not type(cone_id) == str:
            cone_id = str(cone_id)
        cur_path: str = os.path.join(self._cone_data_dir, cone_id)
        lines = []
        all_data = []
        try:
            with open(cur_path, 'r') as curf:
                lines = [line.strip() for line in curf.readlines()]
        except FileNotFoundError:
            print(f"[ERROR] Failed to load cone data at directory: {cur_path}. File not found.")
        if len(lines) > 0:
            for data in lines:
                components: list[str] = data.split(self._cone_data_delimiter)
                if not (len(components) == 4):
                    raise ValueError(f"[ERROR] Cone data is missing or including extra values. Data Length: {len(components)} - Expected: 4.")
                else:
                    all_data.append({
                        "lat": components[0],
                        "long": components[1],
                        "ip_address": components[2],
                        "timestamp": components[3]
                    })
        return all_data
    

    def update_cone(self, cone_id: str | int, lat: str, long: str, ip: str) -> bool:
        '''
        Adds new location and IP to the file IF it passes the spam-safety check.
        '''
        update_timestamp = time.time()
        cone_data = self.load_cone(cone_id)

        # newline safety
        self._newline_check(cone_id)

        # Safety: Each IP address can only update the location of a cone once every n minutes
        # we need to check all of the cone data that is older than n minutes and make sure the IP address given is not in any of those
        min_timestamp = update_timestamp - (self._update_time_limit_minutes * 60)
        for update_data in cone_data[1:]:
            if (float(update_data["timestamp"]) > min_timestamp) and (update_data["ip_address"] == ip):
                return False
        
        # if this code is reached then the given ip has not updated that cone in the last n minutes and we can add a new row to the repository
        new_line: str = f"{lat}|{long}|{ip}|{update_timestamp}"
        filepath: str = os.path.join(self._cone_data_dir, str(cone_id))
        with open(filepath, 'a') as updatef:
            updatef.write(f"{new_line}\n") 
        return True
    

    def add_to_mailing_list(self, email: str) -> None:
        '''
        TODO:
        - Add to some sort of mailing list (maybe a csv that can then be exported?)
        - Add a safety check in there so the same IP can't add a million emails and brick the server
        '''
        with open(self._mailing_list_loc, 'a') as mailingf:
            mailingf.write(email)


CONFIG_PATH: str = "config.json"
CONFIG_DATA = None
with open(CONFIG_PATH, 'r') as configf:
    CONFIG_DATA = json.load(configf)
REPO = Repository(
    cone_data_dir = CONFIG_DATA["cone_data_dir"],
    update_time_limit_minutes = CONFIG_DATA["update_time_limit_minutes"],
    cone_data_delimiter = CONFIG_DATA["cone_data_delimiter"],
    mailing_list_loc = CONFIG_DATA["mailing_list_loc"]
)


REPO.update_cone(
    "22",
    "-40.00",
    "-180.00",
    "0.0.0.0"
)