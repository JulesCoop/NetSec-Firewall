import heapq

#indexes of the priority and the rule inside the list in the questions dictionary
P_INDEX = 0
R_INDEX = 2

#some questions do not have rules for them
def validId(id):
    """To check if a question with a specific id has a 
    corresponding rule or not.

    Args:
        id (str): id of the question
    """
    if id not in ["experienced", "server_exp"]:
        return True
    return False


def to_string_format(questions_dict, answers_dict):
    """To convert the answers into the string 
    that will be written to the file.

    Args:
        questions_dict (dict): dictionary with the questions 
                ids, the questions and their corresponding rules
        answers_dict (dict) : dictionary with booleans for each question id
    """
    #1. always the same initial part
    final_string = "#iptables firewall implementation\n*filter\n\
:INPUT DROP [0:0]\n:FORWARD ACCEPT [0:0]\n:OUTPUT ACCEPT [0:0]"

    #2. add all the rules in order

    #go through the answers and SORT THEM in a priority queue
    pq = [] #new list to heapify
    for id in answers_dict.keys():
        if validId(id) and answers_dict[id]: #if the answer is yes
            #add PRIORITY and RULE to pq (as a tuple)
            heapq.heappush(pq, (questions_dict[id][P_INDEX], questions_dict[id][R_INDEX]))
    
    #go through the sorted list to add the rules in the right order
    for i in range(len(pq)):
        final_string += heapq.heappop(pq)[R_INDEX]
    

    #3. commit
    final_string += "COMMIT"

    return final_string

