# Proposta: banco de 36 perguntas (`questoes/banco_v09.csv`)

**Situação:** PROPOSTA para revisão. **Não substitui** o banco atual: o firmware v0.9 (r2 e r3) continua com o `banco_v08.csv`, de 13 perguntas. O `banco_v08.csv`, o `banco_v07.csv` e o `ORIGEM_GUARDIA.json` (origem histórica do modelo) **não mudam**. O campo `revisado_por` está vazio de propósito.

**Versão:** `banco_v09`. Arquivo novo; nada foi sobrescrito. No firmware, a versão e o hash do banco ficam em um manifesto próprio, `BANCO_FIRMWARE.json` (ver seção 7).

## 1. Resumo

| Item | Valor |
|---|---|
| Perguntas | **36**: 3 por célula (3 níveis × 4 categorias) |
| Mantidas do banco v0.8 | **11 sem mudança** e **2 com revisão de formato**, aprovadas (`V07-EXP-1-R1`, `V07-DES-1-R1`) |
| Novas | **23** (`origem = nova-v0.9`, ids `V09-…`). Nesta revisão, **6 foram trocadas** por questão de dificuldade (seção 2) |
| Posição da resposta certa | **9 A, 9 B, 9 C, 9 D**. Cada substituta manteve a letra correta da pergunta que substituiu |
| Ids | Únicos. Enunciados sem repetição. Alternativas distintas em cada pergunta |
| Texto | Mesma convenção do banco atual: **sem acentos**, porque a fonte da tela não tem `ã`. A única exceção continua sendo o `ê` de "potências" (V07-MES-1-R1), já convertido pelo firmware |

## 2. Revisão da progressão de dificuldade

### Critério usado

As perguntas históricas (v0.7/v0.8) servem de âncora para cada nível. As novas foram comparadas com elas, célula por célula.

| Nível | O que exige | Âncoras históricas |
|---|---|---|
| Explorador | Um passo; fato do dia a dia ou regra geral | 6 x 7; Casa/Caza; 1,3,5,7; Qual e um planeta? |
| Desafiante | Dois passos, ou uma regra escolar específica / exceção | 12 x 8; Plural de flor (-es); 2,4,8,16; Qual e um mamifero? |
| Mestre | Abstração ou regra composta | Binário 1010; "Ontem eles ___ bola"; Fibonacci; phishing; senha forte |

Esses níveis continuam sendo **estimativas de quem escreveu**. Só o piloto mede a taxa de acerto real de cada `id`.

### Substituições propostas

As perguntas históricas não foram mexidas. As 6 trocas são todas em perguntas novas da proposta anterior. As substitutas recebem **ids novos**, para a revisão ficar rastreável. As antigas não chegaram a ser usadas.

| Sai | Por quê | Entra | Por que é Desafiante/Mestre |
|---|---|---|---|
| V09-DES-POR-1 "Oposto de alto?" | Antônimo de palavra cotidiana: tão fácil quanto "Plural de bola" (Explorador) | **V09-DES-POR-3** "Feminino de ator?" → Atriz | Feminino irregular (-triz): regra específica, como "flor → flores" |
| V09-DES-POR-2 "Qual escrita esta certa?" (Escola) | Grafia sem dúvida real; mais fácil que "Casa/Caza" (Explorador) | **V09-DES-POR-4** "Qual escrita esta certa?" → Tigela | Dúvida real de G/J antes de E; erro comum na escola |
| V09-DES-MAT-2 "72 dividido por 9?" | Tabuada direta, mesmo nível de "6 x 7" (Explorador) | **V09-DES-MAT-3** "96 dividido por 4?" → 24 | Dois passos (metade da metade), como "12 x 8 = 10x8 + 2x8" |
| V09-DES-LOG-2 "Intruso: 2,4,7,8" | Par/ímpar resolve num olhar; equivale ao intruso de Explorador | **V09-DES-LOG-3** "Intruso: 6,12,18,22" → 22 | Todos pares: só a tabuada do 6 separa o intruso |
| V09-DES-CG-2 "Qual e um inseto?" | Mais fácil que "Patas da aranha?" (Explorador), e a dica dava a resposta pelo nº de patas | **V09-DES-CG-4** "Estado do gelo?" → Solido (ver seção 2.1) | Fato escolar de ciências (estados físicos da matéria), no nível de "Qual e um mamifero?" |
| V09-MES-LOG-2 "A>B e B>C. Maior?" | Transitividade em um passo: abaixo de Fibonacci e de "2,6,12,20" | **V09-MES-LOG-3** "Continue: 3,5,9,17" → 33 | Regra composta (dobrar e tirar 1, ou diferenças que dobram) |

