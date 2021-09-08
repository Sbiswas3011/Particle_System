import pygame
from pygame.locals import *
import math
import random
import itertools
import numpy as np

WHITE = (255,255,255)
BLACK = (0,0,0)
BLUE = (0,0,255)
GREEN = (0,255,0)
RED = (255,0,0)
width=1200
height=600 
(width, height) = (1200, 600)
observer=(600,400)
origin=(600,300)
zero=0

running = True

def wavelength_to_rgb(wavelength, gamma=0.8):
    '''This converts a given wavelength of light to an 
    approximate RGB color value. The wavelength must be given
    in nanometers in the range from 380 nm through 750 nm
    (789 THz through 400 THz).

    Based on code by Dan Bruton
    http://www.physics.sfasu.edu/astro/color/spectra.html
    '''
    wavelength = float(wavelength)
    if wavelength >= 380 and wavelength <= 440:
        attenuation = 0.3 + 0.7 * (wavelength - 380) / (440 - 380)
        R = ((-(wavelength - 440) / (440 - 380)) * attenuation) ** gamma
        G = 0.0
        B = (1.0 * attenuation) ** gamma
    elif wavelength >= 440 and wavelength <= 490:
        R = 0.0
        G = ((wavelength - 440) / (490 - 440)) ** gamma
        B = 1.0
    elif wavelength >= 490 and wavelength <= 510:
        R = 0.0
        G = 1.0
        B = (-(wavelength - 510) / (510 - 490)) ** gamma
    elif wavelength >= 510 and wavelength <= 580:
        R = ((wavelength - 510) / (580 - 510)) ** gamma
        G = 1.0
        B = 0.0
    elif wavelength >= 580 and wavelength <= 645:
        R = 1.0
        G = (-(wavelength - 645) / (645 - 580)) ** gamma
        B = 0.0
    elif wavelength >= 645 and wavelength <= 750:
        attenuation = 0.3 + 0.7 * (750 - wavelength) / (750 - 645)
        R = (1.0 * attenuation) ** gamma
        G = 0.0
        B = 0.0
    else:
        R = 0.0
        G = 0.0
        B = 0.0
    R *= 255
    G *= 255
    B *= 255
    return (int(R), int(G), int(B))


def rgb_to_hsv(r, g, b): 
    # R, G, B values are divided by 255
    # to change the range from 0..255 to 0..1:
    r, g, b = r / 255.0, g / 255.0, b / 255.0 
    # h, s, v = hue, saturation, value
    cmax = max(r, g, b)    # maximum of r, g, b
    cmin = min(r, g, b)    # minimum of r, g, b
    diff = cmax-cmin       # diff of cmax and cmin.
    # if cmax and cmax are equal then h = 0
    if cmax == cmin:
        h = 0     
    # if cmax equal r then compute h
    elif cmax == r:
        h = (60 * ((g - b) / diff) + 360) % 360
    # if cmax equal g then compute h
    elif cmax == g:
        h = (60 * ((b - r) / diff) + 120) % 360 
    # if cmax equal b then compute h
    elif cmax == b:
        h = (60 * ((r - g) / diff) + 240) % 360        
    return h

