# Política adaptativa gradual (experimento `gradual-v2-exp`)

**Situação:** EXPERIMENTO na branch local `exp/politica-gradual`. **Não aprovado e não integrado ao firmware.** O firmware v0.9 r2 continua com o [fluxo-0.8](fluxo_partida.md).
**Referência:** [`guardia/politica_gradual.py`](../guardia/politica_gradual.py) · **Testes:** [`tests/test_politica_gradual.py`](../tests/test_politica_gradual.py)
**Porta em C++:** `coflume/firmware/experimentos/politica_gradual/coflume_politica_gradual.h`, comparada com esta referência.
**Origem:** revisão da proposta "Adaptação Gradual v1", que voltava silenciosamente a uma escolha fora da regra quando o banco tinha lacunas.

> Esta política é uma **proteção** da escolha de dificuldade. Ela **não melhora a precisão da rede neural**, não muda o modelo, os pesos nem o contrato 1.0.0 e **não comprova melhora na aprendizagem dos participantes**. Todos os números abaixo são **[SINTÉTICO]**.

## 1. O que muda em relação ao fluxo-0.8

Nada muda em:
- a primeira pergunta, no nível escolhido;
- as 3 perguntas, de 30 s cada;
- a dica e o tempo esgotado contando como erro;
- 3 categorias distintas em ordem sorteada;
- o alvo de 0,70 e o desempate;
- a abertura com 2 acertos em 3, decidida pelo validador do firmware;
- a modalidade Agente Secreto, que não usa a política.

A mudança está só nas **perguntas 2 e 3**. Um nível é **compatível** quando, ao mesmo tempo:

1. está entre os permitidos do fluxo-0.8 (nível inicial ± 1, limitado a 0..2);
2. difere **no máximo 1 nível** do nível da pergunta anterior;
3. depois de **erro ou tempo esgotado**, **não é maior** que o nível anterior.

| Nível inicial | Anterior | Resultado anterior | Compatíveis |
|---|---|---|---|
| Desafiante (1) | 1 | acerto / erro | 0, 1, 2 / 0, 1 |
| Desafiante (1) | 0 | acerto / erro | 0, 1 / 0 |
| Desafiante (1) | 2 | acerto / erro | 1, 2 / 1, 2 |
| Explorador (0) | 0 | acerto / erro | 0, 1 / 0 |
| Mestre (2) | 2 | acerto / erro | 1, 2 / 1, 2 |
| Mestre (2) | 1 | acerto / erro | 1, 2 / 1 |

O nível anterior é sempre compatível. Por isso, só falta opção compatível quando **o banco** não tem perguntas nas células compatíveis.

## 2. Decisão de cada pergunta

1. **Categoria:** a **primeira** das categorias restantes, **na ordem sorteada**, que tenha pergunta em algum nível **compatível**. A ordem sorteada é preservada entre as categorias viáveis. A troca fica registrada em `categoria_substituida` e `categoria_fluxo08`.
2. **Candidatos:** os níveis compatíveis que têm pergunta nessa categoria.
3. **Previsões:** a Guardiã avalia todos os níveis disponíveis da categoria, para o log. A escolha usa só os candidatos.
4. **Escolha:**

| Situação | Nível | `motivo` |
|---|---|---|
| Pergunta 1 | Nível inicial | `nivel_inicial_pergunta_1` |
| Modelo indisponível (desativado ou reprovado no autoteste) | Candidato **mais próximo do nível anterior** (empate: o mais baixo). Com o anterior disponível, **mantém o nível**. | `fallback_sem_modelo` |
| Previsão `INVALIDO`, NaN ou fora de [0, 1] em **algum candidato** | O mesmo: mais próximo do nível anterior | `fallback_previsao_invalida` |
| Previsões válidas em todos os candidatos | Candidato com P(acerto) mais próxima de **0,70**; empate como no fluxo-0.8 (prefere o inicial; depois, o mais baixo) | `guardia` |
| **Nenhuma categoria restante com nível compatível** | **Nenhum.** A decisão é recusada (`SemNivelCompativelError` em Python; `viavel=false` em C++) | `sem_nivel_compativel` |

Uma previsão inválida num nível que **não** é candidato não muda a escolha, porque esse nível não poderia ser apresentado.

**Nenhum fallback viola a regra:** todos escolhem entre os candidatos. Quando não há candidato, não existe "volta" à escolha sem a regra.

### 2.1 Quando não há nível compatível

- **Antes da partida:** `problemas_de_viabilidade_gradual(tem_pergunta)`, ou `gradual::banco_viavel()` em C++, percorre:
  - 3 níveis iniciais × 24 ordens de categorias;
  - acerto ou erro nas perguntas 1 e 2;
  - **qualquer** nível que a pergunta 2 possa receber, já que a escolha depende das previsões.

  Se a verificação passa, a recusa **não pode** acontecer. Os testes confirmam isso em 400 bancos aleatórios, em Python e em C++.
- **No firmware (proposta, ainda não implementada):** é a mesma regra que o fluxo-0.8 já define para banco inviável (seção 3.1, item 4). Se o banco não passar na verificação ao ligar, a partida adaptativa **não começa**, e a tela mostra "BANCO INCOMPLETO". A recusa durante a partida fica só como proteção defensiva: tela de erro, servo fechado, nenhuma pergunta fora da regra.

