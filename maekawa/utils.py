from mpi4py import MPI
from comm_params import *

# MPI Communications.
COMM_WORLD = MPI.COMM_WORLD
my_rank = COMM_WORLD.Get_rank()  # Process's rank in COMM_WORLD.
size = COMM_WORLD.Get_size()  # COMM_WORLD's size.

# Communication params.
TAG = 0  # Default tag.
ROOT = 0  # Root's rank, just for logging information.


def unicast(dest, msg):  # Non-blocking send.
    assert dest is not None or isinstance(dest, int), f'[Process {my_rank}] Invalid unicast dest.'

    COMM_WORLD.isend(msg, dest=dest, tag=TAG)


def multicast(group, msg):
    assert group is not None or len(group) != 0, f'[Process {my_rank}] empty group multicast.'
    for rank in group:
        COMM_WORLD.isend(msg, dest=rank, tag=TAG)  # Non-blocking send.


def recv_any():  # Receive msg in a standard blocking way.
    stt = MPI.Status()
    data = COMM_WORLD.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=stt)  # Blocking op.

    return (stt.Get_source(), data)


def init_voting_set(size):
    voting_set = set()
    # Creating 2D Cartesian grid for graph topology.
    dims = MPI.Compute_dims(size, 2)  # Uniformly partition to 2D Cart grid.
    grid = [[0 for i in range(dims[0])] for j in range(dims[1])]
    val = 0
    for i in range(dims[1]):
        for j in range(dims[0]):
            grid[i][j] = val
            val += 1

    my_row = int(my_rank / dims[0])
    my_col = my_rank % dims[0]

    # Add neighbor's ID to voting_set.
    for val in grid[my_row]:
        #voting_set.add(val)
        if val != my_rank:
            voting_set.add(val)
    for i in range(dims[1]):
        #voting_set.add(grid[i][my_col])
        if grid[i][my_col] != my_rank:
            voting_set.add(grid[i][my_col])

    return voting_set
