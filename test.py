#!/usr/bin/env python
# coding: utf-8

# In[32]:


import pandas as pd
import bs4
import requests
import re 
import numpy as np
#크롤링 목적 사이트
targetUrl = "https://www.premierinjuries.com/injury-table.php"
targetInfo = {}
#크롤링 후 목적 데이터 추출
try:
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/5'
    resp = requests.get(targetUrl, headers={'User-Agent': user_agent})
    if resp.status_code == 200:
        html = resp.text
        soup = bs4.BeautifulSoup(html, "html.parser")
        tbody = soup.find('tbody')       
        
    else:
        pass
except Exception as e:
    print(e)

rows = tbody.find_all('tr')

for row in rows:
    row_data = []
    cells = row.find_all('td')
    for cell in cells:
        row_data.append(cell.text)

    if row_data:
        team_class = row.get('class')
        if team_class:
            team_number = team_class[1].split('_')[-1]
            if team_number not in targetInfo:
                targetInfo[team_number] = []
            targetInfo[team_number].append(row_data)
#팀명 추출
team = []
div_elements = tbody.find_all('div', class_='injury-team')
for div in div_elements:
    team.append(div.text)
#팀명 정규표현식
for i in range (0,len(team)):
    team[i] = re.sub(r"[^\uAC00-\uD7A30-9a-zA-Z\s]", "", team[i])
    team[i] = re.sub(" ","_", team[i])


# In[82]:



# 각 팀 번호와 팀명 매칭
dataframes = {}
for team_number, data in targetInfo.items():
df = pd.DataFrame(data)


df.columns = df.iloc[0]
df = df.iloc[1:]

df = df.drop(columns=df.columns[6])


for i in range(0,len(df.columns)):
    df[df.columns[i]] = df[df.columns[i]].str.replace(df.columns[i], '')

df["Injury Date"] = df["Further Detail"].str.split(': ').str[0]
df["Injury Detail"] = df["Further Detail"].str.split(': ').str[1]
df["Injury Date"] = np.where(df["Further Detail"].str.contains(':'), df["Injury Date"], np.nan)
df.loc[df["Injury Date"].isna(), "Injury Detail"] = df.loc[df["Injury Date"].isna(), "Further Detail"].str.split(': ').str[0]
df.columns = [re.sub(r"[^\uAC00-\uD7A30-9a-zA-Z\s]", "", col) for col in df.columns]
df.columns = [re.sub(" ", "_", col) for col in df.columns]
df = df.drop(columns="Further_Detail")
injury_Date = pd.to_datetime(df['Injury_Date'] + ', 2023', errors='coerce')
# "Potential_Return" 열의 값을 날짜로 변환
Potential_Return = pd.to_datetime(df['Potential_Return'], format='%d/%m/%Y', errors='coerce')
# "Potential_Return"과 "Injury_Date" 사이의 차이를 계산하여 새로운 열로 추가
df['Period'] = (Potential_Return- injury_Date).dt.days
df = df.drop(columns="Injury_Detail")
df = df.reset_index(drop=True)  

dataframes[team_number] = df

dict_arr = list(dataframes.keys())


# In[83]:


dict_arr = list(dataframes.keys())
combined_df = pd.concat([dataframes[key] for key in dict_arr[:19]], axis=0)


# In[84]:


combined_df


# In[85]:


#팀명 dataframe생성
teamDf = pd.DataFrame({'team': team})


# In[86]:


#db 접속, 데이터 베이스 엔진 생성을 위한 라이브러리
import pymysql  
from sqlalchemy import create_engine,types
#oracle,postgre,mySQL,mariadb 구분해주는 함수
import db_func as db
out_id = "root"
out_db = "mariadb"
out_ip = "127.0.0.1"
out_port = "3306"
out_db_name = "injury"
out_pw ="0000"


#### 문자컬럼에 대해서 varchar (100) 적용 _ 사용시 속도 SpeedUp 50배 
out_dbengine = db.dbengine(out_db)
out_engine = create_engine(out_dbengine.format(out_id,out_pw,out_ip,out_port,out_db_name)) 
#팀명 테이블 생성(테이블이름 : team)
tableName = "team"
out_data = teamDf
out_name = tableName

try : out_data.to_sql(name=out_name, if_exists="replace", con=out_engine,  index=True)
except Exception as e:#에러난거 적기
            print(e)        


# In[87]:


#리그 전체의 부상자 명단(테이블이름 : entire)
tableName = "entire"
out_data =  combined_df.iloc[:, :-2]
out_name = tableName
try : 
    out_data.to_sql(name=out_name, if_exists="replace", con=out_engine,  index=True)
    objectColumns = list(out_data.columns[out_data.dtypes == 'object'])
    typeDict={}
    maxLen = 100
    for i in range(0, len(objectColumns)):
        # dataframes[dict_arr[i]].str.len().max() 최대치 사용할 경우
        typeDict[ objectColumns[i] ] = types.VARCHAR(100)
        #### 문자컬럼에 대해서 varchar (100) 적용 _ 사용시 속도 SpeedUp 50배   
        out_data.to_sql(name=out_name, if_exists="replace", con=out_engine, dtype=typeDict, index=True)
    
except Exception as e:#에러난거 적기
            print(e)  


# In[89]:


#팀별 부상자 테이블 생성(테이블이름 : 팀 이름)
for i in range(0,19):
    try:        
        tableName = team[i]
        out_data = dataframes[dict_arr[i]]       
        out_name = tableName
        out_engine = create_engine(out_dbengine.format(out_id,out_pw,out_ip,out_port,out_db_name)) 
        #### 문자컬럼에 대해서 varchar (100) 적용 _ 사용시 속도 SpeedUp 50배 
        objectColumns = list(out_data.columns)
        typeDict={}
        maxLen = 100
        for i in range(0, len(objectColumns)):
            # dataframes[dict_arr[i]].str.len().max() 최대치 사용할 경우
            typeDict[ objectColumns[i] ] = types.VARCHAR(100)
        #### 문자컬럼에 대해서 varchar (100) 적용 _ 사용시 속도 SpeedUp 50배  
        out_engine.execute(f"DROP TABLE IF EXISTS {out_name}")
        out_data.to_sql(name=out_name, if_exists="replace", con=out_engine, dtype=typeDict, index=True)
        
    except Exception as e:#에러난거 적기
            print(e)

