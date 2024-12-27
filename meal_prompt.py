import cmd
from tinydb import TinyDB, Query
import re
from validation import *
from parse import *
from print import *
import random

db = TinyDB('db.json')
q = Query()

item_flags = ['-n', '-t', '--taste', '-f', '-c', '-s']

def validate_line(line, required_flags, allowed_flags):
    """
    Parses and validates a user's input.
    
    Checks flags and provided arguments are valid.
    
    Return:
    parsed_input -- if valid
    False -- if not valid
    """
    # Parse input
    parsed_input = parse_input(line, allowed_flags)
    
    # Validate input
    if not valid_flags(parsed_input, required_flags, allowed_flags):
        return False
    
    if not valid_args(parsed_input, edit=True):
        return False
    
    # Transform input
    transformed_input = transform_input(parsed_input)
    
    return transformed_input
    

def handle_remove(line):
    """
    Removes item from database if it exists.
    """
    
    # Convert user input to list of tuples for validation
    list_cmds = parse_flags(line)
    
    required_flags = ['-n']
    allowed_flags = ['-n']
    
    # Check provided flags are valid
    if not list_cmds or not valid_flags(list_cmds, required_flags, allowed_flags):
        return
    else:
        print(list_cmds[0][1])
        name = " ".join(list_cmds[0][1])
        item = db.search(q.name == name)
        if item:
            confirm_delete = input(f"Item found: {item}. Confirm delete (y/n) ")
            if confirm_delete == "y":
                db.remove(q.name == name)
                print(f"Deleted item: {name}")
            else:
                print("Item not deleted.")
        else:
            print(f"Item not found in db: {name}")

def handle_prompt(line):
    """
    Generates a meal prompt if user input is valid.
    
    """

    list_cmds = parse_flags(line)
    required_flags = ['--taste']
    allowed_flags = ['--taste']

    if not list_cmds or not valid_flags(list_cmds, required_flags, allowed_flags):
        return
    
    for cmd in list_cmds:
        flag = cmd[0][0]            
        
        match flag:
            case '--taste':
                for taste in cmd[1]:
                    is_valid_taste = validate_taste(taste)
                    if is_valid_taste:
                        generate_prompt(taste)
                    else:
                        return
    
def generate_prompt(taste):
    """
    Pseudo-randomly select ingredients for a "meal prompt"
    """
    fruit = get_random_ingredient("fruit", taste)
    veg = get_random_ingredient("vegetable", taste)
    carb = get_random_ingredient("carb", taste)
    protein = get_random_ingredient("protein", taste)
    fat = get_random_ingredient("fat", taste)
    
    ingredients = [item for item in [fruit, veg, protein, carb, fat] if item]
    
    # Remove duplicates by converting to set and back to list
    non_duplicate_ingredients = list(set(ingredients))
    
    print("")
    print("-" * 20)
    print(f"{taste.title()} Meal Prompt")
    print("-" * 20)
    for ingredient in non_duplicate_ingredients:
            print(f"- {ingredient}") 
    print("")
    
def get_random_ingredient(type, taste):
        """
        Selects an ingredient from a source and category
        
        Params: 
        type -- protein, fat, carb, fruit, or vegetable
        taste -- sweet or savoury
        """
        
        query = q.type.any(type) & q.taste.any(taste)
        
        # Only select fruit/veg in season
        if type == "fruit" or type == "vegetable":
              query &= q.season.test(is_in_season)
        
        pick_from_favs = random.choices([True, False], weights=[55, 45], k=1)[0]
        if pick_from_favs:
                matches = db.search(query & (q.favourite == "y"))
                if len(matches) > 0: # Only get from favs if there are favourites
                      query &= q.favourite == "y"
        
        matches = db.search(query)
  
        if len(matches) > 0:
            return random.choice(matches)['name']
        else:
            return None   

def handle_show(line):
    """
    Positional arguments:
    all -- shows all items in db, grouped by type
    seasonal -- shows seasonal items (all by default unless a flag is specified)
    fav -- shows favourited items (all by default unless a flag is specified)
    
    Flags:
    -t {name} -- shows item(s) matching given name
    -t {type} -- shows all items of given type
    --taste {taste} -- shows all items of given taste
    
    """
    
    allowed_positional = ['all', 'seasonal', 'favs', 'exact']
    allowed_flags = ['-n', '-t', '--taste']

    parsed = parse_show(line, allowed_positional, allowed_flags)
    if parsed:
        query, is_name_query, show_all = parsed
    else:
        query = None
        is_name_query = False
        show_all = False
    
    if query:
        print("")
        results = db.search(query)
        if results:
            if is_name_query:
                print_item(results[0])
            else:
                print_cols(results)
        else:
            print("No items found.")
        print("")
    elif show_all:
        print("")
        types = ['fruit', 'vegetable', 'carb', 'protein', 'fat']
        for type in types:
            items = get_all_type(type)
            print("-" * (len(type) + 1))
            print(f"{type.title()}s")
            print("-" * (len(type) + 1))
            print_cols(items)
            print("")
        
        return

def get_all_type(type):
    """
    Gets items for a given type
    """
    return db.search(q.type.any(type))

