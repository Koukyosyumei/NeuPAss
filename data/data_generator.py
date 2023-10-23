import os
import random
import subprocess

import joblib
import numpy as np
from sklearn.mixture import GaussianMixture

from code_generator import code_generator

source_dir = "source"
binary_dir = "binary"
params_dir = "params"

random.seed(42)


def run_grid_search(fname="sample"):
    code = code_generator(random.randint(1, 4))
    cpp_path = os.path.join(source_dir, fname + ".cpp")
    exe_path = os.path.join(binary_dir, fname)
    pf_dir = os.path.join(params_dir, fname)
    os.makedirs(pf_dir, exist_ok=True)

    with open(cpp_path, mode="w") as f:
        f.write(code)

    # Compile the C++ program
    compile_command = ["g++", cpp_path, "-o", exe_path]
    compile_process = subprocess.Popen(
        compile_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    compile_output, compile_error = compile_process.communicate()

    # Check if compilation was successful
    if compile_process.returncode == 0:
        # print(f"Compilation successful - {fname}")

        i = 0
        for x in np.linspace(0.0, 1.0, 11):
            for y in np.linspace(0.1, 1.0, 10):
                for z in np.linspace(0.0, 1.0, 11):
                    # Execute the compiled program and capture its output
                    execute_command = [exe_path] + [str(x), str(y), str(z)]
                    execution_process = subprocess.Popen(
                        execute_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                    )
                    stdout, stderr = execution_process.communicate()
                    vals = np.array(list(map(float, str(stdout)[2:].split("\\n")[:-1])))

                    gmm = GaussianMixture(n_components=10)
                    gmm.fit(vals.reshape(-1, 1))

                    np.savez_compressed(
                        os.path.join(pf_dir, str(i)),
                        x=x,
                        y=y,
                        z=z,
                        weights=gmm.weights_,
                        means=gmm.means_,
                        covariances=gmm.covariances_,
                    )

                    i += 1


if __name__ == "__main__":
    joblib.Parallel(n_jobs=-1)(
        joblib.delayed(run_grid_search)(f"code{i}") for i in range(1000)
    )
