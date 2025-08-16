import os
import time
import csv


class Repository:
    def __init__(self, cone_data_dir: str, update_time_limit_minutes: int, cone_data_delimiter: str, mailing_list_loc: str, mailing_list_time_limit_minutes: int) -> None:
        self._cone_data_dir: str = cone_data_dir
        self._update_time_limit_minutes = update_time_limit_minutes
        self._cone_data_delimiter: str = cone_data_delimiter
        self._mailing_list_loc: str = mailing_list_loc
        self._mailing_list_time_limit_minutes: int = mailing_list_time_limit_minutes
    

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
    

    def __handle_entry(self, entry) -> dict:
        try:
            update = float(entry.get("timestamp"))
        except (ValueError, TypeError, AttributeError):
            update = None
        # Attempt to parse lat/long as floats
        try:
            lat = float(entry.get("lat"))
        except (TypeError, ValueError):
            lat = None
        try:
            long = float(entry.get("long"))
        except (TypeError, ValueError):
            long = None
        return {"update": update, "lat": lat, "long": long}
        

    def list_cones(self):
        """
        Return a list of cones available in the cone_data_dir.
        Each item is a dict:
          {
            "id": int,
            "last_update": float | None,
            "last_lat": float | None,
            "last_long": float | None
          }
        Files that are not numeric names are ignored.
        """
        cones = []
        try:
            for name in os.listdir(self._cone_data_dir):
                # Only consider files that are numeric (cone IDs)
                if not name.isdigit():
                    continue
                cone_id = int(name)
                data = self.load_cone(cone_id)
                # last update is the timestamp of the last entry, if any
                if data and isinstance(data, list) and len(data) > 0:
                    first_entry_data = self.__handle_entry(data[0])
                    last_entry_data = self.__handle_entry(data[-1])
                cones.append({
                    "id": cone_id,
                    "last_update": last_entry_data["update"],
                    "last_lat": last_entry_data["lat"],
                    "last_long": last_entry_data["long"],
                    "first_lat": first_entry_data["lat"],
                    "first_long": first_entry_data["long"]
                })
        except FileNotFoundError:
            # directory missing — return empty list
            return []
        # sort by id for predictable ordering
        cones.sort(key=lambda x: x["id"])
        return cones


    # def list_cones(self):
    #     """
    #     Return a list of cones available in the cone_data_dir.
    #     Each item is a dict:
    #       {
    #         "id": int,
    #         "last_update": float | None,
    #         "last_lat": float | None,
    #         "last_long": float | None
    #       }
    #     Files that are not numeric names are ignored.
    #     """
    #     cones = []
    #     try:
    #         for name in os.listdir(self._cone_data_dir):
    #             # Only consider files that are numeric (cone IDs)
    #             if not name.isdigit():
    #                 continue
    #             cone_id = int(name)
    #             data = self.load_cone(cone_id)
    #             # last update is the timestamp of the last entry, if any
    #             last_update = None
    #             last_lat = None
    #             last_long = None
    #             if data and isinstance(data, list) and len(data) > 0:
    #                 last_entry = data[-1]
    #                 try:
    #                     last_update = float(last_entry.get("timestamp"))
    #                 except (ValueError, TypeError, AttributeError):
    #                     last_update = None
    #                 # Attempt to parse lat/long as floats
    #                 try:
    #                     last_lat = float(last_entry.get("lat"))
    #                 except (TypeError, ValueError):
    #                     last_lat = None
    #                 try:
    #                     last_long = float(last_entry.get("long"))
    #                 except (TypeError, ValueError):
    #                     last_long = None
    #             cones.append({
    #                 "id": cone_id,
    #                 "last_update": last_update,
    #                 "last_lat": last_lat,
    #                 "last_long": last_long
    #             })
    #     except FileNotFoundError:
    #         # directory missing — return empty list
    #         return []
    #     # sort by id for predictable ordering
    #     cones.sort(key=lambda x: x["id"])
    #     return cones


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
        for update_data in cone_data:
            if (float(update_data["timestamp"]) > min_timestamp) and (update_data["ip_address"] == ip):
                return False
        
        # if this code is reached then the given ip has not updated that cone in the last n minutes and we can add a new row to the repository
        new_line: str = f"{lat}{self._cone_data_delimiter}{long}{self._cone_data_delimiter}{ip}{self._cone_data_delimiter}{update_timestamp}"
        filepath: str = os.path.join(self._cone_data_dir, str(cone_id))
        with open(filepath, 'a') as updatef:
            updatef.write(f"{new_line}\n") 
        return True
    

    def add_to_mailing_list(self, email: str, ip_address: str) -> bool:
        now = time.time()
        recent_threshold = now - self._mailing_list_time_limit_minutes

        # Ensure the CSV exists, if not, create it with header
        file_exists = os.path.isfile(self._mailing_list_loc)
        if not file_exists:
            with open(self._mailing_list_loc, mode='w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['email', 'ip', 'timestamp'])

        # Check for recent requests from this IP
        with open(self._mailing_list_loc, mode='r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    timestamp = float(row['timestamp'])
                except (ValueError, KeyError):
                    continue
                if row.get('ip') == ip_address and timestamp >= recent_threshold:
                    return False

        with open(self._mailing_list_loc, mode='a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([email, ip_address, now])
        return True