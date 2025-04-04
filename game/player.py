import pygame
import math
import os
from .items import ABILITIES

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 60
        self.speed = 5
        self.health = 10
        self.max_health = 10
        self.mana = 100
        self.max_mana = 100
        self.facing_right = True  # Direção que o jogador está olhando
        self.message_timer = 0
        self.damage_flash_timer = 0
        self.damage_flash_duration = 500
        self.invincible_timer = 0
        self.invincible_duration = 1000
        self.in_castle = False
        self.in_water = False
        self.is_dead = False
        self.jump_power = -15
        self.gravity = 0.8
        self.vertical_speed = 0
        self.max_fall_speed = 20
        self.abilities = {
            'fireball': ABILITIES['fireball'](),
            'teleport': ABILITIES['teleport']()
        }
        self.inventory = []
        self.last_update = pygame.time.get_ticks()
        
        # Nome do jogador
        self.name = "Andre Pereira"
        
        # Fonte para textos
        self.font = pygame.font.Font(None, 24)
        
        # Atributos básicos
        self.mana_regen = 1  # Mana regenerada por segundo
        self.last_mana_regen = pygame.time.get_ticks()
        
        # Inventário e habilidades
        self.selected_ability = None
        self.experience = 0
        self.level = 1
        self.exp_to_next_level = 100
        
        # Estados
        self.is_jumping = False
        self.vertical_velocity = 0
        
        # Timers e cooldowns
        self.damage_flash_timer = 0
        self.damage_flash_duration = 30
        self.last_damage_time = 0
        self.damage_cooldown = 1000  # 1 segundo
        self.water_effect_timer = 0
        self.water_effect_alpha = 0
        
        # Configurações de pulo
        self.gravity = 0.5
        self.jump_power = 10
        self.max_fall_speed = 10
        
        # Carregar imagem
        self.image = pygame.image.load(os.path.join('assets', 'images', 'magic.png')).convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        self.image_right = pygame.transform.flip(self.image, True, False)
        self.image_left = self.image
        
        # Cria o retângulo de colisão
        self.rect = pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def add_item(self, item):
        self.inventory.append(item)
        
    def remove_item(self, item):
        if item in self.inventory:
            self.inventory.remove(item)
            
    def use_item(self, item_index):
        if 0 <= item_index < len(self.inventory):
            item = self.inventory[item_index]
            if item.use(self):
                self.remove_item(item)
                
    def add_ability(self, ability):
        self.abilities.append(ability)
        if self.selected_ability is None:
            self.selected_ability = ability
            
    def use_ability(self, game):
        if self.selected_ability and self.mana >= self.selected_ability.mana_cost:
            if self.selected_ability.use(self, game):
                self.mana -= self.selected_ability.mana_cost
                
    def gain_experience(self, amount):
        self.experience += amount
        while self.experience >= self.exp_to_next_level:
            self.level_up()
            
    def level_up(self):
        self.level += 1
        self.experience -= self.exp_to_next_level
        self.exp_to_next_level = int(self.exp_to_next_level * 1.5)
        self.max_health += 2
        self.health = self.max_health
        self.max_mana += 10
        self.mana = self.max_mana
        
    def take_damage(self):
        if not self.in_water:  # Só toma dano se estiver na água
            return
            
        current_time = pygame.time.get_ticks()
        if current_time - self.last_damage_time >= self.damage_cooldown:
            self.health -= 1
            self.last_damage_time = current_time
            self.damage_flash_timer = self.damage_flash_duration
            
            if self.health <= 0:
                self.is_dead = True

    def enter_castle(self):
        if not self.in_castle:
            self.in_castle = True
            self.message_timer = 180  # 3 segundos a 60 FPS

    def leave_castle(self):
        self.in_castle = False

    def enter_water(self):
        if not self.in_water:
            self.in_water = True
            self.water_effect_timer = 0

    def leave_water(self):
        if self.in_water:
            self.in_water = False
            self.water_effect_timer = 0
            self.damage_flash_timer = 0  # Reseta o timer de dano ao sair da água

    def update(self):
        # Movimento horizontal
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
            self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed
            self.facing_right = True
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += self.speed
            
        # Atualiza os timers
        current_time = pygame.time.get_ticks()
        if self.damage_flash_timer > 0:
            self.damage_flash_timer = max(0, self.damage_flash_timer - (current_time - self.last_update))
        if self.invincible_timer > 0:
            self.invincible_timer = max(0, self.invincible_timer - (current_time - self.last_update))
        if self.message_timer > 0:
            self.message_timer = max(0, self.message_timer - (current_time - self.last_update))
            
        self.last_update = current_time
        
        # Uso de habilidades
        if keys[pygame.K_q]:  # Bola de Fogo
            self.abilities['fireball'].use(self, None)
        elif keys[pygame.K_e]:  # Teleporte
            self.abilities['teleport'].use(self, None)
        
        # Atualiza regeneração de mana
        if current_time - self.last_mana_regen >= 1000:  # A cada segundo
            self.mana = min(self.mana + self.mana_regen, self.max_mana)
            self.last_mana_regen = current_time
        
        # Atualiza o timer de dano
        if self.damage_flash_timer > 0:
            self.damage_flash_alpha = (self.damage_flash_timer / self.damage_flash_duration) * 255
            
        # Atualiza o efeito de água
        if self.in_water:
            self.water_effect_alpha = min(self.water_effect_alpha + 5, 128)
            # Aplica dano a cada 60 frames (1 segundo) se estiver na água
            if pygame.time.get_ticks() % 60 == 0:
                self.take_damage()
        else:
            self.water_effect_alpha = max(self.water_effect_alpha - 5, 0)
            
        # Atualiza o retângulo de colisão
        self.rect.x = self.x
        self.rect.y = self.y

    def draw(self, screen, camera_x, camera_y):
        # Calcula a posição na tela
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # Desenha o jogador
        current_image = self.image_right if self.facing_right else self.image_left
        screen.blit(current_image, (screen_x - self.width/2, screen_y - self.height/2))
        
        # Desenha a barra de vida
        health_width = 40
        health_height = 5
        health_x = screen_x - health_width/2
        health_y = screen_y - self.height/2 - 10
        
        # Fundo da barra de vida
        pygame.draw.rect(screen, (255, 0, 0), (health_x, health_y, health_width, health_height))
        # Vida atual
        current_health_width = (self.health / self.max_health) * health_width
        pygame.draw.rect(screen, (0, 255, 0), (health_x, health_y, current_health_width, health_height))
        
        # Efeito de dano
        if self.damage_flash_timer > 0:
            flash_surface = pygame.Surface((self.width, self.height))
            flash_surface.fill((255, 0, 0))
            flash_surface.set_alpha(self.damage_flash_timer)
            screen.blit(flash_surface, (screen_x - self.width/2, screen_y - self.height/2))
        
        # Desenha o nome do jogador acima do personagem
        name_text = self.font.render(self.name, True, (255, 255, 255))
        name_rect = name_text.get_rect(center=(screen_x + self.width/2, screen_y - 20))
        # Adiciona um fundo escuro semi-transparente para melhor legibilidade
        bg_rect = name_rect.inflate(20, 10)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 128))
        screen.blit(bg_surface, bg_rect)
        screen.blit(name_text, name_rect)
        
        # Efeito de água
        if self.in_water:
            water_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            alpha = int(128 + math.sin(pygame.time.get_ticks() * 0.01) * 64)  # Varia entre 64 e 192
            water_surface.fill((0, 0, 255, alpha))  # Azul com transparência variável
            screen.blit(water_surface, (screen_x - self.width/2, screen_y - self.height/2))
            
        # Mensagem do castelo
        if self.in_castle and self.message_timer > 0:
            text = self.font.render("Bem-vindo ao Castelo!", True, (255, 255, 255))
            text_rect = text.get_rect(center=(screen.get_width()/2, 50))
            screen.blit(text, text_rect)
            
        # Desenha as instruções das teclas
        instructions = [
            "Setas: Mover",
            "ESC: Sair",
            f"Vida: {self.health}/{self.max_health}"
        ]
        for i, text in enumerate(instructions):
            text_surface = self.font.render(text, True, (255, 255, 255))
            screen.blit(text_surface, (10, 10 + i * 30)) 