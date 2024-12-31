import unittest
from cmd import Cmd
from io import StringIO
import sys
from meal_prompt import MealPrompt, get_random_ingredient
from tinydb import TinyDB, Query

db = TinyDB('testdb.json')
q = Query()

class TestMealPrompt(unittest.TestCase):
      """
      Unit tests for MealPrompt.
      
      Uses StringIO to capture system output, as most methods in MealPrompt do not have a return value but instead print a value.
      
      """
      def setUp(self):
        self.app = MealPrompt()
        
      def test_quit(self):
           self.assertEqual(self.app.do_quit(""), True, "Quit return is wrong.")
      
      def test_square(self):
            # Capture output with StringIO() object
            output = StringIO()
            
            # Redirect sys.stdout to the StringIO object
            sys.stdout = output

            # Simulate calling the command            
            self.app.do_square("4")

            # Restore stdout
            sys.stdout = sys.__stdout__

            # Check the output
            self.assertEqual(output.getvalue().strip(), "16")
            
      def test_get_random_ingredient(self):
           type = "fruit"
           taste = "sweet"
           expected = {
            "name": "blueberry",
            "type": ["fruit"],
            "taste": ["sweet"],
            "favourite": "n",
            "compliments": ["yogurt"],
            "season": [5, 10]
            }
           
           self.assertEqual(get_random_ingredient(type, taste), expected, "Random ingredient is wrong.")
           
            
            
            
if __name__ == '__main__':
      unittest.main()