import pygame
from settings import *
from support import *
from debug import debug

class Player(pygame.sprite.Sprite):
    
    def __init__(self,pos,groups, obstacle_sprites, create_attack, destroy_weapon):
        super().__init__(groups)
        self.image=pygame.image.load('../graphics/test/player.png').convert_alpha()
        self.rect=self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0,-26)

        #graphics setup
        self.import_player_assets()
        self.status = 'down'
        self.active_status='down'
        self.frame_index=0
        self.animation_speed=0.15
        self.obstacle_sprites = obstacle_sprites

        #weapon
        self.create_attack=create_attack
        self.destroy_weapon=destroy_weapon
        self.weapon_index=0
        self.weapon = list(weapon_data.keys())[self.weapon_index]
        self.can_switch_weapon = True 
        self.weapon_switch_time = None
        self.switch_duration_cooldown = 200

        #movement
        self.direction = pygame.math.Vector2()
        self.speed = 5
        self.attacking=False
        self.attack_cooldown=400
        self.attack_timer = None


    def import_player_assets(self):
        character_path = '../graphics/player/'
        self.animations = {'up': [], 'down': [], 'left':[], 'right':[],
        'right_idle': [], 'left_idle': [], 'up_idle':[], 'down_idle': [],
        'right_attack':[], 'left_attack':[], 'up_attack':[], 'down_attack':[]}

        for animation in self.animations.keys():
            full_path = character_path + animation
            self.animations[animation] = import_folder(full_path)


    def input(self):
        if not self.attacking:
            keys = pygame.key.get_pressed()

            #movement input
            if keys[pygame.K_w]:
                self.direction.y = -1
                self.status = 'up'
            elif keys[pygame.K_s]:
                self.direction.y = 1
                self.status='down'
            else:
                self.direction.y=0

            if keys[pygame.K_d]:
                self.direction.x = 1
                self.status='right'
            elif keys[pygame.K_a]:
                self.direction.x=-1
                self.status='left'
            else:
                self.direction.x = 0

            #attack input
            if keys[pygame.K_SPACE]:
                self.attacking=True
                self.attack_time = pygame.time.get_ticks()
                self.create_attack()

            #magic input
            if keys[pygame.K_LCTRL]:
                self.attacking=True
                self.attack_time = pygame.time.get_ticks()
                print('magic')

            #switch weapons
            if keys[pygame.K_q] and self.can_switch_weapon:
                self.can_switch_weapon = False
                self.weapon_switch_time = pygame.time.get_ticks()
                self.weapon_index+=1
                if(self.weapon_index>=len(weapon_data.keys())):
                    self.weapon_index=0
                self.weapon = list(weapon_data.keys())[self.weapon_index]


    def get_status(self):

        if self.direction.x == 0 and self.direction.y == 0:
            self.active_status = self.status + '_idle'
        else:
            self.active_status = self.status

        if self.attacking:
            self.direction.x=0
            self.direction.y=0
            self.active_status = self.status + '_attack'

        
        return self.active_status

    def cooldowns(self):
        
        current_time = pygame.time.get_ticks()

        if self.attacking:
            if current_time - self.attack_time >= self.attack_cooldown:
                self.attacking = False
                self.destroy_weapon()
        
        if not self.can_switch_weapon:
            if current_time - self.weapon_switch_time >= self.switch_duration_cooldown:
                self.can_switch_weapon=True
                

    def animate(self):
        animation = self.animations[self.active_status]
        
        self.frame_index +=self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index=0
        
        #set the image
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)

    def move(self, speed):
        if self.direction.magnitude() !=0:
            self.direction = self.direction.normalize()
        
        #move hitbox (invisible to player)
        self.hitbox.x += self.direction.x * speed
        self.collision('horizontal')
        self.hitbox.y += self.direction.y * speed
        self.collision('vertical')

        #set sprite center to hitbox (sprite visible to player)
        self.rect.center = self.hitbox.center

    def collision(self,direction):
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    #moving right
                    if self.direction.x>0:
                        self.hitbox.right = sprite.hitbox.left
                    #moving left
                    if self.direction.x<0:
                        self.hitbox.left = sprite.hitbox.right

        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    #moving down
                    if self.direction.y>0:
                        self.hitbox.bottom = sprite.hitbox.top
                    #moving up
                    if self.direction.y<0:
                        self.hitbox.top = sprite.hitbox.bottom

    def update(self):
        self.get_status()
        self.animate()
        self.input()
        self.cooldowns()
        self.move(self.speed)