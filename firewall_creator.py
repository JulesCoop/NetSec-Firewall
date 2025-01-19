import json
import io
import argparse
from datetime import datetime
import os



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


# ------------------------------------------------------------------------
# file input - output

def write_to_file(fileName, data):
    """Write to a file that exists or not
        If the file doesn't exists it's created
        If it does then the data is appended to it
    Args:
        fileName (String): name of the file
        data (String): data to write to the file
    """
    # create file if doesn't exist and appends to it otherwise
    f = open(fileName, "a+")
    f.write(data)
    f.write("\n")
    f.close()


def write_js_to_file(fileName, data):
    """Write a json formated data to a file that exists or not
        If the file doesn't exists it's created
        If it does then the data is appended to it
    Args:
        fileName (String): name of the file
        data (dict): data to write to the file, this data is a json format
    """
    with io.open(fileName, 'a+', encoding='utf8') as outfile:
        json.dump(data, outfile, indent=4)
    

def read_js_to_file(filename):
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




def cancel(tmp_file):
    """Operation called after a call to get_answer_yes_or_no
        It will delete the file and exit the program

    Args:
        tmp_file (str): file_name to remove from device
    """
    if os.path.exists(tmp_file):
        os.remove(tmp_file)
    exit(0)




question_dict = {
    "experienced": ["Are you comfortable with network terminology ?"],
    
    # no experience questions
    "public_no_exp": [1, "Are you on a public network?", "TODO RULE"],
    "webserver_no_exp": [2, "Will you host a webserver?", "TODO RULE"],
    "ssh_no_exp": [3, "Do you need to connect to this device from another device?", "TODO RULE"],

    # experience questions
    "server_exp": ["Will the device host services ?\n If yes answer each number seperated by a space character\nEnter for nothing\n1. SSH\n2. FTP\n3. HTTP\n4. HTTPs", "ssh_exp", "ftp_exp", "http_exp", "https_exp"],
    "ssh_exp": [1, "SSH", "TODO RULE"],
    "ftp_exp":[2, "FTP", "TODO RULE"],
    "http_exp": [3, "HTTP", "TODO RULE"],
    "https_exp": [4, "HTTPS", "TODO RULE"],
}




# available commands / functionnality:
    # load / create firewall implementation
def main(args):
   
    # creating the default output files based on the timestamp
    current_time = datetime.now()
    # put the time in string format
    timestamp = current_time.strftime("%d-%m-%Y_%H-%M-%S")

    output_file = "rules_" + timestamp + ".txt"
    js_output_file = "questions_rules" + timestamp + ".js"
    tmp_file = "tmp_" + timestamp + ".txt"

    # if the output file is already specified
    if args.output:
        output_file = args.output
        # get the output name and remove the extension to add the new js one
        js_output_file = "questions_" + args.output.split(".", 1)[0] + ".js"

        # tmp_file
        tmp_file = "tmp_" + args.output

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
        prev_answer_dict = read_js_to_file(args.file)



    # create new rules / modify the previous
    experience_response = get_answer_yes_no(question_dict["experienced"][0], prev_answer_dict.get("experienced"))
    answers_dict["experienced"] = experience_response

    # experience questions
    if experience_response == True:
        
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
            cancel(tmp_file)

        for num in resp_answer_multiple_choice:
            if num != 0:
                answers_dict[question_dict["server_exp"][num]] = True



    # inexperience questions
    else :
        resp = get_answer_yes_no(question_dict["public_no_exp"][1], prev_answer_dict.get("public_no_exp"))
        answers_dict["public_no_exp"] = resp
        if (resp == None):
            cancel(tmp_file)

        resp = get_answer_yes_no(question_dict["webserver_no_exp"][1], prev_answer_dict.get("webserver_no_exp"))
        answers_dict["webserver_no_exp"] = resp
        if (resp == None):
            cancel(tmp_file)

        resp = get_answer_yes_no(question_dict["ssh_no_exp"][1], prev_answer_dict.get("ssh_no_exp"))
        answers_dict["ssh_no_exp"] = resp
        if (resp == None):
            cancel(tmp_file)
    


    # rename the tmp_file to the real output one
    if os.path.exists(tmp_file):
        os.rename(tmp_file, output_file)

    # empty the file of it's previous content
    with open(js_output_file, 'w') as file:
        pass

    write_js_to_file(js_output_file, answers_dict)
        



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
    parser.add_argument("--file", "-f", type=str, help="Name of the file to load: must be the question_....js file")
    args = parser.parse_args()

    # check the load conditions
    if args.action == "load" and not args.file:
        parser.error("--action requires --file to be specified.")
    # check the args.file is a file
    if args.action == "load" and args.file and not os.path.isfile(args.file):
        parser.error("--file/-f argument must be the name of a file")


    # call to the main code
    main(args)