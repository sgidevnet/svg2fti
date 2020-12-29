import tinycss2.color3
import re

from svg.path import parse_path

class FTIPath:
  def __init__(
    self,
    svg_document=None,
    svg_element=None,
    num_samples=None,
    fti_color=None
  ):
    self.svg_element = svg_element
    self.svg_path = parse_path(svg_element.get('d'))
    self.num_samples = num_samples
    self.fti_color = fti_color

    self._points = []

  @property
  def points(self):
    if len(self._points):
      return self._points
    
    for i in range(0, self.num_samples - 1):
      lerp = float(i) / self.num_samples
      point = self.svg_path.point(lerp)
      print("Sample %d (lerp %f): %s" % (i, lerp, point))
      self._points.append(point)

    self._points.append(self.svg_path.point(1))
    return self._points

  @property
  def fti_begin_path(self):
    if self.is_polygon:
      return "color(%s)\nbgnpolygon();\n" % self.color
    else:
      return "bgnline();\n"

  @property
  def fti_end_path(self):
    if self.is_polygon:
      return "pclos();\n"
    else:
      return "bclos(%i);\n" % self.color

  @property
  def colors_from_style(self):
    style = self.svg_element.get('style')
    if not style:
      return {}
    
    colors = {}
    fill = re.match('fill( +)?:( +)?(?P<fill>[^;]*);', style)
    if fill and fill.groupdict():
      fill = fill.groupdict()['fill']
      parsed_fill = tinycss2.color3.parse_color(fill)
      colors['fill'] = self.fti_color.rgb2index(*self.fti_color.rgb_float_to_dec(parsed_fill))

    stroke = re.match('stroke( +)?:( +)?(?P<stroke>[^;]*);', style)
    if stroke and stroke.groupdict():
      stroke = stroke.groupdict()['stroke']
      parsed_stroke = tinycss2.color3.parse_color(stroke)
      colors['stroke'] = self.fti_color.rgb2index(*self.fti_color.rgb_float_to_dec(parsed_stroke))

    return colors

  @property
  def is_polygon(self):
    attr_stroke = self.colors_from_attribute('stroke')
    attr_fill = self.colors_from_attribute('fill')
    css_colors = self.colors_from_style

    if attr_fill or 'fill' in self.colors_from_style:
      return True
    
    return False

  @property
  def color(self):
    attr_stroke = self.colors_from_attribute('stroke')
    attr_fill = self.colors_from_attribute('fill')
    css_colors = self.colors_from_style

    print("colors", attr_fill, attr_stroke, css_colors)

    if self.is_polygon and 'fill' in css_colors:
      return css_colors['fill']
    elif self.is_polygon:
      return attr_fill
    elif not self.is_polygon and 'stroke' in css_colors:
      return css_colors['stroke']
    elif not self.is_polygon and attr_stroke:
      return attr_stroke
    
    return 0

  # @property
  # def color(self):
    # random
    # return "color(%i);\n" % random.sample(range(-255, 15), 1)[0]

  def colors_from_attribute(self, attr):
    color = self.svg_element.get(attr)

    if not color or 'url' in color:
      return ''

    parsed = tinycss2.color3.parse_color(color)
    if not parsed:
      return ''

    return self.fti_color.rgb2index(*self.fti_color.rgb_float_to_dec(parsed))

  def map_points(self, fn):
    self._points = list(map(fn, self._points))