def handle_edit(line):
    """
    Edits item in database based on user input.
    """
    input = validate_line(line, ['-n'], item_flags)
    if not input:
        print("Edit cancelled.")
        return
    print(input)
    

def validate_add_args(line):
    """
    Validates cmd line arguments provided by user.
    
    Returns early if required flags not provided or invalid arguments required.
    
    """
    list_cmds = parse_flags(line)
    
    kwargs = {"name": "", "type": [], "taste": [], "favourite": "n", "compliments": [], "season": []}

    required_flags = ['-n', '-t', '--taste', '-s']
    allowed_flags = ['-n', '-t', '--taste', '-s', '-c', '-f']

    if not list_cmds or not valid_flags(list_cmds, required_flags, allowed_flags):
        return
        
    for cmd in list_cmds:
        flag = cmd[0][0]            
        
        match flag:
            case "-n":
                name = " ".join(cmd[1])
                item = db.search(q.name == name)
                if item:
                    print(f"Item already exists in database: {name}")
                    return
                else:
                    kwargs['name'] = name
            case "-t":
                for type in cmd[1]:
                    is_valid_type = validate_type(type)
                    if is_valid_type:
                        kwargs['type'].append(type)
            case '--taste':
                for taste in cmd[1]:
                    is_valid_taste = validate_taste(taste)
                    if is_valid_taste:
                        kwargs['taste'].append(taste)
                    else:
                        return
            case '-s':
                if len(cmd[1]) != 2:
                    print("-s requires exactly int arguments: {start month} {end month}")
                    return
                else:
                    for month in cmd[1]:
                        is_valid_month = validate_month(month)
                        if is_valid_month:
                            kwargs['season'].append(int(month))
            case '-f':
                if validate_fav(cmd[1][0]):
                    kwargs['favourite'] = cmd[1][0]
            case '-c':
                for item in cmd[1]:
                    kwargs['compliments'].append(item)
    
    return kwargs

class MealPrompt(cmd.Cmd):
    prompt = ">>> "
    GREEN = "\033[32m"
    END = "\033[0m"
    banner = r"""
                       _                                      
                      | |                                  _ 
  _ __ ___   ___  __ _| |  _ __  _ __ ___  _ __ ___  _ __ | |_ 
 | '_ ` _ \ / _ \/ _` | | | '_ \| '__/ _ \| '_ ` _ \| '_ \| __|
 | | | | | |  __/ (_| | | | |_) | | | (_) | | | | | | |_) | |_ 
 |_| |_| |_|\___|\__,_|_| | .__/|_|  \___/|_| |_| |_| .__/ \__|
                          | |                       | |        
                          |_|                       |_|        
"""
    intro = f"{GREEN}{banner}{END}\nWelcome to Meal Prompt! \nBy emoore29.github.io.  \nBanner font by patorjk.com. \nType 'help' for available commands. \n"
    
    def __init__(self):
        super().__init__()
        
    def do_pmt(self, line):
        """
        Generate a sweet or savoury meal prompt.
        
        Required:
        --taste         Type of meal (sweet or savoury)
        """
        handle_prompt(line)
        
    def do_edit(self, line):
        """
        Edit an item's features.
        
        Required:
        -n         Name of item to edit (use +<new name> to update name)
        
        
        Optional (at least one required):
        (+<arg> to add, -<arg> to remove, <arg> to replace all)
        
        -t         Type (+<type> to add a type, -<type> to rm a type)
        --taste    Taste
        -f         Favourite
        -c         Compliments
        -s         Season
        """
        handle_edit(line)

    def do_rm(self, line):
        """
        
        Remove an item from the database.
        
        Required:
        -n        Name of item        
        """
        handle_remove(line)

    def do_add(self, line):
        """
        Add an item to the database.
        
        Required:
        -n        Name of item
        -t        Type of item, separated by spaces (fruit, vegetable, carb, fat, protein)
        --taste   Taste of item, separated by spaces (sweet, savoury)
        -s        Months item is in season {start month} {end month} (required for fruit and vegetable only)
        
        Optional: 
        -c        Ingredients that compliment the item, separated by spaces (use "" for items with more than one word)
        -f        Favourite item (y, n)
        """
        kwargs = validate_add_args(line)
      
        if kwargs:
            try:
                  db.insert(kwargs)
                  print(f"Item added to db: {kwargs['name']}")
            except SystemExit:
                  pass
        

    def do_show(self, line):
        """
        Display items from the database.
        
        Use to display items by type, name, taste, in-season, and favourites, or a combination of them.
        
        At least one of the below is required.
        
        all       Show all items in database
        seasonal  Show seasonal items in database (all unless flags provided)
        favs      Show favourite items (all unless flags provided)
        exact     Shows exact match (e.g. '--taste sweet savoury' displays items that include both 'sweet' and 'savoury' values)
        -n        Name of item
        -t        Type of item (fruit, vegetable, carb, fat, protein)
        --taste   Taste of item (sweet, savoury)
        -f        Favourite item (y, n)
        
        """
        handle_show(line)

    def do_quit(self, line):
        """Exit the CLI."""
        return True

if __name__ == '__main__':
    MealPrompt().cmdloop()