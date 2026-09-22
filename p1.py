# %% Núcleo e gramáticas dos exercícios
from collections import Counter, defaultdict
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from functools import lru_cache
import html
import re

from lark import Lark
from lark.exceptions import UnexpectedCharacters


def compilar(definicoes, comentarios=True):
    nomes = [linha.split(':', 1)[0].split('.')[0] for linha in definicoes.splitlines()
             if linha.strip() and not linha.lstrip().startswith('//')]
    ruido = '\n%ignore /[ \\t\\r\\n]+/\n'
    if comentarios:
        ruido += 'COMENTARIO: /#[^\\n]*/\n%ignore COMENTARIO\n'
    return 'start: _token*\n_token: ' + ' | '.join(nomes) + '\n' + definicoes + ruido


@lru_cache(maxsize=16)
def criar_lexer(gramatica):
    return Lark(gramatica, parser='lalr', lexer='basic', propagate_positions=True)


def analisar(texto, gramatica, dominio='geral'):
    try:
        return list(criar_lexer(gramatica).lex(texto))
    except UnexpectedCharacters as erro:
        resto = texto[erro.pos_in_stream:].split('\n', 1)[0]
        if erro.char == '"':
            dica = 'Feche as aspas do nome, status ou descrição antes de mudar de linha.'
        elif dominio == 'rastreio':
            if re.match(r'\d', resto):
                dica = ('CEP: 01310-100; data: 10/09/2026; hora: 08:15; '
                        'peso: 1,250kg. Confira os separadores e o tamanho do campo.')
            elif '@' in resto.split(' ', 1)[0] or erro.char == '@':
                dica = 'Contato de entrega deve ser um e-mail como em@exemplo.com.'
            else:
                dica = ('Código de rastreio: duas letras, nove dígitos e duas letras '
                        '(BR123456789BR). Status e endereços precisam de aspas.')
        elif dominio == 'banco':
            dica = ('Confira a chave: nome@dominio.com, CPF 123.456.789-09, '
                    'CNPJ 12.345.678/0001-90 ou telefone no formato desta versão. '
                    'Valores: R$ 10,50; datas: 01/09/2026.')
        else:
            dica = ('Preço usa vírgula e dois centavos (R$ 25,90); quantidade usa x '
                    '(2x). A1 exige maiúsculas nos comandos e R$ no preço.')
        erro.dica = dica
        raise


DEFS_A1 = r'''
PEDIDO: "PEDIDO"
ENTREGA: "ENTREGA"
CUPOM: "CUPOM"
QTD.2: /\d+x/
ITEM: /"[^"\n]*"/
PRECO.2: /R\$ ?\d+,\d{2}/
CODIGO: /[A-Z][A-Z0-9]*/
'''
GRAMATICA_A1_BASE = compilar(DEFS_A1, comentarios=False)
GRAMATICA_A1 = compilar(DEFS_A1 + '\nOBS: "OBS"\n', comentarios=False)

DEFS_A2 = r'''
PEDIDO.3: /pedido\b/i
ENTREGA.3: /entrega\b/i
CUPOM.3: /cupom\b/i
OBS.3: /obs\b/i
TAXA.3: /taxa\b/i
PAGAMENTO.3: /pagamento\b/i
FORMA_PGTO.3: /(pix|cart[aã]o|dinheiro|vale_refeicao)\b/i
QTD.2: /\d+x\b/i
PRECO.2: /R\$ ?\d{1,3}(\.\d{3})*,\d{2}/
TEXTO: /"[^"\n]*"/
NUMERO: /\d+/
CODIGO: /[A-Za-z_][A-Za-z0-9_]*/
'''
GRAMATICA_A2_BASE = compilar(DEFS_A2)
# PRECO.2 vence NUMERO.0 no prefixo 25 de 25,90.
# QTD.2 e PRECO.2 não casam a mesma entrada completa: x versus vírgula.
DEFS_A2_FINAL = DEFS_A2.replace('vale_refeicao)', 'vale_refeicao|vr)').replace(
    r'/R\$ ?\d{1,3}(\.\d{3})*,\d{2}/',
    r'/(R\$ ?)?\d{1,3}(\.\d{3})*,\d{2}(?![\w,.])/')
