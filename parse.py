import re
from validation import *
from tinydb import TinyDB, Query
from season import *

db = TinyDB('db.json')
q = Query()

def parse_input(input):
      """
      Captures any args before flags.
      
      Then captures flags and respective arguments in dictionary key-val pairs.
      
      Param:
      input -- input from user
    
      Return:
      parsed_input -- dictionary in the form {flag: argument}
      """
      if input == "":
          print("At least one positional argument or flag is required. Type 'help' for more info.")
          return False
      
      # First split input into positional args and flags
      split_input = re.split(r"(?=-|$)", input, maxsplit=1)
      positional_args = split_input[0].strip().split(" ") # List of positional args
      raw_flags = split_input[1].strip()
      
      # Get flags and corresponding args
      pattern = r'(-[a-z]|--[a-z]+)\s+(.*?)(?=(?:-[a-z]|--[a-z]+)\s+|$)'
      results = re.findall(pattern, raw_flags)
      
      # Add key-val flag-args to dictionary
      parsed_flags = {}
      for tuple in results:
            flag = tuple[0].strip()
            raw_args = tuple[1]
            # Pattern to find words starting with +, -, " ", or at the start of the string
            # that are either wrapped in "" or not
            # pattern = r'([+\-\s]|^)(?:"([^"]+)"|(\S+))'
            pattern = r'([+-])?"([^"]+)"|([+-])?(\S+)'
            # Capture args grouped by " "
            matches = re.findall(pattern, raw_args)
            refined_args = []
            for match in matches:
                # Join all the matched groups (e.g. +, orange, '')
                joined = "".join(match).strip()
                refined_args.append(joined)
            parsed_flags[flag] = refined_args
      return positional_args, parsed_flags


def parse_flags(line):
    """
    Converts raw user input into list of tuples for validation.
    
    Param:
    line -- line input by user
    
    Return:
    False -- if 
    List of tuples in the form (flag, argument)
    """
    
    # Split line to get flags and their corresponding arguments
    cmds = re.findall(r'-*[a-z]*\s"?[a-z0-9"?\s]*', line)
    
    print("cmds from parse flags", cmds)
    
    if len(cmds) < 1:
        print("Argument/s required for flag/s.")
        return False
    
    # Initialise list to store flags + corresponding arguments
    list_cmds = []
    
    # Group flags and their respective arguments in tuples
    for cmd in cmds:
        cmd.strip()
        flag = re.findall(r'-{1,2}[a-z]*', cmd)
        input_args = re.findall(r'(?<=\s)(\"[^\"]*\"|\w+)(?=\s|$)', cmd)
        args = []
        for arg in input_args:
            stripped_arg = arg.strip("\"")
            args.append(stripped_arg)
        list_cmds.append((flag, args))
        
    return list_cmds


def parse_show(line, allowed_positional, allowed_flags):
    """
    TODO: Refactor match statements.
    
    Generates a TinyDB query based on provided arguments.
    
    Params:
    line -- raw input from user
    allowed_positional -- allowed positional arguments
    allowed_flags -- allowed flags
    
    Return:
    False -- if provided arguments are invalid
    query -- query for searching db based on provided args   
    """
    query = None # Query to be built upon
    exact = False # Whether or not exact matches are preferred (e.g. taste: sweet AND savoury, not sweet OR savoury)
    is_name_query = False
    show_all = False
    
    if line == "":
        print("At least one argument is required. Type 'help show' for more info.")
        return False
    
    # Split into positional and flags 
    split_line = re.split(r"(?=-)", line, maxsplit=1)
    positional_args = split_line[0].strip().split(" ") # List of positional args
    # Check provided positional args are allowed
    for arg in positional_args:
        if arg not in allowed_positional and arg != '':
            print(f"Invalid positional argument: {arg}")
            return False
    
    # Handle "show all" case
    if len(split_line) == 1:        
        if positional_args[0] == "all":
            show_all = True
            return query, is_name_query, show_all
        
    # Handle other positional args
    for arg in positional_args:
        match arg:
            case "seasonal":
                if query is None:
                    query = q.season.test(is_in_season)
                else:
                    query &= q.season.test(is_in_season)
            case "favs":
                if query is None:
                    query = q.favourite == 'y'
                else:
                    query &= q.favourite == 'y'
            case "exact":
                exact = True      
            
    # Check if flags were provided
    if len(split_line) > 1:
        flag_cmds = parse_flags(split_line[1])
        # Check provided flags are valid
        if flag_cmds:
            if not flag_cmds or not valid_flags(flag_cmds, [], allowed_flags):
                return False 
        else:
            return False 
        
        for cmd in flag_cmds:
            flag = cmd[0][0]       
            match flag:
                case "-n":
                    # Return early with query
                    # If user searches for a name, other arguments are ignored
                    is_name_query = True
                    name = " ".join(cmd[1])
                    query = q.name == name
                    return query, is_name_query, False
                case "-t":
                    types = cmd[1]
                    for type in types:
                        is_valid_type = validate_type(type)
                        if not is_valid_type:
                            return False                         
                    if query is None:
                        query =  q.type.all(types) if exact else q.type.any(types)
                    else:
                        query &= q.type.all(types) if exact else q.type.any(types)
                case "--taste":
                    tastes = cmd[1]
                    
                    for taste in tastes:
                        is_valid_taste = validate_taste(taste)
                        if not is_valid_taste:
                            return False
                    if query is None:
                        query = q.taste.all(tastes) if exact else q.taste.any(tastes)
                    else:
                        query &= q.taste.all(tastes) if exact else q.taste.any(tastes)              
    return query, is_name_query, show_all
    
def transform_input(parsed_input):
    """
    Transforms input into expected data structure(s).
    """
    for flag, args in parsed_input.items():
        match flag:
            case '-s':
                # Convert string digits to ints
                int_months = []
                for arg in args:
                    int_months.append(int(arg)) # No need to try/except because args have already been validated
                parsed_input[flag] = int_months
    
    return parsed_input