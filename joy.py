"""
Joy
===

Joy is a tiny creative coding library in Python.

BASIC USAGE

An example of using joy:

    >>> from joy import *
    >>>
    >>> c = Circle(center=Point(x=100, y=100), radius=50)
    >>> show(c)

The `cicle` function creates a new circle and the `show` function
displys it.

PRINCIPLES

Joy follows functional programming approach for it's interface. Each
function/class gives a shape and those shapes can be transformed and
combined using other utililty functions.

By design, there is no global state in the library.

Joy uses SVG to render the shapes and the shapes are really a very thin
wrapper over SVG nodes. It is possible to use every functionality of SVG,
even if that is not exposed in the API.

COORDINATE SYSTEM

Joy uses a canvas with (0, 0) as the center of the canvas.

By default the size of the canvas is (300, 300).

BASIC SHAPES

Joy supports `Circle`, `Rect` and `Line` as basic shapes.

    >>> c = Circle(center=Point(x=100, y=100), radius=50)
    >>> r = Rectangle(center=Point(0, 0), width=200, height=200)
    >>> show(c, r)

All basic shapes have default values of all the arguments, making it
easier to start using them.

    >>> c = Circle()
    >>> r = Rectangle()
    >>> z = Line()
    >>> show(c, r, z)

COMBINING SHAPES

The `combine` function is used to combine multiple shapes into a
single shape.

    >>> shape = combine(Circle(), Rect())
    >>> show(shape)

TRANSFORMATIONS

Joy supports `Translate`, `Rotate` and `Scale` transformations.

The `Translate` transformation moves the given shape by `x` and `y`.

    >>> c1 = Circle(radius=50)
    >>> c2 = c1 | Translate(x=100, y=0)
    >>> show(c1, c2)

As you've seen the above example, transformations are applied using
the `|` operator.

The `Rotate` transformation rotates a shape clockwise by the specified
angle.

    >>> shape = Rectangle() | Rotate(angle=45)
    >>> show(shape)

By default the `rotate` function rotates the shape around the origin.
However, it is also possible to specify the anchor point for rotation.

    >>> shape = Rectangle() | Rotate(angle=45, anchor=Point(x=100, y=100))
    >>> show(shape)

The `Scale` transformation scales a shape.

    >>> shape = Circle() | Scale(sx=1, sy=0.5)
    >>> show(shape)

HIGER ORDER TRANSFORMATIONS

Joy supports a transorm called `Cycle` to rotate a shape multiple times
with angle from 0 to 360 degrees and combining all the resulting shapes.

    >>> flower = Rectangle() | Cycle()
    >>> show(flower)

By default, `Cycle` repeats the rotation for `18` times, however that can be
customizing by specifying the parameter `n`.

    >>> shape = rect() | Cycle(n=3)
    >>> show(shape)

JUPYTER LAB INTEGRATION

Joy integrates very well with Jupyter notebooks and every shape is
represented as SVG image by jupyter.
"""
import html

__version__ = "0.1"
__author__ = "Anand Chitipothu <anand@fossunited.org>"

SQRT2 = 2**0.5

class Shape:
    """Shape is the base class for all shapes in Joy.

    A Shape is an SVG node and supports converting it self into svg text.

    Typically, users do not interact with this class directly, but use it
    through it's subclasses.
    """
    def __init__(self, tag, children=None, transform=None, **attrs):
        """Creates a new shape.
        """
        self.tag = tag
        self.children = children
        self.attrs = attrs
        self.transform = None

    def __repr__(self):
        return f"<{self.tag} {self.attrs}>"

    def __getattr__(self, name):
        if not name.startswith("_") and name in self.attrs:
            return self.attrs[name]
        else:
            raise AttributeError(name)

    def apply_transform(self, transform):
        if self.transform is not None:
            transform = self.transform | transform

        shape = self.clone()
        shape.transform = transform
        return shape

    def clone(self):
        shape = object.__new__(self.__class__)
        shape.__dict__.update(self.__dict__)
        return shape

    def get_attrs(self):
        attrs = dict(self.attrs)
        if self.transform:
            attrs['transform'] = self.transform.as_str()
        return attrs

    def _svg(self, indent="") -> str:
        """Returns the svg representation of this node.

        This method is used to recursively construct the svg of a node
        and it's children.

            >>> c = Shape(tag='circle', cx=100, cy=100, r=50)
            >>> c._svg()
            '<circle cx="100" cy="100" r="50" />'
        """
        attrs = self.get_attrs()
        if self.children:
            tag_text = render_tag(self.tag, **attrs, close=False)
            return (
                indent + tag_text + "\n" +
                "".join(c._svg(indent + "  ") for c in self.children) +
                indent + "</" + self.tag + ">\n"
            )
        else:
            tag_text = render_tag(self.tag, **attrs, close=True)
            return indent + tag_text + "\n"

    def as_svg(self, width=300, height=300) -> str:
        """Renders this node as svg image.

        The svg image is assumed to be of size (300, 300) unless the
        width and the height arguments are provided.

        Example:

            >>> c = Shape(tag='circle', cx=100, cy=100, r=50)
            >>> print(c.as_svg())
            <svg width="300" height="300" viewBox="-150 -150 300 350" fill="none" stroke="black" xmlns="http://www.w3.org/2000/svg">
              <circle cx="100" cy="100" r="50" />
            </svg>
        """
        return SVG([self], width=width, height=height).render()

    def __add__(self, shape):
        if not isinstance(shape, Shape):
            return NotImplemented
        return Group([self, shape])

    def _repr_svg_(self):
        """Returns the svg representation of this node.

        This method is called by Juputer to render this object as an
        svg image.
        """
        return self.as_svg()

