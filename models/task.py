# models/task.py
# Modelo de una tarea del sistema

import datetime


class Task:
    """Una tarea pendiente del usuario."""

    def __init__(self, task_id, description, priority, due_date=None):
        self.id = task_id              # identificador único (para el AVL)
        self.description = description # texto de la tarea
        self.priority = priority       # 0=Baja, 1=Media, 2=Alta
        self.due_date = self._parse_due(due_date)  # si no hay fecha → hoy
        self.weight = self._calculate_weight()

    def _parse_due(self, due_date):
        """Convierte a date. Si no hay fecha válida, usa hoy."""
        if due_date is None:
            return datetime.date.today()

        if isinstance(due_date, datetime.datetime):
            return due_date.date()

        if isinstance(due_date, datetime.date):
            return due_date

        if isinstance(due_date, str):
            text = due_date.strip()
            for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
                try:
                    return datetime.datetime.strptime(text, fmt).date()
                except ValueError:
                    continue

        return datetime.date.today()

    def _calculate_weight(self):
        # Prioridad domina (Alta=2000, Media=1000, Baja=0)
        base = self.priority * 1000

        # Fecha más cercana → mayor peso
        hoy = datetime.date.today()
        diferencia_dias = abs((self.due_date - hoy).days)
        peso_fecha = diferencia_dias * 10

        # Empate: ID más bajo gana
        return base - peso_fecha - self.id

    def due_label(self):
        return self.due_date.strftime("%Y-%m-%d")

    def priority_label(self):
        return {0: "Baja", 1: "Media", 2: "Alta"}.get(self.priority, str(self.priority))

    def __str__(self):
        return f"[{self.id}] {self.description} ({self.priority_label()} · {self.due_label()})"

    def __repr__(self):
        return self.__str__()

    def has_more_priority(self, otra):
        """True si esta tarea tiene mayor peso que otra."""
        return self.weight > otra.weight
