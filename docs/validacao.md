# Registro de validação

Validação local realizada em **15/09/2026**, com Python 3.12, Lark 1.3.1 e
ipywidgets 8.1.8.

## Execução

| Verificação | Resultado |
|---|---|
| `python -m unittest discover -s tests -v` | 30 testes aprovados |
| Notebook executado em kernel Python novo | 14 células de código executadas; zero erros |
| Testes dentro do notebook autossuficiente | 30 testes aprovados |
| Estrutura do arquivo ipynb | Validada com nbformat |
| Prévia HTML das saídas | Aberta em navegador; cabeçalho e realce de tokens conferidos visualmente |
| Demonstração no terminal | Casos válidos/ inválidos, comanda R$ 90,00 e saldo R$ 3.762,70 |

O notebook foi executado a partir de uma pasta sem `p1.py` para conferir que
suas células contêm o código necessário. A geração instala Lark e ipywidgets
quando ausentes; a instalação automática não precisou rodar no kernel de
validação porque as versões já estavam disponíveis.

## Cobertura dos testes

- Tabela de tokens com os lexemas e posições do exercício 1.
- Categorias e erros dos exercícios 2 e 3.
- Exemplos positivos e negativos para as regex do exercício 4.
- Diferença entre cupom léxico válido e desconto recusado.
- OBS, VR, DESC20, CNPJ e SAQUE.
- Preço com e sem símbolo e sua disputa com número e quantidade.
- Versão original versus telefone local do B2 estendido.
- Alertas nos limites de valor, direção e horário.
- Contas de comanda, frete e extrato.
- Requisitos de quantidade de tokens e reservadas do desafio.
- Casos válidos, inválidos e posições das mensagens do desafio.
- Conflitos de e-mail/reservada e rastreio/identificador.
- Comentários, fronteiras de palavra e offsets originais.
- Datas inexistentes rejeitadas no pós-processamento.
- Campos fora de ordem ou repetidos rejeitados no resumo.
- Escape de HTML e máscaras sem alterar os tokens originais.
- Seleção de exemplos, clique do botão, slider e máscara dos widgets.
- Limpeza das saídas antigas quando a entrada passa a ser inválida.

## Limites da validação

A execução foi feita em kernel Jupyter local, não dentro de uma conta Google
Colab. O notebook inclui a configuração do gerenciador de widgets do Colab;
a abertura interativa nesse serviço deve ser conferida pelo estudante.

O workflow do GitHub está incluído no projeto, mas sua execução remota depende
de publicar o repositório. Os testes locais e o notebook não substituem a
conferência dos nomes, da composição do grupo e do envio do link na faculdade.
