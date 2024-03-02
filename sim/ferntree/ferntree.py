from host.simHost import SimHost
import time

# Settings
# weather_data_file = "example_input_data.json"

start_time = time.time()

sim = SimHost()
sim.run_simulation()

end_time = time.time()
print(f"Execution time: {end_time - start_time} seconds.")