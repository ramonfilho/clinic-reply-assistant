from clinic_reply.load import load_export
from clinic_reply.turns import content_words, pair_turns, turns_of


def test_content_words_drop_greetings_and_acknowledgments():
    assert content_words("Oi, bom dia! Sim, pode ser") == []
    assert content_words("Quero saber o valor do botox") == [
        "quero",
        "saber",
        "o",
        "valor",
        "do",
        "botox",
    ]


def test_turns_group_consecutive_messages_of_one_side(raw_dir):
    messages = load_export(raw_dir).messages
    turns = turns_of(messages[messages["conversation_id"] == "chat-1"])
    assert [turn.sender for turn in turns] == ["patient", "clinic"]
    # The out-of-hours template has no author and is left out of the clinic turn.
    assert turns[1].text == "Oi Marina, tudo bem?\nPosso te passar a campanha?"
    assert turns[1].attendant == "Bia Prado"


def test_a_case_needs_a_human_reply(raw_dir):
    pairs = pair_turns(load_export(raw_dir).messages)
    assert list(pairs["conversation_id"]) == ["chat-1"]  # chat-2 never got a reply
    case = pairs.iloc[0]
    assert case["query"].startswith("Quero saber da campanha")
    assert case["reply"] == "Oi Marina, tudo bem?\nPosso te passar a campanha?"
    assert case["attendant"] == "Bia Prado"
    assert case["is_query"]
