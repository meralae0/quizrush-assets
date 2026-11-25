"""Construit live/bank.json + live/a/NN_QQ_{q,a}.mp3 à partir des épisodes (voix déjà découpée par segments.json)."""
import json, os, subprocess, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = os.path.join(R, 'live'); os.makedirs(out + '/a', exist_ok=True)
bank = []
eps = sorted(e for e in os.listdir(R + '/episodes') if e.isdigit() and os.path.exists(f'{R}/episodes/{e}/voice/segments.json'))
for e in eps:
    d = f'{R}/episodes/{e}'
    qs = json.load(open(d + '/questions.json')); seg = json.load(open(d + '/voice/segments.json'))
    meta = json.load(open(d + '/meta.json')) if os.path.exists(d + '/meta.json') else {}
    for i, q in enumerate(qs):
        b = i // 10; blk = seg[b]; k = (1 if b == 0 else 0) + 2 * (i % 10)
        clips = {}
        for tag, kk in (('q', k), ('a', k + 1)):
            s, t = blk['segs'][kk]; f = f'{out}/a/{e}_{i:02d}_{tag}.mp3'
            if not os.path.exists(f):
                subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f"{d}/{blk['file']}", '-ss', f'{s:.2f}', '-t', f'{t-s:.2f}',
                                '-af', 'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,volume=2.5dB',
                                '-ac', '1', '-b:a', '64k', f], check=True)
            clips[tag] = f'a/{e}_{i:02d}_{tag}.mp3'
        img = f'{d}/media/{i:02d}.jpg'
        if not os.path.exists(img): continue
        bank.append({'id': f'{e}_{i:02d}', 'ep': e, 'lvl': q['lvl'], 'q': q['q'], 'o': q['o'], 'a': q['a'], 'f': q['f'],
                     'img': f'episodes/{e}/media/{i:02d}.jpg', 'contain': bool(q.get('contain')), 'clip': clips})
json.dump(bank, open(out + '/bank.json', 'w'), ensure_ascii=False)
print(len(bank), 'questions', eps)
