from typing import NamedTuple, Dict


class Block(NamedTuple):
    name: str
    width: int
    height: int


Blocks: Dict[str, Block] = {
        'logic-processor': Block(name='logic-processor', width=2, height=2), 
        'hyper-processor': Block(name='hyper-processor', width=3, height=3), 
        'memory-bank': Block(name='memory-bank', width=2, height=2),
        'thorium-wall': Block(name='thorium-wall', width=1, height=1),
        'liquid-source': Block(name='liquid-source', width=1, height=1),
        'large-logic-display': Block(name='large-logic-display', width=3, height=3),
}
