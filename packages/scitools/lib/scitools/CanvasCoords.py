#!/usr/bin/env python
"""Transformation between canvas and physical coordinates."""

def roundInt(a): return int(a+0.5)

class CanvasCoords:
    """
    Utilities for transforming between canvas coordinates and
    physical (real) coordinates.
    """
    def __init__(self):
        # 400x400 pixels is default:
        self.canvas_x = self.canvas_y = 400  
        # origin: lower left corner:
        self.x_origin = 0; self.y_origin = self.canvas_y
        # x and y measured in pixels:
        self.x_range = self.canvas_x                  
        self.xy_scale = self.canvas_x/self.x_range

    def set_coordinate_system(self, canvas_width, canvas_height,
                              x_origin, y_origin, x_range = 1.0):
        """
        Define parameters in the physical coordinate system
        (origin, width) expressed in canvas coordinates.
        x_range is the width of canvas window in physical coordinates.
        """
        self.canvas_x = canvas_width   # width  of canvas window
        self.canvas_y = canvas_height  # height of canvas window

        # the origin in canvas coordinates:
        self.x_origin = x_origin
        self.y_origin = y_origin

        # x range (canvas_x in physical coords):
        self.x_range = x_range
        self.xy_scale = self.canvas_x/self.x_range

    def print_coordinate_system(self):
        print "canvas = (%d,%d)" % (self.canvas_x, self.canvas_y)
        print "canvas origin = (%d,%d)" % (self.x_origin, self.y_origin)
        print "range of physical x coordinate =", self.x_range
        print "xy_scale (from physical to canvas): ", self.xy_scale
    
    # --- transformations between physical and canvas coordinates: ---
    
    def physical2canvas(self, x, y):
        """Transform physical (x,y) to canvas 2-tuple."""
        return (roundInt(self.x_origin + x*self.xy_scale),
                roundInt(self.y_origin - y*self.xy_scale))
    
    def cx(self,x):
        """Transform physical x to canvas x."""
        return roundInt(self.x_origin + x*self.xy_scale)
    
    def cy(self,y):
        """Transform physical y to canvas y."""
        return roundInt(self.y_origin - y*self.xy_scale)
    
    def physical2canvas4(self, coords):
        """
        Transform physical 4-tuple (x1,x2,y1,y2) to
        canvas 4-tuple.
        """
        return (roundInt(self.x_origin + coords[0]*self.xy_scale),
                roundInt(self.y_origin - coords[1]*self.xy_scale),
                roundInt(self.x_origin + coords[2]*self.xy_scale),
                roundInt(self.y_origin - coords[3]*self.xy_scale))
    
    def canvas2physical(self, x, y):
        """Inverse of physical2canvas."""
        return (float((x - self.x_origin)/self.xy_scale),
                float((self.y_origin - y)/self.xy_scale))
    
    def canvas2physical4(self, coords):
        """Inverse of physical2canvas4."""
        return (float((coords[0] - self.x_origin)/self.xy_scale),
                float((self.y_origin - coords[1])/self.xy_scale),
                float((coords[2] - self.x_origin)/self.xy_scale),
                float((self.y_origin - coords[3])/self.xy_scale))

    def scale(self, dx):
        """
        Transform a length in canvas coordinates
        to a length in physical coordinates.
        """
        return self.xy_scale*dx

    # short forms:
    c2p  = canvas2physical
    c2p4 = canvas2physical4
    p2c  = physical2canvas
    p2c4 = physical2canvas4

if __name__ == '__main__':
    from Tkinter import *
    root = Tk()
    c = Canvas(root,width=400, height=400)
    c.pack()
    # let physical (x,y) be at (200,200) and let the x range be 2:
    C.set_coordinate_system(400,400, 200,200, 2.0)
    cc = C.p2c4((0.2, 0.2, 0.6, 0.6))
    c.create_oval(cc[0],cc[1],cc[2],cc[3],fill='red',outline='blue')
    c1, c2 = C.physical2canvas(0.2,0.2)
    c.create_text(c1, c2, text='(0.2,0.2)')
    c1, c2 = C.physical2canvas(0.6,0.6)
    c.create_text(c1, c2, text='(0.6,0.6)')
    c.create_line(C.cx(0.2), C.cy(0.2),
                  C.cx(0.6), C.cy(0.2),
                  C.cx(0.6), C.cy(0.6),
                  C.cx(0.2), C.cy(0.6),
                  C.cx(0.2), C.cy(0.2))
