from generate_character import CharacterGenerator
import os

def generate_npc_sprites():
    generator = CharacterGenerator()
    
    # Villager colors (green and brown theme)
    villager_colors = {
        'body': (76, 153, 0, 255),      # Green vest
        'head': (255, 218, 185, 255),   # Peach skin
        'detail': (101, 67, 33, 255),   # Brown details
        'legs': (139, 69, 19, 255)      # Brown pants
    }
    
    # Merchant colors (blue and gold theme)
    merchant_colors = {
        'body': (25, 25, 112, 255),     # Dark blue robe
        'head': (255, 218, 185, 255),   # Peach skin
        'detail': (218, 165, 32, 255),  # Golden details
        'legs': (70, 130, 180, 255)     # Steel blue pants
    }
    
    # Guard colors (silver and red theme)
    guard_colors = {
        'body': (169, 169, 169, 255),   # Silver armor
        'head': (255, 218, 185, 255),   # Peach skin
        'detail': (139, 0, 0, 255),     # Dark red details
        'legs': (128, 128, 128, 255)    # Gray pants
    }
    
    # Generate NPC sprites
    npcs = {
        'villager': villager_colors,
        'merchant': merchant_colors,
        'guard': guard_colors
    }
    
    for npc_type, colors in npcs.items():
        sheet = generator.create_character_spritesheet(colors)
        sheet.save(generator.base_path / f'npc_{npc_type}.png')
        print(f"Generated {npc_type} spritesheet!")

if __name__ == "__main__":
    generate_npc_sprites()