# models/task.py
# Modelo de una tarea del sistema

class Task:
    """Una tarea pendiente del usuario."""

    def __init__(self, task_id, description, priority, due_date=None):
        self.id = task_id              # identificador único (para el AVL)
        self.description = description # texto de la tarea
        self.priority = priority       # 1=Baja, 2=Media, 3=Alta (para el heap)
        self.due_date = due_date       # fecha de vencimiento (opcional)

    def __str__(self):
        # Cómo se ve al hacer print(task)
        nombres = {1: "Baja", 2: "Media", 3: "Alta"}
        nivel = nombres.get(self.priority, str(self.priority))
        return f"[{self.id}] {self.description} ({nivel})"

    def __repr__(self):
        # Útil al depurar en listas
        return self.__str__()

    def has_more_priority(self, otra):
        """
        True si esta tarea gana a 'otra' en prioridad.
        Si empatan, gana la de fecha más cercana.
        """
        if self.priority != otra.priority:
            return self.priority > otra.priority

        # misma prioridad: comparar fechas (si existen)
        if self.due_date is None and otra.due_date is None:
            return False
        if self.due_date is None:
            return False  # sin fecha = menos urgente
        if otra.due_date is None:
            return True
        return self.due_date < otra.due_date