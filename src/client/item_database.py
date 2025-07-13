from .items import Item, ItemType

# Weapons
IRON_SWORD = Item(
    name="Iron Sword",
    item_type=ItemType.WEAPON,
    description="A basic iron sword.",
    icon_name="iron_sword.png",
    stats={
        'damage': 10,
        'speed': 1.0,
        'rarity': 'common'
    }
)

STEEL_SWORD = Item(
    name="Steel Sword",
    item_type=ItemType.WEAPON,
    description="A well-crafted steel sword.",
    icon_name="steel_sword.png",
    stats={
        'damage': 15,
        'speed': 1.1,
        'rarity': 'uncommon'
    }
)

MAGIC_STAFF = Item(
    name="Magic Staff",
    item_type=ItemType.WEAPON,
    description="A staff imbued with magical energy.",
    icon_name="magic_staff.png",
    stats={
        'damage': 8,
        'magic': 12,
        'mana_regen': 2,
        'rarity': 'rare'
    }
)

# Armor
LEATHER_ARMOR = Item(
    name="Leather Armor",
    item_type=ItemType.ARMOR,
    description="Basic leather protection.",
    icon_name="leather_armor.png",
    stats={
        'defense': 5,
        'speed': 0.1,
        'rarity': 'common'
    }
)

STEEL_ARMOR = Item(
    name="Steel Armor",
    item_type=ItemType.ARMOR,
    description="Heavy but protective steel armor.",
    icon_name="steel_armor.png",
    stats={
        'defense': 12,
        'speed': -0.1,
        'rarity': 'uncommon'
    }
)

MAGE_ROBE = Item(
    name="Mage's Robe",
    item_type=ItemType.ARMOR,
    description="Enchanted robe that enhances magical abilities.",
    icon_name="mage_robe.png",
    stats={
        'defense': 4,
        'magic': 8,
        'mana_regen': 1,
        'rarity': 'rare'
    }
)

# Potions
HEALTH_POTION = Item(
    name="Health Potion",
    item_type=ItemType.POTION,
    description="Restores 50 HP when used.",
    icon_name="health_potion.png",
    stats={
        'heal': 50,
        'rarity': 'common'
    }
)

MANA_POTION = Item(
    name="Mana Potion",
    item_type=ItemType.POTION,
    description="Restores 50 MP when used.",
    icon_name="mana_potion.png",
    stats={
        'mana': 50,
        'rarity': 'common'
    }
)

STRENGTH_POTION = Item(
    name="Strength Potion",
    item_type=ItemType.POTION,
    description="Temporarily increases strength by 5.",
    icon_name="strength_potion.png",
    stats={
        'strength': 5,
        'duration': 60,
        'rarity': 'uncommon'
    }
)

# Materials
IRON_ORE = Item(
    name="Iron Ore",
    item_type=ItemType.MATERIAL,
    description="Raw iron ore for crafting.",
    icon_name="iron_ore.png",
    stats={
        'rarity': 'common'
    }
)

MAGIC_CRYSTAL = Item(
    name="Magic Crystal",
    item_type=ItemType.MATERIAL,
    description="A crystal pulsing with magical energy.",
    icon_name="magic_crystal.png",
    stats={
        'rarity': 'rare'
    }
)

# Quest Items
ANCIENT_RELIC = Item(
    name="Ancient Relic",
    item_type=ItemType.QUEST,
    description="A mysterious artifact from an ancient civilization.",
    icon_name="ancient_relic.png",
    stats={
        'rarity': 'epic'
    }
)

# Dictionary of all items for easy access
ALL_ITEMS = {
    'iron_sword': IRON_SWORD,
    'steel_sword': STEEL_SWORD,
    'magic_staff': MAGIC_STAFF,
    'leather_armor': LEATHER_ARMOR,
    'steel_armor': STEEL_ARMOR,
    'mage_robe': MAGE_ROBE,
    'health_potion': HEALTH_POTION,
    'mana_potion': MANA_POTION,
    'strength_potion': STRENGTH_POTION,
    'iron_ore': IRON_ORE,
    'magic_crystal': MAGIC_CRYSTAL,
    'ancient_relic': ANCIENT_RELIC
}