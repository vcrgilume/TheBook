'DATA IMPORTATION'
'1'

import pandas as pd
import taceconomics
import os

taceconomics.api_key = os.environ.get("TAC_API_KEY")

series_list    = pd.read_csv("LIST_MACRO_INDICATOR_TEST.csv", delimiter=';')
countries_list = pd.read_csv("LIST_COUNTRIES.csv",sep=";")
print(countries_list)

options = "?collapse=M&start_date=2000"
base_finale = pd.DataFrame()

for index, row in series_list.iterrows():
    code   = row["code"]
    symbol = row["symbol"]
    name = row["name"]
    area = row["area"]
    long_name = row["long_name"]
    criterion = row["criterion"]
    source = row["source"]
    typedata = row["type"]

    for country in countries_list.country_id:

        code_final = f"{code}/{country}{options}"

        # data = pd.DataFrame( taceconomics.get(f'data/{code_final}')['data'] )
        data = taceconomics.getdata(code_final)
        
        if data is not None:
            # TODO : faire des calculs stats ou tout ajout

            data = data.reset_index()
            data["country_id"] = country
            data["symbol"] = symbol
            data.columns = ["timestamp","value","country_id","symbol"]

            base_finale = pd.concat([base_finale,data])
        else:
            print(f":No {symbol} data for contry:  {country}")
            


base_finale.to_csv('ExtractAPItacsPRINT.csv', index=False)