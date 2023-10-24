#include <iostream>
#include <cmath>
#include <random>

std::random_device seed_gen;
std::default_random_engine engine(seed_gen());

double random_number_generator(double x, double y, double z) {
	double r = 0;

	if (z < 0.4){
		std::lognormal_distribution<> ld_dist(x, 0.8);
		double b_id_true = ld_dist(engine);
		b_id_true = std::cos(b_id_true);
		r += b_id_true;
	} else {
		std::normal_distribution<> n_dist(0.8, y);
		double b_id_false = n_dist(engine);
		b_id_false = std::cos(b_id_false);
		r += b_id_false;
	}
	if (z == 0.1){
		std::normal_distribution<> n_dist(x, y);
		double b_id_true = n_dist(engine);
	} else {
		std::normal_distribution<> n_dist(x, 0.3);
		double b_id_false = n_dist(engine);
	}
	if (z > 0.3){
		std::normal_distribution<> n_dist(0.7, 0.9);
		double b_id_true = n_dist(engine);
		r += b_id_true;
	} else {
		std::lognormal_distribution<> ld_dist(0.0, y);
		double b_id_false = ld_dist(engine);
		r += b_id_false;
	}
	return r;
}

int main(int argc, char *argv[]){
	double x = atof(argv[1]);
	double y = atof(argv[2]);
	double z = atof(argv[3]);
	for (int i = 0; i < 1000; i ++){
		std::cout << random_number_generator(x, y, z) << std::endl;
	}
}

