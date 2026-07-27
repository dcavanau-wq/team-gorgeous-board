#!/usr/bin/env python3
"""Read codes.json (source of truth: per-person B/S/E/X per date) -> data.json (computed board data).
Used by the board shell (index.html fetches data.json) and by the automated updater."""
import json, datetime

cfg = json.load(open('codes.json'))
PROG_START = datetime.date.fromisoformat(cfg['programStart'])
CLOSED = set(datetime.date.fromisoformat(d) for d in cfg.get('closedDays', []))
DISPLAY = {"Madison Chitwood": "Maddy Chitwood"}
VALID = {'B','S','E','X'}

# window end = latest date anyone has a code
all_dates = [datetime.date.fromisoformat(d) for p in cfg['people'] for d in p['codes']]
end_d = max(all_dates) if all_dates else PROG_START
start_d = PROG_START
dates = []
d = start_d
while d <= end_d:
    dates.append(d); d += datetime.timedelta(days=1)

people = []
for pinfo in cfg['people']:
    name = DISPLAY.get(pinfo['name'], pinfo['name'])
    role = pinfo['role']; codes = pinfo['codes']
    days={}; seq=[]; comp=part=miss=0; pts=0.0
    for dt in dates:
        iso=dt.isoformat()
        if dt in CLOSED: days[iso]='CLOSED'; continue
        v=codes.get(iso,'')
        if v not in VALID: days[iso]='OFF'; continue
        days[iso]=v
        if v=='B': comp+=1; pts+=1.0; seq.append('B')
        elif v in ('S','E'): part+=1; pts+=0.5; seq.append('P')
        elif v=='X': miss+=1; seq.append('X')
    cur=0
    for v in reversed(seq):
        if v in ('B','P'): cur+=1
        else: break
    longc=run=0
    for v in seq:
        if v=='B': run+=1; longc=max(longc,run)
        else: run=0
    worked=comp+part+miss
    BADGES=[(60,'👑'),(30,'💎'),(14,'🔥'),(7,'⭐'),(3,'🥉')]
    badge=next((e for t,e in BADGES if cur>=t),'')
    th=[3,7,14,30,60]; nxt=next((t for t in th if cur<t),None)
    if nxt:
        prev=max([0]+[t for t in th if t<=cur]); prog=(cur-prev)/(nxt-prev) if nxt>prev else 0
        emo_next=dict((t,e) for t,e in BADGES)[nxt]; to_next=nxt-cur
    else:
        prog=1.0; emo_next='👑'; to_next=0
    people.append(dict(name=name,role=role,streak=cur,complete=comp,partial=part,missed=miss,
        points=round(pts,1),worked=worked,longestComplete=longc,badge=badge,
        progress=round(prog,3),nextEmoji=emo_next,toNext=to_next,days=days))

first_sun = start_d - datetime.timedelta(days=(start_d.weekday()+1)%7)
last_sat  = end_d + datetime.timedelta(days=(5-end_d.weekday())%7)
all_days=[]; d=first_sun
while d<=last_sat: all_days.append(d); d+=datetime.timedelta(days=1)
weeks=[all_days[k:k+7] for k in range(0,len(all_days),7)]
week_objs=[]
for grp in weeks:
    a,b=grp[0],grp[-1]
    label=f"{a.strftime('%b')} {a.day}–{b.day}" if a.month==b.month else f"{a.strftime('%b')} {a.day} – {b.strftime('%b')} {b.day}"
    week_objs.append(dict(label=label,dates=[x.isoformat() for x in grp]))

data=dict(people=people,weeks=week_objs,dataStart=start_d.isoformat(),dataEnd=end_d.isoformat(),
          updated=cfg.get('updated',''))
json.dump(data, open('data.json','w'))
print("data.json written. dataEnd=",end_d.isoformat(),"people=",len(people))
