import re, jellyfish
from rapidfuzz import fuzz
from intent2 import norm, clean
APPS=["claude","codex","terminal","chrome","slack","vscode","notes","whatsapp","gmail","opencode"]
ALIAS={"cloud":"claude","clock":"claude","cloth":"claude","clog":"claude","clod":"claude","clawed":"claude","plot":"claude","code x":"codex","codecs":"codex","google chrome":"chrome","vs code":"vscode","chroman":"chrome","club":"claude","clubs":"claude","flock":"claude","claud":"claude","clowd":"claude","products":"codex","codec":"codex","codeks":"codex","kodak":"codex"}
def sim(a,b):
    # spelling + sound: metaphone and first-letter-insensitive
    s1=fuzz.ratio(a,b); s2=fuzz.ratio(jellyfish.metaphone(a),jellyfish.metaphone(b))
    s3=fuzz.ratio(a[1:],b[1:])
    return max(s1,s2,s3*0.9)
def app_of(tok):
    if tok in ALIAS: return ALIAS[tok]
    best=max(APPS,key=lambda x:sim(tok,x)); return best if sim(tok,best)>=45 else tok
FIXED={"send it":"SEND","new chat":"NEW_CHAT","scratch that":"UNDO","undo that":"UNDO","stop listening":"SLEEP"}
def find_cmd(w):
    # a command phrase anywhere in a short burst wins (bystander words around it are dropped)
    for i in range(min(len(w),4)):
        for k,v in FIXED.items():
            kw=k.split(); seg=" ".join(w[i:i+len(kw)])
            if len(w)-i>=len(kw) and fuzz.ratio(seg,k)>=78: return v,i
    return None,None
def parse(text):
    n=norm(text)
    if not n: return ("NONE",None)
    w=n.split()
    # 'open X' anywhere in the first 3 words
    for i in range(min(3,len(w))):
        if w[i] in ("open","opened","oven","hope") or fuzz.ratio(w[i],"open")>=75:
            rest=w[i+1:]
            if len(rest)>=2 and " ".join(rest[:2]) in ALIAS: tok=" ".join(rest[:2]); tail=rest[2:]
            elif rest and (rest[0] in ALIAS or rest[0].startswith("chrom")): tok=rest[0]; tail=rest[1:]
            else: tok=rest[0] if rest else ""; tail=rest[1:]
            t=" ".join(tail).replace("and search","and search")
            m=re.match(r"(and )?search (for )?(.*)",t)
            if m: return ("OPEN_SEARCH",(app_of(tok),m.group(3)))
            return ("OPEN",app_of(tok))
    if len(w)<=7:
        v,i=find_cmd(w)
        if v: return (v,None)
    if fuzz.ratio(w[0],"type")>=75 or w[0] in("tight","taipei","tie","typed"):
        return ("TYPE",clean(" ".join(w[1:])))
    return ("TYPE",clean(n))
def same(a,b):
    if a[0]!=b[0]: return False
    if a[0]=="TYPE":
        import jiwer; return jiwer.wer(a[1] or "-",b[1] or "-")<=0.1
    if a[0]=="OPEN_SEARCH":
        import jiwer; return a[1][0]==b[1][0] and jiwer.wer(a[1][1] or "-",b[1][1] or "-")<=0.15
    return a==b
