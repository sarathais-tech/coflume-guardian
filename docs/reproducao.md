# Reprodução do treinamento da Guardiã IA

O fluxo usa dados sintéticos e avalia os modelos no conjunto de validação. Python 3.11 foi usado no treinamento de referência. Execute os comandos na raiz do repositório.

## 1. Preparar o ambiente

```bash
git clone https://github.com/sarathais-tech/coflume-guardian.git
cd coflume-guardian
python -m venv .venv
```

Ative o ambiente conforme seu terminal:

| Terminal | Comando |
|---|---|
| Windows PowerShell | `.\.venv\Scripts\Activate.ps1` |
| Windows Prompt de Comando | `.venv\Scripts\activate.bat` |
| Linux ou macOS | `source .venv/bin/activate` |

```bash
python -m pip install -r requirements-treino.txt
```

## 2. Gerar os dados sintéticos

```bash
python -m ferramentas.gerar_sinteticos --semente 2026
```

O simulador gera `dados/sinteticos/sessoes_v2.csv`. O treino usa a divisão por participante já versionada em [`splits/split_v2.json`](../splits/split_v2.json). Para regenerar a divisão a partir do CSV, execute `python -m ferramentas.dividir`.

## 3. Treinar e comparar os modelos

```bash
python -m ferramentas.treinar --saida resultados/reproducao-local --salvar-modelos modelos/reproducao-local
```

O comando treina baseline, árvore de decisão, regressão logística e MLP. Abra `resultados/reproducao-local/validacao.json` para consultar métricas como log loss e ROC-AUC. A MLP candidata é salva em `modelos/reproducao-local/mlp_candidata.npz`. O conjunto de teste permanece lacrado.

Compare com as [métricas de referência](../resultados/sinteticos/treino_v2/validacao.json). As versões de Python e das bibliotecas estão registradas no JSON, e CPU e dependências podem afetar o resultado do novo treino.

## 4. Exportar o modelo da InovaTech para C++

Depois de gerar os dados no passo 2, execute:

```bash
python -m ferramentas.exportar_bancada --saida embarcado/bancada_reproduzida
```

A exportação usa os pesos de referência versionados e confere o hash do relatório de validação registrado em [`ORIGEM.json`](../resultados/sinteticos/treino_v2/ORIGEM.json). A saída contém `guardia_modelo.h`, `guardia_runtime.h` e os arquivos da bancada. O modelo da feira é **`mlp8-sint-20261101-e6a4cf00`**, com arquitetura **13 → 8 → 1**. A [release do Coflume](https://github.com/sarathais-tech/coflume/releases/tag/v0.9-r4-inovatech) contém o firmware que usa esses pesos.

## 5. Verificar a integração

```bash
python -m pytest -q tests/test_bancada_wokwi.py
```

Os testes de equivalência com C++ usam `g++` ou `clang++`. Para executar a bancada no ESP32-S3 simulado, siga o [guia do Wokwi](bancada_wokwi.md). Para acompanhar o modelo escolhendo a dificuldade durante um Quiz, siga a [demonstração do Coflume](https://github.com/sarathais-tech/coflume#experimente-a-guardiã-ia).
