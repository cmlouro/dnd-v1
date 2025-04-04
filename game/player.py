import pygame

class Player:
    def __init__(self, name, character_class):
        self.name = name
        self.character_class = character_class
        self.level = 1
        self.hp = 10  # Vida inicial reduzida para 10
        self.max_hp = 10
        self.strength = 10
        self.dexterity = 10
        self.constitution = 10
        self.intelligence = 10
        self.wisdom = 10
        self.charisma = 10
        
        # Posição inicial do jogador
        self.x = 400
        self.y = 300
        self.speed = 4
        
        # Tamanho da galinha
        self.width = 48
        self.height = 48
        
        # Retângulo de colisão
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Cores da galinha
        self.body_color = (255, 255, 0)  # Amarelo
        self.head_color = (255, 200, 0)  # Amarelo mais escuro
        self.beak_color = (255, 140, 0)  # Laranja
        self.legs_color = (255, 140, 0)  # Laranja
        self.wing_color = (255, 220, 0)  # Amarelo mais claro para asas
        
        # Estado do jogador
        self.in_castle = False
        self.in_water = False
        self.message_timer = 0
        self.damage_timer = 0
        self.is_taking_damage = False
        self.is_dead = False
        self.font = pygame.font.Font(None, 36)
        
        # Timer para piscar quando toma dano
        self.damage_flash_timer = 0

    def update(self):
        if self.is_dead:
            return

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.x += self.speed
        if keys[pygame.K_UP]:
            self.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.y += self.speed
            
        # Atualiza o retângulo de colisão
        self.rect.x = self.x
        self.rect.y = self.y
        
        # Atualiza o timer da mensagem
        if self.message_timer > 0:
            self.message_timer -= 1
            
        # Atualiza o timer de dano na água
        if self.in_water:
            self.damage_timer += 1
            if self.damage_timer >= 60:  # 1 segundo (60 FPS)
                self.take_damage(1)
                self.damage_timer = 0
                
        # Atualiza o timer do flash de dano
        if self.damage_flash_timer > 0:
            self.damage_flash_timer -= 1

    def take_damage(self, amount):
        if not self.is_dead:
            self.hp -= amount
            self.damage_flash_timer = 10  # Pisca vermelho por 10 frames
            if self.hp <= 0:
                self.hp = 0
                self.die()

    def die(self):
        self.is_dead = True

    def enter_castle(self):
        if not self.in_castle:
            self.in_castle = True
            self.message_timer = 120

    def leave_castle(self):
        self.in_castle = False

    def enter_water(self):
        if not self.in_water:
            self.in_water = True
            self.damage_timer = 0
            self.take_damage(1)  # Dano imediato ao entrar na água

    def leave_water(self):
        self.in_water = False
        self.damage_timer = 0

    def draw(self, screen):
        if self.is_dead:
            # Tela preta de Game Over
            screen.fill((0, 0, 0))
            text = self.font.render("GAME OVER", True, (255, 0, 0))
            text_rect = text.get_rect(center=(screen.get_width()/2, screen.get_height()/2))
            screen.blit(text, text_rect)
            return

        # Desenha a galinha com flash vermelho quando toma dano
        if self.damage_flash_timer > 0:
            # Desenha um círculo vermelho de fundo
            pygame.draw.circle(screen, (255, 0, 0), 
                             (int(self.x + self.width/2), int(self.y + self.height/2)), 
                             int(self.width/2 + 5))
        
        # Corpo da galinha
        pygame.draw.ellipse(screen, self.body_color, 
                          (self.x + 8, self.y + 8, self.width - 16, self.height - 16))
        
        # Cabeça da galinha
        pygame.draw.circle(screen, self.head_color, 
                         (int(self.x + self.width - 12), int(self.y + 12)), 12)
        
        # Bico
        pygame.draw.polygon(screen, self.beak_color, [
            (self.x + self.width - 4, self.y + 12),
            (self.x + self.width + 8, self.y + 12),
            (self.x + self.width - 4, self.y + 16)
        ])
        
        # Olho
        pygame.draw.circle(screen, (0, 0, 0), 
                         (int(self.x + self.width - 8), int(self.y + 10)), 2)
        
        # Pernas
        pygame.draw.line(screen, self.legs_color, 
                        (self.x + 16, self.y + self.height - 8),
                        (self.x + 8, self.y + self.height + 4), 3)
        pygame.draw.line(screen, self.legs_color, 
                        (self.x + self.width - 16, self.y + self.height - 8),
                        (self.x + self.width - 8, self.y + self.height + 4), 3)
        
        # Asas
        pygame.draw.ellipse(screen, self.wing_color,
                          (self.x + 4, self.y + 16, 20, 16))
        pygame.draw.ellipse(screen, self.wing_color,
                          (self.x + self.width - 24, self.y + 16, 20, 16))
        
        # Barra de vida
        health_width = 50
        health_height = 5
        health_x = self.x
        health_y = self.y - 10
        
        # Fundo da barra de vida
        pygame.draw.rect(screen, (255, 0, 0), 
                        (health_x, health_y, health_width, health_height))
        
        # Barra de vida atual
        current_health_width = (self.hp / self.max_hp) * health_width
        pygame.draw.rect(screen, (0, 255, 0), 
                        (health_x, health_y, current_health_width, health_height))
        
        # Mostra mensagem quando está no castelo
        if self.in_castle and self.message_timer > 0:
            text = self.font.render("Bem-vindo ao castelo!", True, (255, 255, 255))
            screen.blit(text, (10, 10))
            
        # Mostra mensagem quando está na água
        if self.in_water:
            text = self.font.render("Cuidado com a água!", True, (0, 0, 255))
            screen.blit(text, (10, 50))

        # Desenha as instruções das teclas
        instructions = [
            "Setas: Mover",
            "ESC: Sair",
            f"Vida: {self.hp}/{self.max_hp}"
        ]
        for i, text in enumerate(instructions):
            text_surface = self.font.render(text, True, (255, 255, 255))
            screen.blit(text_surface, (10, 10 + i * 30)) 