import os

# ========= 🚨 MUST SET BEFORE ANY IMPORTS 🚨 =========
# Disable GPU and Metal (causes hangs on macOS)
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["METAL_DEVICE_WRAPPER_TYPE"] = "1"

# Aggressively limit threading to prevent deadlocks
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

# TensorFlow specific settings
os.environ["TF_NUM_INTRAOP_THREADS"] = "1"
os.environ["TF_NUM_INTEROP_THREADS"] = "1"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

# Disable TensorFlow GPU (force CPU only)
os.environ["TF_FORCE_GPU_ALLOW_GROWTH"] = "false"

# 🔥 ADD THESE CRITICAL macOS FIXES 🔥
os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"
os.environ["GRPC_POLL_STRATEGY"] = "poll"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
# ======================================================

from src.plant_detection import logger
from src.plant_detection.pipeline.data_validation_stage import DataValidationTrainingPipeline
from src.plant_detection.pipeline.data_transformation_stage import DataTransformationTrainingPipeline
from src.plant_detection.pipeline.model_training_stage import ModelTrainingPipeline



STAGE_NAME = "Data Validation stage"
try:
   logger.info(f">>>>>> stage {STAGE_NAME} started <<<<<<") 
   data_validation = DataValidationTrainingPipeline()
   data_validation.main()
   logger.info(f">>>>>> stage {STAGE_NAME} completed <<<<<<\n\nx==========x")
except Exception as e:
        logger.exception(e)
        raise e

STAGE_NAME = "Data Transformation stage"
try:
   logger.info(f">>>>>> stage {STAGE_NAME} started <<<<<<") 
   data_transformation = DataTransformationTrainingPipeline()
   data_transformation.main()
   logger.info(f">>>>>> stage {STAGE_NAME} completed <<<<<<\n\nx==========x")
except Exception as e:
        logger.exception(e)
        raise e

STAGE_NAME = "Model Training stage"
try:
   logger.info(f">>>>>> stage {STAGE_NAME} started <<<<<<")
   logger.info("About to create ModelTrainingPipeline instance...")
   model_training = ModelTrainingPipeline()
   logger.info("ModelTrainingPipeline created, calling main()...")
   model_training.main()
   logger.info(f">>>>>> stage {STAGE_NAME} completed <<<<<<\n\nx==========x")
except Exception as e:
        logger.exception(e)
        raise e