"""Quiz Rush Show — rendu d'un quiz long (16:9) et de shorts (9:16).
Usage: python3 tools/render_quiz.py episodes/01
Chaque question = 2 cartes PNG (question / réponse) + segment ffmpeg (chrono animé).
"""
import json, os, sys, subprocess, math, wave, struct, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_B = os.path.join(ROOT, 'fonts', 'Montserrat[wght].ttf')
FONT_M = os.path.join(ROOT, 'fonts', 'Poppins-Medium.ttf')
FONT_BB = os.path.join(ROOT, 'fonts', 'Poppins-Bold.ttf')
NAVY = (11, 16, 38); YEL = (255, 210, 63); PINK = (255, 61, 127); GRN = (43, 217, 107)
RED = (255, 77, 90); BLUE = (90, 140, 255); WHITE = (255, 255, 255); GREY = (150, 160, 190)
CHIP = [YEL, PINK, GRN, BLUE]
LVLC = {'EASY': GRN, 'MEDIUM': BLUE, 'HARD': PINK, 'GENIUS': YEL}
FPS = 30


def mont(size, w=900):
    f = ImageFont.truetype(FONT_B, size)
    try: f.set_variation_by_axes([w])
    except Exception: pass
    return f


def pop(size): return ImageFont.truetype(FONT_M, size)
def popb(size): return ImageFont.truetype(FONT_BB, size)


def bg(w, h):
    im = Image.new('RGB', (w, h), NAVY)
    glow = Image.new('RGB', (w, h), (0, 0, 0)); g = ImageDraw.Draw(glow)
    g.ellipse([w * 0.55, -h * 0.4, w * 1.3, h * 0.9], fill=(120, 30, 90))
    g.ellipse([-w * 0.3, h * 0.3, w * 0.45, h * 1.5], fill=(20, 60, 140))
    glow = glow.filter(ImageFilter.GaussianBlur(min(w, h) * 0.18))
    return Image.blend(im, glow, 0.55)


def wrap(d, text, font, maxw):
    words = text.split(); lines = []; cur = ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=font) <= maxw: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur); return lines


def fit_text(d, text, maxw, maxlines, start, minsize, fontf):
    s = start
    while s > minsize:
        f = fontf(s); ls = wrap(d, text, f, maxw)
        if len(ls) <= maxlines: return f, ls
        s -= 4
    f = fontf(minsize); return f, wrap(d, text, f, maxw)


def rounded_photo(path, w, h, r):
    im = Image.open(path).convert('RGB')
    im = ImageOps.fit(im, (w, h), Image.LANCZOS, centering=(0.5, 0.45))
    m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], r, fill=255)
    return im, m


def bolt(d, cx, cy, s, fill):
    pts = [(0.15, -1), (-0.55, 0.12), (-0.02, 0.12), (-0.2, 1), (0.58, -0.18), (0.05, -0.18), (0.32, -1)]
    d.polygon([(cx + x * s, cy + y * s) for x, y in pts], fill=fill)


def logo(d, x, y, size):
    f = mont(size); w1 = d.textlength('QUIZ', font=f)
    d.text((x, y), 'QUIZ', font=f, fill=WHITE); d.text((x + w1, y), ' RUSH', font=f, fill=YEL)
    return x + w1 + d.textlength(' RUSH', font=f)


# ---------- 16:9 cards ----------
W, H = 1920, 1080
PH = (60, 150, 1040, 870)  # photo box x0,y0,x1,y1
TIMER_Y = 1010


