import math
import itertools
import functools
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import Iterable, Tuple, Callable, Iterator

Point = Tuple[float, float]
Polygon = Tuple[Point, ...]
PolygonIterator = Iterable[Polygon]
TransformFunc = Callable[[Polygon], Polygon]
FilterFunc = Callable[[Polygon], bool]

def draw_polygons(polygon_iter, title = "", count = None,
                  show_axes= True, fill = False, ax=None) :

    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))

    num = count if count is not None else 1000
    polys = list(itertools.islice(polygon_iter, num))
    all_points = []
    for poly in polys:
        all_points.extend(poly)
        patch = patches.Polygon(poly, closed=True, fill=fill,
                                edgecolor='black', linewidth=1.5, alpha=0.7)
        ax.add_patch(patch)

    if all_points:
        xs, ys = zip(*all_points)
        margin = 1.0
        ax.set_xlim(min(xs) - margin, max(xs) + margin)
        ax.set_ylim(min(ys) - margin, max(ys) + margin)

    ax.set_aspect('equal')
    ax.set_title(title, fontsize=12)

    if show_axes:
        ax.spines['left'].set_position('zero')
        ax.spines['bottom'].set_position('zero')
        ax.spines['left'].set_color('gray')
        ax.spines['bottom'].set_color('gray')
        ax.spines['right'].set_color('none')
        ax.spines['top'].set_color('none')
        ax.xaxis.set_ticks([])
        ax.yaxis.set_ticks([])
      
        ax.annotate('', xy=(ax.get_xlim()[1], 0), xytext=(0, 0),
                    arrowprops=dict(arrowstyle='->', color='gray'))
        ax.annotate('', xy=(0, ax.get_ylim()[1]), xytext=(0, 0),
                    arrowprops=dict(arrowstyle='->', color='gray'))
    else:
        ax.axis('off')

    if ax is None:
        plt.show()
    else:
        return ax

def polygon_area(poly):
    n = len(poly)
    area = 0.0
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        area += x1 * y2 - x2 * y1
    return abs(area) / 2.0

def polygon_perimeter(poly):
    n = len(poly)
    per = 0.0
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        per += math.hypot(x2 - x1, y2 - y1)
    return per

def side_lengths(poly):
    n = len(poly)
    return [math.hypot(poly[(i+1)%n][0]-poly[i][0], poly[(i+1)%n][1]-poly[i][1]) for i in range(n)]

def shortest_side(poly):
    return min(side_lengths(poly))

def is_convex(poly):
    n = len(poly)
    if n < 3:
        return False
    prev_sign = 0
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i+1)%n]
        x3, y3 = poly[(i+2)%n]
        cross = (x2-x1)*(y3-y2) - (y2-y1)*(x3-x2)
        if abs(cross) < 1e-9:
            continue
        sign = 1 if cross > 0 else -1
        if prev_sign == 0:
            prev_sign = sign
        elif sign != prev_sign:
            return False
    return True

def point_inside_convex(point, poly):
    n = len(poly)
    px, py = point
    signs = []
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i+1)%n]
        cross = (x2-x1)*(py-y1) - (y2-y1)*(px-x1)
        if abs(cross) > 1e-9:
            signs.append(cross > 0)
    return all(signs) or not any(signs) if signs else True

def gen_zigzag_indices():
    for i in itertools.count(0):
        if i == 0:
            yield 0
        else:
            yield i
            yield -i

def gen_rectangle(w = 1.2, h = 0.8, gap= 0.2):
    step = w + gap
    for k in gen_zigzag_indices():
        x0 = k * step
        yield ((x0, 0.0), (x0 + w, 0.0), (x0 + w, h), (x0, h))

def gen_triangle(base = 1.2, height= 1.0):
    for k in gen_zigzag_indices():
        x0 = k * base
        yield ((x0, 0.0), (x0 + base, 0.0), (x0 + base/2, height))

def gen_hexagon(r = 0.7):
    angles = [i * math.pi/3 for i in range(6)]
    for k in gen_zigzag_indices():
        cx = 2 * r * k
        verts = [(cx + r * math.cos(a), r * math.sin(a)) for a in angles]
        yield tuple(verts)

def tr_translate(dx, dy):
    def transform(poly):
        return tuple((x + dx, y + dy) for x, y in poly)
    return transform

