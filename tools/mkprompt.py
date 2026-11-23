import json,sys
ep=sys.argv[1]; v=json.load(open(f'episodes/{ep}/voice.json'))
out=[f"I uploaded 4 audio files v0.mp3, v1.mp3, v2.mp3, v3.mp3 (in that order). Each is a sequence of spoken paragraphs. For each file, give the exact START time in seconds (with 2 decimals) of every paragraph EXCEPT the first one. Listen carefully. Paragraphs begin with these words:"]
for b in range(4):
    p=([v['intro']] if b==0 else [])
    for i in range(b*10,b*10+10): p+=[v['q'][i],v['a'][i]]
    if b==3: p.append(v['outro'])
    out.append(f"\nv{b}.mp3 ({len(p)} paragraphs):")
    for k,t in enumerate(p): out.append(f"{k+1}. {' '.join(t.split()[:6])}")
out.append('\nAnswer ONLY with JSON like {"0":[t2,t3,...],"1":[...],"2":[...],"3":[...]} where each list has (number of paragraphs - 1) numbers.')
print('\n'.join(out))
