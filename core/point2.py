

class Point2:

    def __init__(self, x: int, y: int) -> None:
        self.x: int = x
        self.y: int = y
    
    def __eq__(self, other_point):
        return self.x == other_point.x and self.y == other_point.y
    
    def __ne__(self, other_point):
        return self.x != other_point.x and self.y != other_point.y
    
    def __gt__(self, other_point):
        return ((self.y == other_point.y and self.x > other_point.x) or 
                (self.y > other_point.y))
    
    def __ge__(self, other_point):
        return ((self.y == other_point.y and self.x >= other_point.x) or 
                (self.y > other_point.y))
    
    def __lt__(self, other_point):
        return ((self.y == other_point.y and self.x < other_point.x) or 
                (self.y < other_point.y))

    def __lt__(self, other_point):
        return ((self.y == other_point.y and self.x <= other_point.x) or 
                (self.y <= other_point.y))

    @classmethod
    def unpack(cls, pos: int):
        return cls(pos >> 16, pos & 0xFFFF)
    
    @classmethod
    def pack(cls, x: int, y: int) -> int:
        return (x << 16 | y & 0xFFFF)
    
    @classmethod
    def x(cls, pos: int) -> int:
        return pos >> 16
    
    @classmethod
    def y(cls, pos: int) -> int:
        return pos & 0xFFFF

