import json,sys,time,numpy as np,soundfile as sf
from faster_whisper import WhisperModel
from seg import Gate,SR,F
PROMPT="open claude, open codex, open terminal, send it, new chat, scratch that, type"
m=WhisperModel('base.en',device='cpu',compute_type='int8',cpu_threads=2); m.transcribe(np.zeros(SR,np.float32))
for n in sys.argv[1:]:
    raw,_=sf.read(f'demo/{n}.wav',dtype='float32'); den,_=sf.read(f'demo/{n}_gt.wav',dtype='float32')
    L=min(len(raw),len(den)); raw=raw[:L]; den=den[:L]
    g=Gate(up=3,down=2,hang=12); bursts=[]
    for i in range(0,L-F,F):
        r=g.push(den[i:i+F])
        if not r: continue
        a=max(0,r[0]*F-6000); b=min(L,r[1]*F+1600); t=time.time()
        segs,_=m.transcribe(raw[a:b],language='en',beam_size=1,temperature=0.0,initial_prompt=PROMPT,condition_on_previous_text=False,
            word_timestamps=True,no_repeat_ngram_size=3,repetition_penalty=1.15,compression_ratio_threshold=2.0,no_speech_threshold=0.6)
        W=[(w.word,a+int(w.start*SR),a+int(w.end*SR),float(w.probability)) for z in segs for w in z.words]
        bursts.append({"a":a,"b":b,"ms":int((time.time()-t)*1000),"w":W})
    json.dump(bursts,open(f'demo/words_{n}.json','w')); print(n,len(bursts),'bursts')
