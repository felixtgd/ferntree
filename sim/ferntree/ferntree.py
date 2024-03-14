import os
import sys
import argparse
import importlib
import logging
import json
import time


# Global variable to control logging
ENABLE_LOGGING = True

# Set up logging
logger = logging.getLogger("ferntree")
if ENABLE_LOGGING:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
else:
    logging.basicConfig(level=logging.CRITICAL, format="%(message)s")


def build_and_run_simulation():
    # Load sim_builder
    try:
        sim_builder = importlib.import_module("sim_builder")
    except ImportError as e:
        logger.error(f"Failed to import model: {e}")
        sys.exit(1)

    # Build simulation
    builder = sim_builder.SimBuilder(model_path)
    sim = builder.build_simulation()

    # Start simulation
    sim.run_simulation()


if __name__ == "__main__":
    logger.info("")
    logger.info("FERNTREE")
    logger.info("")

    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--model", help="model name", required=True)
    args = parser.parse_args()
    model = args.model

    logger.info(f"Model: \t{model}")
    logger.info("")

    # Get the absolute path to the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Load user configuration
    conf_path = os.path.join(script_dir, "conf", "usrconf.json")
    with open(conf_path) as f:
        conf = json.load(f)

    # Set up paths
    ft_path = os.path.abspath(os.path.join(script_dir, conf["env"]["path"]))
    model_path = os.path.abspath(
        os.path.join(script_dir, conf["workspace"]["path"], model)
    )

    # Add paths to sys.path
    sys.path.insert(0, ft_path)
    sys.path.insert(0, model_path)

    logger.info(f"Script directory: \t{script_dir}")
    logger.info(f"Ferntree directory: \t{ft_path}")
    logger.info(f"Model directory: \t{model_path}")
    logger.info("")

    # Build and run the simulation
    start_time = time.time()
    build_and_run_simulation()
    end_time = time.time()

    logger.info("")
    logger.info(f"Execution time: {(end_time - start_time):.2f} seconds.")
    logger.info("")
