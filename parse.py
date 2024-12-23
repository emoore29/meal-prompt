import re
from validation import *
from tinydb import TinyDB, Query
from season import *

db = TinyDB('db.json')
q = Query()

def parse_flags(line):
    """
    Groups flags and respective arguments in tuples.
    
    Param:
    line -- line input by user
    
    Return:
    List of tuples in the form (flag, argument)
    """
    
    # Split line to get flags and their corresponding arguments
    cmds = re.findall(r'-*[a-z]*\s"?[a-z0-9"?\s]*', line)
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
    TODO: Refactor match to be more robust.
    
    Generates a query based on provided arguments
    
    Params:
    line -- raw input from user
    allowed_positional -- allowed positional arguments
    allowed_flags -- allowed flags
    
    
    Return:
    None -- if provided arguments are invalid
    query -- query for searching db based on provided args   
    """
    query = None # Query to be built upon
    exact = False # Whether or not exact matches are preferred (e.g. taste: sweet AND savoury, not sweet OR savoury)
    is_name_query = False
    
    if line == "":
        print("At least one argument is required. Type 'help show' for more info.")
        return
    
    # Split into positional and flags 
    split_line = re.split(r"(?=-)", line, maxsplit=1)
    positional_args = split_line[0].strip().split(" ") # List of positional args
    
    # Check provided positional args are allowed
    for arg in positional_args:
        if arg not in allowed_positional and arg != '':
            print(f"Invalid positional argument: {arg}")
            return
    
    for arg in positional_args:
        match arg:
            case "all":
                # TODO: Handle all
                # 
                continue
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
        if not valid_flags(flag_cmds, [], allowed_flags):
            return
        
        for cmd in flag_cmds:
            flag = cmd[0][0]       
            match flag:
                case "-n":
                    # Return early with query
                    # If user searches for a name, other arguments are ignored
                    is_name_query = True
                    name = " ".join(cmd[1])
                    query = q.name == name
                    return query, is_name_query
                case "-t":
                    types = cmd[1]
                    for type in types:
                        is_valid_type = validate_type(type)
                        if not is_valid_type:
                            return                        
                    if query is None:
                        query =  q.type.all(types) if exact else q.type.any(types)
                    else:
                        query &= q.type.all(types) if exact else q.type.any(types)
                case "--taste":
                    tastes = cmd[1]
                    for taste in tastes:
                        is_valid_taste = validate_taste(taste)
                        if not is_valid_taste:
                            return
                    if query is None:
                        query = q.taste.all(tastes) if exact else q.taste.any(tastes)
                    else:
                        query &= q.taste.all(tastes) if exact else q.taste.any(tastes)              
    return query, is_name_query
    