from entsoe import EntsoePandasClient

def callentsoe(country_code, start_date, end_date):    
        
    API_KEY = "c7465662-663b-4054-84bb-ea958f346c5a"

    client = EntsoePandasClient(api_key=API_KEY)   

    try:
               
        prices = client.query_day_ahead_prices(country_code, start=start_date, end=end_date )
        
  
        #print(prices)
    
        #prices.to_csv("prueba.csv", header=True)
        return prices
 
    except Exception as e:
        print("ERROR:")
        print(e)

    return 
