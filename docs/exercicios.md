# Resolução dos exercícios e experimentos

## 0. Recapitulação

Na linha de montagem de um compilador, o analisador léxico transforma caracteres
em tokens. O parser verifica a organização desses tokens, e a análise semântica
verifica significados e restrições. Só depois vêm etapas como geração e
otimização de código.

Na metáfora do restaurante, o lexer é o funcionário que separa e etiqueta os
ingredientes. Ele reconhece as peças; quem monta o prato é o parser.

- **Token:** categoria, por exemplo `PRECO`.
- **Lexema:** trecho reconhecido, por exemplo `R$ 25,90`.
- **Padrão:** regra que reconhece o trecho, normalmente uma regex.
- **Atributo convertido:** valor útil obtido do lexema, como `Decimal('25.90')`.

Comentários e espaços não são entregues como tokens nas linguagens que usam
`%ignore`, mas suas posições continuam contando para linha e coluna.

## 1. Exercício 1 - Tokenização manual

Entrada com a gramática original A2:

```text
# almoço
pedido 3X "Pastel de Queijo" R$ 8,50
PAGAMENTO Cartão
```

| TOKEN | LEXEMA | LINHA | COLUNA |
|---|---|---:|---:|
| PEDIDO | `pedido` | 2 | 1 |
| QTD | `3X` | 2 | 8 |
| TEXTO | `"Pastel de Queijo"` | 2 | 11 |
| PRECO | `R$ 8,50` | 2 | 30 |
| PAGAMENTO | `PAGAMENTO` | 3 | 1 |
| FORMA_PGTO | `Cartão` | 3 | 11 |

O comentário ocupa a primeira linha, mas não produz token. O modificador `/i`
permite as variações de caixa. As colunas são contadas a partir de 1.

## 2. Exercício 2 - Prioridades no B1 original

| Entrada | Resultado | Justificativa |
|---|---|---|
| `em@banco.com` | `CHAVE_EMAIL` | Prioridade 4 vence a reservada `EM`, de prioridade 3. O `@` permite que `\b` case após `em`, por isso a fronteira sozinha não resolve. |
| `EMPRESA` | Erro em L1, C1, `E` | Depois de `EM` há uma letra, então `em\b` não casa; B1 não tem identificador genérico. |
| `+5511987654321` | `CHAVE_TELEFONE` | Casa com `\+55\d{10,11}`, prioridade 2; os demais padrões não reconhecem esse início completo. |
| `09:45` | `HORA` | Casa com `\d{2}:\d{2}`, prioridade 2. No B1 original não existe token `NUMERO` concorrente. |

## 3. Exercício 3 - Primeiro erro léxico

O erro está na **linha 2, coluna 27, caractere `j`**:

```text
PIX ENVIADO R$ 45,00 PARA joao@@mail.com EM 01/09/2026 10:00
                          ^
```

O e-mail não casa porque o segundo `@` não pertence ao padrão da parte de domínio.
Nenhum outro token do B2 original reconhece o início `j`. O lexer informa a
posição em que não conseguiu começar um token, e não necessariamente a posição
do caractere que um humano identificaria como a causa do erro.

## 4. Exercício 4 - Expressões regulares

```lark
RASTREIO_COD: /[A-Z]{2}\d{9}[A-Z]{2}/
PLACA: /[A-Z]{3}\d[A-Z]\d{2}/
CEP: /\d{5}-\d{3}/
```

- Rastreio: duas letras maiúsculas, nove dígitos, duas letras maiúsculas.
- Placa: três letras, um dígito, uma letra e dois dígitos.
- CEP: cinco dígitos, hífen e três dígitos.

Exemplos válidos: `BR123456789BR`, `ABC1D23` e `01310-100`.
Esses padrões conferem formatos, não a existência dos registros. No teste
isolado usamos `re.fullmatch`, que exige que a entrada inteira corresponda.

## 5. Exercício 5 - Cupom GANHEI100

