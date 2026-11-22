"""Découpe chaque bloc voix en répliques : choisit les silences qui collent le mieux
aux positions attendues (proportionnelles au nombre de mots) — programmation dynamique."""
import subprocess, re, json, math, statistics as st
import wave, numpy as np
def gaps(f):
    with wave.open(f) as w:
        sr=w.getframerate(); a=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768
    hop=int(sr*0.02); n=len(a)//hop
    rms=np.sqrt((a[:n*hop].reshape(n,hop)**2).mean(1))+1e-6
    db=20*np.log10(rms); thr=np.percentile(db,15)+8
    low=db<thr; G=[]; i=0
    while i<n:
        if low[i]:
            j=i
            while j<n and low[j]: j+=1
            if (j-i)*0.02>=0.12: G.append((i*0.02,j*0.02))
            i=j
        else: i+=1
    return G
def split(f, texts, dur, anchors=None):
    n = len(texts); wc = [len(t.split())+1.5 for t in texts]
    G = [(a,b) for a,b in gaps(f) if a>0.3 and b<dur-0.1]
    # positions attendues : parole proportionnelle aux mots + pause entre répliques
    tot = sum(wc); exp=[]; c=0
    for w in wc[:-1]:
        c += w; exp.append(dur*c/tot)
    if anchors: exp=[a-0.3 for a in anchors]
    m = len(G); INF=1e18
    mid=[(a+b)/2 for a,b in G]; ln=[b-a for a,b in G]
    sig = 0.9 if anchors else dur/n*0.35
    cost=lambda k,j: ((mid[j]-exp[k])/sig)**2 - 2.5*math.log(ln[j]+0.05)
    D=[[INF]*m for _ in range(n-1)]; P=[[-1]*m for _ in range(n-1)]
    for j in range(m): D[0][j]=cost(0,j)
    for k in range(1,n-1):
        best=INF; bj=-1
        for j in range(m):
            if j>0 and D[k-1][j-1]<best: best=D[k-1][j-1]; bj=j-1
            if best<INF: D[k][j]=best+cost(k,j); P[k][j]=bj
    j=min(range(m),key=lambda j:D[n-2][j]); cuts=[]
    for k in range(n-2,-1,-1):
        cuts.append(mid[j]); j=P[k][j]
    cuts=[0.0]+cuts[::-1]+[dur]
    return [(cuts[i],cuts[i+1]) for i in range(n)]
v=json.load(open('voice.json')); out=[]
import os
AN=json.load(open('voice/anchors.json')) if os.path.exists('voice/anchors.json') else {}
for b in range(4):
    p=([v['intro']] if b==0 else [])
    for i in range(b*10,b*10+10): p+=[v['q'][i],v['a'][i]]
    if b==3: p.append(v['outro'])
    f=f'voice/voice{b}.wav'; dur=float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f],capture_output=True,text=True).stdout)
    segs=split(f,p,dur,AN.get(str(b))); wc=[len(t.split()) for t in p]; ds=[s[1]-s[0] for s in segs]
    print(b,'corr %.2f'%st.correlation(wc,ds),'s/word',[round(d/w,2) for d,w in zip(ds,wc)])
    out.append({'file':f,'segs':segs,'texts':p})
json.dump(out,open('voice/segments.json','w'),indent=1)
