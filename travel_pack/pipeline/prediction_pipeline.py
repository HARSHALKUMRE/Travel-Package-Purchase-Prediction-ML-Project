import os
import sys

import numpy as np
import pandas as pd
from travel_pack.entity.config_entity import TravelPredictorConfig
from travel_pack.entity.s3_estimator import TravelEstimator
from travel_pack.exception import TravelException
from travel_pack.logger import logging
from travel_pack.utils.main_utils import read_yaml_file
from pandas import DataFrame


class TravelData:
    def __init__(self,
                 Age,
                 CityTier,
                 DurationOfPitch,
                 NumberOfPersonVisiting,
                 NumberOfFollowups,
                 PreferredPropertyStar,
                 NumberOfTrips,
                 Passport,
                 PitchSatisfactionScore,
                 OwnCar,
                 NumberOfChildrenVisiting,
                 MonthlyIncome,
                 TypeofContact,
                 Occupation,
                 Gender,
                 ProductPitched,
                 MaritalStatus,
                 Designation,
                 ):
        """
        Travel Data constructor
        Input: all features of the trained model for prediction
        """
        try:
            self.Age = Age
            self.CityTier = CityTier
            self.DurationOfPitch = DurationOfPitch
            self.NumberOfPersonVisiting = NumberOfPersonVisiting
            self.NumberOfFollowups = NumberOfFollowups
            self.PreferredPropertyStar = PreferredPropertyStar
            self.NumberOfTrips = NumberOfTrips
            self.Passport = Passport
            self.PitchSatisfactionScore = PitchSatisfactionScore
            self.OwnCar = OwnCar
            self.NumberOfChildrenVisiting = NumberOfChildrenVisiting
            self.MonthlyIncome = MonthlyIncome
            self.TypeofContact = TypeofContact
            self.Occupation = Occupation
            self.Gender = Gender
            self.ProductPitched = ProductPitched
            self.MaritalStatus = MaritalStatus
            self.Designation = Designation
        except Exception as e:
            raise TravelException(e, sys) from e
        
    def get_travel_input_data_frame(self) -> DataFrame:
        """
        This function returns a DataFrame from TravelData class input
        """
        try:
            
            travel_input_dict = self.get_travel_data_as_dict()
            return DataFrame(travel_input_dict)
        
        except Exception as e:
            raise TravelException(e, sys) from e
        
        
    def get_travel_data_as_dict(self):
        """
        This function returns a dictionary from TravelData class input 
        """
        logging.info("Entered get_travel_data_as_dict method as TravelData class")
        
        try:
            input_data = {
                "Age": [self.Age],
                "CityTier": [self.CityTier],
                "DurationOfPitch": [self.DurationOfPitch],
                "NumberOfPersonVisiting": [self.NumberOfPersonVisiting],
                "NumberOfFollowups": [self.NumberOfFollowups],
                "PreferredPropertyStar": [self.PreferredPropertyStar],
                "NumberOfTrips": [self.NumberOfTrips],
                "Passport": [self.Passport],
                "PitchSatisfactionScore": [self.PitchSatisfactionScore],
                "OwnCar": [self.OwnCar],
                "NumberOfChildrenVisiting": [self.NumberOfChildrenVisiting],
                "MonthlyIncome": [self.MonthlyIncome],
                "TypeofContact": [self.TypeofContact],
                "Occupation": [self.Occupation],
                "Gender": [self.Gender],
                "ProductPitched": [self.ProductPitched],
                "MaritalStatus": [self.MaritalStatus],
                "Designation": [self.Designation],
            }
            
            logging.info("Created travel data dict")
            
            logging.info("Exited get_travel_data_as_dict method as TravelData class")
            
            return input_data
        except Exception as e:
            raise TravelException(e, sys) from e
        
class TravelClassifier:
    def __init__(self, prediction_pipeline_config: TravelPredictorConfig = TravelPredictorConfig(),) -> None:
        """
        :param prediction_pipeline_config: Configuration for prediction the value
        """
        try:
            # self.schema_config = read_yaml_file(SCHEMA_FILE_PATH)
            self.prediction_pipeline_config = prediction_pipeline_config
        except Exception as e:
            raise TravelException(e, sys) from e
        
    def predict(self, dataframe) -> str:
        """
        This is the method of TravelClassifier
        Returns: Prediction in string format
        """
        try:
            logging.info("Entered predict method of TravelClassifier class")
            model = TravelEstimator(
                bucket_name=self.prediction_pipeline_config.model_bucket_name,
                model_path=self.prediction_pipeline_config.model_file_path,
            )
            result = model.predict(dataframe)
            
            return result
        except Exception as e:
            raise TravelException(e, sys) from e
        