A existência e a validade do cupom pertencem à **análise semântica**, como regra
de negócio. A sequência `GANHEI100` tem formato de identificador e pode virar
`CODIGO` normalmente. A verificação de existência exige consultar o conjunto de
cupons aceitos. Colocar essa consulta no lexer misturaria reconhecimento de
caracteres com regras que podem mudar sem alterar a linguagem.

Na implementação, `comanda` mantém a tokenização válida, recusa o desconto e
apresenta um aviso. O tokenizador não consulta `CUPONS`.

## 6. Exercícios guiados

### 6.1 A1 - Observações

Acrescentamos o literal `OBS: "OBS"` às definições. A função `compilar` inclui
automaticamente o nome na alternativa `_token`.

```text
PEDIDO 1x "Pizza" R$ 50,00 OBS "sem cebola"
```

Sequência esperada: `PEDIDO QTD ITEM PRECO OBS ITEM`. O A1 continua sensível a
maiúsculas, como o exemplo de partida.

### 6.2 A2 - VR e DESC20

`vr` foi incluído na alternativa de `FORMA_PGTO.3`. `DESC20` foi adicionado à
tabela de cupons com fração `Decimal('0.20')`.

```text
PEDIDO 2x "Pizza" R$ 50,00
TAXA R$ 10,00
CUPOM DESC20
PAGAMENTO vr
```

Subtotal: R$ 100,00. Desconto: R$ 20,00. Taxa: R$ 10,00. **Total: R$ 90,00**.
O desconto incide sobre os itens, antes da taxa. Valores usam `Decimal` e o
desconto é arredondado para centavos, evitando resíduos de ponto flutuante.

### 6.3 B1 - CNPJ

```lark
CHAVE_CNPJ.2: /\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}/
```

`12.345.678/0001-90` vira `CHAVE_CNPJ`. O CPF pontuado começa com três dígitos
antes do primeiro ponto, e o CNPJ com dois; os padrões se distinguem pela forma.

### 6.4 B2 - Saque

Adicionamos `SAQUE.3: /saque\b/i` ao lexer e tratamos o saque como débito no
pós-processamento.

```text
SALDO INICIAL R$ 300,00
SAQUE R$ 200,00 EM 05/09/2026 18:00
```

O valor da transação é **-R$ 200,00** e o saldo final é **R$ 100,00**. O resumo
rejeita a estrutura `SAQUE RECEBIDO ...`, mesmo que suas peças sejam tokens válidos.

## 7. Exercícios de nível desafio

### 7.1 A2 - Preço sem R$

```lark
PRECO.2: /(R\$ ?)?\d{1,3}(\.\d{3})*,\d{2}(?![\w,.])/
```

O grupo `(R\$ ?)?` torna o símbolo e seu espaço opcionais. `25,90` e
`R$ 25,90` viram `PRECO`.

**Conflito:** `NUMERO` consegue reconhecer o prefixo `25` de `25,90`. A prioridade
2 de `PRECO` vence a prioridade padrão 0 de `NUMERO`. `QTD.2` mantém prioridade
2; seu padrão exige `x`, enquanto o preço exige vírgula e centavos, portanto
os padrões não reconhecem a mesma sequência completa. Em `25x`, o token é `QTD`.

O lookahead negativo `(?![\w,.])` impede aceitar apenas o início de um preço
com centavos excedentes, como `25,900`. Mantivemos o agrupamento de milhar do
roteiro: use `1.250,00`, e não `1250,00`.

### 7.2 B2 - Telefone sem +55

```lark
CHAVE_TELEFONE.2: /(\+55\d{10,11}|\d{11})(?![\w+])/
```

Aceita `+5511987654321` e `11987654321`. A segunda alternativa tem exatamente
11 dígitos, conforme o exemplo solicitado. Telefone local com 10 dígitos não
foi incluído nesta extensão.

