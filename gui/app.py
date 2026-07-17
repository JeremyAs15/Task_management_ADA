import tkinter as tk
from tkinter import ttk, messagebox
from models.task import Task
from services.task_manager import TaskManager

class TaskManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de Tareas - Proyecto ADA")
        self.root.geometry("800x600")
        
        self.tree_window = None
        self.tree_canvas = None
        self.heap_window = None
        self.heap_canvas = None
        
        self.manager = TaskManager()
        
        self.setup_ui()

    def setup_ui(self):
        # Frame Principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # --- Frame Izquierdo (Formulario) ---
        left_frame = ttk.LabelFrame(main_frame, text="Agregar Tarea", padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # ID
        ttk.Label(left_frame, text="ID (Único):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entry_id = ttk.Entry(left_frame)
        self.entry_id.grid(row=0, column=1, pady=5)
        
        # Descripción
        ttk.Label(left_frame, text="Descripción:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.entry_desc = ttk.Entry(left_frame)
        self.entry_desc.grid(row=1, column=1, pady=5)
        
        # Prioridad
        ttk.Label(left_frame, text="Prioridad (0-Baja, 1-Media, 2-Alta):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.combo_prior = ttk.Combobox(left_frame, values=["0", "1", "2"], state="readonly")
        self.combo_prior.current(0)
        self.combo_prior.grid(row=2, column=1, pady=5)

        # Fecha de Vencimiento
        ttk.Label(left_frame, text="Fecha (YYYY-MM-DD):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.entry_date = ttk.Entry(left_frame)
        import datetime
        self.entry_date.insert(0, str(datetime.date.today()))
        self.entry_date.grid(row=3, column=1, pady=5)
        
        # Botón Agregar
        btn_add = ttk.Button(left_frame, text="Agregar Tarea", command=self.add_task)
        btn_add.grid(row=4, column=0, columnspan=2, pady=10)
        
        # --- Botones de Acción Extra ---
        ttk.Separator(left_frame, orient=tk.HORIZONTAL).grid(row=5, column=0, columnspan=2, sticky="ew", pady=0)
        
        btn_complete_urgent = ttk.Button(left_frame, text="Completar Tarea más Urgente", command=self.complete_urgent)
        btn_complete_urgent.grid(row=6, column=0, columnspan=2, pady=5, sticky="ew")
        
        # Buscar/Eliminar por ID
        ttk.Label(left_frame, text="ID para Buscar/Completar:").grid(row=7, column=0, columnspan=2, sticky=tk.W, pady=(15, 0))
        self.entry_action_id = ttk.Entry(left_frame)
        self.entry_action_id.grid(row=8, column=0, columnspan=2, pady=5, sticky="ew")
        
        btn_search = ttk.Button(left_frame, text="Buscar Tarea", command=self.search_task)
        btn_search.grid(row=9, column=0, pady=5, padx=2, sticky="ew")
        
        btn_complete_id = ttk.Button(left_frame, text="Completar por ID", command=self.complete_by_id)
        btn_complete_id.grid(row=9, column=1, pady=5, padx=2, sticky="ew")
        
        ttk.Separator(left_frame, orient=tk.HORIZONTAL).grid(row=10, column=0, columnspan=2, sticky="ew", pady=10)
        btn_test_avl = ttk.Button(left_frame, text="Reporte Balance AVL", command=self.show_balance_report)
        btn_test_avl.grid(row=11, column=0, columnspan=2, pady=5, sticky="ew")
        
        btn_view_avl = ttk.Button(left_frame, text="Ver Árbol AVL (Visual)", command=self.show_avl_tree)
        btn_view_avl.grid(row=12, column=0, columnspan=2, pady=5, sticky="ew")

        btn_view_heap = ttk.Button(left_frame, text="Ver Montículo Heap (Visual)", command=self.show_heap_tree)
        btn_view_heap.grid(row=13, column=0, columnspan=2, pady=5, sticky="ew")
        
        # --- Frame Derecho (Lista) ---
        right_frame = ttk.LabelFrame(main_frame, text="Lista de Tareas (Ordenadas por ID - AVL)", padding="10")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        columns = ("id", "desc", "date", "prior", "weight")
        self.tree = ttk.Treeview(right_frame, columns=columns, show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("desc", text="Descripción")
        self.tree.heading("date", text="Fecha")
        self.tree.heading("prior", text="Prioridad")
        self.tree.heading("weight", text="Peso")
        
        self.tree.column("id", width=50)
        self.tree.column("desc", width=200)
        self.tree.column("date", width=80)
        self.tree.column("prior", width=80)
        self.tree.column("weight", width=80)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Mostrar la más urgente arriba
        self.lbl_urgent = ttk.Label(right_frame, text="Tarea más urgente: Ninguna", font=("Arial", 10, "bold"), foreground="blue")
        self.lbl_urgent.pack(pady=10)

    def refresh_list(self):
        # Limpiar lista
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Llenar lista desde AVL (Inorder)
        tasks = self.manager.list_tasks()
        for t in tasks:
            prior_str = {0: "Baja", 1: "Media", 2: "Alta"}.get(t.priority, str(t.priority))
            self.tree.insert("", tk.END, values=(t.id, t.description, t.due_date, prior_str, t.weight))
            
        # Actualizar más urgente
        urgent = self.manager.get_most_urgent()
        if urgent:
            self.lbl_urgent.config(text=f"Próxima a atender: [{urgent.id}] {urgent.description}")
        else:
            self.lbl_urgent.config(text="Tarea más urgente: Ninguna")
            
        # Actualizar visualización de los árboles si las ventanas están abiertas
        self.draw_tree()
        self.draw_heap()

    def show_avl_tree(self):
        if self.tree_window is None or not self.tree_window.winfo_exists():
            self.tree_window = tk.Toplevel(self.root)
            self.tree_window.title("Visualizador Árbol AVL")
            self.tree_window.geometry("800x600")
            
            self.tree_canvas = tk.Canvas(self.tree_window, bg="white")
            self.tree_canvas.pack(fill=tk.BOTH, expand=True)
            
        self.draw_tree()

    def draw_tree(self):
        if self.tree_window is None or not self.tree_window.winfo_exists():
            return
            
        self.tree_canvas.delete("all")
        root_node = self.manager.avl.root
        if root_node is not None:
            self._draw_node(root_node, 400, 50, 200, 70)
            
    def _draw_node(self, node, x, y, dx, dy):
        r = 20
        # Dibujar lineas a los hijos primero
        if node.left:
            self.tree_canvas.create_line(x, y, x - dx, y + dy, fill="black", width=2)
            self._draw_node(node.left, x - dx, y + dy, dx / 1.7, dy)
        if node.right:
            self.tree_canvas.create_line(x, y, x + dx, y + dy, fill="black", width=2)
            self._draw_node(node.right, x + dx, y + dy, dx / 1.7, dy)
            
        # Dibujar nodo actual
        color = "lightblue"
        self.tree_canvas.create_oval(x - r, y - r, x + r, y + r, fill=color, outline="black", width=2)
        self.tree_canvas.create_text(x, y, text=str(node.key), font=("Arial", 12, "bold"))

    def show_heap_tree(self):
        if self.heap_window is None or not self.heap_window.winfo_exists():
            self.heap_window = tk.Toplevel(self.root)
            self.heap_window.title("Visualizador Montículo (Max-Heap)")
            self.heap_window.geometry("800x600")
            
            self.heap_canvas = tk.Canvas(self.heap_window, bg="white")
            self.heap_canvas.pack(fill=tk.BOTH, expand=True)
            
        self.draw_heap()

    def draw_heap(self):
        if self.heap_window is None or not self.heap_window.winfo_exists():
            return
            
        self.heap_canvas.delete("all")
        items = self.manager.heap.items
        if items:
            self._draw_heap_node(0, items, 400, 50, 200, 70)
            
    def _draw_heap_node(self, index, items, x, y, dx, dy):
        r = 25
        n = len(items)
        left_idx = 2 * index + 1
        right_idx = 2 * index + 2
        
        # Dibujar lineas a los hijos primero
        if left_idx < n:
            self.heap_canvas.create_line(x, y, x - dx, y + dy, fill="black", width=2)
            self._draw_heap_node(left_idx, items, x - dx, y + dy, dx / 1.7, dy)
        if right_idx < n:
            self.heap_canvas.create_line(x, y, x + dx, y + dy, fill="black", width=2)
            self._draw_heap_node(right_idx, items, x + dx, y + dy, dx / 1.7, dy)
            
        # Dibujar nodo actual (mostrar ID y Peso)
        color = "lightgreen"
        self.heap_canvas.create_oval(x - r, y - r, x + r, y + r, fill=color, outline="black", width=2)
        task = items[index]
        self.heap_canvas.create_text(x, y - 5, text=f"ID:{task.id}", font=("Arial", 9, "bold"))
        self.heap_canvas.create_text(x, y + 8, text=f"W:{task.weight}", font=("Arial", 8))

    def add_task(self):
        try:
            task_id = int(self.entry_id.get())
            desc = self.entry_desc.get().strip()
            prior = int(self.combo_prior.get())
            date_str = self.entry_date.get().strip()
            
            if not desc:
                messagebox.showerror("Error", "La descripción no puede estar vacía")
                return
                
            task = Task(task_id, desc, prior, date_str)
            if self.manager.add_task(task):
                messagebox.showinfo("Éxito", f"Tarea {task_id} agregada correctamente.")
                self.entry_id.delete(0, tk.END)
                self.entry_desc.delete(0, tk.END)
                self.refresh_list()
            else:
                messagebox.showerror("Error", f"Ya existe una tarea con el ID {task_id}")
            """ self.manager.add_task(task)
            self.entry_id.delete(0, tk.END)
            self.entry_desc.delete(0, tk.END)
            self.refresh_list() """
        except ValueError:
            messagebox.showerror("Error", "El ID debe ser un número entero válido")

    def complete_urgent(self):
        task = self.manager.complete_urgent()
        if task:
            messagebox.showinfo("Completada", f"Se completó la tarea más urgente:\n{task}")
            self.refresh_list()
        else:
            messagebox.showwarning("Aviso", "No hay tareas para completar.")

    def search_task(self):
        try:
            task_id = int(self.entry_action_id.get())
            task = self.manager.find_task(task_id)
            if task:
                messagebox.showinfo("Resultado", f"Tarea encontrada (O(log n)):\n{task}")
            else:
                messagebox.showwarning("Resultado", f"No se encontró la tarea con ID {task_id}")
        except ValueError:
            messagebox.showerror("Error", "Ingrese un ID válido")

    def complete_by_id(self):
        try:
            task_id = int(self.entry_action_id.get())
            task = self.manager.complete_by_id(task_id)
            if task:
                messagebox.showinfo("Completada", f"Se completó la tarea:\n{task}")
                self.refresh_list()
            else:
                messagebox.showwarning("Aviso", f"No se encontró la tarea con ID {task_id}")
        except ValueError:
            messagebox.showerror("Error", "Ingrese un ID válido")

    def show_balance_report(self):
        report = self.manager.balance_report()
        if not report:
            messagebox.showinfo("Reporte AVL", "El árbol está vacío.")
            return
            
        lines = ["ID | Altura | Factor Balance"]
        lines.append("-" * 30)
        for node_id, height, balance in report:
            lines.append(f"{node_id:2}  | {height:6} | {balance:12}")
            
        is_bal = self.manager.avl.is_balanced()
        lines.append("-" * 30)
        lines.append(f"¿Árbol balanceado?: {'Sí' if is_bal else 'No'}")
        
        messagebox.showinfo("Reporte de Equilibrio AVL", "\n".join(lines))
