import json

class FTIColor:
  def __init__(self, color_map=None):
    self.color_map = json.loads(open(color_map).read())

  def rgb2index(self, fr, fg, fb):
    avg, color = 500, 0
    for fti, (r, g, b) in self.color_map.items():
      cur = abs(r - fr) + abs(g - fg) + abs(b - fb)
      if cur < avg:
        avg = cur
        color = int(fti)
    return color

  def rgb_float_to_dec(self, parsed):
    if not parsed:
      return (0,0,0)
    
    return (
      int(parsed.red * 255),
      int(parsed.green * 255),
      int(parsed.blue * 255)
    )