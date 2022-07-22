// Copyright (c) 2008, Jacob Burnim (jburnim@cs.berkeley.edu)
//
// This file is part of CREST, which is distributed under the revised
// BSD license.  A copy of this license can be found in the file LICENSE.
//
// This program is distributed in the hope that it will be useful, but
// WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See LICENSE
// for details.

#include <iostream>
#include <vector>
#include <algorithm>
#include <assert.h>
#include <cmath>
#include <fstream>
#include <functional>
#include <limits>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <queue>
#include <utility>

#include "base/yices_solver.h"
#include "run_crest/concolic_search.h"

using std::binary_function;
using std::ifstream;
using std::ios;
using std::min;
using std::max;
using std::numeric_limits;
using std::pair;
using std::queue;
using std::random_shuffle;
using std::stable_sort;

namespace crest {

namespace {

typedef pair<size_t,int> ScoredBranch;

struct ScoredBranchComp
  : public binary_function<ScoredBranch, ScoredBranch, bool>
{
  bool operator()(const ScoredBranch& a, const ScoredBranch& b) const {
    return (a.second < b.second);
  }
};

}  // namespace


////////////////////////////////////////////////////////////////////////
//// Search ////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////

Search::Search(const string& program, int max_iterations)
  : program_(program), max_iters_(max_iterations), num_iters_(0) {

  start_time_ = time(NULL);

  { // Read in the set of branches.
    max_branch_ = 0;
    max_function_ = 0;
    branches_.reserve(100000);
    branch_count_.reserve(100000);
    branch_count_.push_back(0);

    ifstream in("branches");
    assert(in);
    function_id_t fid;
    int numBranches;
    while (in >> fid >> numBranches) {
      branch_count_.push_back(2 * numBranches);
      branch_id_t b1, b2;
      for (int i = 0; i < numBranches; i++) {
	assert(in >> b1 >> b2);
	branches_.push_back(b1);
	branches_.push_back(b2);
	max_branch_ = max(max_branch_, max(b1, b2));
      }
    }
    in.close();
    max_branch_ ++;
    max_function_ = branch_count_.size();
  }

  // Compute the paired-branch map.
  paired_branch_.resize(max_branch_);
  for (size_t i = 0; i < branches_.size(); i += 2) {
    paired_branch_[branches_[i]] = branches_[i+1];
    paired_branch_[branches_[i+1]] = branches_[i];
  }

  // Compute the branch-to-function map.
  branch_function_.resize(max_branch_);
  { size_t i = 0;
    for (function_id_t j = 0; j < branch_count_.size(); j++) {
      for (size_t k = 0; k < branch_count_[j]; k++) {
	branch_function_[branches_[i++]] = j;
      }
    }
  }

  // Initialize all branches to "uncovered" (and functions to "unreached").
  total_num_covered_ = num_covered_ = 0;
  reachable_functions_ = reachable_branches_ = 0;
  covered_.resize(max_branch_, false);
  total_covered_.resize(max_branch_, false);
  reached_.resize(max_function_, false);

#if 0
  { // Read in any previous coverage (for faster debugging).
    ifstream in("coverage");
    branch_id_t bid;
    while (in >> bid) {
      covered_[bid] = true;
      num_covered_ ++;
      if (!reached_[branch_function_[bid]]) {
	reached_[branch_function_[bid]] = true;
	reachable_functions_ ++;
	reachable_branches_ += branch_count_[branch_function_[bid]];
      }
    }

    total_num_covered_ = 0;
    total_covered_ = covered_;
  }
#endif

  // Print out the initial coverage.
  fprintf(stderr, "Iteration 0 (0s): covered %u branches [%u reach funs, %u reach branches].\n",
          num_covered_, reachable_functions_, reachable_branches_);

  fprintf(stderr, "Number of branches: %u\n", branches_.size());
  // Sort the branches.
  sort(branches_.begin(), branches_.end());
}


Search::~Search() { }


void Search::WriteInputToFileOrDie(const string& file,
				   const vector<value_t>& input) {
  FILE* f = fopen(file.c_str(), "w");
  if (!f) {
    fprintf(stderr, "Failed to open %s.\n", file.c_str());
    perror("Error: ");
    exit(-1);
  }

  for (size_t i = 0; i < input.size(); i++) {
    fprintf(f, "%lld\n", input[i]);
  }

  fclose(f);
}


void Search::WriteCoverageToFileOrDie(const string& file) {
  FILE* f = fopen(file.c_str(), "w");
  if (!f) {
    fprintf(stderr, "Failed to open %s.\n", file.c_str());
    perror("Error: ");
    exit(-1);
  }

  for (BranchIt i = branches_.begin(); i != branches_.end(); ++i) {
    if (total_covered_[*i]) {
      fprintf(f, "%d\n", *i);
    }
  }

  fclose(f);
}


void Search::LaunchProgram(const vector<value_t>& inputs) {
  WriteInputToFileOrDie("input", inputs);

  /*
  pid_t pid = fork();
  assert(pid != -1);

  if (!pid) {
    system(program_.c_str());
    exit(0);
  }
  */

  system(program_.c_str());
}


void Search::RunProgram(const vector<value_t>& inputs, SymbolicExecution* ex) {
  // if (++num_iters_ > max_iters_) {
  //   // TODO(jburnim): Devise a better system for capping the iterations.
  //   exit(0);
  // }

  // Run the program.
  LaunchProgram(inputs);

  // Read the execution from the program.
  // Want to do this with sockets.  (Currently doing it with files.)
  ifstream in("szd_execution", ios::in | ios::binary);
  assert(in && ex->Parse(in));
  in.close();

  
  /*size_t path_size =  ex->path().constraints().size();
  size_t idx = 0;
  while (idx < path_size) {
    size_t branch_idx = ex->path().constraints_idx()[idx];
    branch_id_t bid = ex->path().branches()[branch_idx];
    fprintf(stderr, "%d ", bid);
    idx++;
  }
  fprintf(stderr, "\n");*/
}


bool Search::UpdateCoverage(const SymbolicExecution& ex) {
  return UpdateCoverage(ex, NULL);
}

bool Search::UpdateCoverage(const SymbolicExecution& ex,
			    set<branch_id_t>* new_branches) {

  const unsigned int prev_covered_ = num_covered_;
  const vector<branch_id_t>& branches = ex.path().branches();
  for (BranchIt i = branches.begin(); i != branches.end(); ++i) {
    if ((*i > 0) && !covered_[*i]) {
      covered_[*i] = true;
      num_covered_++;
      if (new_branches) {
	new_branches->insert(*i);
      }
      if (!reached_[branch_function_[*i]]) {
	reached_[branch_function_[*i]] = true;
	reachable_functions_ ++;
	reachable_branches_ += branch_count_[branch_function_[*i]];
      }
    }
    if ((*i > 0) && !total_covered_[*i]) {
      total_covered_[*i] = true;
      total_num_covered_++;
    }
  }

  fprintf(stderr, "Iteration %d (%lds): covered %u branches [%u reach funs, %u reach branches].\n",
	  num_iters_, time(NULL)-start_time_, total_num_covered_, reachable_functions_, reachable_branches_);

  bool found_new_branch = (num_covered_ > prev_covered_);
  if (found_new_branch) {
    WriteCoverageToFileOrDie("coverage");
  }

  return found_new_branch;
}


void Search::RandomInput(const map<var_t,type_t>& vars, vector<value_t>* input) {
  input->resize(vars.size());

  for (map<var_t,type_t>::const_iterator it = vars.begin(); it != vars.end(); ++it) {
    unsigned long long val = 0;
    for (size_t j = 0; j < 8; j++)
      val = (val << 8) + (rand() / 256);

    switch (it->second) {
    case types::U_CHAR:
      input->at(it->first) = (unsigned char)val; break;
    case types::CHAR:
      input->at(it->first) = (char)val; break;
    case types::U_SHORT:
      input->at(it->first) = (unsigned short)val; break;
    case types::SHORT:
      input->at(it->first) = (short)val; break;
    case types::U_INT:
      input->at(it->first) = (unsigned int)val; break;
    case types::INT:
      input->at(it->first) = (int)val; break;
    case types::U_LONG:
      input->at(it->first) = (unsigned long)val; break;
    case types::LONG:
      input->at(it->first) = (long)val; break;
    case types::U_LONG_LONG:
      input->at(it->first) = (unsigned long long)val; break;
    case types::LONG_LONG:
      input->at(it->first) = (long long)val; break;
    }
  }
}


bool Search::SolveAtBranch(const SymbolicExecution& ex,
                           size_t idx,
                           vector<value_t>* input) {

  const vector<SymbolicPred*>& constraints = ex.path().constraints();

  // Optimization: If any of the previous constraints are identical to the
  // branch_idx-th constraint, immediately return false.
  for (int i = static_cast<int>(idx) - 1; i >= 0; i--) {
    if (constraints[idx]->Equal(*constraints[i])) {

      size_t branch_idx = ex.path().constraints_idx()[idx];
      branch_id_t bid = ex.path().branches()[branch_idx];
      //fprintf(stderr, "[SolveAtBranch] branch_id=%d\n", bid);

      branch_idx = ex.path().constraints_idx()[i];
      bid = ex.path().branches()[branch_idx];
      //fprintf(stderr, "[SolveAtBranch] conflicting branch_id=%d\n", bid);
      return false;
    }
  }

  vector<const SymbolicPred*> cs(constraints.begin(),
				 constraints.begin()+idx+1); // change here to get the prefix of the symbolic path
  map<var_t,value_t> soln;
  constraints[idx]->Negate(); // instead of negating the path, add the constraint for specific branch
  // fprintf(stderr, "Yices . . . ");
  bool success = YicesSolver::IncrementalSolve(ex.inputs(), ex.vars(), cs, &soln);
  //fprintf(stderr, "%d\n", success);
  constraints[idx]->Negate(); // change accordingly

  if (success) {
    // Merge the solution with the previous input to get the next
    // input.  (Could merge with random inputs, instead.)
    *input = ex.inputs();
    // RandomInput(ex.vars(), input);

    typedef map<var_t,value_t>::const_iterator SolnIt;
    for (SolnIt i = soln.begin(); i != soln.end(); ++i) {
      (*input)[i->first] = i->second;
    }
    return true;
  }

  return false;
}


bool Search::CheckPrediction(const SymbolicExecution& old_ex,
			     const SymbolicExecution& new_ex,
			     size_t branch_idx) {

  if ((old_ex.path().branches().size() <= branch_idx)
      || (new_ex.path().branches().size() <= branch_idx)) {
    return false;
  }

   for (size_t j = 0; j < branch_idx; j++) {
     if  (new_ex.path().branches()[j] != old_ex.path().branches()[j]) {
       return false;
     }
   }
   return (new_ex.path().branches()[branch_idx]
           == paired_branch_[old_ex.path().branches()[branch_idx]]);
}


////////////////////////////////////////////////////////////////////////
//// BoundedDepthFirstSearch ///////////////////////////////////////////
////////////////////////////////////////////////////////////////////////

BoundedDepthFirstSearch::BoundedDepthFirstSearch
(const string& program, int max_iterations, int max_depth)
  : Search(program, max_iterations), max_depth_(max_depth) { }

BoundedDepthFirstSearch::~BoundedDepthFirstSearch() { }

void BoundedDepthFirstSearch::Run() {
  // Initial execution (on empty/random inputs).
  SymbolicExecution ex;
  RunProgram(vector<value_t>(), &ex);
  UpdateCoverage(ex);

  DFS(0, max_depth_, ex);
  // DFS(0, ex);
}