GRAMATICA_A2 = compilar(DEFS_A2_FINAL)
CUPONS = {'DESC10': Decimal('0.10'), 'DESC15': Decimal('0.15'),
          'DESC20': Decimal('0.20'), 'PRIMEIRACOMPRA': Decimal('0.20')}
CUPONS_FRETE = {'FRETEGRATIS', 'FRETE10'}

DEFS_B1 = r'''
PIX.3: /pix\b/i
DIRECAO.3: /(enviado|recebido)\b/i
PARA.3: /para\b/i
DE.3: /de\b/i
EM.3: /em\b/i
VALOR.2: /R\$ ?\d{1,3}(\.\d{3})*,\d{2}/
DATA.2: /\d{2}\/\d{2}\/\d{4}/
HORA.2: /\d{2}:\d{2}/
CHAVE_EMAIL.4: /[a-z0-9._+-]+@[a-z0-9-]+(\.[a-z0-9-]+)+/i
CHAVE_CPF.2: /\d{3}\.\d{3}\.\d{3}-\d{2}/
CHAVE_TELEFONE.2: /\+55\d{10,11}/
CHAVE_ALEATORIA.2: /[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/i
'''
DEFINICAO_CNPJ = r'CHAVE_CNPJ.2: /\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}/'
GRAMATICA_B1_BASE = compilar(DEFS_B1, comentarios=False)
GRAMATICA_B1 = compilar(DEFS_B1 + '\n' + DEFINICAO_CNPJ, comentarios=False)
DEFS_B2 = DEFS_B1.replace('(enviado|recebido)', '(enviado|recebido|pago)') + '\n' + DEFINICAO_CNPJ + r'''
SALDO_INICIAL.3: /saldo\s+inicial\b/i
TED.3: /ted\b/i
BOLETO.3: /boleto\b/i
TARIFA.3: /tarifa\b/i
DESCRICAO: /"[^"\n]*"/
'''
GRAMATICA_B2_BASE = compilar(DEFS_B2)
# 11 dígitos locais são telefone por convenção DESTA linguagem.
# Não existe CPF sem pontuação nesta versão: a prioridade não descobriria a intenção.
GRAMATICA_B2 = compilar(DEFS_B2.replace(
    r'/\+55\d{10,11}/', r'/(\+55\d{10,11}|\d{11})(?![\w+])/')
    + r'\nSAQUE.3: /saque\b/i'.replace(r'\n', '\n'))


def tokenizar_a1(texto):
    return analisar(texto, GRAMATICA_A1, 'pedido')


def tokenizar_a2(texto):
    return analisar(texto, GRAMATICA_A2, 'pedido')


def tokenizar_b1(texto, prioridade_email=4):
    gramatica = GRAMATICA_B1.replace('CHAVE_EMAIL.4', f'CHAVE_EMAIL.{prioridade_email}')
    return analisar(texto, gramatica, 'banco')


def tokenizar_b2(texto):
    return analisar(texto, GRAMATICA_B2, 'banco')


def valor_em_reais(lexema):
    return Decimal(str(lexema).replace('R$', '').strip().replace('.', '').replace(',', '.'))


def brl(valor):
    numero = f'{abs(valor):,.2f}'.replace(',', '_').replace('.', ',').replace('_', '.')
    return ('- ' if valor < 0 else '') + 'R$ ' + numero


def linhas_de_tokens(tokens):
    linhas = defaultdict(list)
    for token in tokens:
        linhas[token.line].append(token)
    return linhas


