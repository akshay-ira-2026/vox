import json,sys,collections,jiwer
from intent3 import parse,norm,same
for mname in sys.argv[1:]:
    try: res=json.load(open(f'res_{mname}.json'))
    except: print(mname,"missing"); continue
    agg=collections.defaultdict(list)
    for x in res:
        g=parse(x['ref']); h=parse(x['hyp']); x['ok2']=same(g,h); x['in2']=g[0]==h[0]
        agg[(x['cond'],x['snr'])].append(x)
    print("==",mname)
    for k in sorted(agg):
        xs=agg[k]
        print(k,"WER%.1f"%(100*jiwer.wer([norm(x['ref']) or '-' for x in xs],[norm(x['hyp']) or '-' for x in xs])),"cmd%.0f"%(100*sum(x['ok2'] for x in xs)/len(xs)),"intent%.0f"%(100*sum(x['in2'] for x in xs)/len(xs)))
    bad=[x for x in res if not x['ok2'] and x['cond']=='raw' and x['snr']>=5]
    print(len(bad),"raw fails >=5dB")
    for x in bad[:20]: print(" ",x['snr'],x['noise'],'|',x['ref'],'|',x['hyp'])