def card_169(q, n, total, photo, state):
    """state: 'q' (question) or 'a' (answer revealed)."""
    im = bg(W, H); d = ImageDraw.Draw(im)
    # header
    logo(d, 60, 40, 46)
    lv = q['lvl']; c = LVLC[lv]; f = mont(34)
    tw = d.textlength(lv, font=f)
    d.rounded_rectangle([W - 60 - tw - 280, 40, W - 60 - 250, 96], 14, fill=c)
    d.text((W - 60 - tw - 260, 46), lv, font=f, fill=NAVY)
    s = f'{n}/{total}'; f2 = mont(40)
    d.text((W - 60 - d.textlength(s, font=f2), 44), s, font=f2, fill=WHITE)
    # photo
    pw, ph = PH[2] - PH[0], PH[3] - PH[1]
    p, m = rounded_photo(photo, pw, ph, 36)
    sh = Image.new('L', (W, H), 0); ImageDraw.Draw(sh).rounded_rectangle([PH[0] + 10, PH[1] + 16, PH[2] + 10, PH[3] + 16], 36, fill=150)
    im.paste((0, 0, 0), (0, 0), sh.filter(ImageFilter.GaussianBlur(18)))
    im.paste(p, (PH[0], PH[1]), m); d = ImageDraw.Draw(im)
    # question
    x0 = 1100; maxw = W - 60 - x0
    fq, ls = fit_text(d, q['q'], maxw, 3, 58, 40, mont)
    y = 160
    for l in ls:
        d.text((x0, y), l, font=fq, fill=WHITE); y += int(fq.size * 1.2)
    # options
    oy = max(y + 40, 400); oh = 108; gap = 22
    for i, o in enumerate(q['o']):
        yy = oy + i * (oh + gap)
        correct = i == q['a']
        if state == 'a' and correct: fill, tc, oc = GRN, NAVY, NAVY
        elif state == 'a': fill, tc, oc = (40, 46, 72), (120, 128, 155), (90, 98, 125)
        else: fill, tc, oc = (28, 36, 70), WHITE, CHIP[i]
        d.rounded_rectangle([x0, yy, W - 60, yy + oh], 26, fill=fill, outline=(oc if state == 'q' else fill), width=4)
        d.rounded_rectangle([x0 + 18, yy + 18, x0 + 90, yy + oh - 18], 16, fill=(CHIP[i] if state == 'q' else (NAVY if correct else (60, 66, 92))))
        fl = mont(44); L = 'ABCD'[i]
        d.text((x0 + 54 - d.textlength(L, font=fl) / 2, yy + 26), L, font=fl, fill=(NAVY if state == 'q' else (GRN if correct else (120, 128, 155))))
        fo, ol = fit_text(d, o, W - 60 - x0 - 130, 1, 46, 30, popb)
        d.text((x0 + 116, yy + (oh - fo.size) / 2 - 6), ol[0], font=fo, fill=tc)
    # fact on answer
    if state == 'a':
        fy = PH[3] + 18
        ff, fl_ = fit_text(d, q['f'], PH[2] - PH[0] - 40, 2, 34, 26, pop)
        d.rounded_rectangle([PH[0], fy, PH[2], fy + 30 + len(fl_) * int(ff.size * 1.25)], 20, fill=(20, 26, 55))
        yy = fy + 14
        for l in fl_:
            d.text((PH[0] + 22, yy), l, font=ff, fill=(220, 226, 245)); yy += int(ff.size * 1.25)
    else:
        # timer track
        d.rounded_rectangle([60, TIMER_Y, W - 60, TIMER_Y + 26], 13, fill=(35, 42, 78))
    return im


# ---------- 9:16 cards ----------
VW, VH = 1080, 1920