**Nova ambiguidade:** telefone local e CPF sem pontuação podem ter os mesmos
11 dígitos. Não é possível descobrir a intenção somente pela regex. Nesta
linguagem, CPF continua exigindo pontuação e 11 dígitos sem separadores são
classificados como telefone. Assim, `12345678909` também é telefone nesta versão,
enquanto no B2 original produz erro. Isso é uma convenção, não validação cadastral.

Para aceitar os dois formatos sem adivinhação, uma evolução seria exigir um
indicador explícito, como `TIPO CPF` ou `TIPO TELEFONE`, ou fornecer o tipo da
chave em outro campo. Só aumentar prioridades escolheria arbitrariamente um tipo.

### 7.3 B2 - Alerta de chave aleatória

Após a tokenização e conciliação, verificamos conjuntamente:

1. Operação `PIX`.
2. Valor negativo, indicando saída.
3. Chave do tipo `CHAVE_ALEATORIA`.
4. Módulo do valor estritamente maior que `Decimal('500.00')`.

A mensagem é **PIX para chave aleatória acima de R$ 500,00**. Testamos R$ 500,00
(sem alerta), R$ 500,01 (com alerta) e PIX recebido (sem esse alerta). O sinal
serve para revisar o exemplo; não prova irregularidade.

## 8. Experimentos e reflexões do roteiro

### A1: preço sem prioridade

Retirar `.2` de `PRECO` deixa `CODIGO` capturar `R` em `R$ 25,90`; o erro
ocorre no `$`. Restaurar a prioridade faz o preço ser um único token. A célula
de experimento e o teste automático reproduzem as duas situações.

### A1: PEDIDOS e pedido

`PEDIDOS` vira `CODIGO`, porque não é exatamente a reservada literal `PEDIDO`.
`pedido` em minúsculas falha no A1, cujo identificador também exige maiúsculas.
O A2 usa `/i` para as reservadas e aceita identificadores com letras minúsculas.

### A2: por que 8.50 falha no ponto?

Na entrada sem símbolo monetário, `8` pode casar com `NUMERO`. O lexer avança e
encontra `.`, que não inicia nenhum token naquele contexto. Ele não pode prever
que o autor pretendia escrever um preço. A extensão continua exigindo vírgula.

### B1: pix@loja.com.br

Com e-mail na prioridade 4, ele vence `PIX.3`. Ao baixar para 2, `PIX` captura
o início e sobra `@`. O slider da interface reconstrói a gramática para
demonstrar isso. O teste usa a posição do `@` no texto efetivamente analisado.

### B2: resultados do extrato

Saldo inicial R$ 2.500,00; entradas R$ 3.250,00; saídas R$ 1.987,30; saldo final
R$ 3.762,70. São oito transações e seis chaves, abrangendo cinco categorias
léxicas de chave (e-mail, CPF, CNPJ, telefone e aleatória).

O alerta noturno utiliza o intervalo didático de 20h até antes de 6h e valor
estritamente acima de R$ 1.000,00 para PIX de saída. A máscara pode ser ligada
e desligada sem modificar os tokens usados no cálculo.

### Discussão: tokenizador de LLM e lexer de compilador

**Semelhança:** ambos transformam uma sequência de caracteres em unidades
menores que serão consumidas por outra etapa.

**Diferença:** neste compilador, as categorias e padrões são definidos
explicitamente pelo projetista. Em métodos como BPE, o vocabulário é construído
a partir de frequências de sequências em dados. Um token de LLM pode ser só um
fragmento de palavra e não corresponde necessariamente a uma categoria como
`PRECO`. Depois de definido o vocabulário, a tokenização não precisa reaprender
essas unidades a cada texto.

## 9. Entrega final e autoavaliação

O desafio completo está descrito em `linguagem.md`. A autoavaliação individual
fica em `guia_apresentacao.md`, com perguntas para responder antes da entrega.
Ela deve ser marcada pelo estudante após estudar e executar os exemplos.
