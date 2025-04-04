class GameState:
    def __init__(self):
        self.current_scene = "menu"  # menu, game, combat, inventory
        self.in_combat = False
        self.current_turn = 0
        self.enemies = []
        self.items = []
        
    def change_scene(self, new_scene):
        self.current_scene = new_scene
        
    def start_combat(self, enemies):
        self.in_combat = True
        self.enemies = enemies
        self.current_turn = 0
        
    def end_combat(self):
        self.in_combat = False
        self.enemies = []
        self.current_turn = 0
        
    def next_turn(self):
        self.current_turn += 1 