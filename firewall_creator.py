import json
import io
import argparse
from datetime import datetime
import os

data_answers = {}


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


#TODO
def enable_firewall(fileName):
    pass




def cancel(tmp_file):
    """Operation called after a call to get_answer_yes_or_no
        It will delete the file and exit the program

    Args:
        tmp_file (str): file_name to remove from device
    """
    os.remove(tmp_file)
    exit(0)



# available commands / functionnality:
    # load / create firewall implementation
def main(args):
   
    # creating the default output files based on the timestamp
    current_time = datetime.now()
    # put the time in string format
    timestamp = current_time.strftime("%d-%m-%Y_%S-%M-%H")

    output_file = "rules_" + timestamp + ".txt"
    js_output_file = "questions_rules" + timestamp + ".js"

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
        

    # load existing rules
    if args.action == "load":
        question_dic = read_js_to_file(args.file)
    # new answers for the questions
    new_question_dic = {}


    # create new rules / modify the previous
    #---------------------- exemples -------------------
    # server / client
    question = "are you a server?"
    key = "server"
    prev_answer = question_dic[key] if key in question_dic.keys() else None

    # ask question and get the answer
    response = get_answer_yes_no(question, prev_answer)
    if (response == None):
        exit(0)
    new_question_dic[key] = response


    # server questions
    if response == True:
        write_to_file(tmp_file, "server rules")


        question = "http server?"
        key = "http_server"
        prev_answer = question_dic[key] if key in question_dic.keys() else None
        
        response = get_answer_yes_no(question, prev_answer)
        if (response == None):
            cancel(tmp_file)
        new_question_dic[key] = response
        
        if response == True:
            write_to_file(tmp_file, "http server rules")
        else:
            write_to_file(tmp_file, "block http server rules")


    else:
        write_to_file(tmp_file, "client rules")

        question = "ssh access?"
        key = "ssh_access"
        prev_answer = question_dic[key] if key in question_dic.keys() else None
        
        response = get_answer_yes_no(question, prev_answer)
        if (response == None):
            cancel(tmp_file)
        new_question_dic[key] = response
        
        if response == True:
            write_to_file(tmp_file, "ssh server rules")
        else:
            write_to_file(tmp_file, "block ssh server rules")     



    # rename the tmp_file to the real output one
    os.rename(tmp_file, output_file)

    # empty the file of it's previous content
    with open(js_output_file, 'w') as file:
        pass

    write_js_to_file(js_output_file, new_question_dic)
        



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