import random

"""
dist_one_parameters = [
    "std::bernoulli_distribution b_dist",
    "std::geometric_distribution<> g_dist",
    "std::chi_squared_distribution<> cs_dist",
    "std::cauchy_distribution<> cd_dist",
    "std::student_t_distribution<> st_dist"
]
"""

dist_two_parameters = [
    "std::uniform_real_distribution<> u_dist",
    "std::normal_distribution<> n_dist",
    # "std::extreme_value_distribution<> ev_dist",
    # "std::lognormal_distribution<> ld_dist",
]

cond_ops = ["==", ">", "<"]


def random_decimal_generator():
    return float(int(random.random() * 10)) / 10.0


def if_block_generator(tab=1, b_id="ib", for_ast=False):
    cond = f"z {random.choice(cond_ops)} {random_decimal_generator()}"
    code = "\t" * tab
    code += f"if ({cond})" + "{\n"
    mu = random_decimal_generator()
    sigma = max(0.1, random_decimal_generator())
    dist = random.choice(dist_two_parameters)
    if "uniform" in dist:
        mu, sigma = f"std::min({mu}, {sigma})", f"std::max({mu}, {sigma})"
    if for_ast:
        code += "\t" * (tab + 1) + dist + ";\n"
        code += "\t" * (tab + 1) + f"{dist.split(' ')[1]}({mu}, {sigma});\n"
    else:
        code += "\t" * (tab + 1) + dist + f"({mu}, {sigma});\n"
    code += "\t" * (tab + 1) + f"double b_id_true = {dist.split(' ')[1]}(engine);\n"
    mp = random.random()
    if mp > 0.75:
        code += "\t" * (tab + 1) + "b_id_true = b_id_true * b_id_true;\n"
    if random.random() > 0.1:
        code += "\t" * (tab + 1) + "r += b_id_true;\n"
    code += "\t" * tab + "} else {\n"
    mu = random_decimal_generator()
    sigma = max(0.1, random_decimal_generator())
    dist = random.choice(dist_two_parameters)
    if "uniform" in dist:
        mu, sigma = f"std::min({mu}, {sigma})", f"std::max({mu}, {sigma})"
    if for_ast:
        code += "\t" * (tab + 1) + dist + ";\n"
        code += "\t" * (tab + 1) + f"{dist.split(' ')[1]}({mu}, {sigma});\n"
    else:
        code += "\t" * (tab + 1) + dist + f"({mu}, {sigma});\n"
    code += "\t" * (tab + 1) + f"double b_id_false = {dist.split(' ')[1]}(engine);\n"
    mp = random.random()
    if mp > 0.75:
        code += "\t" * (tab + 1) + "b_id_false = b_id_false * b_id_false;\n"
    if random_decimal_generator() > 0.1:
        code += "\t" * (tab + 1) + "r += b_id_false;\n"
    code += "\t" * tab + "}\n"

    return code


def block_generator(num_block=3, for_ast=False):
    code = ""
    for _ in range(num_block):
        code += if_block_generator(for_ast=for_ast)
    return code


def code_generator(num_block=3, for_ast=False):
    code = "#include <iostream>\n"
    code += "#include <cmath>\n"
    code += "#include <random>\n\n"
    code += "std::random_device seed_gen;\n"
    code += "std::default_random_engine engine(seed_gen());\n\n"
    code += "double random_number_generator(double z) {\n"
    code += "\tdouble r = 0;\n\n"
    code += block_generator(num_block, for_ast)
    code += "\treturn r;\n"
    code += "}\n\n"
    code += "int main(int argc, char *argv[]){\n"
    code += "\tdouble z = atof(argv[1]);\n"
    code += "\tfor (int i = 0; i < 3000; i ++){\n"
    code += "\t\tstd::cout << random_number_generator(z) << std::endl;\n"
    code += "\t}\n"
    code += "}\n"
    return code


if __name__ == "__main__":
    print(code_generator())
