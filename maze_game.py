import tkinter as tk
from tkinter import filedialog, messagebox
import importlib.util
import random


class MazeGameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Maze Solver: Shortest Path Education")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f4f8")

        # ตัวแปรระบบ
        self.cell_size = 40
        self.maze_data = []
        self.rows = 0
        self.cols = 0
        self.node_map = {}
        self.reverse_node_map = {}
        self.graph = {}
        self.student_module = None
        self.path_step = 0
        self.solution_path = []

        self.create_widgets()
        self.generate_random_maze()

    # ---------------- UI ----------------
    def create_widgets(self):
        control_frame = tk.Frame(self.root, bg="#ffffff", bd=2, relief=tk.GROOVE)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        tk.Label(control_frame, text="Control Panel", font=("Arial", 16, "bold"),
                 bg="#ffffff").pack(pady=10)

        self.btn_load_map = self.create_button(
            control_frame, "📂 1. Load Maze (.txt)", self.load_map_file, "#3498db")
        self.btn_gen_maze = self.create_button(
            control_frame, "🎲 2. Random Maze", self.generate_random_maze, "#9b59b6")
        self.btn_load_code = self.create_button(
            control_frame, "🐍 3. Load Student Code", self.load_student_code, "#e67e22")
        self.btn_solve = self.create_button(
            control_frame, "🚀 4. Solve Maze", self.solve_maze, "#2ecc71")

        tk.Label(control_frame, text="Status:", bg="#ffffff").pack(pady=(20, 5))
        self.lbl_status = tk.Label(control_frame, text="Ready",
                                   fg="gray", bg="#ffffff", wraplength=180)
        self.lbl_status.pack()

        self.canvas_frame = tk.Frame(self.root, bg="#f0f4f8")
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH,
                               expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(self.canvas_frame, bg="#2c3e50")
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def create_button(self, parent, text, command, color):
        btn = tk.Button(parent, text=text, command=command, bg=color, fg="black",
                        font=("Arial", 12), width=20, pady=5, relief=tk.FLAT)
        btn.pack(pady=5)
        return btn

    # ---------------- Maze Generation ----------------
    def generate_random_maze(self):
        rows, cols = 15, 15
        self.maze_data = [[0 for _ in range(cols)] for _ in range(rows)]

        def carve(r, c):
            self.maze_data[r][c] = 1
            dirs = [(0, 2), (0, -2), (2, 0), (-2, 0)]
            random.shuffle(dirs)
            for dr, dc in dirs:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and self.maze_data[nr][nc] == 0:
                    self.maze_data[r + dr//2][c + dc//2] = 1
                    carve(nr, nc)

        carve(0, 0)
        self.maze_data[rows-1][cols-1] = 1

        self.load_maze_data(self.maze_data)
        self.lbl_status.config(text="Random maze generated.")

    # ---------------- Load Map ----------------
    def load_map_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt")])
        if not file_path:
            return

        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()

            data = []
            for line in lines:
                row = [int(x) for x in line.strip() if x in '01']
                if row:
                    data.append(row)

            # Validate equal width
            width = len(data[0])
            for row in data:
                if len(row) != width:
                    raise ValueError("All rows must have equal length")

            self.load_maze_data(data)
            self.lbl_status.config(
                text=f"Loaded map: {file_path.split('/')[-1]}")

        except Exception as e:
            messagebox.showerror("Error", f"Invalid map file: {e}")

    # ---------------- Prepare Graph ----------------
    def load_maze_data(self, data):
        self.maze_data = data
        self.rows = len(data)
        self.cols = len(data[0]) if self.rows > 0 else 0

        # Validate start/end
        if self.maze_data[0][0] != 1:
            raise ValueError("Start (0,0) must be path")
        if self.maze_data[self.rows-1][self.cols-1] != 1:
            raise ValueError("End must be path")

        self.prepare_graph_data()
        self.draw_maze()

    def prepare_graph_data(self):
        self.node_map = {}
        self.reverse_node_map = {}
        self.graph = {}

        start = (0, 0)
        end = (self.rows-1, self.cols-1)

        self.node_map[start] = 0
        self.reverse_node_map[0] = start
        self.node_map[end] = 1
        self.reverse_node_map[1] = end

        current_id = 2
        for r in range(self.rows):
            for c in range(self.cols):
                if self.maze_data[r][c] == 1 and (r, c) not in [start, end]:
                    self.node_map[(r, c)] = current_id
                    self.reverse_node_map[current_id] = (r, c)
                    current_id += 1

        # Build Graph
        for r in range(self.rows):
            for c in range(self.cols):
                if self.maze_data[r][c] == 1:
                    u = self.node_map[(r, c)]
                    self.graph[u] = []

                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < self.rows and 0 <= nc < self.cols:
                            if self.maze_data[nr][nc] == 1:
                                v = self.node_map[(nr, nc)]
                                self.graph[u].append(v)

    # ---------------- Drawing ----------------
    def draw_maze(self):
        self.canvas.delete("all")

        cw = min(800 // self.cols, 600 // self.rows)
        self.cell_size = cw

        for r in range(self.rows):
            for c in range(self.cols):
                x1, y1 = c*cw, r*cw
                x2, y2 = x1+cw, y1+cw

                color = "#34495e" if self.maze_data[r][c] == 0 else "#ecf0f1"

                if (r, c) == (0, 0):
                    color = "#e74c3c"
                elif (r, c) == (self.rows-1, self.cols-1):
                    color = "#f1c40f"

                self.canvas.create_rectangle(
                    x1, y1, x2, y2, fill=color, outline="#bdc3c7")

        self.draw_player(0, 0)

    def draw_player(self, r, c):
        self.canvas.delete("player")
        cw = self.cell_size
        pad = cw*0.2
        self.canvas.create_oval(
            c*cw+pad, r*cw+pad,
            (c+1)*cw-pad, (r+1)*cw-pad,
            fill="#3498db", outline="white", width=2, tags="player"
        )

    # ---------------- Student Code ----------------
    def load_student_code(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Python Files", "*.py")])
        if not file_path:
            return

        try:
            spec = importlib.util.spec_from_file_location(
                "student_solver", file_path)
            module = importlib.util.module_from_spec(spec) # type: ignore
            spec.loader.exec_module(module) # type: ignore

            if hasattr(module, "find_shortest_path"):
                self.student_module = module
                self.lbl_status.config(
                    text="Code loaded successfully!", fg="green")
            else:
                raise ValueError("Missing find_shortest_path()")

        except Exception as e:
            self.student_module = None
            messagebox.showerror("Code Error", str(e))

    # ---------------- Solve ----------------
    def solve_maze(self):
        if not self.student_module:
            messagebox.showwarning(
                "Warning", "Please load student code first.")
            return

        try:
            path_nodes = self.student_module.find_shortest_path(self.graph)

            if not isinstance(path_nodes, list):
                raise ValueError("Path must be list")

            if not path_nodes or path_nodes[0] != 0 or path_nodes[-1] != 1:
                raise ValueError("Invalid path start/end")

            # Validate movement
            for i in range(len(path_nodes)-1):
                if path_nodes[i+1] not in self.graph[path_nodes[i]]:
                    raise ValueError("Invalid move in path")

            self.solution_path = path_nodes
            self.start_animation()

        except Exception as e:
            messagebox.showerror("Execution Error", str(e))

    # ---------------- Animation ----------------
    def start_animation(self):
        self.path_step = 0
        self.animate_step()

    def animate_step(self):
        if self.path_step < len(self.solution_path):
            node = self.solution_path[self.path_step]

            if node in self.reverse_node_map:
                r, c = self.reverse_node_map[node]
                self.draw_player(r, c)

                cw = self.cell_size
                cx, cy = c*cw+cw/2, r*cw+cw/2
                self.canvas.create_oval(
                    cx-3, cy-3, cx+3, cy+3,
                    fill="#2ecc71", outline="", tags="trail"
                )

            self.path_step += 1
            self.root.after(200, self.animate_step)
        else:
            messagebox.showinfo("Success", "Maze Solved!")


# ---------------- MAIN ----------------
if __name__ == "__main__":
    root = tk.Tk()
    app = MazeGameApp(root)
    root.mainloop()
