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
    self._colors = {}

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
      return "color(%i)\nbgnpolygon();\n" % (
        self.fill or 7
      )
    else:
      return "bgnline();\n"

  @property
  def fti_end_path(self):    
    if self.is_polygon and self.stroke:
      return "endoutlinepolygon(%i);\n" % (self.stroke)
    elif self.is_polygon:
      return "pclos();\n"
    else:
      return "bclos(%i);\n" % (self.stroke or 0)

  @property
  def colors_from_style(self):
    style = self.svg_element.get('style')
    if not style:
      return {}
    
    colors = {}
    fill = re.search(r'fill( +)?:( +)?(?P<fill>[^;]*);', style)
    if fill and fill.groupdict():
      fill = fill.groupdict()['fill']
      parsed_fill = tinycss2.color3.parse_color(fill)
      colors['fill'] = self.fti_color.rgb2index(*self.fti_color.rgb_float_to_dec(parsed_fill))

    stroke = re.search(r'stroke( +)?:( +)?(?P<stroke>[^;]*);', style)
    if stroke and stroke.groupdict():
      stroke = stroke.groupdict()['stroke']
      parsed_stroke = tinycss2.color3.parse_color(stroke)
      colors['stroke'] = self.fti_color.rgb2index(*self.fti_color.rgb_float_to_dec(parsed_stroke))

    return colors

  @property
  def is_polygon(self):
    attr_fill = self.colors_from_attribute('fill')

    if attr_fill or 'fill' in self.colors_from_style:
      return True
    
    return False

  @property
  def colors(self):
    if len(self._colors):
      return self._colors

    self._colors = {
      'attr_stroke': self.colors_from_attribute('stroke'),
      'attr_fill': self.colors_from_attribute('fill'),
      'css_colors': self.colors_from_style
    }

    return self._colors

  @property
  def fill(self):
    return self.colors['attr_fill'] or self.colors['css_colors'].get('fill', None)

  @property
  def stroke(self):
    return self.colors['attr_stroke'] or self.colors['css_colors'].get('stroke', None)

  def colors_from_attribute(self, attr):
    color = self.svg_element.get(attr)

    if not color or 'url' in color:
      return None

    parsed = tinycss2.color3.parse_color(color)
    if not parsed:
      return None

    return self.fti_color.rgb2index(*self.fti_color.rgb_float_to_dec(parsed))

  def map_points(self, fn):
    self._points = list(map(fn, self._points))
