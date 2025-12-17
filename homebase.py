import world_manager
import entity

class Homebase(entity.Entity):
    icon = "H" # The icon that this entity uses.
    
    def __init__(self, x: int, y: int):
        super().__init__(x, y)
    
    def _deregister(self, world_manager: world_manager.WorldManager):
        world_manager.deregister(self) # Deregisters this homebase from the world manager.