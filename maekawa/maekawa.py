from utils import *


# Algorithm params.
N = size  # Number of nodes in cluster.
state = State.RELEASED  # Default state init as RELEASED.
voted = False
voting_set = init_voting_set(N)  # A set contains reachable processes ID from current process.
local_queue = []  # Storing REQUEST MSGs.
#print(f'[Process {my_rank}] {str(voting_set)}')


def recv_request_msg(source, msg=None):  # Receive REQUEST MSG.
    if msg is None:
        (source, msg) = recv_any()
    assert source is not None
    assert msg == Message.REQUEST, f'[Process {my_rank}] Not a REQUEST MSG.'
    global state, voted
    
    if voted or state == State.HELD:  # If already voted or in Critical Section.
        local_queue.append(source)
    else:  # Send reply back and set voted to True.
        unicast(dest=source, msg=Message.REPLY)
        voted = True


def maekawa_exit():
    global state, voted
    state = State.RELEASED

    # Multicast RELEASE MSGs to all processes in voting set V_i.
    multicast(group=voting_set, msg=Message.RELEASE)

    if len(local_queue) != 0:
        rank = local_queue.pop(0)
        unicast(rank, Message.REPLY)
        voted = True
    else:
        voted = False


def maekawa_enter(critical_section, *args):
    assert critical_section is not None

    global state, voted
    state = State.WANTED

    # Multicast REQUEST MSGs to all processes in voting set V_i.
    multicast(group=voting_set, msg=Message.REQUEST)

    # Wait for REPLY MSGs from all processes in voting set V_i.
    num_replies = 0
    voted = True
    while num_replies < len(voting_set):
        (source, recv_msg) = recv_any()
        if recv_msg == Message.REPLY:
            #print(f'[Process {my_rank}] {source}')
            num_replies += 1
        elif recv_msg == Message.REQUEST:
            recv_request_msg(source, recv_msg)


    # Set state to HELD and enter Critical Section.
    state = State.HELD
    job_result = critical_section(*args)

    # Exit Critical Section.
    maekawa_exit()

    return job_result


def wait_for_votes(times=2):
    global state, voted
    for i in range(times):
        (source, recv_msg) = recv_any()
        if recv_msg == Message.REQUEST:
            recv_request_msg(source, recv_msg)
        elif recv_msg == Message.RELEASE:
            if len(local_queue) == 0:
                voted = False
            else:
                rank = local_queue.pop(0)
                unicast(rank, Message.REPLY)
                voted = True


def test():
    # Critical section, just for testing purpose.
    from time import sleep
    def critical_section():
        print(f'[Process {my_rank}] Entered the CS.')
        sleep(1)
        print(f'[Process {my_rank}] Exited the CS.')
    
    '''
    The number of wait_for_vote() for the process if that process does not send request for Critical Section, is equal to the total number of maekawa_enter() of all other processes.
    '''

    if my_rank == 0:
        maekawa_enter(critical_section)
        maekawa_enter(critical_section)
    elif my_rank == 1:
        wait_for_votes()
        wait_for_votes()
        wait_for_votes()
    elif my_rank == 2:
        wait_for_votes()
        wait_for_votes()
        wait_for_votes()
    elif my_rank == 3:
        maekawa_enter(critical_section)
    

if __name__ == "__main__":
    test()
