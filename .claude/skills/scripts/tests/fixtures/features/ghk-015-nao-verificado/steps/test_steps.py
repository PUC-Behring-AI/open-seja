import re
from pytest_bdd import given, when, then, parsers


@given(parsers.re(r"o usu.rio tem uma conta"))
def _a():
    pass


@when("o usuário informa a senha certa")
def _b():
    pass


@then("o sistema abre a conta")
def _c():
    pass
