import sys, json, os; sys.path.insert(0,'tools'); from render_quiz import *
ep='episodes/02'; qs=json.load(open(f'{ep}/questions.json'))
photo={int(f[:2]):f'{ep}/media/{f}' for f in os.listdir(f'{ep}/media') if f[:2].isdigit()}
b=f'{ep}/build'; os.makedirs(b,exist_ok=True)
for i,q in enumerate(qs):
    card_169(q,i+1,40,photo[i],'q').save(f'{b}/q{i:02d}.png'); card_169(q,i+1,40,photo[i],'a').save(f'{b}/a{i:02d}.png')
im=bg(W,H); d=ImageDraw.Draw(im)
f=mont(130); t1='GUESS THE COUNTRY'; d.text(((W-d.textlength(t1,font=f))/2,300),t1,font=f,fill=WHITE)
f2=mont(96); t2='40 FAMOUS PLACES'; d.text(((W-d.textlength(t2,font=f2))/2,470),t2,font=f2,fill=YEL)
f3=pop(54); t3='Easy  >  Medium  >  Hard  >  Genius   |   10 seconds each'; d.text(((W-d.textlength(t3,font=f3))/2,640),t3,font=f3,fill=(210,216,240))
f4=popb(50); t4='Keep your score and drop it in the comments!'; d.text(((W-d.textlength(t4,font=f4))/2,760),t4,font=f4,fill=PINK)
im.save(f'{b}/intro.png')
im=bg(W,H); d=ImageDraw.Draw(im)
f=mont(110); t1="WHAT'S YOUR SCORE?"; d.text(((W-d.textlength(t1,font=f))/2,330),t1,font=f,fill=WHITE)
f2=pop(56)
for k,(s,c) in enumerate([('0-10  Tourist',GREY),('11-20  Traveler',BLUE),('21-30  Explorer',GRN),('31-39  Globetrotter',YEL),('40  World Master',PINK)]):
    d.text(((W-d.textlength(s,font=f2))/2,500+k*74),s,font=f2,fill=c)
f3=popb(52); t3='Comment your score and subscribe for the next quiz!'; d.text(((W-d.textlength(t3,font=f3))/2,900),t3,font=f3,fill=WHITE)
im.save(f'{b}/outro.png'); print('cards ok')