class BALL(pygame.sprite.Sprite):
    
    def __init__(self, velx, vely, x, y, color,wave,freq,mass):
        self.y=y
        self.x=x        
        self.velx=velx
        self.vely=vely

        self.mass=mass
        self.radius=10+self.mass
        self.radius=10
        self.origcolor=color
        self.color=color
        self.pos=(self.x,self.y)
        self.old_pos=(0,0)
        self.wave=wave
        self.origwave=wave
        self.freq=freq
        self.ady=0
        self.adx=0
        
    def reflect_edge(self):
        if((self.pos[0]+self.radius >= width or self.pos[0]-self.radius <= 0) and ( self.pos[1]+self.radius <= height and self.pos[1]-self.radius >= 0 )):#left and right edge reflect
            self.velx=-self.velx
            
        elif((self.pos[1]-self.radius <= 0 or self.pos[1]+self.radius >= height) and ( self.pos[0]+self.radius <= width and self.pos[0]-self.radius >= 0 )):#top and bottom edge reflect           
            self.vely=-self.vely
            
        elif((self.pos[0]+self.radius >= width or self.pos[0]-self.radius <= 0) and (self.pos[1]+self.radius >= height or self.pos[1]-self.radius <= 0)):#corner reflect
            self.velx=-self.velx
            self.vely=-self.vely
        
            
    def position(self):
        if(self.vely<0):
            self.ady+=abs(self.vely)
        else:
            self.ady-=self.vely
        self.adx+=self.velx
        self.pos=(int(self.x+self.adx),int(self.y+self.ady))
        
    
    def return_coord(self):
        return (self.pos[0],self.pos[1])
        
    
    def return_vel(self):
        return (self.velx,self.vely)

            
    def collide_vel(self,x,y):
        self.velx=x
        self.vely=y
        
    def update_pos(self,x,y):
        self.pos=(int(x),int(y))
        
        
    def update(self):

        self.reflect_edge()
        r1=math.sqrt(((self.pos[0]-600)**2)+((self.pos[1]-400)**2))
        self.position()
        r2=math.sqrt(((self.pos[0]-600)**2)+((self.pos[1]-400)**2))

        dwave=r1*self.wave*math.pow(10,-3)

        if(r2-r1==0):
            pass
        elif(r2-r1>0):
            self.wave+=dwave
        else:
            self.wave-=dwave
            

        if(self.wave>750):
            self.wave=750            
        elif(self.wave<380):
            self.wave=380
            
        self.color=wavelength_to_rgb(self.wave)
            
        pygame.draw.circle(screen,self.color, self.pos, self.radius)
        pygame.draw.circle(screen,self.origcolor, self.pos, self.radius+2,2)
        pygame.draw.aaline(screen,WHITE,observer,self.pos,1)
        self.wave=self.origwave

def check_col(ball1,ball2):
    radius=math.sqrt(((ball1[0]-ball2[0])**2)+((ball1[1]-ball2[1])**2))
    if radius<=20:
        return True
    else:
        return False

    
    
def col_fix(col_list,ball):
    col_coords=[]
    accuracy=0.001
    for i in range(len(col_list)):
        ball1=list(ball[col_list[i][0]].return_coord())
        ball2=list(ball[col_list[i][1]].return_coord())
        ball1_vel=ball[col_list[i][0]].return_vel()
        ball2_vel=ball[col_list[i][1]].return_vel()
        
        if(ball1_vel[0]==0):
            ball1_ratio=ball1_vel[1]
        else:
            ball1_ratio=ball1_vel[1]/ball1_vel[0]
            
        if(ball2_vel[0]==0):
            ball2_ratio=ball2_vel[1]
        else:
            ball2_ratio=ball2_vel[1]/ball2_vel[0]
        

        radius=math.sqrt(((ball1[0]-ball2[0])**2)+((ball1[1]-ball2[1])**2))

        
        
        while(radius<20):
            if(ball1_vel[0]>0):
                ball1[0]=ball1[0]-accuracy
            elif(ball1_vel[0]<0):
                ball1[0]=ball1[0]+accuracy
                
            if(ball2_vel[0]>0):
                ball2[0]=ball2[0]-accuracy
            elif(ball2_vel[0]<0):
                ball2[0]=ball2[0]+accuracy
                
            if(ball1_vel[1]>0):
                ball1[1]=ball1[1]+(ball1_ratio*accuracy)
            elif(ball1_vel[1]<0):
                ball1[1]=ball1[1]-(ball1_ratio*accuracy)
                
            if(ball2_vel[1]>0):
                ball2[1]=ball2[1]+(ball2_ratio*accuracy)
            elif(ball2_vel[1]<0):
                ball2[1]=ball2[1]-(ball2_ratio*accuracy)
                
            radius=math.sqrt(((int(ball1[0])-int(ball2[0]))**2)+((int(ball1[1])-int(ball2[1]))**2))

            
        ball[col_list[i][0]].update_pos(ball1[0],ball1[1])
        ball[col_list[i][1]].update_pos(ball2[0],ball2[1])
        col_coords.append(((int(ball1[0]),int(ball1[1])),(int(ball2[0]),int(ball2[1]))))
        #r=math.sqrt(((int(ball1[0])-int(ball2[0]))**2)+((int(ball1[1])-int(ball2[1]))**2))
        print(radius)

    return col_coords
            
            
