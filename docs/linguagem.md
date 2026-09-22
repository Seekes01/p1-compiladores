# RastreioLang - especificação e diário de ambiguidade

## 1. Cenário

Uma aplicação de logística recebe atualizações de encomendas em texto. O lexer
reconhece comandos, códigos de rastreio, status, CEP, datas, horários, peso,
frete e contatos. O tema corresponde à opção de rastreio de encomendas da P1.

Esta é uma mini-linguagem de estudo; não implementa o protocolo de uma empresa.

## 2. Exemplo completo

```text
# Atualização de encomenda
rastreio AB987654321BR status "em trânsito" cep 20040-020 em 11/09/2026 09:30 origem "São Paulo" destino "Rio de Janeiro" peso 1,250kg frete R$ 25,90 contato em@exemplo.com prazo 3 destinatario 123.456.789-09
```

Cada linha representa um evento. No **pós-processamento**, o cabeçalho obrigatório é:

```text
RASTREIO código STATUS "descrição" CEP número EM data hora
```

Depois do cabeçalho, podem aparecer pares opcionais em qualquer ordem, uma vez
cada: `ORIGEM TEXTO`, `DESTINO TEXTO`, `PESO PESO_VALOR`, `FRETE VALOR`,
`CONTATO EMAIL`, `PRAZO NUMERO`, `DESTINATARIO CPF_VALOR`.
`PRAZO` é uma quantidade inteira de dias e `PESO` está em quilogramas.

## 3. Tabela de tokens

São **22 tipos emitidos**. Comentários e espaços não entram nessa contagem.
As regex abaixo são as usadas em `DEFS_RASTREIO`, incluindo suas restrições
de término. Prioridade omitida no Lark equivale a 0.

| Token | Descrição | Regex Lark | Exemplo | Prioridade |
|---|---|---|---|---:|
| RASTREIO | Início do evento | `/rastreio\b/i` | `rastreio` | 4 |
| STATUS | Rótulo do estado | `/status\b/i` | `STATUS` | 4 |
| CEP | Rótulo do CEP | `/cep\b/i` | `CEP` | 4 |
| EM | Introduz data e hora | `/em\b/i` | `Em` | 4 |
| ORIGEM | Rótulo da origem | `/origem\b/i` | `ORIGEM` | 4 |
| DESTINO | Rótulo do destino | `/destino\b/i` | `DESTINO` | 4 |
| PESO | Rótulo do peso | `/peso\b/i` | `PESO` | 4 |
| FRETE | Rótulo do frete | `/frete\b/i` | `FRETE` | 4 |
| CONTATO | Rótulo do e-mail | `/contato\b/i` | `CONTATO` | 4 |
| PRAZO | Rótulo de dias | `/prazo\b/i` | `PRAZO` | 4 |
| DESTINATARIO | Rótulo do CPF | `/destinatario\b/i` | `DESTINATARIO` | 4 |
| EMAIL | Contato eletrônico | `/[a-z0-9._+-]+@[a-z0-9-]+(\.[a-z0-9-]+)+(?=$\|[\s#])/i` | `em@exemplo.com` | 5 |
| COD_RASTREIO | Código de encomenda | `/[A-Z]{2}\d{9}[A-Z]{2}(?=$\|[\s#])/i` | `BR123456789BR` | 3 |
| CEP_VALOR | CEP pontuado | `/\d{5}-\d{3}(?=$\|[\s#])/` | `01310-100` | 2 |
| DATA | Data no formato dia/mês/ano | `/\d{2}\/\d{2}\/\d{4}(?=$\|[\s#])/` | `10/09/2026` | 2 |
| HORA | Hora e minuto | `/\d{2}:\d{2}(?=$\|[\s#])/` | `08:15` | 2 |
| PESO_VALOR | Peso inteiro ou decimal, com kg | `/\d+(,\d{1,3})?kg(?=$\|[\s#])/i` | `1,250kg` | 2 |
| VALOR | Valor em reais | `/R\$ ?\d{1,3}(\.\d{3})*,\d{2}(?=$\|[\s#])/` | `R$ 25,90` | 2 |
| CPF_VALOR | CPF pontuado | `/\d{3}\.\d{3}\.\d{3}-\d{2}(?=$\|[\s#])/` | `123.456.789-09` | 2 |
| TEXTO | Texto entre aspas | `/"[^"\n]*"/` | `"em trânsito"` | 0 |
| NUMERO | Inteiro não negativo | `/\d+(?=$\|[\s#])/` | `3` | 0 |
| IDENTIFICADOR | Nome genérico | `/[A-Za-z_][A-Za-z0-9_]*(?=$\|[\s#])/` | `LOTE_A` | 0 |

Na tabela Markdown, `\|` escapa a barra vertical para não dividir a célula.
**No arquivo Python e na gramática Lark a alternativa é `|`, sem essa barra
de escape do Markdown.** Para copiar a gramática executável, use `p1.py` ou a
célula do notebook.

### Elementos ignorados

```lark
COMENTARIO: /#[^\n]*/
%ignore COMENTARIO
%ignore /[ \t\r\n]+/
```

