import pygame

class GameState:
    MENU = "MENU"
    PLAYING = "PLAYING"
    PAUSED = "PAUSED"
    INVENTORY = "INVENTORY"
    
    def __init__(self):
        self.current_state = self.MENU
        self.score = 0
        self.discovered_tiles = set()  # Para pontuação de exploração
        self.unlocked_abilities = set()
        self.inventory = []
        self.current_quest = None
        self.completed_quests = set()
        self.font = pygame.font.Font(None, 36)
        
        # Configurações
        self.sound_enabled = True
        self.music_volume = 0.7
        self.sfx_volume = 1.0
        
    def toggle_pause(self):
        if self.current_state == self.PLAYING:
            self.current_state = self.PAUSED
        elif self.current_state == self.PAUSED:
            self.current_state = self.PLAYING
            
    def toggle_inventory(self):
        if self.current_state == self.PLAYING:
            self.current_state = self.INVENTORY
        elif self.current_state == self.INVENTORY:
            self.current_state = self.PLAYING
    
    def draw_menu(self, screen):
        screen.fill((0, 0, 0))
        title = self.font.render("Andre Pereira's Adventure", True, (255, 255, 255))
        start = self.font.render("Pressione ENTER para começar", True, (255, 255, 255))
        controls = self.font.render("Setas: Mover    Espaço: Pular    I: Inventário    ESC: Pausar", True, (255, 255, 255))
        
        screen.blit(title, (screen.get_width()/2 - title.get_width()/2, screen.get_height()/3))
        screen.blit(start, (screen.get_width()/2 - start.get_width()/2, screen.get_height()/2))
        screen.blit(controls, (screen.get_width()/2 - controls.get_width()/2, screen.get_height()*2/3))
    
    def draw_pause(self, screen):
        # Superfície semi-transparente
        overlay = pygame.Surface((screen.get_width(), screen.get_height()))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        screen.blit(overlay, (0, 0))
        
        pause_text = self.font.render("JOGO PAUSADO", True, (255, 255, 255))
        resume_text = self.font.render("Pressione ESC para continuar", True, (255, 255, 255))
        
        screen.blit(pause_text, (screen.get_width()/2 - pause_text.get_width()/2, screen.get_height()/2 - 50))
        screen.blit(resume_text, (screen.get_width()/2 - resume_text.get_width()/2, screen.get_height()/2 + 50))
    
    def draw_inventory(self, screen):
        # Superfície semi-transparente
        overlay = pygame.Surface((screen.get_width(), screen.get_height()))
        overlay.fill((0, 0, 50))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))
        
        title = self.font.render("Inventário", True, (255, 255, 255))
        screen.blit(title, (screen.get_width()/2 - title.get_width()/2, 50))
        
        if not self.inventory:
            empty_text = self.font.render("Inventário vazio", True, (200, 200, 200))
            screen.blit(empty_text, (screen.get_width()/2 - empty_text.get_width()/2, screen.get_height()/2))
        else:
            # Desenha os itens do inventário em uma grade
            item_size = 64
            padding = 20
            items_per_row = 5
            start_x = (screen.get_width() - (items_per_row * (item_size + padding))) // 2
            start_y = 150
            
            for i, item in enumerate(self.inventory):
                row = i // items_per_row
                col = i % items_per_row
                x = start_x + col * (item_size + padding)
                y = start_y + row * (item_size + padding)
                
                # Desenha o fundo do slot
                pygame.draw.rect(screen, (50, 50, 50), (x, y, item_size, item_size))
                pygame.draw.rect(screen, (100, 100, 100), (x, y, item_size, item_size), 2)
                
                # Desenha o item
                if item.image:
                    # Redimensiona a imagem se necessário
                    scaled_image = pygame.transform.scale(item.image, (item_size-8, item_size-8))
                    screen.blit(scaled_image, (x+4, y+4))
                
                # Desenha o nome do item
                name_text = self.font.render(item.name, True, (255, 255, 255))
                screen.blit(name_text, (x, y + item_size + 5))
                
                # Desenha a descrição do item
                desc_font = pygame.font.Font(None, 24)
                desc_text = desc_font.render(item.description, True, (200, 200, 200))
                screen.blit(desc_text, (x, y + item_size + 30))
        
        close_text = self.font.render("Pressione I para fechar", True, (200, 200, 200))
        screen.blit(close_text, (screen.get_width()/2 - close_text.get_width()/2, screen.get_height() - 50)) 