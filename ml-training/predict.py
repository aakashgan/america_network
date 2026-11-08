import json,sys,pathlib,pandas as pd
from xgboost import XGBRegressor
ROOT=pathlib.Path(__file__).resolve().parents[1];A=ROOT/'ml-training'/'artifacts'; cfg=json.loads((A/'preprocessing.json').read_text()); model=XGBRegressor();model.load_model(str(A/'model.json')); requests=json.load(sys.stdin);rows=[]
for r in requests:
 f=r.get('buildingAttributes',{}); rows.append({k:(1 if f.get(k) is True else 0 if f.get(k) is False else f.get(k,-1)) for k in cfg['features']})
pred=model.predict(pd.DataFrame(rows)[cfg['features']]);print(json.dumps([{'nodeId':r['nodeId'],'estimatedDamageFraction':max(0,min(1,float(p)))} for r,p in zip(requests,pred)]))
