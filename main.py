import sys
import pygame
from pygame.locals import *
import random
import math

pygame.init()

FPS = 60
FramePerSec = pygame.time.Clock()

BLACK = (0, 0, 0)
screen_width = 800
screen_height = 800
radius = 350

last_pt1_tick = 10 * FPS
last_pt2_tick = 28 * FPS

directions = ["up", "down", "right", "left"]

GameDisplay = pygame.display.set_mode((screen_width, screen_height))
GameDisplay.fill(BLACK)
pygame.display.set_caption("공포의 칼 피하기 께임")

class sword(pygame.sprite.Sprite):
    def __init__(self, speed, width, height, head, image): 
        pygame.sprite.Sprite.__init__(self)
        self.speed, self.width, self.height = speed, width, height

        self.head = head

        self.image = pygame.image.load(image).convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))

        self.rotated_image = pygame.transform.rotate(self.image, self.head)
        self.rect = self.rotated_image.get_rect()
        self.mask = pygame.mask.from_surface(self.rotated_image)

        self.coord = [screen_width / 2 - self.rotated_image.get_width(), screen_height / 2 - self.rotated_image.get_height()]
        self.coord[0] -= math.cos(math.radians(self.head)) * radius
        self.coord[1] -= -math.sin(math.radians(self.head)) * radius

        self.rect.topleft = self.coord

    def move(self, array):
        self.coord[0] += math.cos(math.radians(self.head)) * self.speed
        self.coord[1] += -math.sin(math.radians(self.head)) * self.speed
        self.rect.topleft = self.coord

        if pow(self.coord[0] - screen_width / 2, 2) + pow(self.coord[1] - screen_height / 2, 2) > pow(radius + self.width + 5, 2):
            array.remove(self)
                            
    def draw(self):
        GameDisplay.blit(self.rotated_image, (self.coord[0], self.coord[1]))

