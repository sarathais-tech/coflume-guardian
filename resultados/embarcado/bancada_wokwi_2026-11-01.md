# Evidência de execução — Guardiã IA no Wokwi

- Data informada pela equipe: 2026-11-01
- Ambiente: Wokwi, ESP32-S3 simulado
- Modelo: `mlp8-sint-20261101-e6a4cf00` (pesos de treino sintético)
- Hash do modelo: `e6a4cf0086ccf5ab1eccecbe7aea02f3962a6ad7ced29b136d36c5b37b5b9991`
- Arquitetura: MLP 13 → 8 → 1, 121 parâmetros
- Contrato: 1.0.0
- Origem: log serial fornecido pela equipe após execução manual no Wokwi
- Situação: **APROVADO_FUNCIONAL**, não é validação em hardware físico nem release de produção

## Log serial integral informado pela equipe

```text
ESP-ROM:esp32s3-20210327
Build:Mar 27 2021
rst:0x1 (POWERON),boot:0x8 (SPI_FAST_FLASH_BOOT)
SPIWP:0xee
mode:DIO, clock div:1
load:0x3fce3808,len:0x370
load:0x403c9700,len:0x900
load:0x403cc700,len:0x2364
entry 0x403c98ac
BANCADA,inicio,guardia_bancada_v2
BANCADA,ambiente,wokwi
BANCADA,modelo_id,mlp8-sint-20261101-e6a4cf00
BANCADA,modelo_hash,e6a4cf0086ccf5ab1eccecbe7aea02f3962a6ad7ced29b136d36c5b37b5b9991
BANCADA,modelo_fonte,SINTETICO
BANCADA,modelo_uso,bancada (nao e versao de producao)
BANCADA,contrato,1.0.0
BANCADA,n_parametros,121
BANCADA,camadas_ocultas,1
BANCADA,chip,ESP32-S3
BANCADA,cpu_mhz_configurada,240
BANCADA,sketch_bytes,355568
BANCADA,pesos_bytes,556
BANCADA,n_vetores,400
BANCADA,n_vetores_aleatorios,200
BANCADA,n_vetores_validacao,200
BANCADA,erro_p_max_aleatorios,1.1920929e-07
BANCADA,erro_p_max_validacao,1.1920929e-07
BANCADA,erro_p_max,1.1920929e-07
BANCADA,erro_features_max,0
BANCADA,falhas_inteiras,0
BANCADA,invalidos,0
BANCADA,casos_entrada_testados,46
BANCADA,casos_entrada_corretos,46
BANCADA,heap_variacao_prever_bytes,0
BANCADA,heap_variacao_montar_entrada_bytes,0
BANCADA,heap_livre_total_informativo,352144
BANCADA,heap_minimo_livre_informativo,346996
BANCADA,latencia_prever_us_media,167.808594
BANCADA,latencia_decisao_3_niveis_us_media,630.743591
BANCADA,latencia_prever_us_pior,222
BANCADA,latencia_valida,nao (CPU simulada; apenas indicativa)
BANCADA,criterio_equivalencia,APROVADO
BANCADA,criterio_entradas,APROVADO
BANCADA,criterio_sem_alocacao,APROVADO
BANCADA,resultado_funcional,APROVADO
BANCADA,criterio_latencia,NAO_AVALIADO
BANCADA,resultado,APROVADO_FUNCIONAL
BANCADA,fim,ok
```

## Interpretação e limites

- 400 vetores avaliados, sendo 200 aleatórios e 200 da validação sintética.
- Divergência máxima de probabilidade: `1.1920929e-07`, abaixo de `1e-5`.
- Features e campos inteiros sem divergências; 46/46 casos específicos corretos.
- As rotinas medidas não apresentaram alteração no heap livre antes/depois de suas chamadas; isso **não demonstra**, isoladamente, ausência de qualquer alocação transitória.
- A latência registrada pertence à simulação e não comprova a latência real do dispositivo.
- Evidência de inferência funcional offline na simulação; **não** demonstra eficácia educacional com usuários reais.
- A avaliação do conjunto de teste lacrado e a medição na placa física ainda estão pendentes.

## Rastreamento

Desenvolvimento da bancada: `sarathais-tech/coflume-guardian-ai`, branch `feat/validacao-final-ab`.
Firmware do cofre v0.7: `sarathais-tech/coflume`, preservado.

Este registro documental foi criado no repositório privado oficial; não importa automaticamente novos arquivos/commits do repositório de desenvolvimento.
