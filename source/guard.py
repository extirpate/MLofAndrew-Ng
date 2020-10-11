import pandas as pd
import numpy  as np


def factory(levs):
    #获得工厂参数基础数据
    df=pd.read_excel('../其他文件/basedata.xlsx',skiprows=1,na_values=0,nrows=20,index_col='lev',na_filter=False)
    df['cost']=df['cost'].astype(np.float64)
    df['get']=df['get'].astype(np.float64)
    df=df.loc[levs,:]
    base_hour_p=df['hourP'].sum() #每小时4个工厂提供的基础加工量
    per_slot_storage=df['storage'].sum() #4个加工厂提供的材料投放量
    return base_hour_p,per_slot_storage

def countFactory():
    df=pd.read_excel('../其他文件/basedata.xlsx',skiprows=49,index_col='index',nrows=9,usecols=['index','datas'])
    df=df.dropna()
    fac_rate=df.loc[['fac_rate'],'datas'][0]
    fac_store=df.loc[['fac_store'],'datas'][0]
    buy_rate=df.loc[['buy_rate'],'datas'][0]
    buy_store=df.loc[['buy_store'],'datas'][0]
    slots=df.loc[['slots'],'datas'][0]
    levs = list(df.loc[['factories'],'datas'][0])
    base_hour_p=factory(levs)[0]
    per_slot_storage=factory()[1]
    # produce = base_hour_p*(1+fac_rate)*1.405 #经验观察值，而非面板写的50%提升，也不是18%+50%,所以这里没有使用buy_rate
    produce = base_hour_p*(1+fac_rate+buy_rate)/1.013333333 #经验观察值，而非面板写的50%提升，也不是18%+50%,所以这里没有使用buy_rate

    storage = per_slot_storage+buy_store+fac_store
    hours = storage//produce
    mins = round((storage/produce-hours)*60,2)
    return produce, storage, hours,mins,slots
def get_needs(nowlevs:dict,need:int):
    df=pd.read_excel('../其他文件/basedata.xlsx',skiprows=25,nrows=19,usecols=['ac1','ac1cost',
                                                                           'ac2','ac2cost',
                                                                           'ac3','ac3cost',
                                                                           'ac4','ac4cost'])
    needs=pd.DataFrame()
    for i in range(4):
        tag=str(i+1)
        df_ac:pd.DataFrame=df.loc[df['ac'+tag]>=nowlevs['ac'+tag],['ac'+tag,'ac'+tag+'cost']]
        df_ac['ac'+tag]=df_ac['ac'+tag].apply(str)
        df_ac['ac']='ac'+tag+'_'+df_ac['ac'+tag]
        df_ac['cost']=df_ac['ac'+tag+'cost']
        df_ac=df_ac.loc[:,['ac','cost']]
        # print(df_ac)
        needs=needs.append(df_ac)
    needs.sort_values(by='cost',inplace=True)
    needs.reset_index(inplace=True,drop=True)
    #返回dataframe， 第一列是ac等级,第二列是需要的数值
    return needs

#计算需要多少病毒材料到目标抗性
#0:数量
#1:df代表明细
def get_poison_result():
    nowlevs={'ac1':20,'ac2':18,'ac3':14,'ac4':12}
    talent_prov=6 #假设蓝色专精3+11+11=25点，提供600专精
    target=75 #目标毒抗等级8000
    need=poison(nowlevs,talent_prov,target)  #结合病毒所等级，专精，目标专精，计算还需要的病毒所等级
    df=get_needs(nowlevs,need)
    df=df.loc[0:need-1]
    need_poison=df['cost'].sum()
    return need_poison,df[['ac','cost']]


def poison(nowlevs:dict,talent_prov:int,target:int):
    import functools
    nowlev = functools.reduce(lambda x,y:x+y,nowlevs.values())
    need=target-talent_prov-nowlev
    return need

now_have_p=1900000
target=get_poison_result()
levs=target[1].iloc[:,0].count()
poisons=target[0]
print('到目标还需要：{}级，{}材料'.format(levs,poisons))
print('需要的ac及等级明细，开销如下：')
print(target[1])
need_p=poisons-now_have_p
print('一共需要{}病毒材料,扣除现有的{},还需要:{}材料'.format(poisons,now_have_p,need_p))
# print(need_p[0])
# print(need_p[1])

produces=countFactory()
slots=produces[4]
hourP=round(produces[0]*slots,2)
print('单通道每小时加工{},  {}个槽合计每小时加工:{}'.format(round(produces[0],2),slots,hourP))
grows=1600*91*(1+0.29)
print('每小时可以产出{}'.format(grows))
hours=round(need_p/hourP,2)
days=round(hours/24,2)
print('加工需要:{}小时,折合{}天'.format(hours,days))
hours_grow=round(need_p/grows,2)
days_grow=round(hours_grow/24,2)
print('产出目标所需量{}小时,折合{}天'.format(hours_grow,days_grow))