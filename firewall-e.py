import json
import io
import argparse
from datetime import datetime
import os
import ipaddress
import heapq



def get_answer_yes_no(question, last_value):
    """Gets the answers to a input field and parses it to a True/False/None variable

    Args:
        question (String): a question
        last_value (String): previous answer/None if not set

    Returns:
        Boolean: True if answer was yes/y and False if it was no/n, None if it was cancel/c
    """

    print(question)
    # prints the last value
    if last_value != None:
        print("Previous answer: " + str(last_value))
    resp = input("")
    
    # infinite loop until the response matches the desired format
    while (resp.lower() not in ["yes", "y", "no", "n", "cancel", "c"]):
        print("The answer must be of form, \"yes\", \"y\", \"no\", \"n\", \"cancel\", \"c\"")
        print(question)
        # prints the last value
        if last_value != None:
            print("Previous answer: " + str(last_value))
        resp = input("")

    if resp.lower() in ["yes", "y"]:
        arg = True
    elif resp.lower() in ["no", "n"]:
        arg = False
    else:
        arg = None
    return arg


def get_answer_multiple_number(question, last_value, allowed_numbers):
    """Gets the answers to a input field and parses it to a list of number variable

    Args:
        question (String): a question
        last_value (list): previous answer/None if not set

    Returns:
        list: A list of unique numbers, None if it was cancel/c
    """
    print(question)
    if (last_value != None and last_value !=[]):
        print("Previous answer: " + str(last_value))
    resp = input("")
    
    # infinite loop
    while True:
        if (resp.lower() == "cancel" or resp.lower() == "c"):
            return None

        # if the response doesn't digital characters or space
        if all(part.isdigit() for part in resp.split()):
            resp_list = list(map(int, resp.split()))
            # if the response doesn't have repeated numbers/digits
            if len(resp_list) == len(set(resp_list)):
                # if the response has valid numbers/digits
                if all(allowed_number in allowed_numbers for allowed_number in resp_list):
                    #exit the loop
                    break
        else:
            print("no match")

        print("The answer must be of form, \"cancel\",\"c\" or \"x y z...\", where x y and z are valid numbers and no numbers are repeated")
        print(question)
        if (last_value != None and last_value !=[]):
            print("Previous answer: " + str(last_value))
        resp = input("")
    
    # converts a list of string to a list of integer
    return list(map(int, resp.split()))


def get_ip_list(question, last_value):
    """Gets the answers to a input field and parses it to a list of ips

    Args:
        question (String): a question
        last_value (list): previous answer/None if not set

    Returns:
        list: A list of ips, None if it was cancel/c
    """

    print(question)
    if (last_value != None and last_value !=[]):
        print("Previous answer: " + str(last_value))
    resp = input("")

    iplist = []
    while(resp != ""):

        try:
            # Try to create an IP address object
            ipaddress.ip_address(resp)
            iplist.append(resp)
        except:
            if (resp.lower() == "cancel" or resp.lower() == "c"):
                return None
            
            print("The Ip address isn't valid or isn't in the right format. Please enter it again.")

        resp = input("")

    return iplist

# ------------------------------------------------------------------------
# file input - output

def write_to_file(fileName, data):
    """Write to a file that exists or not
        If the file doesn't exists it's created
        If it does then the data is written to it
    Args:
        fileName (String): name of the file
        data (String): data to write to the file
    """
    f = open(fileName, "w")
    f.write(data)
    f.write("\n")
    f.close()


def write_json_to_file(fileName, data):
    """Write a json formated data to a file that exists or not
        If the file doesn't exists it's created
        If it does then the data is appended to it
    Args:
        fileName (String): name of the file
        data (dict): data to write to the file, this data is a json format
    """
    with io.open(fileName, 'w', encoding='utf8') as outfile:
        json.dump(data, outfile, indent=4)
    

def read_json_to_file(filename):
    """Reads the content of a json file and saves the data onto a variable

    Args:
        filename (String): name of the file

    Raises:
        ValueError: JSON file isn't correctly formated

    Returns:
        Dict: JSON data represented as a dict
    """
    with open(filename, 'r') as file:
        data = json.load(file)
        if not isinstance(data, dict):
            raise ValueError("JSON file isn't correctly formated")

    return data


