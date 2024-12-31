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

    
def transform_input(parsed_input):
    """
    Transforms input into expected data structure(s).
    """
    seasonal = False
    if "-t" in parsed_input.keys():
        if "fruit" in parsed_input['-t'] or "vegetable" in parsed_input['-t']:
            seasonal = True

    for flag, args in parsed_input.items():
        match flag:
            case '-s':
                # Make non-seasonal items season [] by default
                if not seasonal:
                    parsed_input[flag] = []
                    continue
                # Convert string digits to ints
                int_months = []
                for arg in args:
                    int_months.append(int(arg)) # No need to try/except because args have already been validated
                parsed_input[flag] = int_months
    
    return parsed_input
    
    
def generate_query(processed_input):
    """
    Generates a TinyDB query based on the processed user input.
    
    Return:
    query -- db query    
    """
    query = None # Query to be built upon
    exact = False # Whether or not exact matches are preferred (e.g. taste: sweet AND savoury, not sweet OR savoury)
    is_name_query = False
    types = ['fruit', 'vegetable', 'carb', 'protein', 'fat']
    positional_args, flag_args = processed_input

    for arg in positional_args:
        match arg:
            case "all":
                if query is None:
                    query = q.type.any(types)
                else:
                    query &= q.type.any(types)
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
                
    for flag, args in flag_args.items():
        match flag:
            case "-n":
                    is_name_query = True
                    query = q.name == args[0]
                    return query, is_name_query
            case "-t":                     
                if query is None:
                    query = q.type.all(args) if exact else q.type.any(args)
                else:
                    query &= q.type.all(args) if exact else q.type.any(args)
            case "--taste":                
                if query is None:
                    query = q.taste.all(args) if exact else q.taste.any(args)
                else:
                    query &= q.taste.all(args) if exact else q.taste.any(args)
    
    return query, is_name_query