import json,subprocess,time,sys,os
mode=sys.argv[1]; END=float(sys.argv[2])
ev=json.load(open('demo/events_room10.json'))[mode]
env=dict(os.environ,DISPLAY=':99')
X=lambda *a: subprocess.run(['xdotool',*a],env=env)
last=0
ff=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','x11grab','-framerate','30','-video_size','960x1080','-i',':99','-c:v','libx264','-preset','ultrafast','-pix_fmt','yuv420p',f'demo/rec/{mode}.mp4'],env=env,stdin=subprocess.PIPE)
fs=time.time(); time.sleep(1.5); t0=time.time()
for e in ev:
    if e['t']>END: break
    while time.time()-t0<e['t']: time.sleep(0.01)
    c=e['cmd']
    if c=='OPEN': X('key',{'claude':'alt+1','codex':'alt+2','terminal':'alt+3'}.get(e['arg'],'alt+1'))
    elif c=='TYPE': s=(' ' if last else '')+e['arg']; X('type','--delay','8',s); last=len(s)
    elif c=='SEND': X('key','Return'); last=0
    elif c=='UNDO' and last: X('key','--repeat',str(last),'--delay','1','BackSpace'); last=0
    elif c=='NEW_CHAT': X('key','alt+n'); last=0
while time.time()-t0<END+0.5: time.sleep(0.05)
ff.communicate(b'q'); print(mode,'offset',round(t0-fs,2))
json.dump({'offset':t0-fs},open(f'demo/rec/{mode}.json','w'))
