import json,time,sys,resource,soundfile as sf,sherpa_onnx
from intent3 import norm
d=sys.argv[1]
M="models/sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8/"
rec=sherpa_onnx.OfflineRecognizer.from_transducer(encoder=M+"encoder.int8.onnx",decoder=M+"decoder.int8.onnx",joiner=M+"joiner.int8.onnx",tokens=M+"tokens.txt",num_threads=2,model_type="nemo_transducer",decoding_method="greedy_search")
rows=json.load(open('mix/meta.json')); res=[]
for r in rows:
    p=r['mix'].replace('mix/',d+'/'); x,sr=sf.read(p,dtype='float32'); s=time.time()
    st=rec.create_stream(); st.accept_waveform(sr,x); rec.decode_stream(st)
    res.append({"snr":r['snr'],"noise":r['noise'],"cond":d,"ref":norm(r['text']),"hyp":norm(st.result.text),"sec":time.time()-s})
tag=f"parakeet_{d}"
json.dump(res,open(f'res_{tag}.json','w'))
print(tag,"peakMB",resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024,"lat%.2f"%(sum(x['sec'] for x in res)/len(res)),"total_s")
