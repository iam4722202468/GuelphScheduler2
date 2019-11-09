#include "mcr.h"

std::vector<std::vector<int>> gen_mutate(std::vector<std::vector<void*>> arrs, std::vector<std::vector<int>> currPaths, std::vector<std::vector<std::vector<std::vector<bool>>>> *possibleCombinations) {
  // Loop through all arrays
  // Keep parent incase parent is better than children
  for (unsigned int x = 1; x < currPaths.size(); ++x) {
    std::vector<std::vector<bool>> possibleCombinationsAcc;

    // Loop through all current paths
    for (unsigned int y = 0; y < currPaths.at(x).size(); ++y) {
      std::vector<std::vector<bool>> *possibleBranch = NULL;

      if (y > 0) {
        if (y == 1)
          possibleCombinationsAcc = (*possibleCombinations)[0][currPaths.at(x).at(0)];
        else {
          possibleBranch = &((*possibleCombinations)[y-1][currPaths.at(x).at(y-1)]);

          for (unsigned int i = 0; i < possibleCombinationsAcc.size(); ++i) {
            for (unsigned int j = 0; j < possibleCombinationsAcc.at(i).size(); ++j) {
              possibleCombinationsAcc[i][j] = (*possibleBranch)[i][j] & possibleCombinationsAcc[i][j];
            }
          }
        }

        /*for (auto i : possibleCombinationsAcc) {
          for (auto j : i) {
            std::cout << j << ", ";
          }
          std::cout << std::endl;
        }*/
      }

      /*for (auto i : currPaths.at(x)) {
        std::cout << i << ",";
      }
      std::cout << std::endl;
      std::cout << std::endl;*/

      std::vector<int> availableBranches;

      // Is the current value still a working tree?
      // Ensure that mutations at beginning of tree account for no changes at the end
      bool isStillViable = true;

      if (y == 0) {
        for (unsigned int i = 0; i < arrs.at(y).size(); ++i) {
          availableBranches.push_back(i);
        }
      } else {
        for (int i = 0; i < possibleCombinationsAcc.at(y).size(); ++i) {
          if(possibleCombinationsAcc.at(y).at(i)) {
            availableBranches.push_back(i);
          } else if (currPaths.at(x).at(y) == i) {
            //std::cout << "Branch cancelled\n";
            isStillViable = false;
          }
        }
      }

      // Maybe add branch recovery here in the future
      if (availableBranches.size() == 0) {
        currPaths.erase(currPaths.begin()+x);
        //std::cout << "ERROR\n";
        break;
      }

      unsigned int toChange = rand() % availableBranches.size();
      unsigned int toChangeCheck = rand() % 100;

      // x percentage chance of mutation
      // if branch is not viable, force mutation
      if (toChangeCheck < 15 || !isStillViable) {
        currPaths.at(x).at(y) = availableBranches.at(toChange);
      }
    }
    //std::cout << std::endl;
  }

  return currPaths;
}

gen_trim_struct* gen_trim(std::vector<std::vector<void*>> arrs, std::vector<std::vector<int>> currPaths, int pathNum, int compare(int, int), int fitness(std::vector<std::vector<void*>>*, std::vector<int>, int)) {
  int fitPlaceHigh = 0;
  int fitValueHigh = 0;

  for (unsigned int x = 0; x < currPaths.size(); ++x) {
    int fit = fitness(&arrs, currPaths.at(x), x);
    if (x == 0 || compare(fit, fitValueHigh) > 0) {
      fitValueHigh = fit;
      fitPlaceHigh = x;
    }
  }

  std::vector<int> fitTop = currPaths.at(fitPlaceHigh);

  //std::cout << "Fit: " << fitValueHigh << std::endl;
  gen_trim_struct *topFound = new gen_trim_struct;
  topFound->fitness = fitValueHigh;
  topFound->top = fitTop;

  return topFound;
}

std::vector<std::vector<int>> gen_base(std::vector<std::vector<int>> currPaths, std::vector<int> base, int groupSize) {
  for (int x = 0; x < groupSize; x++) {
    currPaths.push_back(base);
  }

  return currPaths;
}

float standard_deviation(std::vector<int> fitnesses) {
  float var = 0;
  float mean = 0;

  for (unsigned int n = 0; n < fitnesses.size(); ++n) {
    mean += fitnesses[n];
  }
  mean /= fitnesses.size();

  for (unsigned int n = 0; n < fitnesses.size(); n++) {
    var += (fitnesses[n] - mean) * (fitnesses[n] - mean);
  }
  var /= fitnesses.size();

  return sqrt(var);
}

