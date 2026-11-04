import json,time,sys,os,resource
from faster_whisper import WhisperModel
import jiwer, soundfile as sf, numpy as np
from intent import parse,norm
model_name=sys.argv[1]
m=WhisperModel(model_name,device="cpu",compute_type="int8",cpu_threads=2)
rows=json.load(open('mix/meta.json'))
PROMPT="open claude, open codex, open terminal, send it, new chat, scratch that, type"
res=[]
t0=time.time()
for r in rows:
    gold=parse(r['text'])
    for cond,path in [("raw",r['mix']),("den",r['mix'].replace('mix/','den/'))]:
        for vad in ([False,True] if cond=="den" else [False]):
            s=time.time()
            segs,_=m.transcribe(sf.read(path,dtype='float32')[0],language="en",beam_size=1,initial_prompt=PROMPT,vad_filter=vad,condition_on_previous_text=False)
            hyp=" ".join(x.text for x in segs).strip()
            dt=time.time()-s
            res.append({"snr":r['snr'],"noise":r['noise'],"cond":cond+("+vad" if vad else ""),"ref":norm(r['text']),"hyp":norm(hyp),
                        "cmd_ok":parse(hyp)==gold,"intent_ok":parse(hyp)[0]==gold[0],"sec":dt})
json.dump(res,open(f'res_{model_name}.json','w'))
rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
import collections
agg=collections.defaultdict(list)
for x in res: agg[(x['cond'],x['snr'])].append(x)
print(model_name,"peakRSS_MB",round(rss),"total_s",round(time.time()-t0))
for k in sorted(agg):
    xs=agg[k]; refs=[x['ref'] or "-" for x in xs]; hyps=[x['hyp'] or "-" for x in xs]
    print(k, "WER%.1f"%(100*jiwer.wer(refs,hyps)), "cmd%.0f"%(100*sum(x['cmd_ok'] for x in xs)/len(xs)), "intent%.0f"%(100*sum(x['intent_ok'] for x in xs)/len(xs)), "lat%.2f"%(sum(x['sec'] for x in xs)/len(xs)))
