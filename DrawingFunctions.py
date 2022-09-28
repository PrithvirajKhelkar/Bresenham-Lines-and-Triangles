from Point import Point
from ColorType import ColorType

# UTILITY FUNCTIONS

def add_colors(c1, c2, ratio):
    """
    Add two colors using a ratio c1:c2
    Returns the new color.

    :param c1: color 1
    :type c1: ColorType
    :param c2: color 2
    :type c2: ColorType
    :param ratio: a value between [0, 1].
    :type ratio: float
    """
    r1, g1, b1 = c1.getRGB()
    r2, g2, b2 = c2.getRGB()

    r, g, b = r1*(1-ratio) + r2*ratio, g1*(1-ratio) + g2*ratio, b1*(1-ratio) + b2*ratio

    return ColorType(r, g, b)

def interpolate_color(n, m, c1, c2):
    """
    Interpolate colors c1 c2 to a point, such that the point is  between them.
    Returns the new color

    :param n: n units from color 1
    :type n: float
    :param m: m units from color 2
    :type m: float
    :param c1: color 1
    :type c1: ColorType
    :param c2: color 2
    :type c2: ColorType
    """
    t = n/m
    return add_colors(c1, c2, t)

def distance(x1, y1, x2, y2):
    """
    Distance between two points.

    :param x1: X coordinate of point 1
    :type x1: int
    :param y1: Y coordinate of point 1
    :type y1: int
    :param x2: X coordinate of point 2
    :type x2: int
    :param y2: Y coordinate of point 2
    :type y2: int
    """
    return abs(((x2 - x1)**2 + (y2 - y1)**2)**0.5)

def interpolate_texture(x, y, config):
    """
    Get the texture value at point x, y

    :param x: X coordinate
    :type x: int
    :param y: Y coordinate
    :type y: int
    :param config: a dict including the bounding box dimensions
    :type config: dict
    """
    texture = config.get('texture', None)
    x_max = config.get('x_max', None)
    x_min = config.get('x_min', None)
    y_max = config.get('y_max', None)
    y_min = config.get('y_min', None)
    if texture and x_max and x_min and y_max and y_min:
        texture_width = texture.width
        texture_height = texture.height

        t_x = int(((x - x_min)*(texture_width - 1)/(x_max - x_min)))
        t_y = int(((y - y_min)*(texture_height - 1)/(y_max - y_min)))
        return texture.getPoint(t_x, t_y).color
    return ColorType(0, 0, 0)

def SS_modifier(value):
    """
    Super sampling function to modify the ratio
    between the color and the background color.
    Example, value = sin(value)
    Returns the modified value.

    :param value: value between [0, 1]
    :type value: float
    """
    return value

def anti_aliasing(buff, color, x, y, x0, y0, dx, dy, AAlevel):
    """
    Anti-aliasing on AAlevel.
    TODO
    """
    step = 1/AAlevel
    aa = 0
    if dy > dx:
        for i in range(0, AAlevel):
            x_actual = x0 + ((y + (i*step) - y0)*dx/dy)
            if x_actual >= x and x_actual < x + 1:
                aa += 1
    else:
        for i in range(0, AAlevel):
            y_actual = y0 + ((x + (i*step) - x0)*dy/dx)
            print(x, y, x+i*step, y_actual)
            if y_actual >= y and y_actual < y + 1:
                aa += 1
    background_color = buff.getPoint(x, y).color
    return add_colors(background_color, color, SS_modifier(aa/AAlevel))

def iterate(iterable):
    """
    Function to iterate over an iterator without executing any callbacks.
    """
    for _ in iterable:
        continue

def peek(iterable):
    """
    Function to handle StopIterable exception.
    Returns a value or None.
    """
    try:
        value = next(iterable)
    except StopIteration:
        return None
    return value

def validate_triangle_points(p1, p2, p3):
    """
        Function to validate triangle vertices.
        Sum of two sides should be greater than the third side.
        Raises ValueError if False.

        :param p1: vertex 1
        :type p1: Point
        :param p2: vertex 2
        :type p2: Point
        :param p3: vertex 3
        :type p3: Point
    """
    x1, y1 = p1.coords
    x2, y2 = p2.coords
    x3, y3 = p3.coords
    s1 = distance(x1, y1, x2, y2)
    s2 = distance(x2, y2, x3, y3)
    s3 = distance(x1, y1, x3, y3)

    if s1 < s2 + s3 and s2 < s1 + s3 and s3 < s3 + s1:
        return
    else:
        raise ValueError('The three vertices don\'t form a triangle')

# DRAWING FUNCTIONS