Um `#` dentro de um `TEXTO` permanece parte do texto. Fora das aspas, inicia um
comentário até o fim da linha. As posições originais dos tokens são preservadas.

## 4. Como ler os padrões

- `\d`: um dígito; `{9}`: exatamente nove repetições.
- `[A-Z]`: uma letra do intervalo; `/i`: ignora diferença de caixa.
- `\b`: fronteira entre caractere de palavra e não palavra, ou limite da entrada.
  Assim `RASTREIOS` não é dividido na reservada `RASTREIO` e uma letra restante.
- `+`: uma ou mais ocorrências; `*`: zero ou mais; `?`: trecho opcional.
- `\.` e `\$`: ponto e cifrão literais.
- `[^"\n]*`: conteúdo sem aspas e sem quebra de linha.
- `(?=$|[\s#])`: olha adiante, sem consumir, e exige fim da entrada, espaço em
  branco ou começo de comentário. Evita aceitar apenas um prefixo de um campo
  maior malformado, como um CEP seguido de letras.

As 11 reservadas terminam com `\b` e têm `/i`. Datas e CPF conferem o formato;
o lexer não consulta calendário nem calcula dígitos verificadores.

## 5. Diário de ambiguidade

Na implementação, a entrada `CONTATO em@exemplo.com` mostrou um conflito entre
o e-mail e a palavra reservada `EM`. Embora `EM` use `\b`, existe uma fronteira
antes do `@`, então o prefixo ainda pode ser reconhecido como reservada. A
solução foi definir `EMAIL.5` acima das reservadas de prioridade 4. O padrão de
e-mail exige `@` e domínio, portanto `EM` sozinho continua sendo palavra
reservada. Também foi identificado que `BR123456789BR` satisfaz tanto o padrão
específico de rastreio quanto o identificador genérico. `COD_RASTREIO.3` fica
acima de `IDENTIFICADOR`, cuja prioridade é 0. Os testes reduzem essas
prioridades intencionalmente: o primeiro caso produz erro e o segundo passa a
ser identificador, comprovando por que as duas escolhas são necessárias.

### Ordem adotada

```text
5: e-mail
4: palavras reservadas
3: código de rastreio
2: literais estruturados
0: texto, inteiro e identificador
```

O Lark testa primeiro os terminais de maior prioridade. Em empates, considera
o comprimento teórico máximo do padrão, o comprimento da definição e o nome.
Por isso, não tratamos o `basic` como uma busca pelo maior lexema real entre
todos os padrões. Referência: [gramática do Lark](https://lark-parser.readthedocs.io/en/stable/grammar.html).

O identificador genérico serve para demonstrar a diferença entre reconhecimento
léxico e estrutura: `CODIGOERRADO` é uma palavra reconhecível, mas não é um
`COD_RASTREIO`. O resumo recusa seu uso onde espera um código de encomenda.

## 6. Erros e dicas

| Caso | Posição do erro | Explicação e dica |
|---|---|---|
| Status sem fechar aspas | L1 C31, `"` | Fechar o texto do status antes da quebra de linha. |
| CEP `01310.100` | L1 C45, `0` | O CEP exige hífen; nenhum token pode iniciar aquele campo completo. Dica mostra `01310-100`. |
| E-mail `em@@exemplo.com` | L1 C85, `@` | O e-mail completo falha; `EM` é reconhecido antes do `@` remanescente. Dica mostra um e-mail de entrega. |

As posições correspondem às entradas exatas de `CASOS_RASTREIO`. A mensagem
inclui linha, coluna, caractere, contexto com seta e dica. Quando ocorre erro,
as abas anteriores são limpas, para não exibir resultados de outra entrada.

## 7. Casos de teste

- **Válido 1:** evento simples com rastreio, status, CEP, data e hora; 9 tokens.
- **Válido 2:** comentário, reservadas em minúsculas, campos opcionais e o contato
  `em@exemplo.com`; 23 tokens.
- **Válido 3:** três eventos, dois códigos e repetição de frete; 33 tokens,
  duas encomendas e total R$ 35,90.
- **Inválido 1:** aspas abertas no status.
- **Inválido 2:** ponto no lugar do hífen do CEP.
- **Inválido 3:** e-mail com dois sinais `@`.

As entradas completas estão no código, no seletor da interface e no notebook.
Os testes também cobrem as prioridades, as posições, comentários, estrutura
incompleta e campos repetidos.

## 8. Bônus e separação de responsabilidades

`tokenizar_rastreio` somente reconhece tokens. `resumo_rastreio` valida o
cabeçalho e os pares opcionais, converte peso e frete com `Decimal`, prazo com
`int`, data e hora com `datetime`. O resumo conta eventos e encomendas distintas.
Para cada código, vale o último frete informado em ordem cronológica; o mesmo
frete em duas atualizações não é cobrado duas vezes. Em empate de data/hora,
a última declaração na ordem de entrada prevalece.

O mascaramento usa a categoria para esconder parte do e-mail e CPF nas abas
Colorido e Tokens. Os objetos `Token` não são alterados. É uma demonstração de
minimização de exibição, não anonimização de todo o documento: textos livres,
entrada editável e contexto de erro continuam visíveis.