def comanda(tokens):
    itens, observacoes, avisos = [], [], []
    taxa, cupom, pagamento, endereco = Decimal(0), None, 'não informado', 'retirada'
    for linha, ts in linhas_de_tokens(tokens).items():
        tipos = [t.type for t in ts]
        if tipos[:4] == ['PEDIDO', 'QTD', 'TEXTO', 'PRECO']:
            if tipos[4:] not in ([], ['OBS', 'TEXTO']):
                raise ValueError(f'Linha {linha}: após o item, use OBS "texto" ou termine a linha.')
            itens.append((int(ts[1][:-1]), str(ts[2])[1:-1], valor_em_reais(ts[3])))
            if len(ts) > 4:
                observacoes.append(str(ts[5])[1:-1])
        elif tipos == ['TAXA', 'PRECO']:
            taxa = valor_em_reais(ts[1])
        elif tipos == ['CUPOM', 'CODIGO']:
            cupom = str(ts[1]).upper()
        elif tipos == ['PAGAMENTO', 'FORMA_PGTO']:
            pagamento = str(ts[1]).upper()
        elif tipos == ['ENTREGA', 'TEXTO']:
            endereco = str(ts[1])[1:-1]
        elif tipos == ['OBS', 'TEXTO']:
            observacoes.append(str(ts[1])[1:-1])
        else:
            raise ValueError(f'Linha {linha}: sequência não reconhecida pela comanda.')
    subtotal = sum((q*p for q, _, p in itens), Decimal(0))
    desconto = (subtotal * CUPONS.get(cupom, Decimal(0))).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
    if cupom in CUPONS_FRETE:
        taxa = Decimal(0)
    if cupom and cupom not in CUPONS and cupom not in CUPONS_FRETE:
        avisos.append(f'Cupom {cupom} inexistente: desconto recusado pela regra de negócio.')
    return dict(itens=itens, subtotal=subtotal, desconto=desconto, taxa=taxa,
                total=subtotal-desconto+taxa, pagamento=pagamento, endereco=endereco,
                observacoes=observacoes, avisos=avisos)


def conciliar(tokens):
    saldo_inicial, transacoes = Decimal(0), []
    viu_saldo = False
    for linha, ts in linhas_de_tokens(tokens).items():
        tipos = [t.type for t in ts]
        if tipos == ['SALDO_INICIAL', 'VALOR']:
            if viu_saldo or transacoes:
                raise ValueError('SALDO INICIAL deve aparecer uma única vez, antes das transações.')
            saldo_inicial, viu_saldo = valor_em_reais(ts[1]), True
            continue
        op = tipos[0]
        chave = None
        if op in ('PIX', 'TED'):
            if len(ts) < 8 or tipos[:3] != [op, 'DIRECAO', 'VALOR'] or not tipos[4].startswith('CHAVE_'):
                raise ValueError(f'Linha {linha}: use {op} ENVIADO/RECEBIDO valor PARA/DE chave EM data hora.')
            direcao = str(ts[1]).upper()
            if direcao not in ('ENVIADO', 'RECEBIDO') or tipos[3] != ('DE' if direcao == 'RECEBIDO' else 'PARA'):
                raise ValueError(f'Linha {linha}: direção incompatível com PARA/DE.')
            valor, chave, resto = valor_em_reais(ts[2]), ts[4], ts[5:]
            sinal = 1 if direcao == 'RECEBIDO' else -1
        elif op == 'BOLETO' and tipos[:3] == ['BOLETO', 'DIRECAO', 'VALOR'] and str(ts[1]).upper() == 'PAGO':
            valor, resto, sinal, direcao = valor_em_reais(ts[2]), ts[3:], -1, 'PAGO'
        elif op in ('SAQUE', 'TARIFA') and tipos[:2] == [op, 'VALOR']:
            valor, resto, sinal, direcao = valor_em_reais(ts[1]), ts[2:], -1, 'DÉBITO'
        else:
            raise ValueError(f'Linha {linha}: operação ou sequência de campos inválida.')
        if [t.type for t in resto] not in (['EM', 'DATA', 'HORA'], ['EM', 'DATA', 'HORA', 'DESCRICAO']):
            raise ValueError(f'Linha {linha}: termine com EM data hora e descrição opcional entre aspas.')
        instante = datetime.strptime(f'{resto[1]} {resto[2]}', '%d/%m/%Y %H:%M')
        transacoes.append(dict(linha=linha, tipo=op, direcao=direcao, valor=valor*sinal,
                               chave=chave, data=str(resto[1]), hora=str(resto[2]), instante=instante,
                               descricao=str(resto[3])[1:-1] if len(resto) == 4 else ''))
    return saldo_inicial, transacoes


def alertas(transacoes):
    avisos = []
    for tr in transacoes:
        if tr['tipo'] != 'PIX' or tr['valor'] >= 0:
            continue
        hora = tr['instante'].hour
        if (hora >= 20 or hora < 6) and abs(tr['valor']) > 1000:
            avisos.append(f"Linha {tr['linha']}: PIX noturno acima do limiar didático de R$ 1.000,00.")
        if tr['chave'].type == 'CHAVE_ALEATORIA' and abs(tr['valor']) > 500:
            avisos.append(f"Linha {tr['linha']}: PIX para chave aleatória acima de R$ 500,00.")
    return avisos