class SVG:
    """SVG renders any svg element into an svg image.
    """
    def __init__(self, nodes, width=300, height=300):
        self.nodes = nodes
        self.width = width
        self.height = height

    def render(self):
        svg_header = render_tag(
            tag="svg",
            width=self.width,
            height=self.height,
            viewBox=f"-{self.width//2} -{self.height//2} {self.width} {self.height}",
            fill="none",
            stroke="black",
            xmlns="http://www.w3.org/2000/svg") + "\n"
        svg_footer = "</svg>\n"

        nodes = "".join(node._svg(indent="  ") for node in self.nodes)
        return svg_header + nodes + svg_footer

    def _repr_svg_(self):
        return self.render()

    def __str__(self):
        return self.render()

    def __repr__(self):
        return "SVG:{self.nodes}"

class Point:
    """Creates a new Point.

    Point represents a point in the coordinate space and it contains
    attributes x and y.

        >>> p = Point(x=100, y=50)
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, p):
        return isinstance(p, Point) \
            and p.x == self.x \
            and p.y == self.y

    def __repr__(self):
        return f"Point({self.x}, {self.y})"

class Circle(Shape):
    """Creates a circle shape.

    Parameters:
        center:
            The center point of the circle.
            Defaults to Point(0, 0) when not specified.

        radius:
            The radius of the circle.
            Defaults to 100 when not specified.

    Examples:

    Draw a circle.

        >>> c = Circle()
        >>> show(c)

    Draw a Circle with radius 50.

        >>> c = Circle(radius=50)
        >>> show(c)

    Draw a circle with center at (100, 100) and radius as 50.

        >>> c = Circle(center=Point(x=100, y=100), radius=50)
        >>> show(c)

    When no arguments are specified, it uses (0, 0) as the center and
    100 as the radius.
    """
    def __init__(self, center=Point(0, 0), radius=100, **kwargs):
        self.center = center
        self.radius = radius

        cx, cy = self.center.x, self.center.y
        super().__init__("circle",
            cx=cx,
            cy=cy,
            r=self.radius,
            **kwargs)

class Ellipse(Shape):
    """Creates an ellipse shape.

    Parameters:
        center:
            The center point of the ellipse. Defaults to (0, 0) when
            not specified.

        width:
            The width of the ellipse. Defaults to 100 when not
            specified.

        height:
            The height of the ellipse. Defaults to 100 when not
            specified.

    Examples:

    Draw a ellipse with center at origin and width of 200 and height of 100:

        >>> r = Ellipse()
        >>> show(r)

    Draw a ellipse having a width of 100 and a height of 50.

        >>> r = Ellipse(width=100, height=50)
        >>> show(r)

    Draw a ellipse centered at (100, 100) and with a width
    of 200 and height of 100.

        >>> r = Ellipse(center=Point(x=100, y=100), width=200, height=100)
        >>> show(r)
    """
    def __init__(self, center=Point(0, 0), width=200, height=100, **kwargs):
        self.center = center
        self.width = width
        self.height = height

        cx, cy = self.center.x, self.center.y
        rx = width/2
        ry = height/2
        super().__init__(
            tag="ellipse",
            cx=cx,
            cy=cy,
            rx=rx,
            ry=ry,
            **kwargs)

class Rectangle(Shape):
    """Creates a rectangle shape.

    Parameters:
        center:
            The center point of the rectangle. Defaults to (0, 0) when
            not specified.

        width:
            The width of the rectangle. Defaults to 100 when not
            specified.

        height:
            The height of the rectangle. Defaults to 100 when not
            specified.

    Examples:

    Draw a rectangle:

        >>> r = Rectangle()
        >>> show(r)

    Draw a rectangle having a width of 200 and a height of 100.

        >>> r = Rectangle(width=200, height=100)
        >>> show(r)

    Draw a rectangle centered at (100, 100) and with a width
    of 200 and height of 100.

        >>> r = Rectangle(center=Point(x=100, y=100), width=200, height=100)
        >>> show(r)
    """
    def __init__(self, center=Point(0, 0), width=200, height=200, **kwargs):
        self.center = center
        self.width = width
        self.height = height

        cx, cy = self.center.x, self.center.y
        x = cx - width/2
        y = cy - height/2
        super().__init__(
            tag="rect",
            x=x,
            y=y,
            width=width,
            height=height,
            **kwargs)

class Line(Shape):
    """Basic shape for drawing a line connecting two points.

    Parameters:
        start:
            The starting point of the line. Defaults to (-100, 0) when
            not specified.

        end:
            The ending point of the line. Defaults to (100, 0) when not
            specified.

    Examples:

    Draw a line:

        >>> z = line()
        >>> show(z)

    Draw a line from (0, 0) to (100, 50).

        >>> z = line(start=Point(x=0, y=0), end=Point(x=100, y=50))
        >>> show(z)
    """
    def __init__(self, start=Point(-100, 0), end=Point(100, 0), **kwargs):
        self.start = start
        self.end = end

        x1, y1 = self.start.x, self.start.y
        x2, y2 = self.end.x, self.end.y

        super().__init__("line", x1=x1, y1=y1, x2=x2, y2=y2, **kwargs)

class Group(Shape):
    """Creates a container to group a list of shapes.

    This class is not meant for direct consumption of the users. Users
    are recommended to use `combine` to combine multiple shapes and use
    `translate`, `rotate` and `scale` for doing transformations.

    This creates an svg <g> element.

    Parameters:
        shapes:
            The list of shapes to group.

    Examples:

    Combine a circle and a rectangle.

        >> c = Circle()
        >> r = Rectangle()
        >>> shape = Group([c, r])
        >>> show(shape)

    Shapes can also be combined using the + operator and that creates
    a group implicitly.

        >>> shape = Circle() + Rectangle()
        >>> show(shape)
    """
    def __init__(self, shapes, **kwargs):
        super().__init__("g", children=shapes, **kwargs)

def render_tag(tag, *, close=False, **attrs):
    """Renders a html/svg tag.

        >>> render_tag("circle", cx=0, cy=0, r=10)
        '<circle cx="0" cy="0" r="10">'

    When `close=True`, the tag is closed with "/>".

        >>> render_tag("circle", cx=0, cy=0, r=10, close=True)
        '<circle cx="0" cy="0" r="10" />'

    Underscore characters in the attribute name are replaced with hypens.

        >>> render_tag("circle", cx=0, cy=0, r=10, stroke_width=2)
        '<circle cx="0" cy="0" r="10" stroke-width="2">'
    """
    end = " />" if close else ">"

    if attrs:
        items = [(k.replace("_", "-"), html.escape(str(v))) for k, v in attrs.items() if v is not None]
        attrs_text = " ".join(f'{k}="{v}"' for k, v in items)

        return f"<{tag} {attrs_text}{end}"
    else:
        return f"<{tag}{end}"

def combine(*shapes):
    """Combines multiple shapes in to a single shape by overlaying all
    the shapes.

        >>> shape = combine(circle(), rect())
        >>> show(shape)
    """
    return Group(shapes)

class Transformation:
    def apply(self, shape):
        return shape.apply_transform(self)

    def join(self, transformation):
        return TransformationList([self, transformation])

    def __or__(self, right):
        if not isinstance(right, Transformation):
            return NotImplemented
        return self.join(transformation=right)

    def __ror__(self, left):
        if not isinstance(left, Shape):
            return NotImplemented
        return self.apply(shape=left)

class TransformationList(Transformation):
    def __init__(self, transformations):
        self.transformations = transformations

    def join(self, transformation):
        return TransformationList(self.transformations + [transformation])

    def as_str(self):
        return " ".join(t.as_str() for t in self.transformations)

class Translate(Transformation):
    """Creates a new Translate transformation that moves a shape by
    x and y when applied.

    Parameters:
        x:
            The number of units to move in the x direction

        y:
            The number of units to move in the y direction

    Example:

    Translate a circle by (100, 50).

        >>> c = Circle() | Translate(100, 50)
        >>> show(c)
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def as_str(self):
        return f"translate({self.x} {self.y})"

