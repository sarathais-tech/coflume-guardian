# Guia da Guardiã IA: dados sintéticos, treino, avaliação, exportação, e rede × política × validador

**Para quem:** quem chega ao projeto e quer entender, sem ler todo o código, como a Guardiã foi feita e o que ela faz no cofre. Cada seção aponta para o documento detalhado.

> **Resumo honesto:** a Guardiã é uma rede neural pequena (MLP 13 → 8 → 1, 121 parâmetros), treinada **só com dados sintéticos**. Ela roda no ESP32-S3 sem internet.
> - Em validação, ficou **estatisticamente empatada** com a árvore de decisão e a regressão logística.
> - O **teste lacrado (fase C) ainda não foi aberto**.
> - A **latência na placa física** não foi medida.
> - **Nada disso comprova eficácia educacional.**

---

## 1. Rede neural, política e validador: três peças diferentes

O cofre toma decisões em três camadas, e só a primeira é Machine Learning.

| Peça | O que é | Pergunta que responde | Onde está | Pode abrir o cofre? |
|---|---|---|---|---|
| **Rede neural (MLP)** | **Machine Learning**: pesos aprendidos de dados | "Qual a chance de esta criança **acertar** uma pergunta de nível X na categoria Y?" → P(acerto) entre 0 e 1 | `guardia/mlp.py`, `inferencia_ref.py`; no firmware, `guardia_modelo.h` e `guardia_runtime.h` | **Não** |
| **Política** | **Regra escrita**, fixa e auditável | "Dadas as estimativas, **qual nível** será a próxima pergunta?" | `guardia/politica.py` (fluxo-0.8); `guardia/politica_gradual.py` (experimental, desligada); no firmware, `coflume_politica*.h` | **Não** |
| **Validador** | **Regra escrita** | Depende do validador, ver abaixo | — | Só o validador do jogo |

A palavra "validador" aparece em três lugares:

1. **Validador do jogo (firmware):** abre o servo com **2 ou mais acertos em 3** (`coflume::desbloqueia`). É a única peça do quiz que abre o cofre. No Agente Secreto, quem abre é a senha correta, conferida pelo ESP32.
2. **Validador do banco** (`guardia/banco.py`, `ferramentas/validar_banco.py`):
   - confere se cada pergunta **cabe na tela** ST7735 (quebra de linha, altura, margem);
   - confere se o banco permite **todas as partidas** da política (viabilidade).

   Não usa IA.
3. **Autoteste do modelo (firmware, no boot):** 21 vetores conferem se a rede gravada na placa dá as mesmas respostas que o Python. Se falhar, a política usa um nível de reserva **sem** a rede.

### Exemplo (log de demonstração, política gradual ligada)

Na pergunta 3, depois de um erro, a **rede** estimou:
- Desafiante **≈ 80,1%**;
- Mestre **≈ 60,0%**.

A **política** fluxo-0.8 escolheria Mestre: 10,0 pontos do alvo de 70%, contra 10,1 do Desafiante. A **proteção gradual** não deixa subir depois de erro e manteve **Desafiante**. No fim, o **validador do jogo** contou 1 acerto em 3: cofre fechado.

A rede **estima**, a política **decide o nível** e o validador **decide a abertura**.

## 2. Por que dados sintéticos

**Situação:** não há dados reais de crianças. Coletá-los exige autorização dos responsáveis e cuidados de privacidade, e o protocolo prevê isso só para um piloto ([`dados.md`](dados.md)). Por isso o treino usa **participantes simulados**.

**Simulador** ([`simulador.md`](simulador.md)) `sim-1.1`:
- **Participantes:** gera **4.000 "alunos virtuais"**, sem nenhum dado pessoal.
- **Atributos sorteados:** cada um tem uma habilidade geral, habilidade por categoria, propensão a pedir dica e velocidade.
- **Como cada um joga:** como no cofre (fluxo-0.8): 3 perguntas de categorias diferentes, pergunta 1 no nível escolhido, 30 s, dica.
- **Política exploratória:** o nível das perguntas 2 e 3 é **sorteado** dentro do permitido, e não escolhido pela Guardiã. Assim os dados não ficam enviesados pelas escolhas do próprio modelo.
- **Resultado:** **12.000 linhas**, uma por pergunta respondida. O rótulo é **acertou ou errou**, um fato observado, nunca uma regra nossa.
- **Oráculo:** o simulador também guarda a probabilidade verdadeira (`p_real`). Ela **nunca entra no treino**; serve só para medir quão perto o modelo chegou.

