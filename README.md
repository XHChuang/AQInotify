# 爬現空氣品質資訊並篩選特定高測站傳送訊息
依現行空氣品質嚴重惡化警告發布及緊急防制辦法，當污染物達到特定條件的時候就要啟動應變作為，而如何建立一個提醒機制
當空品惡化的時可以馬上知道哪裡不好，何種污染物，可以作為應變參考。

## 使用工具
* [python](https://www.python.org/)
  * requests
  * pandas
  * json
* [Line Notify](https://notify-bot.line.me/zh_TW/)

## 爬環保署空品資訊
現環保署有個公開資料平台，只要註冊會員取的apikey，即可很輕易的抓到相關的資訊，歷史資訊也可以！

[環保署開放資料平台](https://data.epa.gov.tw/)

[本次空品資料資料集](https://data.epa.gov.tw/dataset/detail/AQX_P_432)
```py
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
```
## 呈現資訊
有了空品資料之後，再來是要篩呈現的資訊，本次選擇兩種呈現方式，包含AQI值及PM<sub>2.5</sub>的濃度
```
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
```

## 發送訊息
再來就是要因應不同的情況來發送結果拉，這邊主要針對比較常見的紅色及橘色去做分類，並且把臭氧八小時的例外情況也給考慮進去了

```py
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
        r = requests.post("https://notify-api.line.me/api/notify",headers=headers, params=params1)    
    elif aqi.sum()>=1:#站橘情況
        if o3.sum()>=1 and pm.sum()<2 and pm10.sum()<2 and o32.sum()<2 and so2.sum()<2 and no2.sum()<2 and co8.sum()<2:
            k=0
            params1 = {"message":textO1+textA(df2)}
        elif o3.sum()>=2 and pm.sum()>2:#站橘但PM同超標
            k=1
            params1 = {"message":textO2+textB(df2)}
        else:
            k=1
            params1 = {"message":textO2+textA(df2)} ## 初級預警
        r = requests.post("https://notify-api.line.me/api/notify",headers=headers, params=params1)
```

最後的最後當然還是可以在後續寫個log，用於記錄每次爬蟲的結果跟成效，就因每個狀況需求不同拉~
