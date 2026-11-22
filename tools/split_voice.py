import subprocess,re,json,sys
def gaps(f):
    o=subprocess.run(['ffmpeg','-i',f,'-af','silencedetect=noise=-38dB:d=0.18','-f','null','-'],capture_output=True,text=True).stderr
    s=[float(x) for x in re.findall(r'silence_start: ([\d.]+)',o)]; e=[float(x) for x in re.findall(r'silence_end: ([\d.]+)',o)]
    return list(zip(s,e))
def split(f,texts,dur):
    g=gaps(f); n=len(texts)
    g=[x for x in g if x[0]>0.3 and x[1]<dur-0.1]
    top=sorted(sorted(g,key=lambda x:x[1]-x[0],reverse=True)[:n-1])
    cuts=[0.0]+[ (a+b)/2 for a,b in top]+[dur]
    segs=[(cuts[i],cuts[i+1]) for i in range(n)]
    return segs,len(g),[round(b-a,2) for a,b in top]
v=json.load(open('voice.json'))
blocks=[]
for b in range(4):
    p=([v['intro']] if b==0 else [])
    for i in range(b*10,b*10+10): p+=[v['q'][i],v['a'][i]]
    if b==3: p.append(v['outro'])
    blocks.append(p)
out=[]
for b,p in enumerate(blocks):
    f=f'voice/voice{b}.wav'; dur=float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f],capture_output=True,text=True).stdout)
    segs,ng,gl=split(f,p,dur)
    wc=[len(t.split()) for t in p]; ds=[s[1]-s[0] for s in segs]
    import statistics as st
    r=st.correlation(wc,ds)
    print(b,'gaps',ng,'min chosen gap',min(gl),'next gap?', 'corr %.2f'%r, 'sec/word', [round(d/w,2) for d,w in zip(ds,wc)])
    out.append({'file':f,'segs':segs,'texts':p})
json.dump(out,open('voice/segments.json','w'),indent=1)
