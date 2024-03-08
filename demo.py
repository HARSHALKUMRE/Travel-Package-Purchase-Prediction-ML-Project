import sys
from travel_pack.exception import TravelException
from travel_pack.logger import logging
from travel_pack.pipeline.training_pipeline import TrainPipeline

try:
    pipeline = TrainPipeline()
    pipeline.run_pipeline()
except Exception as e:
    raise TravelException(e, sys) from e