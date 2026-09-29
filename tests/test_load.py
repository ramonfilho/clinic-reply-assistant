import pandas as pd

from clinic_reply.load import load_export, split_name_prefix


def test_messages_come_out_in_chronological_order(raw_dir):
    messages = load_export(raw_dir).messages
    first = messages[messages["conversation_id"] == "chat-1"]
    assert list(first["message_id"]) == ["m1", "m2", "m3", "m4"]


def test_bold_prefix_becomes_the_attendant_and_leaves_the_text(raw_dir):
    messages = load_export(raw_dir).messages
    prefixed = messages[messages["message_id"] == "m3"].iloc[0]
    assert prefixed["attendant"] == "Bia Prado"
    assert prefixed["text"] == "Posso te passar a campanha?"
    assert prefixed["author"] == "human"


def test_clinic_message_without_an_author_is_unknown(raw_dir):
    messages = load_export(raw_dir).messages
    template = messages[messages["message_id"] == "m4"].iloc[0]
    assert template["sender"] == "clinic"
    assert template["author"] == "unknown"
    assert pd.isna(template["attendant"])


def test_patient_messages_and_names(raw_dir):
    export = load_export(raw_dir)
    assert set(export.messages.loc[export.messages["sender"] == "patient", "author"]) == {"patient"}
    assert export.patient_names == {"Marina Castro", "Caio Nunes"}
    assert export.attendant_names == {"Bia Prado"}
    # The profile name is kept apart for the PII step and is not a column of the table.
    assert "Marina Castro" not in export.messages.to_string()


def test_split_name_prefix_without_prefix_returns_the_text():
    assert split_name_prefix("Oi, tudo bem?") == (None, "Oi, tudo bem?")
    assert split_name_prefix("*Bia Prado*\r\n\r\nOi") == ("Bia Prado", "Oi")