# ------------------------------------------------------------------------
# Format related functions

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
:INPUT DROP [0:0]\n:FORWARD ACCEPT [0:0]\n:OUTPUT ACCEPT [0:0]\n"

    #2. add all the rules in order

    #rule that always goes first:
    final_string += "-A INPUT -i lo -j ACCEPT\n"

    #go through the answers and SORT THEM in a priority queue
    pq = [] #new list to heapify
    for id in answers_dict.keys():
        if validId(id) and answers_dict[id]: #if the answer is yes
            #add PRIORITY and RULE to pq (as a tuple)
            heapq.heappush(pq, (questions_dict[id][P_INDEX], questions_dict[id][R_INDEX]))
    
    #go through the sorted list to add the rules in the right order
    for i in range(len(pq)):
        final_string += heapq.heappop(pq)[1]
        final_string += "\n"    
    

    #rule that always goes last:
    final_string += "-A INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT\n"
    #3. commit
    final_string += "\nCOMMIT"

    return final_string



#-------------------------------------------------------------------------



question_dict = {
    "experienced": ["Are you comfortable with network terminology ?"],
    
    # no experience questions
    "public_no_exp": [1, "Are you on a public network?", "-A OUTPUT -p tcp -m tcp --dport 80 -j DROP "],
    "server_no_exp": [2, "Should this device be accessible online by other people?", "-A INPUT -p icmp -m icmp --icmp-type 8 -m limit --limit 1/sec --limit-burst 10 -j ACCEPT\n-A INPUT -p icmp -m icmp --icmp-type 8 -j DROP\n-A INPUT -p icmp -j ACCEPT"],
    "webserver_no_exp": [3, "Will you host a webserver?", "-A INPUT -p tcp -m tcp --dport 80 -j ACCEPT\n-A INPUT -p tcp -m tcp --dport 443 -j ACCEPT"],
    "ssh_no_exp": [4, "Do you need to connect to this device from another device?", "-A INPUT -p tcp -m tcp --dport 22 -m conntrack --ctstate NEW -j ACCEPT "],

    # experience questions
    "services_exp": [0, "Will the device host services?", "-A INPUT -p icmp -m icmp --icmp-type 8 -m limit --limit 1/sec --limit-burst 10 -j ACCEPT\n-A INPUT -p icmp -m icmp --icmp-type 8 -j DROP\n-A INPUT -p icmp -j ACCEPT"],
    "server_exp": ["Which services will it host ?\n Answer each number seperated by a space character if multiple services are hosted\nEnter for nothing\n1. SSH\n2. FTP\n3. HTTP\n4. HTTPs", "ssh_exp", "ftp_exp", "http_exp", "https_exp"],
    "ssh_exp": [1, "SSH", "-A INPUT -p tcp -m tcp --dport 22 -m conntrack --ctstate NEW -j ACCEPT "],
    "ftp_exp":[2, "FTP", ""],
    "http_exp": [3, "HTTP", "-A INPUT -p tcp -m tcp --dport 80 -j ACCEPT"],
    "https_exp": [4, "HTTPS", "-A INPUT -p tcp -m tcp --dport 443 -j ACCEPT"],
    "ftp_ips": [5, "Which Ip's is your FTP server going to communicate with?", ""],
    "blocked_ips": [6, "Which Ip's do you wish to block all incoming traffic from?\nIf none enter nothing", ""]
}




# available commands / functionnality:
    # load / create firewall implementation