# %% Desafio para entrega: RastreioLang
# Prioridades: EMAIL.5 > reservadas.4 > código.3 > literais.2 > identificador.0.
# EMAIL precisa vencer EM em em@exemplo.com: @ cria uma fronteira \b.
# COD_RASTREIO precisa vencer IDENTIFICADOR, que também aceita BR123456789BR.
DEFS_RASTREIO = r'''
RASTREIO.4: /rastreio\b/i
STATUS.4: /status\b/i
CEP.4: /cep\b/i
EM.4: /em\b/i
ORIGEM.4: /origem\b/i
DESTINO.4: /destino\b/i
PESO.4: /peso\b/i
FRETE.4: /frete\b/i
CONTATO.4: /contato\b/i
PRAZO.4: /prazo\b/i
DESTINATARIO.4: /destinatario\b/i
EMAIL.5: /[a-z0-9._+-]+@[a-z0-9-]+(\.[a-z0-9-]+)+(?=$|[\s#])/i
COD_RASTREIO.3: /[A-Z]{2}\d{9}[A-Z]{2}(?=$|[\s#])/i
CEP_VALOR.2: /\d{5}-\d{3}(?=$|[\s#])/
DATA.2: /\d{2}\/\d{2}\/\d{4}(?=$|[\s#])/
HORA.2: /\d{2}:\d{2}(?=$|[\s#])/
PESO_VALOR.2: /\d+(,\d{1,3})?kg(?=$|[\s#])/i
VALOR.2: /R\$ ?\d{1,3}(\.\d{3})*,\d{2}(?=$|[\s#])/
CPF_VALOR.2: /\d{3}\.\d{3}\.\d{3}-\d{2}(?=$|[\s#])/
TEXTO: /"[^"\n]*"/
NUMERO: /\d+(?=$|[\s#])/
IDENTIFICADOR: /[A-Za-z_][A-Za-z0-9_]*(?=$|[\s#])/
'''
GRAMATICA_RASTREIO = compilar(DEFS_RASTREIO)


def tokenizar_rastreio(texto):
    return analisar(texto, GRAMATICA_RASTREIO, 'rastreio')


def resumo_rastreio(tokens):
    eventos = []
    cabecalho = ['RASTREIO', 'COD_RASTREIO', 'STATUS', 'TEXTO', 'CEP', 'CEP_VALOR', 'EM', 'DATA', 'HORA']
    opcionais = dict(ORIGEM='TEXTO', DESTINO='TEXTO', PESO='PESO_VALOR', FRETE='VALOR',
                    CONTATO='EMAIL', PRAZO='NUMERO', DESTINATARIO='CPF_VALOR')
    for linha, ts in linhas_de_tokens(tokens).items():
        if [t.type for t in ts[:9]] != cabecalho:
            raise ValueError(f'Linha {linha}: use RASTREIO código STATUS "texto" CEP número EM data hora.')
        try:
            instante = datetime.strptime(f'{ts[7]} {ts[8]}', '%d/%m/%Y %H:%M')
        except ValueError as erro:
            raise ValueError(f'Linha {linha}: data ou hora inexistente no calendário.') from erro
        evento = dict(linha=linha, codigo=str(ts[1]).upper(), status=str(ts[3])[1:-1],
                      cep=str(ts[5]), instante=instante)
        resto = ts[9:]
        if len(resto) % 2:
            raise ValueError(f'Linha {linha}: campo opcional sem valor.')
        for campo, valor in zip(resto[::2], resto[1::2]):
            if opcionais.get(campo.type) != valor.type or campo.type.lower() in evento:
                raise ValueError(f'Linha {linha}: campo {campo} repetido ou com tipo incorreto.')
            convertido = str(valor)
            if campo.type == 'FRETE':
                convertido = valor_em_reais(valor)
            elif campo.type == 'PESO':
                convertido = Decimal(str(valor)[:-2].replace(',', '.'))
            elif campo.type == 'PRAZO':
                convertido = int(str(valor))
            elif valor.type == 'TEXTO':
                convertido = str(valor)[1:-1]
            evento[campo.type.lower()] = convertido
        eventos.append(evento)
    fretes = {}
    for evento in sorted(eventos, key=lambda e: e['instante']):
        if 'frete' in evento:
            fretes[evento['codigo']] = evento['frete']
    return dict(eventos=eventos, encomendas=len({e['codigo'] for e in eventos}),
                frete_total=sum(fretes.values(), Decimal(0)))