  /*
void BoundedDepthFirstSearch::DFS(int depth, SymbolicExecution& prev_ex) {
  SymbolicExecution cur_ex;
  vector<value_t> input;

  const SymbolicPath& path = prev_ex.path();

  int last = min(max_depth_, static_cast<int>(path.constraints().size()) - 1);
  for (int i = last; i >= depth; i--) {
    // Solve constraints[0..i].
    if (!SolveAtBranch(prev_ex, i, &input)) {
      continue;
    }

    // Run on those constraints.
    RunProgram(input, &cur_ex);
    UpdateCoverage(cur_ex);

    // Check for prediction failure.
    size_t branch_idx = path.constraints_idx()[i];
    if (!CheckPrediction(prev_ex, cur_ex, branch_idx)) {
      fprintf(stderr, "Prediction failed!\n");
      continue;
    }

    // Recurse.
    DFS(i+1, cur_ex);
  }
}
  */


void BoundedDepthFirstSearch::DFS(size_t pos, int depth, SymbolicExecution& prev_ex) {
  SymbolicExecution cur_ex;
  vector<value_t> input;

  const SymbolicPath& path = prev_ex.path();

  for (size_t i = pos; (i < path.constraints().size()) && (depth > 0); i++) {
    // Solve constraints[0..i].
    if (!SolveAtBranch(prev_ex, i, &input)) {
      continue;
    }

    // Run on those constraints.
    RunProgram(input, &cur_ex);
    UpdateCoverage(cur_ex);

    // Check for prediction failure.
    size_t branch_idx = path.constraints_idx()[i];
    if (!CheckPrediction(prev_ex, cur_ex, branch_idx)) {
      fprintf(stderr, "Prediction failed!\n");
      continue;
    }

    // We successfully solved the branch, recurse.
    depth--;
    DFS(i+1, depth, cur_ex);
  }
}


////////////////////////////////////////////////////////////////////////
//// RandomInputSearch /////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////

RandomInputSearch::RandomInputSearch(const string& program, int max_iterations)
  : Search(program, max_iterations) { }

RandomInputSearch::~RandomInputSearch() { }

void RandomInputSearch::Run() {
  vector<value_t> input;
  RunProgram(input, &ex_);

  while (true) {
    RandomInput(ex_.vars(), &input);
    RunProgram(input, &ex_);
    UpdateCoverage(ex_);
  }
}


////////////////////////////////////////////////////////////////////////
//// RandomSearch //////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////

RandomSearch::RandomSearch(const string& program, int max_iterations)
  : Search(program, max_iterations) { }

RandomSearch::~RandomSearch() { }

void RandomSearch::Run() {
  SymbolicExecution next_ex;

  while (true) {
    // Execution (on empty/random inputs).
    fprintf(stderr, "RESET\n");
    vector<value_t> next_input;
    RunProgram(next_input, &ex_);
    UpdateCoverage(ex_);

    // Do some iterations.
    int count = 0;
    while (count++ < 10000) {
      // fprintf(stderr, "Uncovered bounded DFS.\n");
      // SolveUncoveredBranches(0, 20, ex_);

      size_t idx;
      if (SolveRandomBranch(&next_input, &idx)) {
	RunProgram(next_input, &next_ex);
	bool found_new_branch = UpdateCoverage(next_ex);
	bool prediction_failed =
	  !CheckPrediction(ex_, next_ex, ex_.path().constraints_idx()[idx]);

	if (found_new_branch) {
	  count = 0;
	  ex_.Swap(next_ex);
	  if (prediction_failed)
	    fprintf(stderr, "Prediction failed (but got lucky).\n");
	} else if (!prediction_failed) {
	  ex_.Swap(next_ex);
	} else {
	  fprintf(stderr, "Prediction failed.\n");
	}
      }
    }
  }
}

