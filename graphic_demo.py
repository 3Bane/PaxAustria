
"""
author: Wilhelm Poigner
email: 3xtraktor@gmail.com
"""

import pygame 
import math
import random
import os
import sys
import operator
import Vector_2D as v


####
        
####

class VectorSprite(pygame.sprite.Sprite):
    """base class for sprites. this class inherits from pygames sprite class"""
    number = 0
    numbers = {} # { number, Sprite }
    
    def __init__(self, **kwargs):
        """create a (black) surface and paint a blue ball on it"""
        for key, arg in kwargs.items():
            setattr(self, key, arg)
        if "layer" not in kwargs:
            self._layer = 4
            
        pygame.sprite.Sprite.__init__(self, self.groups) #call parent class. NEVER FORGET !
        # self groups is set in PygView.paint()
        self.number = VectorSprite.number # unique number for each sprite
        VectorSprite.number += 1 
        VectorSprite.numbers[self.number] = self 
        # get unlimited named arguments and turn them into attributes
        self.upkey = None
        self.downkey = None
        self.rightkey = None
        self.leftkey = None
        
        # --- default values for missing keywords ----
        #if "pos" not in kwarts
        #pos=v.Vec2d(50,50), move=v.Vec2d(0,0), radius = 50, color=None, 
        #         , hitpoints=100, mass=10, damage=10, bounce_on_edge=True, angle=0
    
        self.age = 0 # in seconds
        if "angle" not in kwargs:
            self.angle = 0 # facing right?
        if "bossnumber" not in kwargs:
            self.bossnumber = None
        if "color" not in kwargs:
            self.color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
        if "damage" not in kwargs:
            self.damage = 10
        self.distance_traveled = 0 # in pixel
        if "drift" not in kwargs:
            self.drift = True
        if "faceing" not in kwargs:
            self.faceing = 0
        if "friction" not in kwargs:
            self.friction = None
        if "hitpoints" not in kwargs:
            self.hitpoints = 100
        self.hitpointsfull = self.hitpoints # makes a copy
        if "kill_on_edge" not in kwargs:
            self.kill_on_edge = True
        if "kill_with_boss" not in kwargs:
            self.kill_with_boss = False
        if "mass" not in kwargs:
            self.mass = 10
        if "max_age" not in kwargs:
            self.max_age = None
        if "max_distance" not in kwargs:
            self.max_distance = None
        if "max_range" not in kwargs:
            self.max_range = 400
        if "misschance" not in kwargs:
            self.misschance = 0.0
        if "movement" not in kwargs:
            self.movement = v.Vec2d(0,0)
        self.navI = 0
        self.path = []
        if "party" not in kwargs:
            self.party = 0
        if "picture" not in kwargs:
            self.picture = None
        if "pointlist" not in kwargs:
            self.pointlist = []
        if "position" not in kwargs:
            self.position = v.Vec2d(50,50)
        if "radius" not in kwargs:
            self.radius = 0
        if "height" not in kwargs:
            self.height = self.radius * 2
        if "speed" not in kwargs:
            self.speed = 2
        if "sticky_with_boss" not in kwargs:
            self.sticky_with_boss = False
        if "target" not in kwargs:
            self.target = None
        else:
            self.tr_distance = (self.position - self.target).get_length()
            self.tr_distance_old = (self.position - self.target).get_length()
        if "threat_lvl" not in kwargs:
            self.threat_lvl = random.randint(0, 5)
        if "turnspeed" not in kwargs:
            self.turnspeed = 5
        if "width" not in kwargs:
            self.width = self.radius * 2
        # ---
        self.create_image()
        
        
        
    def kill(self):
        try:
           del VectorSprite.numbers[self.number] # remove Sprite from numbers dict
        except:
            # key error?
            print("problem: could not delete sprite number" + str(self.number))
        pygame.sprite.Sprite.kill(self)
        
    def animate(self):
        pass
    
    def init2(self):
        pass # for subclasses
        
    def create_image(self):
        if self.picture is not None:
            self.image = self.picture.copy()
        else:            
            self.image = pygame.Surface((self.width,self.height))    
            self.image.fill((self.color))
        self.image = self.image.convert_alpha()
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()
        self.width = self.rect.width
        self.height = self.rect.height
        #self.rect.centerx = self.position.x
        #self.rect.centery = self.position.y
        
    def rotate(self, by_degree):
        """rotates a sprite and changes it's angle by by_degree"""
        self.angle += by_degree
        oldcenter = self.rect.center
        self.image = pygame.transform.rotate(self.image0, self.angle)
        self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = oldcenter
        
    def set_angle(self, degree):
        """rotates a sprite and changes it's angle to degree"""
        self.angle = degree
        self.faceing = degree
        oldcenter = self.rect.center
        self.image = pygame.transform.rotate(self.image0, self.angle)
        self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = oldcenter
        
    def checkNextNavPoint(self):
        distance = self.nextNav - self.position
        if distance.length < 10:
            self.navI += 1
            self.navI = self.navI % len(self.path)
    
    def flyToNextNavPoint(self):
        i2 = (self.navI +1) % len(self.path)
        self.nextNav = self.path[i2]
        self.movement = self.nextNav - self.position
        self.angle = self.movement.get_angle()
        #self.set_angle(-self.movement.get_angle())
        self.movement = self.movement.normalized() * self.speed
        self.checkNextNavPoint()
    
    def turn_to_angle(self, seconds):
        delta = (self.angle - self.faceing) % 360
        if round(delta, 0) == 0:
            return
        if delta < 0:
            newfaceing = self.turnspeed * seconds
        elif delta > 0:
            newfaceing = -self.turnspeed * seconds
        self.faceing += newfaceing
        oldcenter = self.rect.center
        self.image = pygame.transform.rotate(self.image0, -self.faceing)
        self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = oldcenter
        
    def update(self, seconds):
        """calculate movement, position and bouncing on edge"""
        # ----- kill because... ------
        if self.hitpoints <= 0:
            self.kill()
        if self.max_age is not None and self.age > self.max_age:
            self.kill()
        if self.max_distance is not None and self.distance_traveled > self.max_distance:
            self.kill()
            
        self.position += self.movement * seconds
        self.turn_to_angle(seconds)
        self.distance_traveled += self.movement.length * seconds
        self.age += seconds
        
        self.rect.center = ( round(self.position.x, 0), 
                             round(self.position.y, 0) )


