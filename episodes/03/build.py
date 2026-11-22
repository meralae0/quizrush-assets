import sys, json, os; sys.path.insert(0,'tools'); from render_quiz import *
import render_quiz as r
ep='episodes/03'; qs=json.load(open(f'{ep}/questions.json')); TQ=10
photo={int(f[:2]):f'{ep}/media/{f}' for f in os.listdir(f'{ep}/media') if f[:2].isdigit()}
b=f'{ep}/build'; os.makedirs(b,exist_ok=True)
LV={'EASY':(3,13),'MEDIUM':(2,12),'HARD':(1,11),'GENIUS':(1,9)}
for i,q in enumerate(qs):
    s0,s1=LV[q['lvl']]; order=tile_order(1000+i)
    for k in range(TQ+1):
        card_169(q,i+1,40,photo[i],'q',set(order[:s0+round(k*(s1-s0)/TQ)])).save(f'{b}/q{i:02d}_{k}.png')
    card_169(q,i+1,40,photo[i],'a').save(f'{b}/a{i:02d}.png')
im=bg(W,H); d=ImageDraw.Draw(im)
f=mont(130); t1='GUESS THE STADIUM'; d.text(((W-d.textlength(t1,font=f))/2,300),t1,font=f,fill=WHITE)
f2=mont(96); t2='40 FAMOUS STADIUMS'; d.text(((W-d.textlength(t2,font=f2))/2,470),t2,font=f2,fill=YEL)
f3=pop(54); t3='Puzzle reveal  |  Easy  >  Genius  |  10 seconds each'; d.text(((W-d.textlength(t3,font=f3))/2,640),t3,font=f3,fill=(210,216,240))
f4=popb(50); t4='Keep your score and drop it in the comments!'; d.text(((W-d.textlength(t4,font=f4))/2,760),t4,font=f4,fill=PINK)
im.save(f'{b}/intro.png')
im=bg(W,H); d=ImageDraw.Draw(im)
f=mont(110); t1="WHAT'S YOUR SCORE?"; d.text(((W-d.textlength(t1,font=f))/2,330),t1,font=f,fill=WHITE)
f2=pop(56)
for k,(s,c) in enumerate([('0-10  Bench Warmer',GREY),('11-20  Season Ticket',BLUE),('21-30  Ultra',GRN),('31-39  Groundhopper',YEL),('40  Stadium Legend',PINK)]):
    d.text(((W-d.textlength(s,font=f2))/2,500+k*74),s,font=f2,fill=c)
f3=popb(52); t3='Comment your score and subscribe for the next quiz!'; d.text(((W-d.textlength(t3,font=f3))/2,900),t3,font=f3,fill=WHITE)
im.save(f'{b}/outro.png'); print('cards ok')
r.main_voice(ep, TQ=TQ); print('long ok')
r.shorts(ep,[[0,1,3,6,9,10],[11,13,14,16,24,27],[30,31,32,33,36,39]],
 ['ONLY 3% NAME ALL 6 STADIUMS','GUESS THE STADIUM FROM THE PUZZLE','THE HARDEST STADIUM QUIZ'], puzzle=True)
