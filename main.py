import pygame
import sys
import random
import math
import os
from game.player import Player
from game.game_state import GameState
from game.map import GameMap
from game.npc import NPC
from game.items import ITEMS, ABILITIES
from game.piranha import Piranha
from game.objectives import ObjectiveManager

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Andre Pereira's Adventure")
        self.clock = pygame.time.Clock()
        
        # Componentes do jogo
        self.game_state = GameState()
        self.game_map = GameMap()
        self.player = None  # Será criado quando o jogo começar
        self.piranhas = []
        self.npcs = []
        
        # Inicializa o gerenciador de objetivos
        self.objective_manager = ObjectiveManager()
        
        # Gera algumas piranhas iniciais
        self.generate_piranhas(5)  # Começa com 5 piranhas
        
        # Gera alguns NPCs iniciais
        self.generate_npcs(3)  # Começa com 3 NPCs
        
        # Gera alguns itens no mapa
        self.items = []
        self.generate_items(5)  # Começa com 5 itens espalhados

    def generate_piranhas(self, count):
        for _ in range(count):
            # Encontra uma posição de água para spawnar a piranha
            water_found = False
            attempts = 0
            while not water_found and attempts < 100:
                x = random.randint(-500, 500)
                y = random.randint(-500, 500)
                if self.game_map.get_tile_at(x, y) == 'water':
                    self.piranhas.append(Piranha(x, y, self.game_map))
                    water_found = True
                attempts += 1

    def generate_npcs(self, count):
        for _ in range(count):
            # Gera NPCs em um raio de 200 pixels do centro
            x = random.randint(-200, 200)
            y = random.randint(-200, 200)
            if self.game_map.get_tile_at(x, y) != 'water':  # NPCs não spawnam na água
                self.npcs.append(NPC(x, y))

    def generate_items(self, count):
        for _ in range(count):
            # Gera itens em um raio de 200 pixels do centro
            x = random.randint(-200, 200)
            y = random.randint(-200, 200)
            if self.game_map.get_tile_at(x, y) != 'water':  # Itens não spawnam na água
                potion = ITEMS['potion']()
                potion.x = x
                potion.y = y
                self.items.append(potion)

    def start_new_game(self):
        # Cria o jogador no centro da tela
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        self.player = Player(screen_width // 2, screen_height // 2)
        self.game_state.current_state = GameState.PLAYING
        
        # Define o objetivo inicial
        self.objective_manager.set_objective("Eliminar NPCs", 2)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.KEYDOWN:
                if self.game_state.current_state == GameState.MENU:
                    if event.key == pygame.K_RETURN:
                        self.start_new_game()
                        
                elif self.game_state.current_state == GameState.PLAYING:
                    if event.key == pygame.K_ESCAPE:
                        self.game_state.toggle_pause()
                    elif event.key == pygame.K_i:
                        self.game_state.toggle_inventory()
                    elif event.key == pygame.K_SPACE:
                        if not self.player.is_jumping:
                            self.player.vertical_velocity = -10
                            self.player.is_jumping = True
                    elif event.key == pygame.K_q:  # Usar habilidade
                        if self.player:
                            self.player.use_ability(self)
                    elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:  # Usar item
                        if self.player:
                            item_index = event.key - pygame.K_1
                            self.player.use_item(item_index)
                            
                elif self.game_state.current_state == GameState.PAUSED:
                    if event.key == pygame.K_ESCAPE:
                        self.game_state.toggle_pause()
                        
                elif self.game_state.current_state == GameState.INVENTORY:
                    if event.key == pygame.K_i or event.key == pygame.K_ESCAPE:
                        self.game_state.toggle_inventory()
        
        # Movimento contínuo
        if self.game_state.current_state == GameState.PLAYING and self.player:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.player.x -= self.player.speed
                self.player.facing_right = False
            if keys[pygame.K_RIGHT]:
                self.player.x += self.player.speed
                self.player.facing_right = True
            if keys[pygame.K_UP]:
                self.player.y -= self.player.speed
            if keys[pygame.K_DOWN]:
                self.player.y += self.player.speed
                
        return True
        
    def update(self):
        if self.game_state.current_state == GameState.PLAYING:
            # Atualiza o jogador
            self.player.update()
            
            # Atualiza as habilidades do jogador
            for ability in self.player.abilities.values():
                ability.update(self)
            
            # Atualiza o mapa baseado na posição do jogador
            self.game_map.update_chunks(self.player.x, self.player.y)
            
            # Verifica colisões
            self.check_castle_collision()
            self.check_water_collision()
            
            # Atualiza os NPCs e verifica se algum morreu
            npcs_to_remove = []
            for npc in self.npcs:
                npc.update(self.player.x, self.player.y)
                if npc.is_dead:
                    npcs_to_remove.append(npc)
                    self.objective_manager.on_npc_killed()
            
            # Remove NPCs mortos
            for npc in npcs_to_remove:
                if npc in self.npcs:
                    self.npcs.remove(npc)
            
            # Atualiza as piranhas
            self.update_piranhas()
            
            # Verifica coleta de itens
            self.check_item_collection()
            
            # Atualiza a câmera
            self.camera_x = self.player.x - (self.screen.get_width() // 2)
            self.camera_y = self.player.y - (self.screen.get_height() // 2)
            
            # Atualiza os objetivos
            self.objective_manager.update()
            
    def draw(self):
        if self.game_state.current_state == GameState.MENU:
            self.game_state.draw_menu(self.screen)
            
        elif self.game_state.current_state == GameState.PLAYING:
            # Limpa a tela
            self.screen.fill((135, 206, 235))  # Cor do céu
            
            # Desenha o mapa
            self.game_map.draw(self.screen, self.camera_x, self.camera_y)
            
            # Desenha os itens
            for item in self.items:
                screen_x = item.x - self.camera_x
                screen_y = item.y - self.camera_y
                if (-32 <= screen_x <= self.screen.get_width() + 32 and
                    -32 <= screen_y <= self.screen.get_height() + 32):
                    self.screen.blit(item.image, (screen_x - 16, screen_y - 16))
            
            # Desenha os NPCs
            for npc in self.npcs:
                npc.draw(self.screen, self.camera_x, self.camera_y)
            
            # Desenha as piranhas
            for piranha in self.piranhas:
                piranha.draw(self.screen, self.camera_x, self.camera_y)
            
            # Desenha as habilidades
            for ability in self.player.abilities.values():
                ability.draw(self.screen, self.camera_x, self.camera_y)
            
            # Desenha o jogador
            self.player.draw(self.screen, self.camera_x, self.camera_y)
            
            # Desenha a UI
            self.draw_ui()
            
            # Desenha os objetivos
            self.objective_manager.draw(self.screen)
            
        if self.game_state.current_state == GameState.PAUSED:
            self.game_state.draw_pause(self.screen)
            
        if self.game_state.current_state == GameState.INVENTORY:
            self.game_state.draw_inventory(self.screen)
            
        pygame.display.flip()
        
    def draw_ui(self):
        if not self.player:
            return
            
        # Barra de vida
        health_width = 200
        health_height = 20
        health_x = 10
        health_y = 40  # Movido para baixo
        
        pygame.draw.rect(self.screen, (255, 0, 0), 
                        (health_x, health_y, health_width, health_height))
        current_health_width = (self.player.health / self.player.max_health) * health_width
        pygame.draw.rect(self.screen, (0, 255, 0), 
                        (health_x, health_y, current_health_width, health_height))
                        
        # Barra de mana
        mana_y = health_y + health_height + 5
        pygame.draw.rect(self.screen, (0, 0, 100), 
                        (health_x, mana_y, health_width, health_height))
        current_mana_width = (self.player.mana / self.player.max_mana) * health_width
        pygame.draw.rect(self.screen, (0, 0, 255), 
                        (health_x, mana_y, current_mana_width, health_height))
                        
        # Nível e experiência
        level_text = f"Nível {self.player.level}"
        exp_text = f"EXP: {self.player.experience}/{self.player.exp_to_next_level}"
        level_surface = self.player.font.render(level_text, True, (255, 255, 255))
        exp_surface = self.player.font.render(exp_text, True, (255, 255, 255))
        self.screen.blit(level_surface, (10, mana_y + health_height + 5))
        self.screen.blit(exp_surface, (10, mana_y + health_height + 30))
        
        # Habilidade selecionada
        if self.player.selected_ability:
            ability_text = f"Q: {self.player.selected_ability.name}"
            ability_surface = self.player.font.render(ability_text, True, (255, 255, 255))
            self.screen.blit(ability_surface, (10, mana_y + health_height + 55))
            
        # Instruções das teclas (movidas para o canto superior direito)
        instructions = [
            "Setas: Mover",
            "Espaço: Pular",
            "Q: Bola de Fogo",
            "I: Abrir/Fechar Inventário",
            "1-4: Usar Item do Inventário",
            "ESC: Pausar"
        ]
        for i, text in enumerate(instructions):
            text_surface = self.player.font.render(text, True, (255, 255, 255))
            self.screen.blit(text_surface, (self.screen.get_width() - text_surface.get_width() - 10, 10 + i * 25))
        
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

    def update_piranhas(self):
        for piranha in self.piranhas:
            piranha.update()
            
            # Verifica colisão com o jogador
            if self.player and self.player.in_water:
                dx = piranha.x - self.player.x
                dy = piranha.y - self.player.y
                distance = math.sqrt(dx * dx + dy * dy)
                
                if distance < 30:  # Distância para causar dano
                    self.player.take_damage()
                    
        # Remove piranhas que saíram da água
        self.piranhas = [p for p in self.piranhas if self.game_map.get_tile_at(p.x, p.y) == 'water']
        
        # Mantém um número mínimo de piranhas
        if len(self.piranhas) < 5:
            self.generate_piranhas(1)

    def check_item_collection(self):
        # Lista para armazenar itens que devem ser removidos
        items_to_remove = []
        
        for item in self.items:
            # Calcula a distância entre o jogador e o item
            dx = self.player.x - item.x
            dy = self.player.y - item.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            # Se o jogador está próximo o suficiente, coleta o item
            if distance < 40:  # Raio de coleta de 40 pixels
                # Adiciona o item ao inventário do game_state
                self.game_state.inventory.append(item)
                items_to_remove.append(item)
                
                # Efeito sonoro ou visual de coleta (opcional)
                # TODO: Adicionar efeito sonoro
        
        # Remove os itens coletados da lista de itens no mapa
        for item in items_to_remove:
            self.items.remove(item)
            
        # Gera novos itens se necessário
        if len(self.items) < 5:
            self.generate_items(1)

    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run() 