# Usage (depuis la racine du dépôt) : python3 tools/auto_anchors.py 13 14  -> écrit episodes/NN/voice/anchors.json sans AI Studio
import sys,json,subprocess,math,re,statistics as st
exec(open('tools/split_voice.py').read().split('def split')[0])
def syl(t):
    n=0
    for w in re.findall(r"[A-Za-z']+|\d+",t):
        if w.isdigit(): n+=2*len(w); continue
        n+=max(1,len(re.findall(r'[aeiouy]+',w.lower())))
    return n+0.5*t.count(',')+0.3*len(re.findall(r'[.!?]',t))
def solve(f,p,dur):
    G=[(a,c) for a,c in gaps(f) if a>0.3 and c<dur-0.1]
    m=len(G); K=len(p)-1; W=[syl(t) for t in p]
    gl=[c-a for a,c in G]
    # voiced time between positions
    def voiced(s,e,inner):
        return (e-s)-sum(gl[j] for j in inner)
    rate=(dur-sum(gl))/sum(W)
    starts=[0.0]+[c for a,c in G]; ends=[a for a,c in G]+[dur]
    INF=1e18
    def segcost(k,i0,j1):
        # segment k from after gap i0 (-1=start) to before gap j1 (m=end)
        s=0.0 if i0<0 else G[i0][1]; e=dur if j1>=m else G[j1][0]
        v=voiced(s,e,range(i0+1,j1))
        exp=rate*W[k]; return ((v-exp)/(0.18*exp+0.4))**2
    D=[[INF]*m for _ in range(K)]; P=[[-1]*m for _ in range(K)]
    for j in range(m): D[0][j]=segcost(0,-1,j)-3*math.log(gl[j]+0.05)
    for k in range(1,K):
        for j in range(k,m):
            best=INF;bi=-1
            for i in range(k-1,j):
                if D[k-1][i]>=INF: continue
                c=D[k-1][i]+segcost(k,i,j)
                if c<best: best=c;bi=i
            D[k][j]=best-3*math.log(gl[j]+0.05); P[k][j]=bi
    best=INF;bj=-1
    for j in range(K-1,m):
        c=D[K-1][j]+segcost(K,j,m)
        if c<best: best=c;bj=j
    ch=[];j=bj
    for k in range(K-1,-1,-1): ch.append(j); j=P[k][j]
    ch=ch[::-1]; cuts=[0]+[(G[j][0]+G[j][1])/2 for j in ch]+[dur]
    ds=[cuts[i+1]-cuts[i] for i in range(len(p))]
    r=[d/w for d,w in zip(ds,W)]
    return [round((G[j][0]+G[j][1])/2+0.3,2) for j in ch], st.correlation(W,ds), min(r)/rate, max(r)/rate, min(gl[j] for j in ch)
for e in sys.argv[1:]:
  v=json.load(open(f'episodes/{e}/voice.json')); AN={}
  for b in range(4):
    p=([v['intro']] if b==0 else [])
    for i in range(b*10,b*10+10): p+=[v['q'][i],v['a'][i]]
    if b==3: p.append(v['outro'])
    f=f'episodes/{e}/voice/voice{b}.wav'
    dur=float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f],capture_output=True,text=True).stdout)
    an,c,mn,mx,mg=solve(f,p,dur); AN[str(b)]=an
    print(e,b,'corr %.2f rel min %.2f max %.2f mingap %.2f'%(c,mn,mx,mg))
  json.dump(AN,open(f'episodes/{e}/voice/anchors.json','w'))
