import pygame
import math

class Item:
    def __init__(self, name, description, image_name=None):
        self.name = name
        self.description = description
        
        # Cria uma imagem padrão para o item
        self.image = pygame.Surface((32, 32))
        
        if image_name:
            try:
                self.image = pygame.image.load(f'assets/images/items/{image_name}')
            except:
                # Se não conseguir carregar a imagem, cria uma imagem colorida
                if "Poção" in name:
                    self.image.fill((255, 0, 0))  # Vermelho para poções
                else:
                    self.image.fill((100, 100, 100))  # Cinza para outros itens
                
                # Adiciona uma borda
                pygame.draw.rect(self.image, (200, 200, 200), self.image.get_rect(), 2)

class Potion(Item):
    def __init__(self, healing_amount):
        super().__init__("Poção de Vida", "Recupera vida quando usado", "potion.png")
        self.healing_amount = healing_amount
        
    def use(self, player):
        player.health = min(player.health + self.healing_amount, player.max_health)
        return True  # Item consumido

class Ability:
    def __init__(self, name, description, mana_cost, cooldown):
        self.name = name
        self.description = description
        self.mana_cost = mana_cost
        self.cooldown = cooldown
        self.last_used = 0
        
    def can_use(self, player):
        current_time = pygame.time.get_ticks()
        return (current_time - self.last_used) >= self.cooldown * 1000

class Fireball:
    def __init__(self, x, y, direction, speed=10):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
        self.speed = speed
        self.direction = direction  # True para direita, False para esquerda
        self.distance_traveled = 0
        self.max_distance = 300  # Distância máxima que a bola de fogo pode viajar
        
    def update(self):
        # Move a bola de fogo na direção correta
        if self.direction:
            self.x += self.speed  # Move para a direita
        else:
            self.x -= self.speed  # Move para a esquerda
            
        # Atualiza a distância percorrida
        self.distance_traveled += self.speed
        
        # Retorna False se a bola de fogo atingiu sua distância máxima
        return self.distance_traveled < self.max_distance

class FireballAbility(Ability):
    def __init__(self):
        super().__init__(
            "Bola de Fogo",
            "Lança uma bola de fogo que causa dano aos inimigos",
            10,  # Custo de mana
            1    # Cooldown em segundos
        )
        self.fireballs = []
        self.width = 20  # Largura para verificação de visibilidade
        self.height = 20  # Altura para verificação de visibilidade
        self.explosion_duration = 30  # Duração da explosão em frames
        self.explosions = []  # Lista para armazenar explosões ativas
    
    def use(self, player, game):
        if not self.can_use(player) or player.mana < self.mana_cost:
            return False
            
        # Cria uma nova bola de fogo na posição do jogador
        fireball = Fireball(
            player.x + (30 if player.facing_right else -30),  # Offset para a bola de fogo começar na frente do jogador
            player.y,
            player.facing_right,
            speed=15  # Aumenta a velocidade da bola de fogo
        )
        self.fireballs.append(fireball)
        
        # Consome mana
        player.mana -= self.mana_cost
        self.last_used = pygame.time.get_ticks()
        return True
        
    def update(self, game=None):
        # Atualiza todas as bolas de fogo ativas e remove as que atingiram a distância máxima
        fireballs_to_remove = []
        for fireball in self.fireballs:
            if not fireball.update():
                fireballs_to_remove.append(fireball)
                continue
                
            # Verifica colisão com NPCs se o game foi fornecido
            if game:
                for npc in game.npcs:
                    if self.check_collision(fireball, npc):
                        # Cria uma explosão na posição da colisão
                        self.explosions.append({
                            'x': fireball.x,
                            'y': fireball.y,
                            'timer': self.explosion_duration,
                            'radius': 0,
                            'max_radius': 50
                        })
                        fireballs_to_remove.append(fireball)
                        break
        
        # Remove as bolas de fogo que devem ser removidas
        for fireball in fireballs_to_remove:
            if fireball in self.fireballs:
                self.fireballs.remove(fireball)
        
        # Atualiza as explosões
        explosions_to_remove = []
        for explosion in self.explosions:
            explosion['timer'] -= 1
            explosion['radius'] = int((1 - explosion['timer'] / self.explosion_duration) * explosion['max_radius'])
            if explosion['timer'] <= 0:
                explosions_to_remove.append(explosion)
        
        # Remove explosões que terminaram
        for explosion in explosions_to_remove:
            self.explosions.remove(explosion)
        
    def check_collision(self, fireball, npc):
        # Verifica colisão entre a bola de fogo e o NPC usando a hitbox maior do NPC
        dx = fireball.x - npc.x
        dy = fireball.y - npc.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Usa a hitbox maior do NPC para a colisão
        collision_distance = (fireball.width/2 + npc.hitbox_width/2)
        
        if distance < collision_distance:
            # Aplica dano ao NPC
            npc.take_damage()
            return True
        return False
        
    def draw(self, screen, camera_x, camera_y):
        # Desenha as bolas de fogo
        for fireball in self.fireballs:
            screen_x = fireball.x - camera_x
            screen_y = fireball.y - camera_y
            
            # Só desenha se estiver visível na tela
            if (-fireball.width <= screen_x <= screen.get_width() + fireball.width and
                -fireball.height <= screen_y <= screen.get_height() + fireball.height):
                # Desenha a bola de fogo como um círculo vermelho com efeito de brilho
                pygame.draw.circle(screen, (255, 200, 0), (int(screen_x), int(screen_y)), 10)  # Núcleo amarelo
                pygame.draw.circle(screen, (255, 100, 0), (int(screen_x), int(screen_y)), 8)  # Centro laranja
                pygame.draw.circle(screen, (255, 0, 0), (int(screen_x), int(screen_y)), 6)  # Centro vermelho
        
        # Desenha as explosões
        for explosion in self.explosions:
            screen_x = explosion['x'] - camera_x
            screen_y = explosion['y'] - camera_y
            
            # Só desenha se estiver visível na tela
            if (-explosion['max_radius'] <= screen_x <= screen.get_width() + explosion['max_radius'] and
                -explosion['max_radius'] <= screen_y <= screen.get_height() + explosion['max_radius']):
                # Desenha a explosão como círculos concêntricos
                alpha = int((explosion['timer'] / self.explosion_duration) * 255)
                for radius in range(explosion['radius'], 0, -5):
                    color = (255, 200 - radius, 0, alpha)
                    surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                    pygame.draw.circle(surface, color, (radius, radius), radius)
                    screen.blit(surface, (int(screen_x - radius), int(screen_y - radius)))

class TeleportAbility(Ability):
    def __init__(self):
        super().__init__(
            "Teleporte",
            "Teleporta o jogador para uma curta distância",
            30,  # Custo de mana
            10   # Cooldown em segundos
        )
        
    def use(self, player, game):
        if not self.can_use(player):
            return False
            
        # Teleporta o jogador na direção que está olhando
        distance = 100  # Distância do teleporte em pixels
        if player.facing_right:
            player.x += distance
        else:
            player.x -= distance
            
        self.last_used = pygame.time.get_ticks()
        return True
        
    def update(self, game=None):
        # O teleporte não precisa de atualização contínua
        pass
        
    def draw(self, screen, camera_x, camera_y):
        # O teleporte não tem representação visual contínua
        pass

# Lista de todos os itens disponíveis no jogo
ITEMS = {
    'potion': lambda: Potion(3),  # Recupera 3 de vida
}

# Lista de todas as habilidades disponíveis no jogo
ABILITIES = {
    'fireball': FireballAbility,
    'teleport': TeleportAbility,
} 