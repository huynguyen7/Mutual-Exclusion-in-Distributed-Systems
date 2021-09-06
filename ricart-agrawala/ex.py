from mpi4py import MPI


"""

    @author: Huy Nguyen
    - Source: 
        +https://www.coursera.org/learn/cloud-computing-2/lecture/51kBv/2-3-ricart-agrawalas-algorithm

    - Let's assume we have reliable unicast for this implementation.

    - We have 2 types of msg: REPLY and REQUEST messages in this algorithm.
        +REPLY_MSG = 'ACK'
        +REQUEST_MSG = (T_i, P_i) where T_i is the local Lamport's timestamp, and P_i is the process id.

"""


# MPI Communications.
COMM_WORLD = MPI.COMM_WORLD
my_rank = COMM_WORLD.Get_rank()  # Process's rank in COMM_WORLD.
size = COMM_WORLD.Get_size()  # COMM_WORLD's size.

# ID of each process (correspond to MPI process id). <Process ID: MPI rank>, just to make it look like the example.
MPI_rank_to_group_ID = {80:0, 6:1, 12:2, 3:3, 32:4, 5:5}
MPI_ranks = [0,1,2,3,4,5]
group_IDs = [80,6,12,3,32,5]
my_ID = group_IDs[my_rank]

# Communication params.
TAG = 0  # Default tag.
LOCAL_COUNTER = 'lc'  # Key for messaging.
MSG = 'msg'  # Key for messaging.
REPLY_MSG = 'ACK'

# Algorithm's params
RELEASED, WANTED, HELD = 0,1,2
state = RELEASED  # Default state as RELEASED.
local_queue = []  # Storing request msg.
local_counter = 0  # Clock, init as 0, used for Lamport's timestamps.
num_replies = 0


def unicast(msg=None, dest=None):  # Send msg to a defined rank's process in Lamport's environment.
    assert dest is not None

    global local_counter
    #local_counter += 1
    data = {LOCAL_COUNTER: local_counter, MSG: msg}
    COMM_WORLD.isend(data, dest=dest, tag=TAG)  # Non-blocking op.


def multicast(msg=None, group=None):  # Multicast msg in Lamport's environment.
    assert group is not None

    global local_counter, my_rank
    #local_counter += 1
    data = {LOCAL_COUNTER: local_counter, MSG: msg}

    for rank in MPI_ranks:
        if my_rank != rank:
            COMM_WORLD.isend(data, dest=rank, tag=TAG)  # Non-blocking op.


def instruction(job, *args):  # Passing a lambda or a predefined function, then its params to run the job in Lamport's environment.
    assert job is not None

    global local_counter
    local_counter += 1
    return job(*args)


def recv_any():  # Receive msg in Lamport's environment.
    stt = MPI.Status()
    data = COMM_WORLD.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=stt)  # Blocking op.

    global local_counter
    #local_counter = max(local_counter, data[LOCAL_COUNTER])+1
    local_counter = max(local_counter, data[LOCAL_COUNTER])
    return (stt.Get_source(), data)


def recv_request_msg(source=None, msg=None):
    if msg == None:
        (source, msg) = recv_any()

    global state, local_counter, my_rank, my_ID
    assert msg != REPLY_MSG, f'[Process {my_ID}] Not a REQUEST MSG.'

    #print(f'[Process {my_ID}]\t{str((local_counter,my_ID))} {str(msg[MSG])}')
    if state == HELD or (state == WANTED and (local_counter, my_ID) < msg[MSG]):
        local_queue.append(source)  # Queue the request.
    else:
        unicast(REPLY_MSG, dest=source)


def ra_exit():  # Ricart-Agrawala's exit()
    global state
    # Change state to RELEASED and Reply to all queued MSGs.
    state = RELEASED
    local_queue_size = len(local_queue)
    while local_queue_size != 0:
        rank = local_queue.pop(0)
        unicast(REPLY_MSG, dest=rank)
        local_queue_size -= 1


def ra_enter(critical_section, *args):  # Ricart-Agrawala's enter()
    assert critical_section is not None

    global state, local_counter, my_rank, my_ID, num_replies

    state = WANTED  # Set current state to WANTED.

    # Multicast message (ask for entering).
    request_msg = (local_counter, my_ID)  # Request message.
    multicast(request_msg, group=MPI_ranks)

    # Wait until all other processes reply.
    # NOTES: This could cause a a whole cluster to stop if the process does not receive enough REPLY_MSG.
    while num_replies < size-1:  # Process does not send msg to itself.
        (source, recv_msg) = recv_any()
        #(_, recv_msg) = recv_any()
        if recv_msg[MSG] == REPLY_MSG:
            num_replies += 1
        else:
            recv_request_msg(source, msg=recv_msg)
        #print(f'[Process {my_ID}] src:{group_IDs[source]} {str(recv_msg)} num_repl {num_replies}')
    num_replies = 0
    
    # Change state to HELD and execute Critical Section.
    state = HELD
    job_result = instruction(critical_section, *args)

    #print(f'[Process {my_ID}] {str(local_queue)}')
    
    # DONE Critical Section.
    ra_exit()
    return job_result

''' MAIN '''
def example():

    # Critical section for testing.
    from time import sleep
    def critical_section():
        print('[Process %d] Entered critical section.' % my_ID)
        sleep(1)
        print('[Process %d] Exited critical section.' % my_ID)

    if my_ID == 80:
        ra_enter(critical_section)
    elif my_ID == 6:
        recv_request_msg()
        recv_request_msg()
    elif my_ID == 12:
        ra_enter(critical_section)
    elif my_ID == 3:
        recv_request_msg()
        recv_request_msg()
    elif my_ID == 32:
        recv_request_msg()
        recv_request_msg()
    elif my_ID == 5:
        recv_request_msg()
        recv_request_msg()


if __name__ == "__main__":
    example()