def card_916(q, n, total, photo, state, hook=None):
    im = bg(VW, VH); d = ImageDraw.Draw(im)
    if hook:
        fh, hl = fit_text(d, hook, VW - 120, 2, 64, 44, mont)
        y = 120
        for l in hl:
            d.text(((VW - d.textlength(l, font=fh)) / 2, y), l, font=fh, fill=YEL); y += int(fh.size * 1.15)
    s = f'{n}/{total}'; f2 = mont(44)
    d.text(((VW - d.textlength(s, font=f2)) / 2, 300), s, font=f2, fill=WHITE)
    px0, py0, px1, py1 = 60, 380, VW - 60, 1000
    p, m = rounded_photo(photo, px1 - px0, py1 - py0, 36)
    im.paste(p, (px0, py0), m); d = ImageDraw.Draw(im)
    fq, ls = fit_text(d, q['q'], VW - 120, 3, 58, 40, mont)
    y = 1040
    for l in ls:
        d.text(((VW - d.textlength(l, font=fq)) / 2, y), l, font=fq, fill=WHITE); y += int(fq.size * 1.18)
    oy = max(y + 24, 1250); oh = 96; gap = 18
    for i, o in enumerate(q['o']):
        yy = oy + i * (oh + gap); correct = i == q['a']
        if state == 'a' and correct: fill, tc = GRN, NAVY
        elif state == 'a': fill, tc = (40, 46, 72), (120, 128, 155)
        else: fill, tc = (28, 36, 70), WHITE
        d.rounded_rectangle([60, yy, VW - 60, yy + oh], 24, fill=fill, outline=(CHIP[i] if state == 'q' else fill), width=4)
        fl = mont(42); L = 'ABCD'[i]
        d.text((96, yy + 22), L, font=fl, fill=(CHIP[i] if state == 'q' else tc))
        fo, ol = fit_text(d, o, VW - 260, 1, 44, 30, popb)
        d.text((160, yy + (oh - fo.size) / 2 - 6), ol[0], font=fo, fill=tc)
    if state == 'q':
        d.rounded_rectangle([60, 1760, VW - 60, 1784], 12, fill=(35, 42, 78))
    return im


# ---------- audio ----------
SR = 48000


def tone(freq, dur, vol=0.5, decay=8.0, kind='sine'):
    n = int(SR * dur); out = []
    for i in range(n):
        t = i / SR; env = math.exp(-decay * t)
        if kind == 'sine': v = math.sin(2 * math.pi * freq * t)
        else: v = (random.random() * 2 - 1)
        out.append(v * env * vol)
    return out


