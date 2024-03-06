import sys
import os
import argparse
import importlib
import logging
import json
import time


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("")
    logger.info("FERNTREE")
    logger.info("")

    if len(sys.argv) != 3:
        logger.error("Usage: python ferntree.py -m <model>")
        sys.exit(1)
    else:
        # Change working directory to the location of this file
        os.chdir(os.path.dirname(os.path.realpath(__file__)))

        # Get model name from command line
        parser = argparse.ArgumentParser()
        parser.add_argument("-m", "--model", help="model name", required=True)
        args = parser.parse_args()
        model = args.model

        # Load user configuration
        with open('conf/usrconf.json') as f:
            conf = json.load(f)
        # absolute path to ferntree environment
        ft_path = os.path.abspath(conf['env']['path'])
        sys.path.insert(0, ft_path)
        # absolute path to workspace with model
        model_path = os.path.abspath(os.path.join(conf['workspace']['path'], model))
        sys.path.insert(0, model_path)

        logger.info(f"Model: \t{model}")
        logger.info("")
        logger.info(f"Ferntree directory: \t{ft_path}")
        logger.info(f"Model directory: \t{model_path}")
        logger.info("")

        try:
            start_time = time.time()
    
            # Load model
            importlib.import_module(model)

            end_time = time.time()
            logger.info(f"Execution time: {(end_time - start_time):.2f} seconds.")
        
        except ImportError as e:
            logger.error(f"Failed to import model: {e}")
            sys.exit(1)
