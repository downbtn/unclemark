import sys
import ezdxf
import numpy as np
from math import cos, sin
from ezdxf.math import bulge_to_arc

# dxf_to_paths takes a filepath to the dxf file, shift (if true, centers path to 0,0),
# and scale (multiplies each coordinate by a given float, default is 1.0, no scale).
# It returns a 2D array, where each array element is a path, and each path is an array
# of coordinate tuples (x, y)

def arc_to_points(p0, p1, bulge, steps=20):
    """Convert a DXF bulge segment into discretized (x, y) points."""
    center, a0, a1, r = bulge_to_arc(p0, p1, bulge)
    cx, cy = center

    return [
        (
            cx + r * cos(t),
            cy + r * sin(t)
        )
        for t in np.linspace(a0, a1, steps)
    ]

def dxf_to_paths(filepath, shift=True, scale=1.0):

  try:
    doc = ezdxf.readfile(filepath)
  except IOError:
    print(f"Not a DXF file or a generic I/O error.")
    sys.exit(1)
  except ezdxf.DXFStructureError:
    print(f"Invalid or corrupted DXF file.")
    sys.exit(2)

  msp = doc.modelspace()

  paths = []
  minleft = 999999
  mintop = 999999

  for e in msp:
      etype = e.dxftype()

      # ---------------- LINE ----------------
      if etype == "LINE":
          p0 = (e.dxf.start.x, e.dxf.start.y)
          p1 = (e.dxf.end.x,   e.dxf.end.y)
          minleft = min(e.dxf.start.x, e.dxf.end.x, minleft)
          mintop = min(e.dxf.start.y, e.dxf.end.y, mintop)
          paths.append([p0, p1])

      # ------------ LWPOLYLINE --------------
      elif etype == "LWPOLYLINE":
          pts = list(e.get_points())
          if len(pts) < 2:
              continue

          path = []

          for i in range(len(pts) - 1):
              x0, y0, _, _, bulge = pts[i]
              x1, y1, *_ = pts[i + 1]

              if bulge == 0:
                  path.append((x0, y0))
              else:
                  path.extend(
                      arc_to_points((x0, y0), (x1, y1), bulge)
                  )

          # add final vertex
          path.append((pts[-1][0], pts[-1][1]))

          if e.closed:
              path.append(path[0])

          for coord in path:
              xcoord, ycoord = coord
              minleft = min(xcoord, minleft)
              mintop = min(ycoord, mintop)

          paths.append(path)

      # --------------- POLYLINE --------------
      elif etype == "POLYLINE":
          verts = list(e.vertices)
          if len(verts) < 2:
              continue

          path = []

          for i in range(len(verts) - 1):
              v0 = verts[i]
              v1 = verts[i + 1]

              x0, y0 = v0.dxf.location.x, v0.dxf.location.y
              x1, y1 = v1.dxf.location.x, v1.dxf.location.y
              bulge = v0.dxf.bulge

              if bulge == 0:
                  path.append((x0, y0))
              else:
                  path.extend(
                      arc_to_points((x0, y0), (x1, y1), bulge)
                  )

          # final vertex
          path.append(
              (verts[-1].dxf.location.x, verts[-1].dxf.location.y)
          )

          if e.is_closed:
              path.append(path[0])

          for coord in path:
              xcoord, ycoord = coord
              minleft = min(xcoord, minleft)
              mintop = min(ycoord, mintop)

          paths.append(path)


  # shift to top left if true
  if shift:
    for i,path in enumerate(paths):
      for j,coord in enumerate(path):
          x, y = coord
          newcoord = (x-minleft)*scale, (y-mintop)*scale
          paths[i][j] = newcoord

  return(paths)


path = 'test_square.dxf'
print(dxf_to_paths(path, shift=True, scale=0.7))
