import random
import argparse
from tinydb import TinyDB, Query
from print import *
from season import *

# Original code using argparse instead of cmd, kept for reference.

db = TinyDB('db.json')
q = Query()


def generate_prompt(args):
        """
        Prints a seasonal meal prompt with one random ingredient of each: fruit, veg, carb, fat, protein
        
        Params:
        args -- sweet or savoury - show error/warn if other cmd given
        """
        if not args:
            print("Meal prompt requires type: sweet or savoury")
            return

        elif args:
            flavour = args[0]
            if flavour != "sweet" and flavour != "savoury":
                   print(f"Argument not recognised: {type}")
                   return 
        
        fruit = get_random_ingredient("fruit", flavour)
        veg = get_random_ingredient("vegetable", flavour)
        carb = get_random_ingredient("carb", flavour)
        protein = get_random_ingredient("protein", flavour)
        fat = get_random_ingredient("fat", flavour)
        
        
        # fats = db.search(q.type.any("fat") & q.flavour.any(flavour))
        # fat = random.choices(fats)[0]['name'] if len(fats) > 0 else None
        ingredients = [item for item in [fruit, veg, protein, carb, fat] if item]
        for ingredient in ingredients:
                print(f"- {ingredient}")

def get_random_ingredient(type, taste):
        """
        Selects an ingredient from a source and category
        
        Params: 
        type -- protein, fat, carb, fruit, or vegetable
        flavour -- sweet or savoury
        """
        
        query = q.type.any(type) & q.flavour.any(taste)
        if type == "fruit" or type == "vegetable":
              query &= q.season.test(is_in_season)
        
        pick_from_favs = random.choices([True, False], weights=[70, 30], k=1)[0]
        if pick_from_favs:
                matches = db.search(query & (q.favourite == "y"))
                if len(matches) > 0: # Only get from favs if there are favourites
                      query &= q.favourite == "y"
        
        matches = db.search(query)
  
        if len(matches) > 0:
              return random.choice(matches)['name']
        else:
              return None

def handle_help(args):
    print("Available commands:")
    sorted_commands = sorted(COMMANDS.keys())
    for command in sorted_commands:
            print(command)
            
def handle_exit(args):
    print("Exiting. Goodbye!")
    exit()
    
                
        
COMMANDS = {
        "meal": generate_prompt,
        "help": handle_help,
        "exit": handle_exit,
        "add": add.handle_add,
        "show": display.show,    
        "rm": remove.remove_ingredient
}

def add_add_subcommand(subparsers):
    """
    Adds 'add' subcommand to parser
    """
    add_parser = subparsers.add_parser("add", help="Add a new item")
    add_parser.add_argument("-t", "--type", required=True, choices=["fruit", "veg", "carb", "fat", "protein"], help="Food group of the item")
    add_parser.add_argument("-n", "--name", required=True, help="Name of the item")
    add_parser.add_argument("-f", "--flavour", required=True,  choices=["sweet", "savoury"], help="Category of the item")
    add_parser.add_argument("-s", "--start", choices=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"], help="Start month the item is in season")
    add_parser.add_argument("-e", "--end", choices=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"], help="End month the item is in season")
    add_parser.add_argument("-fav", "--favourite", choices=["y", "n"], help="Favourite the item. Defaults to no.")
    add_parser.set_defaults(func=add.handle_add)
    
def add_remove_subcommand(subparsers):
    """
    Adds 'rm' subcommand to parser
    """
    add_parser = subparsers.add_parser("rm", help="Remove an item")
    add_parser.add_argument("-t", "--type", required=True, choices=["fruit", "veg", "carb", "fat", "protein"], help="Food group of the item")
    add_parser.add_argument("-n", "--name", required=True, help="Name of the item")
    add_parser.set_defaults(func=add.handle_add)

def main_parser():
      """
      Creates the main argument parser and subcommands.
      """
      parser = argparse.ArgumentParser()
      
      subparsers = parser.add_subparsers()
            
      add_add_subcommand(subparsers)
      add_remove_subcommand(subparsers)
      
      return parser


if __name__ == "__main__":
    parser = main_parser()
    print("Welcome to Meal Prompt! Type 'help' for a list of commands.")
    while True:
        try:
            raw_input = input(">> ").strip()
            if not raw_input: 
                continue
            
            # Handle 'help' and 'exit' manually
            if raw_input.lower() == "help":
                parser.print_help()
                continue
            if raw_input.lower() in ["exit", "quit"]:
                print("Exiting program.")
                break
                
            parts = raw_input.split()
        
            try:
                parsed_args = parser.parse_args(parts)
                if hasattr(parsed_args, 'func'):
                    parsed_args.func(parsed_args)
            except SystemExit:
                print("Error parsing command. Type 'help' for a list of commands.")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting program.")
            break
    

        
    
    