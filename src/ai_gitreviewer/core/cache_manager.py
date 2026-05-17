import json
import hashlib
import os

class CacheManager:
    def __init__(self, cache_file=".reviewer_cache.json"):
        self.cache_file = cache_file
        self.cache = self._load_cache()

    def _load_cache(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def get_file_hash(self, content):
        """Generates a unique fingerprint for the file content."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def is_changed(self, filepath, content):
        """Returns True if the file has been modified since the last scan."""
        current_hash = self.get_file_hash(content)
        return self.cache.get(filepath) != current_hash

    def update(self, filepath, content):
        """Saves the new hash to the cache file."""
        self.cache[filepath] = self.get_file_hash(content)
        with open(self.cache_file, "w") as f:
            json.dump(self.cache, f, indent=4)