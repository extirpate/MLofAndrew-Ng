import pandas as pd
import numpy  as np

class Calc(object):
    def __init__(self):
        pass

    #根据参数表中的工厂参数表获得每小时所有工厂提供的每小时基础加工数量（base_hour_p),
    #每个槽位一次投放的最大量(per_slot_storage)
    @property
    def factory_base(self):
        #获得工厂参数基础数据
        df=pd.read_excel('../其他文件/basedata.xlsx',skiprows=1,na_values=0,nrows=20,index_col='lev',na_filter=True
                         ,usecols=['lev','cost','get','hourP','storage'])
        df['cost']=df['cost'].astype(np.float64)
        df['get']=df['get'].astype(np.float64)
        total_cost_iron=self.__calc_fac_needs(df)
        df=df.loc[list(self.base_data['factories']),:]
        self.base_hour_p=df['hourP'].sum() #每小时4个工厂提供的基础加工量
        self.per_slot_storage=df['storage'].sum() #4个加工厂提供的材料投放量,每个槽的投放量
        return {'fac_base':self.base_hour_p,'fac_store':self.per_slot_storage,'total_cost_iron':total_cost_iron}

    def __calc_fac_needs(self,df:pd.DataFrame):
        total_cost=0
        for i in list(self.base_data['factories']):
            this_one_need= list(df.loc[df.index>=i,['cost']].sum())[0]
            total_cost+=this_one_need
        return total_cost





    #根据参数表中的自定义参数，获取基本配置信息
    #加成后的每小时加工数量(produce),加成后的每个槽位存储量(storage),满负荷加工时间(hours,mins),通道数(slots)
    @property
    def base_data(self):
        df=pd.read_excel('../其他文件/basedata.xlsx',skiprows=49,index_col='index',nrows=15,usecols=['index','datas'])
        df=df.dropna()
        def got(a):
            b=eval(a)
            d={}
            for i in range(len(b)):
                str='{{ \'ac{}\':{}}}'.format(i+1,b[i])
                dic=eval(str)
                d.update(dic)
            return d
        self.result={'fac_rate':df.loc[['fac_rate'],'datas'][0],
                'fac_store':df.loc[['fac_store'],'datas'][0],
                'buy_rate':df.loc[['buy_rate'],'datas'][0],
                'buy_store':df.loc[['buy_store'],'datas'][0],
                'slots':df.loc[['slots'],'datas'][0],
                'poisons':got(df.loc[['poisons'],'datas'][0]),
                'factories':eval(df.loc[['factories'],'datas'][0]),
                'target_resist':df.loc[['target_resist'],'datas'][0],
                'spe_provide':df.loc[['spe_provide'],'datas'][0],
                'having_posi':df.loc[['having_posi'],'datas'][0],
                'having_iron':df.loc[['having_iron'],'datas'][0],
                'grows_posi':df.loc[['grows_posi'],'datas'][0],
                'grows_iron':df.loc[['grows_iron'],'datas'][0],
                'iron_dis':df.loc[['iron_dis'],'datas'][0],
                }
        return self.result
    @property
    def effective(self):
        produce = self.factory_base['fac_base']*(1+self.base_data['fac_rate']+self.base_data['buy_rate'])/1.013333333
        #经验观察值，而非面板写的50%提升，也不是18%+50%,
        storage = self.factory_base['fac_store']+self.base_data['buy_store']+self.base_data['fac_store']
        hours = storage//produce
        mins = round((storage/produce-hours)*60,2)
        #加成后每个通道每小时的加工数量，  每个通道的储量,  满负荷下可以加工多少小时，分钟
        return {'produce':round(produce,2), 'storage':storage, 'hours':hours,'mins':mins}


    #根据参数文件，计算需要的病毒等级数(needs)
    def needs(self,need:int):
        nowlevs=self.base_data['poisons']
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
        needs=needs.iloc[0:need,:]
        #返回dataframe， 第一列是ac等级,第二列是需要的数值
        return needs

    #计算需要多少病毒材料到目标抗性
    #0:数量
    #1:df代表明细
    @property
    def poison_result(self):
        # nowlevs={'ac1':20,'ac2':18,'ac3':14,'ac4':12}
        nowlevs=self.base_data['poisons']
        # talent_prov=6 #假设蓝色专精3+11+11=25点，提供600专精
        talent_prov=self.base_data['spe_provide'] #假设蓝色专精3+11+11=25点，提供600专精
        # target=75 #目标毒抗等级8000
        target=self.base_data['target_resist'] #目标毒抗等级8000
        #结合病毒所等级，专精，目标专精，计算还需要的病毒所等级
        need=self.poison(nowlevs,talent_prov,target)
        df=self.needs(need)
        need_poison=df['cost'].sum()
        return need,need_poison,df[['ac','cost']]


    def poison(self,nowlevs:dict,talent_prov:int,target:int):
        import functools
        nowlev = functools.reduce(lambda x,y:x+y,nowlevs.values())
        need=target-talent_prov-nowlev
        return need

if __name__ =='__main__':
    a = Calc()
    target=a.base_data['target_resist']
    levs=a.base_data['poisons']
    totallevs=sum(list(levs.values()))
    poisons=list(a.base_data['poisons'].values())
    print(list(poisons))
    print('当前4个病毒工厂等级分别为：{},共提供病毒等级：{},同时专精提供的病毒等级{}'.format(poisons,totallevs,a.base_data['spe_provide']))
    result=a.poison_result
    need_levs=result[0]
    posi_material=result[1]
    details=result[2]
    print('-------------1.关于土地生产所需材料----------')
    print('毒抗到目标{}级，还需要：{}级，共计{}材料'.format(target,need_levs,posi_material))
    print('需要的ac及等级明细，开销如下：')
    print(details)
    now_have_p=a.base_data['having_posi']
    need_p=posi_material-int(now_have_p)
    print('如上所示，一共需要{}病毒材料,扣除现有的{},还需要:{}材料'.format(posi_material,now_have_p,need_p))
    grows_posi=a.base_data['grows_posi']
    grows_iron=a.base_data['grows_iron']
    print('目前每小时土地收获{}病毒材料,{}复合材料,每小时共收获材料{}'.format(grows_posi,grows_iron,grows_posi+grows_iron))
    hours_grow=round(need_p/grows_posi,2)
    days_grow=round(hours_grow/24,2)
    print('树田产出目标所需量病毒材料要{}小时,折合{}天'.format(hours_grow,days_grow))

    need_iron= a.factory_base['total_cost_iron']
    hav_iron=a.base_data['having_iron']
    real_need_iron=round((need_iron-hav_iron)*(1-a.base_data['iron_dis']))
    hours_iron=round(real_need_iron/grows_iron)
    days_iron=round(hours_iron/24,2)
    print('4工厂升至20级，尚需{}复合材料,按每小时土地收获{}油铁，需要{}小时,折合{}天'.format(real_need_iron,a.base_data['grows_iron'],hours_iron,days_iron))


    print('-----------2.关于加工能力-----------')
    produces=a.effective['produce']
    slots=a.base_data['slots']
    hourP=round(produces*slots,2)
    print('单通道每小时加工{},  {}个槽合计每小时加工:{}'.format(produces,slots,hourP))

    hours_p=round((need_p+real_need_iron)/hourP,2)
    days_p=round(hours_p/24,2)
    print('加工复合材料及病毒材料到目标等级需要:{}小时,折合{}天'.format(hours_p,days_p))

