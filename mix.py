import json,subprocess,numpy as np,soundfile as sf,os,glob,random
random.seed(7)
SR=16000
def load(f):
    out=subprocess.run(['ffmpeg','-loglevel','error','-i',f,'-ar',str(SR),'-ac','1','-f','f32le','-'],capture_output=True,check=True).stdout
    return np.frombuffer(out,dtype=np.float32).copy()
noises={os.path.basename(f)[:-4]:load(f) for f in sorted(glob.glob('noise/*.wav'))}
names=list(noises)
meta=json.load(open('clean/meta.json'))
rows=[]
os.makedirs('mix',exist_ok=True)
for i,m in enumerate(meta):
    s=load(m['f'])
    s=np.concatenate([np.zeros(int(.6*SR)),s,np.zeros(int(.6*SR))]).astype(np.float32)
    nname=names[i%len(names)]
    n=noises[nname]
    while len(n)<len(s): n=np.concatenate([n,n])
    st=random.randint(0,len(n)-len(s)); n=n[st:st+len(s)]
    ps=np.mean(s[s!=0]**2); pn=np.mean(n**2)+1e-12
    for snr in [20,10,5,0]:
        g=np.sqrt(ps/(pn*10**(snr/10)))
        x=s+g*n; x=x/max(1,np.abs(x).max()/0.95)
        f=f"mix/{os.path.basename(m['f'])[:-4]}_{nname}_{snr}.wav"
        sf.write(f,x,SR); rows.append({**m,'mix':f,'noise':nname,'snr':snr})
json.dump(rows,open('mix/meta.json','w'),indent=1)
print(len(rows),'mixes')
