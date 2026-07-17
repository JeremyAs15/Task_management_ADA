# tests/test_task_manager.py
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.task import Task
from services.task_manager import TaskManager


def test_ejemplo_del_pdf():
    m = TaskManager()

    # 0=Baja, 1=Media, 2=Alta
    m.add_task(Task(101, "Estudiar para el examen", 2, date(2026, 7, 20)))
    m.add_task(Task(102, "Comprar útiles", 1, date(2026, 7, 18)))
    m.add_task(Task(103, "Revisar correos", 0))

    urgente = m.get_most_urgent()
    assert urgente.id == 101

    t = m.find_task(102)
    assert t is not None
    assert t.description == "Comprar útiles"

    print("OK: ejemplo del PDF")
    print("Más urgente:", urgente)
    print("Buscar 102:", t)


def test_create_task_id_automatico():
    m = TaskManager()
    t1 = m.create_task("Primera", 1)
    t2 = m.create_task("Segunda", 2)
    t3 = m.create_task("Tercera", 0)

    assert t1.id == 1
    assert t2.id == 2
    assert t3.id == 3
    assert m.find_task(2).description == "Segunda"
    assert m.get_most_urgent().id == 2  # Alta
    print("OK: create_task asigna IDs automáticos")


def test_complete_urgent_sincroniza():
    m = TaskManager()
    m.add_task(Task(101, "Alta", 2))
    m.add_task(Task(102, "Media", 1))

    completada = m.complete_urgent()
    assert completada.id == 101

    assert m.find_task(101) is None
    assert m.get_most_urgent().id == 102

    ids = [t.id for t in m.list_tasks()]
    assert ids == [102]
    print("OK: complete_urgent sincroniza heap + AVL")


def test_complete_by_id_sincroniza():
    m = TaskManager()
    m.add_task(Task(101, "Alta", 2))
    m.add_task(Task(102, "Media", 1))
    m.add_task(Task(103, "Baja", 0))

    completada = m.complete_by_id(102)
    assert completada.id == 102
    assert m.find_task(102) is None
    assert m.get_most_urgent().id == 101

    ids = [t.id for t in m.list_tasks()]
    assert ids == [101, 103]
    print("OK: complete_by_id sincroniza heap + AVL")


def test_no_duplicar_ids():
    m = TaskManager()
    ok1 = m.add_task(Task(101, "Una", 0))
    ok2 = m.add_task(Task(101, "Otra", 2))

    assert ok1 is True
    assert ok2 is False
    assert m.find_task(101).description == "Una"
    print("OK: no duplica IDs")


def test_balance_report_desde_manager():
    m = TaskManager()
    for i in range(1, 6):
        m.add_task(Task(i, f"T{i}", 1))

    report = m.balance_report()
    assert len(report) == 5
    for _, _, balance in report:
        assert -1 <= balance <= 1
    print("OK: balance_report desde TaskManager")


def test_editar_solo_descripcion():
    m = TaskManager()
    t = m.create_task("Texto viejo", 1)
    updated = m.update_description(t.id, "Texto nuevo")
    assert updated is not None
    assert m.find_task(t.id).description == "Texto nuevo"
    assert m.update_description(t.id, "   ") is None  # vacío no vale
    print("OK: update_description solo cambia el texto")


if __name__ == "__main__":
    test_ejemplo_del_pdf()
    test_create_task_id_automatico()
    test_complete_urgent_sincroniza()
    test_complete_by_id_sincroniza()
    test_no_duplicar_ids()
    test_balance_report_desde_manager()
    test_editar_solo_descripcion()
    print("\nTodas las pruebas TaskManager pasaron.")