  /*
bool RandomSearch::SolveUncoveredBranches(SymbolicExecution& prev_ex) {
  SymbolicExecution cur_ex;
  vector<value_t> input;

  bool success = false;

  int cnt = 0;

  for (size_t i = 0; i < prev_ex.path().constraints().size(); i++) {

    size_t bid_idx = prev_ex.path().constraints_idx()[i];
    branch_id_t bid = prev_ex.path().branches()[bid_idx];
    if (covered_[paired_branch_[bid]])
      continue;

    if (!SolveAtBranch(prev_ex, i, &input)) {
      if (++cnt == 1000) {
	cnt = 0;
	fprintf(stderr, "Failed to solve at %u/%u.\n",
		i, prev_ex.path().constraints().size());
      }
      continue;
    }
    cnt = 0;

    RunProgram(input, &cur_ex);
    UpdateCoverage(cur_ex);
    if (!CheckPrediction(prev_ex, cur_ex, bid_idx)) {
      fprintf(stderr, "Prediction failed.\n");
      continue;
    }

    success = true;
    cur_ex.Swap(prev_ex);
  }

  return success;
}
  */

void RandomSearch::SolveUncoveredBranches(size_t i, int depth,
					  const SymbolicExecution& prev_ex) {
  if (depth < 0)
    return;

  fprintf(stderr, "position: %zu/%zu (%d)\n",
	  i, prev_ex.path().constraints().size(), depth);

  SymbolicExecution cur_ex;
  vector<value_t> input;

  int cnt = 0;

  for (size_t j = i; j < prev_ex.path().constraints().size(); j++) {
    size_t bid_idx = prev_ex.path().constraints_idx()[j];
    branch_id_t bid = prev_ex.path().branches()[bid_idx];
    if (covered_[paired_branch_[bid]])
      continue;

    if (!SolveAtBranch(prev_ex, j, &input)) {
      if (++cnt == 1000) {
	cnt = 0;
	fprintf(stderr, "Failed to solve at %zu/%zu.\n",
		j, prev_ex.path().constraints().size());
      }
      continue;
    }
    cnt = 0;

    RunProgram(input, &cur_ex);
    UpdateCoverage(cur_ex);
    if (!CheckPrediction(prev_ex, cur_ex, bid_idx)) {
      fprintf(stderr, "Prediction failed.\n");
      continue;
    }

    SolveUncoveredBranches(j+1, depth-1, cur_ex);
  }
}


