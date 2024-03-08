import os

PIPELINE_NAME: str = "travel_pack"
ARTIFACT_DIR: str = "artifacts"

MONGODB_URL_KEY = "MONGODB_URL"

DATABASE_NAME = "iNeuron"
COLLECTION_NAME = "travel"

# common file name
FILE_NAME: str = "travel.csv"
TRAIN_FILE_NAME: str = "train.csv"
TEST_FILE_NAME: str = "test.csv"

"""
Data Ingestion related constant start with DATA_INGESTION VAR NAME
"""
DATA_INGESTION_COLLECTION_NAME: str = "travel"
DATA_INGESTION_DIR_NAME: str = "data_ingestion"
DATA_INGESTION_FEATURE_STORE_DIR: str = "feature_store"
DATA_INGESTION_INGESTED_DIR: str = "ingested"
DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO: float = 0.2