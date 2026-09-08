import os
os.environ["ENTSOE_ENDPOINT_URL"] = "https://external-api.tp.entsoe.eu/api"
from entsoe import EntsoePandasClient

def callentsoe(country_code, start_date, end_date):    
        
    #API_KEY = "c7465662-663b-4054-84bb-ea958f346c5a"
    API_KEY = "5b61e3af-607b-49af-8508-ad3077f15fbe"

    client = EntsoePandasClient(api_key=API_KEY)
    num_intentos = 3

    for i in range(num_intentos):
        try:
                prices = client.query_day_ahead_prices(country_code, start=start_date, end=end_date )
                print("Llamada a ENTSO-E exitosa")
                return prices
        except Exception as e:
            print("Error al llamar a ENTSO-E:", str(e))
            if i == num_intentos - 1:
                raise

        #print(prices)
    
        #prices.to_csv("prueba.csv", header=True)


    return 