def write_wav(path, samples):
    with wave.open(path, 'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(b''.join(struct.pack('<h', int(max(-1, min(1, s)) * 32000)) for s in samples))


def make_sfx(dirp):
    os.makedirs(dirp, exist_ok=True)
    tick = [a * 0.6 + b * 0.25 for a, b in zip(tone(2000, 0.05, 0.6, 60), tone(0, 0.05, 0.4, 80, 'noise'))]
    write_wav(f'{dirp}/tick.wav', tick)
    ding = [sum(x) for x in zip(tone(880, 0.9, 0.35, 4), tone(1320, 0.9, 0.25, 5), tone(1760, 0.9, 0.15, 6))]
    write_wav(f'{dirp}/ding.wav', ding)
    whoosh = []
    n = int(SR * 0.35)
    for i in range(n):
        t = i / n; whoosh.append((random.random() * 2 - 1) * math.sin(math.pi * t) ** 2 * 0.35)
    write_wav(f'{dirp}/whoosh.wav', whoosh)


def make_music(path, dur):
    """Fond synthétisé maison (aucune revendication Content ID): pad + pulsation douce."""
    cmd = ['ffmpeg', '-y', '-v', 'error', '-f', 'lavfi', '-i',
           f"aevalsrc='0.06*sin(2*PI*110*t)*(0.6+0.4*sin(2*PI*0.25*t))+0.04*sin(2*PI*164.81*t)+0.035*sin(2*PI*220*t)*(0.5+0.5*sin(2*PI*2*t))^8+0.03*sin(2*PI*329.63*t)*(0.5+0.5*sin(2*PI*0.5*t))':s={SR}:d={dur}",
           '-af', 'lowpass=f=1800,aecho=0.6:0.5:180:0.3', '-ac', '2', path]
    subprocess.run(cmd, check=True)


def run(cmd): subprocess.run(cmd, check=True)


def segment(qpng, apng, out, tq, ta, w, h, bar):
    """bar = (x0, y, x1, hgt). Barre jaune qui se vide + compte à rebours."""
    x0, y, x1, bh = bar; L = x1 - x0
    vf = (f"[0:v]split[b0][b1];[b1]crop={x0}:{bh}:0:{y}[mg];"
          f"[b0][2:v]overlay=x='{x0}-{L}*t/{tq}':y={y}:eval=frame[o1];[o1][mg]overlay=0:{y},"
          f"drawtext=fontfile='{FONT_BB}':text='%{{eif\\:max(1,ceil({tq}-t))\\:d}}':fontsize={int(bh*3.2)}:fontcolor=white:x={x1}-tw:y={y}-{int(bh*3.6)}[q];"
          f"[1:v]null[a];[q][a]concat=n=2:v=1:a=0,format=yuv420p[v]")
    run(['ffmpeg', '-y', '-v', 'error', '-loop', '1', '-t', str(tq), '-framerate', str(FPS), '-i', qpng,
         '-loop', '1', '-t', str(ta), '-framerate', str(FPS), '-i', apng,
         '-f', 'lavfi', '-t', str(tq), '-i', f'color=c=0xFFD23F:s={L}x{bh}:r={FPS}',
         '-filter_complex', vf, '-map', '[v]', '-r', str(FPS), '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', out])


def audio_track(out, n_q, tq, ta, sfx, intro=0.0, total=None):
    """Ticks chaque seconde, ding à la révélation, musique dessous."""
    seg = tq + ta; total = total or intro + n_q * seg
    inputs = ['-i', f'{sfx}/music.wav']; fl = []; k = 1; labels = []
    events = []
    for i in range(n_q):
        s0 = intro + i * seg
        for sec in range(int(tq)): events.append(('tick', s0 + sec))
        events.append(('ding', s0 + tq))
    for name in ('tick', 'ding'):
        inputs += ['-i', f'{sfx}/{name}.wav']
    idx = {'tick': 1, 'ding': 2}
    # amix with adelay per event via asplit
    cnt = {'tick': sum(1 for e in events if e[0] == 'tick'), 'ding': sum(1 for e in events if e[0] == 'ding')}
    fl.append(f"[1:a]asplit={cnt['tick']}" + ''.join(f'[t{i}]' for i in range(cnt['tick'])))
    fl.append(f"[2:a]asplit={cnt['ding']}" + ''.join(f'[d{i}]' for i in range(cnt['ding'])))
    ti = di = 0
    for name, at in events:
        ms = int(at * 1000)
        if name == 'tick': fl.append(f'[t{ti}]adelay={ms}|{ms}[e{len(labels)}]'); ti += 1
        else: fl.append(f'[d{di}]adelay={ms}|{ms}[e{len(labels)}]'); di += 1
        labels.append(f'[e{len(labels)}]')
    fl.append('[0:a]volume=0.55[m]')
    fl.append(''.join(labels) + '[m]' + f'amix=inputs={len(labels)+1}:normalize=0:duration=longest,atrim=0:{total},loudnorm=I=-14:TP=-1.5,aresample=48000[out]')
    script = out + '.filter'; open(script, 'w').write(';\n'.join(fl))
    run(['ffmpeg', '-y', '-v', 'error', *inputs, '-filter_complex_script', script, '-map', '[out]', '-ac', '2', '-ar', '48000', out])


def main(ep):
    qs = json.load(open(f'{ep}/questions.json'))
    media = sorted(f for f in os.listdir(f'{ep}/media') if f[:2].isdigit())
    photo = {int(f[:2]): f'{ep}/media/{f}' for f in media}
    build = f'{ep}/build'; os.makedirs(build, exist_ok=True)
    sfx = f'{build}/sfx'; make_sfx(sfx)
    TQ, TA = 10, 4
    total = len(qs)
    segs = []
    # intro card (4 s)
    im = bg(W, H); d = ImageDraw.Draw(im)
    x = logo(d, 0, 0, 1)  # measure
    f = mont(130); t1 = 'GENERAL KNOWLEDGE'; d.text(((W - d.textlength(t1, font=f)) / 2, 300), t1, font=f, fill=WHITE)
    f2 = mont(96); t2 = '40 QUESTIONS'; d.text(((W - d.textlength(t2, font=f2)) / 2, 470), t2, font=f2, fill=YEL)
    f3 = pop(54); t3 = 'Easy  >  Medium  >  Hard  >  Genius   |   10 seconds each'
    d.text(((W - d.textlength(t3, font=f3)) / 2, 640), t3, font=f3, fill=(210, 216, 240))
    f4 = popb(50); t4 = 'Keep your score and drop it in the comments!'
    d.text(((W - d.textlength(t4, font=f4)) / 2, 760), t4, font=f4, fill=PINK)
    im.save(f'{build}/intro.png')
    run(['ffmpeg', '-y', '-v', 'error', '-loop', '1', '-t', '4', '-framerate', str(FPS), '-i', f'{build}/intro.png', '-vf', 'format=yuv420p', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', f'{build}/s_intro.mp4'])
    segs.append(f'{build}/s_intro.mp4')
    for i, q in enumerate(qs):
        a = f'{build}/q{i:02d}.png'; b = f'{build}/a{i:02d}.png'
        card_169(q, i + 1, total, photo[i], 'q').save(a)
        card_169(q, i + 1, total, photo[i], 'a').save(b)
        o = f'{build}/s{i:02d}.mp4'
        segment(a, b, o, TQ, TA, W, H, (60, TIMER_Y, W - 60, 26)); segs.append(o)
    # outro
    im = bg(W, H); d = ImageDraw.Draw(im)
    f = mont(110); t1 = "WHAT'S YOUR SCORE?"; d.text(((W - d.textlength(t1, font=f)) / 2, 330), t1, font=f, fill=WHITE)
    f2 = pop(56)
    for k, (s, c) in enumerate([('0-10  Beginner', GREY), ('11-20  Smart', BLUE), ('21-30  Brilliant', GRN), ('31-39  Genius', YEL), ('40  Legend', PINK)]):
        d.text(((W - d.textlength(s, font=f2)) / 2, 500 + k * 74), s, font=f2, fill=c)
    f3 = popb(52); t3 = 'Comment your score and subscribe for the next quiz!'
    d.text(((W - d.textlength(t3, font=f3)) / 2, 900), t3, font=f3, fill=WHITE)
    im.save(f'{build}/outro.png')
    run(['ffmpeg', '-y', '-v', 'error', '-loop', '1', '-t', '8', '-framerate', str(FPS), '-i', f'{build}/outro.png', '-vf', 'format=yuv420p', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', f'{build}/s_outro.mp4'])
    segs.append(f'{build}/s_outro.mp4')
    open(f'{build}/list.txt', 'w').write(''.join(f"file '{os.path.abspath(s)}'\n" for s in segs))
    run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', f'{build}/list.txt', '-c', 'copy', f'{build}/video_noaudio.mp4'])
    dur = 4 + total * (TQ + TA) + 8
    make_music(f'{sfx}/music.wav', dur)
    audio_track(f'{build}/audio.m4a.wav', total, TQ, TA, sfx, intro=4, total=dur)
    run(['ffmpeg', '-y', '-v', 'error', '-i', f'{build}/video_noaudio.mp4', '-i', f'{build}/audio.m4a.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2', '-shortest', f'{ep}/video.mp4'])
    print('long ok', dur)


def shorts(ep, groups, hooks):
    qs = json.load(open(f'{ep}/questions.json'))
    media = sorted(f for f in os.listdir(f'{ep}/media') if f[:2].isdigit())
    photo = {int(f[:2]): f'{ep}/media/{f}' for f in media}
    build = f'{ep}/build'; sfx = f'{build}/sfx'
    TQ, TA = 5, 2.5
    for si, (grp, hook) in enumerate(zip(groups, hooks), 1):
        segs = []
        for k, i in enumerate(grp):
            a = f'{build}/vq{si}_{k}.png'; b = f'{build}/va{si}_{k}.png'
            card_916(qs[i], k + 1, len(grp), photo[i], 'q', hook).save(a)
            card_916(qs[i], k + 1, len(grp), photo[i], 'a', hook).save(b)
            o = f'{build}/vs{si}_{k}.mp4'; segment(a, b, o, TQ, TA, VW, VH, (60, 1760, VW - 60, 24)); segs.append(o)
        # end card 3 s
        im = bg(VW, VH); d = ImageDraw.Draw(im)
        f = mont(84)
        for j, (t, c) in enumerate([('HOW MANY', WHITE), ('DID YOU GET?', YEL)]):
            d.text(((VW - d.textlength(t, font=f)) / 2, 700 + j * 110), t, font=f, fill=c)
        f2 = popb(50); t = 'Full 40-question quiz on the channel'
        d.text(((VW - d.textlength(t, font=f2)) / 2, 1000), t, font=f2, fill=WHITE)
        im.save(f'{build}/vend{si}.png')
        run(['ffmpeg', '-y', '-v', 'error', '-loop', '1', '-t', '3', '-framerate', str(FPS), '-i', f'{build}/vend{si}.png', '-vf', 'format=yuv420p', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', f'{build}/vend{si}.mp4'])
        segs.append(f'{build}/vend{si}.mp4')
        open(f'{build}/vlist{si}.txt', 'w').write(''.join(f"file '{os.path.abspath(s)}'\n" for s in segs))
        run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', f'{build}/vlist{si}.txt', '-c', 'copy', f'{build}/short{si}_v.mp4'])
        dur = len(grp) * (TQ + TA) + 3
        make_music(f'{sfx}/music.wav', dur)
        audio_track(f'{build}/short{si}.wav', len(grp), TQ, TA, sfx, 0, dur)
        run(['ffmpeg', '-y', '-v', 'error', '-i', f'{build}/short{si}_v.mp4', '-i', f'{build}/short{si}.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2', '-shortest', f'{ep}/short{si}.mp4'])
        print('short', si, dur)


if __name__ == '__main__':
    main(sys.argv[1])


# ================= V2 : voix d'animateur =================
import numpy as np


def load_wav(path):
    with wave.open(path) as w:
        sr = w.getframerate(); ch = w.getnchannels()
        a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    if ch == 2: a = a.reshape(-1, 2).mean(1)
    return a, sr


def to48(a, sr):
    if sr == SR: return a
    n = int(len(a) * SR / sr)
    return np.interp(np.linspace(0, len(a) - 1, n), np.arange(len(a)), a).astype(np.float32)


def trim(a, thr=0.02):
    idx = np.where(np.abs(a) > thr)[0]
    if len(idx) == 0: return a
    s = max(0, idx[0] - int(0.03 * SR)); e = min(len(a), idx[-1] + int(0.12 * SR))
    return a[s:e]


def voice_clips(ep):
    segs = json.load(open(f'{ep}/voice/segments.json'))
    clips = []
    for b in segs:
        a, sr = load_wav(os.path.join(ep, b['file'])); a = to48(a, sr)
        for (s, e) in b['segs']:
            clips.append(trim(a[int(s * SR):int(e * SR)]))
    # ordre: intro, q1,a1..q40,a40, outro
    return clips


def segment_v2(qpng, apng, out, pre, tq, ta, bar):
    x0, y, x1, bh = bar; L = x1 - x0; tot = pre + tq
    vf = (f"[0:v]split[b0][b1];[b1]crop={x0}:{bh}:0:{y}[mg];"
          f"[b0][2:v]overlay=x='{x0}-{L}*max(0,t-{pre})/{tq}':y={y}:eval=frame[o1];[o1][mg]overlay=0:{y},"
          f"drawtext=fontfile='{FONT_BB}':text='%{{eif\\:max(1,ceil({tq}-max(0,t-{pre})))\\:d}}':fontsize={int(bh*3.2)}:fontcolor=white:x={x1}-tw:y={y}-{int(bh*3.6)}[q];"
          f"[1:v]null[a];[q][a]concat=n=2:v=1:a=0,format=yuv420p[v]")
    run(['ffmpeg', '-y', '-v', 'error', '-loop', '1', '-t', f'{tot:.3f}', '-framerate', str(FPS), '-i', qpng,
         '-loop', '1', '-t', f'{ta:.3f}', '-framerate', str(FPS), '-i', apng,
         '-f', 'lavfi', '-t', f'{tot:.3f}', '-i', f'color=c=0xFFD23F:s={L}x{bh}:r={FPS}',
         '-filter_complex', vf, '-map', '[v]', '-r', str(FPS), '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', out])


def still(png, dur, out):
    run(['ffmpeg', '-y', '-v', 'error', '-loop', '1', '-t', f'{dur:.3f}', '-framerate', str(FPS), '-i', png, '-vf', 'format=yuv420p', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', out])


def fr(x):  # arrondi à la frame pour que vidéo et audio restent calés
    return round(x * FPS) / FPS


def main_voice(ep, TQ=8):
    qs = json.load(open(f'{ep}/questions.json'))
    photo = {int(f[:2]): f'{ep}/media/{f}' for f in os.listdir(f'{ep}/media') if f[:2].isdigit()}
    build = f'{ep}/build'; sfx = f'{build}/sfx'; os.makedirs(build, exist_ok=True); make_sfx(sfx)
    clips = voice_clips(ep); assert len(clips) == 2 * len(qs) + 2, len(clips)
    intro_v, outro_v = clips[0], clips[-1]
    segs = []; ev = []  # ev: (kind, time, data)
    t = 0.0
    d = fr(len(intro_v) / SR + 0.9); ev.append(('voice', 0.3, intro_v))
    still(f'{build}/intro.png', d, f'{build}/v_intro.mp4'); segs.append(f'{build}/v_intro.mp4'); t += d
    chapters = []
    for i, q in enumerate(qs):
        if i % 10 == 0: chapters.append((t, q['lvl'].title()))
        qv, av = clips[1 + 2 * i], clips[2 + 2 * i]
        pre = fr(len(qv) / SR + 0.35); ta = fr(max(3.2, len(av) / SR + 0.9))
        ev.append(('voice', t + 0.15, qv))
        for k in range(TQ): ev.append(('tick', t + pre + k, None))
        ev.append(('ding', t + pre + TQ, None)); ev.append(('voice', t + pre + TQ + 0.35, av))
        o = f'{build}/v{i:02d}.mp4'
        segment_v2(f'{build}/q{i:02d}.png', f'{build}/a{i:02d}.png', o, pre, TQ, ta, (60, TIMER_Y, W - 60, 26))
        segs.append(o); t += pre + TQ + ta
    chapters.append((t, "What's your score?"))
    d = fr(len(outro_v) / SR + 2.5); ev.append(('voice', t + 0.4, outro_v))
    still(f'{build}/outro.png', d, f'{build}/v_outro.mp4'); segs.append(f'{build}/v_outro.mp4'); t += d
    total = t
    open(f'{build}/vlist.txt', 'w').write(''.join(f"file '{os.path.abspath(s)}'\n" for s in segs))
    run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', f'{build}/vlist.txt', '-c', 'copy', f'{build}/video_v_noaudio.mp4'])
    # ---- mix audio (numpy) ----
    N = int(total * SR) + SR
    voice = np.zeros(N, np.float32); fx = np.zeros(N, np.float32)
    tick = load_wav(f'{sfx}/tick.wav')[0]; ding = load_wav(f'{sfx}/ding.wav')[0]
    for kind, at, data in ev:
        s = int(at * SR)
        src = data if kind == 'voice' else (tick * 0.7 if kind == 'tick' else ding * 0.8)
        tgt = voice if kind == 'voice' else fx
        e = min(N, s + len(src)); tgt[s:e] += src[:e - s]
    make_music(f'{sfx}/music_long.wav', total + 1)
    mus = load_wav(f'{sfx}/music_long.wav')[0][:N]; mus = np.pad(mus, (0, N - len(mus)))
    env = np.convolve((np.abs(voice) > 0.01).astype(np.float32), np.ones(int(0.25 * SR)) / int(0.25 * SR), 'same')
    duck = 1 - 0.6 * np.clip(env * 4, 0, 1)
    mix = voice * 1.0 + fx * 0.5 + mus * 0.8 * duck
    mix = mix[:int(total * SR)]
    mix = mix / max(1e-6, np.abs(mix).max()) * 0.9
    raw = f'{build}/mix_v.wav'
    with wave.open(raw, 'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32000).astype(np.int16).tobytes())
    run(['ffmpeg', '-y', '-v', 'error', '-i', f'{build}/video_v_noaudio.mp4', '-i', raw, '-map', '0:v', '-map', '1:a',
         '-af', 'loudnorm=I=-14:TP=-1.5', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2', '-shortest', f'{ep}/video.mp4'])
    json.dump([(round(a, 1), b) for a, b in chapters], open(f'{ep}/chapters.json', 'w'))
    print('voice long ok', round(total, 1), chapters)
