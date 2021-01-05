#!/usr/bin/env python

import json

PRIMARY_COLORS = [
  (0, 0, 0),
  (255, 0, 0),
  (0, 255, 0),
  (255, 255, 0),
  (0, 0, 255),
  (255, 0, 255),
  (0, 255, 255),
  (255, 255, 255),
  (85, 85, 85),
  (198, 113, 113),
  (113, 198, 113),
  (142, 142, 56),
  (113, 113, 198),
  (142, 56, 142),
  (56, 142, 142),
  (170, 170, 170)
]

color_map = {}

for i, (r, g, b) in enumerate(PRIMARY_COLORS):
  color_map[i] = (r, g, b)
  base = -16 * i

  for j, (rm, gm, bm) in zip(range(0, i), PRIMARY_COLORS):
    mixed_index = base - j
    color_map[mixed_index] = (
      (r + rm) / 2,
      (g + gm) / 2,
      (b + bm) / 2
    )

f = open('map.json', 'w')
f.write(json.dumps(color_map))
f.close()
