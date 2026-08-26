import json
import os


class JSONRepository:

    def __init__(self, file_path):
        self.file_path = file_path
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        directory = os.path.dirname(self.file_path)

        if directory:
            os.makedirs(directory, exist_ok=True)

        if not os.path.exists(self.file_path):
            self._write_data([])

    def _read_data(self):
        try:
            with open(self.file_path, "r") as file:
                return json.load(file)

        except json.JSONDecodeError:
            print(
                f"Warning: {self.file_path} "
                "contains invalid JSON. Resetting file."
            )
            return []

    def _write_data(self, data):
        with open(self.file_path, "w") as file:
            json.dump(data, file, indent=4)

    def get_all(self):
        return self._read_data()

    def save_all(self, data):
        self._write_data(data)

    def add(self, item):
        data = self._read_data()
        data.append(item)
        self._write_data(data)

    def delete(self, key, value):
        data = self._read_data()

        filtered_data = [
            item for item in data
            if item.get(key) != value
        ]

        self._write_data(filtered_data)

    def find_by(self, key, value):
        data = self._read_data()

        for item in data:
            if item.get(key) == value:
                return item

        return None

    def find_all_by(self, key, value):
        data = self._read_data()

        return [item for item in data if item.get(key) == value]

    def update(self, key, value, new_item):
        """Replace the first record where item[key] == value.

        Returns True if a record was found and replaced, False
        otherwise. Centralizing this here removes the need for every
        service to hand-roll a read-modify-write loop.
        """

        data = self._read_data()
        updated = False

        for index, item in enumerate(data):

            if item.get(key) == value:
                data[index] = new_item
                updated = True
                break

        if updated:
            self._write_data(data)

        return updated

    def count(self):
        return len(self._read_data())