// returns all possible paths after used path
std::vector<std::vector<int>> getPossiblePaths(std::vector<std::vector<std::vector<std::vector<bool>>>> *possibleCombinations, std::vector<int> path) {
  std::vector<std::vector<int>> paths;

  if (path.size() > 0) {
    // go until the end of the current path, return if not possible
    std::vector<std::vector<bool>> acc = (*possibleCombinations)[0][path[0]];
    for (int x = 1; x < path.size(); ++x) {
      std::vector<std::vector<bool>> joinWith = (*possibleCombinations)[x][path[x]];
      for (int i = 0; i < joinWith.size(); ++i) {
        for (int j = 0; j < joinWith.at(i).size(); ++j) {
          acc[i][j] = acc[i][j] & joinWith[i][j];
        }
      }
    }

    /*for (int i = 0; i < acc.size(); ++i) {
      for (int j = 0; j < acc.at(i).size(); ++j) {
        std::cout << acc[i][j] << ", ";
      }
      std::cout << std::endl;
    }*/

    // Loop through values possible for next value.
    // These values are found on the line one after the path ends
    for (int x = 0; x < acc[path.size()].size(); x++) {
      if (acc[path.size()][x]) {
        // append working value to new path
        std::vector<int> newPath = path;
        newPath.push_back(x);
        paths.push_back(newPath);
      }
    }
  } else {
    for (int x = 0; x < (*possibleCombinations)[path.size()].size(); ++x) {
      // append working value to new path
      std::vector<int> newPath = path;
      newPath.push_back(x);
      paths.push_back(newPath);
    }

  }

  return paths;
}

// Get a working branch to start with
std::vector<int> initialBranch(std::vector<std::vector<std::vector<std::vector<bool>>>> possibleCombinations, std::vector<int> base) {
  if (base.size() == possibleCombinations.size())
    return base;

  std::vector<std::vector<int>> paths = getPossiblePaths(&possibleCombinations, base);

  if (paths.size() == 0) {
    return {};
  }

  for (auto x : paths) {
    if (initialBranch(possibleCombinations, x).size() > 0) {
      return initialBranch(possibleCombinations, x);
    }
  }

  return {};
}

void gen(std::vector<std::vector<void*>> arrs, int compare(int, int), int fitness(std::vector<std::vector<void*>>*, std::vector<int>, int), bool filter(void*, void*, int, int), std::vector<gen_trim_struct*> *captured) {
  int groups = 5;
  int cycles = 100;
  int groupSize = 10;

  std::vector<std::vector<std::vector<std::vector<bool>>>> possibleCombinations;

  // Generate possibleCombinations array
  // this array contains all possible combinations of given values
  // possibleCombinations[x1][y1][x2][y2] will return true if x1,y1 and x2,y2 can exist together
  for (unsigned int i = 0; i < arrs.size(); ++i) {
    std::vector<std::vector<std::vector<bool>>> possibleOuter;
    for (unsigned int j = 0; j < arrs.at(i).size(); ++j) {
      void* curr = arrs[i][j];

      std::vector<std::vector<bool>> outer;
      for (unsigned int i2 = 0; i2 < arrs.size(); ++i2) {
        std::vector<bool> inner;
        for (unsigned int j2 = 0; j2 < arrs.at(i2).size(); ++j2) {
          inner.push_back(filter(curr, arrs[i2][j2], i, i2));
        }
        outer.push_back(inner);
        inner.clear();
      }
      possibleOuter.push_back(outer);
      outer.clear();
    }
    possibleCombinations.push_back(possibleOuter);
    possibleOuter.clear();
  }

  std::vector<std::vector<std::vector<int>>> currPathsGroup;

  if (arrs.size() == 0)
    return;

  std::vector<int> base_path = initialBranch(possibleCombinations, {});

  if (base_path.size() == 0)
    return;

  // init
  for (int x = 0; x < groups; ++x) {
    std::vector<std::vector<int>> currPaths;
    currPaths = gen_base(currPaths, base_path, groupSize);

    currPathsGroup.push_back(currPaths);
  }

  for (int cycle = 0; cycle < cycles; ++cycle) {
    // mutate
    for (int x = 0; x < groups; ++x) {
      currPathsGroup.at(x) = gen_mutate(arrs, currPathsGroup.at(x), &possibleCombinations);
    }

    /*for (auto x : currPathsGroup) {
      for (unsigned int i = 0; i < x.size(); ++i) {
        for (auto z : x.at(i)) {
          std::cout << z << ", ";
        }
      std::cout << std::endl;
      }
      std::cout << "_______________________" << std::endl;
    }*/

    // trim
    std::vector<int> endCondition;
    for (int x = 0; x < groups; ++x) {
      gen_trim_struct *topGen = gen_trim(arrs, currPathsGroup.at(x), x, compare, fitness);

      currPathsGroup.at(x).clear();
      currPathsGroup.at(x) = gen_base(currPathsGroup.at(x), topGen->top, groupSize);

      if (captured->size() == 0 || captured->back()->fitness < topGen->fitness) {
        captured->push_back(topGen);
      } else {
        delete topGen;
      }
    }

    //std::cout << std::endl;
  }
}
