from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math
NAVY=(11,16,38); YEL=(255,210,63); PINK=(255,61,127); GRN=(43,217,107); WHITE=(255,255,255)
def mont(size):
    f=ImageFont.truetype('fonts/Montserrat[wght].ttf',size)
    try: f.set_variation_by_axes([900])
    except Exception: pass
    return f
def bolt(d,cx,cy,s,fill):
    pts=[(0.15,-1),(-0.55,0.12),(-0.02,0.12),(-0.2,1),(0.58,-0.18),(0.05,-0.18),(0.32,-1)]
    d.polygon([(cx+x*s,cy+y*s) for x,y in pts],fill=fill)
def bg(w,h):
    im=Image.new('RGB',(w,h),NAVY)
    glow=Image.new('RGB',(w,h),(0,0,0)); g=ImageDraw.Draw(glow)
    g.ellipse([w*0.55,-h*0.4,w*1.3,h*0.9],fill=(120,30,90)); g.ellipse([-w*0.3,h*0.3,w*0.45,h*1.5],fill=(20,60,140))
    glow=glow.filter(ImageFilter.GaussianBlur(min(w,h)*0.18))
    return Image.blend(im,Image.composite(glow,im,Image.new('L',(w,h),255)),0.6)
# avatar 800x800
A=bg(800,800); d=ImageDraw.Draw(A)
d.ellipse([90,90,710,710],outline=YEL,width=22)
for i in range(12):
    a=math.radians(i*30); r1,r2=330,300
    d.line([(400+r1*math.sin(a),400-r1*math.cos(a)),(400+r2*math.sin(a),400-r2*math.cos(a))],fill=YEL,width=10)
f=mont(300); t='Q'; bb=d.textbbox((0,0),t,font=f)
d.text((400-(bb[2]-bb[0])/2-bb[0]-30,400-(bb[3]-bb[1])/2-bb[1]),t,font=f,fill=WHITE)
bolt(d,560,450,120,PINK)
A.save('brand/avatar_quizrush.png')
# banner 2560x1440 (safe zone 1546x423 centered)
B=bg(2560,1440); d=ImageDraw.Draw(B)
f=mont(190); t1='QUIZ'; t2=' RUSH'
w1=d.textlength(t1,font=f); w2=d.textlength(t2,font=f); x=1280-(w1+w2)/2-60; y=720-150
d.text((x,y),t1,font=f,fill=WHITE); d.text((x+w1,y),t2,font=f,fill=YEL)
bolt(d,x+w1+w2+80,y+105,95,PINK)
f2=ImageFont.truetype('fonts/Poppins-Medium.ttf',62)
s='Can you beat the clock?  New quizzes every week'
d.text((1280-d.textlength(s,font=f2)/2,y+250),s,font=f2,fill=(200,210,235))
B.save('brand/banner_quizrush.png')
