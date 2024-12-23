import re
from tinydb import TinyDB, Query
from season import *


db = TinyDB('db.json')
q = Query()

def print_cols(items):
    """
    Takes list of items, prints with max 10 rows (new col once 10 is exceeded)
    """
    max_rows = 8
    column_width = max(len(item['name']) for item in items) + 2
    
    sorted_items = sorted(items, key=lambda x: x['name'])
    
    
    for row in range(max_rows):
            row_text = "" # Start a new row
            i = row # Start at current row index
            while i < len(sorted_items):
                if sorted_items[i]['favourite'] == 'y':
                      item = f"\033[92m{sorted_items[i]['name']}\033[0m"
                else:
                      item = sorted_items[i]['name']
                padding = column_width - visible_len(item)
                row_text += item + " " * padding
                i += max_rows
            if row_text != "":
                print(row_text)
            else:
                continue
    
def visible_len(s):
      """ 
      Calculates the visible length of a string by removing ANSI escape codes.
      Prevents incorrect formatting when highlighting favourite items in green.
      """
      return len(re.sub(r'\033\[[0-9;]*m', '', s))

def print_item(item):
      """
      Pretty prints an item's features from the database.
      """
      
      months = {
            1: "Jan",
            2: "Feb",
            3: "Mar",
            4: "Apr",
            5: "May",
            6: "Jun",
            7: "Jul",
            8: "Aug",
            9: "Sep",
            10: "Oct",
            11: "Nov",
            12: "Dec"
      }

      
      print(item['name'].title())
      print("-" * 10)
      print("Type: ", ", ".join(item['type']))
      print("Taste: ", ", ".join(item['taste']))
      print("Favourite: ", "yes" if item['favourite'] == 'y' else "no")
      print("Compliments: ", ", ".join(item['compliments'])) if len(item['compliments']) > 1 else print("Compliments: none")
      print("Season: ", f"{months[item['season'][0]]} - {months[item['season'][1]]}") if item['season'] != 'n/a' else print("Season: n/a")