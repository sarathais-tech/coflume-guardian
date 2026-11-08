"""Política adaptativa GRADUAL (experimento) — implementação de REFERÊNCIA.

Versão: ``gradual-v2-exp``. Situação: EXPERIMENTO em ``exp/politica-gradual``,
não aprovado e não integrado ao firmware. Documento: docs/politica_gradual_exp.md.

É o fluxo-0.8 (``guardia/politica.py``) com uma PROTEÇÃO a mais nas perguntas
2 e 3: o nível só pode mudar de forma gradual em relação à pergunta anterior.

Nível COMPATÍVEL na pergunta ``ordem >= 1``:
  1. está entre os permitidos do fluxo-0.8 (nível inicial ± 1, limitado a 0..2);
  2. difere no máximo 1 do nível da pergunta anterior;
  3. se a resposta anterior foi erro ou tempo esgotado, não é maior que o
     nível anterior.

O nível anterior é sempre compatível, porque está entre os permitidos. Logo,
só falta nível compatível quando o BANCO não tem pergunta nas células
compatíveis. Esse caso é tratado de forma explícita (seção 3 do documento):
a categoria é trocada pela próxima viável da ordem sorteada; sem nenhuma, a
decisão é recusada com ``SemNivelCompativelError``. Nunca há volta silenciosa a
uma escolha que viole a regra. ``problemas_de_viabilidade_gradual`` detecta
antes da partida os bancos em que isso pode acontecer.

A Guardiã continua só estimando P(acerto). Ela não escolhe a categoria e não
participa do desbloqueio (2 acertos em 3, inalterado).
"""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass, field
from typing import Sequence

from guardia import contrato as C
from guardia.politica import (
    MOTIVO_GUARDIA,
    MOTIVO_PERGUNTA_1,
    MOTIVO_PREVISAO_INVALIDA,
    MOTIVO_SEM_MODELO,
    N_PERGUNTAS,
    Prever,
    TemPergunta,
    escolher_nivel,
    niveis_permitidos,
)

VERSAO_POLITICA = "gradual-v2-exp"
MAX_MUDANCA = 1
MOTIVO_SEM_NIVEL_COMPATIVEL = "sem_nivel_compativel"


@dataclass(frozen=True)
class Anterior:
    """Resultado da pergunta anterior, na mesma partida."""

    nivel: int
    acertou: bool  # False também para tempo esgotado


class SemNivelCompativelError(RuntimeError):
    """Nenhuma categoria restante tem pergunta em um nível compatível."""


@dataclass(frozen=True)
class DecisaoGradual:
    """Decisão de uma pergunta, com os campos do log do fluxo-0.8 e os da regra gradual."""

    ordem: int
    nivel_inicial: int
    categoria_sorteada: int
    categoria: int
    niveis_permitidos: tuple[int, ...]
    niveis_compativeis: tuple[int, ...]      # permitidos que a regra gradual aceita
    niveis_disponiveis: tuple[int, ...]      # permitidos com pergunta nesta categoria
    candidatos: tuple[int, ...]              # compatíveis E disponíveis: só entre eles se escolhe
    previsoes: dict[int, float] = field(default_factory=dict)  # de todos os disponíveis (log)
    nivel: int = 0
    p_previsto: float = C.INVALIDO
    motivo: str = MOTIVO_GUARDIA
    nivel_sem_regra: int | None = None       # o que o fluxo-0.8 escolheria NESTA categoria (só com previsões válidas)
    categoria_fluxo08: int | None = None     # categoria que o fluxo-0.8 escolheria

    @property
    def categoria_substituida(self) -> bool:
        return self.categoria != self.categoria_sorteada

    @property
    def limitou(self) -> bool:
        """A regra gradual mudou a escolha da MLP nesta categoria."""
        return self.nivel_sem_regra is not None and self.nivel_sem_regra != self.nivel


def _valida(p: float) -> bool:
    return p != C.INVALIDO and math.isfinite(p) and 0.0 <= p <= 1.0


def niveis_compativeis(ordem: int, nivel_inicial: int, anterior: Anterior | None) -> list[int]:
    """Permitidos do fluxo-0.8 que respeitam a mudança gradual."""
    permitidos = niveis_permitidos(ordem, nivel_inicial)
    if ordem == 0:
        return permitidos
    if anterior is None:
        raise ValueError("As perguntas 2 e 3 precisam do resultado da pergunta anterior.")
    if anterior.nivel not in permitidos:
        raise ValueError(f"Nível anterior {anterior.nivel} fora dos permitidos {permitidos}.")
    return [n for n in permitidos
            if abs(n - anterior.nivel) <= MAX_MUDANCA and (anterior.acertou or n <= anterior.nivel)]


def _sem_modelo(candidatos: Sequence[int], referencia: int) -> int:
    """Fallback: o candidato mais próximo da referência; empate -> o mais baixo."""
    return min(candidatos, key=lambda n: (abs(n - referencia), n))


