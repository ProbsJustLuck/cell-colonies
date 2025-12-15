import WorldManager

class Entity:
    category = None # What category this entity is (from "type").
    icon = None # The icon that this entity uses.
    
    def __init__(self, x: int, y: int):
        self._x: int = x # The x coordinate of this entity.
        self._y: int = y # The y coordinate of this entity.

        self._alive: bool = True # Whether this entity is laive or not.

    def tick(self):
        return None # Generic tick function
    
    def get_pos(self):
        return { self._x, self._y }
    
    def _deregister(self, worldmanager: WorldManager.WorldManager):
        pass