def distance(coord,ball):
    ball1=list(ball[coord[0]].return_coord())
    ball2=list(ball[coord[1]].return_coord())
    radius=math.sqrt(((ball1[0]-ball2[0])**2)+((ball1[1]-ball2[1])**2))
    return radius
    

def find_b(xi,yi,xvel,yvel,xj,yj):
    
    if(yvel>0):
            
        mi=((yi-abs(yvel))-yi)/((xi+xvel)-xi)
        mj=((yj-abs(yvel))-yj)/((xj+xvel)-xj)
            
    elif(yvel<0):
            
        mi=((yi+abs(yvel))-yi)/((xi+xvel)-xi)
        mj=((yj+abs(yvel))-yj)/((xj+xvel)-xj)
        
    else:
        
        mi=0
        mj=0
        
                    
    ci=yi-(mi*xi)
    cj=yj-(mj*xj)
    a=mi
    #print("slopes",mi,mj)
    b=-1
    d=abs(ci-cj)/(math.sqrt((a**2)+(b**2)))
    return d

    
def collisions_manual(ball_list,ball): 
    
    ball_list_dup=ball_list
    collide=[]
    
    for ballno,coordinate in ball_list.items():
        for ballno2,coordinate2 in ball_list_dup.items():
            if(ballno!=ballno2 and check_col(coordinate,coordinate2)==True):
                if(coordinate[0]<=coordinate2[0]):
                    collide.append((ballno,ballno2))
                else:
                    collide.append((ballno2,ballno))
                    
    collide=list(set(collide))
    
    collide_coords=col_fix(collide,ball)

    
    for i in range(len(collide)):
        
        viox=ball[collide[i][0]].return_vel()[0]
        vioy=ball[collide[i][0]].return_vel()[1]
        vjox=ball[collide[i][1]].return_vel()[0]
        vjoy=ball[collide[i][1]].return_vel()[1]
        viox+=vjox
        vioy+=vjoy
        vjoy=0
        vjox=0
        D=20
        rev=False


        b=find_b(collide_coords[i][0][0],collide_coords[i][0][1],viox,vioy,collide_coords[i][1][0],collide_coords[i][1][1])
        #print(b)
            
            
        #print("b:",b)
        if(int(b)>=20):
            theta=0
            phi=0
            print("here")
                       
        elif(viox>0):
            theta=round(math.degrees(math.asin(math.sqrt(1-math.pow(b/D,2)))),4)
            phi=round(math.degrees(math.asin(b/D)),4)
           
        else:
            rev=True
            theta=round(180-math.degrees(math.asin(math.sqrt(1-math.pow(b/D,2)))),4)
            phi=round(180-math.degrees(math.asin(b/D)),4)
            

               
        if(theta!=0 and phi!=0):    
            #shift=round(math.degrees(math.atan2(vioy,viox)),4)
            #radii=round(-(math.degrees(math.atan2(collide_coords[i][1][1]-collide_coords[i][0][1],collide_coords[i][1][0]-collide_coords[i][0][0]))),4)
            #print("shift and radii",shift,radii)
            #print("angles before",theta,phi)
            
            if(rev==False):
                
                shift=round(math.degrees(math.atan2(vioy,viox)),4)
                radii=round(-(math.degrees(math.atan2(collide_coords[i][1][1]-collide_coords[i][0][1],collide_coords[i][1][0]-collide_coords[i][0][0]))),4)
                print("x positive shift and radii",shift,radii)
                print("angles before",theta,phi)
                
                if(shift>radii):
                    #theta=theta+shift
                    theta=radii+90
                    #phi=shift-phi
                    phi=radii
                elif(shift<radii):
                    #theta=shift-theta
                    theta=radii-90
                    phi=radii
                    #phi=phi+shift
            else:
                
                shift=round(math.degrees(math.atan2(vioy,viox)),4)
                radii=round(-(math.degrees(math.atan2(collide_coords[i][0][1]-collide_coords[i][1][1],collide_coords[i][0][0]-collide_coords[i][1][0]))),4)
                print("x negative shift and radii",shift,radii)
                print("angles before",theta,phi)
                
                if(shift>radii):
                    #theta=theta+shift
                    theta=radii
                    #phi=shift-phi
                    phi=radii+90
                elif(shift<radii):
                    #theta=shift-theta
                    theta=radii
                    #phi=phi+shift
                    phi=radii-90
                    
                #temp=theta
                #theta=phi
                #phi=temp
                
                
            theta=round(theta,4)
            phi=round(phi,4)
            print("angles after",theta,phi)

                
            vj=(vioy-(viox*math.tan(math.radians(theta))))/(math.sin(math.radians(phi))-(math.cos(math.radians(phi))*math.tan(math.radians(theta))))    
            vi=(viox-(vj*math.cos(math.radians(phi))))/math.cos(math.radians(theta))
            vinx=vi*math.cos(math.radians(theta))
            viny=vi*math.sin(math.radians(theta))
            vjnx=vj*math.cos(math.radians(phi))
            vjny=vj*math.sin(math.radians(phi))
                
        else:
            vinx=0
            viny=0
            vjny=vioy
            vjnx=viox
            #print("perfect collison")
            
            
        ball[collide[i][0]].collide_vel(vinx,viny)
        ball[collide[i][1]].collide_vel(vjnx,vjny)
           
            
                
       #print("i:",vinx,viny,"j:",vjnx,vjny)
       
        
           