def tr_rotate(angle_rad, cx = 0.0, cy = 0.0):
    cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)
    def transform(poly):
        res = []
        for x, y in poly:
            xr = cx + (x - cx) * cos_a - (y - cy) * sin_a
            yr = cy + (x - cx) * sin_a + (y - cy) * cos_a
            res.append((xr, yr))
        return tuple(res)
    return transform

def tr_symmetry(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    dx, dy = x2 - x1, y2 - y1
    mag2 = dx*dx + dy*dy
    if mag2 < 1e-9:
        return lambda poly: poly
    def transform(poly):
        new_verts = []
        for x, y in poly:
            ux, uy = x - x1, y - y1
            t = (ux*dx + uy*dy) / mag2
            px = x1 + t * dx
            py = y1 + t * dy
            rx = 2*px - x
            ry = 2*py - y
            new_verts.append((rx, ry))
        return tuple(new_verts)
    return transform

def tr_homothety(scale, cx = 0.0, cy = 0.0):
    def transform(poly):
        return tuple((cx + scale*(x - cx), cy + scale*(y - cy)) for x, y in poly)
    return transform

def flt_convex_polygon(poly):
    return is_convex(poly)

def flt_square(max_area):
    return lambda poly: polygon_area(poly) < max_area

def flt_short_side(max_len):
    return lambda poly: shortest_side(poly) < max_len

def flt_point_inside(point):
    return lambda poly: is_convex(poly) and point_inside_convex(point, poly)

def flt_angle_point(point):
    def _filter(poly):
        eps = 1e-9
        return any(abs(x - point[0]) < eps and abs(y - point[1]) < eps for x, y in poly)
    return _filter

def flt_polygon_angles_inside(other_poly):
    def _filter(poly):
        if not is_convex(poly):
            return False
        return any(point_inside_convex(v, poly) for v in other_poly)
    return _filter

def filtering_decorator(filter_func):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not args:
                raise TypeError("Функция должна принимать итератор первым аргументом")
            iterable = args[0]
            filtered_iter = filter(filter_func, iterable)
            return func(filtered_iter, *args[1:], **kwargs)
        return wrapper
    return decorator

def transforming_decorator(transform_func):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not args:
                raise TypeError("Функция должна принимать итератор первым аргументом")
            iterable = args[0]
            transformed_iter = map(transform_func, iterable)
            return func(transformed_iter, *args[1:], **kwargs)
        return wrapper
    return decorator

flt_convex_polygon_decorator = filtering_decorator(flt_convex_polygon)
flt_angle_point_decorator = lambda point: filtering_decorator(flt_angle_point(point))
flt_square_decorator = lambda max_area: filtering_decorator(flt_square(max_area))
flt_short_side_decorator = lambda max_len: filtering_decorator(flt_short_side(max_len))
flt_point_inside_decorator = lambda point: filtering_decorator(flt_point_inside(point))
flt_polygon_angles_inside_decorator = lambda other_poly: filtering_decorator(flt_polygon_angles_inside(other_poly))

tr_translate_decorator = lambda dx, dy: transforming_decorator(tr_translate(dx, dy))
tr_rotate_decorator = lambda angle, cx=0.0, cy=0.0: transforming_decorator(tr_rotate(angle, cx, cy))
tr_symmetry_decorator = lambda p1, p2: transforming_decorator(tr_symmetry(p1, p2))
tr_homothety_decorator = lambda scale, cx=0.0, cy=0.0: transforming_decorator(tr_homothety(scale, cx, cy))

def agr_max_side(poly_iter):
    return functools.reduce(lambda max_val, poly: max(max_val, max(side_lengths(poly))), poly_iter, 0.0)

def agr_min_area(poly_iter):
    return functools.reduce(lambda min_val, poly: min(min_val, polygon_area(poly)), poly_iter, float('inf'))

def agr_perimeter(poly_iter) :
    return functools.reduce(lambda total, poly: total + polygon_perimeter(poly), poly_iter, 0.0)

def agr_area(poly_iter):
    return functools.reduce(lambda total, poly: total + polygon_area(poly), poly_iter, 0.0)

def agr_origin_nearest(poly_iter):
    def nearest_in_poly(poly):
        return min(poly, key=lambda p: math.hypot(p[0], p[1]))
    best = functools.reduce(lambda best_pt, poly: min(best_pt, nearest_in_poly(poly), key=lambda p: math.hypot(p[0], p[1])),
                            poly_iter, (float('inf'), float('inf')))
    return best

def zip_polygons(*iterators):
    for polys in zip(*iterators):
        yield functools.reduce(lambda a, b: a + b, polys)

if __name__ == "__main__":
    rect_stream = gen_rectangle(w=1.2, h=0.8, gap=0.2)
    draw_polygons(rect_stream, title="а) Последовательность прямоугольников ", count=7)

    triangle_stream = gen_triangle(base=1.2, height=1.0)
    draw_polygons(triangle_stream, title="б) Последовательность треугольников ", count=7)

    hexagon_stream = gen_hexagon(r=0.7)
    draw_polygons(hexagon_stream, title="в) Последовательность шестиугольников", count=7)

    base_rects = list(itertools.islice(gen_rectangle(0.8, 0.4, 0.5), 6))
    angle30 = math.radians(30)
    ribbon1 = map(tr_rotate(angle30), base_rects)
    ribbon2 = map(tr_translate(1.5, 2.0), map(tr_rotate(angle30), base_rects))
    ribbon3 = map(tr_translate(-1.5, -2.0), map(tr_rotate(angle30), base_rects))
    all_ribbons = itertools.chain(ribbon1, ribbon2, ribbon3)
    draw_polygons(all_ribbons, title="Три параллельные ленты (угол 30°)", count=18, show_axes=True)

    base_rects2 = list(itertools.islice(gen_rectangle(1.0, 0.3, 0.8), 5))
    ribbonA = map(tr_translate(0, 1.5), base_rects2)
    ribbonB = map(tr_translate(1, 1), map(tr_rotate(math.radians(60)), base_rects2))
    cross_ribbons = itertools.chain(ribbonA, ribbonB)
    draw_polygons(cross_ribbons, title="Две пересекающиеся ленты", count=10, show_axes=True)

    base_tris = list(itertools.islice(gen_triangle(1.0, 1.2), 5))
    top_ribbon = map(tr_translate(0, 2.0), base_tris)
    bottom_ribbon = map(tr_translate(0, -2.0), map(tr_symmetry((0,0), (1,0)), base_tris))
    sym_tris = itertools.chain(top_ribbon, bottom_ribbon)
    draw_polygons(sym_tris, title="Симметричные ленты треугольников", count=10, show_axes=True)

    def make_quad_at_distance(dist, size_factor = 0.3):
      half_side = size_factor * dist / 2
      cx, cy = dist, dist
      return ((cx - half_side, cy - half_side),
                (cx + half_side, cy - half_side),
                (cx + half_side, cy + half_side),
                (cx - half_side, cy + half_side))

    distances = [0.6, 1.2, 1.8, 2.4, 3.0]
    quads = []
    for d in distances:
        quads.append(make_quad_at_distance(d, size_factor=0.3))   
        quads.append(make_quad_at_distance(-d, size_factor=0.3))  

    fig, ax = plt.subplots(figsize=(8, 8))
    draw_polygons(iter(quads), title="Четырёхугольники вдоль y=x",
                  show_axes=True, ax=ax)

    x_vals = [-3.5, -2.5, -1.5, -0.5, 0.5, 1.5, 2.5, 3.5]
    ax.plot(x_vals, x_vals, 'r--', linewidth=1, alpha=0.7)
    ax.legend()
    plt.show()

    polygons_mixed = [
        ((0,0), (2,0), (2,1), (0,1)),          
        ((0,0), (1,0), (1,1), (0,1)),          
        ((0,0), (2,0), (1,1), (2,2), (0,2)),   
        ((0,0), (3,0), (1.5, 2)),             
        ((0,0), (2,0), (1,1), (2,2), (0,2), (1,1)) 
    ]
    convex_polys = list(filter(flt_convex_polygon, polygons_mixed))
    print(f"flt_convex_polygon: из {len(polygons_mixed)} фигур выпуклых: {len(convex_polys)}")
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    draw_polygons(iter(polygons_mixed), title="Исходные (выпуклые + невыпуклые)", show_axes=True, ax=axes[0])
    draw_polygons(iter(convex_polys), title="Только выпуклые", show_axes=True, ax=axes[1])
    plt.tight_layout()
    plt.show()

    polys_area = [
        ((0,0), (2,0), (2,2), (0,2)),   
        ((0,0), (1,0), (1,1), (0,1)),   
        ((0,0), (3,0), (1.5, 2)),       
        ((0,0), (1.5,0), (1.5,1.5), (0,1.5)), 
        ((0,0), (0.5,0), (0.5,0.5), (0,0.5))  
    ]
    max_area = 2.0
    small_area_polys = list(filter(flt_square(max_area), polys_area))
    print(f"flt_square(max_area={max_area}): из {len(polys_area)} фигур с площадью < {max_area}: {len(small_area_polys)}")
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    draw_polygons(iter(polys_area), title="Исходные (разная площадь)", show_axes=True, ax=axes[0])
    draw_polygons(iter(small_area_polys), title=f"Площадь < {max_area}", show_axes=True, ax=axes[1])
    plt.tight_layout()
    plt.show()

    scales_side = [0.3, 0.5, 0.7, 0.9, 1.1, 1.3, 1.5, 2.0]
    squares_side = [tr_homothety(s)(((0,0),(1,0),(1,1),(0,1))) for s in scales_side]
    max_len = 0.8
    short_side_polys = list(filter(flt_short_side(max_len), squares_side))
    print(f"flt_short_side(max_len={max_len}): из {len(squares_side)} квадратов с короткой стороной < {max_len}: {len(short_side_polys)}")
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    draw_polygons(iter(squares_side), title="Исходные квадраты разного размера", show_axes=True, ax=axes[0])
    draw_polygons(iter(short_side_polys), title=f"Короткая сторона < {max_len}", show_axes=True, ax=axes[1])
    plt.tight_layout()
    plt.show()
  
    test_point = (0.6, 0.6)
    polygons_point = [
        ((0,0), (1,0), (1,1), (0,1)),        
        ((0.5,0.5), (1.5,0.5), (1.5,1.5), (0.5,1.5)), 
        ((0,0), (2,0), (1,1)),               
        ((1,0), (2,0), (2,1), (1,1)),        
        ((0,0), (0.5,0), (0.5,0.5), (0,0.5)) 
    ]
  
    inside_polys = list(filter(flt_point_inside(test_point), polygons_point))
    print(f"flt_point_inside(point={test_point}): из {len(polygons_point)} фигур содержат точку: {len(inside_polys)}")
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    draw_polygons(iter(polygons_point), title="Исходные полигоны", show_axes=True, ax=axes[0])
    draw_polygons(iter(inside_polys), title=f"Содержат точку {test_point}", show_axes=True, ax=axes[1])

    for ax in axes:
        ax.plot(test_point[0], test_point[1], 'ro', markersize=8)
    plt.tight_layout()
    plt.show()

    convex = list(filter(flt_convex_polygon, polygons_mixed))
    small_area = list(filter(flt_square(2.0), polygons_mixed))
    short_side = list(filter(flt_short_side(0.8), polygons_mixed))
    has_origin = list(filter(flt_angle_point((0,0)), polygons_mixed))
    inside = list(filter(flt_point_inside((1,1)), polygons_mixed))
    outer_square = ((0,0),(3,0),(3,3),(0,3))
    contains_vertex = list(filter(flt_polygon_angles_inside(outer_square), polygons_mixed))

    print(f"1. Выпуклые: {len(convex)} из {len(polygons_mixed)}")
    print(f"2. Площадь < 2.0: {len(small_area)} фигур")
    print(f"3. Короткая сторона < 0.8: {len(short_side)} фигур")
    print(f"4. Содержат точку (1,1): {len(inside)} фигур")
    print(f"5. Имеют вершину (0,0): {len(has_origin)} фигур")
    print(f"6. Содержат вершины внешнего квадрата: {len(contains_vertex)} фигур")


    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    filters_data = [
        ("Выпуклые", convex, polygons_mixed),
        ("Площадь < 2.0", small_area, polygons_mixed),
        ("Короткая сторона < 0.8", short_side, polygons_mixed),
        ("Содержат (1,1)", inside, polygons_mixed),
        ("Имеют вершину (0,0)", has_origin, polygons_mixed),
        ("Содержат вершины квадрата", contains_vertex, polygons_mixed)
    ]
    colors = ['blue', 'green', 'red', 'purple', 'orange', 'brown']
    for idx, (title, filtered, original) in enumerate(filters_data):
        ax = axes[idx//3, idx%3]
        for poly in original:
            ax.add_patch(patches.Polygon(poly, closed=True, fill=False, edgecolor='lightgray', lw=1))
        for poly in filtered:
            ax.add_patch(patches.Polygon(poly, closed=True, fill=False, edgecolor=colors[idx], lw=2))
        ax.set_title(title)
        ax.set_aspect('equal')
        ax.set_xlim(-1, 4)
        ax.set_ylim(-1, 4)
        ax.axhline(0, color='gray', lw=0.5)
        ax.axvline(0, color='gray', lw=0.5)
    plt.tight_layout()
    plt.show()

    print("\nАгрегирующие функции\n")

    demo_polys = [
        ((0,0), (2,0), (2,1), (0,1)),        
        ((1,1), (3,1), (2,2)),               
        ((0,0), (1,0), (1,1), (0,1)),       
        ((2,2), (4,2), (4,4), (2,4))          
    ]
    
    print(f"Исходные полигоны: {len(demo_polys)} шт.")
    print(f"Ближайшая к (0,0) вершина: {agr_origin_nearest(iter(demo_polys))}")
    print(f"Максимальная длина стороны: {agr_max_side(iter(demo_polys)):.3f}")
    print(f"Минимальная площадь: {agr_min_area(iter(demo_polys)):.3f}")
    print(f"Суммарный периметр: {agr_perimeter(iter(demo_polys)):.3f}")
    print(f"Суммарная площадь: {agr_area(iter(demo_polys)):.3f}")

    def collect(poly_iter):
        return list(poly_iter)

    demo_polys = [
        ((0,0), (2,0), (2,2), (0,2)),         
        ((0,0), (1,0), (1,1), (0,1)),          
        ((0,0), (3,0), (1.5,2)),              
        ((0,0), (2,0), (1,1), (2,2), (0,2)),  
        ((0,0), (2,0), (2,1), (1,1), (0,1))   
    ]
    print("\nИсходные полигоны для фильтрации:")
    for i, p in enumerate(demo_polys):
        print(f"  {i}: {p}")
    
    @flt_convex_polygon_decorator
    def get_convex(poly_iter):
        return list(poly_iter)
    convex = get_convex(iter(demo_polys))
    print(f"\n1. @flt_convex_polygon_decorator -> оставлены выпуклые: {len(convex)} шт. Индексы: {[demo_polys.index(p) for p in convex]}")

    @flt_angle_point_decorator((0,0))
    def has_origin(poly_iter):
        return list(poly_iter)
    origin_polys = has_origin(iter(demo_polys))
    print(f"2. @flt_angle_point_decorator((0,0)) -> имеют вершину (0,0): {len(origin_polys)} шт. Индексы: {[demo_polys.index(p) for p in origin_polys]}")

    @flt_square_decorator(2.0)
    def small_area(poly_iter):
        return list(poly_iter)
    area_polys = small_area(iter(demo_polys))
    print(f"3. @flt_square_decorator(2.0) -> площадь < 2: {len(area_polys)} шт. Индексы: {[demo_polys.index(p) for p in area_polys]}")

    @flt_short_side_decorator(0.8)
    def short_side(poly_iter):
        return list(poly_iter)
    short_polys = short_side(iter(demo_polys))
    print(f"4. @flt_short_side_decorator(0.8) -> короткая сторона < 0.8: {len(short_polys)} шт. Индексы: {[demo_polys.index(p) for p in short_polys]}")

    @flt_point_inside_decorator((1,1))
    def contains_point(poly_iter):
        return list(poly_iter)
    point_polys = contains_point(iter(demo_polys))
    print(f"5. @flt_point_inside_decorator((1,1)) -> содержат (1,1): {len(point_polys)} шт. Индексы: {[demo_polys.index(p) for p in point_polys]}")

    @flt_polygon_angles_inside_decorator(((0,0),(3,0),(3,3),(0,3)))
    def contains_vertex(poly_iter):
        return list(poly_iter)
    vertex_polys = contains_vertex(iter(demo_polys))
    print(f"6. @flt_polygon_angles_inside_decorator(внешний квадрат) -> содержат его вершины: {len(vertex_polys)} шт. Индексы: {[demo_polys.index(p) for p in vertex_polys]}")
    source_tri = ((0,0), (2,0), (1,1.5))
    print(f"\nИсходный полигон для трансформаций: {source_tri}")

    @tr_translate_decorator(1, -1)
    def translate(poly_iter):
        return list(poly_iter)
    translated = translate(iter([source_tri]))[0]
    print(f"7. @tr_translate_decorator(1, -1) -> {translated}")

    @tr_rotate_decorator(math.radians(45))
    def rotate(poly_iter):
        return list(poly_iter)
    rotated = rotate(iter([source_tri]))[0]
    print(f"8. @tr_rotate_decorator(45°) -> {rotated}")

    @tr_symmetry_decorator((0,0), (1,0))
    def symmetry(poly_iter):
        return list(poly_iter)
    sym = symmetry(iter([source_tri]))[0]
    print(f"9. @tr_symmetry_decorator(ось X) -> {sym}")

    @tr_homothety_decorator(1.5)
    def homothety(poly_iter):
        return list(poly_iter)
    hom = homothety(iter([source_tri]))[0]
    print(f"10. @tr_homothety_decorator(1.5) -> {hom}")

    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    transforms = [
        ("трансляция (1,-1)", source_tri, translated),
        ("ротация 45°", source_tri, rotated),
        ("симметрия (ось X)", source_tri, sym),
        ("увеличение 1.5", source_tri, hom)
    ]
    for i, (title, orig, trans) in enumerate(transforms):
        ax = axes[i//2, i%2]
        ax.add_patch(patches.Polygon(orig, closed=True, fill=False, edgecolor='blue', lw=2, label='исходный'))
        ax.add_patch(patches.Polygon(trans, closed=True, fill=False, edgecolor='red', lw=2, label='преобразованный'))
        ax.set_title(title)
        ax.set_aspect('equal')
        ax.set_xlim(-2, 3)
        ax.set_ylim(-2, 3)
        ax.axhline(0, color='gray', lw=0.5)
        ax.axvline(0, color='gray', lw=0.5)
        ax.legend()
    plt.tight_layout()
    plt.show()

    areas = [polygon_area(p) for p in demo_polys]
    perimeters = [polygon_perimeter(p) for p in demo_polys]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    ax1.bar(range(len(areas)), areas, color='green', alpha=0.7)
    ax1.set_title('Площади отдельных полигонов')
    ax1.set_xlabel('№ полигона')
    ax1.set_ylabel('Площадь')
    ax2.bar(range(len(perimeters)), perimeters, color='orange', alpha=0.7)
    ax2.set_title('Периметры отдельных полигонов')
    ax2.set_xlabel('№ полигона')
    ax2.set_ylabel('Периметр')
    plt.suptitle(f'Суммарная площадь = {agr_area(iter(demo_polys)):.2f},  Суммарный периметр = {agr_perimeter(iter(demo_polys)):.2f}')
    plt.tight_layout()
    plt.show()
    
    it1 = iter([((1,1),(2,2),(3,1)), ((11,11),(12,12),(13,11))])
    it2 = iter([((1,-1),(2,-2),(3,-1)), ((11,-11),(12,-12),(13,-11))])

    zipped = zip_polygons(it1, it2)
    result_polygons = list(zipped)

    for poly in result_polygons:
        print(poly)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))

    tri_up = ((1,1),(2,2),(3,1))
    tri_down = ((1,-1),(2,-2),(3,-1))
    ax1.add_patch(patches.Polygon(tri_up, closed=True, fill=False, edgecolor='blue', lw=2))
    ax1.add_patch(patches.Polygon(tri_down, closed=True, fill=False, edgecolor='red', lw=2))
    ax1.set_title("Исходные треугольники")
    ax1.set_aspect('equal')

    merged = result_polygons[0]
    ax2.add_patch(patches.Polygon(merged, closed=True, fill=False, edgecolor='green', lw=2))
    ax2.set_aspect('equal')

    for ax in (ax1, ax2):
        ax.set_xlim(0, 4)
        ax.set_ylim(-2.5, 2.5)
        ax.axhline(0, color='gray', lw=0.5)
        ax.axvline(0, color='gray', lw=0.5)

    plt.suptitle("Пример склейки полигонов")
    plt.show()
