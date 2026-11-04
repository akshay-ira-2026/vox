import re
from rapidfuzz import process, fuzz
APPS=["claude","codex","terminal","chrome","slack","vscode","notes","whatsapp","gmail","opencode"]
FILLERS=r"\b(um+|uh+|erm|hmm|like,|you know,)\b"
def norm(t):
    t=t.lower(); t=re.sub(r"[^\w\s']"," ",t); return re.sub(r"\s+"," ",t).strip()
def clean(t):
    t=re.sub(FILLERS,"",t,flags=re.I); t=re.sub(r"\b(\w+)( \1\b)+",r"\1",t,flags=re.I)
    return re.sub(r"\s+"," ",t).strip()
FIXED={"send it":"SEND","new chat":"NEW_CHAT","scratch that":"UNDO","undo that":"UNDO","stop listening":"SLEEP"}
def parse(text):
    n=norm(text)
    if not n: return ("NONE",None)
    m=process.extractOne(n,list(FIXED),scorer=fuzz.ratio)
    if m and m[1]>=78 and len(n.split())<=4: return (FIXED[m[0]],None)
    w=n.split()
    if fuzz.ratio(w[0],"open")>=75 or w[0] in("open","opened","oven","hope"):
        rest=" ".join(w[1:]); app_tok=w[1] if len(w)>1 else ""
        a=process.extractOne(app_tok,APPS,scorer=fuzz.ratio)
        tail=" ".join(w[2:])
        if tail.startswith("and search for "): return ("OPEN_SEARCH",(a[0] if a else app_tok, tail[len("and search for "):]))
        return ("OPEN",a[0] if a and a[1]>=60 else rest)
    if fuzz.ratio(w[0],"type")>=75 or w[0] in("tight","taipei","tie"):
        return ("TYPE",clean(" ".join(w[1:])))
    return ("TYPE",clean(n))
