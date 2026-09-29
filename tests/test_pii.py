import pytest

from clinic_reply.pii import name_words, scrub


@pytest.mark.parametrize(
    "phone", ["(31) 99999-1234", "31 9 9999-1234", "+55 31 99999-1234", "31999991234", "99999-1234"]
)
def test_phone_formats(phone):
    assert scrub(f"meu número é {phone}, pode chamar") == "meu número é [PHONE], pode chamar"


def test_email_and_cpf():
    assert scrub("mande para ana.silva@email.com") == "mande para [EMAIL]"
    assert scrub("CPF 123.456.789-00, certo?") == "CPF [CPF], certo?"


def test_birth_date_goes_and_appointment_date_stays():
    text = "nasci em 12/05/1990, consulta dia 22/07 às 10:00"
    assert scrub(text) == "nasci em [DATE], consulta dia 22/07 às 10:00"


def test_names_match_whole_words_without_case_or_accents():
    names = name_words(["Marina Castro Magalhães", "Bia Prado"])
    text = "Oi MARINA, aqui é a Bia. Magalhaes, certo?"
    assert scrub(text, names) == "Oi [NAME], aqui é a [NAME]. [NAME], certo?"


def test_name_inside_another_word_is_kept():
    assert scrub("Anabela chegou", name_words(["Ana"])) == "Anabela chegou"


def test_connectives_and_short_words_are_not_names():
    words = name_words(["Maria de Souza dos Santos", "Jo Lima"])
    assert words == {"maria", "souza", "santos", "lima"}


def test_text_without_personal_data_is_unchanged():
    text = "Já vou te explicar tudo certinho sobre a campanha 🥰 dia 22/07 às 10:00"
    assert scrub(text, name_words(["Bia Prado"])) == text
