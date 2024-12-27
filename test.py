import re


def parse_args(line):
      """
      Captures flags and respective arguments in tuples.
      
      Param:
      line -- line input by user
    
      Return:
      List of tuples in the form (flag, argument)
      
      Words separated as spaces are treated as individual args:
      --taste sweet savoury --> ('--taste', ['sweet', 'savoury'])
      
      Words separated by spaces wrapped in quotation marks are treated as one arg:
      -c "blood orange" --> ('-c', ['blood orange'])
      """
      flags = ['-n', '-t', '--taste', '-c', '-s']

      capture = ""
      for i, flag in enumerate(flags):
            if i == len(flags) - 1:
                  capture += f"{flag}"
            else:
                  capture += f"{flag}|"
                  
      pattern = f"({capture})(.*?)(?={capture}|$)"
      results = re.findall(pattern, line)

      # Remove any whitespace around args and flags
      # Check for missing arguments from flags
      for i, tuple in enumerate(results):
            flag = tuple[0].strip()
            args = tuple[1].strip().split(" ")
            
            results[i] = flag, args
            if args == '':
                  print(f"Missing argument for {tuple[0]}")
                  return False
            
      # Check provided args are valid for each flag
      
            
      print(results)
      return results

parse_args("-n two names -t fruit --taste sweet -c chocolate -s 1 -m")

# def validate_args(cmd):
#       """
#       Checks arguments provided by user are valid for each flag.
      
#       Params:
#       cmd -- list of tuples in the form (flag, argument)
      
#       Return:
#       False if any arg is invalid
#       True if all args are valid      
#       """
#       for tuple in cmd:
#             flag = tuple[0]
#             args = tuple[1]
#             match flag:
#                 case "-n":
                    
#                 case "-t":
#                     valid_args = ["fruit", "vegetable", "carb", "fat", "protein"]
                    
                    
#                 case "--taste":
                
                 
      
      
      
#       return True