def bresenhams_line(buff, drawPoint, p1, p2, config):
    """
    A generator function implementing Bresenham's algorithm to draw a line.

    :param buff: a buff to draw on
    :type buff: Buff
    :param drawPoint: a function to plot a point with color
    :type drawPoint: function
    :param p1: starting point of the line
    :type p1: Point
    :param p2: end point of the line
    :type p2: Point
    :param config: a dict with config variables
    :type config: dict
    """
    x0, y0 = p1.coords
    x1, y1 = p2.coords
    xk, yk = x0, y0

    # flag to indicate if the slope <= 1
    slope_leq_1 = True

    dy = abs(y1 - y0)
    dx = abs(x1 - x0)

    if dy > dx :
        """
            If slope is > 1, interchange values. 
            To increment along the y axis instead.
        """
        dx, dy = dy, dx
        slope_leq_1 = False

    c1 = 2*dy
    c2 = 2*dy - 2*dx
    p = c1 - dx
    for i in range(0, dx, 1):
        color = interpolate_color(i, dx+1, p1.color, p2.color) if (config.get('doSmooth',
            False) and not config.get('doTexture',
            False)) else config.get('first_vertex_color', p1.color)
        if config.get('doTexture', False):
            color = interpolate_texture(xk, yk, config)

        # aaColor = color
        # if config.get('doAA', False) and config.get('doAAlevel', 0):
        #     aaColor = anti_aliasing(buff, color, xk, yk, x0, y0, abs(x1 - x0),
        #  abs(y1 - y0), config.get('doAAlevel', 1))

        
        drawPoint(buff, Point((xk, yk), color))
        yield Point((xk, yk), color)
        if p < 0:
            # plot (x +- 1, y) or (x, y +- 1)
            if slope_leq_1:
                xk = xk + 1 if xk < x1 else xk - 1
            else:
                yk = yk + 1 if yk < y1 else yk - 1
            p = p + c1
        else:
            # plot (x +- 1, y +- 1)
            xk = xk + 1 if xk < x1 else xk - 1
            yk = yk + 1 if yk < y1 else yk - 1
            p = p + c2
    return

def sketch_line(buff, drawPoint, p1, p2, config):
    """
    Function to draw a line.

    :param buff: a buff to draw on
    :type buff: Buff
    :param drawPoint: a function to plot a point with color
    :type drawPoint: function
    :param p1: starting point of the line
    :type p1: Point
    :param p2: end point of the line
    :type p2: Point
    :param config: a dict with config variables
    :type config: dict
    """
    iterate(bresenhams_line(buff, drawPoint, p1, p2, config))
    return


def sketch_triangle(buff, drawPoint, p1, p2, p3, config):
    """
    Function to draw a triangle.

    :param buff: a buff to draw on
    :type buff: Buff
    :param drawPoint: a function to plot a point with color
    :type drawPoint: function
    :param p1: first point of the triangle
    :type p1: Point
    :param p2: second point of the triangle
    :type p2: Point
    :param p3: third point of the triangle
    :type p3: Point
    :param config: a dict with config variables
    :type config: dict
    """
    validate_triangle_points(p1, p2, p3)

    points = [p1, p2, p3]

    # sorting the points by their y values, in ascending order.
    points.sort(key = lambda point: point.coords[1])

    # saving the first vertex color, for lines and triangle with doSmooth=False
    config['first_vertex_color'] = p1.color

    # calculate the bounding box dimensions for the triangle. Used for texture mapping
    if config.get('doTexture', False) and config.get('texture', None):
        config['y_max'] = points[2].coords[1]
        config['y_min'] = points[0].coords[1]

        config['x_max'] = max(p1.coords[0], p2.coords[0], p3.coords[0])
        config['x_min'] = min(p1.coords[0], p2.coords[0], p3.coords[0])

    # iterables for the three lines in the triangle.
    line_1 = bresenhams_line(buff, drawPoint, points[0], points[1], config)
    line_2 = bresenhams_line(buff, drawPoint, points[0], points[2], config)
    line_3 = bresenhams_line(buff, drawPoint, points[1], points[2], config)

    # flag which is turned True when the triangle split point is reached
    split = False

    # starting with line 1 and line 2
    first = line_1
    second = line_2

    first_point, second_point = next(first), next(second)

    # run the loop as long as one of the two iterators hasn't exhausted itself
    while first_point or second_point:
        # if both points are none, end the loop
        if first_point == None and second_point == None:
            break
        # if the first point is none and split is false, switch the iterator
        elif first_point == None:
            if split:
                break
            first = line_3
            first_point = next(first)
            split = True

        # if the second point is none and split is false, switch the iterator
        elif second_point == None:
            if split:
                break
            second = line_3
            second_point = next(second)
            split = True

        # when the y values in both points are equal, draw a line using bresenhams func.
        # the line would be parallel to the x axis.
        if(first_point.coords[1] == second_point.coords[1]):
            # draw the y = c line
            iterate(bresenhams_line(buff, drawPoint, first_point, second_point,
                {  **config, 'doAA': False } ))
            first_point = peek(first)
            second_point = peek(second)

        # if the first point's y is less than the second, move up the first iterator
        elif first_point.coords[1] < second_point.coords[1]:
            # move up the left iterator
            first_point = peek(first)
        # if the second point's y is less than the first, move up the second iterator
        else:
            # move up the right iterator
            second_point = peek(second)
