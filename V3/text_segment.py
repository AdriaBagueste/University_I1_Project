from segment import *
from node import *

A = Node('A', 0, 0)
B = Node('B', 3, 4)
C = Node('C', 5, 12)

AB = Segment('AB', A, B)
BC = Segment('AB', B, C)

print(AB.__dict__, BC.__dict__)