# %% Casos de uso (todos os dados são exemplos didáticos)
UUID_EXEMPLO = '7d9f3c2a-1b4e-4c8a-9f21-0a6b5e3d7c10'
EXTRATO_EXEMPLO = '''# Extrato de demonstração
SALDO INICIAL R$ 2.500,00
PIX RECEBIDO R$ 3.200,00 DE 12.345.678/0001-90 EM 05/09/2026 09:15 "Salário"
PIX ENVIADO R$ 1.200,00 PARA maria.souza@example.com EM 06/09/2026 10:02 "Aluguel"
PIX ENVIADO R$ 89,90 PARA +5511987654321 EM 07/09/2026 19:45 "Pizza"
BOLETO PAGO R$ 149,90 EM 08/09/2026 08:30 "Internet"
PIX RECEBIDO R$ 50,00 DE 123.456.789-09 EM 09/09/2026 12:10 "Almoço"
PIX ENVIADO R$ 35,00 PARA 7d9f3c2a-1b4e-4c8a-9f21-0a6b5e3d7c10 EM 10/09/2026 14:32 "Doação"
TED ENVIADO R$ 500,00 PARA 98.765.432/0001-10 EM 10/09/2026 16:00 "Curso"
TARIFA R$ 12,50 EM 10/09/2026 23:59 "Serviços"'''
CASOS_A1 = {
    'Guiado: OBS': 'PEDIDO 1x "Pizza" R$ 50,00 OBS "sem cebola"',
    'Pedido com entrega': 'PEDIDO 3x "Coxinha" R$ 7,50 ENTREGA "Rua A, 100"',
    'Palavra maior': 'PEDIDOS 2x',
    'Inválido: minúsculas': 'pedido 2x',
    'Inválido: símbolo': 'PEDIDO 2x "Açaí 500ml" R$ 19,90 @CUPOM',
}
CASOS_A2 = {
    'Guiado: VR e DESC20': 'PEDIDO 2x "Pizza" R$ 50,00\nTAXA R$ 10,00\nCUPOM DESC20\nPAGAMENTO vr',
    'Desafio: sem R$': 'pedido 3X "Pastel" 8,50\npagamento cartão',
    'Pedido completo': 'PEDIDO 2x "X-Burger" R$ 25,90\nPEDIDO 1x "Batata" R$ 18,50\nPEDIDO 3x "Refri" R$ 6,00\nTAXA R$ 7,99\nCUPOM DESC10\nPAGAMENTO pix',
    'Frete grátis': 'pedido 1x "Combo" R$ 1.150,00\ntaxa R$ 15,00\ncupom FRETEGRATIS',
    'Cupom inexistente (léxico válido)': 'PEDIDO 1x "Temaki" R$ 32,00\nCUPOM GANHEI100',
    'Inválido: centavos': 'PEDIDO 2x "Pastel" 8.50',
    'Inválido: aspas': 'PEDIDO 1x "Pizza',
}
CASOS_B1 = {
    'Guiado: CNPJ': 'PIX RECEBIDO R$ 100,00 DE 12.345.678/0001-90 EM 10/09/2026 08:15',
    'Conflito pix@': 'PIX ENVIADO R$ 10,00 PARA pix@loja.com.br EM 01/09/2026 08:00',
    'CPF': 'PIX RECEBIDO R$ 50,00 DE 123.456.789-09 EM 09/09/2026 12:10',
    'Telefone': 'PIX ENVIADO R$ 89,90 PARA +5511987654321 EM 07/09/2026 19:45',
    'Aleatória': f'PIX ENVIADO R$ 35,00 PARA {UUID_EXEMPLO} EM 10/09/2026 14:32',
    'Inválido: telefone local no B1': 'PIX ENVIADO R$ 20,00 PARA 11987654321 EM 02/09/2026 10:10',
}
CASOS_B2 = {
    'Extrato completo': EXTRATO_EXEMPLO,
    'Guiado: SAQUE': 'SALDO INICIAL R$ 300,00\nSAQUE R$ 200,00 EM 05/09/2026 18:00',
    'Desafio: telefone local': 'PIX ENVIADO R$ 20,00 PARA 11987654321 EM 02/09/2026 10:10',
    'Desafio: alerta de chave aleatória': f'PIX ENVIADO R$ 600,00 PARA {UUID_EXEMPLO} EM 10/09/2026 14:32',
    'Alerta noturno': 'PIX ENVIADO R$ 1.500,00 PARA a@example.com EM 11/09/2026 22:40',
    'Inválido: e-mail': 'SALDO INICIAL R$ 300,00\nPIX ENVIADO R$ 45,00 PARA joao@@mail.com EM 01/09/2026 10:00',
    'Inválido: aspas': 'PIX ENVIADO R$ 15,00 PARA a@b.com EM 01/09/2026 10:00 "Café',
}
CASOS_RASTREIO = {
    'Válido 1: entrega': 'RASTREIO BR123456789BR STATUS "saiu para entrega" CEP 01310-100 EM 10/09/2026 08:15',
    'Válido 2: completo e minúsculas': '# Encomenda de exemplo\nrastreio AB987654321BR status "em trânsito" cep 20040-020 em 11/09/2026 09:30 origem "São Paulo" destino "Rio de Janeiro" peso 1,250kg frete R$ 25,90 contato em@exemplo.com prazo 3 destinatario 123.456.789-09',
    'Válido 3: vários eventos': 'RASTREIO BR123456789BR STATUS "postado" CEP 01310-100 EM 10/09/2026 08:15 FRETE R$ 25,90\nRASTREIO BR123456789BR STATUS "entregue" CEP 01310-100 EM 12/09/2026 14:30 FRETE R$ 25,90\nRASTREIO CD111222333BR STATUS "postado" CEP 30130-010 EM 12/09/2026 15:00 FRETE R$ 10,00',
    'Inválido 1: aspas abertas': 'RASTREIO BR123456789BR STATUS "saiu para entrega',
    'Inválido 2: CEP com ponto': 'RASTREIO BR123456789BR STATUS "postado" CEP 01310.100 EM 10/09/2026 08:15',
    'Inválido 3: contato': 'RASTREIO BR123456789BR STATUS "postado" CEP 01310-100 EM 10/09/2026 08:15 CONTATO em@@exemplo.com',
}


