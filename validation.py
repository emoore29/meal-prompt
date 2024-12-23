def validate_taste(str):
      valid_tastes = ['sweet', 'savoury']
      if str not in valid_tastes:
            print(f"Invalid taste. Choose from: {valid_tastes}")
            return False
      else:
            return True
      
def validate_type(str):
      valid_types = ['fruit', 'vegetable', 'carb', 'fat', 'protein']
      if str not in valid_types:
            print(f"Invalid type. Choose from: {valid_types}")
            return False
      else:
            return True
      
def validate_fav(str):
      valid_favs = ['y', 'n']
      if str not in valid_favs:
            print(f"Invalid favourite. Choose from: {valid_favs}")
            return False
      else:
            return True
      
def validate_month(str):
      month = int(str)
      valid_months = list(range(1, 13))
      if month not in valid_months:
            print(f"Invalid month. Choose from: {valid_months}")
            return False
      else:
            return True
      
def valid_flags(input, required, allowed):
    """
    Checks user has provided all required flags and/or the provided flags are valid.
    Returns False if they have not.
    """
    input_flags = []

    for cmd in input:
        flag = cmd[0][0]
        input_flags.append(flag)
        
    # Check provided flags are valid
    for flag in input_flags:
          if flag not in allowed:
                print(f"Provided flag is invalid: {flag}")  
                return False      

    # Check required flags were provided
    for flag in required:
        if flag not in input_flags:
            print(f"Required flag missing: {flag}")
            return False
    return True
