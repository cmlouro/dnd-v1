import pygame
import math
import os
import random

class NPC:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.initial_x = x  # Posição inicial X
        self.initial_y = y  # Posição inicial Y
        self.width = 48
        self.height = 48
        self.hitbox_width = 64  # Hitbox maior que a imagem
        self.hitbox_height = 64  # Hitbox maior que a imagem
        self.speed = 2
        self.roam_radius = 100  # Raio máximo de movimento ao redor da posição inicial
        
        # Vida do NPC
        self.health = 2
        self.max_health = 2
        self.health_bar_width = 40
        self.health_bar_height = 5
        self.health_bar_offset = 10  # Distância da barra de vida em relação ao topo do NPC
        
        # Carrega a imagem do NPC
        self.image = pygame.image.load(os.path.join('assets', 'images', 'npc.png')).convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        self.image_left = self.image
        self.image_right = pygame.transform.flip(self.image, True, False)
        
        # Estado do movimento
        self.facing_right = True
        self.movement_timer = 0
        self.movement_duration = random.randint(60, 180)  # 1-3 segundos
        self.pause_timer = 0
        self.pause_duration = random.randint(60, 120)  # 1-2 segundos
        self.moving = False
        self.direction = random.choice(['left', 'right', 'up', 'down'])
        
        # Animação
        self.walk_frame = 0
        self.walk_speed = 0.2
        self.last_update = pygame.time.get_ticks()
        
        # Balão de fala
        self.show_speech = False
        self.speech_font = pygame.font.Font(None, 24)
        self.speech_text = "OLÁ! SOU UM NPC!"
        self.speech_color = (0, 0, 0)
        self.speech_bg_color = (255, 255, 255)
        self.speech_padding = 10
        self.interaction_radius = 100  # Raio de interação em pixels
        
        # Estado de dano
        self.damage_flash_timer = 0
        self.damage_flash_duration = 10  # Frames que o flash de dano dura
        self.is_dead = False

    def take_damage(self, amount=1):
        if not self.is_dead:
            self.health -= amount
            self.damage_flash_timer = self.damage_flash_duration
            if self.health <= 0:
                self.health = 0
                self.is_dead = True

    def update(self, player_x, player_y):
        if self.is_dead:
            return
            
        # Atualiza o timer de flash de dano
        if self.damage_flash_timer > 0:
            self.damage_flash_timer -= 1
            
        # Verifica se o jogador está próximo
        distance = math.sqrt((player_x - self.x) ** 2 + (player_y - self.y) ** 2)
        self.show_speech = distance < self.interaction_radius
        
        # Atualiza a animação
        now = pygame.time.get_ticks()
        if now - self.last_update > 100:
            self.walk_frame = (self.walk_frame + self.walk_speed) % 4
            self.last_update = now
            
        if self.pause_timer > 0:
            self.pause_timer -= 1
            return
            
        if self.movement_timer <= 0:
            # Escolhe uma nova direção e duração
            self.direction = random.choice(['left', 'right', 'up', 'down'])
            self.movement_timer = random.randint(60, 180)
            self.moving = True
        else:
            self.movement_timer -= 1
            
        if self.movement_timer <= 0:
            self.pause_timer = random.randint(60, 120)
            self.moving = False
            
        if self.moving:
            # Calcula a próxima posição
            next_x = self.x
            next_y = self.y
            
            if self.direction == 'left':
                next_x -= self.speed
                self.facing_right = False
            elif self.direction == 'right':
                next_x += self.speed
                self.facing_right = True
            elif self.direction == 'up':
                next_y -= self.speed
            elif self.direction == 'down':
                next_y += self.speed
                
            # Verifica se a próxima posição está dentro do raio permitido
            distance_from_start = math.sqrt(
                (next_x - self.initial_x) ** 2 + 
                (next_y - self.initial_y) ** 2
            )
            
            if distance_from_start <= self.roam_radius:
                self.x = next_x
                self.y = next_y
            else:
                # Se estiver saindo do raio, inverte a direção
                if self.direction == 'left':
                    self.direction = 'right'
                    self.facing_right = True
                elif self.direction == 'right':
                    self.direction = 'left'
                    self.facing_right = False
                elif self.direction == 'up':
                    self.direction = 'down'
                elif self.direction == 'down':
                    self.direction = 'up'

    def draw(self, screen, camera_x, camera_y):
        if self.is_dead:
            return
            
        # Calcula a posição na tela
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # Só desenha se estiver visível na tela
        if (-self.width <= screen_x <= screen.get_width() + self.width and
            -self.height <= screen_y <= screen.get_height() + self.height):
            
            # Escolhe a imagem baseada na direção
            current_image = self.image_right if self.facing_right else self.image_left
            
            # Aplica um pequeno movimento de balanço ao andar
            offset_y = math.sin(self.walk_frame * math.pi) * 2 if self.moving else 0
            
            # Desenha o NPC
            screen.blit(current_image, (screen_x, screen_y + offset_y))
            
            # Desenha a barra de vida
            health_x = screen_x + (self.width - self.health_bar_width) / 2
            health_y = screen_y - self.health_bar_offset
            
            # Fundo da barra de vida
            pygame.draw.rect(screen, (255, 0, 0), 
                           (health_x, health_y, self.health_bar_width, self.health_bar_height))
            
            # Vida atual
            current_health_width = (self.health / self.max_health) * self.health_bar_width
            pygame.draw.rect(screen, (0, 255, 0), 
                           (health_x, health_y, current_health_width, self.health_bar_height))
            
            # Efeito de dano (flash vermelho)
            if self.damage_flash_timer > 0:
                flash_surface = pygame.Surface((self.width, self.height))
                flash_surface.fill((255, 0, 0))
                flash_surface.set_alpha(128)  # Semi-transparente
                screen.blit(flash_surface, (screen_x, screen_y + offset_y))
            
            # Desenha o balão de fala se necessário
            if self.show_speech:
                # Renderiza o texto
                text_surface = self.speech_font.render(self.speech_text, True, self.speech_color)
                text_rect = text_surface.get_rect()
                
                # Cria o balão de fala
                balloon_rect = pygame.Rect(
                    screen_x - text_rect.width/2 + self.width/2 - self.speech_padding,
                    screen_y - text_rect.height - 30 - self.speech_padding,
                    text_rect.width + 2 * self.speech_padding,
                    text_rect.height + 2 * self.speech_padding
                )
                
                # Desenha o balão de fala
                pygame.draw.rect(screen, self.speech_bg_color, balloon_rect, border_radius=10)
                pygame.draw.rect(screen, self.speech_color, balloon_rect, 2, border_radius=10)
                
                # Desenha o triângulo do balão
                triangle_points = [
                    (screen_x + self.width/2, balloon_rect.bottom),
                    (screen_x + self.width/2 - 10, balloon_rect.bottom - 10),
                    (screen_x + self.width/2 + 10, balloon_rect.bottom - 10)
                ]
                pygame.draw.polygon(screen, self.speech_bg_color, triangle_points)
                pygame.draw.polygon(screen, self.speech_color, triangle_points, 2)
                
                # Desenha o texto
                screen.blit(text_surface, (
                    screen_x - text_rect.width/2 + self.width/2,
                    screen_y - text_rect.height - 30
                )) 