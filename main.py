import io
import json
import logging
from pathlib import Path
import pandas as pd
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from src import DatasetInfo, DatasetStorage, HealthResponse, setup_logging

setup_logging(verbose=True)
logger = logging.getLogger(__name__)

app = FastAPI(title="Data Processing API", version="1.0.0")
storage = DatasetStorage()

@app.get("/health", response_model=HealthResponse)
def health_check():
    """Return the application status and version."""
    return HealthResponse(status="ok", version="1.0.0")

@app.post("/upload", response_model=DatasetInfo)
async def upload_dataset(file: UploadFile = File(...)):
    """Read and store a CSV upload."""
    filename = file.filename or ""
    suffix = Path(filename).suffix.lower()
    if suffix != ".csv":
        logger.warning(f"Unsupported file format: {suffix}")
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{suffix}'. Please upload a .csv file.",
        )

    contents = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(contents))
    except pd.errors.EmptyDataError:
        logger.warning(f"Empty CSV upload: {filename}")
        raise HTTPException(status_code=400, detail="The CSV file is empty.")
    except pd.errors.ParserError as e:
        logger.warning(f"CSV parse error in {filename}: {e}")
        raise HTTPException(status_code=400, detail=f"Could not parse CSV: {e}")
    except UnicodeDecodeError:
        logger.warning(f"Encoding error in {filename}")
        raise HTTPException(
            status_code=400, detail="The file could not be decoded."
        )
    dataset_id = storage.save(df, filename)
    logger.info(f"Uploaded dataset: id={dataset_id}, filename={filename}, rows={len(df)}")
    return storage.get_metadata(dataset_id)
    

@app.get("/datasets/{dataset_id}")
def get_dataset(dataset_id: int, limit: int = Query(default=100, ge=1)):
    """Return up to limit rows from a stored dataset."""
    item = storage.get(dataset_id)
    if item is None:
        logger.warning(f"Dataset id not found: {dataset_id}")
        raise HTTPException(status_code=404, detail="Dataset not found")
    records = json.loads(item.head(limit).to_json(orient="records"))
    logger.info(f"Returned dataset: id={dataset_id}, rows={len(records)}")
    return {"id": dataset_id, "data": records, "total_rows": len(item)}