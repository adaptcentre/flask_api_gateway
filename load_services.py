import json
from threading import Lock


class ServicesLoaderSingleton:
    _instance = None

    def __new__(cls, json_path=None):
        """Create a single instance of the class."""
        if cls._instance is None:
            cls._instance = super(ServicesLoaderSingleton, cls).__new__(cls)
            cls._instance._initialize(json_path)
        return cls._instance

    def _initialize(self, json_path):
        """Initialize the class with the JSON file."""
        self.json_path = json_path
        print(self.json_path)
        self.data = []
        if self.json_path:
            self._load_json()

    def _load_json(self):
        """Load JSON data from the file."""
        try:
            with open(self.json_path, 'r') as file:
                self.data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading JSON file: {e}")
            self.data = []

    def get_json_as_list(self):
        """Return the loaded JSON data as a list."""
        return self.data
