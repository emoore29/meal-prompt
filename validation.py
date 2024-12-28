def validate_taste(args, prompt, edit):
      valid_tastes = ['sweet', 'savoury']
      
      if edit:
            valid_options = []
            for type in valid_tastes:
                  add_type = "+" + type
                  rm_type = "-" + type
                  valid_options.append(add_type)
                  valid_options.append(rm_type)
                  
            for str in args:
                  if str not in valid_options:
                        print(f"Invalid taste: {str}")
                        return False
      elif prompt:
            if len(args) > 1:
                  print("Only one taste argument allowed for a meal prompt.")
                  return False
            for str in args:
                  if str not in valid_tastes:
                        print(f"Invalid taste: {str}")
                        return False
      else:
            for str in args:
                  if str not in valid_tastes:
                        print(f"Invalid taste: {str}")
                        return False
      return True
      
def validate_type(args, edit):
      valid_types = ['fruit', 'vegetable', 'carb', 'fat', 'protein']
      if edit:
            valid_options = []
            for type in valid_types:
                  add_type = "+" + type
                  rm_type = "-" + type
                  valid_options.append(add_type)
                  valid_options.append(rm_type)
            
            for str in args:
                  if str not in valid_options:
                       print(f"Invalid type: {str}")
                       return False
      else:
            for str in args:
                  if str not in valid_types:
                        print(f"Invalid type: {str}")
                        return False
      return True
      
def valid_fav(str):
      valid_favs = ['y', 'n']
      if str not in valid_favs:
            print(f"Invalid favourite. Choose from: {valid_favs}")
            return False
      else:
            return True
      
def valid_month(str):
      try:
            month = int(str)
      except TypeError:
            print("Month must be an integer between 1 and 12 (inclusive)")
            return False
      
      valid_months = list(range(1, 13))
      if month not in valid_months:
            print(f"Invalid month. Choose from: {valid_months}")
            return False
      else:
            return True
      
def valid_flags(parsed_flags, required, allowed):
    """
    Checks user has provided all required flags and/or the provided flags are valid.
    Returns False if they have not.
    """
    if not parsed_flags:
          print("No flags provided")
          return False
    
    for flag in parsed_flags.keys():
        if flag not in allowed:
                print(f"Provided flag is invalid: {flag}")  
                return False      

    # Check required flags were provided
    for flag in required:
        if flag not in parsed_flags.keys():
            print(f"Required flag missing: {flag}")
            return False
    return True

def validate_name(args, edit):
      """
      Checks name is a single argument, unless editing. 
      If editing, ensures only two arguments were provided - -<name> and +<new name>
      """
      if edit:
            if len(args) > 2:
                  print("Exactly two arguments required to edit name: -<old name> +<new name>")
                  return False
            elif len(args) == 2:
                  editing = False
                  if args[0][0] in "+-" and args[1][0] in "+-":
                      editing = True     
                  if not editing:
                        print("Require '+' before new name, '-' before old name.")
                        return False
                  
      else:
            if len(args) != 1:
                  print("Only one argument allowed for name. Multi-word name must be wrapped in \"\"")
                  return False
            
      return True

def valid_flag_args(parsed_flags, prompt, edit):
      """
      Validates arguments in parsed_input against flags.  
      Converts arguments where required - e.g. str months to int, quoted names to single arg??
      
      Params:
      parsed_input -- list of tuples containing (flag, args)    
      """
      for flag, args in parsed_flags.items():
          if len(args) == 0:
                print(f"Missing arguments for {flag}")
                return False
          
          match flag:
                case '-n':
                      valid = validate_name(args, edit)
                      if not valid:
                            return False
                case '-t':
                      valid = validate_type(args, edit)
                      if not valid:
                            return False
                case '--taste':
                      valid = validate_taste(args, prompt, edit)
                      if not valid:
                            return False
                case '-f':
                      if len(args) > 1:
                            print("Too many arguments provided for -f flag.")
                            return False
                      else:
                            if not valid_fav(args[0]):
                                  return False
                case '-c':
                      # Compliments don't (yet) require validation
                      continue
                case '-s':
                      if len(args) != 2:
                            print("Must provide exactly two months.")
                            return False
                      for arg in args:
                            if not valid_month(arg):
                                  return False
      return True

def valid_positional(parsed_positional, positional_args):
      """
      Checks list of positional args are allowed
      """
      
      for arg in parsed_positional:
            if arg not in positional_args:
                  print(f"Invalid positional argument: {arg}")
                  return False
       
      return True