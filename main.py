import pygame
import sys
import random
import math
from game.player import Player
from game.game_state import GameState
from game.map import GameMap

class Piranha:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 16
        self.height = 16
        self.speed = 2
        self.direction = random.uniform(0, 2 * math.pi)  # Direção aleatória
        
    def update(self):
        # Movimento circular/aleatório
        self.x += self.speed * math.cos(self.direction)
        self.y += self.speed * math.sin(self.direction)
        # Muda de direção aleatoriamente
        if random.random() < 0.02:  # 2% de chance por frame
            self.direction = random.uniform(0, 2 * math.pi)
            
    def draw(self, screen):
        # Desenha a piranha como um triângulo vermelho
        points = [
            (self.x, self.y - self.height/2),
            (self.x + self.width, self.y),
            (self.x, self.y + self.height/2)
        ]
        pygame.draw.polygon(screen, (255, 0, 0), points)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Dungeons and Dragons - A Galinha Aventureira")
        self.clock = pygame.time.Clock()
        self.game_state = GameState()
        self.game_map = GameMap()
        # Criar um personagem inicial (galinha)
        self.player = Player("Galinha", "Aventureira")
        # Lista de piranhas
        self.piranhas = []
        self.spawn_piranhas()
        # Debug
        self.debug_mode = True

    def spawn_piranhas(self):
        # Encontra todos os tiles de água
        water_tiles = []
        for y in range(self.game_map.height):
            for x in range(self.game_map.width):
                if self.game_map.map_data[y][x] == 'water':
                    water_tiles.append((x, y))
        
        # Cria 5 piranhas em posições aleatórias na água
        for _ in range(5):
            if water_tiles:
                tile_x, tile_y = random.choice(water_tiles)
                x = tile_x * self.game_map.tile_size + self.game_map.tile_size/2
                y = tile_y * self.game_map.tile_size + self.game_map.tile_size/2
                self.piranhas.append(Piranha(x, y))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                # Tecla D para ativar/desativar modo debug
                if event.key == pygame.K_d:
                    self.debug_mode = not self.debug_mode
        return True

    def check_castle_collision(self):
        # Converte a posição do jogador para coordenadas do mapa
        tile_x = self.player.x // self.game_map.tile_size
        tile_y = self.player.y // self.game_map.tile_size
        
        # Verifica se as coordenadas estão dentro dos limites do mapa
        if (0 <= tile_x < self.game_map.width and 
            0 <= tile_y < self.game_map.height):
            # Verifica se o tile atual é um castelo
            if self.game_map.map_data[int(tile_y)][int(tile_x)] == 'castle':
                self.player.enter_castle()
            else:
                self.player.leave_castle()

    def check_water_collision(self):
        # Converte a posição do jogador para coordenadas do mapa
        tile_x = self.player.x // self.game_map.tile_size
        tile_y = self.player.y // self.game_map.tile_size
        
        # Verifica se as coordenadas estão dentro dos limites do mapa
        if (0 <= tile_x < self.game_map.width and 
            0 <= tile_y < self.game_map.height):
            # Verifica se o tile atual é água
            if self.game_map.map_data[int(tile_y)][int(tile_x)] == 'water':
                self.player.enter_water()
                # Aplica dano imediatamente para teste
                if not self.player.in_water:
                    self.player.take_damage(1)
            else:
                self.player.leave_water()

    def update_piranhas(self):
        for piranha in self.piranhas:
            piranha.update()
            # Mantém as piranhas dentro da água
            tile_x = piranha.x // self.game_map.tile_size
            tile_y = piranha.y // self.game_map.tile_size
            if (tile_x < 0 or tile_x >= self.game_map.width or
                tile_y < 0 or tile_y >= self.game_map.height or
                self.game_map.map_data[int(tile_y)][int(tile_x)] != 'water'):
                # Se a piranha sair da água, inverte sua direção
                piranha.direction += math.pi  # 180 graus

    def update(self):
        if self.player and not self.player.is_dead:
            self.player.update()
            self.check_castle_collision()
            self.check_water_collision()
            self.update_piranhas()

    def draw(self):
        # Desenhar o mapa primeiro
        self.game_map.draw(self.screen)
        # Desenhar as piranhas
        for piranha in self.piranhas:
            piranha.draw(self.screen)
        # Depois desenhar o jogador
        if self.player:
            self.player.draw(self.screen)
            
        # Desenhar informações de debug
        if self.debug_mode:
            tile_x = self.player.x // self.game_map.tile_size
            tile_y = self.player.y // self.game_map.tile_size
            if (0 <= tile_x < self.game_map.width and 
                0 <= tile_y < self.game_map.height):
                tile_type = self.game_map.map_data[int(tile_y)][int(tile_x)]
                debug_text = f"Tile: ({tile_x}, {tile_y}) - Tipo: {tile_type}"
                debug_surface = self.player.font.render(debug_text, True, (255, 255, 255))
                self.screen.blit(debug_surface, (10, 100))
                
                if self.player.in_water:
                    water_text = "NA ÁGUA - TOMANDO DANO!"
                    water_surface = self.player.font.render(water_text, True, (255, 0, 0))
                    self.screen.blit(water_surface, (10, 130))
        
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run() 