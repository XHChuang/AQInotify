import requests
import pandas as pd
import json
import datetime ,time

'''
定義全域變數，設定發訊token及標準篩定
'''

now = datetime.datetime.now()
limAQ,limAQ2,limAQ3,limAQ4,limAQ5=100,150,200,300,400
limPM,limPM2,limPM3=35.5,54.5,150.5
limO32,limO33,limO34=125,165,205
limp10,limp102,limp103=101,255,355
limso2,limso22,limso23=76,186,305
limno2,limno22,limno23=101,361,650
limco8,limco82,limco83=9.5,12.5,15.5
apikey='your-api-key'

# 設定發訊
token1="token1" #放入你的token

## 爬環署AQIand空品資訊，並存入backup
def AQI_r():
    r=requests.get('https://data.epa.gov.tw/api/v2/aqx_p_432?api_key='+apikey)
    dfR=pd.DataFrame(json.loads(r.text)["records"])
    dfR.to_csv("AQI_T.csv",index=False) #所有測站
    filt = (dfR['county']=='南投縣')
    df1=dfR.loc[filt]
    df1.reset_index(inplace=True,drop=True)
    df1.to_csv("AQI_N.csv",index=False)
    df2=pd.read_csv("AQI_N.csv")#only南投測站
    df2.loc[:,'aqi'].astype(int)
    df2.loc[:,'pm2.5_avg'].astype(float)
    return df2,r

def textA(df1):#正常情況
    text=''
    for i in range(0,len(df1)):
        text=text+'\n'+df1['sitename'][i]+'：'+df1['pollutant'][i]+'('+str(df1['aqi'][i])+')'
    return text

def textB(df1):#臭氧八小時例外
    text=''
    for i in range(0,len(df1)):
        text=text+'\n'+df1['sitename'][i]+'：'+df1['pollutant'][i]+'('+str(df1['aqi'][i])+') PM2.5(\u03BCg/m3)：'+'('+str(df1['pm2.5_avg'][i])+')'
    return text

def AQI_msg(df1): #橘色情況
    filt = (df1['aqi']>limAQ)
    df2=df1.loc[filt]
    df2.reset_index(inplace=True,drop=True)
    o3=df1['pollutant']=='臭氧八小時'
    textO1='\n'+df1['publishtime'][0]+'現南投縣為橘色提醒'
    textO2='\n'+df1['publishtime'][0]+'現南投縣為初級預警'
    textR1='\n'+df1['publishtime'][0]+'現南投縣為紅色提醒'
    textR2='\n'+df1['publishtime'][0]+'現南投縣為中級預警'
    textR3='\n'+df1['publishtime'][0]+'現南投縣為紅色提醒及初級預警'
    o32,o33,o34=df1['o3']>limO32,df1['o3']>limO33,df1['o3']>limO34
    pm10,pm102,pm103=df1['pm10_avg']>limp10,df1['pm10_avg']>limp102,df1['pm10_avg']>limp103
    so2,so22,so23=df1['so2']>limso2,df1['so2']>limso22,df1['so2_avg']>limso23
    no2,no22,no23=df1['no2']>limno2,df1['no2']>limno22,df1['no2']>limno23
    co8,co82,co83=df1['co_8hr']>limco8,df1['co_8hr']>limco82,df1['co_8hr']>limco83
    aqi,aqi2,aqi3=df1['aqi']>limAQ,df1['aqi']>limAQ2,df1['aqi']>limAQ3
    pm,pm2,pm3=df1['pm2.5_avg']>limPM,df1['pm2.5_avg']>limPM2,df1['pm2.5_avg']>limPM3
    headers = {
    "Authorization": "Bearer " + token1,
    "Content-Type": "application/x-www-form-urlencoded"
    }
    print(o3.sum())
    print(pm.sum())
    if aqi2.sum()>=1:#站紅情況
        if o3.sum()>=1 and pm2.sum()<2 and pm102.sum()<2 and o33.sum()<2 and so22.sum()<2 and no22.sum()<2 and co82.sum()<2:
            k=0
            params1 = {"message":textR1+textA(df2)}
        elif o3.sum()>=2 and pm2.sum()>2:
            k=2
            params1 = {"message":textR2+textB(df2)}
        elif o3.sum()>=2 and pm.sum()>2:#站紅但PM同超標
            k=2
            params1 = {"message":textR3+textB(df2)}
        else:
            k=2
            params1 = {"message":textR2+textA(df2)} ## 中級預警
    
    elif aqi.sum()>=1:#站橘情況
        if o3.sum()>=1 and pm.sum()<2 and pm10.sum()<2 and o32.sum()<2 and so2.sum()<2 and no2.sum()<2 and co8.sum()<2:
            k=0
            params1 = {"message":textO1+textA(df2)}
        elif o3.sum()>=2 and pm.sum()>2:#站紅但PM同超標
            k=1
            params1 = {"message":textO2+textB(df2)}
        else:
            k=1
            params1 = {"message":textO2+textA(df2)} ## 中級預警

    r = requests.post("https://notify-api.line.me/api/notify",headers=headers, params=params1)

# df,r=AQI_r()
# AQI_msg(df)