def decidir_pergunta_gradual(
    ordem: int,
    nivel_inicial: int,
    categorias_restantes: Sequence[int],
    tem_pergunta: TemPergunta,
    prever: Prever | None,
    anterior: Anterior | None,
) -> DecisaoGradual:
    """Decide categoria e nível de uma pergunta com a regra gradual.

    1. Categoria: a PRIMEIRA das restantes, na ordem sorteada, que tenha
       pergunta em algum nível COMPATÍVEL. Nenhuma: ``SemNivelCompativelError``.
    2. Previsões: de todos os níveis disponíveis da categoria (para o log); a
       escolha considera só os candidatos (compatíveis e disponíveis).
    3. Escolha:
       - pergunta 1: nível inicial;
       - sem modelo, ou previsão inválida em algum CANDIDATO: o candidato mais
         próximo do nível ANTERIOR (empate: o mais baixo). Como o nível anterior
         é compatível, isso mantém o nível sempre que a categoria o tiver;
       - senão: candidato com P(acerto) mais próxima de 0,70 (empate como no
         fluxo-0.8: prefere o nível inicial; depois, o mais baixo).
    """
    if not categorias_restantes:
        raise ValueError("Não há categorias restantes.")
    permitidos = tuple(niveis_permitidos(ordem, nivel_inicial))
    compativeis = tuple(niveis_compativeis(ordem, nivel_inicial, anterior))

    categoria_fluxo08 = next((c for c in categorias_restantes if any(tem_pergunta(n, c) for n in permitidos)), None)
    for categoria in categorias_restantes:
        candidatos = tuple(n for n in compativeis if tem_pergunta(n, categoria))
        if candidatos:
            break
    else:
        raise SemNivelCompativelError(
            f"Pergunta {ordem + 1}: sem pergunta nos níveis compatíveis {list(compativeis)} "
            f"para as categorias {list(categorias_restantes)}."
        )
    disponiveis = tuple(n for n in permitidos if tem_pergunta(n, categoria))
    previsoes = {n: float(prever(n, categoria)) for n in disponiveis} if prever is not None else {}

    if ordem == 0:
        nivel, motivo = nivel_inicial, MOTIVO_PERGUNTA_1
    elif prever is None:
        nivel, motivo = _sem_modelo(candidatos, anterior.nivel), MOTIVO_SEM_MODELO
    elif not all(_valida(previsoes[n]) for n in candidatos):
        nivel, motivo = _sem_modelo(candidatos, anterior.nivel), MOTIVO_PREVISAO_INVALIDA
    else:
        nivel, motivo = escolher_nivel({n: previsoes[n] for n in candidatos}, nivel_inicial), MOTIVO_GUARDIA

    sem_regra = None
    if ordem > 0 and previsoes and all(_valida(p) for p in previsoes.values()):
        sem_regra = escolher_nivel(previsoes, nivel_inicial)

    assert nivel in candidatos
    p = previsoes.get(nivel, C.INVALIDO)
    return DecisaoGradual(
        ordem=ordem, nivel_inicial=nivel_inicial, categoria_sorteada=int(categorias_restantes[0]),
        categoria=int(categoria), niveis_permitidos=permitidos, niveis_compativeis=compativeis,
        niveis_disponiveis=disponiveis, candidatos=candidatos, previsoes=previsoes, nivel=nivel,
        p_previsto=p if _valida(p) else C.INVALIDO, motivo=motivo, nivel_sem_regra=sem_regra,
        categoria_fluxo08=categoria_fluxo08,
    )


def problemas_de_viabilidade_gradual(tem_pergunta: TemPergunta) -> list[str]:
    """Verifica se o banco sustenta QUALQUER partida com a regra gradual.

    Percorre os 3 níveis iniciais × 24 ordens de categorias × acerto ou erro
    nas perguntas 1 e 2 × QUALQUER nível que a pergunta 2 possa receber (a
    escolha depende das previsões, então todos os candidatos são testados).
    Se a lista voltar vazia, ``SemNivelCompativelError`` não pode ocorrer.
    """
    problemas = []
    for ini in range(C.N_NIVEIS):
        for ordem_cat in itertools.permutations(range(C.N_CATEGORIAS)):
            try:
                d1 = decidir_pergunta_gradual(0, ini, list(ordem_cat), tem_pergunta, None, None)
            except SemNivelCompativelError as e:
                problemas.append(f"nível {ini}, ordem {list(ordem_cat)}: {e}")
                continue
            rest1 = [c for c in ordem_cat if c != d1.categoria]
            for ac1 in (True, False):
                a1 = Anterior(d1.nivel, ac1)
                try:
                    d2 = decidir_pergunta_gradual(1, ini, rest1, tem_pergunta, None, a1)
                except SemNivelCompativelError as e:
                    problemas.append(f"nível {ini}, ordem {list(ordem_cat)}, P1 {'acerto' if ac1 else 'erro'}: {e}")
                    continue
                rest2 = [c for c in rest1 if c != d2.categoria]
                for n2, ac2 in itertools.product(d2.candidatos, (True, False)):
                    try:
                        decidir_pergunta_gradual(2, ini, rest2, tem_pergunta, None, Anterior(n2, ac2))
                    except SemNivelCompativelError as e:
                        problemas.append(f"nível {ini}, ordem {list(ordem_cat)}, P2 nível {n2} "
                                         f"{'acerto' if ac2 else 'erro'}: {e}")
    return problemas
