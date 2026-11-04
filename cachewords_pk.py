import json,sys,time,os,numpy as np,soundfile as sf,sherpa_onnx
from seg import Gate,SR,F
D='models/sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8'
rec=sherpa_onnx.OfflineRecognizer.from_transducer(encoder=f'{D}/encoder.int8.onnx',decoder=f'{D}/decoder.int8.onnx',joiner=f'{D}/joiner.int8.onnx',tokens=f'{D}/tokens.txt',model_type='nemo_transducer',num_threads=2)
HANG=int(os.environ.get('HANG','12'))
for n in sys.argv[1:]:
    raw,_=sf.read(f'demo/{n}.wav',dtype='float32'); den,_=sf.read(f'demo/{n}_gt.wav',dtype='float32')
    L=min(len(raw),len(den)); raw=raw[:L]; den=den[:L]
    g=Gate(up=3,down=2,hang=HANG); bursts=[]
    for i in range(0,L-F,F):
        r=g.push(den[i:i+F])
        if not r: continue
        a=max(0,r[0]*F-6000); b=min(L,r[1]*F+1600); t=time.time()
        st=rec.create_stream(); st.accept_waveform(SR,raw[a:b]); rec.decode_stream(st); res=st.result
        toks=list(res.tokens); ts=list(res.timestamps); W=[]
        for k,(tk,t0) in enumerate(zip(toks,ts)):
            t1=ts[k+1] if k+1<len(ts) else (b-a)/SR
            if tk.startswith(' ') or tk.startswith('▁') or not W: W.append([tk.replace('▁',' '),a+int(t0*SR),a+int(t1*SR),1.0])
            else: W[-1][0]+=tk; W[-1][2]=a+int(t1*SR)
        bursts.append({"a":a,"b":b,"ms":int((time.time()-t)*1000),"w":W,"text":res.text})
    json.dump(bursts,open(f'demo/words_{n}_pk_{HANG}.json','w')); print(n,len(bursts),'bursts', [bu['text'] for bu in bursts][:6], 'median ms',int(np.median([bu['ms'] for bu in bursts])))
