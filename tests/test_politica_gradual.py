"""Política gradual (experimento gradual-v2-exp): regras, lacunas no banco e fallbacks."""

import itertools
import math
import random

import pytest

from guardia import contrato as C
from guardia import politica as P
from guardia import politica_gradual as G
from guardia.politica_gradual import Anterior, decidir_pergunta_gradual as decidir

CELULAS = [(n, c) for n in range(C.N_NIVEIS) for c in range(C.N_CATEGORIAS)]


def banco(sem=()):
    """Banco com todas as 12 células, menos as de ``sem``."""
    vazias = set(sem)
    return lambda n, c: (n, c) not in vazias


def previsor(tabela):
    return lambda n, c: tabela[n]


# --- Níveis compatíveis -------------------------------------------------------------------

@pytest.mark.parametrize("ini,ant,acertou,esperado", [
    (1, 1, True, [0, 1, 2]), (1, 1, False, [0, 1]),
    (1, 0, True, [0, 1]), (1, 0, False, [0]),          # de 0 não pula para 2
    (1, 2, True, [1, 2]), (1, 2, False, [1, 2]),
    (0, 0, True, [0, 1]), (0, 0, False, [0]), (0, 1, False, [0, 1]),
    (2, 2, True, [1, 2]), (2, 2, False, [1, 2]), (2, 1, False, [1]),
])
def test_niveis_compativeis(ini, ant, acertou, esperado):
    assert G.niveis_compativeis(1, ini, Anterior(ant, acertou)) == esperado


def test_compativeis_exigem_anterior_valido():
    with pytest.raises(ValueError):
        G.niveis_compativeis(1, 1, None)
    with pytest.raises(ValueError):
        G.niveis_compativeis(1, 0, Anterior(2, True))  # 2 não é permitido para inicial 0
    assert G.niveis_compativeis(0, 2, None) == [2]


def test_primeira_pergunta_no_nivel_escolhido():
    for ini in range(3):
        d = decidir(0, ini, [3, 1, 0, 2], banco(), previsor({0: .9, 1: .9, 2: .9}), None)
        assert d.nivel == ini and d.motivo == P.MOTIVO_PERGUNTA_1 and d.categoria == 3


# --- Escolha pela MLP, fallbacks e explicações -------------------------------------------

def test_mlp_escolhe_entre_compativeis():
    # Desafiante, errou no nível 1: Mestre (0,70 exato) é excluído.
    d = decidir(1, 1, [0, 2], banco(), previsor({0: .95, 1: .60, 2: .70}), Anterior(1, False))
    assert d.candidatos == (0, 1) and d.nivel == 1 and d.motivo == P.MOTIVO_GUARDIA
    assert d.nivel_sem_regra == 2 and d.limitou and d.previsoes == {0: .95, 1: .60, 2: .70}
    # Acertou: Mestre é permitido e escolhido.
    d = decidir(1, 1, [0, 2], banco(), previsor({0: .95, 1: .60, 2: .70}), Anterior(1, True))
    assert d.nivel == 2 and not d.limitou


@pytest.mark.parametrize("ruim", [C.INVALIDO, math.nan, math.inf, 1.5, -0.01])
def test_previsao_invalida_em_candidato_mantem_o_anterior(ruim):
    d = decidir(2, 1, [0], banco(), previsor({0: .70, 1: ruim, 2: .70}), Anterior(0, True))
    assert d.motivo == P.MOTIVO_PREVISAO_INVALIDA and d.nivel == 0 and d.p_previsto == .70  # p do nível apresentado, que é válida
    assert d.nivel_sem_regra is None and not d.limitou


def test_previsao_invalida_fora_dos_candidatos_nao_bloqueia_a_mlp():
    # Errou no 1: o nível 2 não é candidato, então sua previsão inválida não importa para a escolha.
    d = decidir(1, 1, [0], banco(), previsor({0: .72, 1: .40, 2: math.nan}), Anterior(1, False))
    assert d.motivo == P.MOTIVO_GUARDIA and d.nivel == 0 and d.nivel_sem_regra is None


def test_sem_modelo_mantem_o_anterior():
    for ini, ant, ac in itertools.product(range(3), range(3), (True, False)):
        if abs(ant - ini) > 1:
            continue
        d = decidir(1, ini, [0], banco(), None, Anterior(ant, ac))
        assert d.motivo == P.MOTIVO_SEM_MODELO and d.nivel == ant and d.previsoes == {}


def test_sem_modelo_com_lacuna_vai_para_o_mais_proximo_sem_subir_apos_erro():
    # Mestre errou no 2; a categoria 0 só tem nível 1 -> 1 (desce, nunca sobe).
    d = decidir(1, 2, [0], banco(sem=[(2, 0)]), None, Anterior(2, False))
    assert d.nivel == 1 and d.motivo == P.MOTIVO_SEM_MODELO


# --- Bancos com lacunas ------------------------------------------------------------------

def test_caso_da_v1_sobe_apos_erro_foi_corrigido():
    """Caso que a v1 errava: Matemática só no Mestre, erro em Desafiante."""
    tem = banco(sem=[(0, 0), (1, 0)])
    d = decidir(1, 1, [0, 2, 3], tem, previsor({0: .80, 1: .40, 2: .65}), Anterior(1, False))
    assert d.categoria == 2 and d.categoria_substituida and d.categoria_fluxo08 == 0
    assert d.nivel in (0, 1) and d.nivel <= 1


