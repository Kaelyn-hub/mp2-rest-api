import logging

logger = logging.getLogger(__name__)


class DatasetStorage:
    def __init__(self):
        self._store = {}
        self._counter = 0

    def save(self, df, filename):
        '''Return the ID of the newly stored dataset.'''
        self._counter += 1
        dataset_id = self._counter
        self._store[dataset_id] = {"filename": filename, "data": df.copy()}
        logger.debug(f"Stored dataset: id={dataset_id}, rows={len(df)}")
        return dataset_id

    def get(self, dataset_id):
        """Return a copy of the stored DataFrame, or None."""
        item = self._store.get(dataset_id)
        if item is None:
            logger.debug(f"Dataset not found: id={dataset_id}")
            return None
        logger.debug(f"Retrieved dataset: id={dataset_id}")
        return item["data"].copy()

    def get_metadata(self, dataset_id):
        """Return the dataset metadata, or None."""
        item = self._store.get(dataset_id)
        if item is None:
            logger.debug(f"Metadata not found: id={dataset_id}")
            return None
        df = item["data"]
        metadata = {
            "id": dataset_id,
            "filename": item["filename"],
            "rows": int(len(df)),
            "columns": int(len(df.columns)),
            "column_names": [str(c) for c in df.columns],
        }
        logger.debug(f"Retrieved metadata: id={dataset_id}")
        return metadata


    def update(self, dataset_id, df):
        """Replace an existing dataset; return True, or False if missing."""
        item = self._store.get(dataset_id)
        if item is None:
            logger.debug(f"Dataset not found for update: id={dataset_id}")
            return False
        self._store[dataset_id]["data"] = df.copy()
        logger.debug(f"Updated dataset: id={dataset_id}")
        return True

    def clear(self):
        """Clear all data and reset the ID counter."""
        self._store.clear()
        self._counter = 0
        logger.debug("Cleared the datasets and reset the id's")