import random
from .npc import NPC

class NPCSpawner:
    def __init__(self):
        self.npcs = []
        self.npc_types = {
            "villager": {
                "dialogues": [
                    "Welcome to our village!",
                    "Beautiful weather today, isn't it?",
                    "Be careful of monsters in the forest.",
                    "I heard there's treasure in the caves.",
                ],
            },
            "merchant": {
                "dialogues": [
                    "Want to trade?",
                    "I've got the best prices in town!",
                    "Fresh goods from the capital!",
                    "Buy something, will ya?",
                ],
            },
            "guard": {
                "dialogues": [
                    "Stay out of trouble.",
                    "I'm keeping an eye on you.",
                    "Report any suspicious activity.",
                    "The village is under my protection.",
                ],
            },
        }
        
    def spawn_npc(self, x, y, npc_type="villager"):
        """Spawn a new NPC at the given position"""
        if npc_type not in self.npc_types:
            npc_type = "villager"
            
        npc = NPC(x, y, npc_type)
        
        # Add random dialogues from the NPC's type
        dialogues = self.npc_types[npc_type]["dialogues"]
        for dialogue in dialogues:
            npc.add_dialogue(dialogue)
            
        self.npcs.append(npc)
        return npc
        
    def update(self, player_x, player_y):
        """Update all NPCs"""
        for npc in self.npcs:
            # Check for player interaction range
            npc.is_talking = npc.can_interact(player_x, player_y)
            
    def draw(self, screen, camera_x, camera_y):
        """Draw all NPCs"""
        for npc in self.npcs:
            npc.draw(screen, camera_x, camera_y)