class Rotate(Transformation):
    """Creates a new rotate transformation.

    When applied to a shape, it rotates the given shape by angle, around
    the anchor point.

    Parameters:

        angle:
            The angle to rotate the shape in degrees.

        anchor:
            The andhor point around which the rotation is performed.

    Examples:

    Rotates a square by 45 degrees.

        >>> shape = Rectangle() | Rotate(angle=45)
        >>> show(shape)

    Rotate a rectangle around it's top-left corner and
    combine with it self.

        >>> r1 = Rectangle()
        >>> r2 = r1 | Rotate(angle=45, anchor=(r.point[0]))
        >>> shape = combine(r1, r2)
        >>> show(shape)
    """
    def __init__(self, angle, anchor=Point(0, 0)):
        self.angle = angle
        self.anchor = anchor

    def as_str(self):
        origin = Point(0, 0)
        if self.anchor == origin:
            return f"rotate({self.angle})"
        else:
            return f"rotate({self.angle} {self.anchor.x} {self.anchor.y})"

class Scale(Transformation):
    """Creates a new scale transformation.

    Parameters:
        sx:
            The scale factor in the x direction.

        sy:
            The scale factor in the y direction. Defaults to
            the value of sx if not provided.
    """
    def __init__(self, sx, sy=None):
        if sy is None:
            sy = sx
        self.sx = sx
        self.sy = sy

    def as_str(self):
        return f"scale({self.sx} {self.sy})"

