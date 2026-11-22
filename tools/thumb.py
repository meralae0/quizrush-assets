import sys; sys.path.insert(0,'tools'); from render_quiz import *
def thumb(ep, ids, l1, l2, out):
    im=bg(1280,720); d=ImageDraw.Draw(im)
    # 2x2 photos right
    pw,ph=300,250; x0,y0=640,70
    for k,i in enumerate(ids):
        p,m=rounded_photo(f'{ep}/media/{i:02d}.jpg',pw,ph,22)
        x=x0+(k%2)*(pw+16); y=y0+(k//2)*(ph+16)
        im.paste(p,(x,y),m)
    d=ImageDraw.Draw(im)
    # question mark badge
    d.ellipse([890,250,1030,390],fill=PINK); f=mont(110); d.text((960-d.textlength('?',font=f)/2,252),'?',font=f,fill=WHITE)
    f1=mont(96); f2=mont(150)
    y=110
    for t,c,f in [(l1[0],WHITE,f1),(l1[1],WHITE,f1),(l2,YEL,f2)]:
        d.text((50,y),t,font=f,fill=c,stroke_width=4,stroke_fill=NAVY); y+=int(f.size*1.08)
    bolt(d,560,560,70,PINK)
    d.rounded_rectangle([50,600,420,670],18,fill=GRN); f3=mont(40); d.text((70,612),'EASY > GENIUS',font=f3,fill=NAVY)
    im.save(out,quality=92)
thumb('episodes/01',[3,14,2,17],('CAN YOU','GET'),'40/40','episodes/01/thumb.jpg')