class Balloon(VectorSprite):
    
    def create_image(self):
        if self.picture is not None:
            self.image = self.picture.copy()
        else:            
            self.image = pygame.Surface((self.width,self.height))    
            pygame.draw.circle(self.image, (50*self.threat_lvl, 10*self.threat_lvl , 50),
                               (self.width//2, self.height//2), self.width)
            #self.image.fill((self.color))
        self.image = self.image.convert_alpha()
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()
        self.width = self.rect.width
        self.height = self.rect.height


class Explosion(VectorSprite):
    
    def __init__(self, **kwargs):
        VectorSprite.__init__(self, **kwargs)
        #self.max_age = 0.5
        if self.max_age is None:
            self.max_age = 0.25
    
    def create_image(self):
        self.image = PygView.expimages[0]
        #self.image.set_colorkey((0,0,0))
        #self.image = self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.width = self.rect.width
        self.height = self.rect.height
        
        
    def update(self, seconds):
        VectorSprite.update(self, seconds)
        i = int(self.age/(self.max_age/len(PygView.expimages)))
        if i >= len(PygView.expimages):
            i = -1
        # i = self.age * 38 % len(PygView.expimages)
        self.image = PygView.expimages[int(i)] 
        self.rect = self.image.get_rect()
        self.width = self.rect.width
        self.height = self.rect.height
        self.rect.center = (self.position.x, self.position.y)
        

class Turret(VectorSprite):
    
    def update(self, seconds):
        VectorSprite.update(self, seconds)
        vec = self.startVec.rotated(self.carrier.faceing)
        self.position = self.carrier.position + vec
        try:
            if self.carrier.hitpoints <= 0:
                self.kill()
        except:
            self.kill()
        

class PDturret(Turret):
    pass
    

class Missile(VectorSprite):
    
    def create_image(self):
        if self.picture is not None:
            self.image = self.picture.copy()
        else:            
            self.image = pygame.Surface((self.width,self.height))    
            self.image.fill((self.color))
        self.image = self.image.convert_alpha()
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()
        self.width = self.rect.width
        self.height = self.rect.height
        self.image0 = pygame.transform.rotate(self.image0, 180)
        self.set_angle(self.angle)
        
    def kill(self):
        Explosion(position = self.position)
        VectorSprite.kill(self)
    
    #def update(self, seconds):
        #VectorSprite.update(self, seconds)
        #self.tr_distance = (self.position - self.target).get_length()
        #if self.tr_distance > self.tr_distance_old:
        #    self.kill()
        #self.tr_distance_old = self.tr_distance

class PDshot(Missile):
    
    def kill(self):
        VectorSprite.kill(self)


class Ship(VectorSprite):
    
    def update(self, seconds):
        self.flyToNextNavPoint()
        VectorSprite.update(self, seconds)
        

class AttackFighter(VectorSprite):
    
    def __init__(self, **kwargs):
        VectorSprite.__init__(self, **kwargs)
        if "TargetSprite" not in kwargs:
            self.TargetSprite = None
            
    def update(self, seconds):
        self.set_angle(-self.movement.get_angle())
        #speedlimit
        currentspeed = self.movement.get_length()
        if currentspeed != self.speed:
            self.movement = self.movement.normalized() * self.speed
        VectorSprite.update(self, seconds)
    
        
####


class Flytext(pygame.sprite.Sprite):
    def __init__(self, x, y, text="hallo", rgb=(200, 0, 0), blockxy = True,
                 dx=0, dy=-75, duration=1, acceleration_factor = 0.96, delay = 0):
        """a text flying upward and for a short time and disappearing"""
        self._layer = 7  # order of sprite layers (before / behind other sprites)
        pygame.sprite.Sprite.__init__(self, self.groups)  # THIS LINE IS IMPORTANT !!
        self.text = text
        self.r, self.g, self.b = rgb[0], rgb[1], rgb[2]
        self.dx = dx
        self.dy = dy
        #if blockxy:
        #    self.x, self.y = PygView.scrollx + x * 32, PygView.scrolly + y * 32
        #else:
        self.x, self.y = x, y
        self.duration = duration  # duration of flight in seconds
        self.acc = acceleration_factor  # if < 1, Text moves slower. if > 1, text moves faster. 
        self.image = write2(self.text, (self.r, self.g, self.b), 22)  # font 22
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)
        self.time = 0 - delay

    def update(self, seconds):
        self.time += seconds
        if self.time < 0:
            self.rect.center = (-100,-100)
        else:
            self.y += self.dy * seconds
            self.x += self.dx * seconds
            self.dy *= self.acc  # slower and slower
            self.dx *= self.acc
            self.rect.center = (self.x, self.y)
            
            if self.time > self.duration:
                self.kill()      # remove Sprite from screen and from groups


def write2(msg="pygame is cool", fontcolor=(255, 0, 255), fontsize=42, font=None):
    """returns pygame surface with text. You still need to blit the surface."""
    myfont = pygame.font.SysFont(font, fontsize)
    mytext = myfont.render(msg, True, fontcolor)
    mytext = mytext.convert_alpha()
    return mytext

####
def write(background, text, x=50, y=20, color=(0,0,0),
          fontsize=None, center=False):
        """write text on pygame surface. """
        if fontsize is None:
            fontsize = round(PygView.height/50)
            font = pygame.font.SysFont('mono', fontsize, bold=True)
            fw, fh = font.size(text)
            surface = font.render(text, True, color)
            
        if center: # center text around x,y
            background.blit(surface, (x-fw//2, y-fh//2))
        else:      # topleft corner is x,y
            background.blit(surface, (x,y))



def paint_hex(background, middle, radius, color=(64,64,64)):
    
    start= v.Vec2d(middle.x, middle.y)
    pointlist = []
    line = v.Vec2d(0, radius)
    pointlist.append(middle+line)
    line.rotate(90+60)
    
    for s in range(6):
       pointlist.append(pointlist[-1]+line)
       line.rotate(60)
       
    pygame.draw.polygon(background, color, [(p.x, p.y) for p in pointlist],1)  


####

class PygView():
  
    width = 0
    height = 0
    gridsize = 50
    pictures = {}
    expimages = []
  
    def __init__(self, width=1400, height=700, gridsize=50, fps=60):
        """Initialize pygame, window, background, font,...
           default arguments 
        """
        pygame.init()
        pygame.display.set_caption("ESC to quit")
        PygView.width = width    # also self.width 
        PygView.height = height  # also self.height
        PygView.gridsize = gridsize 
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        tmp = pygame.image.load(os.path.join("data","background10.jpg"))
        hdiff = int (round(self.width/28*10, 0))
        
        self.backgroundimg = pygame.transform.scale(tmp, (self.width-hdiff, self.height))
        self.background = pygame.Surface((self.width, self.height))
        self.background.blit(self.backgroundimg, (hdiff//2,0))
        pygame.draw.ellipse(self.background, (64,64,64), (PygView.width/4, PygView.height/7, PygView.width/2, PygView.height/7*5), 1)
        #border left
        pygame.draw.polygon(self.background, (64,64,64), (
                                                          (0,0),
                                                          (PygView.width/14*3, 0),
                                                          (PygView.width/28*5, PygView.height/14),
                                                          (PygView.width/28*5, PygView.height/14*13),
                                                          (PygView.width/14*3, PygView.height),
                                                          (0, PygView.height),
                                                          ), 0)
        #border right
        pygame.draw.polygon(self.background, (64,64,64), (
                                                          (PygView.width,0),
                                                          (PygView.width/14*11, 0),
                                                          (PygView.width/28*23, PygView.height/14),
                                                          (PygView.width/28*23, PygView.height/14*13),
                                                          (PygView.width/14*11, PygView.height),
                                                          (PygView.width, PygView.height),
                                                          ), 0)
        # self.grid()
        PygView.pictures["hunterpic"] = pygame.image.load(os.path.join("data","Hunter.png")).convert_alpha()
        PygView.pictures["hunterpic"] = pygame.transform.scale(PygView.pictures["hunterpic"], (40, 40)).convert_alpha()
        
        PygView.pictures["swarmhunterpic"] = pygame.image.load(os.path.join("data","Hunter.png")).convert_alpha()
        PygView.pictures["swarmhunterpic"] = pygame.transform.scale(PygView.pictures["swarmhunterpic"], (20, 20)).convert_alpha()
        
        PygView.pictures["bomberpic"] = pygame.image.load(os.path.join("data", "Bomber.png")).convert_alpha()
        PygView.pictures["bomberpic"] = pygame.transform.scale(PygView.pictures["bomberpic"], (40, 40)).convert_alpha()
        
        PygView.pictures["swarmbomberpic"] = pygame.image.load(os.path.join("data", "Bomber.png")).convert_alpha()
        PygView.pictures["swarmbomberpic"] = pygame.transform.scale(PygView.pictures["swarmbomberpic"], (20, 20)).convert_alpha()
        
        PygView.pictures["paladinpic"] = pygame.image.load(os.path.join("data", "Paladin.png")).convert_alpha()
        PygView.pictures["paladinpic"] = pygame.transform.scale(PygView.pictures["paladinpic"], (70, 70)).convert_alpha()
        
        PygView.pictures["frigatepic"] = pygame.image.load(os.path.join("data", "Frigate.png")).convert_alpha()
        PygView.pictures["frigatepic"] = pygame.transform.scale(PygView.pictures["frigatepic"], (120, 120)).convert_alpha()
        
        PygView.pictures["mothershippic"] = pygame.image.load(os.path.join("data", "Mothership.png")).convert_alpha()
        PygView.pictures["mothershippic"] = pygame.transform.scale(PygView.pictures["mothershippic"], (250, 250)).convert_alpha()
        
        PygView.pictures["dreadnaughtpic"] = pygame.image.load(os.path.join("data", "Dreadnaught.png")).convert_alpha()
        PygView.pictures["dreadnaughtpic"] = pygame.transform.scale(PygView.pictures["dreadnaughtpic"], (250, 250)).convert_alpha()
        
        PygView.pictures["turret0pic"] = pygame.image.load(os.path.join("data", "Turret0.png")).convert_alpha()
        PygView.pictures["turret0pic"] = pygame.transform.scale(PygView.pictures["turret0pic"], (60, 60)).convert_alpha()
        
        PygView.pictures["turret1pic"] = pygame.image.load(os.path.join("data", "Turret1.png")).convert_alpha()
        PygView.pictures["turret1pic"] = pygame.transform.scale(PygView.pictures["turret1pic"], (60, 60)).convert_alpha()
        
        PygView.pictures["pdturretpic"] = pygame.image.load(os.path.join("data", "PDturret.png")).convert_alpha()
        PygView.pictures["pdturretpic"] = pygame.transform.scale(PygView.pictures["pdturretpic"], (31, 31)).convert_alpha()
        
        PygView.pictures["missile0pic"] = pygame.image.load(os.path.join("data", "Missile0.png")).convert_alpha()
        PygView.pictures["missile0pic"] = pygame.transform.scale(PygView.pictures["missile0pic"], (21, 21)).convert_alpha()
        
        PygView.pictures["missile1pic"] = pygame.image.load(os.path.join("data", "Missile1.png")).convert_alpha()
        PygView.pictures["missile1pic"] = pygame.transform.scale(PygView.pictures["missile1pic"], (21, 21)).convert_alpha()
        
        PygView.pictures["pdshotpic"] = pygame.image.load(os.path.join("data", "PDshot.png")).convert_alpha()
        PygView.pictures["pdshotpic"] = pygame.transform.scale(PygView.pictures["pdshotpic"], (13, 13)).convert_alpha()
        
        
        for p in range(10):
            name = "exp" + str(p) + ".png"
            i = pygame.image.load(os.path.join("data", name)).convert_alpha()
            i = pygame.transform.scale(i, (45, 45)).convert_alpha()
            PygView.expimages.append(i)
        
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.playtime = 0.0
        self.font = pygame.font.SysFont('mono', 24, bold=True)
        for x in range (0, PygView.width, 150):
            for y in range (0, PygView.height, 87):
                paint_hex(self.background, v.Vec2d(x, y), 50)
        for x in range (0, PygView.width, 150):
            for y in range (0, PygView.height, 87):
                paint_hex(self.background, v.Vec2d(x+75, y+45), 50)

 
    def paint(self):
        """painting ships on the surface"""
        #groups
        self.allgroup =  pygame.sprite.LayeredUpdates()
        self.mtargetgroup = pygame.sprite.Group()
        self.pdtargetgroup = pygame.sprite.Group()
        self.shipgroup = pygame.sprite.Group()
        self.attackfightergroup = pygame.sprite.Group()
        self.vectorspritegroup = pygame.sprite.Group()
        self.turretgroup = pygame.sprite.Group()
        self.pdturretgroup = pygame.sprite.Group()
        self.balloongroup = pygame.sprite.Group()
        self.flytextgroup = pygame.sprite.Group()
        self.missilegroup = pygame.sprite.Group()
        self.pdshotgroup = pygame.sprite.Group()
        self.explosiongroup = pygame.sprite.Group()
        
        Flytext.groups = self.flytextgroup, self.allgroup
        VectorSprite.groups = self.allgroup, self.vectorspritegroup
        Ship.groups = self.allgroup, self.shipgroup, self.mtargetgroup
        AttackFighter.groups = self.allgroup, self.shipgroup, self.attackfightergroup, self.pdtargetgroup
        Turret.groups = self.allgroup, self.turretgroup, self.mtargetgroup
        PDturret.groups = self.allgroup, self.pdturretgroup, self.mtargetgroup
        Balloon.groups = self.allgroup, self.balloongroup, self.mtargetgroup
        Missile.groups = self.allgroup, self.missilegroup, self.pdtargetgroup
        PDshot.groups = self.allgroup, self.pdshotgroup
        Explosion.groups = self.allgroup, self.explosiongroup
        
        
        #-----------mothership1----------
        self.mothership1 = Ship(picture = PygView.pictures["mothershippic"],
                                color = (164, 164, 64),
                                party = 1, threat_lvl = 20, hitpoints = 100000)
        w = PygView.width
        h = PygView.height
        self.mothership1.path = [v.Vec2d(round(w*0.750,0), round(h*0.50,0)),
        
                                  v.Vec2d(round(w*0.725,0), round(h*0.35,0)),
                                  v.Vec2d(round(w*0.690,0), round(h*0.27,0)),
                                  v.Vec2d(round(w*0.650,0), round(h*0.20,0)),
                                  v.Vec2d(round(w*0.600,0), round(h*0.17,0)),
                                  v.Vec2d(round(w*0.575,0), round(h*0.16,0)),
                                  v.Vec2d(round(w*0.550,0), round(h*0.15,0)),
                                  v.Vec2d(round(w*0.525,0), round(h*0.15,0)),
                                 
                                 v.Vec2d(round(w*0.500,0), round(h*0.15,0)),
                                 
                                  v.Vec2d(round(w*0.475,0), round(h*0.15,0)),
                                  v.Vec2d(round(w*0.450,0), round(h*0.15,0)),
                                  v.Vec2d(round(w*0.425,0), round(h*0.16,0)),
                                  v.Vec2d(round(w*0.400,0), round(h*0.17,0)),
                                  v.Vec2d(round(w*0.350,0), round(h*0.20,0)),
                                  v.Vec2d(round(w*0.310,0), round(h*0.27,0)),
                                  v.Vec2d(round(w*0.275,0), round(h*0.35,0)),
                                  v.Vec2d(round(w*0.255,0), round(h*0.40,0)),
                                  v.Vec2d(round(w*0.250,0), round(h*0.45,0)),
                                  
                                 v.Vec2d(round(w*0.250,0), round(h*0.50,0)),
        
                                  v.Vec2d(round(w*0.250,0), round(h*0.55,0)),
                                  v.Vec2d(round(w*0.255,0), round(h*0.60,0)),
                                  v.Vec2d(round(w*0.275,0), round(h*0.65,0)),
                                  v.Vec2d(round(w*0.310,0), round(h*0.73,0)),
                                  v.Vec2d(round(w*0.350,0), round(h*0.80,0)),
                                  v.Vec2d(round(w*0.400,0), round(h*0.83,0)),
                                  v.Vec2d(round(w*0.425,0), round(h*0.84,0)),
                                  v.Vec2d(round(w*0.450,0), round(h*0.85,0)),
                                  v.Vec2d(round(w*0.475,0), round(h*0.85,0)),
                                 
                                 v.Vec2d(round(w*0.500,0), round(h*0.85,0)),
                                 
                                  v.Vec2d(round(w*0.525,0), round(h*0.85,0)),
                                  v.Vec2d(round(w*0.550,0), round(h*0.85,0)),
                                  v.Vec2d(round(w*0.575,0), round(h*0.84,0)),
                                  v.Vec2d(round(w*0.600,0), round(h*0.83,0)),
                                  v.Vec2d(round(w*0.650,0), round(h*0.80,0)),
                                  v.Vec2d(round(w*0.690,0), round(h*0.73,0)),
                                  v.Vec2d(round(w*0.725,0), round(h*0.65,0)),
                                  v.Vec2d(round(w*0.745,0), round(h*0.60,0)),
                                  v.Vec2d(round(w*0.750,0), round(h*0.55,0))
                                 ]
        self.mothership1.position = self.mothership1.path[0]
        #self.mothership0.flyToNextNavPoint() 
                                 
        
        #-----------dreadnaught2----------
        self.dreadnaught2 = Ship(picture = PygView.pictures["dreadnaughtpic"], 
                                 color = (64, 164, 164),
                                 party = 0, threat_lvl = 20, hitpoints = 120000)
        w = PygView.width
        h = PygView.height
        self.dreadnaught2.path = [v.Vec2d(round(w*0.250,0), round(h*0.50,0)),
        
                                  v.Vec2d(round(w*0.250,0), round(h*0.55,0)),
                                  v.Vec2d(round(w*0.255,0), round(h*0.60,0)),
                                  v.Vec2d(round(w*0.275,0), round(h*0.65,0)),
                                  v.Vec2d(round(w*0.310,0), round(h*0.73,0)),
                                  v.Vec2d(round(w*0.350,0), round(h*0.80,0)),
                                  v.Vec2d(round(w*0.400,0), round(h*0.83,0)),
                                  v.Vec2d(round(w*0.425,0), round(h*0.84,0)),
                                  v.Vec2d(round(w*0.450,0), round(h*0.85,0)),
                                  v.Vec2d(round(w*0.475,0), round(h*0.85,0)),
                                 
                                 v.Vec2d(round(w*0.500,0), round(h*0.85,0)),
                             
                                  v.Vec2d(round(w*0.525,0), round(h*0.85,0)),
                                  v.Vec2d(round(w*0.550,0), round(h*0.85,0)),
                                  v.Vec2d(round(w*0.575,0), round(h*0.84,0)),
                                  v.Vec2d(round(w*0.600,0), round(h*0.83,0)),
                                  v.Vec2d(round(w*0.650,0), round(h*0.80,0)),
                                  v.Vec2d(round(w*0.690,0), round(h*0.73,0)),
                                  v.Vec2d(round(w*0.725,0), round(h*0.65,0)),
                                  v.Vec2d(round(w*0.745,0), round(h*0.60,0)),
                                  v.Vec2d(round(w*0.750,0), round(h*0.55,0)),
                                 
                                 v.Vec2d(round(w*0.750,0), round(h*0.50,0)),
                                 
                                  v.Vec2d(round(w*0.750,0), round(h*0.45,0)),
                                  v.Vec2d(round(w*0.745,0), round(h*0.40,0)),
                                  v.Vec2d(round(w*0.725,0), round(h*0.35,0)),
                                  v.Vec2d(round(w*0.690,0), round(h*0.27,0)),
                                  v.Vec2d(round(w*0.650,0), round(h*0.20,0)),
                                  v.Vec2d(round(w*0.600,0), round(h*0.17,0)),
                                  v.Vec2d(round(w*0.575,0), round(h*0.16,0)),
                                  v.Vec2d(round(w*0.550,0), round(h*0.15,0)),
                                  v.Vec2d(round(w*0.525,0), round(h*0.15,0)),
                                 
                                 v.Vec2d(round(w*0.500,0), round(h*0.15,0)),
                                 
                                  v.Vec2d(round(w*0.475,0), round(h*0.15,0)),
                                  v.Vec2d(round(w*0.450,0), round(h*0.15,0)),
                                  v.Vec2d(round(w*0.425,0), round(h*0.16,0)),
                                  v.Vec2d(round(w*0.400,0), round(h*0.17,0)),
                                  v.Vec2d(round(w*0.350,0), round(h*0.20,0)),
                                  v.Vec2d(round(w*0.310,0), round(h*0.27,0)),
                                  v.Vec2d(round(w*0.275,0), round(h*0.35,0)),
                                  v.Vec2d(round(w*0.255,0), round(h*0.40,0)),
                                  v.Vec2d(round(w*0.250,0), round(h*0.45,0))
                                 ]
        self.dreadnaught2.position = self.dreadnaught2.path[0]
        self.dreadnaught2.set_angle(180)
        
        
        #-----------turretD1-------------
        self.turretD1 = Turret(picture = PygView.pictures["turret0pic"], position = self.dreadnaught2.position,
                              carrier = self.dreadnaught2, startVec = v.Vec2d(100, 0), max_range = 500,
                              party = 0, threat_lvl = 7, hitpoints = 500)
        
        
        #-----------turretD2-------------
        self.turretD2 = Turret(picture = PygView.pictures["turret0pic"],position = self.dreadnaught2.position,
                              carrier = self.dreadnaught2, startVec = v.Vec2d(75, -30), max_range = 500,
                              party = 0, threat_lvl = 7, hitpoints = 500)
                              
        
        #-----------turretD3-------------
        self.turretD3 = Turret(picture = PygView.pictures["turret0pic"],position = self.dreadnaught2.position,
                              carrier = self.dreadnaught2, startVec = v.Vec2d(75, 30), max_range = 500,
                              party = 0, threat_lvl = 7, hitpoints = 500)
                              
                              
        #-----------pdturretD1-----------    
        self.pdturretD1 = PDturret(picture = PygView.pictures["pdturretpic"],position = self.dreadnaught2.position,
                              carrier = self.dreadnaught2, startVec = v.Vec2d(50, -40), max_range = 200,
                              party = 0, threat_lvl = 7, hitpoints = 300)
                              
                              
        #-----------pdturretD2-----------    
        self.pdturretD2 = PDturret(picture = PygView.pictures["pdturretpic"],position = self.dreadnaught2.position,
                              carrier = self.dreadnaught2, startVec = v.Vec2d(-50, 0), max_range = 200,
                              party = 0, threat_lvl = 7, hitpoints = 300)
                              
                              
        #-----------pdturretD3-----------    
        self.pdturretD3 = PDturret(picture = PygView.pictures["pdturretpic"],position = self.dreadnaught2.position,
                              carrier = self.dreadnaught2, startVec = v.Vec2d(50, 40), max_range = 200,
                              party = 0, threat_lvl = 7, hitpoints = 300)
                              
                              
                              
                              
        #-----------turretM1-------------
        self.turretM1 = Turret(picture = PygView.pictures["turret1pic"],position = self.mothership1.position,
                              carrier = self.mothership1, startVec = v.Vec2d(85, 0), max_range = 700,
                              party = 1, threat_lvl = 7, hitpoints = 500)


        #-----------pdturretM1-----------    
        self.pdturretM1 = PDturret(picture = PygView.pictures["pdturretpic"],position = self.mothership1.position,
                              carrier = self.mothership1, startVec = v.Vec2d(-50, 0), max_range = 300,
                              party = 1, threat_lvl = 7, hitpoints = 300)
                              
                              
        #-----------pdturretM2-----------    
        self.pdturretM2 = PDturret(picture = PygView.pictures["pdturretpic"],position = self.mothership1.position,
                              carrier = self.mothership1, startVec = v.Vec2d(75, -30), max_range = 300,
                              party = 1, threat_lvl = 7, hitpoints = 300)
                              
                              
        #-----------pdturretM3-----------    
        self.pdturretM3 = PDturret(picture = PygView.pictures["pdturretpic"],position = self.mothership1.position,
                              carrier = self.mothership1, startVec = v.Vec2d(75, 30), max_range = 300,
                              party = 1, threat_lvl = 7, hitpoints = 300)
                              
        
        
        #_____________attackFighterD1___________
        self.attackFighterD1 = AttackFighter(picture = PygView.pictures["swarmhunterpic"],
                                             position = v.Vec2d(620,300), movement = v.Vec2d(2000, -500), 
                                             party = 0, hitpoints = 60, speed = 500)
        
        
        #_____________attackFighterD2___________
        self.attackFighterD2 = AttackFighter(picture = PygView.pictures["swarmhunterpic"],
                                             position = v.Vec2d(640,320), movement = v.Vec2d(2000, -500), 
                                             party = 0, hitpoints = 60, speed = 500)
        
        
        #_____________attackFighterD3___________
        self.attackFighterD3 = AttackFighter(picture = PygView.pictures["swarmhunterpic"],
                                             position = v.Vec2d(660,340), movement = v.Vec2d(2000, -500), 
                                             party = 0, hitpoints = 60, speed = 500)
        
        
        #_____________attackFighterD4___________
        self.attackFighterD4 = AttackFighter(picture = PygView.pictures["swarmhunterpic"],
                                             position = v.Vec2d(640,360), movement = v.Vec2d(2000, -500), 
                                             party = 0, hitpoints = 60, speed = 500)
        
        
        #_____________attackFighterD5___________
        self.attackFighterD5 = AttackFighter(picture = PygView.pictures["swarmhunterpic"],
                                             position = v.Vec2d(620,380), movement = v.Vec2d(2000, -500), 
                                             party = 0, hitpoints = 60, speed = 500)
        
        
        
        
        for b in range(20):
            Balloon(position = v.Vec2d(random.randint(278, 1100), 
                               random.randint(20, 680)), width=8, height=8, 
                               hitpoints = random.randint(40,400), party = 8967)
        
        
    def run(self):
        """-----------The mainloop------------"""
        self.paint() 
        
                   
        running = True
        while running:
            # --------- update time -------------            
            
            milliseconds = self.clock.tick(self.fps)
            seconds = milliseconds / 1000.0
            self.playtime += seconds
            
            
            # ------------ event handler: keys pressed and released -----
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False 
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    
                    #if event.key == pygame.K_l:
                    #    Flytext(self.turretD1.position.x, self.turretD1.position.y, text="lol")
                    
                    if event.key == pygame.K_e:
                        Explosion(position = v.Vec2d(650,350))        
                    
                    
                    
            # ---------- update screen ----------- 
            self.screen.blit(self.background, (0, 0))
            
            # --------- pressed key handler --------------  
            pressedkeys = pygame.key.get_pressed() 
            
            
            if pressedkeys[pygame.K_x]:
                for t in self.turretgroup:
                    pygame.draw.circle(self.screen, t.carrier.color, t.rect.center, t.max_range, 2)
            
            
            #---------FPS anzeige----------
            milliseconds = self.clock.tick(self.fps)
            seconds = milliseconds / 1000.0
            self.playtime += seconds
            
            w = PygView.width
            h = PygView.height
            write(self.screen, "FPS:  {:4.3}".format(self.clock.get_fps()), x = round(w*0.01, 0), y = round(h*0.95, 0))
            write(self.screen, "TIME:{:6.3} sec".format(self.playtime), x = round(w*0.01, 0), y = round(h*0.97, 0))
            
            #------collision dedection missile----------
            for tar in self.mtargetgroup:
                crash = pygame.sprite.spritecollide(tar, self.missilegroup, False, pygame.sprite.collide_mask)
                for m in crash:
                    if m.party == tar.party:
                        continue
                    Flytext(m.position.x, m.position.y, text="{} -{}".format(tar.hitpoints, m.damage))
                    tar.hitpoints -= m.damage
                    #Explosion(position = v.Vec2d(m.position.x, m.position.y))        
                    m.kill()
                    
            
            #------collision dedection pdshot----------
            for tar in self.pdtargetgroup:
                crash = pygame.sprite.spritecollide(tar, self.pdshotgroup, False, pygame.sprite.collide_mask)
                for pd in crash:
                    if pd.party == tar.party:
                        continue
                    Flytext(pd.position.x, pd.position.y, text="-{}".format(pd.damage))
                    tar.hitpoints -= pd.damage
                    #Explosion(position = v.Vec2d(m.position.x, m.position.y))        
                    pd.kill()
                    
            
            #-------------SchwarmUpdate------------
            #s = v.Vec2d(0,0)
            for f in self.attackfightergroup:
                if f.number == self.attackFighterD1.number:
                    continue
                f.movement *= 0.9
                f.movement += self.attackFighterD1.movement
            #s = s/len(self.attackfightergroup)
            
            
            #----------fighter follows mouse-----------
            x,y = pygame.mouse.get_pos()
            diff = v.Vec2d(x, y) - self.attackFighterD1.position
            self.attackFighterD1.movement = diff
            
            # ----------------------------
            self.allgroup.update(seconds) 
            self.allgroup.draw(self.screen)  
            
            # draw line to enemy      
            # ------ turret auto-aim------
            for tr in self.turretgroup:
                targets = []
                for ta in self.mtargetgroup:
                    if ta.party != tr.party:
                        if ta.position.get_distance(tr.position) <= tr.max_range:
                            targets.append(ta)
                            
                primaryTarget = None
                for ta in targets:
                    if primaryTarget is None:
                        primaryTarget = ta
                    elif ta.threat_lvl > primaryTarget.threat_lvl:
                        primaryTarget = ta
                if primaryTarget is not None:
                    pygame.draw.line(self.screen, (255,64,64), 
                                     (tr.position.x, tr.position.y), 
                                     (primaryTarget.position.x, primaryTarget.position.y), 1
                                    )
                    
                    
                    if random.random() < 0.03:
                        diff = primaryTarget.position - tr.position
                        diff = diff.normalized() * 300
                        Missile(picture = PygView.pictures["missile" +str(tr.party)+ "pic"], 
                                position = v.Vec2d(tr.position.x, tr.position.y), 
                                movement = diff, angle = -diff.get_angle()-180, misschance = 0.01, 
                                target = v.Vec2d(primaryTarget.position.x, primaryTarget.position.y), 
                                hitpoints = 10, damage = 50, party = tr.party, max_age = 3, 
                                max_distance = tr.max_range, threat_lvl = 8)
            
                    vectordiff = tr.position - primaryTarget.position
                    tr.set_angle(-vectordiff.get_angle()-180)
                    
                    
                    
                    
            # ------ pdturret auto-aim ------
            for tr in self.pdturretgroup:
                targets = []
                for ta in self.pdtargetgroup:
                    if ta.party != tr.party:
                        if ta.position.get_distance(tr.position) <= tr.max_range:
                            targets.append(ta)
                            
                primaryTarget = None
                for ta in targets:
                    if primaryTarget is None:
                        primaryTarget = ta
                    elif ta.threat_lvl > primaryTarget.threat_lvl:
                        primaryTarget = ta
                if primaryTarget is not None:
                    pygame.draw.line(self.screen, (0,70,150), 
                                     (tr.position.x, tr.position.y), 
                                     (primaryTarget.position.x, primaryTarget.position.y), 1
                                    )
                    
                    
                    if random.random() < 0.8:
                        diff = primaryTarget.position - tr.position
                        diff = diff.normalized() * 400
                        pdm = v.Vec2d(500, 0)
                        abetung = random.randint(-10,10)
                        vectordiff = tr.position - primaryTarget.position
                        tr.set_angle(-vectordiff.get_angle()-180 + abetung)
                        pdm = pdm.rotated(vectordiff.get_angle()-180 + abetung)
                        PDshot(picture = PygView.pictures["pdshotpic"], 
                                position = v.Vec2d(tr.position.x, tr.position.y), 
                                movement = pdm, angle = -vectordiff.get_angle()-180 + abetung, misschance = 0.01, 
                                target = v.Vec2d(primaryTarget.position.x, primaryTarget.position.y), 
                                hitpoints = 2, damage = 2, party = tr.party, max_age = 2, 
                                max_distance = tr.max_range, threat_lvl = 1)
                        
                    
           
           
            
            pygame.display.flip()
        pygame.quit()
    
####

if __name__ == '__main__':

    # call with width of window and fps
    PygView().run()

