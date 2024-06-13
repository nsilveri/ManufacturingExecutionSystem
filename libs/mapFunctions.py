# mapFunction.py

class Mapper:
    def __init__(self, original_width, original_height, root_width, root_height):
        self.original_width = original_width
        self.original_height = original_height
        self.root_width = root_width
        self.root_height = root_height
        self.gui_scale = 0
    
    def _map(self, value, from_low, from_high, to_low, to_high):
        if to_high != 0:
            return (value - from_low) * (to_high - to_low) / (from_high - from_low) + to_low
        else:
            return value
    
    def _map_win_x(self, value):
        value_adapted = int(self._map(value, 0, self.original_width, 0, self.root_width))
        return value_adapted
    
    def _map_win_y(self, value):
        value_adapted = int(self._map(value, 0, self.original_height, 0, self.root_height))
        return value_adapted
    
    def _map_rel_x(self, value):
        value_adapted = int(self._map(value, 0, self.original_width, 0, self.root_width))
        return value_adapted
    
    def _map_rel_y(self, value):
        value_adapted = int(self._map(value, 0, self.original_height, 0, self.root_height))
        return value_adapted
    
    def _map_frame_x(self, value):
        gui_scale_int = self.gui_scale / 100
        if self.gui_scale != 0:
            value_adapted = int(self._map(value, 0, value, 0, (value + gui_scale_int)))
            return value_adapted
        else:
            return value
    
    def _map_frame_y(self, value):
        gui_scale_int = self.gui_scale / 100
        if self.gui_scale != 0:
            value_adapted = int(self._map(value, 0, value, 0, (value + gui_scale_int)))
            return value_adapted
        else:
            return value
    
    def _map_item_x(self, value, frame_dim_x):
        gui_scale_int = self.gui_scale / 100
        if self.gui_scale != 0:
            value_adapted = int(self._map(value, 0, frame_dim_x, 0, (frame_dim_x + gui_scale_int)))
            return value_adapted
        else:
            return value
    
    def _map_item_y(self, value, frame_dim_y):
        gui_scale_int = self.gui_scale / 100
        if self.gui_scale != 0:
            value_adapted = int(self._map(value, 0, frame_dim_y, 0, (frame_dim_y + gui_scale_int)))
            return value_adapted
        else:
            return value