  bool RandomSearch::SolveRandomBranch(vector<value_t>* next_input, size_t* idx) {
  /*
  const SymbolicPath& p = ex_.path();
  vector<ScoredBranch> zero_branches, other_branches;
  zero_branches.reserve(p.constraints().size());
  other_branches.reserve(p.constraints().size());

  vector<size_t> idxs(p.constraints().size());
  for (size_t i = 0; i < idxs.size(); i++) {
    idxs[i] = i;
  }
  random_shuffle(idxs.begin(), idxs.end());

  vector<int> seen(max_branch_);
  for (vector<size_t>::const_iterator i = idxs.begin(); i != idxs.end(); ++i) {
    branch_id_t bid = p.branches()[p.constraints_idx()[*i]];
    if (!covered_[paired_branch_[bid]]) {
      zero_branches.push_back(make_pair(*i, seen[bid]));
    } else {
      other_branches.push_back(make_pair(*i, seen[bid]));
    }
    seen[bid] += 1;
  }

  stable_sort(zero_branches.begin(), zero_branches.end(), ScoredBranchComp());

  int tries = 1000;
  for (size_t i = 0; (i < zero_branches.size()) && (tries > 0); i++, tries--) {
    if (SolveAtBranch(ex_, zero_branches[i].first, next_input))
      return;
  }

  stable_sort(other_branches.begin(), other_branches.end(), ScoredBranchComp());
  for (size_t i = 0; (i < other_branches.size()) && (tries > 0); i++, tries--) {
    if (SolveAtBranch(ex_, other_branches[i].first, next_input))
      return;
  }
  */

  vector<size_t> idxs(ex_.path().constraints().size());
  for (size_t i = 0; i < idxs.size(); i++)
    idxs[i] = i;

  for (int tries = 0; tries < 1000; tries++) {
    // Pick a random index.
    if (idxs.size() == 0)
      break;
    size_t r = rand() % idxs.size();
    size_t i = idxs[r];
    swap(idxs[r], idxs.back());
    idxs.pop_back();

    if (SolveAtBranch(ex_, i, next_input)) {
      fprintf(stderr, "Solved %zu/%zu\n", i, idxs.size());
      *idx = i;
      return true;
    }
  }

  // We failed to solve a branch, so reset the input.
  fprintf(stderr, "FAIL\n");
  next_input->clear();
  return false;
}


////////////////////////////////////////////////////////////////////////
//// RandomSearch //////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////

UniformRandomSearch::UniformRandomSearch(const string& program,
					 int max_iterations,
					 size_t max_depth)
  : Search(program, max_iterations), max_depth_(max_depth) { }

UniformRandomSearch::~UniformRandomSearch() { }

void UniformRandomSearch::Run() {
  // Initial execution (on empty/random inputs).
  RunProgram(vector<value_t>(), &prev_ex_);
  UpdateCoverage(prev_ex_);

  while (true) {
    fprintf(stderr, "RESET\n");

    // Uniform random path.
    DoUniformRandomPath();
  }
}

void UniformRandomSearch::DoUniformRandomPath() {
  vector<value_t> input;

  size_t i = 0;
  size_t depth = 0;
  fprintf(stderr, "%zu constraints.\n", prev_ex_.path().constraints().size());
  while ((i < prev_ex_.path().constraints().size()) && (depth < max_depth_)) {
    if (SolveAtBranch(prev_ex_, i, &input)) {
      fprintf(stderr, "Solved constraint %zu/%zu.\n",
	      (i+1), prev_ex_.path().constraints().size());
      depth++;

      // With probability 0.5, force the i-th constraint.
      if (rand() % 2 == 0) {
	RunProgram(input, &cur_ex_);
	UpdateCoverage(cur_ex_);
	size_t branch_idx = prev_ex_.path().constraints_idx()[i];
	if (!CheckPrediction(prev_ex_, cur_ex_, branch_idx)) {
	  fprintf(stderr, "prediction failed\n");
	  depth--;
	} else {
	  cur_ex_.Swap(prev_ex_);
	}
      }
    }

    i++;
  }
}


////////////////////////////////////////////////////////////////////////
//// HybridSearch //////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////

HybridSearch::HybridSearch(const string& program, int max_iterations, int step_size)
  : Search(program, max_iterations), step_size_(step_size) { }

HybridSearch::~HybridSearch() { }

void HybridSearch::Run() {
  SymbolicExecution ex;

  while (true) {
    // Execution on empty/random inputs.
    RunProgram(vector<value_t>(), &ex);
    UpdateCoverage(ex);

    // Local searches at increasingly deeper execution points.
    for (size_t pos = 0; pos < ex.path().constraints().size(); pos += step_size_) {
      RandomLocalSearch(&ex, pos, pos+step_size_);
    }
  }
}

void HybridSearch::RandomLocalSearch(SymbolicExecution *ex, size_t start, size_t end) {
  for (int iters = 0; iters < 100; iters++) {
    if (!RandomStep(ex, start, end))
      break;
  }
}

bool HybridSearch::RandomStep(SymbolicExecution *ex, size_t start, size_t end) {

  if (end > ex->path().constraints().size()) {
    end = ex->path().constraints().size();
  }
  assert(start < end);

  SymbolicExecution next_ex;
  vector<value_t> input;

  fprintf(stderr, "%zu-%zu\n", start, end);
  vector<size_t> idxs(end - start);
  for (size_t i = 0; i < idxs.size(); i++) {
    idxs[i] = start + i;
  }

  for (int tries = 0; tries < 1000; tries++) {
    // Pick a random index.
    if (idxs.size() == 0)
      break;
    size_t r = rand() % idxs.size();
    size_t i = idxs[r];
    swap(idxs[r], idxs.back());
    idxs.pop_back();

    if (SolveAtBranch(*ex, i, &input)) {
      RunProgram(input, &next_ex);
      UpdateCoverage(next_ex);
      if (CheckPrediction(*ex, next_ex, ex->path().constraints_idx()[i])) {
	ex->Swap(next_ex);
	return true;
      }
    }
  }

  return false;
}


////////////////////////////////////////////////////////////////////////
//// CfgBaselineSearch /////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////

CfgBaselineSearch::CfgBaselineSearch(const string& program, int max_iterations)
  : Search(program, max_iterations) { }

CfgBaselineSearch::~CfgBaselineSearch() { }


void CfgBaselineSearch::Run() {
  SymbolicExecution ex;

  while (true) {
    // Execution on empty/random inputs.
    fprintf(stderr, "RESET\n");
    RunProgram(vector<value_t>(), &ex);
    UpdateCoverage(ex);

    while (DoSearch(5, 250, 0, ex)) {
      // As long as we keep finding new branches . . . .
      ex.Swap(success_ex_);
    }
  }
}


bool CfgBaselineSearch::DoSearch(int depth, int iters, int pos,
				 const SymbolicExecution& prev_ex) {

  // For each symbolic branch/constraint in the execution path, we will
  // compute a heuristic score, and then attempt to force the branches
  // in order of increasing score.
  vector<ScoredBranch> scoredBranches(prev_ex.path().constraints().size() - pos);
  for (size_t i = 0; i < scoredBranches.size(); i++) {
    scoredBranches[i].first = i + pos;
  }

  { // Compute (and sort by) the scores.
    random_shuffle(scoredBranches.begin(), scoredBranches.end());
    map<branch_id_t,int> seen;
    for (size_t i = 0; i < scoredBranches.size(); i++) {
      size_t idx = scoredBranches[i].first;
      size_t branch_idx = prev_ex.path().constraints_idx()[idx];
      branch_id_t bid = paired_branch_[prev_ex.path().branches()[branch_idx]];
      if (covered_[bid]) {
	scoredBranches[i].second = 100000000 + seen[bid];
      } else {
	scoredBranches[i].second = seen[bid];
      }
      seen[bid] += 1;
    }
  }
  stable_sort(scoredBranches.begin(), scoredBranches.end(), ScoredBranchComp());

  // Solve.
  SymbolicExecution cur_ex;
  vector<value_t> input;
  for (size_t i = 0; i < scoredBranches.size(); i++) {
    if (iters <= 0) {
      return false;
    }

    if (!SolveAtBranch(prev_ex, scoredBranches[i].first, &input)) {
      continue;
    }

    RunProgram(input, &cur_ex);
    iters--;

    if (UpdateCoverage(cur_ex, NULL)) {
      success_ex_.Swap(cur_ex);
      return true;
    }
  }

  return false;
}


////////////////////////////////////////////////////////////////////////
//// CfgHeuristicSearch ////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////

CfgHeuristicSearch::CfgHeuristicSearch
(const string& program, int max_iterations)
  : Search(program, max_iterations),
    cfg_(max_branch_), cfg_rev_(max_branch_), dist_(max_branch_) {

  // Read in the CFG.
  ifstream in("cfg_branches", ios::in | ios::binary);
  assert(in);
  size_t num_branches;
  in.read((char*)&num_branches, sizeof(num_branches));
  assert(num_branches == branches_.size());
  for (size_t i = 0; i < num_branches; i++) {
    branch_id_t src;
    size_t len;
    in.read((char*)&src, sizeof(src));
    in.read((char*)&len, sizeof(len));
    cfg_[src].resize(len);
    in.read((char*)&cfg_[src].front(), len * sizeof(branch_id_t));
  }
  in.close();

  // Construct the reversed CFG.
  for (BranchIt i = branches_.begin(); i != branches_.end(); ++i) {
    for (BranchIt j = cfg_[*i].begin(); j != cfg_[*i].end(); ++j) {
      cfg_rev_[*j].push_back(*i);
    }
  }
}


CfgHeuristicSearch::~CfgHeuristicSearch() { }


void CfgHeuristicSearch::Run() {
  set<branch_id_t> newly_covered_;
  SymbolicExecution ex;

  while (true) {
    covered_.assign(max_branch_, false);
    num_covered_ = 0;

    // Execution on empty/random inputs.
    fprintf(stderr, "RESET\n");
    RunProgram(vector<value_t>(), &ex);
    if (UpdateCoverage(ex)) {
      UpdateBranchDistances();
      PrintStats();
    }

    // while (DoSearch(3, 200, 0, kInfiniteDistance+10, ex)) {
    while (DoSearch(5, 30, 0, kInfiniteDistance, ex)) {
    // while (DoSearch(3, 10000, 0, kInfiniteDistance, ex)) {
      PrintStats();
      // As long as we keep finding new branches . . . .
      UpdateBranchDistances();
      ex.Swap(success_ex_);
    }
    PrintStats();
  }
}


void CfgHeuristicSearch::PrintStats() {
  fprintf(stderr, "Cfg solves: %u/%u (%u lucky [%u continued], %u on 0's, %u on others,"
	  "%u unsats, %u prediction failures)\n",
	  (num_inner_lucky_successes_ + num_inner_zero_successes_ + num_inner_nonzero_successes_ + num_top_solve_successes_),
	  num_inner_solves_, num_inner_lucky_successes_, (num_inner_lucky_successes_ - num_inner_successes_pred_fail_),
	  num_inner_zero_successes_, num_inner_nonzero_successes_,
	  num_inner_unsats_, num_inner_pred_fails_);
  fprintf(stderr, "    (recursive successes: %u)\n", num_inner_recursive_successes_);
  fprintf(stderr, "Top-level SolveAlongCfg: %u/%u\n",
	  num_top_solve_successes_, num_top_solves_);
  fprintf(stderr, "All SolveAlongCfg: %u/%u  (%u all concrete, %u no paths)\n",
	  num_solve_successes_, num_solves_,
	  num_solve_all_concrete_, num_solve_no_paths_);
  fprintf(stderr, "    (sat failures: %u/%u)  (prediction failures: %u) (recursions: %u)\n",
	  num_solve_unsats_, num_solve_sat_attempts_,
	  num_solve_pred_fails_, num_solve_recurses_);
}


void CfgHeuristicSearch::UpdateBranchDistances() {
  // We run a BFS backward, starting simultaneously at all uncovered vertices.
  queue<branch_id_t> Q;
  for (BranchIt i = branches_.begin(); i != branches_.end(); ++i) {
    if (!covered_[*i]) {
      dist_[*i] = 0;
      Q.push(*i);
    } else {
      dist_[*i] = kInfiniteDistance;
    }
  }

  while (!Q.empty()) {
    branch_id_t i = Q.front();
    size_t dist_i = dist_[i];
    Q.pop();

    for (BranchIt j = cfg_rev_[i].begin(); j != cfg_rev_[i].end(); ++j) {
      if (dist_i + 1 < dist_[*j]) {
	dist_[*j] = dist_i + 1;
	Q.push(*j);
      }
    }
  }
}


bool CfgHeuristicSearch::DoSearch(int depth,
				  int iters,
				  int pos,
				  int maxDist,
				  const SymbolicExecution& prev_ex) {

  fprintf(stderr, "DoSearch(%d, %d, %d, %zu)\n",
	  depth, pos, maxDist, prev_ex.path().branches().size());

  if (pos >= static_cast<int>(prev_ex.path().constraints().size()))
    return false;

  if (depth == 0)
    return false;


  // For each symbolic branch/constraint in the execution path, we will
  // compute a heuristic score, and then attempt to force the branches
  // in order of increasing score.
  vector<ScoredBranch> scoredBranches(prev_ex.path().constraints().size() - pos);
  for (size_t i = 0; i < scoredBranches.size(); i++) {
    scoredBranches[i].first = i + pos;
  }

  { // Compute (and sort by) the scores.
    random_shuffle(scoredBranches.begin(), scoredBranches.end());
    map<branch_id_t,int> seen;
    for (size_t i = 0; i < scoredBranches.size(); i++) {
      size_t idx = scoredBranches[i].first;
      size_t branch_idx = prev_ex.path().constraints_idx()[idx];
      branch_id_t bid = paired_branch_[prev_ex.path().branches()[branch_idx]];

      scoredBranches[i].second = dist_[bid] + seen[bid];
      seen[bid] += 1;

      /*
      if (dist_[bid] == 0) {
        scoredBranches[i].second = 0;
      } else {
        scoredBranches[i].second = dist_[bid] + seen[bid];
        seen[bid] += 1;
      }
      */
    }
  }
  stable_sort(scoredBranches.begin(), scoredBranches.end(), ScoredBranchComp());

  // Solve.
  SymbolicExecution cur_ex;
  vector<value_t> input;
  for (size_t i = 0; i < scoredBranches.size(); i++) {
    if ((iters <= 0) || (scoredBranches[i].second > maxDist))
      return false;

    num_inner_solves_ ++;

    if (!SolveAtBranch(prev_ex, scoredBranches[i].first, &input)) {
      num_inner_unsats_ ++;
      continue;
    }

    RunProgram(input, &cur_ex);
    iters--;

    size_t b_idx = prev_ex.path().constraints_idx()[scoredBranches[i].first];
    branch_id_t bid = paired_branch_[prev_ex.path().branches()[b_idx]];
    set<branch_id_t> new_branches;
    bool found_new_branch = UpdateCoverage(cur_ex, &new_branches);
    bool prediction_failed = !CheckPrediction(prev_ex, cur_ex, b_idx);


    if (found_new_branch && prediction_failed) {
      fprintf(stderr, "Prediction failed.\n");
      fprintf(stderr, "Found new branch by forcing at "
	              "distance %zu (%d) [lucky, pred failed].\n",
	      dist_[bid], scoredBranches[i].second);

      // We got lucky, and can't really compute any further stats
      // because prediction failed.
      num_inner_lucky_successes_ ++;
      num_inner_successes_pred_fail_ ++;
      success_ex_.Swap(cur_ex);
      return true;
    }

    if (found_new_branch && !prediction_failed) {
      fprintf(stderr, "Found new branch by forcing at distance %zu (%d).\n",
	      dist_[bid], scoredBranches[i].second);
      size_t min_dist = MinCflDistance(b_idx, cur_ex, new_branches);
      // Check if we were lucky.
      if (FindAlongCfg(b_idx, dist_[bid], cur_ex, new_branches)) {
	assert(min_dist <= dist_[bid]);
	// A legitimate find -- return success.
	if (dist_[bid] == 0) {
	  num_inner_zero_successes_ ++;
	} else {
	  num_inner_nonzero_successes_ ++;
	}
	success_ex_.Swap(cur_ex);
	return true;
      } else {
	// We got lucky, but as long as there were no prediction failures,
	// we'll finish the CFG search to see if that works, too.
	assert(min_dist > dist_[bid]);
	assert(dist_[bid] != 0);
	num_inner_lucky_successes_ ++;
      }
    }

    if (prediction_failed) {
      fprintf(stderr, "Prediction failed.\n");
      if (!found_new_branch) {
	num_inner_pred_fails_ ++;
	continue;
      }
    }

    // If we reached here, then scoredBranches[i].second is greater than 0.
    num_top_solves_ ++;
    if ((dist_[bid] > 0) &&
        SolveAlongCfg(b_idx, scoredBranches[i].second-1, cur_ex)) {
      num_top_solve_successes_ ++;
      PrintStats();
      return true;
    }

    if (found_new_branch) {
      success_ex_.Swap(cur_ex);
      return true;
    }

    /*
    if (DoSearch(depth-1, 5, scoredBranches[i].first+1, scoredBranches[i].second-1, cur_ex)) {
      num_inner_recursive_successes_ ++;
      return true;
    }
    */
  }

  return false;
}


size_t CfgHeuristicSearch::MinCflDistance
(size_t i, const SymbolicExecution& ex, const set<branch_id_t>& bs) {

  const vector<branch_id_t>& p = ex.path().branches();

  if (i >= p.size())
    return numeric_limits<size_t>::max();

  if (bs.find(p[i]) != bs.end())
    return 0;

  vector<size_t> stack;
  size_t min_dist = numeric_limits<size_t>::max();
  size_t cur_dist = 1;

  fprintf(stderr, "Found uncovered branches at distances:");
  for (BranchIt j = p.begin()+i+1; j != p.end(); ++j) {
    if (bs.find(*j) != bs.end()) {
      min_dist = min(min_dist, cur_dist);
      fprintf(stderr, " %zu", cur_dist);
    }

    if (*j >= 0) {
      cur_dist++;
    } else if (*j == kCallId) {
      stack.push_back(cur_dist);
    } else if (*j == kReturnId) {
      if (stack.size() == 0)
	break;
      cur_dist = stack.back();
      stack.pop_back();
    } else {
      fprintf(stderr, "\nBad branch id: %d\n", *j);
      exit(1);
    }
  }

  fprintf(stderr, "\n");
  return min_dist;
}

bool CfgHeuristicSearch::FindAlongCfg(size_t i, unsigned int dist,
				      const SymbolicExecution& ex,
				      const set<branch_id_t>& bs) {

  const vector<branch_id_t>& path = ex.path().branches();

  if (i >= path.size())
    return false;

  branch_id_t bid = path[i];
  if (bs.find(bid) != bs.end())
    return true;

  if (dist == 0)
    return false;

  // Compute the indices of all branches on the path that immediately
  // follow the current branch (corresponding to the i-th constraint)
  // in the CFG. For example, consider the path:
  //     * ( ( ( 1 2 ) 4 ) ( 5 ( 6 7 ) ) 8 ) 9
  // where '*' is the current branch.  The branches immediately
  // following '*' are : 1, 4, 5, 8, and 9.
  vector<size_t> idxs;
  { size_t pos = i + 1;
    CollectNextBranches(path, &pos, &idxs);
  }

  for (vector<size_t>::const_iterator j = idxs.begin(); j != idxs.end(); ++j) {
    if (FindAlongCfg(*j, dist-1, ex, bs))
      return true;
  }

  return false;
}


bool CfgHeuristicSearch::SolveAlongCfg(size_t i, unsigned int max_dist,
				       const SymbolicExecution& prev_ex) {
  num_solves_ ++;

  fprintf(stderr, "SolveAlongCfg(%zu,%u)\n", i, max_dist);
  SymbolicExecution cur_ex;
  vector<value_t> input;
  const vector<branch_id_t>& path = prev_ex.path().branches();

  // Compute the indices of all branches on the path that immediately
  // follow the current branch (corresponding to the i-th constraint)
  // in the CFG. For example, consider the path:
  //     * ( ( ( 1 2 ) 4 ) ( 5 ( 6 7 ) ) 8 ) 9
  // where '*' is the current branch.  The branches immediately
  // following '*' are : 1, 4, 5, 8, and 9.
  bool found_path = false;
  vector<size_t> idxs;
  { size_t pos = i + 1;
    CollectNextBranches(path, &pos, &idxs);
    // fprintf(stderr, "Branches following %d:", path[i]);
    for (size_t j = 0; j < idxs.size(); j++) {
      // fprintf(stderr, " %d(%u,%u,%u)", path[idxs[j]], idxs[j],
      //      dist_[path[idxs[j]]], dist_[paired_branch_[path[idxs[j]]]]);
      if ((dist_[path[idxs[j]]] <= max_dist)
	  || (dist_[paired_branch_[path[idxs[j]]]] <= max_dist))
	found_path = true;
    }
    //fprintf(stderr, "\n");
  }

  if (!found_path) {
    num_solve_no_paths_ ++;
    return false;
  }

  bool all_concrete = true;
  num_solve_all_concrete_ ++;

  // We will iterate through these indices in some order (random?
  // increasing order of distance? decreasing?), and try to force and
  // recurse along each one with distance no greater than max_dist.
  random_shuffle(idxs.begin(), idxs.end());
  for (vector<size_t>::const_iterator j = idxs.begin(); j != idxs.end(); ++j) {
    // Skip if distance is wrong.
    if ((dist_[path[*j]] > max_dist)
	&& (dist_[paired_branch_[path[*j]]] > max_dist)) {
      continue;
    }

    if (dist_[path[*j]] <= max_dist) {
      // No need to force, this branch is on a shortest path.
      num_solve_recurses_ ++;
      if (SolveAlongCfg(*j, max_dist-1, prev_ex)) {
	num_solve_successes_ ++;
	return true;
      }
    }

    // Find the constraint corresponding to branch idxs[*j].
    vector<size_t>::const_iterator idx =
      lower_bound(prev_ex.path().constraints_idx().begin(),
		  prev_ex.path().constraints_idx().end(), *j);
    if ((idx == prev_ex.path().constraints_idx().end()) || (*idx != *j)) {
      continue;  // Branch is concrete.
    }
    size_t c_idx = idx - prev_ex.path().constraints_idx().begin();

    if (all_concrete) {
      all_concrete = false;
      num_solve_all_concrete_ --;
    }

    if(dist_[paired_branch_[path[*j]]] <= max_dist) {
      num_solve_sat_attempts_ ++;
      // The paired branch is along a shortest path, so force.
      if (!SolveAtBranch(prev_ex, c_idx, &input)) {
	num_solve_unsats_ ++;
	continue;
      }
      RunProgram(input, &cur_ex);
      if (UpdateCoverage(cur_ex)) {
	num_solve_successes_ ++;
	success_ex_.Swap(cur_ex);
	return true;
      }
      if (!CheckPrediction(prev_ex, cur_ex, *j)) {
	num_solve_pred_fails_ ++;
	continue;
      }

      // Recurse.
      num_solve_recurses_ ++;
      if (SolveAlongCfg(*j, max_dist-1, cur_ex)) {
	num_solve_successes_ ++;
	return true;
      }
    }
  }

  return false;
}

void CfgHeuristicSearch::SkipUntilReturn(const vector<branch_id_t> path, size_t* pos) {
  while ((*pos < path.size()) && (path[*pos] != kReturnId)) {
    if (path[*pos] == kCallId) {
      (*pos)++;
      SkipUntilReturn(path, pos);
      if (*pos >= path.size())
	return;
      assert(path[*pos] == kReturnId);
    }
    (*pos)++;
  }
}

void CfgHeuristicSearch::CollectNextBranches
(const vector<branch_id_t>& path, size_t* pos, vector<size_t>* idxs) {
  // fprintf(stderr, "Collect(%u,%u,%u)\n", path.size(), *pos, idxs->size());

  // Eat an arbitrary sequence of call-returns, collecting inside each one.
  while ((*pos < path.size()) && (path[*pos] == kCallId)) {
    (*pos)++;
    CollectNextBranches(path, pos, idxs);
    SkipUntilReturn(path, pos);
    if (*pos >= path.size())
      return;
    assert(path[*pos] == kReturnId);
    (*pos)++;
  }

  // If the sequence of calls is followed by a branch, add it.
  if ((*pos < path.size()) && (path[*pos] >= 0)) {
    idxs->push_back(*pos);
    (*pos)++;
    return;
  }

  // Alternatively, if the sequence is followed by a return, collect the branches
  // immediately following the return.
  /*
  if ((*pos < path.size()) && (path[*pos] == kReturnId)) {
    (*pos)++;
    CollectNextBranches(path, pos, idxs);
  }
  */
}


bool CfgHeuristicSearch::DoBoundedBFS(int i, int depth, const SymbolicExecution& prev_ex) {
  if (depth <= 0)
    return false;

  fprintf(stderr, "%d (%d: %d) (%d: %d)\n", depth,
          i-1, prev_ex.path().branches()[prev_ex.path().constraints_idx()[i-1]],
          i, prev_ex.path().branches()[prev_ex.path().constraints_idx()[i]]);

  SymbolicExecution cur_ex;
  vector<value_t> input;
  const vector<SymbolicPred*>& constraints = prev_ex.path().constraints();
  for (size_t j = static_cast<size_t>(i); j < constraints.size(); j++) {
    if (!SolveAtBranch(prev_ex, j, &input)) {
      continue;
    }

    RunProgram(input, &cur_ex);
    iters_left_--;
    if (UpdateCoverage(cur_ex)) {
      success_ex_.Swap(cur_ex);
      return true;
    }

    if (!CheckPrediction(prev_ex, cur_ex, prev_ex.path().constraints_idx()[j])) {
      fprintf(stderr, "Prediction failed!\n");
      continue;
    }

    return (DoBoundedBFS(j+1, depth-1, cur_ex)
	    || DoBoundedBFS(j+1, depth-1, prev_ex));
  }

  return false;
}


////////////////////////////////////////////////////////////////////////
//// PathDirectedSearch /////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////

PathDirectedSearch::PathDirectedSearch(const string& program, int max_iterations)
  : Search(program, max_iterations) { }

PathDirectedSearch::~PathDirectedSearch() { }


void PathDirectedSearch::Run() {

  if (DoSearch()) {
      vector<value_t> input = success_ex_.inputs();
      fprintf(stderr, "inputs:\n");
      for(int i=0; i < input.size(); i++) {
        fprintf(stderr, "%d ", input.at(i));
      }
  }
}


bool PathDirectedSearch::DoSearch() {

  
  SymbolicExecution ex;
  vector<value_t> init_input;
  init_input.push_back(60);
  init_input.push_back(63);
  init_input.push_back(120);
  init_input.push_back(109);
  init_input.push_back(108);
  init_input.push_back(32);
  init_input.push_back(118);
  init_input.push_back(101);
  init_input.push_back(114);
  init_input.push_back(115);
  init_input.push_back(105);
  init_input.push_back(111);
  init_input.push_back(110);
  init_input.push_back(61);
  init_input.push_back(34);
  init_input.push_back(49);
  init_input.push_back(46);
  init_input.push_back(48);
  init_input.push_back(34);
  init_input.push_back(63);
  init_input.push_back(62);
  init_input.push_back(10);

  init_input.push_back(97); 
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);

  
  
