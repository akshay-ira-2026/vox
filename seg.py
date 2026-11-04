import numpy as np, onnxruntime as ort
SR=16000; F=512
class Gate:
    """Near-field speech gate: Silero VAD + loudness above a rolling room floor.
    Room noise (babble, vacuum, fan) sets the floor; the person at the mic is louder than the room."""
    def __init__(s,path='models/silero_vad.onnx',up=4.0,down=2.5,hang=12,maxlen=9.0):
        so=ort.SessionOptions(); so.intra_op_num_threads=1; so.inter_op_num_threads=1
        s.v=ort.InferenceSession(path,so,providers=['CPUExecutionProvider'])
        s.st=np.zeros((2,1,128),np.float32); s.ctx=np.zeros(64,np.float32)
        s.hist=[]; s.up=up; s.down=down; s.hang=hang; s.maxf=int(maxlen*SR/F)
        s.insp=False; s.run=0; s.sil=0; s.start=0; s.n=0
    def vp(s,fr):
        o,s.st=s.v.run(None,{'input':np.concatenate([s.ctx,fr])[None,:].astype(np.float32),'state':s.st,'sr':np.array(SR,dtype=np.int64)}); s.ctx=fr[-64:]; return float(o[0][0])
    def push(s,fr):
        """returns (start_frame,end_frame) when a segment closes"""
        db=10*np.log10(np.mean(fr**2)+1e-10); p=s.vp(fr)
        s.hist.append(db); s.hist=s.hist[-94:]   # ~3 s
        floor=np.percentile(s.hist,20)
        out=None; i=s.n
        if not s.insp:
            s.run = s.run+1 if (p>0.4 and db>floor+s.up) else 0
            if s.run>=3: s.insp=True; s.start=i-4; s.sil=0
        else:
            s.sil = 0 if db>floor+s.down and p>0.2 else s.sil+1
            if s.sil>=s.hang or i-s.start>=s.maxf:
                out=(max(0,s.start),i-s.sil+2); s.insp=False; s.run=0
        s.n+=1; return out