# %% Interface compartilhada
def mascarar(token):
    valor = str(token)
    if token.type in ('CHAVE_EMAIL', 'EMAIL'):
        return valor[0] + '***@' + valor.split('@', 1)[1]
    if token.type in ('CHAVE_CPF', 'CPF_VALOR'):
        return '***.***.***-' + valor[-2:]
    if token.type == 'CHAVE_CNPJ':
        return '**.***.***/****-' + valor[-2:]
    if token.type == 'CHAVE_TELEFONE':
        return '*' * (len(valor)-4) + valor[-4:]
    if token.type == 'CHAVE_ALEATORIA':
        return valor[:8] + '-****'
    return valor


def cor_token(tipo):
    if tipo.startswith('CHAVE') or tipo in ('EMAIL', 'CPF_VALOR'):
        return '#9d174d'
    if tipo in ('PRECO', 'VALOR', 'PESO_VALOR'):
        return '#166534'
    if tipo in ('ITEM', 'TEXTO', 'DESCRICAO'):
        return '#9a3412'
    if tipo in ('NUMERO', 'QTD', 'DATA', 'HORA', 'CEP_VALOR', 'COD_RASTREIO'):
        return '#6b21a8'
    return '#1e40af'


def tabela_html(cabecalho, linhas):
    h = '<tr>' + ''.join(f'<th>{html.escape(str(c))}</th>' for c in cabecalho) + '</tr>'
    corpo = ''.join('<tr>' + ''.join(f'<td>{html.escape(str(v))}</td>' for v in linha) + '</tr>' for linha in linhas)
    return '<div style="overflow:auto"><table class="p1-table">' + h + corpo + '</table></div>'


def tabela_tokens_html(tokens, ocultar=False):
    return tabela_html(['#', 'TOKEN', 'LEXEMA', 'LINHA', 'COLUNA'],
                      [(i, t.type, mascarar(t) if ocultar else str(t), t.line, t.column)
                       for i, t in enumerate(tokens, 1)])


