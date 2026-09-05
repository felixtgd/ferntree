import argparse
import logging
import time

from src.domains.ferntree.sim_builder import SimBuilder

# Set up logger
LOGGERNAME: str = "ferntree"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(filename)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger: logging.Logger = logging.getLogger(LOGGERNAME)


def build_and_run_simulation(sim_id: str, model_id: str) -> None:
    """Build and run the simulation: load the simulation builder, build the simulation,
    and start the simulation.

    Args:
        sim_id (str): id of simulation doc in db
        model_id (str): id of model specs doc in db

    """
    # Build simulation
    builder = SimBuilder(sim_id, model_id)
    sim = builder.build_simulation()

    # Start simulation
    sim.run_simulation()


if __name__ == "__main__":
    logger.info("")
    logger.info("FERNTREE")
    logger.info("")

    # Parse command-line arguments
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument(
        "-m", "--model_id", help="id of model specs doc in db", required=True
    )
    parser.add_argument(
        "-s", "--sim_id", help="id of simulation doc in db", required=True
    )
    args: argparse.Namespace = parser.parse_args()
    model_id: str = args.model_id
    sim_id: str = args.sim_id

    logger.info(f"Model ID: \t{model_id}")
    logger.info(f"Simulation ID: \t{sim_id}")

    logger.info("")

    # Build and run the simulation
    start_time: float = time.time()
    build_and_run_simulation(sim_id, model_id)
    end_time: float = time.time()

    logger.info("")
    logger.info(f"Simulation execution time: {(end_time - start_time):.2f} seconds.")
    logger.info("")
