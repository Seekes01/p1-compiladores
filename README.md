# Integrante

**Augusto Preto**

# Atividade Prática 1 - Compiladores

## Meu Analisador Léxico de Mercado: RastreioLang

O projeto recebe registros em texto e separa cada entrada em tokens usando Python
e Lark. Os cenários são pedidos de delivery, transações PIX e rastreio de encomendas.

A organização segue um fluxo simples: entrada, reconhecimento dos tokens,
tratamento de erros e resumo dos dados. As regras de cálculo ficam separadas
do lexer. Os exemplos e a interface estão no notebook.

**Disciplina:** Compiladores - Ciência da Computação, 8º semestre, FMU.  
**Prazo:** 25/09/2026, às 23h59.  
**Entrega:** link de um repositório público no GitHub; um membro faz o envio.  

## Comece pelo notebook

1. Baixe `Atividade_Pratica_1.ipynb` deste repositório.
2. Abra [Google Colab](https://colab.research.google.com/).
3. Use **Arquivo > Fazer upload de notebook** e selecione o arquivo.
4. Execute todas as células em ordem. A primeira instala as dependências necessárias.
5. Nas interfaces, selecione um caso ou edite a entrada e clique em **Analisar**.

O notebook é **autossuficiente**: contém o código e os testes, sem depender de
clonar o repositório, montar o Drive ou informar um endereço de GitHub.
O visualizador de notebooks do GitHub permite ler o material, mas os controles
interativos precisam de um kernel Python, como o do Colab ou VS Code.

## Conteúdo e organização

```text
Atividade_Pratica_1.ipynb     Notebook com explicações, código, testes e interfaces
p1.py                       Analisadores e execução no terminal
tests/test_p1.py             Testes automáticos de comportamento
docs/exercicios.md           Respostas, alterações e resultados dos experimentos
docs/linguagem.md            Tabela de tokens, sintaxe de uso e ambiguidades
docs/guia_apresentacao.md    Roteiro de estudo e autoavaliação
docs/entrega.md              Publicação e envio no ambiente da faculdade
docs/validacao.md            Registro dos testes executados
docs/previa.html             Exemplo estático das saídas, para abrir no navegador
scripts/gerar_notebook.py    Gera o notebook a partir do código e documentação
requirements.txt            Dependências para executar
requirements-dev.txt        Dependências para gerar e validar o notebook
.github/workflows/testes.yml Verificação automática após publicar no GitHub
```

### O que foi implementado

| Parte do material | Resultado | Onde conferir |
|---|---|---|
| Recapitulação e discussão sobre tokenizadores | Respostas conceituais | `docs/exercicios.md` |
| Exercícios de caderno 1 a 5 | Tabela, classificações, localização do erro, regex e reflexão | `docs/exercicios.md` e notebook |
| Guiado A1 | `OBS` e teste com pizza | `tokenizar_a1` |
| Guiado A2 | Pagamento `vr` e cupom `DESC20` com cálculo de desconto | `tokenizar_a2`, `comanda` |
| Guiado B1 | Chave CNPJ | `tokenizar_b1` |
| Guiado B2 | `SAQUE` como saída | `tokenizar_b2`, `conciliar` |
| Desafio A2 | Preços com e sem `R$` | `GRAMATICA_A2` |
| Desafio B2: telefone | Telefone com `+55` ou 11 dígitos locais; ambiguidade explicada | `GRAMATICA_B2` e documentação |
| Desafio B2: alerta | PIX de saída para chave aleatória acima de R$ 500,00 | `alertas` |
| Desafio para entrega | RastreioLang, com 22 tipos de token | `tokenizar_rastreio` |
| Bônus | Resumo, conversões de valores e máscara de chaves | Abas da interface |
| Autoavaliação | Perguntas e roteiro de demonstração | `docs/guia_apresentacao.md` |

## Desafio: exemplo de entrada

```text
# Evento de entrega
RASTREIO BR123456789BR STATUS "saiu para entrega" CEP 01310-100 EM 10/09/2026 08:15 FRETE R$ 25,90 CONTATO em@exemplo.com
```

A análise identifica categorias como `RASTREIO`, `COD_RASTREIO`, `STATUS`, `TEXTO`,
`CEP_VALOR`, `DATA`, `HORA`, `VALOR` e `EMAIL`. Cada token preserva o lexema,
a linha, a coluna e as posições inicial/final no texto original.

A interface oferece quatro abas:

- **Colorido:** realce dos lexemas no texto original.
- **Tokens:** categoria, lexema, linha e coluna.
- **Resumo:** pós-processamento adequado ao cenário.
- **Estatística:** contagem de cada categoria.

O B1 inclui um controle de prioridade do e-mail para reproduzir o conflito entre
`PIX` e `pix@loja.com.br`. No desafio, o caso completo usa `em@exemplo.com` para
demonstrar o mesmo tipo de conflito com `EM`.

## Requisitos do desafio

| Requisito | Implementação |
|---|---|
| Tabela com descrição, regex, exemplo e prioridade | `docs/linguagem.md` |
| Pelo menos 12 tipos de token | 22, sem contar comentários e espaços ignorados |
| Pelo menos 4 reservadas com `/i` e `\b` | 11 reservadas, prioridade 4 |
| Pelo menos 3 literais por regex | Código, CEP, data, hora, peso, valor, CPF, texto e outros |
| Conflito resolvido e comentado | `EMAIL.5` versus `EM.4`; `COD_RASTREIO.3` versus identificador |
| Comentários e espaços ignorados | `%ignore COMENTARIO` e `%ignore /[ \t\r\n]+/` |
| Erro com linha, coluna e dicas | Tratamento de `UnexpectedCharacters` |
| Entrada, botão, texto colorido e tabela | `interface_lexer` com ipywidgets |
| 3 casos válidos e 2 inválidos | 3 válidos e 3 inválidos em `CASOS_RASTREIO` |
| Diário de ambiguidade | `docs/linguagem.md` |
| Bônus: resumo | Eventos, encomendas distintas e total de frete |
| Bônus: conversões | `Decimal`, `int` e `datetime` |
| Bônus: mascaramento | E-mail e CPF na saída do desafio; outras chaves no B2 |

## Execução local

Ambiente de referência: **Python 3.12**. No terminal, dentro da pasta do projeto:

```bash
python -m venv .venv
```

Ative o ambiente:

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

```bash
# Linux/macOS
source .venv/bin/activate
```

Instale e execute:

```bash
python -m pip install -r requirements.txt
python p1.py
python -m unittest discover -s tests -v
```

No VS Code, instale as extensões Python e Jupyter, abra o notebook e escolha o
interpretador da `.venv` como kernel. A execução de `p1.py` no terminal demonstra
os resultados; a interface interativa está no notebook.

Para atualizar o notebook depois de editar o código ou a documentação:

```bash
python -m pip install -r requirements-dev.txt
python scripts/gerar_notebook.py
python scripts/gerar_notebook.py --check
```

## Resultados de referência

| Caso | Resultado esperado |
|---|---|
| Pedido de R$ 100,00, DESC20 e taxa de R$ 10,00 | Total R$ 90,00 |
| Pedido completo do roteiro | Total R$ 87,46 |
| Extrato completo | Entradas R$ 3.250,00; saídas R$ 1.987,30; saldo R$ 3.762,70 |
| Saldo R$ 300,00 e saque R$ 200,00 | Saldo R$ 100,00 |
| PIX de saída para chave aleatória de R$ 500,00 | Sem o novo alerta |
| Mesmo caso com R$ 500,01 | Novo alerta exibido |
| Rastreio com três eventos e dois códigos | Duas encomendas; frete R$ 35,90 |

O registro de validação está em `docs/validacao.md`. Os testes verificam posições,
conflitos, limites dos alertas, cálculos, máscaras e eventos dos widgets.

## Decisões e limites

- Usamos `lexer="basic"` e `.lex()`. A regra inicial aceita qualquer sequência de
  categorias; reconhecer tokens não garante uma instrução bem formada.
- Os resumos validam a ordem dos campos e convertem valores em uma camada
  separada. Uma data como `31/02/2026` tem formato léxico válido, mas a conversão
  de calendário a rejeita.
- As gramáticas `*_BASE` preservam as versões necessárias aos exercícios
  originais. As funções públicas utilizam as extensões solicitadas.
- No B2 estendido, 11 dígitos sem pontuação significam telefone. Não tentamos
  descobrir se o autor pretendia informar CPF; veja a discussão de ambiguidade.
- Os dados são exemplos didáticos. O programa não consulta Correios, bancos,
  cadastros de CPF/CNPJ nem serviços de verificação de e-mail.
- Os alertas são regras didáticas do exercício, não diagnóstico de fraude.
- A máscara altera somente a apresentação de chaves reconhecidas. A entrada,
  mensagens de erro e campos de texto livre não são anonimizados automaticamente.
- O total de frete do rastreio considera a última declaração cronológica por
  código, evitando contar novamente o frete a cada atualização de status.

## Referências

- Material da disciplina: *Aula CP 05 (Prática 1) - Construindo um Analisador
  Léxico com Lark*, fornecido como `p1.pdf`, Prof. Hercules Ramos, FMU, 2026.
  As gramáticas dos cenários A e B foram adaptadas desse roteiro. O PDF original
  não faz parte dos arquivos publicados.
- [Documentação do Lark: gramática, prioridades e `%ignore`](https://lark-parser.readthedocs.io/en/stable/grammar.html).
- [Documentação do ipywidgets](https://ipywidgets.readthedocs.io/en/stable/).

## Entrega

Consulte `docs/entrega.md` para publicar os arquivos em um repositório **público**
e enviar o endereço na atividade. A criação dos arquivos locais não equivale à
publicação no GitHub nem ao envio no ambiente da faculdade.
