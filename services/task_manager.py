# services/task_manager.py
# Une el heap (prioridad) y el AVL (búsqueda por ID)


from structures.max_heap import MaxHeap
from structures.avl_tree import AVLTree


class TaskManager:
    """Encargado de agregar, buscar y completar tareas."""

    def __init__(self):
        self.heap = MaxHeap()   # por prioridad
        self.avl = AVLTree()    # por ID

    def add_task(self, task):
        """
        Inserta en AMBAS estructuras.
        False si el ID ya existía.
        """
        if self.avl.search(task.id) is not None:
            return False  # no duplicar IDs

        self.heap.insert(task)
        self.avl.insert(task)
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

    def list_tasks(self):
        """Lista ordenada por ID (desde el AVL)."""
        return self.avl.inorder()

    def balance_report(self):
        """Para la demo de equilibrio del AVL."""
        return self.avl.get_balance_report()