**Divisão por participante** ([`dados.md`](dados.md)): 70% / 15% / 15% dos **participantes**, ou seja, **2.800 / 600 / 600**. Ninguém aparece em dois conjuntos. A divisão está versionada em `splits/split_v2.json`.

**O teste é lacrado:**
- o código se recusa a abri-lo sem uma confirmação explícita;
- ele só será aberto uma vez, na fase C ([adendo 02](protocolo_adendo_02.md)).

| Dados sintéticos permitem afirmar | Não permitem afirmar |
|---|---|
| O pipeline funciona de ponta a ponta | Que a Guardiã ajuda crianças reais a aprender |
| Comparar modelos em condições controladas | Desempenho com crianças reais |

## 3. As 13 entradas da rede

Calculadas só com o que aconteceu **antes** da pergunta ([`features.md`](features.md)). São idênticas em Python e em C++, o que é testado.

| # | Entrada |
|---|---|
| 1 | Nível candidato (0, 1 ou 2): o nível que se quer avaliar |
| 2 | Nível inicial escolhido pela criança |
| 3 | Número de perguntas já respondidas |
| 4 | Taxa de acerto na sessão |
| 5 | Taxa de acerto na categoria |
| 6 | Tempo médio usado (fração do limite) |
| 7 | Dicas por pergunta |
| 8 | Resultado da última resposta (−1, 0 ou +1) |
| 9 | Sequência de acertos ou erros (−3 a +3) |
| 10–13 | Categoria da pergunta (uma entrada por categoria, valendo 1 ou 0) |

As 9 primeiras são **padronizadas** com a média e o desvio do treino. Depois vêm **8 neurônios ocultos (ReLU)** e **1 saída (sigmoide)**.

## 4. Treinamento

[`treino.md`](treino.md); decisão de treinar no CI: [ADR 0010](adr/0010-treino-oficial-no-ci.md).

1. **Quatro modelos, com os mesmos dados:**
   - baseline ingênuo (taxa por par de níveis);
   - **árvore de decisão**;
   - **regressão logística**;
   - **MLP** (Keras).
2. **Escolha de hiperparâmetros:** validação cruzada em 5 dobras **dentro do treino**, por participante. O critério é a log loss.
3. **MLP:** arquiteturas [8], [16], [16, 8] e [32, 16]. Venceu a menor a até 1% da melhor: **[8]**, com 121 parâmetros. Treino com Adam, L2 e parada antecipada.
4. **Cinco sementes** (2026 a 2030), relatadas como média ± desvio. A **candidata** é a semente **2026**, fixada **antes** de ver os resultados, para não escolher a "melhor sorte".
5. **Execução oficial no GitHub Actions** (execução 41329660286): ambiente registrado (`pip freeze`) e SHA-256 dos dados e dos resultados. Os pesos da candidata estão em `resultados/sinteticos/treino_v2/mlp_candidata.npz`.

Para reproduzir: [`reproducao.md`](reproducao.md) e [`treino.md`](treino.md), seção 3.

## 5. Avaliação

Métricas pré-registradas no [protocolo](protocolo_avaliacao.md):
- **log loss**, a principal;
- Brier;
- ROC-AUC;
- **ECE** (calibração), com o diagrama de confiabilidade;
- erro contra `p_real`.

**Validação** ([`resultados/sinteticos/treino_v2/relatorio_validacao.md`](../resultados/sinteticos/treino_v2/relatorio_validacao.md)), [SINTÉTICO]:

| Modelo | Log loss | ROC-AUC | ECE |
|---|---|---|---|
| Baseline | 0,6386 | 0,6218 | 0,0112 |
| Árvore | 0,6359 | 0,6261 | 0,0199 |
| Logística | 0,6335 | 0,6368 | 0,0257 |
| MLP (candidata, semente 2026) | 0,6346 | 0,6340 | 0,0129 |
| *Oráculo `p_real` (limite teórico)* | *0,5794* | *0,7342* | *0,0216* |

- **Comparações:** todas as comparações por bootstrap **cruzaram zero**. Em validação, os modelos estão **empatados**.
- **Calibração:** a candidata tem boa calibração (ECE baixa), mas a média das 5 sementes é maior (0,023 ± 0,005).
- **Quando a MLP vira padrão:** só no **teste lacrado (fase C)**, e só se:
  1. a log loss for melhor que a da árvore, com intervalo de confiança inteiro abaixo de zero; ou, se o intervalo cruzar zero, se a ECE for menor;
  2. **e** se passar na viabilidade embarcada, que inclui a **latência na placa física**.

  Se não passar, a árvore vira padrão e o resultado negativo é relatado ([adendo 02](protocolo_adendo_02.md)).

**Situação em 08/11/2026:**
- o teste **não foi aberto** (`resultados/sinteticos/teste_v2/teste.json` não existe);
- a latência na placa **não foi medida**;
- os firmwares v0.8 e v0.9 usam a MLP **como experimento**.

## 6. Exportação para o ESP32-S3

[`contrato_integracao.md`](contrato_integracao.md), [`viabilidade_embarcada.md`](viabilidade_embarcada.md), [`bancada_wokwi.md`](bancada_wokwi.md).

1. **`python -m ferramentas.exportar_bancada`.** Antes de gerar qualquer arquivo, o script:
   - confere o SHA-256 dos resultados do CI;
   - carrega `mlp_candidata.npz`;
   - **recalcula toda a validação** em Python e compara com as métricas registradas.
2. **`guardia/exportar/mlp_cpp.py`** gera:
   - `guardia_modelo.h`: pesos, média e desvio em float32, com 9 dígitos, para o compilador reconstruir o mesmo float; também o id e o **hash SHA-256 dos parâmetros**;
   - `vetores_teste.h`: casos de equivalência;
   - `MODELO.json`.
3. **`guardia_runtime.h`** (escrito à mão, versionado) faz as features e a inferência em C++. Contrato 1.0.0.
4. **Equivalência:** nos 400 vetores, features idênticas e erro de P(acerto) ≤ 1,2×10⁻⁷ entre Python e C++. A bancada no Wokwi deu `APROVADO_FUNCIONAL` (01/11/2026).
5. **No firmware:** o `coflume` copia `guardia_modelo.h` e `guardia_runtime.h` **byte a byte**, com os hashes em `ORIGEM_GUARDIA.json`. No boot, roda o **autoteste** com 21 vetores.

Modelo em uso: `mlp8-sint-20261101-e6a4cf00` (o prefixo `sint` indica dados sintéticos). Ele foi exportado **para a bancada** e não é uma release de produção.

### Visualização no painel

O painel USB da v0.9-r4 mostra a rede, mas não lê nada de dentro da placa. Ele **refaz a conta** no notebook com os mesmos pesos, a partir das entradas que o ESP32 envia, e **confere** com a previsão enviada pela placa. Por isso aparece como "cálculo reproduzido no painel", e não como medição interna. Detalhes em `firmware/v0.9-r4/painel/docs/rede_neural_avaliacao.md`, no repositório `coflume`.

## 7. Banco de perguntas

O banco não faz parte do modelo: a rede usa só o **nível** e a **categoria**, nunca o texto da pergunta.

| Banco | Situação |
|---|---|
| `banco_v07.csv` | Histórico |
| `banco_v08.csv` | 13 perguntas; usado na v0.8, na r2 e na r3 |
| **`banco_v09.csv`** | **36 perguntas** (3 por nível × categoria), usado na v0.9-r4. Revisão em [`banco_v09_proposta.md`](banco_v09_proposta.md). O nível das perguntas novas é estimativa de quem escreveu; o piloto pode medi-lo pelo `id` nos logs |