class Repeat(Transformation):
    """Repeat is a higher-order transformation that repeats a
    transformation multiple times.

    Parameters:
        n:
            The number of times to rotate. This also determines the
            angle of each rotation, which will be 360/n.

        transformation:
            The transfomation to apply repeatedly.

    Examples:

    Draw three circles:

        >>> shape = Circle(radius=25) | Repeat(4, Translate(x=50, y=0))
        >>> show(shape)

    Rotate a line multiple times:

        >>> shape = Line() | Repeat(36, Rotate(angle=10))
        >>> show(shape)

    Rotate and shrink a line multiple times:

        >>> shape = Line() | Repeat(18, Rotate(angle=10) | Scale(sx=0.9))
        >>> show(shape)
    """
    def __init__(self, n, transformation):
        self.n = n
        self.transformation = transformation

    def apply(self, shape):
        shapes = [shape]
        for i in range(self.n-1):
            shape = self.transformation.apply(shape)
            shapes.append(shape)
        return Group(shapes)

class Cycle(Transformation):
    """
    Rotates the given shape repeatedly and combines all the resulting
    shapes.

    The cycle function is very amazing transformation and it creates
    surprising patterns.

    Parameters:
        n:
            The number of times to rotate. This also determines the
            angle of each rotation, which will be 360/n.

        anchor:
            The anchor point for the rotation. Defaults to (0, 0) when
            not specified.

        s:
            Optional scale factor to scale the shape for each rotation.
            This can be used to grow or shrink the shape while rotating.

        angle:
            Optional angle of rotation. Defaults to 360/n when not
            specified,
    Examples:

    Cycle a line:

        >>> shape = Line() | Cycle()
        >>> show(shape)

    Cycle a square:

        >>> shape = Rectangle() | Cycle()
        >>> show(shape)

    Cycle a rectangle:

        >>> shape = Rectangle(width=200, height=100) | Cycle()
        >>> show(shape)

    Cycle an ellipse:

        >>> e = scale(Circle(), sx=1, sy=0.5)
        >>> show(e | Cycle())

    Create a spiral with shirnking squares:

        >>> shape = Rectangle(width=300, height=300) | cycle(n=72, s=0.92)
        >>> show(shape)
    """
    def __init__(self, n=18, anchor=Point(x=0, y=0), s=None, angle=None):
        self.n = n
        self.angle = angle if angle is not None else 360/n
        self.anchor = anchor
        self.s = s

    def apply(self, shape):
        shapes = [shape | Rotate(angle=i*self.angle, anchor=self.anchor) for i in range(self.n)]
        if self.s is not None:
            shapes = [shape_ | Scale(sx=self.s**i) for i, shape_ in enumerate(shapes)]
        return Group(shapes)

def show(*shapes):
    """Shows the given shapes.

    It also adds a border to the canvas and axis at the origin with
    a light color as a reference.

    Parameters:

        shapes:
            The shapes to show.

    Examples:

    Show a circle:

        >>> show(circle())

    Show a circle and square.

        >>> c = circle()
        >>> s = rect()
        >>> show(c, s)
    """
    markers = [
        Rectangle(width=300, height=300, stroke="#ddd"),
        Line(start=Point(x=-150, y=0), end=Point(x=150, y=0), stroke="#ddd"),
        Line(start=Point(x=0, y=-150), end=Point(x=0, y=150), stroke="#ddd")
    ]
    shapes = markers + list(shapes)
    img = SVG(shapes)

    from IPython.display import display
    display(img)
