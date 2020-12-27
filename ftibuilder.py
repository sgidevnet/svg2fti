import argparse
import xml.etree.ElementTree as ET
import itertools
import random

from svg.path import parse_path

"""
FTIBuilder: generate SGI Icon
@mach-kernel / dstancu@nyu.edu
"""

class FTIPath:
  def __init__(
    self,
    svg_document=None,
    svg_element=None,
    num_samples=None
  ):
    self.svg_element = svg_element
    self.svg_path = parse_path(svg_element.get('d'))
    self.num_samples = num_samples

    # opaque
    self._points = []

  # sgi output colors are int -255 -> 15
  # def ident_color_string():
  # case hex, case ref, etc 

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
    if self.svg_element.get('fill'):
      return "bgnpolygon();\n%s" % self.color
    else:
      return "bgnline();\n"

  @property
  def fti_end_path(self):
    if self.svg_element.get('fill'):
      return "pclos();\n"
    else:
      return "endline();\n"

  @property
  def color(self):
    return "color(%i);\n" % random.sample(range(-255, 15), 1)[0]

  def map_points(self, fn):
    self._points = list(map(fn, self._points))

class FTIBuilder:
  def __init__(self, svg=None, num_samples=None, out=None):
    # args
    self.svg_et = ET.parse(svg)
    self.num_samples = num_samples
    self.out = out

    # data
    self.fti_paths = list(self.gen_fti_paths())

  def gen_fti_paths(self):
    for el in self.svg_et.findall('.//{http://www.w3.org/2000/svg}path'):
      yield FTIPath(
        svg_document=self.svg_et,
        svg_element=el,
        num_samples=self.num_samples
      )

  def write_fti(self):
    self.fix_scale()

    f = open(self.out, 'w')

    for num, fti_path in enumerate(self.fti_paths):

      f.write("#Path %d\n" % (num))
      f.write(fti_path.fti_begin_path);
      for vertex in fti_path.points:
        # reflect y
        f.write("vertex(%f,%f);\n" % (vertex.real, 100 - vertex.imag))
      f.write(fti_path.fti_end_path)

    f.close()

  """
  FTI only allows 100x100 so we are going to find the max of (max(real), max(imag)),
  then scale all points accordingly. Make smaller images larger and larger
  images fit on the canvas
  """
  def fix_scale(self):
    max_real, max_imag, max_final = 0, 0, 0

    for fti_path in self.fti_paths:
      for point in fti_path.points:
        max_real = max(max_real, point.real)
        max_imag = max(max_imag, point.imag)

    max_final = max(max_imag, max_real)
    scale = float(100) / max_final

    print(
      "SCALE ADJUSTMENT:\nmax_real %f\nmax_imag %f\nmax_final %f\nscale %f" % 
      (max_real, max_imag, max_final, scale)
    )

    for path in self.fti_paths:
      path.map_points(lambda p: p * scale)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='svg to SGI fti')
  parser.add_argument(
    '--svg',
    help='an svg',
    default=False,
    type=str,
    required=True
  )

  parser.add_argument(
    '--out',
    help='your output',
    default='out.fti',
    type=str,
    required=False
  )

  parser.add_argument(
    '--num_samples',
    help='fti does not support curves. higher is smoother.',
    default=50,
    type=int,
    required=False
  )
  FTIBuilder(**vars(parser.parse_args())).write_fti()