  RunProgram(init_input, &ex);

  // Solve.
  vector<value_t> input;

  vector<int> rare_path;
  char path[10000] = "3739557 3739560 3739563 3739566 3739569 3739572 3739271 3739277 3728363 3728373 3728380 3728364 3728365 3728367 3728370 3738821 3738824 3738827 3738830 3738833 3738836 3738839 3738847 3728364 3728365 3728367 3728370 3738857 3725227 3725233 3725298 3728364 3728365 3728367 3728370 3738862 3725227 3725233 3725298 3738780 3738781 3725227 3725233 3725298 3738793 3725227 3725233 3725298 3738799 3738800 3725227 3725233 3725298 3738802 3738867 3725227 3725233 3725298 3804638 3804638 3804638 3739316 3739319 3739323 3739328 3739331 3739334 3739342 3728364 3728365 3728366 3728372 3728380 3728364 3728365 3728367 3728370 3804537 3804537 3804537 3728364 3728365 3728367 3728370 3728348 3739470 3739486 3728348 3739636 3739639 3739642 3739645 3739648 3739651 3739654 3739657 3739660 3739664 3739668 3739672 3739675 3739676 3739683 3739695 3739699 3739705 3738625 3738497 3738501 3738509 3738510 3738520 3738523 3738526 3738529 3738532 3738535 3738538 3738541 3738544 3738547 3738583 3738587 3738590 3738598 3738603 3738606 3726833 3726838";
  //fprintf(stderr, "%s", path);
  char *token = strtok(path, " ");
  //fprintf(stderr, "%s", token);
  // loop through the string to extract all other tokens
  while( token != NULL ) {
    //fprintf(stderr, "%s", token);
    rare_path.push_back(atoi(token));
    token = strtok(NULL, " ");
  }
  

  