### As demais perguntas novas

| id | Avaliação |
|---|---|
| V09-EXP-MAT-1, -MAT-2, -POR-1, -POR-2, -LOG-1, -CG-2 | Manter: um passo, abaixo das âncoras de Explorador |
| V09-EXP-LOG-2 "Continue: A,C,E,G" | Manter, **observar no piloto**: pular letras pode ser mais difícil que pular números |
| V09-EXP-CG-1 "Patas da aranha?" | Manter, **observar no piloto**: depende de um fato específico |
| V09-DES-MAT-1, -LOG-1, -CG-1 | Manter: dois passos ou fato escolar |
| V09-MES-MAT-1, -MAT-2, -POR-1, -POR-2, -LOG-1, -CG-1 | Manter: porcentagem, fração, coletivo, grafia com XC, sequência composta, fato específico |

### 2.1 A pergunta da água (revisão de 08/11)

A substituta anterior, **V09-DES-CG-3** "Quantos graus ferve a agua?" → 100, deixava a condição "ao nível do mar, em Celsius" só na dica. A revisão pediu a condição no enunciado. Todas as redações testadas passam do limite da tela (no máximo 2 linhas de 13 colunas, ou seja, 112 px):

| Redação testada | Altura da tela de pergunta |
|---|---|
| "Ao nivel do mar, a agua ferve a quantos graus Celsius?" | 160 px |
| "Nivel do mar: agua ferve a quantos graus C?" | 144 px |
| "Agua ferve a quantos C ao nivel do mar?" | 128 px |
| "Agua ferve no nivel do mar a (Celsius):" | 128 px |
| "Ferve a agua (mar, Celsius)?" | 128 px |
| "Nivel do mar, Celsius: agua ferve a?" | 128 px |

Por isso a pergunta foi trocada por outra de dificuldade equivalente, do mesmo tema escolar (a água e os estados físicos da matéria). Ela não precisa de condição para ter uma única resposta:

- **V09-DES-CG-4** "Estado do gelo?" → **Solido** (Liquido, Gasoso e Plasma são os outros estados). Dica: "Tem forma propria, como uma pedra". Tela de pergunta: 112 px, apta. Mantém a letra A, então as respostas continuam 9 por letra.
- **Reserva, se a equipe preferir outro tema:** "Quem bombeia o sangue?" → Coracao (Pulmao, Figado, Rim). Também apta, com 112 px. Não está no CSV.

A V09-DES-CG-3 não chegou a ser usada; o id fica reservado e não é reaproveitado.

As telas antes/depois estão em `firmware/v0.9-r4/docs/banco_v09_substituicoes.png` (coflume).

## 3. Revisões de formato (aprovadas)

| id atual → proposto | Mudança | Motivo |
|---|---|---|
| V07-EXP-1 → **V07-EXP-1-R1** | "Quanto e 6 x 7?" → "**6 x 7 = ?**" | A quebra de linha separava a conta |
| V07-DES-1 → **V07-DES-1-R1** | "Quanto e 12 x 8?" → "**12 x 8 = ?**" | Mesmo problema |

As outras 11 perguntas do banco v0.8 foram mantidas **byte a byte**.

## 4. As 36 perguntas

