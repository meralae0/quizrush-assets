"""Construit un épisode complet à partir de episodes/NN/meta.json (+ questions.json, voice/segments.json).
Usage : python3 tools/build_ep.py episodes/04 [long|shorts|thumb|desc|all]
meta.json : {"mode": "tiles"|"zoom"|"none", "card": ["GUESS THE FLAG", "40 COUNTRIES"], "sub": "...",
             "tiers": ["0-10  ...", ...5], "thumb": {"ids": [..4], "l1": ["GUESS THE", "FLAG"], "l2": "40"},
             "title": "...", "desc_intro": "...", "tags": "#quiz ...", "noun": "flag",
             "shorts": [{"ids": [5 ids], "hook": "...", "title": "...", "caption": "..."}, ...]}
"""
import sys, os, json, wave
sys.path.insert(0, os.path.dirname(__file__))
from render_quiz import *
import render_quiz as R
import numpy as np

TQ = 10
LV_TILES = {'EASY': (3, 13), 'MEDIUM': (2, 12), 'HARD': (1, 11), 'GENIUS': (1, 9)}
LV_ZOOM = {'EASY': (3.0, 1.35), 'MEDIUM': (3.6, 1.6), 'HARD': (4.2, 1.9), 'GENIUS': (4.8, 2.3)}


def reveal(meta, q, i, k, K):
    if meta['mode'] == 'tiles':
        s0, s1 = LV_TILES[q['lvl']]
        return set(tile_order(1000 + i)[:s0 + round(k * (s1 - s0) / K)])
    if meta['mode'] == 'zoom':
        z0, z1 = LV_ZOOM[q['lvl']]; fx, fy = q.get('focus', [0.5, 0.5])
        return ('zoom', z0 * (z1 / z0) ** (k / K), fx, fy)
    return None


def load(ep):
    meta = json.load(open(f'{ep}/meta.json')); qs = json.load(open(f'{ep}/questions.json'))
    photo = {int(f[:2]): f'{ep}/media/{f}' for f in os.listdir(f'{ep}/media') if f[:2].isdigit() and f.endswith('.jpg')}
    b = f'{ep}/build'; os.makedirs(b, exist_ok=True)
    return meta, qs, photo, b


def cards(ep):
    meta, qs, photo, b = load(ep)
    for i, q in enumerate(qs):
        for k in range(TQ + 1):
            card_169(q, i + 1, len(qs), photo[i], 'q', reveal(meta, q, i, k, TQ)).save(f'{b}/q{i:02d}_{k}.png')
        card_169(q, i + 1, len(qs), photo[i], 'a').save(f'{b}/a{i:02d}.png')
    im = bg(W, H); d = ImageDraw.Draw(im)
    f = mont(130); t1 = meta['card'][0]; d.text(((W - d.textlength(t1, font=f)) / 2, 300), t1, font=f, fill=WHITE)
    f2 = mont(96); t2 = meta['card'][1]; d.text(((W - d.textlength(t2, font=f2)) / 2, 470), t2, font=f2, fill=YEL)
    f3 = pop(54); t3 = meta['sub']; d.text(((W - d.textlength(t3, font=f3)) / 2, 640), t3, font=f3, fill=(210, 216, 240))
    f4 = popb(50); t4 = 'Keep your score and drop it in the comments!'; d.text(((W - d.textlength(t4, font=f4)) / 2, 760), t4, font=f4, fill=PINK)
    im.save(f'{b}/intro.png')
    im = bg(W, H); d = ImageDraw.Draw(im)
    f = mont(110); t1 = "WHAT'S YOUR SCORE?"; d.text(((W - d.textlength(t1, font=f)) / 2, 330), t1, font=f, fill=WHITE)
    f2 = pop(56)
    for k, (s, c) in enumerate(zip(meta['tiers'], [GREY, BLUE, GRN, YEL, PINK])):
        d.text(((W - d.textlength(s, font=f2)) / 2, 500 + k * 74), s, font=f2, fill=c)
    f3 = popb(52); t3 = 'New quiz every day! Subscribe so you never miss one.'; d.text(((W - d.textlength(t3, font=f3)) / 2, 900), t3, font=f3, fill=WHITE)
    im.save(f'{b}/outro.png')


