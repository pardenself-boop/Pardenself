"""Original procedural scuffs and skyline for the TOOLBOXX interface."""
import random


def scuffed_metal(canvas,x0,y0,x1,y1,seed=17,density=90):
    rng=random.Random(seed)
    width=max(1,x1-x0);height=max(1,y1-y0)
    for _ in range(density):
        x=x0+rng.random()*width;y=y0+rng.random()*height
        length=min(x1-x,rng.uniform(2,28))
        canvas.create_line(x,y,x+length,y+rng.uniform(-1,1),fill=rng.choice(('#302b28','#3c332c','#1c1a1b','#514033')),width=1)
    canvas.create_rectangle(x0+2,y0+2,x1-2,y1-2,outline='#4c3d32',width=1)
    for x,y in ((x0+7,y0+7),(x1-7,y0+7),(x0+7,y1-7),(x1-7,y1-7)):
        canvas.create_oval(x-2,y-2,x+2,y+2,fill='#86715a',outline='#181614')
        canvas.create_line(x-1,y,x+1,y,fill='#25201b')


def skyline(canvas,x0,y0,x1,y1,seed=91):
    rng=random.Random(seed)
    for layer,color in ((0,'#33261f'),(1,'#191719')):
        x=x0-layer*8
        while x<x1:
            width=rng.randint(12,35);height=rng.randint(12,max(13,int((y1-y0)*.84)))
            roof=y1-height
            canvas.create_rectangle(x,roof,min(x1,x+width),y1,fill=color,outline='')
            if rng.random()>.7:canvas.create_line(x+width/2,roof,x+width/2,roof-rng.randint(5,17),fill=color,width=2)
            if layer:
                for wx in range(int(x)+4,min(int(x+width)-2,int(x1)),7):
                    for wy in range(int(roof)+5,int(y1)-2,8):
                        if rng.random()>.5:canvas.create_rectangle(wx,wy,wx+2,wy+2,fill='#9a6033',outline='')
            x+=width+2
