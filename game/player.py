import pygame
import math
import os

class Player:
    def __init__(self, name, character_class):
        self.name = name
        self.character_class = character_class
        
        # Posição e dimensões
        self.x = 400
        self.y = 300
        self.width = 48
        self.height = 48
        self.speed = 5
        
        # Vida
        self.health = 10
        self.max_health = 10
        
        # Carrega a imagem do jogador
        self.image = pygame.image.load(os.path.join('assets', 'images', 'magic.png')).convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        self.image_left = self.image
        self.image_right = pygame.transform.flip(self.image, True, False)
        self.facing_right = True
        
        # Retângulo para colisão
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Estado do jogador
        self.in_castle = False
        self.in_water = False
        self.is_dead = False
        
        # Timers e efeitos
        self.message_timer = 0
        self.damage_flash_timer = 0
        self.damage_flash_alpha = 0
        self.damage_flash_duration = 30  # Duração do flash em frames
        self.water_effect_alpha = 0
        self.water_effect_timer = 0
        self.last_damage_time = 0
        self.damage_cooldown = 1000  # 1 segundo
        
        # Configurações de pulo
        self.is_jumping = False
        self.vertical_velocity = 0
        self.gravity = 0.5
        self.jump_power = 10
        self.max_fall_speed = 10
        
        # Fonte para mensagens
        self.font = pygame.font.Font(None, 36)

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
        # Atualiza o timer de dano
        if self.damage_flash_timer > 0:
            self.damage_flash_timer -= 1
            self.damage_flash_alpha = (self.damage_flash_timer / self.damage_flash_duration) * 255
            
        # Atualiza o timer da mensagem do castelo
        if self.message_timer > 0:
            self.message_timer -= 1
            
        # Atualiza o efeito de água
        if self.in_water:
            self.water_effect_alpha = min(self.water_effect_alpha + 5, 128)
            # Aplica dano a cada 60 frames (1 segundo) se estiver na água
            if pygame.time.get_ticks() % 60 == 0:
                self.take_damage()
        else:
            self.water_effect_alpha = max(self.water_effect_alpha - 5, 0)
            
        # Atualiza o pulo
        if self.is_jumping:
            self.vertical_velocity = min(self.vertical_velocity + self.gravity, self.max_fall_speed)
            if self.vertical_velocity >= 0:
                self.is_jumping = False
                self.vertical_velocity = 0
                
        # Processa input do teclado
        keys = pygame.key.get_pressed()
        
        # Movimento horizontal
        if keys[pygame.K_LEFT]:
            self.x -= self.speed
            self.facing_right = False
        if keys[pygame.K_RIGHT]:
            self.x += self.speed
            self.facing_right = True
            
        # Movimento vertical
        if keys[pygame.K_UP]:
            self.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.y += self.speed
            
        # Pulo
        if keys[pygame.K_SPACE] and not self.is_jumping:
            self.is_jumping = True
            self.vertical_velocity = -self.jump_power
            
        # Atualiza o retângulo de colisão
        self.rect.x = self.x
        self.rect.y = self.y

    def draw(self, screen, screen_x, screen_y):
        if self.is_dead:
            screen.fill((0, 0, 0))
            text = self.font.render("GAME OVER", True, (255, 0, 0))
            text_rect = text.get_rect(center=(screen.get_width()/2, screen.get_height()/2))
            screen.blit(text, text_rect)
            return
        
        # Desenha a barra de vida
        health_width = 100
        health_height = 10
        health_x = 10
        health_y = 10
        
        # Borda da barra de vida
        pygame.draw.rect(screen, (255, 255, 255), 
                        (health_x-2, health_y-2, health_width+4, health_height+4))
        # Fundo vermelho
        pygame.draw.rect(screen, (255, 0, 0), 
                        (health_x, health_y, health_width, health_height))
        # Vida atual em verde
        current_health_width = (self.health / self.max_health) * health_width
        pygame.draw.rect(screen, (0, 255, 0), 
                        (health_x, health_y, current_health_width, health_height))
        
        # Desenha o jogador
        current_image = self.image_right if self.facing_right else self.image_left
        
        # Aplica o efeito de pulo
        offset_y = -self.vertical_velocity if self.is_jumping else 0
        
        # Desenha o personagem na posição da tela
        screen.blit(current_image, (screen_x, screen_y + offset_y))
        
        # Desenha o nome do jogador acima do personagem
        name_text = self.font.render(self.name, True, (255, 255, 255))
        name_rect = name_text.get_rect(center=(screen_x + self.width/2, screen_y - 20 + offset_y))
        # Adiciona um fundo escuro semi-transparente para melhor legibilidade
        bg_rect = name_rect.inflate(20, 10)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 128))
        screen.blit(bg_surface, bg_rect)
        screen.blit(name_text, name_rect)
        
        # Efeito de dano (flash vermelho)
        if self.damage_flash_timer > 0:
            flash_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            flash_surface.fill((255, 0, 0, 128))  # Vermelho semi-transparente
            screen.blit(flash_surface, (screen_x, screen_y + offset_y))
            
        # Efeito de água
        if self.in_water:
            water_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            alpha = int(128 + math.sin(pygame.time.get_ticks() * 0.01) * 64)  # Varia entre 64 e 192
            water_surface.fill((0, 0, 255, alpha))  # Azul com transparência variável
            screen.blit(water_surface, (screen_x, screen_y + offset_y))
            
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