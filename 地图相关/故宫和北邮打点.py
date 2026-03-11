import tkinter as tk
from tkinter import filedialog
import math
from PIL import Image, ImageTk
import os


class MapPointingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("地图打点建模")

        # 打开图像文件
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if not file_path:
            root.destroy()
            return

        pil_image = Image.open(file_path)
        self.image = ImageTk.PhotoImage(pil_image)

        # 创建画布并设置滚动区域
        self.canvas = tk.Canvas(root, width=self.root.winfo_screenwidth(),
                                height=self.root.winfo_screenheight())
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.image_id = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

        # 创建垂直滚动条
        self.v_scrollbar = tk.Scrollbar(root, orient=tk.VERTICAL, command=self.canvas.yview)
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.config(yscrollcommand=self.v_scrollbar.set)

        # 绑定鼠标滚轮事件
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)

        # 读取节点和边文件
        self.nodes = {}
        self.edges = []
        try:
            with open("nodes.txt", "r", encoding="utf-8") as f:
                for line in f:
                    node_id, info = line.strip().split(":")
                    x_str, y_str, type_str, name = info.split(",")
                    x = int(x_str)
                    y = int(y_str)
                    node_type = int(type_str)
                    self.nodes[int(node_id)] = (x, y, node_type, name)
                    self.draw_node(int(node_id), x, y, node_type)

            with open("edges.txt", "r", encoding="utf-8") as f:
                for line in f:
                    start_id, end_id = map(int, line.strip().split(","))
                    self.edges.append((start_id, end_id))
                    self.draw_edge(start_id, end_id)
        except FileNotFoundError:
            pass

        # 模式变量
        self.mode = None
        self.current_type = 0
        self.selected_node = None
        type_building = [x[:-4] for x in os.listdir(r'节点图片\building')]
        type_service = [x[:-4] for x in os.listdir(r'节点图片\service')]
        type_cross = [x[:-4] for x in os.listdir(r'节点图片\cross')]
        self.type_chinese = type_building + type_service + type_cross

        # 绑定事件
        self.canvas.bind("<Button-1>", self.on_click)
        self.root.bind("<Key>", self.on_key)

    def draw_node(self, node_id, x, y, node_type):
        color = ["red", "green", "blue", "yellow", "orange", "purple", "brown", "pink", "gray", "cyan",
                 "magenta", "lime", "teal", "navy", "olive"][node_type]
        self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill=color, tags=f"node_{node_id}")
        # 在节点位置绘制标号
        self.canvas.create_text(x, y - 5, text=str(node_id), fill='black')

    def draw_edge(self, start_id, end_id):
        start_x, start_y, _, _ = self.nodes[start_id]
        end_x, end_y, _, _ = self.nodes[end_id]
        self.canvas.create_line(start_x, start_y, end_x, end_y, width=1, tags=f"edge_{start_id}_{end_id}")

    def find_nearest_node(self, x, y):
        min_dist = float('inf')
        nearest_node = None
        for node_id, (node_x, node_y, _, _) in self.nodes.items():
            dist = math.sqrt((x - node_x) ** 2 + (y - node_y) ** 2)
            if dist < min_dist:
                min_dist = dist
                nearest_node = node_id
        return nearest_node

    def on_click(self, event):
        # 获取画布滚动后的实际位置
        x = event.x + self.canvas.canvasx(0)
        y = event.y + self.canvas.canvasy(0)
        x = int(x)
        y = int(y)
        print(x, y)
        if self.mode == "n":
            node_id = len(self.nodes)
            default_name = f'name{node_id}'
            # 创建弹出窗口
            top = tk.Toplevel(self.root)
            top.title("输入节点名称")
            label = tk.Label(top, text="请输入节点名称:")
            label.pack()
            entry = tk.Entry(top)
            entry.insert(0, default_name)  # 设置默认文本
            entry.pack()

            def save_name():
                name = entry.get()
                self.nodes[node_id] = (x, y, self.current_type, name)
                self.draw_node(node_id, x, y, self.current_type)
                with open("nodes.txt", "a", encoding="utf-8") as f:
                    f.write(f"{node_id}:{x},{y},{self.current_type},{name}\n")
                top.destroy()

            button = tk.Button(top, text="保存", command=save_name)
            button.pack()
        elif self.mode == "e":
            node = self.find_nearest_node(x, y)
            if self.selected_node is None:
                self.selected_node = node
            else:
                if node != self.selected_node:
                    edge = (self.selected_node, node)
                    if edge not in self.edges and (edge[1], edge[0]) not in self.edges:
                        self.edges.append(edge)
                        self.draw_edge(*edge)
                        with open("edges.txt", "a", encoding="utf-8") as f:
                            f.write(f"{self.selected_node},{node}\n")
                self.selected_node = None

    def on_key(self, event):
        if event.char == "n":
            self.mode = "n"
            print('mode: ' + event.char)
        elif event.char == "e":
            self.mode = "e"
            print('mode: ' + event.char)
        elif event.char == "z":
            self.mode = None
            print('mode: None')
        elif event.char in "1234567890yuiop":
            key_map = "1234567890yuiop"
            self.current_type = key_map.index(event.char)
            chinese = self.type_chinese[self.current_type]
            print('type: ' + str(self.current_type) + chinese)

    def on_mousewheel(self, event):
        # 根据鼠标滚轮方向滚动画布
        if event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        else:
            self.canvas.yview_scroll(1, "units")


if __name__ == "__main__":
    root = tk.Tk()
    app = MapPointingApp(root)
    root.mainloop()

