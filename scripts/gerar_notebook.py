import hashlib
import json
from pathlib import Path
import sys

import nbformat


RAIZ = Path(__file__).resolve().parents[1]


def gerar():
    celulas = []

    def markdown(texto):
        celulas.append(nbformat.v4.new_markdown_cell(texto))

    def codigo(texto):
        celulas.append(nbformat.v4.new_code_cell(texto))

    markdown('''# Augusto Preto

# Atividade Prática 1 - Compiladores
## Analisadores léxicos com Lark e desafio RastreioLang

Execute as células em ordem. Este notebook contém todas as implementações e
testes; não exige outros arquivos. As interfaces interativas funcionam no
Colab ou em um kernel Jupyter com ipywidgets.

**Organização:** preparação, código, respostas teóricas, experimentos,
interfaces A1/A2/B1/B2, desafio, testes e roteiro de apresentação.

''')
    codigo('''import importlib.metadata
import subprocess
import sys

necessarias = {"lark": "1.3.1", "ipywidgets": "8.1.8"}
instalar = []
for pacote, versao in necessarias.items():
    try:
        atual = importlib.metadata.version(pacote)
    except importlib.metadata.PackageNotFoundError:
        atual = None
    if atual != versao:
        instalar.append(f"{pacote}=={versao}")
if instalar:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", *instalar])

try:
    from google.colab import output
except ImportError:
    pass
else:
    output.enable_custom_widget_manager()

print("Ambiente pronto: Lark e ipywidgets.")
''')
    fonte = (RAIZ / 'p1.py').read_text(encoding='utf-8')
    partes = fonte.split('# %% ')
    for parte in partes[1:]:
        titulo, corpo = parte.split('\n', 1)
        if titulo == 'Execução no terminal':
            continue
        markdown('## ' + titulo)
        codigo(corpo.strip())

    markdown((RAIZ / 'docs/exercicios.md').read_text(encoding='utf-8'))
    markdown('## Conferência executável da tabela do exercício 1')
    codigo('''from IPython.display import display, HTML
entrada_teorica = '# almoço\\npedido 3X "Pastel de Queijo" R$ 8,50\\nPAGAMENTO Cartão'
display(HTML(CSS + tabela_tokens_html(analisar(entrada_teorica, GRAMATICA_A2_BASE))))
''')
    markdown('## Experimento A1: preço com e sem prioridade')
    codigo('''for nome, gramatica in [
    ("Sem prioridade", GRAMATICA_A1_BASE.replace("PRECO.2:", "PRECO:")),
    ("Prioridade corrigida", GRAMATICA_A1_BASE),
]:
    try:
        ts = analisar("R$ 25,90", gramatica)
        print(nome, [(t.type, str(t)) for t in ts])
    except UnexpectedCharacters as e:
        print(f"{nome}: erro na linha {e.line}, coluna {e.column}, caractere {e.char!r}")
''')
    for nome, dominio in [('A1 - Comanda com OBS', 'a1'), ('A2 - VR, DESC20 e preço sem R$', 'a2'),
                          ('B1 - CNPJ e laboratório de prioridade', 'b1'), ('B2 - Saque, telefone local e alertas', 'b2')]:
        markdown('## Interface ' + nome + '\n\nEscolha um exemplo, edite o texto e clique em **Analisar**.')
        codigo(f'ui_{dominio} = interface_lexer({nome!r}, tokenizar_{dominio}, CASOS_{dominio.upper()}, {dominio!r}, laboratorio={dominio == "b1"})')

    markdown((RAIZ / 'docs/linguagem.md').read_text(encoding='utf-8'))
    markdown('## Desafio: casos de teste e resultados legíveis sem widgets')
    codigo('''for nome, texto in CASOS_RASTREIO.items():
    print("\\n" + nome + "\\n" + texto)
    try:
        ts = tokenizar_rastreio(texto)
        print(f"Resultado: {len(ts)} tokens; {resumo_rastreio(ts)['encomendas']} encomenda(s).")
    except UnexpectedCharacters as e:
        print(f"Erro L{e.line} C{e.column}: {e.char!r}. Dica: {e.dica}")

texto = CASOS_RASTREIO["Válido 2: completo e minúsculas"]
ts = tokenizar_rastreio(texto)
display(HTML(CSS + texto_colorido_html(texto, ts, True)))
display(HTML(tabela_tokens_html(ts, True)))
display(HTML(resumo_html(ts, "rastreio", True)))
''')
    markdown('## Interface RastreioLang')
    codigo('ui_rastreio = interface_lexer("RastreioLang - Meu Analisador Léxico de Mercado", tokenizar_rastreio, CASOS_RASTREIO, "rastreio")')
    markdown('## Testes automáticos\n\nAs verificações abaixo incluem os exercícios teóricos, extensões práticas, desafio e callbacks da interface.')
    testes = (RAIZ / 'tests/test_p1.py').read_text(encoding='utf-8').split("if __name__ == '__main__':")[0]
    testes = testes.replace('import p1\n', 'from types import SimpleNamespace\np1 = SimpleNamespace(**globals())\n')
    codigo(testes + '''
suite = unittest.TestSuite()
for classe in (ExerciciosTeoricos, ExerciciosPraticos, DesafioRastreio, Apresentacao):
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(classe))
resultado = unittest.TextTestRunner(verbosity=2).run(suite)
assert resultado.wasSuccessful(), "Há falhas a corrigir antes da entrega."
''')
    markdown((RAIZ / 'docs/guia_apresentacao.md').read_text(encoding='utf-8'))
    markdown('''## Referências e entrega

- Material da disciplina: *Aula CP 05 (Prática 1) - Construindo um Analisador Léxico com Lark*, Prof. Hercules Ramos, FMU, 2026. As gramáticas A e B foram adaptadas desse roteiro.
- [Documentação do Lark](https://lark-parser.readthedocs.io/en/stable/grammar.html).
- [Documentação do ipywidgets](https://ipywidgets.readthedocs.io/en/stable/).

Publique o projeto com README em um repositório público no GitHub e envie o
link na atividade até **25/09/2026 às 23h59**. Confira os nomes e a composição
do grupo. A publicação não efetua o envio no ambiente da faculdade.
''')
    for i, celula in enumerate(celulas):
        celula.id = hashlib.sha256(f'{i}:{celula.source}'.encode()).hexdigest()[:12]
    nb = nbformat.v4.new_notebook(cells=celulas)
    nb.metadata = dict(kernelspec=dict(display_name='Python 3', language='python', name='python3'),
                       language_info=dict(name='python', version='3.12'),
                       colab=dict(provenance=[]))
    nbformat.validate(nb)
    return nb


if __name__ == '__main__':
    destino = RAIZ / 'Atividade_Pratica_1.ipynb'
    novo = gerar()
    if '--check' in sys.argv:
        atual = nbformat.read(destino, as_version=4)
        nbformat.validate(atual)
        esperado = [(c.cell_type, c.source) for c in novo.cells]
        encontrado = [(c.cell_type, c.source) for c in atual.cells]
        if esperado != encontrado:
            raise SystemExit('Notebook desatualizado. Execute python scripts/gerar_notebook.py.')
        print(f'Notebook consistente: {len(atual.cells)} células.')
    else:
        nbformat.write(novo, destino)
        print(f'Gerado: {destino.name} ({len(novo.cells)} células).')
