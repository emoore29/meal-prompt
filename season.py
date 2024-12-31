from datetime import date


def is_in_season(entry):
      if entry == []:
            # Ignore season for non-seasonal items
            return False
            
      start = entry[0]
      end = entry[1]
      today = date.today()
      month = today.month
      
      if start <= end: # Range doesn't wrap around year
            return start <= month <= end
      else: # Range wraps around year
            return month >= start or month <= end