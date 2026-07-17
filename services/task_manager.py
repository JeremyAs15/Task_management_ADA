# services/task_manager.py
# Une el heap (prioridad) y el AVL (búsqueda por ID)

from models.task import Task
from structures.max_heap import MaxHeap
from structures.avl_tree import AVLTree


class TaskManager:
    """Encargado de agregar, buscar y completar tareas."""

    def __init__(self):
        self.heap = MaxHeap()   # por prioridad
        self.avl = AVLTree()    # por ID
        self._next_id = 1       # IDs automáticos

    def create_task(self, description, priority, due_date=None):
        """
        Crea una tarea con ID automático e inserta en heap + AVL.
        Devuelve la tarea creada.
        """
        task = Task(self._next_id, description, priority, due_date)
        self._next_id += 1
        self.heap.insert(task)
        self.avl.insert(task)
        return task

    def add_task(self, task):
        """
        Inserta una tarea ya construida en AMBAS estructuras.
        False si el ID ya existía.
        Actualiza _next_id si hace falta.
        """
        if self.avl.search(task.id) is not None:
            return False

        self.heap.insert(task)
        self.avl.insert(task)
        if task.id >= self._next_id:
            self._next_id = task.id + 1
        return True

    def find_task(self, task_id):
        """Busca solo en el AVL (rápido por ID)."""
        return self.avl.search(task_id)

    def get_most_urgent(self):
        """Mira la más urgente sin completarla."""
        return self.heap.peek()

    def complete_urgent(self):
        """
        Completa la más prioritaria:
        1) sale del heap
        2) se borra del AVL
        """
        task = self.heap.extract_max()
        if task is None:
            return None

        self.avl.delete(task.id)
        return task

    def complete_by_id(self, task_id):
        """
        Completa una tarea específica por ID:
        1) se busca en AVL
        2) se quita del heap
        3) se quita del AVL
        """
        task = self.avl.search(task_id)
        if task is None:
            return None

        self.heap.remove_by_id(task_id)
        self.avl.delete(task_id)
        return task

    def delete_task(self, task_id):
        """Elimina la tarea de heap y AVL (alias de completar por ID)."""
        return self.complete_by_id(task_id)

    def update_description(self, task_id, new_description):
        """
        Edita solo la descripción.
        Como el peso no depende del texto, no hay que reordenar el heap.
        """
        task = self.avl.search(task_id)
        if task is None:
            return None
        text = (new_description or "").strip()
        if not text:
            return None
        task.description = text
        return task

    def list_tasks(self):
        """Lista ordenada por ID (desde el AVL)."""
        return self.avl.inorder()

    def balance_report(self):
        """Para la demo de equilibrio del AVL."""
        return self.avl.get_balance_report()