class flight(pygame.sprite.Sprite):
    def __init__(self, speed, coord, width, height): 
        pygame.sprite.Sprite.__init__(self)
        self.speed, self.coord, self.width, self.height = speed, coord, width, height

        self.image = pygame.image.load("textures\\apple.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))

        self.rect = self.image.get_rect()
        self.rect.topleft = self.coord
        self.mask = pygame.mask.from_surface(self.image)

        self.rest_of_shield = 0

        self.havebomb = False
        self.rest_of_flame = 0
        self.bomb_coord = [0, 0]

        self.pt1_nextpt1 = 5
        self.pt1_shooting = 0
        self.pt2_representative_head = 0
        self.pt2_nextpt2 = 5

    def collidewithsword(self, array, score):
        if pygame.sprite.spritecollide(self, array, False):
            if pygame.sprite.spritecollide(self, array, True, pygame.sprite.collide_mask):
                if self.rest_of_shield > 0:
                    self.rest_of_shield = 0
                    return True
                else:
                    self.image = pygame.image.load("textures\\cut_apple.png").convert_alpha()
                    self.image = pygame.transform.scale(self.image, (self.width, self.height))
                    gameover(self.image, self.coord, score)
                return False
            else:
                return True
        else:
            return True
        
    def collidewithshield(self, array, duration):
        if pygame.sprite.spritecollide(self, array, False):
            if pygame.sprite.spritecollide(self, array, True, pygame.sprite.collide_mask):
                self.rest_of_shield = duration * FPS

    def collidewithbomb(self, array):
        if pygame.sprite.spritecollide(self, array, False):
            if pygame.sprite.spritecollide(self, array, True, pygame.sprite.collide_mask):
                self.havebomb = True

    def usebomb(self, array):
        for swordentity in array:
            if pow((self.coord[0] + self.width / 2) - swordentity.coord[0], 2) + pow((self.coord[1] + self.height / 2) - swordentity.coord[1], 2) < 22500:
                array.remove(swordentity)
        self.havebomb = False
        self.bomb_coord = [self.coord[0] + self.width / 2 - 150, self.coord[1] + self.height / 2 - 150]
        self.rest_of_flame = 128

    def draw(self):
        GameDisplay.blit(self.image, (self.coord[0], self.coord[1]))

class edge(pygame.sprite.Sprite):
    def __init__(self, coord, image):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(image).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = coord
        self.mask = pygame.mask.from_surface(self.image)

class item(pygame.sprite.Sprite):
    def __init__(self, width, height, image):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(image)
        self.image = pygame.transform.scale(self.image, (width, height))
        self.head = random.random() * 360
        self.coord = [screen_width / 2 - self.image.get_width(), screen_height / 2 - self.image.get_height()]
        self.distance = random.random() * (radius - self.image.get_width())
        self.coord[0] -= math.cos(math.radians(self.head)) * self.distance
        self.coord[1] -= -math.sin(math.radians(self.head)) * self.distance

        self.rect = self.image.get_rect()
        self.rect.topleft = self.coord
        self.mask = pygame.mask.from_surface(self.image)
    
    def draw(self):
        GameDisplay.blit(self.image, (self.coord[0], self.coord[1]))

def pattern1(flightentity, array, tick):
    global last_pt1_tick
    if (tick - last_pt1_tick) == (flightentity.pt1_nextpt1 - 1) * FPS:
        flightentity.pt1_shooting = 4
    if (tick - last_pt1_tick) % (FPS / 3) == 0 and flightentity.pt1_shooting > 0:
        new_sword = sword(5, 58, 8, random.random() * 360, "textures\\blue_sword.png")
        new_sword.head = math.degrees(math.atan(-((new_sword.coord[1] + new_sword.rotated_image.get_height() / 2) - (flightentity.coord[1] + flightentity.height / 2))/((new_sword.coord[0] + new_sword.rotated_image.get_width() / 2) - (flightentity.coord[0] - flightentity.width / 2))))
        if new_sword.coord[0] + new_sword.rotated_image.get_width() / 2 > screen_width / 2 and new_sword.coord[1] + new_sword.rotated_image.get_height() / 2 < screen_height / 2: #1사분면
            new_sword.head += 180
        if new_sword.coord[0] + new_sword.rotated_image.get_width() / 2 < screen_width / 2 and new_sword.coord[1] + new_sword.rotated_image.get_height() / 2 < screen_height / 2: #2사분면
            new_sword.head += 360
        if new_sword.coord[0] + new_sword.rotated_image.get_width() / 2 > screen_width / 2 and new_sword.coord[1] + new_sword.rotated_image.get_height() / 2 > screen_height / 2: #4사분면
            new_sword.head += 180
        new_sword.rotated_image = pygame.transform.rotate(new_sword.image, new_sword.head)
        new_sword.rect = new_sword.rotated_image.get_rect()
        new_sword.mask = pygame.mask.from_surface(new_sword.rotated_image)
        array.add(new_sword)
        flightentity.pt1_shooting -= 1
    if (tick - last_pt1_tick) == (flightentity.pt1_nextpt1 * FPS):
        flightentity.pt1_nextpt1 = random.randint(3, 7)
        last_pt1_tick = tick 

def pattern2(flightentity, array, tick):
    global last_pt2_tick
    if (tick - last_pt2_tick) == (flightentity.pt2_nextpt2 - 2) * FPS:
        flightentity.pt2_representative_head = random.random() * 360
    elif (tick - last_pt2_tick) > (flightentity.pt2_nextpt2 - 2) * FPS and (tick - last_pt2_tick) < flightentity.pt2_nextpt2 * FPS:
        return True
    elif (tick - last_pt2_tick) == flightentity.pt2_nextpt2 * FPS:
        for i in range(-3, 4):
            array.add(sword(6, 58, 8, flightentity.pt2_representative_head + 22 * i, "textures\\red_sword.png"))
        flightentity.pt2_nextpt2 = random.randrange(4, 8)
        last_pt2_tick = tick

def pause():
    pause_running = True
    pause_text = pygame.font.SysFont("Sans", 50).render("Press space to start...", True, (192, 192, 0))
    while pause_running:
        pygame.display.update()
        GameDisplay.blit(pause_text, (screen_width / 2 - pause_text.get_width() / 2, screen_height / 2 - pause_text.get_height() / 2))
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == pygame.K_SPACE:
                    pause_running = False
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

def gameover(flight_image, flight_coord, score):
    gameover_running = True
    black_image = pygame.image.load("textures\\black_apple.png").convert_alpha()
    black_image = pygame.transform.scale(black_image, (48, 58))
    gameover_image = pygame.image.load("textures\\gameover.png").convert_alpha()
    gameover_image = pygame.transform.scale(gameover_image, (768, 248))
    scoretext = pygame.font.SysFont("Sans", 50).render(f"SCORE: {score}", True, (255, 255, 0))
    guidetext = pygame.font.SysFont("Sans", 30).render(f"press space to continue...", True, (128, 128, 0))
    while gameover_running:
        pygame.display.update()
        GameDisplay.blit(black_image, flight_coord)
        GameDisplay.blit(flight_image, flight_coord)
        GameDisplay.blit(gameover_image, (screen_width / 2 - gameover_image.get_width() / 2, 50))
        GameDisplay.blit(scoretext, (screen_width / 2 - scoretext.get_width() / 2, 500))
        GameDisplay.blit(guidetext, (screen_width / 2 - guidetext.get_width() / 2, 550))
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == pygame.K_SPACE:
                    gameover_running = False
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

def main():
    running = True
    tick = 0
    on_pattern1 = False
    on_pattern2 = False
    global last_pt1_tick, last_pt2_tick
    swordlist = pygame.sprite.Group()
    flightentity = flight(7, [screen_width / 2 - 24, screen_height / 2 - 29], 48, 58)

    shieldlist = pygame.sprite.Group()
    bomblist = pygame.sprite.Group()

    for i in directions:
        globals()[f"{i}edge"] = edge(flightentity.coord, f"textures\\{i}edge.png")

    score = 0

    shield_able = False
    bomb_able = False
    last_shield_tick = 0
    last_bomb_tick = 0
    shield_duration = 15

    shield_image = pygame.image.load("textures\\shield.png").convert_alpha()
    shield_image = pygame.transform.scale(shield_image, (50, 50))
    shield_on_apple_image = pygame.image.load("textures\\shield_on_apple.png").convert_alpha()
    shield_on_apple_image = pygame.transform.scale(shield_on_apple_image, (96, 116))

    bomb_image = pygame.image.load("textures\\bomb.png").convert_alpha()
    bomb_image = pygame.transform.scale(bomb_image, (66, 38))
    flame_image = pygame.image.load("textures\\flame.png").convert_alpha()
    flame_image = pygame.transform.scale(flame_image, (300, 300))

    field = pygame.sprite.Sprite()
    field.image = pygame.image.load("textures\\field.png").convert_alpha()
    field.rect = field.image.get_rect()
    field.rect.topleft = (0, 0)
    field.mask = pygame.mask.from_surface(field.image)

    while running:
        tick += 1

        if tick == last_pt1_tick:
            on_pattern1 = True

        if tick == last_pt2_tick:
            on_pattern2 = True

        if on_pattern1:
            pattern1(flightentity, swordlist, tick)
        
        if on_pattern2:
            pt2_warning = pattern2(flightentity, swordlist, tick)

        if tick % (5 * FPS / 6) == 0:
            swordlist.add(sword(random.random() * 4 + 4, 58, 8, random.random() * 360, "textures\\sword.png"))
            
        if tick % (FPS / 6) == 0:
            score += 1

        if shield_able == False and tick - last_shield_tick > 20 * FPS:
            shield_able = True
        
        if bomb_able == False and tick - last_bomb_tick > 20 * FPS:
            bomb_able = True
        
        if shield_able and random.random() < 0.003:
            shield_able = False
            last_shield_tick = tick
            shieldlist.add(item(50, 50, "textures\\shield.png"))

        if bomb_able and random.random() < 0.002:
            bomb_able = False
            last_bomb_tick = tick
            bomblist.add(item(66, 38, "textures\\bomb.png"))

 
        pygame.display.update()
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
                if flightentity.havebomb and event.key == pygame.K_z:
                    flightentity.usebomb(swordlist)

        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_w] or pressed[pygame.K_UP]:
            if pygame.sprite.collide_mask(globals()["upedge"], field):
                theta = math.atan(-((flightentity.coord[1] + flightentity.height / 2) - screen_height / 2) / ((flightentity.coord[0] + flightentity.width / 2) - screen_width / 2))
                flightentity.coord[0] -= flightentity.speed * math.cos(theta) * math.sin(theta)
                flightentity.coord[1] -= flightentity.speed * math.cos(theta) * math.cos(theta)
            else:
                flightentity.coord[1] -= flightentity.speed
        if pressed[pygame.K_s] or pressed[pygame.K_DOWN]:
            if pygame.sprite.collide_mask(globals()["downedge"], field):
                theta = math.atan(-((flightentity.coord[1] + flightentity.height / 2) - screen_height / 2) / ((flightentity.coord[0] + flightentity.width / 2) - screen_width / 2))
                flightentity.coord[0] -= flightentity.speed * math.cos(-theta) * math.sin(-theta)
                flightentity.coord[1] += flightentity.speed * math.cos(-theta) * math.cos(-theta)
            else:
                flightentity.coord[1] += flightentity.speed
        if pressed[pygame.K_d] or pressed[pygame.K_RIGHT]:
            if pygame.sprite.collide_mask(globals()["rightedge"], field):
                theta = math.atan(-((flightentity.coord[1] + flightentity.height / 2) - screen_height / 2) / ((flightentity.coord[0] + flightentity.width / 2) - screen_width / 2))
                flightentity.coord[0] += flightentity.speed * math.sin(theta) * math.sin(theta)
                flightentity.coord[1] += flightentity.speed * math.sin(theta) * math.cos(theta)
            else:
                flightentity.coord[0] += flightentity.speed
        if pressed[pygame.K_a] or pressed[pygame.K_LEFT]:
            if pygame.sprite.collide_mask(globals()["leftedge"], field):
                theta = math.atan(-((flightentity.coord[1] + flightentity.height / 2) - screen_height / 2) / ((flightentity.coord[0] + flightentity.width / 2) - screen_width / 2))
                flightentity.coord[0] -= flightentity.speed * math.sin(-theta) * math.sin(-theta)
                flightentity.coord[1] += flightentity.speed * math.sin(-theta) * math.cos(-theta)
            else:
                flightentity.coord[0] -= flightentity.speed

        
                
        flightentity.rect.topleft = flightentity.coord
        for i in directions:
            globals()[f"{i}edge"].rect.topleft = flightentity.coord
        

        GameDisplay.fill(BLACK)

        flightentity.draw()

        for swordentity in swordlist:
            swordentity.move(swordlist)
            swordentity.draw()

        for shieldentity in shieldlist:
            shieldentity.draw()

        for bombentity in bomblist:
            bombentity.draw()

        GameDisplay.blit(field.image, (0, 0))

        rest_of_shield_text = pygame.font.SysFont("Sans", 50).render(f"{round(flightentity.rest_of_shield / FPS, 1)}s", True, (0, 255, 0))
        bomb_text = pygame.font.SysFont("Sans", 50).render("z", True, (0, 255, 0))

        if flightentity.rest_of_shield > 0:
            GameDisplay.blit(shield_image, (20, 20))
            GameDisplay.blit(shield_on_apple_image, (flightentity.coord[0] - 24, flightentity.coord[1] - 39))
            GameDisplay.blit(rest_of_shield_text, (20 + shield_image.get_width() / 2 - rest_of_shield_text.get_width() / 2, 80))
            flightentity.rest_of_shield -= 1
        else:
            flightentity.collidewithshield(shieldlist, shield_duration)

        if flightentity.havebomb:
            GameDisplay.blit(bomb_image, (100, 20))
            GameDisplay.blit(bomb_text, (100 + bomb_image.get_width() / 2 - bomb_text.get_width() / 2, 80))
        else:
            flightentity.collidewithbomb(bomblist)

        if flightentity.rest_of_flame > 0:
            GameDisplay.blit(flame_image, flightentity.bomb_coord)
            flame_image.set_alpha(flightentity.rest_of_flame)
            flightentity.rest_of_flame -= 1

        if on_pattern2 and pt2_warning:
            GameDisplay.blit(pygame.font.SysFont("Sans", 100).render("!", True, (255, 128, 0)), (screen_width / 2 - (math.cos(math.radians(flightentity.pt2_representative_head)) * radius * 6 / 7) - 2, screen_height / 2 + (math.sin(math.radians(flightentity.pt2_representative_head)) * radius * 6 / 7) - 10))

        score_text = pygame.font.SysFont("Sans", 50).render(f"SCORE: {score}", True, (255, 255, 0))
        GameDisplay.blit(score_text, (screen_width / 2 - score_text.get_width() / 2, 0))

        running = flightentity.collidewithsword(swordlist, score)

        FramePerSec.tick(FPS)
pause()
main()