def long(ep):
    cards(ep)
    main_voice(ep, TQ=TQ)
    v = f'{ep}/video.mp4'; t = f'{ep}/build/v_tmp.mp4'
    run(['ffmpeg', '-y', '-v', 'error', '-i', v, '-c:v', 'copy', '-af', 'volume=2.5dB,alimiter=limit=0.89', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', t])
    os.replace(t, v)


def endcard_916(path):
    im = bg(VW, VH); d = ImageDraw.Draw(im)
    f = mont(84)
    for j, (t, c) in enumerate([('WATCH THE', WHITE), ('FULL QUIZ', YEL), ('ON YOUTUBE', WHITE)]):
        d.text(((VW - d.textlength(t, font=f)) / 2, 560 + j * 110), t, font=f, fill=c)
    f2 = popb(54); t = 'Quiz Rush Show'; d.text(((VW - d.textlength(t, font=f2)) / 2, 940), t, font=f2, fill=PINK)
    f3 = popb(48); t = 'A new quiz every day!'; d.text(((VW - d.textlength(t, font=f3)) / 2, 1030), t, font=f3, fill=WHITE)
    im.save(path)


def shorts_voice(ep):
    meta, qs, photo, b = load(ep)
    clips = voice_clips(ep)
    sfx = f'{b}/sfx'; make_sfx(sfx)
    tick = load_wav(f'{sfx}/tick.wav')[0]; ding = load_wav(f'{sfx}/ding.wav')[0]
    op = os.path.join(os.path.dirname(__file__), 'assets', 'short_outro.wav')
    outro = trim(to48(*load_wav(op))) if os.path.exists(op) else np.zeros(SR, np.float32)
    TS, BAR, TXT = 5, (60, V_BAR_Y, VW - 60, 22), (f'{V_CIRCLE[0]}-tw/2', f'{V_CIRCLE[1]}-th/2', 70)
    for si, sh in enumerate(meta['shorts'], 1):
        segs = []; ev = []; t = 0.0
        for k, i in enumerate(sh['ids']):
            q = qs[i]; qv, av = clips[1 + 2 * i], clips[2 + 2 * i]
            pre = fr(len(qv) / SR + 0.3); ta = fr(max(2.5, len(av) / SR + 0.7))
            ps = []
            for j in range(TS + 1):
                pj = f'{b}/sv{si}_{k}_{j}.png'
                card_916(q, k + 1, len(sh['ids']), photo[i], 'q', sh['hook'], reveal(meta, q, i, j * 2, 10)).save(pj); ps.append(pj)
            apng = f'{b}/sva{si}_{k}.png'; card_916(q, k + 1, len(sh['ids']), photo[i], 'a', sh['hook']).save(apng)
            o = f'{b}/svs{si}_{k}.mp4'; segment_puz(ps, apng, o, pre, TS, ta, BAR, TXT); segs.append(o)
            ev.append(('voice', t + 0.1, qv))
            for s in range(TS): ev.append(('tick', t + pre + s, None))
            ev.append(('ding', t + pre + TS, None)); ev.append(('voice', t + pre + TS + 0.3, av))
            t += pre + TS + ta
        ec = f'{b}/svend.png'; endcard_916(ec); d = fr(len(outro) / SR + 1.2)
        still(ec, d, f'{b}/svend{si}.mp4'); segs.append(f'{b}/svend{si}.mp4'); ev.append(('voice', t + 0.3, outro)); t += d
        open(f'{b}/svlist{si}.txt', 'w').write(''.join(f"file '{os.path.abspath(s)}'\n" for s in segs))
        run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', f'{b}/svlist{si}.txt', '-c', 'copy', f'{b}/sv{si}_v.mp4'])
        N = int(t * SR) + SR; voice = np.zeros(N, np.float32); fx = np.zeros(N, np.float32)
        for kind, at, data in ev:
            s = int(at * SR); src = data if kind == 'voice' else (tick * 0.7 if kind == 'tick' else ding * 0.8)
            tgt = voice if kind == 'voice' else fx; e = min(N, s + len(src)); tgt[s:e] += src[:e - s]
        make_music(f'{sfx}/music_s.wav', t + 1)
        mus = load_wav(f'{sfx}/music_s.wav')[0][:N]; mus = np.pad(mus, (0, N - len(mus)))
        env = np.convolve((np.abs(voice) > 0.01).astype(np.float32), np.ones(int(0.25 * SR)) / int(0.25 * SR), 'same')
        mix = voice + fx * 0.5 + mus * 0.8 * (1 - 0.6 * np.clip(env * 4, 0, 1)); mix = mix[:int(t * SR)]
        mix = mix / max(1e-6, np.abs(mix).max()) * 0.9
        raw = f'{b}/svmix{si}.wav'
        with wave.open(raw, 'w') as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32000).astype(np.int16).tobytes())
        run(['ffmpeg', '-y', '-v', 'error', '-i', f'{b}/sv{si}_v.mp4', '-i', raw, '-map', '0:v', '-map', '1:a',
             '-af', 'loudnorm=I=-14:TP=-1.5,volume=2dB,alimiter=limit=0.89', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2', '-shortest', f'{ep}/short{si}.mp4'])
        print('short', si, round(t, 1))


def thumb(ep):
    meta, qs, photo, b = load(ep)
    src = open(os.path.join(os.path.dirname(__file__), 'thumb.py')).read().split("if __name__")[0]
    g = {}; exec(src, g)
    th = meta['thumb']; ids = th['ids']
    tl = [None] + [reveal(meta, qs[i], i, 4, 10) for i in ids[1:]] if meta['mode'] != 'none' else None
    if meta['mode'] == 'tiles':
        R.PCOLS, R.PROWS = 3, 3; tl = [None, {0, 1, 3, 4, 5, 7}, {1, 2, 4, 6, 8}, {0, 4, 5, 7, 8}]
    g['thumb'](ep, ids, tuple(th['l1']), th['l2'], f'{ep}/thumb.jpg', tl)
    R.PCOLS, R.PROWS = 5, 4


def desc(ep, links=None):
    meta, qs, photo, b = load(ep)
    cr = {x['i']: x for x in json.load(open(f'{ep}/media/credits.json')) if x}
    ch = json.load(open(f'{ep}/chapters.json'))
    t = lambda s: f'{int(s) // 60}:{int(s) % 60:02d}'
    L = [meta['desc_intro'], '', '0:00 Intro']
    for (s, _), n in zip(ch, ['Easy (1-10)', 'Medium (11-20)', 'Hard (21-30)', 'Genius (31-40)', "What's your score?"]): L.append(f'{t(s)} {n}')
    L += ['', ' | '.join(meta['tiers']).replace('  ', ' '), '', 'A new quiz every day on Quiz Rush Show. Subscribe so you never miss one!', '', meta['tags'], '', 'Photos from Wikimedia Commons:']
    for i in range(len(qs)):
        x = cr.get(i)
        if x: L.append(f"Q{i + 1} {x['title'].rsplit('.', 1)[0][:38]} - {x.get('artist', '')[:28]} - {x.get('lic', '')}")
    s = '\n'.join(L)
    while len(s) > 4900: L = L[:-1]; s = '\n'.join(L)
    open(f'{ep}/description.txt', 'w').write(s)
    print('desc', len(s))


if __name__ == '__main__':
    ep = sys.argv[1]; what = sys.argv[2] if len(sys.argv) > 2 else 'all'
    if what in ('long', 'all'): long(ep)
    if what in ('shorts', 'all'): shorts_voice(ep)
    if what in ('thumb', 'all'): thumb(ep)
    if what in ('desc', 'all'): desc(ep)
