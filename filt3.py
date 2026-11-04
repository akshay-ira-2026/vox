import json,os,numpy as np,soundfile as sf
from scipy.signal import butter,sosfilt
from engine4 import dedupe
from strict import cmd_start,parse
from split import parse_all
from intent3 import norm,APPS,same
SR=16000; sos=butter(4,[300,3400],btype='band',fs=SR,output='sos')
REF=[parse(s) for s in json.load(open('demo/script.json'))]
def lcs(out):
    n,m=len(REF),len(out); D=[[0]*(m+1) for _ in range(n+1)]
    for i in range(n):
        for j in range(m): D[i+1][j+1]=D[i][j]+1 if same(REF[i],out[j]) else max(D[i][j+1],D[i+1][j])
    return D[n][m], m-D[n][m]
class Dict:
    def __init__(s): s.out=[]; s.armed=False; s.open=None; s.last=-10**9
    def feed(s,keep):
        flat=[];tt=[]
        for w,s0,s1,_ in keep:
            for p in norm(w).split(): flat.append(p); tt.append((s0,s1))
        i=0
        while i<len(flat):
            g0=tt[i][0]-(tt[i-1][1] if i else s.last); c=cmd_start(flat,i)
            if not c and s.open is not None and g0<1.6*SR:
                j=i
                while j<len(flat) and not (cmd_start(flat,j) and cmd_start(flat,j)[0]!="TYPE"): j+=1
                k=s.open; s.out[k]=parse(" ".join(["type",s.out[k][1]]+flat[i:j])); s.last=tt[j-1][1]; i=j; continue
            if (c and c[0]=="TYPE") or (not c and s.armed):
                j=i+(1 if c else 0); j0=j
                while j<len(flat):
                    c2=cmd_start(flat,j)
                    if c2 and c2[0]!="TYPE": break
                    if j>j0 and tt[j][0]-tt[j-1][1]>1.6*SR: break
                    j+=1
                p=parse(" ".join(flat[i:j]) if c else "type "+" ".join(flat[i:j]))
                if p[1]: s.out.append(p); s.open=len(s.out)-1
                s.armed=False; i=max(j,i+1)
            elif c and c[0]=="OPEN":
                p=parse(" ".join(flat[i:i+2]))
                if p[0]=="OPEN" and p[1] in APPS: s.out.append(p); s.armed=True; s.open=None
                i+=2
            elif c: s.out.append((c[0],None)); s.armed=c[0] in("NEW_CHAT","UNDO"); s.open=None; i+=c[1]
            else: s.open=None; i+=1
            s.last=tt[min(i,len(tt))-1][1]
def run(n,drop,src,wf,v=False):
    sig,_=sf.read(f'demo/{n}{src}.wav',dtype='float32'); sig=sosfilt(sos,sig)
    def e(a,b): b=max(b,a+800); return 10*np.log10(np.mean(sig[a:b]**2)+1e-10)
    B=json.load(open(wf.format(n=n))); hist=[]; D=Dict(); lats=[]
    for bu in B:
        W=dedupe([tuple(w) for w in bu['w']]); lats.append(bu['ms'])
        if not W: continue
        E=[e(w[1],w[2]) for w in W]; hist+=E; hist=hist[-60:]; lvl=np.percentile(hist,85)
        keep=[w for w,x in zip(W,E) if x>=lvl-drop]; D.feed(keep)
        if v: print('  ',"".join(k[0] for k in keep),'|X|',"".join(w[0] for w,x in zip(W,E) if x<lvl-drop))
    ok,fa=lcs(D.out); return ok,fa,int(np.median(lats)),D.out
def baseline(n,wf):
    B=json.load(open(wf.format(n=n))); out=[]
    for bu in B:
        t="".join(w[0] for w in bu['w'])
        out+=[p for p in parse_all(t) if p[0]!='NONE']
    return lcs(out)
if __name__=="__main__":
    for tag,wf in [('asr-raw','demo/words_{n}.json'),('asr-den','demo/words_{n}_base.en_12_den.json')]:
        for n in ['room10','room5']:
            print(tag,n,'BASELINE',baseline(n,wf),' '.join(f"{src or 'raw'}/d{d}:%d-%d"%run(n,d,src,wf)[:2] for src in ['','_gt'] for d in [6,8,10,99]))
