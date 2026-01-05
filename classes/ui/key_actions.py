from enum import StrEnum

class KeyActions(StrEnum):
    PAN_ALIAS = "pan_alias"

    PAN_UP = "pan_up"
    PAN_DOWN = "pan_down"
    PAN_LEFT = "pan_left"
    PAN_RIGHT = "pan_right"

    ZOOM_IN_ALIAS = "zoom_in_alias"
    ZOOM_OUT_ALIAS = "zoom_out_alias"

    ADVANCE_DIALOGUE = "advance_dialogue"
    PAUSE_UNPAUSE = "pause/unpause"

    STEP_FORWARD = "step_forward"
    STEP_BACKWARD = "step_backward"

    REGENERATE_WORLD = "regenerate_world"