def texto_colorido_html(texto, tokens, ocultar=False):
    partes, cursor = [], 0
    for token in tokens:
        intervalo = texto[cursor:token.start_pos]
        if ocultar:
            intervalo = re.sub(r'#[^\n]*', '# comentário oculto', intervalo)
        partes.append(html.escape(intervalo))
        partes.append(f'<span title="{token.type}" style="color:{cor_token(token.type)};font-weight:700">'
                      + html.escape(mascarar(token) if ocultar else str(token)) + '</span>')
        cursor = token.end_pos
    final = texto[cursor:]
    if ocultar:
        final = re.sub(r'#[^\n]*', '# comentário oculto', final)
    partes.append(html.escape(final))
    return '<pre class="p1-code">' + ''.join(partes) + '</pre>'


def erro_lexico_html(texto, erro):
    linha = texto.splitlines()[erro.line-1] if texto.splitlines() else ''
    mensagem = f'Erro léxico: linha {erro.line}, coluna {erro.column}, caractere {erro.char!r}.'
    contexto = linha + '\n' + ' ' * (erro.column-1) + '^'
    return '<h4>' + html.escape(mensagem) + '</h4><pre>' + html.escape(contexto) + '</pre><p>' + html.escape(getattr(erro, 'dica', 'Confira o formato do campo.')) + '</p>'


def estatisticas_html(tokens):
    return tabela_html(['Tipo de token', 'Quantidade'], Counter(t.type for t in tokens).most_common())


def resumo_html(tokens, dominio, ocultar=False):
    if dominio == 'a2':
        r = comanda(tokens)
        tabela = tabela_html(['Qtd.', 'Item', 'Unitário', 'Total'],
                            [(q, n, brl(p), brl(q*p)) for q, n, p in r['itens']])
        return tabela + tabela_html(['Campo', 'Resultado'],
                [(chave, brl(r[chave])) for chave in ('subtotal', 'desconto', 'taxa', 'total')]
                + [('Pagamento', r['pagamento']), ('Entrega', r['endereco']),
                   ('Observações', '; '.join(r['observacoes'])), ('Avisos', '; '.join(r['avisos']) or 'Nenhum')])
    if dominio == 'b2':
        inicial, trs = conciliar(tokens)
        saldo, linhas = inicial, []
        for tr in trs:
            saldo += tr['valor']
            chave = (mascarar(tr['chave']) if ocultar else str(tr['chave'])) if tr['chave'] else ''
            linhas.append((tr['data'], tr['hora'], tr['tipo'], chave, tr['descricao'], brl(tr['valor']), brl(saldo)))
        entradas = sum((tr['valor'] for tr in trs if tr['valor'] > 0), Decimal(0))
        saidas = -sum((tr['valor'] for tr in trs if tr['valor'] < 0), Decimal(0))
        return (tabela_html(['Resumo', 'Valor'], [('Saldo inicial', brl(inicial)), ('Entradas', brl(entradas)),
                ('Saídas', brl(saidas)), ('Saldo final', brl(saldo)), ('Transações', len(trs))])
                + tabela_html(['Data', 'Hora', 'Operação', 'Chave', 'Descrição', 'Valor', 'Saldo'], linhas)
                + '<h4>Alertas didáticos</h4><p>' + html.escape(' | '.join(alertas(trs)) or 'Nenhum alerta.') + '</p>')
    if dominio == 'rastreio':
        r = resumo_rastreio(tokens)
        return (tabela_html(['Indicador', 'Resultado'], [('Eventos', len(r['eventos'])), ('Encomendas', r['encomendas']),
                ('Frete por encomenda, última declaração', brl(r['frete_total']))])
                + tabela_html(['Código', 'Status', 'CEP', 'Data/hora', 'Peso (kg)', 'Prazo (dias)'],
                [(e['codigo'], e['status'], e['cep'], e['instante'].strftime('%d/%m/%Y %H:%M'),
                  e.get('peso', ''), e.get('prazo', '')) for e in r['eventos']]))
    chaves = [t for t in tokens if t.type.startswith('CHAVE_')]
    return tabela_html(['Chave reconhecida', 'Valor'], [(t.type, mascarar(t) if ocultar else str(t)) for t in chaves]) if chaves else '<p>Veja a classificação nas abas Colorido e Tokens.</p>'


