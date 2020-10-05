import pandas as pd
import numpy  as np
def factory():
    df=pd.read_excel('../其他文件/basedata.xlsx',skiprows=1,na_values=0,nrows=20,index_col='lev',na_filter=False)
    df['cost']=df['cost'].astype(np.float64)
    df['get']=df['get'].astype(np.float64)
    levs=[10,10,10,12]
    df=df.loc[levs,:]
    base_hour_p=df['hourP'].sum() #每小时4个工厂提供的基础加工量
    per_slot_storage=df['storage'].sum() #4个加工厂提供的材料投放量
    return base_hour_p,per_slot_storage
df=pd.read_excel('../其他文件/basedata.xlsx',skiprows=26,index_col='index',nrows=4,usecols=['index','datas'])
df=df.dropna()
print(df)
fac_rate=df.loc[['fac_rate'],'datas'][0]
fac_store=df.loc[['fac_store'],'datas'][0]
buy_rate=df.loc[['buy_rate'],'datas'][0]
buy_store=df.loc[['buy_store'],'datas'][0]

base_hour_p=factory()[0]
per_slot_storage=factory()[1]
#452000
produce = base_hour_p*(1+fac_rate)*(1+buy_rate)
storage = per_slot_storage+buy_store+fac_store
print(produce)
print(storage)