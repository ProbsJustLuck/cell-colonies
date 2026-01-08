from typing import TYPE_CHECKING, Any
import pygame

from classes.entity import Entity
from classes.position import Position
from classes.ui.colors import TeamColor
from classes.ui.menu_area import MenuArea
from classes.ui.key_actions import KeyActions
from constants import Constants

if TYPE_CHECKING:
    from classes.ui.typewriter import Typewriter
    from classes.world_manager import WorldManager
    from classes.ui.button import Button
    from classes.ui.slider import Slider

class States:
    running: bool = True
    full_pause: bool = False
    sim_pause: bool = True

    # Menu flags
    skipped_animation: bool = False
    loaded_menu: bool = False
    current_area = MenuArea.MAIN_MENU
    starting_opacity: int = 0

    controls_section = "controls"
    first_tick = False

    # Sim options
    sim_size: int = 20
    sim_homebases: int = 2
    sim_walls: int = 40
    health_multiplier: float = 1.0
    spawn_rate: int = 3

    old_size: int = 20
    old_homebases: int = 2
    old_walls: int = 40
    old_health: float = 1.0

    # Simulation
    game_end: bool = False
    panning: bool = False
    second_render_page: bool = False
    world: "WorldManager | None" = None
    max_catchup: int = 5
    max_history: int = 30
    sound_fx_volume: float = 0.5
    music_volume: float = 0.5

    selected_cell: Entity | None = None
    selected_id: int | None = None
    disabled_cells: list[str] = []

    hovered_pos: Position | None = None

    last_played_game: dict[str, "WorldManager | tuple[Any, ...]"] | None = None
    
    ## Zooming + panning
    offset: pygame.Vector2 = pygame.Vector2(0, 0)
    SIM_RECT = pygame.Rect(55, 70, 590, 520)
    zoom: float = Constants.DEFAULT_ZOOM
    zoom_levels: list[float] = []
    zoom_index: int = 0
    panning: bool = False
    old_cursor_pos: tuple[int, int] = (0, 0)

    ## Sim buttons
    fast_forward: "Button | None" = None
    forward: "Button | None" = None
    pause: "Button | None" = None
    rewind: "Button | None" = None
    fast_rewind: "Button | None" = None
    tps_button: "Button | None" = None
    tps_up: "Button | None" = None
    tps_down: "Button | None" = None
    tps_slider: "Slider | None" = None
    prev_render_page: "Button | None" = None
    next_render_page: "Button | None" = None
    fit_view_button: "Button | None" = None

    quit_button: "Button | None" = None
    reset_button: "Button | None" = None

    ## Special buttons
    special_buttons: dict[int, "Button"] = {}
    special_sliders: dict[int, "Slider"] = {}

    # tps control
    target_tps: float = 2
    tps: float = 0
    show_tps: bool = False
    tps_change: int = 0

    # Seed controls
    changing_seed: bool = False
    seed_button: "Button | None" = None
    seed_box: pygame.Rect | None = None
    typing_box: pygame.Rect | None = None
    typing_seed: bool = False
    seed_string: str = ""
    backspace_repeat: int = 0
    caret_timer: int = 0

    ## Seed speed ups
    homebase_change: int = 0
    health_change: int = 0
    spawn_change: int = 0
    wall_change: int = 0
    size_change: int = 0

    # Bob ross
    typewriter: "Typewriter | None" = None
    finished_timer: int = 0
    seen_bob: bool = False
    skip_tutorial: bool = False

    waiting_for_pan: bool = False
    panned: bool = False
    zoomed: bool = False

    waiting_for_pause: bool = False
    paused_forward: bool = False

    waiting_for_rewind: bool = True
    rewinded: bool = False

    finished_tutorial: bool = False


    # Controls
    bindings: dict[KeyActions, int] = {
        KeyActions.PAN_ALIAS: pygame.K_a,

        KeyActions.PAN_UP: pygame.K_UP,
        KeyActions.PAN_DOWN: pygame.K_DOWN,
        KeyActions.PAN_LEFT: pygame.K_LEFT,
        KeyActions.PAN_RIGHT: pygame.K_RIGHT,

        KeyActions.ZOOM_IN_ALIAS: pygame.K_EQUALS,
        KeyActions.ZOOM_OUT_ALIAS: pygame.K_MINUS,

        KeyActions.ADVANCE_DIALOGUE: pygame.K_c,
        KeyActions.PAUSE_UNPAUSE: pygame.K_SPACE,

        KeyActions.STEP_FORWARD: pygame.K_PERIOD,
        KeyActions.STEP_BACKWARD: pygame.K_COMMA,

        KeyActions.REGENERATE_WORLD: pygame.K_r,
    }
    second_binding_page: bool = False
    rebinding: tuple[KeyActions, "Button"] | None = None
    conflicts: list[KeyActions] = []

    toggle_colonies: list["Button"] = []
    allowed_colonies: list[TeamColor] = list(TeamColor)


    # Resolutions
    reverting: bool = False
    reverting_time: int = 0
    skip_button_hover: bool = False

    option_fullscreen: bool = False
    current_fullscreen: bool = False
    revert_fullscreen: bool = False

    option_res: int = 3
    current_res: int = 3
    revert_res: int = 3


    # Developer stuff
    show_paths: bool = False
    show_target_lines: bool = False


    # Catalogue stuff
    cell_color_index: int = 0
    cell_color_timer: int = 0
    catalogue_area: str = "homebase"
    unlocked_teleporter: bool = False


    # Rewind timeline
    TIMELINE_RECT = pygame.rect.Rect(19, 70, 31, 518)
    y_offset: int = 0

    # Other stuff
    font_cache: dict[int, pygame.font.Font] = {}