import pygame, sys, random, math, os
from pygame.locals import *

SCREEN_SIZE = SCREEN_W, SCREEN_H = (800, 800)
PADDING = 10

BG_COLOR = (48, 54, 47)
WHITE = (255, 251, 219)
BLUE = (114, 132, 168)
RED = (255, 140, 97)
GREEN = (96, 211, 148)
COLORS = [WHITE, BLUE, RED, GREEN]
TYPES = ["wHITE", "BLUE", "RED", "GREEN"]

PARTICLE_NUM = 100
PARTICLES = []
TRAILS = []
PARTICLES_BY_TYPE = [[], [], [], []]
MAX_SPEED = 2
FORCE = 10
DISTANCE_PUSH_THRESHOLD = 40
DISTANCE_PULL_THRESHOLD = 100

# Initial setup
pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("Particle's Life")


clock = pygame.time.Clock()

class Particle:
  def __init__(self, initialPos, color, mass, screen, acceleration, particleType):
    self.position = initialPos
    self.color = color
    self.mass = mass
    self.size = mass
    self.screen = screen
    self.velocity = (0, 0)
    self.acceleration = acceleration
    self.type = particleType
    
    x = random.uniform(-1, 1)
    y = random.uniform(-1, 1)
    length = math.sqrt(x**2 + y**2)
    self.direction = (x/length, y/length)
    
  def accelerate(self):
    speedVector = (self.velocity[0] + self.acceleration[0] + random.uniform(-0.5, 0.5), self.velocity[1] + self.acceleration[1] + random.uniform(-0.5, 0.5))
    speed = math.sqrt(speedVector[0]**2 + speedVector[1]**2)
    if (speed < MAX_SPEED): 
      self.velocity = speedVector
    else:
      self.acceleration = (0, 0)
      
  def draw(self):
    pygame.draw.circle(self.screen, self.color, self.position, self.size)
    TRAILS.append(Trail(self.position, self.color))
    
  def drawLine(self, other):
    # pygame.draw.line(self.screen, self.color, self.position, other.position)
    pass
    
  def wallCollisionCheck(self):
    if (self.position[0] + self.velocity[0] > SCREEN_W - self.size or self.position[0] + self.velocity[0] < self.size ):
      self.velocity = (-self.velocity[0], self.velocity[1])
      self.acceleration = (-self.acceleration[0], self.acceleration[1])
    if (self.position[1] + self.velocity[1] > SCREEN_H - self.size or self.position[1] + self.velocity[1] < self.size ):
      self.velocity = (self.velocity[0], -self.velocity[1])
      self.acceleration = (self.acceleration[0], -self.acceleration[1])
  
  def comeTowardsOther(self, other):
    distance = math.sqrt((self.position[0]-other.position[0])**2 + (self.position[1]-other.position[1])**2 + 1)
    pullDirection = (other.position[0] - self.position[0], other.position[1] - self.position[1])
    # self.acceleration = (self.acceleration[0] + pullDirection[0]*FORCE, self.acceleration[1] + pullDirection[1]*FORCE)
    self.acceleration = (self.acceleration[0] + pullDirection[0]*FORCE/(self.mass*distance**2), self.acceleration[1] + pullDirection[1]*FORCE/(self.mass*distance**2))
    
  def awayFromOther(self, other):
    distance = math.sqrt((self.position[0]-other.position[0])**2 + (self.position[1]-other.position[1])**2 + 1)
    pushDirection = (-other.position[0] + self.position[0], -other.position[1] + self.position[1])
    # self.acceleration = (self.acceleration[0] + pushDirection[0]*FORCE, self.acceleration[1] + pushDirection[1]*FORCE)
    self.acceleration = (self.acceleration[0] + pushDirection[0]*FORCE/(self.mass*distance**2), self.acceleration[1] + pushDirection[1]*FORCE/(self.mass*distance**2))
    
  def pushAndPull(self, other):
    distance = math.sqrt((self.position[0]-other.position[0])**2 + (self.position[1]-other.position[1])**2)
    if (distance <= DISTANCE_PULL_THRESHOLD and distance > 0):
      if (self.type == other.type):
        # self.drawLine(other)
        self.comeTowardsOther(other)
      if (distance < self.size*2 + other.size and distance != 0):
        self.awayFromOther(other)
        if (self.type == other.type):
          self.drawLine(other)
      if (distance <= DISTANCE_PULL_THRESHOLD and distance > 0):
        if ((self.type == "GREEN" and other.type == "BLUE") or (self.type == "GREEN" and other.type == "WHITE")):
          self.comeTowardsOther(other)
        if ((self.type == "GREEN" or self.type == "BLUE") and (other.type == "RED" or other.type == "WHITE")):
          other.awayFromOther(self)
          self.comeTowardsOther(other)
    if (distance <= DISTANCE_PULL_THRESHOLD and distance > DISTANCE_PUSH_THRESHOLD):
      self.awayFromOther(other)
          
  def update(self):
    for p in PARTICLES:
      self.pushAndPull(p)
    self.wallCollisionCheck()
    self.accelerate()
    self.position = (self.position[0] + self.velocity[0], self.position[1] + self.velocity[1])
    self.draw()
 
class Trail:
  def __init__(self, position, color):
    self.position = position
    self.color = color
    self.size = 4
    self.lifeTime = 3
    
  def update(self):
    pygame.draw.circle(screen, self.color, self.position, self.size)
    self.lifeTime -= 0.1
    self.size -= 0.2
  
def createRandomParticle():
  index = random.choice([0, 1, 2, 3])
  color = COLORS[index]
  particleType = TYPES[index]
  position = (random.randint(PADDING, SCREEN_W-PADDING), random.randint(PADDING, SCREEN_H-PADDING))
  mass = 4
  acceleration = (0, 0)
  p = Particle(position, color, mass, screen, acceleration, particleType)
  PARTICLES_BY_TYPE[index].append(p)
  return p

def resource_path(relative_path):
    try:
    # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

for i in range(PARTICLE_NUM):
  PARTICLES.append(createRandomParticle())
  
# Game loop
while True:
  screen.fill(BG_COLOR)
  for particle in PARTICLES:
    particle.update()
  for trail in TRAILS:
    trail.update()
    if (trail.lifeTime <= 0):
      TRAILS.remove(trail)
    
  # for i in range(4):
  #   for j in range(len(PARTICLES_BY_TYPE[i].) - 1):
  #     p = PARTICLES_BY_TYPE[i][j]
  #     pp =PARTICLES_BY_TYPE[i][j+1]
  #     p.drawLine(pp)
    
  for event in pygame.event.get():
    if event.type == QUIT:
      pygame.quit()
      sys.exit()
    if event.type == KEYDOWN:
      if event.key == K_r:
        PARTICLES = []
        for i in range(PARTICLE_NUM):
          PARTICLES.append(createRandomParticle())

  pygame.display.update()
  clock.tick(300)
      