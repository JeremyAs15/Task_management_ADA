# models/task.py
# Modelo de una tarea del sistema

import datetime
import random

class Task:
    """Una tarea pendiente del usuario."""

    def __init__(self, task_id, description, priority, due_date=None):
        self.id = task_id              # identificador único (para el AVL)
        self.description = description # texto de la tarea
        self.priority = priority       # 0=Baja, 1=Media, 2=Alta
        
        # Fecha de vencimiento (datetime.date)
        if isinstance(due_date, str):
            try:
                self.due_date = datetime.datetime.strptime(due_date, "%Y-%m-%d").date()
            except ValueError:
                self.due_date = datetime.date.today()
        else:
            self.due_date = due_date if due_date else datetime.date.today()
            
        self.weight = self._calculate_weight()

    def _calculate_weight(self):
        # Base según la prioridad (Alta suma 2000, Media 1000, Baja 0)
        base = self.priority * 1000
        
        # Diferencia de días
        hoy = datetime.date.today()
        diferencia_dias = abs((self.due_date - hoy).days)
        
        # Restar 10 por cada día de diferencia
        peso_fecha = diferencia_dias * 10
        
        # Tie breaker aleatorio: DEBE ser menor que 10 para que no anule la fecha
        # (Si fuera de 0 a 100, el azar tendría más peso que 10 días de diferencia)
        tie_breaker = random.randint(0, 9)
        
        return base - peso_fecha - tie_breaker

    def __str__(self):
        nombres = {0: "Baja", 1: "Media", 2: "Alta"}
        nivel = nombres.get(self.priority, str(self.priority))
        return f"[{self.id}] {self.description} ({nivel} - {self.due_date}) Peso: {self.weight}"

    def __repr__(self):
        return self.__str__()

    def has_more_priority(self, otra):
        """
        Verdad si esta tarea tiene mayor peso que 'otra'.
        """
        return self.weight > otra.weight