import re
from rapidfuzz import fuzz
from intent3 import parse, norm
KEYS=[("send it",2),("scratch that",2),("new chat",2),("stop listening",2),("open",1),("type",1)]
SOUND={"type":["type","tight","typed","tie","taipei"],"open":["open","opened","oven","hope"]}
def split(text):
    """one breath can carry several commands: 'open claude type hello send it' -> 3 commands"""
    w=norm(text).split(); cuts=[0]; i=1
    while i<len(w):
        hit=False
        for k,n in KEYS:
            seg=" ".join(w[i:i+n])
            if (n==1 and w[i] in SOUND[k]) or (n==2 and fuzz.ratio(seg,k)>=80):
                # 'type' only starts a command right after an app name or a fixed command
                if k=="type" and not (cuts and parse(" ".join(w[cuts[-1]:i]))[0] in("OPEN","SEND","NEW_CHAT","UNDO")): break
                if k=="open" and parse(" ".join(w[cuts[-1]:i]))[0]=="TYPE" and i-cuts[-1]>1 and i+1<len(w) and len(w)-i>3: break
                cuts.append(i); hit=True; break
        i+=1
    cuts.append(len(w))
    return [" ".join(w[a:b]) for a,b in zip(cuts,cuts[1:]) if b>a]
def parse_all(text): return [parse(p) for p in split(text)]
