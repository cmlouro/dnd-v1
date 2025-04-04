import pygame
import sys
import random
import math
import os
from game.player import Player
from game.game_state import GameState
from game.map import GameMap
from game.npc import NPC

class Piranha:
    def __init__(self, x, y, game_map):
        self.x = x
        self.y = y
        self.width = 32
        self.height = 32
        self.speed = 2
        self.direction = random.uniform(0, 2 * math.pi)  # Direção aleatória
        self.game_map = game_map  # Referência para o mapa
        
        # Carrega e ajusta a imagem da piranha
        self.image = pygame.image.load(os.path.join('assets', 'images', 'piranha-fish.png')).convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        self.original_image = self.image
            
    def is_in_water(self, x, y):
        # Verifica se a posição está em água
        return self.game_map.get_tile_at(x, y) == 'water'
            
    def update(self):
        # Calcula a próxima posição
        next_x = self.x + self.speed * math.cos(self.direction)
        next_y = self.y + self.speed * math.sin(self.direction)
        
        # Só move se a próxima posição estiver na água
        if self.is_in_water(next_x, next_y):
            self.x = next_x
            self.y = next_y
        else:
            # Se vai sair da água, muda a direção
            self.direction = random.uniform(0, 2 * math.pi)
        
        # Muda de direção aleatoriamente com menos frequência
        if random.random() < 0.01:  # 1% de chance por frame
            self.direction = random.uniform(0, 2 * math.pi)
            
    def draw(self, screen, camera_x, camera_y):
        # Calcula a posição na tela
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # Só desenha se estiver visível na tela
        if (-self.width <= screen_x <= screen.get_width() + self.width and
            -self.height <= screen_y <= screen.get_height() + self.height):
            # Rotaciona a imagem na direção do movimento
            angle = math.degrees(self.direction)
            rotated_image = pygame.transform.rotate(self.original_image, -angle - 90)
            screen.blit(rotated_image, (
                screen_x - rotated_image.get_width()/2,
                screen_y - rotated_image.get_height()/2
            ))

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Dungeons and Dragons - A Aventura Mágica")
        self.clock = pygame.time.Clock()
        self.game_state = GameState()
        self.game_map = GameMap()
        self.player = Player("Andre Pereira", "Feiticeiro")
        
        # Lista de NPCs e Piranhas
        self.npcs = []
        self.piranhas = []
        self.spawn_npcs(5)  # Cria 5 NPCs
        self.spawn_piranhas()  # Cria as piranhas
        
        # Câmera
        self.camera_x = 0
        self.camera_y = 0
        
        # Debug
        self.debug_mode = True

    def update_camera(self):
        # A câmera segue o jogador
        target_x = self.player.x - self.screen.get_width() // 2
        target_y = self.player.y - self.screen.get_height() // 2
        
        # Suavização do movimento da câmera
        self.camera_x += (target_x - self.camera_x) * 0.1
        self.camera_y += (target_y - self.camera_y) * 0.1

    def spawn_npcs(self, num_npcs):
        # Cria NPCs em posições fixas do mapa
        npc_positions = [
            (200, 200),   # NPC na vila
            (500, 100),   # NPC perto do castelo
            (700, 400),   # NPC na floresta
            (300, 500),   # NPC perto do lago
            (100, 600)    # NPC no caminho
        ]
        
        for pos in npc_positions[:num_npcs]:
            self.npcs.append(NPC(pos[0], pos[1]))

    def find_water_positions(self, num_positions):
        # Encontra posições válidas de água no mapa
        water_positions = []
        
        # Procura em uma área grande ao redor do jogador
        search_radius = 1000
        step = 64  # Tamanho do tile
        
        for x in range(int(self.player.x - search_radius), int(self.player.x + search_radius), step):
            for y in range(int(self.player.y - search_radius), int(self.player.y + search_radius), step):
                if self.game_map.get_tile_at(x, y) == 'water':
                    water_positions.append((x, y))
                    if len(water_positions) >= num_positions * 3:  # Coleta mais posições para ter opções
                        break
            if len(water_positions) >= num_positions * 3:
                break
                
        # Embaralha e retorna apenas o número necessário
        random.shuffle(water_positions)
        return water_positions[:num_positions]

    def spawn_piranhas(self):
        # Encontra posições de água válidas
        water_positions = self.find_water_positions(5)
        
        # Cria piranhas nas posições de água
        for pos in water_positions:
            self.piranhas.append(Piranha(pos[0], pos[1], self.game_map))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_d:
                    self.debug_mode = not self.debug_mode
        return True

    def check_castle_collision(self):
        # Verifica vários pontos ao redor do jogador para melhor detecção
        points_to_check = [
            (self.player.x, self.player.y),  # Centro
            (self.player.x - self.player.width/4, self.player.y - self.player.height/4),  # Superior esquerdo
            (self.player.x + self.player.width/4, self.player.y - self.player.height/4),  # Superior direito
            (self.player.x - self.player.width/4, self.player.y + self.player.height/4),  # Inferior esquerdo
            (self.player.x + self.player.width/4, self.player.y + self.player.height/4)   # Inferior direito
        ]
        
        castle_count = 0
        for x, y in points_to_check:
            tile_type = self.game_map.get_tile_at(x, y)
            if tile_type == 'castle':
                castle_count += 1
        
        # Só considera dentro do castelo se a maioria dos pontos estiver em tiles do tipo castle
        if castle_count >= 3:
            self.player.enter_castle()
        else:
            self.player.leave_castle()

    def check_water_collision(self):
        # Verifica vários pontos ao redor do jogador para melhor detecção
        points_to_check = [
            (self.player.x, self.player.y),  # Centro
            (self.player.x - self.player.width/3, self.player.y - self.player.height/3),  # Superior esquerdo
            (self.player.x + self.player.width/3, self.player.y - self.player.height/3),  # Superior direito
            (self.player.x - self.player.width/3, self.player.y + self.player.height/3),  # Inferior esquerdo
            (self.player.x + self.player.width/3, self.player.y + self.player.height/3)   # Inferior direito
        ]
        
        water_tiles = 0
        total_tiles = len(points_to_check)
        
        for x, y in points_to_check:
            tile_type = self.game_map.get_tile_at(x, y)
            if tile_type == 'water':
                water_tiles += 1
        
        # Só considera na água se mais de 50% dos pontos estiverem em água
        if water_tiles > total_tiles / 2:
            self.player.enter_water()
        else:
            self.player.leave_water()

    def check_collision(self, obj1, obj2):
        # Verifica colisão entre dois objetos usando seus retângulos
        rect1 = pygame.Rect(obj1.x - obj1.width/2, obj1.y - obj1.height/2, 
                          obj1.width, obj1.height)
        rect2 = pygame.Rect(obj2.x - obj2.width/2, obj2.y - obj2.height/2, 
                          obj2.width, obj2.height)
        return rect1.colliderect(rect2)

    def is_in_water(self, x, y):
        # Verifica se uma posição específica está na água
        return self.game_map.get_tile_at(x, y) == 'water'

    def update_piranhas(self):
        for piranha in self.piranhas[:]:  # Usar uma cópia da lista para evitar problemas ao remover
            # Verifica se a piranha está na água
            if not self.is_in_water(piranha.x, piranha.y):
                # Procura água próxima
                found_water = False
                search_radius = 50  # Reduzido o raio de busca
                
                for dx in range(-search_radius, search_radius + 1, 10):
                    for dy in range(-search_radius, search_radius + 1, 10):
                        new_x = piranha.x + dx
                        new_y = piranha.y + dy
                        if self.is_in_water(new_x, new_y):
                            piranha.x = new_x
                            piranha.y = new_y
                            found_water = True
                            break
                    if found_water:
                        break
                
                # Se não encontrar água próxima, remove a piranha
                if not found_water:
                    self.piranhas.remove(piranha)
                    continue
            
            # Atualiza o movimento da piranha
            old_x, old_y = piranha.x, piranha.y
            piranha.update()
            
            # Se o novo movimento levaria a piranha para fora da água, reverte o movimento
            if not self.is_in_water(piranha.x, piranha.y):
                piranha.x = old_x
                piranha.y = old_y
                piranha.change_direction()  # Muda a direção quando bate na borda da água
            
            # Só causa dano se o jogador E a piranha estiverem na água
            if self.player.in_water and self.is_in_water(piranha.x, piranha.y) and self.check_collision(piranha, self.player):
                self.player.take_damage()

    def update(self):
        if self.player and not self.player.is_dead:
            self.player.update()
            self.check_castle_collision()
            self.check_water_collision()
            
            # Atualiza a câmera
            self.update_camera()
            
            # Atualiza o mapa
            self.game_map.update_chunks(self.player.x, self.player.y)
            
            # Atualiza os NPCs e as Piranhas
            for npc in self.npcs:
                npc.update(self.player.x, self.player.y)
            
            # Atualiza as piranhas e verifica colisões
            self.update_piranhas()

    def draw(self):
        # Desenha o mapa
        self.game_map.draw(self.screen, int(self.camera_x), int(self.camera_y))
        
        # Desenha os NPCs
        for npc in self.npcs:
            npc.draw(self.screen, int(self.camera_x), int(self.camera_y))
            
        # Desenha as piranhas
        for piranha in self.piranhas:
            piranha.draw(self.screen, int(self.camera_x), int(self.camera_y))
            
        # Desenha o jogador
        if self.player:
            screen_x = self.player.x - self.camera_x
            screen_y = self.player.y - self.camera_y
            self.player.draw(self.screen, screen_x, screen_y)
            
        # Desenha informações de debug
        if self.debug_mode:
            tile_type = self.game_map.get_tile_at(self.player.x, self.player.y)
            debug_text = f"Tile: ({int(self.player.x/64)}, {int(self.player.y/64)}) - Tipo: {tile_type}"
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