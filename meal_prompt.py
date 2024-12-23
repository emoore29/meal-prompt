import cmd
from tinydb import TinyDB, Query
import re
from validation import *
from parse import *
from print import *

db = TinyDB('db.json')
q = Query()

def handle_remove(line):
    """
    Removes item from database if it exists.
    
    """
    list_cmds = parse_flags(line)
    
    required_flags = ['-n']
    allowed_flags = ['-n']
        
    if not valid_flags(list_cmds, required_flags, allowed_flags):
        return
    else:
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
    
def handle_item(line):
    """
    Displays info for a specific item.
    
    """
    
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
        query, is_name_query = parsed
    else:
        query = None
        is_name_query = False
    
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
        
    
    

def validate_add_args(line):
    """
    Validates cmd line arguments provided by user.
    
    Returns early if required flags not provided or invalid arguments required.
    
    """
    list_cmds = parse_flags(line)
    
    
    kwargs = {"name": "", "type": [], "taste": [], "favourite": "n", "compliments": [], "season": []}

    required_flags = ['-n', '-t', '--taste', '-s']
    allowed_flags = ['-n', '-t', '--taste', '-s', '-c', '-f']

    if not valid_flags(list_cmds, required_flags, allowed_flags):
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
    intro = "Welcome to Meal Prompt. Type 'help' for available commands."
    
    def __init__(self):
        super().__init__()
        

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
        fav       Show favourite items (all unless flags provided)
        exact     Shows exact match (e.g. '--taste sweet savoury' displays items that include both 'sweet' and 'savoury' values)
        -n        Name of item
        -t        Type of item (fruit, vegetable, carb, fat, protein)
        --taste   Taste of item (sweet, savoury)
        -s        Months item is in season {start month} {end month} (required for fruit and vegetable only)
        -c        Ingredients that compliment the item
        -f        Favourite item (y, n)
        
        """
        handle_show(line)

    def do_quit(self, line):
        """Exit the CLI."""
        return True

if __name__ == '__main__':
    MealPrompt().cmdloop()