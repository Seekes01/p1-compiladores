# Guia de apresentação e estudo

## Demonstração sugerida (5 a 7 minutos)

1. **Objetivo (30 s).** “O projeto transforma o texto de pedidos, transações e
   rastreios em tokens. Cada token tem categoria, lexema, linha e coluna.”
2. **RastreioLang (1 min).** Abra o primeiro caso válido. Mostre `RASTREIO`,
   `COD_RASTREIO`, `TEXTO`, `CEP_VALOR`, `DATA` e `HORA` nas duas primeiras abas.
3. **Prioridade (1 min).** No B1, escolha o caso `pix@`, reduza a prioridade
   para 2 e mostre o erro no `@`. Volte para 4. Explique a relação com `EM`
   e `EMAIL` do desafio.
4. **Erros (1 min).** No desafio, selecione aspas abertas e CEP com ponto.
   Mostre linha, coluna, seta e dica específica.
5. **Extensões (1 min).** Mostre VR/DESC20, saque e alerta para chave aleatória.
6. **Bônus (1 min).** Abra o caso com três eventos, confira dois códigos e
   R$ 35,90 de frete. Ligue/desligue a máscara no caso completo.
7. **Testes (30 s).** Execute a célula de testes e explique um caso de fronteira:
   R$ 500,00 não dispara o alerta; R$ 500,01 dispara.

## Perguntas que você precisa saber responder

**Por que `start: _token*`?**  
Para aceitar qualquer quantidade de tokens enquanto estudamos só o lexer.
Essa regra não exige a estrutura de um comando completo.

**Qual é a diferença entre token e lexema?**  
`CEP_VALOR` é o tipo; `01310-100` é o texto concreto reconhecido.

**O que significa `/i`?**  
Aceitar letras maiúsculas e minúsculas no padrão.

**Por que usar `\b`?**  
Para não reconhecer uma palavra reservada apenas como começo de uma palavra
maior. `EM` é reservada; `EMPRESA` não é.

**Por que `\b` não basta para um e-mail?**  
Porque `@` não é caractere de palavra. Existe uma fronteira após `em` em
`em@exemplo.com`, então precisamos dar prioridade maior ao e-mail completo.

**O que `.5` significa?**  
Prioridade léxica 5. Um padrão que casa nessa prioridade é testado antes de
outro com prioridade 4. Não indica quantidade de caracteres ou repetições.

**Como você mostra linha e coluna?**  
Os tokens do Lark já trazem esses atributos. A exceção `UnexpectedCharacters`
também os fornece quando a leitura falha.

**Como o texto é colorido sem perder espaços?**  
`start_pos` e `end_pos` delimitam cada lexema no texto original. A interface
preserva os intervalos entre tokens e colore somente o trecho reconhecido.

**O que os widgets fazem?**  
`Textarea` recebe a entrada; `Button.on_click` chama a análise;
`Dropdown.observe` reage à escolha de exemplo. As abas usam widgets `HTML`
atualizados pelo callback. `Output`, apresentado no roteiro, é outra forma de
exibir saídas de `display`, mas não é necessário para estas abas de HTML.

**Uma data reconhecida necessariamente existe?**  
Não. A regex verifica o formato. A conversão com `datetime` rejeita valores
como 31 de fevereiro na etapa posterior.

**Como distinguir telefone local e CPF sem pontuação?**  
Somente 11 dígitos não bastam. Nossa convenção exige pontuação no CPF e trata
11 dígitos puros como telefone. Um campo explícito de tipo resolveria a intenção.

**Por que não usar `float` para dinheiro?**  
`Decimal` permite representar os valores decimais dos exemplos sem resíduos
binários. A regra de arredondamento do desconto é definida explicitamente.

## Autoavaliação individual

Marque depois de executar e explicar cada item com suas palavras:

- [ ] Diferencio token, lexema e padrão.
- [ ] Escrevo um token com literal e outro com regex.
- [ ] Explico `%ignore` e a preservação de linha e coluna.
- [ ] Demonstro e resolvo um conflito de prioridade.
- [ ] Explico `/i` e `\b`, inclusive a limitação com `@`.
- [ ] Identifico e trato `UnexpectedCharacters`.
- [ ] Explico `line`, `column`, `start_pos` e `end_pos`.
- [ ] Explico os componentes da interface e seus callbacks.
- [ ] Distingo erro léxico, erro de estrutura e regra de negócio.
- [ ] Consigo ler cada regex da tabela do desafio em voz alta.
- [ ] Executei o notebook do início ao fim no meu ambiente.

