import matplotlib.pyplot as plt
import numpy as np
from skimage import draw

grid = np.zeros((62, 120))
rr, cc = draw.ellipse(r=26, c=60, r_radius=10, c_radius=3)

grid[rr, cc] = 1

plt.imshow(grid)
plt.show()