def main(args):
   
    # creating the default output files based on the timestamp
    current_time = datetime.now()
    # put the time in string format
    timestamp = current_time.strftime("%d-%m-%Y_%H-%M-%S")

    output_file = "rules_" + timestamp + ".txt"
    json_output_file = "questions_rules" + timestamp + ".json"

    # if the output file is already specified
    if args.output:
        output_file = args.output
        # get the output name and remove the extension to add the new json one
        json_output_file = "questions_" + args.output.split(".", 1)[0] + ".json"


        # file already exists check if want to overwrite
        if os.path.isfile(args.output):
            overwrite = get_answer_yes_no("A file named " + args.output + " already exists, do you want to overwrite it?", None)
            if overwrite == False or overwrite == None:
                exit(0)
    
    # new answers for the questions
    answers_dict = {}
    prev_answer_dict = {}
    # load existing rules
    if args.action == "load":
        prev_answer_dict = read_json_to_file(args.file)

    # Welcome text
    print("****** Welcome to FireWALL-E ******")
    print("Unless instructed otherwise, answer the questions with 'yes'/'y', or 'no'/'n'")
    print("You can also cancel with 'cancel' or 'c'")
    print("---------------\n")

    # create new rules / modify the previous
    experience_response = get_answer_yes_no(question_dict["experienced"][0], prev_answer_dict.get("experienced"))
    answers_dict["experienced"] = experience_response

    # experience questions
    if experience_response == True:
        
        resp = get_answer_yes_no(question_dict["services_exp"][1], prev_answer_dict.get("services_exp"))
        answers_dict["services_exp"] = resp
        if (resp == None):
            exit(0)
        
        # The device will act as a server
        if (resp == True):
            # loads the previous answers as a list of strings
            prev_answer_multiple_choice = []
            # check through all the options of the questions
            for k in ["ssh_exp", "ftp_exp", "http_exp", "https_exp"]:
                prev = prev_answer_dict.get(k)
                if prev == True:
                    # appends the name of the "rule" to the list (SSH, FTP, HTTP or HTTPS)
                    prev_answer_multiple_choice.append(question_dict[k][1])
            
            resp_answer_multiple_choice = get_answer_multiple_number(question_dict["server_exp"][0], prev_answer_multiple_choice, [0, 1, 2, 3, 4])
            if (resp_answer_multiple_choice == None):
                exit(0)

            for num in resp_answer_multiple_choice:
                if num != 0:
                    answers_dict[question_dict["server_exp"][num]] = True

            # ask which ip the server is going to communicate with
            if answers_dict.get("ftp_exp") != None:
                ip_list = get_ip_list(question_dict["ftp_ips"][1], prev_answer_dict.get("ftp_ips"))
                answers_dict["ftp_ips"] = ip_list

                final_rule = ""
                for ip in ip_list:
                    final_rule +="-A INPUT -s " + ip + " -p tcp -m tcp --dport 20 -j ACCEPT\n"
                    final_rule +="-A INPUT -s " + ip + " -p tcp -m tcp --dport 21 -j ACCEPT\n"

                # adding the final rule to the questions
                question_dict["ftp_ips"][2] = final_rule[:-1]


        
        #block all ip's desired
        ip_list = get_ip_list(question_dict["blocked_ips"][1], prev_answer_dict.get("blocked_ips"))
        answers_dict["blocked_ips"] = ip_list

        final_rule = ""
        for ip in ip_list:
            final_rule +="-A INPUT -s " + ip + " -j DROP\n"

        # adding the final rule to the questions
        question_dict["blocked_ips"][2] = final_rule[:-1]

    # inexperience questions
    else :
        resp = get_answer_yes_no(question_dict["public_no_exp"][1], prev_answer_dict.get("public_no_exp"))
        answers_dict["public_no_exp"] = resp
        if (resp == None):
            exit(0)


        resp = get_answer_yes_no(question_dict["server_no_exp"][1], prev_answer_dict.get("server_no_exp"))
        answers_dict["server_no_exp"] = resp
        if (resp == None):
            exit(0)

        resp = get_answer_yes_no(question_dict["webserver_no_exp"][1], prev_answer_dict.get("webserver_no_exp"))
        answers_dict["webserver_no_exp"] = resp
        if (resp == None):
            exit(0)


        resp = get_answer_yes_no(question_dict["ssh_no_exp"][1], prev_answer_dict.get("ssh_no_exp"))
        answers_dict["ssh_no_exp"] = resp
        if (resp == None):
            exit(0)

    # writes the answers to questions to a json file
    write_json_to_file(json_output_file, answers_dict)
    
    write_to_file(output_file ,to_string_format(question_dict, answers_dict))

    print("-----------------")
    print("The rules have been created and stored in",output_file)
    print("Run 'sudo iptables-restore",output_file,"'to apply them.")


if __name__ == "__main__":
    # parsing the options before the call to code

    parser = argparse.ArgumentParser(
        description = """Program to simplify the creation of firewall rules.
The program has two modes, create a new set of rules, or to load and modify an old one.
The default mode performed by the program is to create a new set of rules.
""",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("--action", "-a", choices=["create", "load"], help="Action to perform on the file.")
    parser.add_argument("--output", "-o", type=str, help="Name of the file to create")
    parser.add_argument("--file", "-f", type=str, help="Name of the file to load: must be the question_....json file")
    args = parser.parse_args()

    # check the load conditions
    if args.action == "load" and not args.file:
        parser.error("--action requires --file to be specified.")
    # check the args.file is a file
    if args.action == "load" and args.file and not os.path.isfile(args.file):
        parser.error("--file/-f argument must be the name of a file")


    # call to the main code
    main(args)