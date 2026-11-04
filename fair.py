import json,jiwer,numpy as np
from strict import parse
from intent3 import same
REF=[parse(s) for s in json.load(open('demo/script.json'))]
def align(out):
    # LCS on kind (+app), then score dictation by WER
    def m(a,b): return a[0]==b[0] and (a[0]!="OPEN" or a[1]==b[1])
    n,k=len(REF),len(out); D=[[0]*(k+1) for _ in range(n+1)]
    for i in range(n):
        for j in range(k): D[i+1][j+1]=D[i][j]+1 if m(REF[i],out[j]) else max(D[i][j+1],D[i+1][j])
    i,j=n,k; pairs=[]
    while i and j:
        if m(REF[i-1],out[j-1]) and D[i][j]==D[i-1][j-1]+1: pairs.append((i-1,j-1)); i-=1; j-=1
        elif D[i-1][j]>=D[i][j-1]: i-=1
        else: j-=1
    return dict(pairs)
def fair(out):
    p=align(out); ctl=[i for i,r in enumerate(REF) if r[0]!="TYPE"]; dic=[i for i,r in enumerate(REF) if r[0]=="TYPE"]
    ctl_ok=sum(1 for i in ctl if i in p)
    wers=[min(1.0,jiwer.wer(REF[i][1],out[p[i]][1] or "-")) if i in p else 1.0 for i in dic]
    false=len(out)-len(p)
    return dict(ctl=f"{ctl_ok}/{len(ctl)}",dict_wer=round(float(np.mean(wers)),3),false=false,typed_ok=sum(w<=0.1 for w in wers))
