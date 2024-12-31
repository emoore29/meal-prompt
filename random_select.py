import random
import argparse
from tinydb import TinyDB, Query
from print import *
from season import *


db = TinyDB('db.json')
q = Query()

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
              random_ingredient = random.choice(matches)
              print(random_ingredient)
              return random_ingredient
        else:
              return None