  size_t idx = 0;
  // { // Print the constraints. 
  //   string tmp;
  //   for (size_t i = 0; i < ex.path().constraints().size(); i++) {
  //     tmp.clear();
  //     ex.path().constraints()[i]->AppendToString(&tmp);
  //     fprintf(stderr, "%s\n", tmp);
  //   }
  // }
  fprintf(stderr, "path size=%d\n", ex.path().constraints().size());
  while (idx < ex.path().constraints().size()) {
    size_t branch_idx = ex.path().constraints_idx()[idx];
    branch_id_t bid = ex.path().branches()[branch_idx];
    fprintf(stderr, "%d ", bid);
    idx++;
  }
  fprintf(stderr, "\n");
  idx = 0;
  while (idx < ex.path().constraints().size() && idx < rare_path.size()) {
    //fprintf(stderr, "idx=%d\n", idx);
    size_t branch_idx = ex.path().constraints_idx()[idx];
    //fprintf(stderr, "branch_idx=%d\n", branch_idx);
    branch_id_t bid = ex.path().branches()[branch_idx];
    //fprintf(stderr, "branch_id=%d\n", bid);
    input.clear();
    if (bid != rare_path[idx]) {
      fprintf(stderr, "branch_id=%d\n", bid);
      bid = paired_branch_[ex.path().branches()[branch_idx]];
      fprintf(stderr, "negated branch_id=%d\n", bid);
      fprintf(stderr, "rare branch_id=%d\n", rare_path[idx]);
      if (bid != rare_path[idx]) {
        fprintf(stderr, "Something is wrong!!! None of the branches are in the path!!!");
        return false;
        //idx++;
        //continue;
      } else {
        fprintf(stderr, "%d\n", branch_idx);
        fprintf(stderr, "%d\n", ex.path().branches()[branch_idx]);
        if (!SolveAtBranch(ex, idx, &input)) {
          fprintf(stderr, "The rare path is not feasible");
          return false;
        } else {
          //successfully entered to another depth
          fprintf(stderr, "inputs:\n");
          for(int i=0; i < input.size(); i++) {
            fprintf(stderr, "%d ", input.at(i));
          }
          fprintf(stderr, "\nRunning program ...");
          SymbolicExecution cur_ex;
          RunProgram(input, &cur_ex);
          fprintf(stderr, "\nCurrent symbolic path size = %d", cur_ex.path().constraints().size());
          fprintf(stderr, "\nUpdating symbolic path ...");
          ex.Swap(cur_ex);

          fprintf(stderr, "\nidx = %d", idx);
          fprintf(stderr, "\nsymbolic path size = %d", ex.path().constraints().size());
          fprintf(stderr, "\nrare path size = %d", rare_path.size());

          fprintf(stderr, "\npath size=%d\n", ex.path().constraints().size());
          size_t index = 0;
          while (index < ex.path().constraints().size()) {
            size_t br_idx = ex.path().constraints_idx()[index];
            branch_id_t br_id = ex.path().branches()[br_idx];
            fprintf(stderr, "%d ", br_id);
            index++;
          }
          fprintf(stderr, "\n");
        }
      }
    }
    idx++;
  }
  success_ex_.Swap(ex);

