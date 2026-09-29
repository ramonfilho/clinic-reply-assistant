"""A two-conversation export in the BotConversa schema, with fictional people."""

import json

import pytest


def _message(message_id, de_mim, texto, ts, atendente=None, tipo="text"):
    return {
        "id": message_id,
        "de_mim": de_mim,
        "tipo": tipo,
        "texto": texto,
        "ts": str(ts),
        "status": "read",
        "atendente": atendente,
        "media": [{"tipo": None}],
    }


@pytest.fixture
def raw_dir(tmp_path):
    """Write one export file. Messages are listed newest first, as in the real export."""
    first = {
        "chat_id": "chat-1",
        "subscriber_id": "sub-1",
        "nome": "Marina Castro",
        "canal": 1,
        "status": "read",
        "atendente": "Bia Prado",
        "ultima_msg": "m4",
        "n_msgs": 4,
        "mensagens": [
            _message("m4", True, "Prezado(a) Paciente! Estamos fora do horário.", 1_700_000_400),
            _message("m3", True, "*Bia Prado*\n\nPosso te passar a campanha?", 1_700_000_300),
            _message("m2", True, "Oi Marina, tudo bem?", 1_700_000_200, atendente="Bia Prado"),
            _message(
                "m1", False, "Quero saber da campanha. Meu número é 31 99999-1234", 1_700_000_100
            ),
        ],
    }
    second = {
        "chat_id": "chat-2",
        "subscriber_id": "sub-2",
        "nome": "Caio Nunes",
        "canal": 1,
        "status": "read",
        "atendente": None,
        "ultima_msg": "m6",
        "n_msgs": 2,
        "mensagens": [
            _message("m6", False, "", 1_700_000_600, tipo="audio"),
            _message("m5", False, "Qual o endereço?", 1_700_000_500),
        ],
    }
    block = {"bloco": 1, "n_conversas": 2, "conversas": [first, second]}
    (tmp_path / "bc_bloco01.json").write_text(json.dumps(block), encoding="utf-8")
    return tmp_path
