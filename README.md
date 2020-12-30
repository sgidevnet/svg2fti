# svg2fti

A very-much-so-held-together-by-tape helper for converting SVGs to SGI FTI vector format.

```
python3 -m pip install -r requirements.txt

usage: svg2fti.py [-h] --svg SVG [--out OUT] [--num_samples NUM_SAMPLES] [--color_map COLOR_MAP]
svg2fti.py: error: the following arguments are required: --svg
```

#### Example

```
python3 svg2fti.py --svg nedit.svg
```

[Input SVG](https://gist.github.com/mach-kernel/05498f26038336d54b62980b2eb485a2) on left.

[Output FTI](https://gist.github.com/mach-kernel/8ef57d877f4a622a5cedd8b19c438367) on right as visualized by [Aqua Phoenix FTI Editor](https://www.aquaphoenix.com/software/ftieditor/index.html)


![](https://i.imgur.com/bjBVVg7m.png) ![](https://i.imgur.com/iIUkdrGm.png)


### Notes

#### Geometry
- Polygon vs line: if a fill color value cannot be resolved, `bgnline()` is used
- Scale: FTI coords are 100x100, 
- Curves: SVG paths mapped to lists of vertices, increasing `num_samples` will make smoother

#### Color attributes

Colors parsed with `tinycss2.color3` from:
- `stroke`
- `fill`
- `style`

- Gradients are ignored
- Try to follow `url(#id)`: the first (via xpath query) color attribute is chosen

#### Palette

- Valid values are 0 -> 15, -16 -> -255
  - 0 -> 15 are a basic color table
  - -16 -> -255 are other colors that are interpolated combinations of colors 0 -> 15
- `color_map.json` contains a mapping of FTI color palette index to RGB values
- Only palette colors available, color with smallest delta to input chosen
