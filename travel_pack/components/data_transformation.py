import os
import sys

import numpy as np
import pandas as pd
from imblearn.combine import SMOTEENN
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, PowerTransformer

from travel_pack.exception import TravelException
from travel_pack.logger import logging
from travel_pack.entity.config_entity import DataTransformationConfig
from travel_pack.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact, DataTransformationArtifact
from travel_pack.constants import TARGET_COLUMN, SCHEMA_FILE_PATH, RANDOM_STATE
from travel_pack.utils.main_utils import save_numpy_array_data, read_yaml_file, drop_columns, save_object

class DataTransformation:
    def __init__(self, data_ingestion_artifact: DataIngestionArtifact,
                 data_transformation_config: DataTransformationConfig,
                 data_validation_artifact: DataValidationArtifact):
        """
        :param data_ingestion_artifact: Output reference of data ingestion artifact stage
        :param data_transformation_config: configuration for data transformation
        """
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_transformation_config = data_transformation_config
            self.data_validation_artifact = data_validation_artifact
            self._schema_config = read_yaml_file(file_path=SCHEMA_FILE_PATH)
        except Exception as e:
            raise TravelException(e, sys) from e

    @staticmethod
    def read_data(file_path) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise TravelException(e, sys)
        
        
    def get_data_transformer_object(self) -> Pipeline:
        """
        Method Name :   get_data_transformer_object
        Description :   This method creates and returns a data transformer object for the data
        
        Output      :   data transformer object is created and returned 
        On Failure  :   Write an exception log and then raise an exception
        """
        logging.info(
            "Entered get_data_transformer_object method of DataTransformation class"
        )
        
        try:
            logging.info("Got numerical, categorical, transformation columns from schema config")
            
            discrete_columns = self._schema_config['discrete_columns']
            continuous_columns = self._schema_config['continuous_columns']
            categorical_columns = self._schema_config['categorical_columns']
            transformation_columns = self._schema_config['transform_columns']
            
            logging.info(
                "Got numerical cols,one hot cols,binary cols from schema config"
            )

            logging.info("Initialized Data Transformer pipeline.")
            
            discrete_pipeline = Pipeline(
                steps=[
                    ("imputer", SimpleImputer(strategy="most_frequent")),
                    ("scaler", StandardScaler()),
                ]
            ) 
            
            continuous_pipeline = Pipeline(
                steps=[
                    ("imputer", SimpleImputer(strategy="mean")),
                    ("scaler", StandardScaler()),
                ]
            )
            
            cat_pipeline = Pipeline(
                steps=[
                    ("imputer", SimpleImputer(strategy="most_frequent")),
                    ("one_hot_encoder", OneHotEncoder()),
                    ("scaler", StandardScaler(with_mean=False)),
                ]
            )
            
            transform_pipeline = Pipeline(
                steps=[
                    ("imputer", SimpleImputer(strategy="mean")),
                    ("transformer", PowerTransformer(standardize=True)),
                ]
            )
            
            preprocessor = ColumnTransformer(
                [
                    ("discrete_pipeline", discrete_pipeline, discrete_columns),
                    ("continuous_pipeline", continuous_pipeline, continuous_columns),
                    ("cat_pipeline", cat_pipeline, categorical_columns),
                    ("power_transformation", transform_pipeline, transformation_columns),
                ]
            )
            
            logging.info("Created preprocessor object from ColumnTransformer")

            logging.info(
                "Exited get_data_transformer_object method of DataTransformation class"
            )
            
            return preprocessor
        
        except Exception as e:
            raise TravelException(e, sys) from e
        
    
    def initiate_data_transformation(self, ) -> DataTransformationArtifact:
        """
        Method Name :   initiate_data_transformation
        Description :   This method initiates the data transformation component for the pipeline 
        
        Output      :   data transformer steps are performed and preprocessor object is created  
        On Failure  :   Write an exception log and then raise an exception
        """
        try:
            if self.data_validation_artifact.validation_status:
                logging.info("Starting data transformation")
                preprocessor = self.get_data_transformer_object()
                logging.info("Got the Preprocessor object")
                
                train_df = DataTransformation.read_data(file_path=self.data_ingestion_artifact.trained_file_path)
                test_df = DataTransformation.read_data(file_path=self.data_ingestion_artifact.test_file_path)
                
                input_feature_train_df = train_df.drop(columns=[TARGET_COLUMN], axis=1)
                target_feature_train_df = train_df[TARGET_COLUMN]
                
                logging.info("Got train features and test features of Training dataset")
                
                input_feature_train_df['Gender'] = input_feature_train_df['Gender'].replace("Fe Male", "Female")
                
                logging.info("Spelling error correct the gender feature on the training dataset")
                
                drop_cols = self._schema_config['drop_columns']
                
                logging.info("drop the columns in drop_cols of Training dataset")
                
                input_feature_train_df = drop_columns(df=input_feature_train_df, cols=drop_cols)
                
                input_feature_test_df = test_df.drop(columns=[TARGET_COLUMN], axis=1)
                target_feature_test_df = test_df[TARGET_COLUMN]
                
                input_feature_test_df['Gender'] = input_feature_test_df['Gender'].replace("Fe Male", "Female")
                
                logging.info("Spelling error correct the gender feature on the testing dataset")
                
                logging.info("drop the columns in drop_cols of Testing dataset")
                
                input_feature_test_df = drop_columns(df=input_feature_test_df, cols=drop_cols)
                
                logging.info("Got train features and test features of Testing dataset")

                logging.info(
                    "Applying preprocessing object on training dataframe and testing dataframe"
                )
                
                input_feature_train_arr = preprocessor.fit_transform(input_feature_train_df)
                
                logging.info(
                    "Used the preprocessor object to fit transform the train features"
                )
                
                input_feature_test_arr = preprocessor.transform(input_feature_test_df)
                
                logging.info("Used the preprocessor object to transform the test features")

                logging.info("Applying SMOTEENN on Training dataset")
                
                smt = SMOTEENN(sampling_strategy="minority", random_state=RANDOM_STATE)
                
                input_feature_train_final, target_feature_train_final = smt.fit_resample(
                    input_feature_train_arr, target_feature_train_df
                )

                logging.info("Applied SMOTEENN on training dataset")

                logging.info("Applying SMOTEENN on testing dataset")

                input_feature_test_final, target_feature_test_final = smt.fit_resample(
                    input_feature_test_arr, target_feature_test_df
                )

                logging.info("Applied SMOTEENN on testing dataset")

                logging.info("Created train array and test array")

                train_arr = np.c_[
                    input_feature_train_final, np.array(target_feature_train_final)
                ]

                test_arr = np.c_[
                    input_feature_test_final, np.array(target_feature_test_final)
                ]

                save_object(self.data_transformation_config.transformed_object_file_path, preprocessor)
                save_numpy_array_data(self.data_transformation_config.transformed_train_file_path, array=train_arr)
                save_numpy_array_data(self.data_transformation_config.transformed_test_file_path, array=test_arr)

                logging.info("Saved the preprocessor object")

                logging.info(
                    "Exited initiate_data_transformation method of Data_Transformation class"
                )

                data_transformation_artifact = DataTransformationArtifact(
                    transformed_object_file_path=self.data_transformation_config.transformed_object_file_path,
                    transformed_train_file_path=self.data_transformation_config.transformed_train_file_path,
                    transformed_test_file_path=self.data_transformation_config.transformed_test_file_path
                )
                return data_transformation_artifact
            else:
                raise Exception(self.data_validation_artifact.message)

                
        except Exception as e:
            raise TravelException(e, sys) from e