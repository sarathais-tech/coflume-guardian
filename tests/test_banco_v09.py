"""Banco da v0.9 (questoes/banco_v09.csv): 36 perguntas, layout na ST7735, viabilidade e histórico."""

import hashlib
from collections import Counter

from guardia.banco import APTA, LayoutTFT, analisar, carregar_banco
import pytest

from guardia.politica import problemas_de_viabilidade
from tests.conftest import RAIZ

V07 = RAIZ / "questoes" / "banco_v07.csv"
V08 = RAIZ / "questoes" / "banco_v08.csv"
V09 = RAIZ / "questoes" / "banco_v09.csv"

# Os bancos anteriores não mudam.
SHA_BANCO_V07 = "6f6115c58954a568d5c6a7aeead62986bf2cdc91fbcf1b516e15f48d04216b09"
SHA_BANCO_V08 = "5e9c14e22ae5dd1d4af3f494038a4bb1e8ba41c6839b7847513fc80134d06daa"

LAYOUT = LayoutTFT.paisagem(
    escala=2, escala_moldura=1, linhas_cabecalho=2, linhas_rodape=0, linhas_separadoras=0, margem_px=16
)


def test_bancos_anteriores_preservados():
    assert hashlib.sha256(V07.read_bytes()).hexdigest() == SHA_BANCO_V07
    assert hashlib.sha256(V08.read_bytes()).hexdigest() == SHA_BANCO_V08


def test_tres_perguntas_por_celula_e_ids_unicos():
    perguntas = carregar_banco(V09)
    assert len(perguntas) == 36
    assert Counter((p.nivel, p.categoria) for p in perguntas) == Counter({(n, c): 3 for n in range(3) for c in range(4)})
    assert len({p.id for p in perguntas}) == 36 and len({p.enunciado for p in perguntas}) == 36
    assert Counter(p.correta for p in perguntas) == Counter({"A": 9, "B": 9, "C": 9, "D": 9})
    for p in perguntas:
        assert len(set(p.alternativas.values())) == 4, p.id


def test_historicas_preservadas_e_novas_rastreaveis():
    v08 = {p.id: p for p in carregar_banco(V08)}
    for p in carregar_banco(V09):
        if p.id in v08:  # mantidas byte a byte (exceto a linha do CSV)
            assert p == p.__class__(**{**v08[p.id].__dict__, "linha_csv": p.linha_csv}), p.id
        elif p.id in ("V07-EXP-1-R1", "V07-DES-1-R1"):  # revisões de formato aprovadas
            original = v08[p.id.removesuffix("-R1")]
            assert (p.nivel, p.categoria, p.alternativas, p.correta) == \
                (original.nivel, original.categoria, original.alternativas, original.correta)
        else:
            assert p.origem == "nova-v0.9" and p.id.startswith("V09-"), p.id
    ids = {p.id for p in carregar_banco(V09)}
    # Substituídas na revisão de dificuldade e na da pergunta da água: os ids antigos não voltam.
    assert not ids & {"V09-DES-MAT-2", "V09-DES-POR-1", "V09-DES-POR-2", "V09-DES-LOG-2", "V09-DES-CG-2",
                      "V09-DES-CG-3", "V09-MES-LOG-2"}
    assert len([i for i in ids if i in v08]) == 11


def test_todas_aptas_na_st7735_e_viaveis_no_fluxo08():
    perguntas = carregar_banco(V09)
    r = analisar(perguntas, LAYOUT)
    assert [a.pergunta.id for a in r.avaliacoes if a.situacao != APTA] == []
    assert max(a.linhas_tela["pergunta"] for a in r.avaliacoes) <= LAYOUT.altura_px - 16
    assert r.adicionais_necessarias(3) == 0 and r.problemas_viabilidade() == []
    celulas = {(p.nivel, p.categoria) for p in perguntas}
    assert problemas_de_viabilidade(lambda n, c: (n, c) in celulas) == []


def test_viavel_na_politica_gradual():
    """A política gradual é experimental (branch exp/politica-gradual); sem ela, este teste é pulado."""
    gradual = pytest.importorskip("guardia.politica_gradual")
    celulas = {(p.nivel, p.categoria) for p in carregar_banco(V09)}
    assert gradual.problemas_de_viabilidade_gradual(lambda n, c: (n, c) in celulas) == []


def test_texto_compativel_com_a_fonte_da_tela():
    for p in carregar_banco(V09):
        texto = p.enunciado + p.dica + "".join(p.alternativas.values())
        assert all(ord(ch) < 128 or ch == "ê" for ch in texto), p.id


def test_pergunta_da_agua_substituida():
    v = {p.id: p for p in carregar_banco(V09)}
    gelo = v["V09-DES-CG-4"]
    assert gelo.enunciado == "Estado do gelo?" and gelo.alternativas[gelo.correta] == "Solido"
    assert not any("ferve" in p.enunciado.lower() for p in v.values())