  return true;
}



////////////////////////////////////////////////////////////////////////
//// PathGuidedSearch /////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////

PathGuidedSearch::PathGuidedSearch(const string& program, int max_iterations, string path)
  : Search(program, max_iterations), path_(path) { }

PathGuidedSearch::~PathGuidedSearch() { }


void PathGuidedSearch::Run() {

  if (DoSearch()) {
      vector<value_t> input = success_ex_.inputs();
      printf("inputs:\n");
      for(int i=0; i < input.size(); i++) {
        printf("%d ", input.at(i));
      }
  }
}


bool PathGuidedSearch::DoSearch() {

  
  SymbolicExecution ex;
  vector<value_t> init_input;
  init_input.push_back(60);
  init_input.push_back(63);
  init_input.push_back(120);
  init_input.push_back(109);
  init_input.push_back(108);
  init_input.push_back(32);
  init_input.push_back(118);
  init_input.push_back(101);
  init_input.push_back(114);
  init_input.push_back(115);
  init_input.push_back(105);
  init_input.push_back(111);
  init_input.push_back(110);
  init_input.push_back(61);
  init_input.push_back(34);
  init_input.push_back(49);
  init_input.push_back(46);
  init_input.push_back(48);
  init_input.push_back(34);
  init_input.push_back(63);
  init_input.push_back(62);
  init_input.push_back(10);

  // 60 97 32 98 61 34 99 34 62 100 60 47 97 62
  init_input.push_back(60);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(32);
  init_input.push_back(98);
  init_input.push_back(61);
  init_input.push_back(34);
  init_input.push_back(99);
  init_input.push_back(34);
  init_input.push_back(62);
  init_input.push_back(100);
  init_input.push_back(60);
  init_input.push_back(47);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(97);
  init_input.push_back(62);
  
  RunProgram(init_input, &ex);

  // Solve.
  vector<value_t> input;

  vector<int> rare_path;
  //char path[10000] = "4648325 4648328 4648331 4648334 4648337 4648340 4648352 4648356 4648359 4648368 4648371 4648372 4648379 4648381 4648382 4648385 4648388 4648395 4648399 4648404 4648407 4648410 4648413 4648416 4648419 4648422 4648425 4648428 4648432 4645502 4645509 4645511 4645513 4644237 4644240 4642941 4642944 4642947 4642951 4642954 4642956 4642959 4642962 4642965";
  //char path[10000] = "4648325 4648328 4648331 4648334 4648337 4648340 4648352 4648038 4648045 4637122 4637123 4637126 4637132 4637133 4637135 4637136 4637138 4648061 4648084 4648087 4648091 4648092 4648096 4648099 4648102 4648109 4648122 4648125 4648129 4648133 4648136 4648140 4648141 4648145 4648148 4648164 4648169 4648172 4637079 4637081 4637084 4637087 4637091 4637102 4637105 4650387 4650394 4650398 4650401 4650406 4648356 4648357";
  
  //xmllint intra-inter
  //char path[10000] = "4648325 4648328 4648331 4648334 4648337 4648340 4648352 4648356 4648359 4648368 4648371 4648372 4648379 4648381 4648382 4648385 4648388 4648395 4648399 4648404 4648407 4648410 4648413 4648416 4648419 4648422 4648425 4648428 4648432 4645502 4645509 4645511 4645512 4645517 4645520 4645523 4645526 4645529 4643937 4643942 4644170 4644171 4644201 4644228 4644231 4644237 4644240 4644244 4644260 4644263 4641972 4641975 4641978 4641981 4641984 4641987 4641990 4641993 4641995 4641998";
  //char path[10000] = "4648325 4648328 4648331 4648334 4648337 4648340 4648352 4648356 4648359 4648368 4648371 4648372 4648379 4648381 4648382 4648385 4648388 4648395 4648399 4648404 4648407 4648410 4648413 4648416 4648419 4648422 4648425 4648428 4648432 4645502 4645509 4645511 4645512 4645517 4645520 4645523 4645526 4645529 4643937 4644171 4644201 4644233 4644237 4644240 4644244 4644260 4644263 4641972 4641975 4641978 4641981 4641984 4641987 4641990 4641993 4641995 4642003 4642012 4642018 4642023";
  //char path[10000] = "4648325 4648328 4648331 4648334 4648337 4648340 4648352 4648356 4648359 4648368 4648371 4648372 4648379 4648381 4648382 4648385 4648388 4648395 4648399 4648404 4648407 4648410 4648413 4648416 4648419 4648422 4648425 4648428 4648432 4645502 4645509 4645511 4645512 4645517 4645520 4645523 4645526 4645529 4643937 4643942 4643945 4644169 4644171 4644201 4644233 4644237 4644240 4644245 4644247 4642941 4642944 4642947 4642950 4642953 4642956 4642959 4642962 4642965 4642973 4642979";
  //char path[10000] = "4648325 4648328 4648331 4648334 4648337 4648340 4648352 4648356 4648359 4648368 4648371 4648372 4648379 4648381 4648382 4648385 4648388 4648395 4648399 4648404 4648407 4648410 4648413 4648416 4648419 4648422 4648425 4648428 4648432 4645502 4645509 4645511 4645512 4645517 4645520 4645523 4645526 4645529 4643937 4643942 4643945 4644169 4644171 4644172 4644200 4644201 4644233 4644237 4644240 4644244 4644259 4643767 4643770 4643773 4643776 4643779 4643782 4643785 4643788 4643791";
  
  //xmllint intra
  //char path[10000] = "4648325 4648328 4648331 4648334 4648337 4648341 4648344 4648347 4648352 4648356 4648359 4648368 4648371 4648372 4648379 4648381 4648382 4648390 4648395 4648398 4648404 4648407 4648410 4648413 4648416 4648419 4648422 4648425 4648428 4648437 4648440 4648443 4648444 4648451 4648463 4648466 4637079 4637081 4637084 4637087 4637091 4637102 4637108 4637117";
  char path_arr[10000];
  strcpy(path_arr, path_.c_str());
  //fprintf(stderr, "%s", path);
  char *token = strtok(path_arr, " ");
  //fprintf(stderr, "%s", token);
  // loop through the string to extract all other tokens
  while( token != NULL ) {
    //fprintf(stderr, "%s", token);
    rare_path.push_back(atoi(token));
    token = strtok(NULL, " ");
  }
  

  

  size_t idx = 0;
  size_t sim_idx = 0;
  // { // Print the constraints. 
  //   string tmp;
  //   for (size_t i = 0; i < ex.path().constraints().size(); i++) {
  //     tmp.clear();
  //     ex.path().constraints()[i]->AppendToString(&tmp);
  //     fprintf(stderr, "%s\n", tmp);
  //   }
  // }
  int found = 0;
  size_t ex_path_size =  ex.path().constraints().size();
  printf("path size=%d\n", ex_path_size);
  while (idx < ex_path_size) {
    size_t branch_idx = ex.path().constraints_idx()[idx];
    branch_id_t bid = ex.path().branches()[branch_idx];
    // if (bid == atoi("4642965")) {
    //   found = 1;
    // }
    printf("%d ", bid);
    idx++;
  }
  fprintf(stderr, "\n");

  int count = 100;
  int best_num_rare_path_nodes = 0;
  int best_num_new_rare_path_nodes = 0;
  vector<int> rare_path_nodes;

  //check if some prefix match, if then do not negate those initial branches
  sim_idx = 0;
  while (sim_idx < ex_path_size && sim_idx < rare_path.size()) {
    //fprintf(stderr, "idx=%d\n", idx);
    size_t branch_idx = ex.path().constraints_idx()[sim_idx];
    //fprintf(stderr, "branch_idx=%d\n", branch_idx);
    branch_id_t bid = ex.path().branches()[branch_idx];
    //fprintf(stderr, "branch_id=%d\n", bid);
    input.clear();
    if (bid == rare_path[sim_idx]) {
      sim_idx++;
    }
    else {
      break;
    }
  }

  idx = sim_idx;

  while (found == 0 && count >= 1) {
    
    int could_solve = 0;
    size_t branch_idx = ex.path().constraints_idx()[idx];
    branch_id_t bid = ex.path().branches()[branch_idx];
    branch_id_t selected_bid = bid;
    printf("selected branch id = %d\n", bid);
    size_t selected_idx = idx;
    
    while(idx < ex_path_size) {
      printf("idx=%d\n", idx);
      if (!SolveAtBranch(ex, idx, &input)) {
        printf("could not solve!\n");
        idx++;
        continue;
      } else {
        size_t branch_idx = ex.path().constraints_idx()[idx];
        branch_id_t bid = ex.path().branches()[branch_idx];
        //if (bid == 4491872) {
          printf("Successfully negated a branch (%d) to do further analysis\n", bid);
        //}
        could_solve = 1;
        SymbolicExecution cur_ex;
        RunProgram(input, &cur_ex);

        size_t cur_path_size =  cur_ex.path().constraints().size();
        size_t cur_idx = 0;
        int num_rare_path_nodes = 0;
        int num_new_rare_path_nodes = 0;

        //if (bid == 4491872) {
          printf("inputs:\n");
          for(int i=0; i < input.size(); i++) {
            printf("%d ", input.at(i));
          }
          printf("\n");
          printf("cur_path_size = %d\n", cur_path_size);
        //}

        while (cur_idx < cur_path_size) {
          size_t cur_branch_idx = cur_ex.path().constraints_idx()[cur_idx];
          branch_id_t cur_bid = cur_ex.path().branches()[cur_branch_idx];
          //if (bid == 4491872) {
            printf("%d ", cur_bid);
          //}
          // if (cur_bid == atoi("4642965")) {
          //   found = 1;
          //   printf("\n\n\nFound the node!!!\n\n\n");
          //   //break;
          // }
          if (std::count(rare_path.begin(), rare_path.end(), cur_bid)) {
            num_rare_path_nodes++;
            // if (!(std::count(rare_path_nodes.begin(), rare_path_nodes.end(), cur_bid))) {
            //   rare_path_nodes.push_back(cur_bid);
            //   num_new_rare_path_nodes++;
            // }
          }
          cur_idx++;
        }
        //if (bid == 4491872) {
          printf("\nbest_num_rare_path_nodes = %d\n", best_num_rare_path_nodes);
          printf("num_rare_path_nodes = %d\n", num_rare_path_nodes);
          //printf("\nbest_num_new_rare_path_nodes = %d\n", best_num_new_rare_path_nodes);
          printf("num_new_rare_path_nodes = %d\n", num_new_rare_path_nodes);
          //exit(0);
        //}
        if (num_rare_path_nodes > best_num_rare_path_nodes) {
          best_num_rare_path_nodes = num_rare_path_nodes;
          size_t branch_idx = ex.path().constraints_idx()[idx];
          branch_id_t bid = ex.path().branches()[branch_idx];
          selected_idx = idx;
          selected_bid = bid;
          printf("branch to negate=%d\n", bid);
          //break;
        }
        // else if (num_new_rare_path_nodes > best_num_new_rare_path_nodes) {
        //   best_num_new_rare_path_nodes = num_new_rare_path_nodes;
        //   size_t branch_idx = ex.path().constraints_idx()[idx];
        //   branch_id_t bid = ex.path().branches()[branch_idx];
        //   selected_idx = idx;
        //   selected_bid = bid;
        //   printf("branch to negate=%d\n", bid);
        //   //break;
        // }
      }
      idx++;
      //idx_count--;
    }
    printf("\nSelected branch for negation: %d\n", selected_bid);
    printf("could_solve = %d\n", could_solve);
    //exit(0);
    if (could_solve == 0) {
      printf("No path is not feasible");
      return false;
    } else {
      printf("idx before = %d\n", idx);
      idx = selected_idx + 1; //to start negating from this point in the next iteration
      printf("idx after = %d\n", idx);
      printf("Successfully negated a branch to get closer to the rare path\n");
      SolveAtBranch(ex, selected_idx, &input);
      printf("inputs:\n");
      for(int i=0; i < input.size(); i++) {
        printf("%d ", input.at(i));
      }
      printf("\nRunning program ...");
      SymbolicExecution cur_ex;
      RunProgram(input, &cur_ex);
      printf("\nCurrent symbolic path size = %d", cur_ex.path().constraints().size());
      printf("\nUpdating symbolic path ...");
      ex.Swap(cur_ex);
      ex_path_size =  ex.path().constraints().size();
      printf("path size=%d\n", ex_path_size);
      size_t ix = 0;
      while (ix < ex_path_size) {
        size_t branch_idx = ex.path().constraints_idx()[ix];
        branch_id_t bid = ex.path().branches()[branch_idx];
        // if (bid == atoi("4642965")) {
        //   found = 1;
        //   fprintf(stderr, "\n\n\nFound the node finally!!!\n\n\n");
        // }
        printf("%d ", bid);
        ix++;
      }
      printf("\n");
      //exit(0);
    }
    count--;
    printf("count = %d\n", count);
    printf("ex path size = %d\n", ex_path_size);
    printf("idx = %d\n", idx);
  }
  success_ex_.Swap(ex);

  return true;
}


}  // namespace crest