### 2.2 O banco precisa de cobertura melhor

A regra gradual é mais exigente com o banco do que o fluxo-0.8:
- **Banco atual** (13 perguntas, as 12 células preenchidas): **viável.**
- **12 bancos com uma célula vazia:** todos **viáveis**.
- **20 bancos aleatórios com 2 a 7 células vazias:** **15 inviáveis** para a regra gradual. **11 deles são viáveis no fluxo-0.8.**

**Exemplo:** sem Desafiante em Português e em Conhecimentos gerais, o seguinte acontece:
1. a criança começa em Mestre e acerta ou erra a pergunta 1, de Matemática, no nível 2;
2. a pergunta 2, de Lógica, cai no nível 1, e ela **erra**;
3. na pergunta 3, o único nível compatível é o 1, e as categorias restantes (Português e Conhecimentos gerais) não têm Desafiante.

O fluxo-0.8 subiria para Mestre depois do erro. A regra gradual recusa.

**Consequência:** a ampliação para 36 perguntas, com 3 por célula, atende à regra. Antes de usar qualquer banco, ele deve passar em `problemas_de_viabilidade_gradual`.

## 3. Comparação Python × C++ com a MLP real

O gerador `firmware/experimentos/politica_gradual/ferramentas/gerar_referencia_gradual.py`, no `coflume`, usa:
- esta referência;
- a MLP `mlp8-sint-20261101-e6a4cf00` carregada do `.npz` (com o hash conferido).

Os bancos são o completo, os 12 com uma célula vazia e 20 aleatórios com 2 a 7 células vazias.

Cenários por banco:
- 3 níveis iniciais × 24 ordens × 16 combinações de resposta nas perguntas 1 e 2;
- os perfis de resposta são: acerto em 3 s, acerto em 15 s com dica, erro em 12 s e tempo esgotado.

Nos 5 primeiros bancos, as mesmas partidas também rodam **sem modelo** e com **previsão inválida (NaN) no nível 2**.

| Resultado | Valor |
|---|---|
| Partidas / decisões | 49.536 / 144.706 |
| Decisões iguais em Python e C++ (categoria, nível, motivo, escolha sem a regra) | **todas** |
| Recusas `sem_nivel_compativel` iguais nas duas linguagens, só em bancos inviáveis | 3.710 partidas, nos 15 bancos inviáveis |
| Viabilidade dos 33 bancos igual nas duas linguagens | sim |
| Maior diferença de P(acerto) entre Python e o runtime C++ | 1,19e-7 |

Testes com previsões aleatórias (C++, 400 bancos com lacunas, 4.800 partidas) confirmaram três coisas:
- a regra nunca foi violada;
- a categoria é sempre a primeira viável da ordem sorteada;
- só houve recusa em bancos que a verificação declarou inviáveis.

Também rodaram com AddressSanitizer e UndefinedBehaviorSanitizer, sem erros.

## 4. Efeito (proteção, não melhoria de precisão)

Medido com a MLP real, no **banco completo**:

| Cenários | Decisões | Alteradas pela regra |
|---|---|---|
| Referência acima (acertos a partir de 3 s) | 3.456 | **0** |
| Varredura ampla: 3 níveis × 24 ordens × 24 perfis por pergunta (acerto ou erro × 2, 4, 6, 10, 20 ou 30 s × dica) | 124.416 | **448 (0,36%)**, todas na pergunta 3 |

Na varredura ampla, das 448 alterações:
- 330 impediram uma **subida depois de erro**;
- 118 impediram um **salto de 2 níveis** entre perguntas seguidas (por exemplo, 0 → 2 a partir de Desafiante).

Nas outras 99,64% das decisões, a escolha é idêntica à do fluxo-0.8. A regra serve de **proteção** contra mudanças bruscas de dificuldade: ela não aumenta a precisão da Guardiã nem mede efeito educacional.

## 5. Log proposto para o firmware

Além dos campos do fluxo-0.8 (seção 5 de `fluxo_partida.md`), a linha da decisão ganha:
- `politica=gradual-v2-exp`;
- `niveis_compativeis` e `candidatos`;
- `nivel_sem_regra`, a escolha do fluxo-0.8 na mesma categoria, quando as previsões são válidas;
- `limitou` (0 ou 1);
- `categoria_fluxo08`.

Com isso dá para auditar cada vez que a proteção atua.

## 6. Próximos passos (dependem de aprovação)

1. **Revisão** desta política e dos resultados pela equipe.
2. **Integração no firmware:** só depois da aprovação, numa revisão nova da v0.9, com:
   - `GUARDIA_POLITICA_GRADUAL`, um `#define` que comece **desligado**;
   - verificação do banco ao ligar;
   - os campos de log da seção 5;
   - testes de partida completa.

   A r2 continua com o fluxo-0.8.
3. **Fase C (teste lacrado):** o adendo 02 congelou a avaliação com o fluxo-0.8 (seção 7 do protocolo). Se a política gradual for adotada antes da fase C, isso precisa de **novo adendo**, escrito **antes** de abrir o teste.

## Histórico

| Data | Revisão | Mudança |
|---|---|---|
| 07/11/2026 | gradual-v2-exp | Primeira definição, a partir da revisão da Adaptação Gradual v1: filtro de categorias por compatibilidade, recusa explícita, fallback pelo nível anterior e verificação de viabilidade do banco |
