import random
from math import sin, cos, pi, log
from tkinter import *

CANVAS_WIDTH = 640
CANVAS_HEIGHT = 480
CANVAS_CENTER_X = CANVAS_WIDTH / 2
CANVAS_CENTER_Y = CANVAS_HEIGHT / 2
IMAGE_ENLARGE = 11  # 图像放大
HEART_COLOR = "#FF99CC"


def heart_function(t, shrink_ratio: float = IMAGE_ENLARGE):  # (t  ，  shrink_ratio = float  ，  IMAGE_ENLARGE)
    # 爱心曲线公式
    x = 16 * (sin(t) ** 3)  # ** 幂 次方
    y = -(13 * cos(t) - 5 * cos(2 * t) - 2 * cos(3 * t) - cos(4 * t))
    # 放大
    x *= shrink_ratio  # 收缩率
    y *= shrink_ratio
    # 移到画布中央
    x += CANVAS_CENTER_X
    y += CANVAS_CENTER_Y
    return int(x), int(y)


# 内部散射
def scatter_inside(x, y, beta=0.15):
    # log(x)：返回 x 的自然对数（底数为e）
    # log(x, base)：返回以base为基的x的对数。base默认为e，也可以手动输入
    ratio_x = - beta * log(random.random())
    ratio_y = - beta * log(random.random())
    dx = ratio_x * (x - CANVAS_CENTER_X)
    dy = ratio_y * (y - CANVAS_CENTER_Y)
    return x - dx, y - dy


def shrink(x, y, ratio):
    force = -1 / (((x - CANVAS_CENTER_X) ** 2 + (y - CANVAS_CENTER_Y) ** 2) ** 0.6)
    dx = ratio * force * (x - CANVAS_CENTER_X)
    dy = ratio * force * (y - CANVAS_CENTER_Y)
    return x - dx, y - dy


# 曲线
def curve(p):
    return 2 * (2 * sin(4 * p)) / (2 * pi)


class Heart:
    def __init__(self, generate_frame=20):
        # set() 函数：创建一个无序不重复元素集，可进行关系测试，删除重复数据，还可以计算交集、差集、并集等
        self._points = set()  # 原始爱心坐标集合
        self._edge_diffusion_points = set()  # 边缘扩散效果点坐标集合
        self._center_diffusion_points = set()  # 中心扩散效果点坐标集合
        self.all_points = {}  # 每帧动态点坐标
        self.build(2000)
        self.random_halo = 1000
        # 生成帧
        self.generate_frame = generate_frame
        for frame in range(generate_frame):
            self.calc(frame)

    def build(self, number):
        # range() 函数可创建一个整数列表 range(计数从start开始, 计数到stop结束[, step步长，默认为1])
        for _ in range(number):
            # 随机生成下一个实数，它在 [x, y] 范围内
            t = random.uniform(0, 2 * pi)
            x, y = heart_function(t)
            self._points.add((x, y))
        # 爱心内扩散
        # list() 方法用于将元组转换为列表
        for _x, _y in list(self._points):
            # 从 0 开始到 2
            for _ in range(3):
                x, y = scatter_inside(_x, _y, 0.05)
                # 边缘扩散效果点坐标集合
                self._edge_diffusion_points.add((x, y))
        # 爱心内再次扩散
        point_list = list(self._points)
        for _ in range(4000):
            # choice() 方法返回一个列表，元组或字符串的随机项
            x, y = random.choice(point_list)
            x, y = scatter_inside(x, y, 0.17)
            self._center_diffusion_points.add((x, y))

    @staticmethod
    def calc_position(x, y, ratio):
        force = 1 / (((x - CANVAS_CENTER_X) ** 2 +
                      (y - CANVAS_CENTER_Y) ** 2) ** 0.520)
        dx = ratio * force * (x - CANVAS_CENTER_X) + random.randint(-1, 1)
        dy = ratio * force * (y - CANVAS_CENTER_Y) + random.randint(-1, 1)
        return x - dx, y - dy

    def calc(self, generate_frame):
        # curve() 函数可以绘制函数的图像   generate_frame [0,20]   curve(…) [-1,1]
        ratio = 10 * curve(generate_frame / 10 * pi)
        # halo_radius 光环半径 [4, 16]
        halo_radius = int(4 + 6 * (1 + curve(generate_frame / 10 * pi)))
        # halo_number 光环数量 [3000, 11000]
        halo_number = int(
            3000 + 4000 * abs(curve(generate_frame / 10 * pi) ** 2))
        all_points = []
        # 光环
        heart_halo_point = set()
        for _ in range(halo_number):
            t = random.uniform(0, 2 * pi)
            x, y = heart_function(t, shrink_ratio=11.6)
            x, y = shrink(x, y, halo_radius)
            if (x, y) not in heart_halo_point:
                heart_halo_point.add((x, y))
                # random.randint() 方法返回指定范围内的整数
                x += random.randint(-14, 14)
                y += random.randint(-14, 14)
                # choice() 方法返回一个列表，元组或字符串的随机项
                size = random.choice((1, 2, 2))
                # append() 方法用于在列表末尾添加新的对象
                all_points.append((x, y, size))
        # 轮廓
        # 原始爱心坐标集合
        for x, y in self._points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 3)
            all_points.append((x, y, size))
        # 内容
        # 边缘扩散效果点坐标集合
        for x, y in self._edge_diffusion_points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 2)
            all_points.append((x, y, size))
        self.all_points[generate_frame] = all_points
        # 中心扩散效果点坐标集合
        for x, y in self._center_diffusion_points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 2)
            all_points.append((x, y, size))
        self.all_points[generate_frame] = all_points

    def render(self, render_canvas, render_frame):
        for x, y, size in self.all_points[render_frame % self.generate_frame]:
            # create_rectangle() 四个参数，前两个左上角坐标，后两个右下角坐标
            render_canvas.create_rectangle(
                x, y, x + size, y + size, width=0, fill=HEART_COLOR)


def draw(main: Tk, render_canvas: Canvas, render_heart: Heart, render_frame=0):
    render_canvas.delete('all')
    render_heart.render(render_canvas, render_frame)
    main.after(160, draw, main, render_canvas, render_heart, render_frame + 1)


if __name__ == '__main__':
    root = Tk()
    root.title("跳动爱心")
    canvas = Canvas(root, bg='black', height=CANVAS_HEIGHT, width=CANVAS_WIDTH)
    canvas.pack()
    heart = Heart()
    draw(root, canvas, heart)
    root.mainloop()
