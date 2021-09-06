from maekawa import maekawa_enter, wait_for_votes, my_rank


"""

    @author: Huy Nguyen
    - Source: 
        +https://www.coursera.org/learn/cloud-computing-2/lecture/GMHYN/2-4-maekawas-algorithm-and-wrap-up

    - Let's assume we have reliable unicast for this implementation.
    - i := my_rank
    - Explanation about voting_set: A voting set V_i contains its own ID P_i and the row, the column contain the P_i from the 2D Cartesian topo.

"""


''' TESTING EXAMPLE '''
def example():
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
    example()