CSS = '''<style>
.p1-table {border-collapse:collapse; font:14px/1.5 system-ui; width:100%; color:#172033; background:white}
.p1-table th {background:#173047; color:white; text-align:left}
.p1-table td,.p1-table th {padding:7px 11px; border-bottom:1px solid #dce4eb}
.p1-code {white-space:pre-wrap; overflow-wrap:anywhere; padding:18px; background:#f5f8fb; color:#172033; line-height:1.8}
</style>'''


def interface_lexer(titulo, tokenizar, casos, dominio='', laboratorio=False):
    import ipywidgets as widgets
    from IPython.display import display
    seletor = widgets.Dropdown(options=list(casos), description='Casos:', layout=widgets.Layout(width='98%'))
    entrada = widgets.Textarea(value=next(iter(casos.values())), layout=widgets.Layout(width='98%', height='170px'))
    botao = widgets.Button(description='Analisar', button_style='primary', icon='search')
    mascara = widgets.Checkbox(value=dominio in ('b1', 'b2', 'rastreio'), description='Mascarar chaves na saída')
    prioridade = widgets.IntSlider(value=4, min=1, max=5, description='Prior. e-mail:', continuous_update=False)
    status = widgets.HTML()
    paginas = [widgets.HTML() for _ in range(4)]
    abas = widgets.Tab(children=paginas)
    for i, nome in enumerate(['Colorido', 'Tokens', 'Resumo', 'Estatística']):
        abas.set_title(i, nome)

    def atualizar(_=None):
        for pagina in paginas:
            pagina.value = ''
        try:
            tokens = tokenizar(entrada.value, prioridade.value) if laboratorio else tokenizar(entrada.value)
        except UnexpectedCharacters as erro:
            status.value = erro_lexico_html(entrada.value, erro)
            return
        status.value = f'<b>{len(tokens)} tokens reconhecidos.</b> Análise léxica concluída.'
        paginas[0].value = texto_colorido_html(entrada.value, tokens, mascara.value)
        paginas[1].value = tabela_tokens_html(tokens, mascara.value)
        paginas[3].value = estatisticas_html(tokens)
        try:
            paginas[2].value = resumo_html(tokens, dominio, mascara.value)
        except ValueError as erro:
            paginas[2].value = '<b>Erro de estrutura ou de valor no pós-processamento:</b> ' + html.escape(str(erro))

    def escolher(mudanca):
        entrada.value = casos[mudanca['new']]
        atualizar()

    botao.on_click(atualizar)
    seletor.observe(escolher, names='value')
    mascara.observe(atualizar, names='value')
    prioridade.observe(atualizar, names='value')
    elementos = [widgets.HTML(CSS + '<h2>' + html.escape(titulo) + '</h2>'), seletor, entrada,
                 widgets.HBox([botao, mascara])]
    if laboratorio:
        elementos += [prioridade, widgets.HTML('Reservadas: prioridade 3. Compare pix@loja.com.br com prioridade 2 e 4.')]
    elementos += [widgets.HTML('<small>A máscara atua nas chaves reconhecidas da saída. Entrada e contexto de erro continuam editáveis e visíveis.</small>'), status, abas]
    painel = widgets.VBox(elementos)
    atualizar()
    display(painel)
    return dict(painel=painel, entrada=entrada, seletor=seletor, botao=botao, mascara=mascara,
                prioridade=prioridade, status=status, abas=abas, atualizar=atualizar)


# %% Execução no terminal
def demonstrar():
    for nome, texto in CASOS_RASTREIO.items():
        try:
            tokens = tokenizar_rastreio(texto)
            print(f'{nome}: {len(tokens)} tokens; linhas {[t.line for t in tokens[:3]]}')
        except UnexpectedCharacters as erro:
            print(f'{nome}: erro L{erro.line} C{erro.column} {erro.char!r}; {erro.dica}')
    print('Comanda guiada:', brl(comanda(tokenizar_a2(CASOS_A2['Guiado: VR e DESC20']))['total']))
    inicial, trs = conciliar(tokenizar_b2(EXTRATO_EXEMPLO))
    print('Saldo final do extrato:', brl(inicial + sum(t['valor'] for t in trs)))


if __name__ == '__main__':
    demonstrar()
