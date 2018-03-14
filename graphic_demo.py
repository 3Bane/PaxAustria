
"""
author: Wilhelm Poigner
email: 3xtraktor@gmail.com
"""

import pygame 
import math
import random
import os
import operator
import Vector_2D as v


####
        
####

class VectorSprite(pygame.sprite.Sprite):
    """base class for sprites. this class inherits from pygames sprite class"""
    number = 0
    numbers = {} # { number, Sprite }
    
    def __init__(self, layer=4, **kwargs):
        """create a (black) surface and paint a blue ball on it"""
        self._layer = layer   # pygame Sprite layer
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
        
        for key, arg in kwargs.items():
            #print(key, arg)
            setattr(self, key, arg)
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
            self.kill_on_edge = False
        if "kill_with_boss" not in kwargs:
            self.kill_with_boss = False
        if "mass" not in kwargs:
            self.mass = 10
        if "maxage" not in kwargs:
            self.max_age = None
        if "max_distance" not in kwargs:
            self.max_distance = None
        if "max_range" not in kwargs:
            self.max_range = 400
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
        if "threat_lvl" not in kwargs:
            self.threat_lvl = random.randint(0, 5)
        if "turnspeed" not in kwargs:
            self.turnspeed = 5
        if "width" not in kwargs:
            self.width = self.radius * 2
        # ---
        self.create_image()
        
        
    def kill(self):
        del VectorSprite.numbers[self.number] # remove Sprite from numbers dict
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
        if self.max_distance is not None and self.distance > self.max_distance:
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


class Turret(VectorSprite):
    
    def update(self, seconds):
        VectorSprite.update(self, seconds)
        vec = self.startVec.rotated(self.carrier.faceing)
        self.position = self.carrier.position + vec
        

class Ship(VectorSprite):
    
    def update(self, seconds):
        self.flyToNextNavPoint()
        VectorSprite.update(self, seconds)
        
        
####

def write(background, text, x=50, y=20, color=(0,0,0),
          fontsize=None, center=False):
        """write text on pygame surface. """
        if fontsize is None:
            fontsize = 24
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
  
    def __init__(self, width=1300, height=700, gridsize=50, fps=30):
        """Initialize pygame, window, background, font,...
           default arguments 
        """
        pygame.init()
        pygame.display.set_caption("ESC to quit")
        PygView.width = width    # also self.width 
        PygView.height = height  # also self.height
        PygView.gridsize = gridsize 
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        tmp = pygame.image.load(os.path.join("data","background06.jpg"))
        self.background = pygame.transform.scale(tmp, (self.width, self.height))
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
        PygView.pictures["bomberpic"] = pygame.image.load(os.path.join("data", "Bomber.png")).convert_alpha()
        PygView.pictures["paladinpic"] = pygame.image.load(os.path.join("data", "Paladin.png")).convert_alpha()
        PygView.pictures["frigatepic"] = pygame.image.load(os.path.join("data", "Frigate.png")).convert_alpha()
        PygView.pictures["mothershippic"] = pygame.image.load(os.path.join("data", "Mothership.png")).convert_alpha()
        PygView.pictures["dreadnaughtpic"] = pygame.image.load(os.path.join("data", "Dreadnaught.png")).convert_alpha()
        PygView.pictures["turretpic"] = pygame.image.load(os.path.join("data", "Turret.png")).convert_alpha()
        
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
        self.targetgroup = pygame.sprite.Group()
        self.shipgroup = pygame.sprite.Group()
        self.vectorspritegroup = pygame.sprite.Group()
        self.turretgroup = pygame.sprite.Group()
        self.balloongroup = pygame.sprite.Group()
        
        VectorSprite.groups = self.allgroup, self.vectorspritegroup
        Ship.groups = self.allgroup, self.shipgroup, self.targetgroup
        Turret.groups = self.allgroup, self.turretgroup, self.targetgroup
        Balloon.groups = self.allgroup, self.balloongroup, self.targetgroup
        
        
        #-----------mothership1----------
        self.mothership1 = Ship(picture = PygView.pictures["mothershippic"],
                                color = (164, 164, 64),
                                party=1, hitpoints = 7500, threat_lvl = 20)
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
                                 party = 2, hitpoints = 8000, threat_lvl = 20)
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
        self.turretD1 = Turret(picture = PygView.pictures["turretpic"],position = self.dreadnaught2.position,
                              carrier = self.dreadnaught2, startVec = v.Vec2d(100, 0), max_range = 500,
                              party = 2, hitpoints = 250, threat_lvl = 10)
        
        
        #-----------turretD2-------------
        self.turretD2 = Turret(picture = PygView.pictures["turretpic"],position = self.dreadnaught2.position,
                              carrier = self.dreadnaught2, startVec = v.Vec2d(75, -30), max_range = 500,
                              party = 2, hitpoints = 250, threat_lvl = 10)
                              
        
        #-----------turretD3-------------
        self.turretD3 = Turret(picture = PygView.pictures["turretpic"],position = self.dreadnaught2.position,
                              carrier = self.dreadnaught2, startVec = v.Vec2d(75, 30), max_range = 500,
                              party = 2, hitpoints = 250, threat_lvl = 10)
                              
        
        #-----------turretM1-------------
        self.turretM1 = Turret(picture = PygView.pictures["turretpic"],position = self.mothership1.position,
                              carrier = self.mothership1, startVec = v.Vec2d(85, 0), max_range = 400,
                              party = 1, hitpoints = 250, threat_lvl = 10)
        
        for b in range(50):
            Balloon(position = v.Vec2d(random.randint(278, 1000), 
                               random.randint(20, 680)), width=8, height=8, 
                               hitpoints = random.randint(40,400))
        
        
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
                    
            # ---------- update screen ----------- 
            self.screen.blit(self.background, (0, 0))
            
            # --------- pressed key handler --------------  
            pressedkeys = pygame.key.get_pressed() 
            
            
            if pressedkeys[pygame.K_x]:
                for t in self.turretgroup:
                    pygame.draw.circle(self.screen, t.carrier.color, t.rect.center, t.max_range, 2)
            
            
            
          
            
            self.allgroup.update(seconds) 
            self.allgroup.draw(self.screen)  
            
            # draw line to enemy      
            # ------ turret auto-aim------
            for tr in self.turretgroup:
                targets = []
                for ta in self.targetgroup:
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
                    pygame.draw.line(self.screen, (64,64,64), 
                                     (tr.position.x, tr.position.y), 
                                     (primaryTarget.position.x, primaryTarget.position.y), 1
                                    )
            
                vectordiff = self.turretD1.position - primaryTarget.position
                tr.set_angle(-vectordiff.get_angle()-180)
           
            
            pygame.display.flip()
        pygame.quit()
    
####

if __name__ == '__main__':

    # call with width of window and fps
    PygView().run()

