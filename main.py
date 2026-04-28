import pygame
import math
import time
sin:list = [math.sin(math.radians(a)) for a in range(360)]
cos:list = [math.cos(math.radians(a)) for a in range(360)]
print(sin[1])
print(cos[1])


class Vertex:
    def __init__(self,x:int,y:int):
        self.x:int = x
        self.y:int = y
    def __add__(self, other):
        return Vertex(self.x+other.x,self.y+other.y)
    def __sub__(self, other):
        return Vertex(self.x-other.x,self.y-other.y)
    def __str__(self):
        return f"({self.x}, {self.y})"
    def rotate(self,angle:int):
        return Vertex(self.x * cos[angle] - self.y * sin[angle], self.x * sin[angle] + self.y * cos[angle])

class LineDef:
    def __init__(self,v1:int,v2:int,texture_lower:int=0,texture_upper:int=0,texture_middle:int=0):
        self.v1: int = v1
        self.v2: int = v2
        self.texture_lower:int = texture_lower
        self.texture_upper:int = texture_upper
        self.texture_middle:int = texture_middle

class Sector:
    def __init__(self,sides:list[int],floor_height:int,ceiling_height:int,floor_texture=0,ceiling_texture=0,light_level:int=8):
        self.sides:list[int] = sides
        self.floor_height:int = floor_height
        self.ceiling_height:int = ceiling_height
        self.floor_texture:int = floor_texture
        self.ceiling_texture:int = ceiling_texture
        self.light_level:int = light_level

class seg:
    def __init__(self, linedef:int,v1:int,v2:int):
        self.linedef:int = linedef
        self.v1:int = v1
        self.v2:int = v2
    def __str__(self):
        return f"seg({self.linedef}, {self.v1}, {self.v2})"

class SubSector:
    def __init__(self,sector:int,segs:list[int]):
        self.sector:int = sector
        self.segs:list[int] = segs

class Camera:
    def __init__(self,x:int,y:int,z:int,angle:int,sizex:int,focallength:int,sizey:int):
        self.x = x
        self.y = y
        self.z = z
        self.sizex = sizex
        self.sizey = sizey
        self.focallength = focallength
        self.angle = angle
    def update(self,x,y,z,a):
        self.x = x
        self.y = y
        self.z = z
        self.angle = a

class Player:
    def __init__(self,x,y,z,a,c):
        self.x = x
        self.y = y
        self.z = z
        self.a = a
        self.c = c
    def update(self):
        global keys
        dx = sin[self.a]*10
        dy = cos[self.a]*10
        if keys["a"]:
            self.a-=4
        if keys["d"]:
            self.a+=4
        if keys["w"]:
            self.x += dx
            self.y += dy
        if keys["s"]:
            self.x -= dx
            self.y -= dy
        if keys["q"]:
            self.x -= dy
            self.y += dx
        if keys["e"]:
            self.x += dy
            self.y -= dx
        if self.a > 359:
            self.a = self.a % 360
        self.c.update(self.x,self.y,self.z,self.a)


Vertexes:list[Vertex] = [Vertex(-100,100),Vertex(100,100),Vertex(100,-100),Vertex(-100,-100)]
Lines:list[LineDef] = [LineDef(0,1,0,0,2),LineDef(1,2,0,0,3),LineDef(2,3,0,0,4),LineDef(3,0,0,0,5)]

Sectors:list[Sector] = [Sector([0],-100,100)]
Segs:list[seg] = [seg(n,l.v1,l.v2) for n,l in enumerate(Lines)]
SubSectors:list[SubSector] = [SubSector(0,[0,1])]

Main_Camera:Camera = Camera(0,0,0,0,200,200,200)
P:Player = Player(0,0,0,0,Main_Camera)

def get_texture_color(texture:int)-> tuple[int,int,int]:
    match texture:
        case 0:
            return (0,0,0)
        case 1:
            return (255,255,255)
        case 2:
            return (255,0,0)
        case 3:
            return (0,255,0)
        case 4:
            return (0,0,255)
        case 5:
            return (255,255,0)
        case 6: 
            return (0,255,255)
        case 7:
            return (255,0,255)

def draw_wall(x1,x2,b1,b2,t1,t2,c,w):
    dyb = b2-b1
    dyt = t2-t1
    dx = x2-x1
    if dx == 0: dx = 1
    xs = x1
    for x in range(x1,x2):
        y1 = dyb*(x-xs+0.5)/dx+b1
        y2 = dyt*(x-xs+0.5)/dx+t1
        for y in range(int(y2),int(y1)):
            w.set_at((x,y),c)
        w.set_at((x,int(y1)),c)
        w.set_at((x,int(y2)),c)

def render_seg(seg:int, subsector:int,camera:Camera, window:pygame.Surface):
    seg_object = Segs[seg]
    linedef_object = Lines[seg_object.linedef]
    subsector_object = SubSectors[subsector]
    sector_object = Sectors[subsector_object.sector]
    v1 = Vertexes[seg_object.v1]
    v2 = Vertexes[seg_object.v2]
    v1 -= Vertex(camera.x,camera.y)
    v2 -= Vertex(camera.x,camera.y)
    v1 = v1.rotate(camera.angle)
    v2 = v2.rotate(camera.angle)
    bottom = -(sector_object.floor_height-camera.z)
    top = -(sector_object.ceiling_height-camera.z)
    if bottom > top:
        # Calculate screen pos
        if v1.y == 0: v1.y=1
        if v2.y == 0: v2.y=1
        SW2 = int(camera.sizex//2)
        SH2 = int(camera.sizey//2)
        v1x = int(v1.x*200/v1.y+SW2)
        v2x = int(v2.x*200/v2.y+SW2)
        v1_top = int(top*200/v1.y+SH2)
        v1_bottom = int(bottom*200/v1.y+SH2)
        v2_top = int(top*200/v2.y+SH2)
        v2_bottom = int(bottom*200/v2.y+SH2)
        print(v1x,v1_bottom,v2x,v2_bottom)
        
        draw_wall(v1x,v2x,v1_bottom,v2_bottom,v1_top,v2_top,get_texture_color(linedef_object.texture_middle),window)
        


def render_subsector(subsector:int,camera:Camera,window:pygame.Surface):
    subsector_object = SubSectors[subsector]
    for seg in subsector_object.segs:
        render_seg(seg,subsector,camera,window)


window = pygame.display.set_mode((200, 200),pygame.SCALED)

# Setting name for window
pygame.display.set_caption('Doom like game')
keys = {"w":False,"d":False,"a":False,"s":False,"q":False,"e":False}
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            match event.key:
                case pygame.K_a:
                    keys["a"] = True
                case pygame.K_d:
                    keys["d"] = True
                case pygame.K_w:
                    keys["w"] = True
                case pygame.K_s:
                    keys["s"] = True
                case pygame.K_q:
                    keys["q"] = True
                case pygame.K_e:
                    keys["e"] = True
        if event.type == pygame.KEYUP:
            match event.key:
                case pygame.K_a:
                    keys["a"] = False
                case pygame.K_d:
                    keys["d"] = False
                case pygame.K_w:
                    keys["w"] = False
                case pygame.K_s:
                    keys["s"] = False
                case pygame.K_q:
                    keys["q"] = False
                case pygame.K_e:
                    keys["e"] = False

    print(keys)
    P.update()
    window.fill((0,0,0))
    render_subsector(0,Main_Camera,window)
    pygame.display.flip()
    time.sleep(0.05)
    
    
    
