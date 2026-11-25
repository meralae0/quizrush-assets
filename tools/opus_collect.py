# Reconstitue voiceN.wav à partir des morceaux base64 Opus (QRC|NN_b|i|...|END) sauvés dans tool-results. Usage: python3 tools/opus_collect.py 13_0 4
import json,glob,re,os,sys,base64,collections
TR='/root/.claude/projects/-home-claude-quizrush-assets/63a873d6-0d7a-5917-b986-bca521517c35/tool-results/'
chunks=collections.defaultdict(dict)
for f in glob.glob(TR+'*javascript_tool*.txt')+glob.glob(TR+'toolu_*.json'):
    try: t=json.load(open(f))[0]['text']
    except Exception: continue
    for m in re.finditer(r"QRC\|(\w+)\|(\d+)\|([A-Za-z0-9+/=]*)\|END",t):
        chunks[m.group(1)][int(m.group(2))]=m.group(3)
for k,d in sorted(chunks.items()):
    print(k, sorted(d), sum(len(v) for v in d.values()))

import struct, zlib, subprocess
def crc_table():
    t=[]
    for i in range(256):
        r=i<<24
        for _ in range(8): r=((r<<1)^0x04C11DB7)&0xffffffff if r&0x80000000 else (r<<1)&0xffffffff
        t.append(r)
    return t
T=crc_table()
def ogg_crc(d):
    c=0
    for b in d: c=((c<<8)&0xffffffff)^T[((c>>24)&0xff)^b]
    return c
def page(data_pkts, gran, serial, seq, flags):
    segs=[]
    for p in data_pkts:
        l=len(p)
        while l>=255: segs.append(255); l-=255
        segs.append(l)
    hdr=b'OggS'+bytes([0,flags])+struct.pack('<qIIi',gran,serial,seq,0)+bytes([len(segs)])+bytes(segs)
    body=b''.join(data_pkts)
    pg=bytearray(hdr+body); c=ogg_crc(pg); pg[22:26]=struct.pack('<I',c); return bytes(pg)
def mux(raw, out, sr=24000, preskip=156):
    pk=[]; i=0
    while i<len(raw):
        l=(raw[i]<<8)|raw[i+1]; pk.append(raw[i+2:i+2+l]); i+=2+l
    head=b'OpusHead'+bytes([1,1])+struct.pack('<HIhB',preskip,sr,0,0)
    tags=b'OpusTags'+struct.pack('<I',2)+b'qr'+struct.pack('<I',0)
    serial=1234; pages=[page([head],0,serial,0,2), page([tags],0,serial,1,0)]
    seq=2; gran=0; batch=[]
    for j,p in enumerate(pk):
        batch.append(p); gran+=960
        if len(batch)==50 or j==len(pk)-1:
            pages.append(page(batch,gran,serial,seq,4 if j==len(pk)-1 else 0)); seq+=1; batch=[]
    open(out,'wb').write(b''.join(pages))
if len(sys.argv)>1:
    k=sys.argv[1]; d=chunks[k]; n=int(sys.argv[2])
    assert sorted(d)==list(range(n)), sorted(d)
    raw=base64.b64decode(''.join(d[i] for i in range(n)))
    ep,blk=k.split('_'); od='/home/claude/quizrush-assets/episodes/%s/voice'%ep; os.makedirs(od,exist_ok=True)
    tmp='/tmp/claude-0/-home-claude-quizrush-assets/63a873d6-0d7a-5917-b986-bca521517c35/scratchpad/opus/%s.opus'%k
    mux(raw,tmp)
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',tmp,'-ar','24000','-ac','1','-c:a','pcm_s16le',od+'/voice%s.wav'%blk],check=True)
    print(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',od+'/voice%s.wav'%blk],capture_output=True,text=True).stdout)
