# Vox v8: whisper base.en finds the CONTROL skeleton (open/send/new chat/scratch) from near-speaker words;
# dictation = near-speaker speech between controls, re-decoded by parakeet on the raw audio.
import json,numpy as np,soundfile as sf,sherpa_onnx
from scipy.signal import sosfilt
import filt3
from fair import fair,align
from filt3 import REF
from intent3 import norm,APPS
from strict import cmd_start,parse
from engine4 import dedupe
SR=16000
D='models/sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8'
rec=sherpa_onnx.OfflineRecognizer.from_transducer(encoder=f'{D}/encoder.int8.onnx',decoder=f'{D}/decoder.int8.onnx',joiner=f'{D}/joiner.int8.onnx',tokens=f'{D}/tokens.txt',model_type='nemo_transducer',num_threads=2)
def pk(x):
    st=rec.create_stream(); st.accept_waveform(SR,x); rec.decode_stream(st); return norm(st.result.text).split()
def clip(w):
    for i in range(min(len(w),6)):
        c=cmd_start(w,i)
        if c and c[0]=='TYPE': w=w[i+1:]; break
        if c and c[0]=='OPEN': w=w[i+2:]; break
    out=[]
    for i in range(len(w)):
        c=cmd_start(w,i)
        if c and c[0] not in('TYPE',): break
        out.append(w[i])
    return " ".join(out)
def go(n,d,src,wf='demo/words_{n}.json',minw=3):
    raw,_=sf.read(f'demo/{n}.wav',dtype='float32')
    sig,_=sf.read(f'demo/{n}{src}.wav',dtype='float32'); sig=sosfilt(filt3.sos,sig)
    def e(a,b): b=max(b,a+800); return 10*np.log10(np.mean(sig[a:b]**2)+1e-10)
    hist=[]; W=[]
    for bu in json.load(open(wf.format(n=n))):
        X=dedupe([tuple(w) for w in bu['w']])
        if not X: continue
        E=[e(w[1],w[2]) for w in X]; hist+=E; hist=hist[-60:]; lvl=np.percentile(hist,85)
        for w,x in zip(X,E):
            if x>=lvl-d:
                for p in norm(w[0]).split(): W.append((p,w[1],w[2]))
    flat=[w[0] for w in W]; ev=[]; i=0
    while i<len(flat):
        c=cmd_start(flat,i)
        if c and c[0]=='OPEN':
            p=parse(" ".join(flat[i:i+2]))
            if p[0]=='OPEN' and p[1] in APPS: ev.append([p,W[i][1],W[i+1][2]])
            i+=2
        elif c and c[0]=='TYPE': ev.append([('TYPEWORD',None),W[i][1],W[i][2]]); i+=1
        elif c: ev.append([(c[0],None),W[i][1],W[i+c[1]-1][2]]); i+=c[1]
        else: i+=1
    # collapse duplicate controls within 1.5 s
    E2=[]
    for x in ev:
        if E2 and x[0]==E2[-1][0] and x[0][0]!='TYPEWORD' and x[1]-E2[-1][2]<1.5*SR: continue
        E2.append(x)
    out=[]; T=[]
    for k,x in enumerate(E2):
        kind=x[0][0]
        if kind!='TYPEWORD': out.append(x[0]); T.append(x[2])
        nxt=E2[k+1] if k+1<len(E2) else None
        fill = kind=='TYPEWORD' or (kind in('OPEN','NEW_CHAT','UNDO') and not (nxt and nxt[0][0]=='TYPEWORD'))
        if not fill: continue
        a=x[2] if kind!='TYPEWORD' else x[1]
        b=nxt[1] if nxt else len(raw)
        inner=[w for w in W if w[1]>=a-800 and w[2]<=b+800 and not (x[1]<=w[1]<=x[2])]
        if inner:
            t=clip(pk(raw[max(0,inner[0][1]-1600):min(inner[-1][2]+3200,b)]))
            if len(t.split())>=minw: out.append(('TYPE',t)); T.append(inner[-1][2])
    go.T=T
    return out
if __name__=='__main__':
    for n in ['room10','room5']:
        for src in ['','_gt']:
            for d in [6,8,10,99]:
                o=go(n,d,src); print(n,src or 'raw',d,fair(o))
    for n,d,src in [('room10',10,''),('room5',8,'_gt')]:
        o=go(n,d,src); p=align(o); print('==',n,d,src,fair(o))
        for x in o: print('   ',x)
