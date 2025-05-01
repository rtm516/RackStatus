import json

CONFIG_FILE = 'config.json'

class Config:
    def __init__(self, filename):
        self._filename = filename
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
                self._data = self._data | json.load(f)
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

# Create an instance and expose its attributes directly at the module level
_config = Config(CONFIG_FILE)

# Set the module’s __getattr__ and __setattr__ to delegate to the instance
def __getattr__(name):
    return getattr(_config, name)

def __setattr__(name, value):
    setattr(_config, name, value)
