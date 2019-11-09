#include <stdlib.h>     /* srand, rand */
#include <time.h>       /* time */
#include <math.h>

#include <iostream>
#include <string>
#include <vector>

struct gen_trim_struct {
  std::vector<int> top;
  int fitness;
};

void gen(std::vector<std::vector<void*>> arrs, int compare(int, int), int fitness(std::vector<std::vector<void*>>*, std::vector<int>, int), bool filter(void*, void*, int, int), std::vector<gen_trim_struct*> *captured);
