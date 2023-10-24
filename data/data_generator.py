import os
import random
import subprocess

import joblib
import networkx as nx
import numpy as np
import torch
from sklearn.exceptions import ConvergenceWarning
from sklearn.mixture import GaussianMixture
from sklearn.utils._testing import ignore_warnings
from torch_geometric.utils import from_networkx

from code_generator import code_generator
from extract_ast import (extract_function_ast, print_function_ast,
                         traverse_function_ast)

source_dir = "source"
binary_dir = "binary"
params_dir = "params"

random.seed(42)

LABEL2CAT = {}
SPELL2CAT = {}


@ignore_warnings(category=ConvergenceWarning)
def run_grid_search(fname="sample", seed=0):
    random.seed(seed)
    code = code_generator(random.randint(1, 4))
    random.seed(seed)
    code4ast = code_generator(random.randint(1, 4))

    cpp_path = os.path.join(source_dir, fname + ".cpp")
    cpp4ast_path = os.path.join(source_dir, fname + "_ast" + ".cpp")
    # grp_path = os.path.join(source_dir, fname + ".pt")
    exe_path = os.path.join(binary_dir, fname)
    pf_dir = os.path.join(params_dir, fname)
    os.makedirs(pf_dir, exist_ok=True)

    with open(cpp_path, mode="w") as f:
        f.write(code)

    with open(cpp4ast_path, mode="w") as f:
        f.write(cpp4ast_path)

    # it = extract_function_ast(cpp_path, "random_number_generator")
    # func_ast = list(it)[-1]

    # graph = nx.DiGraph()
    # traverse_function_ast(func_ast, None, graph, LABEL2CAT, SPELL2CAT)
    # data = from_networkx(graph)
    # torch.save(data, grp_path)

    # Compile the C++ program
    compile_command = ["g++", cpp_path, "-o", exe_path]
    compile_process = subprocess.Popen(
        compile_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    _ = compile_process.communicate()

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
                    vals = np.array(
                        list(map(float, str(stdout)[2:].split("\\n")[:-1])))

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
        joblib.delayed(run_grid_search)(f"code{i}", i) for i in range(2)
    )
