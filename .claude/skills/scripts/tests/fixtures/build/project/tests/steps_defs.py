"""Fixture step definitions (named without test_ so no runner collects them)."""
from pytest_bdd import given, parsers, then, when


@given("que a lista de tarefas está vazia")
def empty_list(tasks):
    assert tasks.tasks == {}


@when(parsers.parse('eu marco a tarefa "{title}" como feita'))
def mark_done(tasks, title):
    tasks.mark_done(title)


@then(parsers.parse('a lista mostra a tarefa "{title}" como feita'))
def shows_done(tasks, title):
    assert tasks.tasks[title] is True


@then(parsers.parse('a lista mostra a tarefa "{title}" como pendente'))
def shows_pending(tasks, title):
    assert tasks.tasks[title] is False


@then("a lista mostra algo")
def always_fails():
    assert False


@then("a lista mostra outra coisa")
def raises_always():
    raise AssertionError("ainda nao existe")


@then("a lista mostra algo se houver")
def conditional(tasks):
    if not tasks.tasks:
        raise AssertionError("vazia")
