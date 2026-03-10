'TACECONOMICS'

import pandas as pd
import taceconomics
import os

taceconomics.api_key = os.environ.get("TAC_API_KEY")

series_list    = pd.read_csv("series.csv",sep=',')
countries_list = pd.read_csv("countries.csv",sep=",")
series_list.head()

base_finale = pd.DataFrame()
for index, row in series_list.iterrows():
    code   = row["code"]
    symbol = row["symbol"]
    name = row["name"]
    category = row["category"]
    long_name = row["long_name"]
    data_type = row["data_type"]
    data_corr = row["data_corr"]


    print(code)

    for country in countries_list.country_id:

        code_final = f"{code}/{country}" #?collapse=M
        print(code_final)

        # data = pd.DataFrame( taceconomics.get(f'data/{code_final}')['data'] )
        data = taceconomics.getdata(code_final)
        
        if data is not None:
            # TODO : faire des calculs stats ou tout ajout

            data = data.reset_index()
            data["country_id"] = country
            data["symbol"] = symbol
            data.columns = ["timestamp","value","coujntry_id","symbol"]

            base_finale = pd.concat([base_finale,data])
        else:
            print(f"No data for contry: {country}")


tt = base_finale[base_finale.symbol=="gdp"].pivot_table(values="value",columns="coujntry_id",index="timestamp")
tt = tt.rolling(8).mean()
tt = pd.melt(tt.reset_index(),id_vars='timestamp')
tt["symbol"] = "gdp_ma8"

base_finale = pd.concat([base_finale,tt])