| id | Origem | Nível | Categoria | Enunciado | A | B | C | D | Correta | Dica |
|---|---|---|---|---|---|---|---|---|---|---|
| V07-EXP-1-R1 | v0.7-revisada | Explorador | Matemática | 6 x 7 = ? | 36 | 42 | 48 | 40 | B | 6 grupos de 7 |
| V09-EXP-MAT-1 | nova-v0.9 | Explorador | Matemática | 8 + 5 = ? | 13 | 12 | 14 | 15 | A | Complete 10 primeiro |
| V09-EXP-MAT-2 | nova-v0.9 | Explorador | Matemática | 15 - 7 = ? | 7 | 8 | 9 | 6 | B | Quanto falta de 7 para 15? |
| V07-EXP-3-R1 | v0.7-revisada | Explorador | Português | Qual palavra esta correta? | Caza | Casa | Kasa | Casza | B | S entre vogais tem som de Z |
| V09-EXP-POR-1 | nova-v0.9 | Explorador | Português | Rima com gato? | Pato | Peixe | Bola | Mesa | A | Termina em -ato |
| V09-EXP-POR-2 | nova-v0.9 | Explorador | Português | Plural de bola? | Bolaz | Boles | Bolas | Bolass | C | Acrescente S no final |
| V08-EXP-LOG-1 | nova-v0.8 | Explorador | Lógica | Continue: 1,3,5,7 | 8 | 9 | 10 | 11 | B | Pule de 2 em 2 |
| V09-EXP-LOG-1 | nova-v0.9 | Explorador | Lógica | Qual e o intruso? | Uva | Pera | Sapo | Kiwi | C | Separe por tipo |
| V09-EXP-LOG-2 | nova-v0.9 | Explorador | Lógica | Continue: A,C,E,G | J | K | H | I | D | Pule uma letra |
| V07-EXP-2 | v0.7 | Explorador | Conhecimentos gerais | Qual e um planeta? | Lua | Sol | Marte | Nuvem | C | Orbita o Sol |
| V09-EXP-CG-1 | nova-v0.9 | Explorador | Conhecimentos gerais | Patas da aranha? | 4 | 6 | 10 | 8 | D | Mais que um inseto |
| V09-EXP-CG-2 | nova-v0.9 | Explorador | Conhecimentos gerais | Qual animal voa? | Coruja | Gato | Peixe | Cavalo | A | Tem penas e asas |
| V07-DES-1-R1 | v0.7-revisada | Desafiante | Matemática | 12 x 8 = ? | 86 | 94 | 96 | 108 | C | 10x8 + 2x8 |
| V09-DES-MAT-1 | nova-v0.9 | Desafiante | Matemática | Metade de 46? | 23 | 22 | 24 | 26 | A | Metade de 40 + metade de 6 |
| V09-DES-MAT-3 | nova-v0.9 | Desafiante | Matemática | 96 dividido por 4? | 22 | 23 | 24 | 26 | C | Metade da metade de 96 |
| V08-DES-POR-1 | nova-v0.8 | Desafiante | Português | Plural de flor? | Flors | Flores | Floris | Floros | B | Se termina em R, use ES |
| V09-DES-POR-3 | nova-v0.9 | Desafiante | Português | Feminino de ator? | Atora | Atoa | Atriza | Atriz | D | Como imperador e imperatriz |
| V09-DES-POR-4 | nova-v0.9 | Desafiante | Português | Qual escrita esta certa? | Tijela | Tegela | Tijella | Tigela | D | Mesma letra de GELO |
| V07-DES-3 | v0.7 | Desafiante | Lógica | Proximo: 2,4,8,16... | 18 | 24 | 30 | 32 | D | Dobra a cada vez |
| V09-DES-LOG-1 | nova-v0.9 | Desafiante | Lógica | Continue: 1,4,9,16 | 25 | 20 | 23 | 32 | A | 1x1, 2x2, 3x3... |
| V09-DES-LOG-3 | nova-v0.9 | Desafiante | Lógica | Intruso: 6,12,18,22 | 6 | 12 | 18 | 22 | D | Pense na tabuada do 6 |
| V07-DES-2 | v0.7 | Desafiante | Conhecimentos gerais | Qual e um mamifero? | Tubarao | Golfinho | Polvo | Sardinha | B | Respira ar |
| V09-DES-CG-1 | nova-v0.9 | Desafiante | Conhecimentos gerais | Maior oceano da Terra? | Indico | Artico | Atlantico | Pacifico | D | O nome lembra paz |
| V09-DES-CG-4 | nova-v0.9 | Desafiante | Conhecimentos gerais | Estado do gelo? | Solido | Liquido | Gasoso | Plasma | A | Tem forma propria, como uma pedra |
| V07-MES-1-R1 | v0.7-revisada | Mestre | Matemática | Binario 1010 = decimal? | 8 | 9 | 10 | 12 | C | Use potências de 2 |
| V09-MES-MAT-1 | nova-v0.9 | Mestre | Matemática | 25% de 80? | 20 | 15 | 25 | 40 | A | 25% e um quarto |
| V09-MES-MAT-2 | nova-v0.9 | Mestre | Matemática | 3/4 de 20? | 12 | 15 | 16 | 5 | B | Ache 1/4 e multiplique por 3 |
| V08-MES-POR-1 | nova-v0.8 | Mestre | Português | Ontem eles ___ bola. | jogou | jogaram | jogam | joga | B | Eles: plural. Ontem: passado |
| V09-MES-POR-1 | nova-v0.9 | Mestre | Português | Coletivo de lobos? | Alcateia | Cardume | Enxame | Rebanho | A | Coletivo e o nome do grupo |
| V09-MES-POR-2 | nova-v0.9 | Mestre | Português | Qual esta certa? | Exceso | Esceso | Excesso | Ecesso | C | Vem de EXCEDER |
| V08-MES-LOG-1 | nova-v0.8 | Mestre | Lógica | Continue: 1,1,2,3,5 | 6 | 7 | 8 | 9 | C | Some os dois anteriores |
| V09-MES-LOG-1 | nova-v0.9 | Mestre | Lógica | Continue: 2,6,12,20 | 26 | 28 | 30 | 32 | C | Some 4, depois 6, depois 8 |
| V09-MES-LOG-3 | nova-v0.9 | Mestre | Lógica | Continue: 3,5,9,17 | 33 | 31 | 25 | 34 | A | Dobre e tire 1 |
| V07-MES-2-R1 | v0.7-revisada | Mestre | Conhecimentos gerais | Phishing e... | Backup | Golpe digital | Antivirus | Hardware | B | Engana o usuario |
| V07-MES-3 | v0.7 | Mestre | Conhecimentos gerais | Qual senha e melhor? | 123456 | senha123 | nome2026 | G7!mP2#x | D | Unica e aleatoria |
| V09-MES-CG-1 | nova-v0.9 | Mestre | Conhecimentos gerais | Planeta mais perto do Sol? | Venus | Terra | Marte | Mercurio | D | Tem nome de deus mensageiro |

