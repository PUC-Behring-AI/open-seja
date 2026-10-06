from pytest_bdd import given, when, then, parsers


@given("o usuário tem uma conta")
def _a():
    pass


@when("o usuário informa a senha certa")
def _b():
    pass


@then(parsers.parse("o sistema abre a {coisa}"))
def _c(coisa):
    pass
