## Montecarlo randomization + Genetic Algorithm
- Find optimal paths given a fitness function, compare function,  and filter function
- Optimized for high memory usage and fast completion time
___

### What is this?
- This is an algorithm for finding optimimal 'paths' given constraints
- For example:
```
0,1,2,5
0,1,1,3
0,0,2,3
-1,1,2,3
```
- Given this, we can write a fitness function to optimize for highest value, and a restriction that the values must be descending
- The optimal path here would be `3, 3, 2, 1`
- This optimal path would have a fitness value of `5+3+2+1` or `11`
___
### How does it work?
- This uses a combination of Montecarlo Randomization and genetic algorithms to find an optimal path.
- Filters are calculated and stored before the genetic algorithm is run to save time
- A working path is found through bruteforce to use as the original parent for all groups
- Children are have slight variations from parent
- Best child is chosen to become a parent
___
### Uses
- I plan to implement this in my course scheduling algorithm to decrease schedule generation times to under 1 second, and to reduce memory usage
___
### Learn More
http://beta.aceparent.me/#/montecarlotree
