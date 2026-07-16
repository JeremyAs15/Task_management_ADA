# tests/test_task_manager.py
from datetime import date
from models.task import Task
from services.task_manager import TaskManager


def test_ejemplo_del_pdf():
    m = TaskManager()

    m.add_task(Task(101, "Estudiar para el examen", 3, date(2026, 7, 20)))
    m.add_task(Task(102, "Comprar útiles", 2, date(2026, 7, 18)))
    m.add_task(Task(103, "Revisar correos", 1))

    # la más urgente es la 101
    urgente = m.get_most_urgent()
    assert urgente.id == 101

    # buscar por ID en AVL
    t = m.find_task(102)
    assert t is not None
    assert t.description == "Comprar útiles"

    print("OK: ejemplo del PDF")
    print("Más urgente:", urgente)
    print("Buscar 102:", t)


def test_complete_urgent_sincroniza():
    m = TaskManager()
    m.add_task(Task(101, "Alta", 3))
    m.add_task(Task(102, "Media", 2))

    completada = m.complete_urgent()
    assert completada.id == 101

    # ya no debe existir en ninguna estructura
    assert m.find_task(101) is None
    assert m.get_most_urgent().id == 102

    ids = [t.id for t in m.list_tasks()]
    assert ids == [102]
    print("OK: complete_urgent sincroniza heap + AVL")


def test_complete_by_id_sincroniza():
    m = TaskManager()
    m.add_task(Task(101, "Alta", 3))
    m.add_task(Task(102, "Media", 2))
    m.add_task(Task(103, "Baja", 1))

    completada = m.complete_by_id(102)
    assert completada.id == 102
    assert m.find_task(102) is None
    assert m.get_most_urgent().id == 101  # sigue siendo la más urgente

    ids = [t.id for t in m.list_tasks()]
    assert ids == [101, 103]
    print("OK: complete_by_id sincroniza heap + AVL")


def test_no_duplicar_ids():
    m = TaskManager()
    ok1 = m.add_task(Task(101, "Una", 1))
    ok2 = m.add_task(Task(101, "Otra", 3))

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


if __name__ == "__main__":
    test_ejemplo_del_pdf()
    test_complete_urgent_sincroniza()
    test_complete_by_id_sincroniza()
    test_no_duplicar_ids()
    test_balance_report_desde_manager()
    print("\nTodas las pruebas TaskManager pasaron.")