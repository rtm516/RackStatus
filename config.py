import json

CONFIG_FILE = 'config.json'

class Config:
    def __init__(self):
        self._filename = CONFIG_FILE
        self._data = {
			'ssid': '',
			'password': '',
			'rackUnits': 12,
			'ledPerUnit': 3,
			'ledPin': 1,
			'refreshTime': 10
		}
        self._load()

    def _load(self):
        try:
            with open(self._filename, 'r') as f:
                self._data.update(json.load(f))
        except (Exception):
            pass
        
        self._save()

    def _save(self):
        with open(self._filename, 'w') as f:
            json.dump(self._data, f)

    def __getattr__(self, name):
        return self._data.get(name)

    def __setattr__(self, name, value):
        if name in ("_filename", "_data"):
            object.__setattr__(self, name, value)
        else:
            self._data[name] = value
            self._save()
