#include <algorithm>
#include <assert.h>
#include <cmath>
#include <fstream>
#include <functional>
#include <limits>
#include <stdio.h>
#include <stdlib.h>
#include <queue>
#include <utility>

#include <streambuf>
#include <iostream>
#include <string>
#include <abc/Driver.h>

using std::binary_function;
using std::cout;
using std::endl;
using std::ifstream;
using std::ofstream;
using std::ios;
using std::min;
using std::max;
using std::numeric_limits;
using std::pair;
using std::queue;
using std::random_shuffle;
using std::stable_sort;
using std::string;
using std::stringstream;

void parse_statements(string line, string* expression);
Vlab::Theory::BigInteger get_model_count(string constraint, int bound);

int main(int argc, char* argv[]){
	if (argc < 2){
		fprintf(stderr, "Syntax: run_branch_translation "
				"<translation directory>"
			);
		return 0;
	}
	ifstream branch_statements, branch_smt;
	ofstream results;
	string line,constraint,directory;
	string expression[6];
	directory = argv[1];
	branch_statements.open(directory+"/branch_statements");
	results.open("results.txt");

	if (branch_statements.is_open()){
		getline(branch_statements,line); //Get rid of the first line
		while(getline(branch_statements,line)){
			parse_statements(line,expression);
			branch_smt.open(directory+"/branch_"+expression[1]+".smt2");
			cout << directory+"/branch_"+expression[1]+".smt2" << endl;
			constraint.assign( (std::istreambuf_iterator<char>(branch_smt)),
					   (std::istreambuf_iterator<char>() ) );
			cout << constraint<< endl;
			Vlab::Theory::BigInteger model_count = get_model_count(constraint, 64);
			results << "branch " << expression[1] << " , count: " << model_count << endl;
			branch_smt.close();
		}
		branch_statements.close();
		results.close();
	}
	return 1;
}

void parse_statements(string line, string* expression){
	string str = line;
	str.erase(remove(str.begin(), str.end(), ' '), str.end()); 
	stringstream s_stream(str);
	int pos = 0;
	while(s_stream.good()){
		string substr;
		getline(s_stream, substr, ',');
		expression[pos] = substr;
		pos++;
	}
}

Vlab::Theory::BigInteger get_model_count(string constraint, int bound){
	Vlab::Driver driver;
	driver.InitializeLogger(0);
	driver.set_option(Vlab::Option::Name::REGEX_FLAG, 0x000f);
	std::istringstream str(constraint);
	driver.Parse(&str);
	driver.InitializeSolver();
	driver.Solve();
	Vlab::Theory::BigInteger count = driver.CountInts(bound);
	driver.reset();

	return count;
}
