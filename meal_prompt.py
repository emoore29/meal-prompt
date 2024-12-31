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

def trim_signs(s):
        return s.lstrip('+-')

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
    intro = f"{GREEN}{banner}{END} \nCreator: emoore29.github.io  \nBanner font: patorjk.com \n\n---------------------------\n\nWelcome to Meal Prompt!\nType 'help' for available commands. \n"
    
    def __init__(self):
        super().__init__()
        
    
    def do_square(self, line):
        def square(str):
            return int(str) * int(str)
        
        print(square(line))
    
    def do_pmt(self, line):
        """
        Generate a sweet or savoury meal prompt.
        
        Required:
        --taste         Type of meal (sweet or savoury)
        """
        self.handle_prompt(line)
        
    def do_edit(self, line):
        """
        Edit an item's features.
        
        Required:
        -n         Name of item to edit (use -<old_name> +<new_name> to update name)
        
        
        Update:
        (+<arg> to add, -<arg> to remove)
        
        -t         Type (+<type> to add a type, -<type> to rm a type)
        --taste    Taste
        -c         Compliments
        
        Replace:
        (input <args> as normal - it will replace the old args)
        -s         Season 
        -f         Favourite
        
        """
        self.handle_edit(line)

    def do_rm(self, line):
        """
        
        Remove an item from the database.
        
        Required:
        -n        Name of item        
        """
        self.handle_remove(line)

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
        self.handle_add(line)
        
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
        self.handle_show(line)

    def do_quit(self, line):
        """Exit the CLI."""
        return True
    
    def process_input(self, line, required_flags, allowed_flags, prompt, edit, positional_args=[]):
        """
        Parses, validates, and transforms a user's input.
        
        Checks flags and provided arguments are valid.
        
        Return:
        parsed_input -- if valid
        False -- if not valid
        """
        # Parse input
        if parse_input(line):
            parsed_positional, parsed_flags = parse_input(line)
        else:
            return False
            
        # Check at least a positional arg or flag was provided
        if not parsed_flags and not parsed_positional:
            print("Input missing either flags or positional args.")
            return False
        
        # Validate parsed input
        if parsed_positional[0] != '':
            if not valid_positional(parsed_positional, positional_args):
                print("invalid positional")
                return False
        
        bulk = False
        if "bulk" in parsed_positional:
            bulk = True

        if parsed_flags != {}:
            if not valid_flags(parsed_flags, required_flags, allowed_flags):
                print("invalid flags")
                return False
            if not valid_flag_args(parsed_flags, prompt, edit, bulk):
                print("invalid flag args")
                return False
        
        # Transform input
        transformed_flags = transform_input(parsed_flags)
        
        return parsed_positional, transformed_flags

    def handle_remove(self, line):
        """
        Removes item from database if it exists.
        """
        processed_input = self.process_input(line, ['-n'], ['-n'], False, False)
        if not processed_input:
            print("Remove cancelled.")
            return
        name = processed_input[1]['-n'][0]
        results = db.search(q.name == name)
        if len(results) > 1:
            print(f"Multiple items found with name {name}")
            confirm_delete = input("\nDeletion will remove all items. Confirm delete? (y/n) ")
        elif len(results) == 1:
            print("")
            print_item(results[0])
            confirm_delete = input(f"\nConfirm delete (y/n) ")
        else:
            print(f"Item not found in db: {name}")
            return
        
        if confirm_delete == "y":
            db.remove(q.name == name)
            print(f"Deleted item: {name}")
        else:
            print("Item not deleted.")
    
    def handle_prompt(self, line):
        """
        Generates a meal prompt if user input is valid.
        
        """

        processed_input = self.process_input(line, ['--taste'], ['--taste'], prompt=True, edit=False)
        if not processed_input:
            print("Prompt cancelled")
            return 
        
        taste = processed_input[1]['--taste'][0]
        
        self.generate_prompt(taste)
        
    def generate_prompt(self, taste):
        """
        Pseudo-randomly select ingredients for a "meal prompt"
        """
        types = ['fruit', 'vegetable', 'carb', 'fat', 'protein']
        added = []
        print("")
        while len(types) > 0:
            random_type = random.choice(types)
            random_ingredient = self.get_random_ingredient(random_type, taste)
            if random_ingredient:
                prompt_type = ""
                for type in random_ingredient['type']:
                    # Add type to prompt_type (unless already added)
                    if type not in added:
                        if len(prompt_type) == 0:
                            prompt_type += type
                        else:
                            prompt_type += "/" + type
                        added.append(type)
                    
                    # Remove type from list of types to search through
                    if type in types:
                        types.remove(type)
                        
                # print(f"{prompt_type}: {random_ingredient['name']}") # Verbose version with types printed
                print(f"{random_ingredient['name']}")
            else:
                types.remove(random_type)
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
                random_ingredient = random.choice(matches)
                return random_ingredient
            else:
                return None   

    def handle_show(self, line):
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
        query = None
        is_name_query = False
        processed_input = self.process_input(line, [], item_flags, False, False, ['all', 'seasonal', 'favs', 'exact'])
        if not processed_input:
            print("Show cancelled.")
            return

        query, is_name_query = generate_query(processed_input)
        
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
        else:
            print("Error.")

    def edit_item(self, name, flag_args, item_to_edit):
        """
        Updates values of item_to_edit and then updates database with new item.
        """
        for flag, args in flag_args.items():
            changes = 0
            match flag:
                case '-n':
                    for arg in args:
                        if arg[0] == "+":
                            item_to_edit['name'] = trim_signs(arg)
                            changes += 1
                case '-t':
                    num_types = len(item_to_edit['type'])
                    count = 0
                    for arg in args:
                        if arg[0] == "-":
                            count -= 1
                        if arg[0] == "+":
                            count += 1
                    if num_types + count == 0:
                        print(f"Item requires at least one type. Cannot remove type.")
                    else:
                        for arg in args:
                            if arg[0] == "-":
                                if trim_signs(arg) in item_to_edit['type']:
                                    item_to_edit['type'].remove(trim_signs(arg))
                                    changes += 1
                                    
                            if arg[0] == "+":
                                if trim_signs(arg) in item_to_edit['type']:
                                    print(f"Item already contains {arg}")
                                else:
                                    item_to_edit['type'].append(trim_signs(arg))
                                    changes += 1
                                    
                case '--taste':
                    num_tastes = len(item_to_edit['taste'])
                    count = 0
                    for arg in args:
                        if arg[0] == "-":
                            count -= 1
                        if arg[0] == "+":
                            count += 1
                    if num_tastes + count == 0:
                        print(f"Item requires at least one taste. Cannot remove taste.")
                    else:
                        for arg in args:
                            if arg[0] == "-":
                                if trim_signs(arg) in item_to_edit['taste']:
                                    item_to_edit['taste'].remove(trim_signs(arg))
                                    changes += 1
                            if arg[0] == "+":
                                if trim_signs(arg) in item_to_edit['taste']:
                                    print(f"Item already contains {trim_signs(arg)}")
                                else:
                                    item_to_edit['taste'].append(trim_signs(arg))
                                    changes += 1
                case '-f':
                    item_to_edit['favourite'] = trim_signs(args[0])
                    changes += 1
                case '-c':
                    for arg in args:
                        if arg[0] == "+":
                            if trim_signs(arg) in item_to_edit['compliments']:
                                    print(f"Item already contains {trim_signs(arg)}")
                            else:
                                item_to_edit['compliments'].append(trim_signs(arg))
                                changes += 1
                        if arg[0] == "-":
                            if trim_signs(arg) in item_to_edit['compliments']:
                                    item_to_edit['compliments'].remove(trim_signs(arg))
                                    changes += 1
                            else:
                                print(f"Item does not contain {trim_signs(arg)}")
                case '-s':
                    item_to_edit['season'] = args
                    changes += 1
        
        if changes > 0:
            try:
                db.update(item_to_edit, q.name==name)
                print("Updated item")
            except SystemExit:
                pass
            
        else:
            print("No changes required.")
        
    def handle_edit(self, line):
        """
        Edits item in database based on user input.
        """
        processed_input = self.process_input(line, ['-n'], ['-n', '-t', '--taste', '-f', '-c', '-s'], prompt=False, edit=True)
        if not processed_input:
            print("Edit cancelled.")
            return
        flag_args = processed_input[1]
        print(flag_args['-n'][0])
        name = trim_signs(flag_args['-n'][0])
        results = db.search(q.name == name)
        if not results:
            print(f"Item not found: {name}")
            return
        elif len(results) == 1:
            item_to_edit = results[0]
        else:
            print("Error. Multiple items of that name found.")
        
        self.edit_item(name, flag_args, item_to_edit)
  
    def handle_add(self, line):
        """
        Add an item to TinyDB.
        """
        processed_input = self.process_input(line, ['-n', '-t', '--taste', '-s'], item_flags, False, False, ['bulk'])
        if not processed_input:
            print("Add cancelled.")
            return

        names_to_process = processed_input[1]['-n']

        added = []
        ignored = []
        
        for name in names_to_process:    
            item_to_add = {"name": "", "type": [], "taste": [], "favourite": "n", "compliments": [], "season": []}
            
            for flag, args in processed_input[1].items():
                match flag:
                    case '-n':
                        item_to_add['name'] = name
                    case "-t":
                        item_to_add['type'] = args
                    case '--taste':
                        item_to_add['taste'] = args
                    case '-s':
                        item_to_add['season'] = args
                    case '-f':
                        item_to_add['favourite'] = args
                    case '-c':
                        item_to_add['compliments'] = args
                        
            item = db.search(q.name == name)
            if item:
                ignored.append(item_to_add)
                continue    
                
            try:
                db.insert(item_to_add)
                added.append(item_to_add)
            except SystemExit:
                pass
            
        if len(added) > 0:
            print("")
            print(f"Added:")
            print_cols(added)
        if len(ignored) > 0:
            print("")
            print("Ignored (already exist in db):")
            print_cols(ignored)
    

if __name__ == '__main__':
    MealPrompt().cmdloop()