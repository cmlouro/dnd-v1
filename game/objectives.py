import pygame

class Objective:
    def __init__(self, description, target_count):
        self.description = description
        self.target_count = target_count
        self.current_count = 0
        self.completed = False
        self.show_completion_message = False
        self.completion_message_timer = 0
        self.completion_message_duration = 180  # 3 segundos a 60 FPS
        
    def update(self):
        if self.show_completion_message:
            if self.completion_message_timer > 0:
                self.completion_message_timer -= 1
            else:
                self.show_completion_message = False
                
    def increment_progress(self):
        if not self.completed:
            self.current_count += 1
            if self.current_count >= self.target_count:
                self.completed = True
                self.show_completion_message = True
                self.completion_message_timer = self.completion_message_duration
                
    def draw(self, screen):
        # Desenha o objetivo atual abaixo das barras de vida/mana
        font = pygame.font.Font(None, 32)
        text = f"Objetivo: {self.description} ({self.current_count}/{self.target_count})"
        text_surface = font.render(text, True, (255, 255, 255))
        screen.blit(text_surface, (10, 100))  # Posicionado abaixo das barras
        
        # Desenha a mensagem de conclusão no centro da tela
        if self.show_completion_message:
            font_large = pygame.font.Font(None, 64)
            completion_text = "Objetivo Concluído!"
            text_surface = font_large.render(completion_text, True, (255, 215, 0))  # Dourado
            
            # Cria um fundo semi-transparente para a mensagem
            message_bg = pygame.Surface((text_surface.get_width() + 40, text_surface.get_height() + 20))
            message_bg.fill((0, 0, 0))
            message_bg.set_alpha(128)
            
            # Posiciona a mensagem no centro da tela
            screen_center_x = screen.get_width() // 2
            screen_center_y = screen.get_height() // 2
            
            bg_x = screen_center_x - message_bg.get_width() // 2
            bg_y = screen_center_y - message_bg.get_height() // 2
            text_x = screen_center_x - text_surface.get_width() // 2
            text_y = screen_center_y - text_surface.get_height() // 2
            
            # Desenha o fundo e o texto
            screen.blit(message_bg, (bg_x, bg_y))
            screen.blit(text_surface, (text_x, text_y))

class ObjectiveManager:
    def __init__(self):
        self.current_objective = None
        self.completed_objectives = []
        
    def set_objective(self, description, target_count):
        self.current_objective = Objective(description, target_count)
        
    def update(self):
        if self.current_objective:
            self.current_objective.update()
            
    def draw(self, screen):
        if self.current_objective:
            self.current_objective.draw(screen)
            
    def on_npc_killed(self):
        if self.current_objective:
            self.current_objective.increment_progress()
            if self.current_objective.completed:
                self.completed_objectives.append(self.current_objective)
                # Aqui podemos adicionar lógica para definir o próximo objetivo 