pygame.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("PARTICLE PHYSICS SIMULATION")
clock = pygame.time.Clock()

c=3*(10**8)
end=False
drawing=0
tick=30
ball=[]
ball_locations={}
leave_alone=[]


while running:
        clock.tick(tick)
        screen.fill(BLACK)
        pygame.draw.circle(screen, RED, observer, 10,1)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running=False
                end=True
                pygame.quit()
                break
                
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if(drawing==0):
                    
                    startx,starty= pygame.mouse.get_pos()
                    drawing+=1
                
            elif event.type == pygame.MOUSEBUTTONUP:
                
                    endx,endy= pygame.mouse.get_pos()
                    drawing=0
                    x1=startx-observer[1]
                    x2=endx-observer[1]
                    y1=observer[0]-starty
                    y2=observer[0]-endy
                    velocitym=(math.sqrt(((x1-x2)**2)+((y1-y2)**2)))/50
                    velocityx=velocitym*math.cos(math.radians(180-math.degrees(math.atan2((y2-y1),(x1-x2)))))
                    velocityy=velocitym*math.sin(math.radians(180-math.degrees(math.atan2((y2-y1),(x1-x2)))))
                    #print(velocityx,velocityy)
                    #color=(random.randint(0,255),random.randint(0,255),random.randint(0,255))
                    hue=rgb_to_hsv(255, 255, 255)
                    wave=750 - 250 / 270 * hue
                    frequency=c/(wave*math.pow(10,-9))
                    mass=random.randint(1,10)
                    ball.append(BALL(velocityx,velocityy,startx,starty,WHITE,wave,frequency,mass))
                    
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if(tick<=1):
                        tick=1
                    else:
                        tick-=1
                elif event.key == pygame.K_RIGHT:
                    if(tick>=120):
                        tick=120
                    else:
                        tick+=1
                        
        if(end==True):
             break
                    
         
        if(drawing>0):
            
            pygame.draw.aaline(screen, WHITE,(startx,starty),(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1]),1)
            pygame.draw.circle(screen,WHITE,(startx,starty),10)
            
        loc_cnt=0
            
        for i in ball:
            ball_locations[loc_cnt]=i.return_coord()
            loc_cnt+=1
            
        collisions_manual(ball_locations,ball)
            
        for i in ball:
            i.update()
                    
        pygame.display.update()
         