## 5. Por que cada resposta nova é a única correta

| id | Justificativa |
|---|---|
| V09-EXP-MAT-1 | 8 + 5 = 13 |
| V09-EXP-MAT-2 | 15 − 7 = 8 |
| V09-EXP-POR-1 | Só "Pato" termina em "-ato" como "gato" |
| V09-EXP-POR-2 | Palavra terminada em vogal faz plural com -S: "bolas"; as outras formas não existem |
| V09-EXP-LOG-1 | Uva, pera e kiwi são frutas; sapo é animal |
| V09-EXP-LOG-2 | A, C, E, G pulam uma letra: a próxima é I |
| V09-EXP-CG-1 | Aranhas têm 8 patas; insetos têm 6 |
| V09-EXP-CG-2 | Entre as opções, só a coruja voa |
| V09-DES-MAT-1 | 46 ÷ 2 = 23 |
| V09-DES-MAT-3 | 96 ÷ 4 = 24 (96 → 48 → 24) |
| V09-DES-POR-3 | O feminino de "ator" é "atriz"; as outras formas não existem |
| V09-DES-POR-4 | "Tigela" se escreve com G; tijela, tegela e tijella não existem |
| V09-DES-LOG-1 | Quadrados perfeitos: 1, 4, 9, 16, **25** |
| V09-DES-LOG-3 | 6, 12 e 18 são múltiplos de 6 (e de 3); 22 não é. Todos são pares, então paridade não separa: o intruso é só o 22 |
| V09-DES-CG-1 | O Pacífico é o maior oceano da Terra |
| V09-DES-CG-4 | O gelo é água no estado sólido; líquido e gasoso são a água e o vapor, e plasma não se aplica |
| V09-MES-MAT-1 | 25% de 80 = 80 ÷ 4 = 20 |
| V09-MES-MAT-2 | 1/4 de 20 = 5; 3 × 5 = 15 |
| V09-MES-POR-1 | Coletivo de lobos: alcateia. Cardume é de peixes, enxame de abelhas, rebanho de gado |
| V09-MES-POR-2 | Só "Excesso" é grafia existente (família de "exceder") |
| V09-MES-LOG-1 | Diferenças +4, +6, +8, +10: 20 + 10 = 30 |
| V09-MES-LOG-3 | Cada termo é o dobro do anterior menos 1 (17 × 2 − 1 = 33); as diferenças +2, +4, +8, +16 levam ao mesmo 33 |
| V09-MES-CG-1 | Mercúrio é o planeta mais próximo do Sol |

