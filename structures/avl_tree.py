# structures/avl_tree.py
# Árbol AVL: busca tareas por ID de forma rápida (O(log n))


class AVLNode:
    """Un nodo = una tarea + hijos izquierdo/derecho."""

    def __init__(self, task):
        self.key = task.id      # ordenamos el árbol por este número
        self.task = task        # guardamos la tarea entera
        self.left = None        # hijo izquierdo (IDs más pequeños)
        self.right = None       # hijo derecho (IDs más grandes)
        self.height = 1         # un nodo solo mide 1 de alto


class AVLTree:
    """Árbol balanceado indexado por ID."""

    def __init__(self):
        self.root = None  # al inicio el árbol está vacío

    # ----- funciones auxiliares -----

    def _get_height(self, node):
        """Si no hay nodo, la altura es 0."""
        if node is None:
            return 0
        return node.height

    def _get_balance(self, node):
        """
        Factor de equilibrio = altura_izq - altura_der
        Debe quedar en -1, 0 o 1.
        """
        if node is None:
            return 0
        return self._get_height(node.left) - self._get_height(node.right)

    def _update_height(self, node):
        """Recalcula la altura mirando a los dos hijos."""
        left_h = self._get_height(node.left)
        right_h = self._get_height(node.right)
        node.height = 1 + max(left_h, right_h)

    def _rotate_right(self, y):
        """
        Rotación simple a la derecha (caso LL).

              y                x
             /       ->       / \
            x                A   y
           /
          A
        """
        x = y.left
        temp = x.right

        # se hace el giro
        x.right = y
        y.left = temp

        # se actualizan alturas (primero el de abajo)
        self._update_height(y)
        self._update_height(x)
        return x  # x es la nueva raíz de este pedazo

    def _rotate_left(self, x):
        """
        Rotación simple a la izquierda (caso RR).

            x                    y
             \         ->       / \
              y                x   C
               \
                C
        """
        y = x.right
        temp = y.left

        y.left = x
        x.right = temp

        self._update_height(x)
        self._update_height(y)
        return y

    def _rebalance(self, node):
        """Si el nodo está torcido, aplica la rotación correcta."""
        self._update_height(node)
        balance = self._get_balance(node)

        # LL: está cargado a la izquierda
        if balance > 1 and self._get_balance(node.left) >= 0:
            return self._rotate_right(node)

        # LR: izquierda, pero el hijo está cargado a la derecha
        if balance > 1 and self._get_balance(node.left) < 0:
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)

        # RR: está cargado a la derecha
        if balance < -1 and self._get_balance(node.right) <= 0:
            return self._rotate_left(node)

        # RL: derecha, pero el hijo está cargado a la izquierda
        if balance < -1 and self._get_balance(node.right) > 0:
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        # si no entró a ningún if, ya estaba bien
        return node

    # ----- operaciones que usa el proyecto -----

    def insert(self, task):
        """Agrega una tarea al árbol (por su ID)."""
        self.root = self._insert(self.root, task)

    def _insert(self, node, task):
        # 1) insertar como árbol de búsqueda normal
        if node is None:
            return AVLNode(task)

        if task.id < node.key:
            node.left = self._insert(node.left, task)
        elif task.id > node.key:
            node.right = self._insert(node.right, task)
        else:
            # el ID ya existía: actualizamos la tarea
            node.task = task
            return node

        # 2) al subir, arreglamos el balance
        return self._rebalance(node)

    def search(self, task_id):
        """Busca una tarea por ID. Devuelve la tarea o None."""
        node = self.root

        while node is not None:
            if task_id == node.key:
                return node.task
            elif task_id < node.key:
                node = node.left
            else:
                node = node.right

        return None  # no se encontró

    def delete(self, task_id):
        """
        Elimina la tarea con ese ID.
        Devuelve True si la borró, False si no existía.
        """
        if self.search(task_id) is None:
            return False
        self.root = self._delete(self.root, task_id)
        return True

    def _delete(self, node, task_id):
        if node is None:
            return None

        # buscar el nodo a borrar
        if task_id < node.key:
            node.left = self._delete(node.left, task_id)
        elif task_id > node.key:
            node.right = self._delete(node.right, task_id)
        else:
            # lo encontramos

            # caso A: no tiene hijo izquierdo
            if node.left is None:
                return node.right

            # caso B: no tiene hijo derecho
            if node.right is None:
                return node.left

            # caso C: tiene dos hijos
            # tomamos el más pequeño de la derecha
            successor = self._find_min(node.right)
            node.key = successor.key
            node.task = successor.task
            node.right = self._delete(node.right, successor.key)

        # al subir, reequilibramos
        return self._rebalance(node)

    def _find_min(self, node):
        """Camina siempre a la izquierda hasta el más pequeño."""
        while node.left is not None:
            node = node.left
        return node

    def inorder(self):
        """Lista las tareas ordenadas por ID (para mostrar en pantalla)."""
        result = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node, result):
        if node is None:
            return
        self._inorder(node.left, result)   # izquierda
        result.append(node.task)           # raíz
        self._inorder(node.right, result)  # derecha

    def get_balance_report(self):
        """
        Para la prueba del PDF.
        Devuelve lista de (id, altura, factor).
        """
        report = []
        self._collect_balance(self.root, report)
        return report

    def _collect_balance(self, node, report):
        if node is None:
            return
        self._collect_balance(node.left, report)
        report.append((node.key, node.height, self._get_balance(node)))
        self._collect_balance(node.right, report)

    def is_balanced(self):
        """True si todos los factores están entre -1 y 1."""
        for _, _, balance in self.get_balance_report():
            if abs(balance) > 1:
                return False
        return True