# structures/max_heap.py
# Montículo binario (max-heap): cola de prioridad para las tareas más urgentes.


class MaxHeap:
    """Cola de prioridad implementada como montículo binario (array)."""

    def __init__(self):
        self.items = []  # arreglo que representa el árbol binario

    # ----- funciones auxiliares -----

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)

    def _parent(self, i):
        return (i - 1) // 2

    def _left(self, i):
        return 2 * i + 1

    def _right(self, i):
        return 2 * i + 2

    def _swap(self, i, j):
        self.items[i], self.items[j] = self.items[j], self.items[i]

    def _sift_up(self, i):
        """Sube el elemento en la posición i mientras gane a su padre."""
        while i > 0:
            padre = self._parent(i)
            if self.items[i].has_more_priority(self.items[padre]):
                self._swap(i, padre)
                i = padre
            else:
                break

    def _sift_down(self, i):
        """Baja el elemento en la posición i mientras algún hijo le gane."""
        n = self.size()
        while True:
            izq = self._left(i)
            der = self._right(i)
            mayor = i

            if izq < n and self.items[izq].has_more_priority(self.items[mayor]):
                mayor = izq
            if der < n and self.items[der].has_more_priority(self.items[mayor]):
                mayor = der

            if mayor == i:
                break  # ya está en su lugar

            self._swap(i, mayor)
            i = mayor

    def _find_index(self, task_id):
        """Busca la posición de una tarea por ID (recorrido lineal)."""
        for i, task in enumerate(self.items):
            if task.id == task_id:
                return i
        return None

    # ----- operaciones que usa el proyecto -----

    def insert(self, task):
        """Agrega una tarea al final y la sube a su lugar (sift-up)."""
        self.items.append(task)
        self._sift_up(self.size() - 1)

    def peek(self):
        """Mira la más urgente SIN quitarla. None si está vacío."""
        if self.is_empty():
            return None
        return self.items[0]

    def extract_max(self):
        """Saca y devuelve la tarea más urgente (raíz del montículo)."""
        if self.is_empty():
            return None

        raiz = self.items[0]
        ultimo = self.items.pop()  # quitamos el último de una vez

        if not self.is_empty():
            self.items[0] = ultimo
            self._sift_down(0)

        return raiz

    def remove_by_id(self, task_id):
        """
        Quita una tarea por su ID (aunque no sea la más urgente).
        True si la encontró y borró.
        """
        i = self._find_index(task_id)
        if i is None:
            return False

        ultimo = self.items.pop()

        if i < self.size():
            # todavía queda un hueco en la posición i: lo llenamos con el último
            # y dejamos que encuentre su lugar (solo una de las dos hará algo)
            self.items[i] = ultimo
            self._sift_up(i)
            self._sift_down(i)

        return True

    def get_all(self):
        """Copia de las tareas (sin ningún orden particular)."""
        return list(self.items)