def test_preserva_a_ordem_sorteada_entre_categorias_viaveis():
    tem = banco(sem=[(0, 3), (1, 3), (0, 1), (1, 1)])  # categorias 3 e 1 só têm Mestre
    d = decidir(1, 1, [3, 1, 2, 0], tem, None, Anterior(1, False))
    assert d.categoria == 2  # pula 3 e 1, fica com a próxima viável na ordem (2, não 0)


def test_sem_nenhuma_categoria_compativel_recusa_explicitamente():
    tem = banco(sem=[(0, 0), (1, 0), (0, 2), (1, 2)])
    with pytest.raises(G.SemNivelCompativelError):
        decidir(1, 1, [0, 2], tem, previsor({0: .7, 1: .7, 2: .7}), Anterior(1, False))
    # O fluxo-0.8, no mesmo banco, cairia em Mestre logo após o erro:
    d08 = P.decidir_pergunta(1, 1, [0, 2], tem, previsor({0: .7, 1: .2, 2: .7}))
    assert d08.nivel == 2


def test_viabilidade_detecta_banco_impossivel():
    assert G.problemas_de_viabilidade_gradual(banco()) == []
    assert G.problemas_de_viabilidade_gradual(banco(sem=CELULAS))  # banco vazio
    # Só Desafiante em Matemática e só Mestre no resto: após erro na P1 não há para onde ir.
    so = {(1, 0)} | {(2, c) for c in range(4)}
    problemas = G.problemas_de_viabilidade_gradual(lambda n, c: (n, c) in so)
    assert any("P1 erro" in p for p in problemas)


def _rodar_partida(rng, tem, ini, ordem_cat, modo):
    """Partida com previsões e respostas aleatórias; confere a regra a cada pergunta."""
    restantes, anterior = list(ordem_cat), None
    for k in range(3):
        if modo == "sem_modelo":
            prever = None
        else:
            tabela = {n: rng.choice([rng.random(), rng.random(), C.INVALIDO, math.nan, 1.3])
                      if modo == "com_invalidas" else rng.random() for n in range(3)}
            prever = previsor(tabela)
        d = decidir(k, ini, restantes, tem, prever, anterior)
        assert d.nivel in d.niveis_permitidos and d.nivel in d.candidatos and tem(d.nivel, d.categoria)
        if k == 0:
            assert d.nivel == ini
        else:
            assert abs(d.nivel - anterior.nivel) <= 1
            assert anterior.acertou or d.nivel <= anterior.nivel
        # categoria = primeira viável na ordem sorteada
        primeira = next(c for c in restantes if any(tem(n, c) for n in d.niveis_compativeis))
        assert d.categoria == primeira
        restantes.remove(d.categoria)
        anterior = Anterior(d.nivel, rng.random() < 0.5)
    assert len(set(ordem_cat) - set(restantes)) == 3


def test_bancos_com_lacunas_nunca_violam_a_regra():
    rng = random.Random(2026)
    viaveis = inviaveis = partidas = recusas = 0
    for _ in range(400):
        sem = rng.sample(CELULAS, rng.randint(0, 7))
        tem = banco(sem)
        problemas = G.problemas_de_viabilidade_gradual(tem)
        viaveis += not problemas
        inviaveis += bool(problemas)
        for _ in range(12):
            ini, ordem_cat = rng.randrange(3), rng.sample(range(4), 4)
            modo = rng.choice(["mlp", "com_invalidas", "sem_modelo"])
            try:
                _rodar_partida(rng, tem, ini, ordem_cat, modo)
                partidas += 1
            except (G.SemNivelCompativelError, P.BancoIncompletoError):
                recusas += 1
                assert problemas, "recusa num banco que a verificação declarou viável"
    assert viaveis > 50 and inviaveis > 50 and partidas > 2000


def test_igual_ao_fluxo08_quando_a_regra_nao_atua():
    """Banco completo: se o fluxo-0.8 escolhe um nível compatível, a escolha é a mesma."""
    rng = random.Random(7)
    iguais = 0
    for _ in range(3000):
        ini = rng.randrange(3)
        ant = rng.choice([n for n in range(3) if abs(n - ini) <= 1])
        anterior = Anterior(ant, rng.random() < .5)
        tab = {n: rng.random() for n in range(3)}
        d08 = P.decidir_pergunta(1, ini, [0, 1], banco(), previsor(tab))
        dg = decidir(1, ini, [0, 1], banco(), previsor(tab), anterior)
        assert dg.categoria == d08.categoria and dg.nivel_sem_regra == d08.nivel
        if d08.nivel in dg.niveis_compativeis:
            assert dg.nivel == d08.nivel and not dg.limitou
            iguais += 1
        else:
            assert dg.limitou
    assert iguais > 2000


def test_regras_de_jogo_inalteradas():
    assert P.N_PERGUNTAS == 3 and P.ACERTOS_PARA_DESBLOQUEIO == 2 and P.ALVO_P_ACERTO == 0.70
    assert [P.desbloqueio_referencia(list(a)) for a in itertools.product((False, True), repeat=3)].count(True) == 4
