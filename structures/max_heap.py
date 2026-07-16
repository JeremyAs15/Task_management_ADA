# structures/max_heap.py
# HEAP TEMPORAL (lista).
# Sirve para probar el sistema mientras se implementa el montículo real.
# La interfaz (nombres de métodos) debe ser la misma en la versión final.


class MaxHeap:
    """Cola de prioridad temporal usando una lista."""

    def __init__(self):
        self.items = []  # aquí guardamos las tareas

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)

    def insert(self, task):
        """Agrega una tarea al final (luego se ordena al extraer)."""
        self.items.append(task)

    def peek(self):
        """Mira la más urgente SIN quitarla. None si está vacío."""
        if self.is_empty():
            return None

        # buscamos la de mayor prioridad
        mejor = self.items[0]
        for task in self.items[1:]:
            if task.has_more_priority(mejor):
                mejor = task
        return mejor

    def extract_max(self):
        """Saca y devuelve la tarea más urgente."""
        if self.is_empty():
            return None

        mejor = self.peek()
        self.items.remove(mejor)
        return mejor

    def remove_by_id(self, task_id):
        """
        Quita una tarea por su ID (aunque no sea la más urgente).
        True si la encontró y borró.
        """
        for i, task in enumerate(self.items):
            if task.id == task_id:
                self.items.pop(i)
                return True
        return False

    def get_all(self):
        """Copia de las tareas"""
        return list(self.items)