**Dicas:** podem ensinar o caminho da resposta (decisão da revisão). Exemplos: "Metade da metade de 96", "Como imperador e imperatriz".

## 6. Validação

| Verificação | Resultado |
|---|---|
| `validar_banco`, layout da ST7735 (paisagem 160×128, corpo em tamanho 2, cabeçalho de 2 linhas, margem de 16 px) | **36 de 36 aptas**; 0 a ajustar; 0 inválidas. 12 de 12 células com 3 perguntas |
| Viabilidade no **fluxo-0.8** | **Todas as partidas viáveis** |
| Viabilidade na **política gradual** (`problemas_de_viabilidade_gradual`, todos os caminhos) | **Viável** |
| **Firmware r3 real** compilado com o `coflume_banco.h` gerado do `banco_v09.csv` (cópia temporária; a r3 não muda) | **196 telas, 0 cortes e 0 sobreposições** com a Guardiã ligada e desligada; partidas no fluxo-0.8 sem falha |
| Firmware r3 real, regra gradual ligada | **150 partidas, 0 recusas**, alternando com o Agente Secreto; `banco_viavel_gradual=1` |
| Conteúdo | Ids únicos; enunciados sem repetição; alternativas distintas; 9 respostas em cada posição; só ASCII, exceto o `ê` já tratado |

A pergunta da água foi substituída na revisão de 08/11 (seção 2.1).

## 7. Versão e hash no firmware (v0.9-r4)

Integrado no firmware experimental **v0.9-r4** do `coflume` (`firmware/v0.9-r4/`). Ele **ainda não foi testado na placa física**. A r2 e a r3 continuam com o `banco_v08`.

| Arquivo (na r4) | Conteúdo |
|---|---|
| `ferramentas/banco_v09.csv` | Cópia byte a byte de `questoes/banco_v09.csv` |
| `ferramentas/gerar_banco_v09.py` | Cópia do gerador da v0.8 com versão e origem como parâmetros. O original continua fixo em `banco_v08` e não muda. Recusa gerar com o nome `banco_v08` |
| `coflume_v09/coflume_banco.h` | Gerado: `COFLUME_BANCO_VERSAO "banco_v09"`, `COFLUME_BANCO_CSV_SHA256`, `COFLUME_BANCO_N 36` |
| `BANCO_FIRMWARE.json` | Versão, hash do CSV, hash do `.h` gerado, contagens, banco anterior e modelo (inalterado). Separado do `ORIGEM_GUARDIA.json`, que não muda |

A linha de boot da r4 traz a versão **e** o hash:

```
COFLUME,versao=v0.9-agente-usb-experimental-r4,banco=banco_v09,perguntas=36,banco_csv_sha256=<sha256>
```

## 8. Pontos para a revisão da equipe

1. Aprovar as 6 substituições da seção 2. A da água foi trocada pela V09-DES-CG-4 (seção 2.1). As revisões de formato das multiplicações já estão aprovadas.
2. Confirmar as duas perguntas marcadas para observar no piloto.
3. Conferir as 36 perguntas na **tela física** (teste F3 de `docs/testes/coflume-v0.9-r4.md` no `coflume`).
