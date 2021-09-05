# MUTUAL EXCLUSION IN DISTRITBUTED SYSTEM
This repository contains academia implementations for timestamps algorithms:
- Ricart-Agrawala's Algorithm.
- Maekawas Algorithm.


## Summary
- Unlike mutex in a shared memory (same OS), we can easily use a mutex (lock) object for Critical Section. In a distributed environment, we deal with mutual exclusion problem through nodes communications.
- Mutual Exclusion problem in Distributed System are a complex problem and it is unsolvable in an fail-silent model (async system). Specifically, quorum-based algorithm is a more prefer choice for solving problem in async system.


## System model
- Perfect links (reliable multicast, for example, TCP..).
- Messages are _eventually_ delivered in **FIFO** order.
- Processes do not fail (yes, there are variances can handle this, but this repo is towards the goal of education).


## Distributed system's properties
- Safety(Handling the worst situation happen in the system, essential): Make sure the Critical Section can only be accesses by one process at a time.
- Liveness(Jobs are eventually delivered, essential): Every request to the Critical Section is served eventually.
- Ordering(Desirable): Requests are granted in the order they were made.

## Performance properties
- Bandwidth: The total number of messages sent in each enter() and exit() operation.
- Client delay: The delay incurred by process at each enter() and exit() operation(when no process is in CS, or waiting).
- Synchronization delay: The time interval between one process exiting the CS and the next process entering it(when there is only one process waiting).


## Building
- Install OpenMPI: [Click here](https://www.open-mpi.org/software/ompi)
- Install _mpi4py_: [Click here](https://mpi4py.readthedocs.io/en/stable/index.html)
- Go to project directory, edit the run.sh file, change the appropriate python interpreter.
- Run the executable bash script:

```
$ ./run.sh
```


## Source
- Cloud Computing Concepts (Part 2): [Click here](https://www.coursera.org/learn/cloud-computing-2/lecture/Fm2qB/2-1-introduction-and-basics)
- More algorithms(can handle nodes failure) and explanation: [Click here](https://www.cs.uic.edu/~ajayk/Chapter9.pdf)
