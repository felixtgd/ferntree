import argparse
import importlib
import json
import logging
import os
import sys
import time

# Set up logger
LOGGERNAME: str = "ferntree"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(filename)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger: logging.Logger = logging.getLogger(LOGGERNAME)


def build_and_run_simulation(sim_id: str, model_id: str) -> None:
    """Build and run the simulation.

    Args:
        sim_id (str): id of simulation doc in db
        model_id (str): id of model specs doc in db

    """
    # Load sim_builder
    try:
        sim_builder = importlib.import_module("sim_builder")
    except ImportError as e:
        logger.error(f"Failed to import model: {e}")
        sys.exit(1)

    # Build simulation
    builder = sim_builder.SimBuilder(sim_id, model_id)
    sim = builder.build_simulation()

    # Start simulation
    sim.run_simulation()


if __name__ == "__main__":
    logger.info("")
    logger.info("FERNTREE")
    logger.info("")

    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-m", "--model_id", help="id of model specs doc in db", required=True
    )
    parser.add_argument(
        "-s", "--sim_id", help="id of simulation doc in db", required=True
    )
    args = parser.parse_args()
    model_id = args.model_id
    sim_id = args.sim_id

    logger.info(f"Model ID: \t{model_id}")
    logger.info(f"Simulation ID: \t{sim_id}")

    logger.info("")

    # Get the absolute path to the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Load user configuration
    conf_path = os.path.join(script_dir, "conf", "usrconf.json")
    with open(conf_path) as f:
        conf = json.load(f)

    # Set up paths
    ft_path = os.path.abspath(os.path.join(script_dir, conf["env"]["path"]))
    # model_path = os.path.abspath(
    #     os.path.join(script_dir, conf["workspace"]["path"], model)
    # )

    # Add paths to sys.path
    sys.path.insert(0, ft_path)
    # sys.path.insert(0, model_path)

    logger.info(f"Script directory: \t{script_dir}")
    logger.info(f"Ferntree directory: \t{ft_path}")
    # logger.info(f"Model directory: \t{model_path}")
    logger.info("")

    # Build and run the simulation
    start_time = time.time()
    # build_and_run_simulation(model_path)
    build_and_run_simulation(sim_id, model_id)
    end_time = time.time()

    logger.info("")
    logger.info(f"Simulation execution time: {(end_time - start_time):.2f} seconds.")
    logger.info("")
