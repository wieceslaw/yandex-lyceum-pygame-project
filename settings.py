'''
game settings
'''
TILE_SIZE = 50
FPS = 60
WIDTH, HEIGHT = 1200, 800
MUSIC = True
SPRITE = True

LEVELS = {
    '0': 'level_0',
    '1': 'level_1',
    '2': 'level_2',
    '3': None
}
tiles_tx = {
    '0': 'box',
    '1': 'green_stone_tile',
    '2': 'stone_tile'
}
wall_tx = {
    '0': 'stone_wall',
    '1': 'box_wall',
    '2': 'stone_wall_2'
}
platforms_tx = {
    '2': ['horizontal_left_platform', 'horizontal_right_platform'],
    '1': ['vertical_up_platform', 'vertical_down_platform'],
    '0': ['stone_platform', 'stone_platform']
}
pikes_tx = {
    '1': 'pike_up',
    '0': 'pike_down',
    '2': 'pike_right',
    '3': 'pike_left'
}
ladders_tx = {
    '0': 'dark_ladder',
    '1': 'light_ladder'
}
portals_tx = {
    '1': 'portal',
    '0': 'portal_1'
}
traps_tx = {
    '1': 'scullet_right',
    '0': 'scullet_left'
}
arrow_tx = {
    '0': 'arrow_left',
    '1': 'arrow_right'
}