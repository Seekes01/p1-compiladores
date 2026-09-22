from contextlib import redirect_stdout
from datetime import datetime
from decimal import Decimal
import io
import re
import unittest

from lark import Lark
from lark.exceptions import UnexpectedCharacters
import p1


class ExerciciosTeoricos(unittest.TestCase):
    def test_tabela_exercicio_1(self):
        texto = '# almoço\npedido 3X "Pastel de Queijo" R$ 8,50\nPAGAMENTO Cartão'
        ts = p1.analisar(texto, p1.GRAMATICA_A2_BASE)
        self.assertEqual([(t.type, str(t), t.line, t.column) for t in ts], [
            ('PEDIDO', 'pedido', 2, 1), ('QTD', '3X', 2, 8),
            ('TEXTO', '"Pastel de Queijo"', 2, 11), ('PRECO', 'R$ 8,50', 2, 30),
            ('PAGAMENTO', 'PAGAMENTO', 3, 1), ('FORMA_PGTO', 'Cartão', 3, 11)])

    def test_exercicio_2(self):
        for texto, tipo in [('em@banco.com', 'CHAVE_EMAIL'), ('+5511987654321', 'CHAVE_TELEFONE'), ('09:45', 'HORA')]:
            with self.subTest(texto=texto):
                ts = p1.analisar(texto, p1.GRAMATICA_B1_BASE)
                self.assertEqual([(t.type, str(t)) for t in ts], [(tipo, texto)])
        with self.assertRaises(UnexpectedCharacters) as erro:
            p1.analisar('EMPRESA', p1.GRAMATICA_B1_BASE)
        self.assertEqual((erro.exception.line, erro.exception.column, erro.exception.char), (1, 1, 'E'))

    def test_exercicio_3_posicao_real(self):
        texto = 'SALDO INICIAL R$ 300,00\nPIX ENVIADO R$ 45,00 PARA joao@@mail.com EM 01/09/2026 10:00'
        with self.assertRaises(UnexpectedCharacters) as erro:
            p1.analisar(texto, p1.GRAMATICA_B2_BASE)
        self.assertEqual(erro.exception.column, texto.splitlines()[1].index('joao') + 1)
        self.assertEqual((erro.exception.line, erro.exception.column, erro.exception.char), (2, 27, 'j'))

    def test_regex_exercicio_4(self):
        for regex, valido, invalido in [
            (r'[A-Z]{2}\d{9}[A-Z]{2}', 'BR123456789BR', 'BR12345678BR'),
            (r'[A-Z]{3}\d[A-Z]\d{2}', 'ABC1D23', 'ABC1234'),
            (r'\d{5}-\d{3}', '01310-100', '01310100')]:
            with self.subTest(regex=regex):
                self.assertIsNotNone(re.fullmatch(regex, valido))
                self.assertIsNone(re.fullmatch(regex, invalido))

    def test_cupom_inexistente_e_semantica(self):
        r = p1.comanda(p1.tokenizar_a2(p1.CASOS_A2['Cupom inexistente (léxico válido)']))
        self.assertEqual(r['total'], Decimal('32.00'))
        self.assertIn('recusado', r['avisos'][0])


class ExerciciosPraticos(unittest.TestCase):
    def test_a1_obs(self):
        ts = p1.tokenizar_a1(p1.CASOS_A1['Guiado: OBS'])
        self.assertEqual([t.type for t in ts], ['PEDIDO', 'QTD', 'ITEM', 'PRECO', 'OBS', 'ITEM'])

    def test_a1_literal_e_palavra_maior(self):
        self.assertEqual(p1.tokenizar_a1('PEDIDOS')[0].type, 'CODIGO')
        with self.assertRaises(UnexpectedCharacters):
            p1.tokenizar_a1('pedido')

    def test_a1_experimento_preco(self):
        gramatica_ruim = p1.GRAMATICA_A1_BASE.replace('PRECO.2:', 'PRECO:')
        with self.assertRaises(UnexpectedCharacters) as erro:
            p1.analisar('R$ 25,90', gramatica_ruim)
        self.assertEqual((erro.exception.column, erro.exception.char), (2, '$'))
        self.assertEqual(p1.tokenizar_a1('R$ 25,90')[0].type, 'PRECO')

    def test_vr_e_desc20_com_calculo(self):
        ts = p1.tokenizar_a2(p1.CASOS_A2['Guiado: VR e DESC20'])
        self.assertEqual(ts[-1].type, 'FORMA_PGTO')
        r = p1.comanda(ts)
        self.assertEqual((r['subtotal'], r['desconto'], r['total']), (Decimal(100), Decimal(20), Decimal(90)))

    def test_preco_sem_simbolo_contra_numero_e_quantidade(self):
        ts = p1.tokenizar_a2('25,90 25 25x R$ 1.250,00 1.250,00')
        self.assertEqual([t.type for t in ts], ['PRECO', 'NUMERO', 'QTD', 'PRECO', 'PRECO'])
        with self.assertRaises(UnexpectedCharacters):
            p1.tokenizar_a2('25,900')

    def test_b1_cnpj_e_cpf(self):
        self.assertEqual(p1.tokenizar_b1('12.345.678/0001-90')[0].type, 'CHAVE_CNPJ')
        self.assertEqual(p1.tokenizar_b1('123.456.789-09')[0].type, 'CHAVE_CPF')

    def test_b1_prioridade_email(self):
        self.assertEqual(p1.tokenizar_b1('pix@loja.com.br', 4)[0].type, 'CHAVE_EMAIL')
        with self.assertRaises(UnexpectedCharacters) as erro:
            p1.tokenizar_b1('pix@loja.com.br', 2)
        self.assertEqual((erro.exception.column, erro.exception.char), (4, '@'))

    def test_saque_sempre_saida(self):
        inicial, trs = p1.conciliar(p1.tokenizar_b2(p1.CASOS_B2['Guiado: SAQUE']))
        self.assertEqual(trs[0]['valor'], Decimal('-200.00'))
        self.assertEqual(inicial+trs[0]['valor'], Decimal('100.00'))
        with self.assertRaises(ValueError):
            p1.conciliar(p1.tokenizar_b2('SAQUE RECEBIDO R$ 200,00 EM 05/09/2026 18:00'))

    def test_telefone_local_e_versoes(self):
        self.assertEqual(p1.tokenizar_b2('11987654321')[0].type, 'CHAVE_TELEFONE')
        for gramatica in (p1.GRAMATICA_B1_BASE, p1.GRAMATICA_B2_BASE):
            with self.assertRaises(UnexpectedCharacters):
                p1.analisar('11987654321', gramatica)
        self.assertEqual(p1.tokenizar_b2('12345678909')[0].type, 'CHAVE_TELEFONE')
        for invalido in ('119876543210', '11987654321abc'):
            with self.assertRaises(UnexpectedCharacters):
                p1.tokenizar_b2(invalido)

    def test_alerta_aleatoria_limiar_e_direcao(self):
        for valor, direcao, esperado in [('500,00', 'ENVIADO', False), ('500,01', 'ENVIADO', True), ('900,00', 'RECEBIDO', False)]:
            with self.subTest(valor=valor, direcao=direcao):
                prep = 'PARA' if direcao == 'ENVIADO' else 'DE'
                texto = f'PIX {direcao} R$ {valor} {prep} {p1.UUID_EXEMPLO} EM 10/09/2026 14:32'
                _, trs = p1.conciliar(p1.tokenizar_b2(texto))
                self.assertEqual(bool(p1.alertas(trs)), esperado)

    def test_alerta_noturno_fronteiras(self):
        for hora, esperado in [('05:59', True), ('06:00', False), ('19:59', False), ('20:00', True)]:
            texto = f'PIX ENVIADO R$ 1.000,01 PARA a@example.com EM 10/09/2026 {hora}'
            _, trs = p1.conciliar(p1.tokenizar_b2(texto))
            self.assertEqual(bool(p1.alertas(trs)), esperado)

    def test_comanda_e_extrato_do_roteiro(self):
        r = p1.comanda(p1.tokenizar_a2(p1.CASOS_A2['Pedido completo']))
        self.assertEqual(r['total'], Decimal('87.46'))
        r = p1.comanda(p1.tokenizar_a2(p1.CASOS_A2['Frete grátis']))
        self.assertEqual((r['total'], r['taxa']), (Decimal('1150.00'), Decimal(0)))
        inicial, trs = p1.conciliar(p1.tokenizar_b2(p1.EXTRATO_EXEMPLO))
        self.assertEqual(sum((t['valor'] for t in trs if t['valor'] > 0), Decimal(0)), Decimal('3250.00'))
        self.assertEqual(-sum((t['valor'] for t in trs if t['valor'] < 0), Decimal(0)), Decimal('1987.30'))
        self.assertEqual(inicial+sum(t['valor'] for t in trs), Decimal('3762.70'))

    def test_data_inexistente_apenas_no_pos_processamento(self):
        ts = p1.tokenizar_b2('SAQUE R$ 20,00 EM 31/02/2026 18:00')
        self.assertIn('DATA', [t.type for t in ts])
        with self.assertRaises(ValueError):
            p1.conciliar(ts)


class DesafioRastreio(unittest.TestCase):
    def test_quantidade_tokens_e_reservadas(self):
        lexer = p1.criar_lexer(p1.GRAMATICA_RASTREIO)
        terminais = [t for t in lexer.terminals if t.name not in lexer.ignore_tokens]
        self.assertEqual(len(terminais), 22)
        reservadas = [t for t in terminais if t.priority == 4]
        self.assertEqual(len(reservadas), 11)
        for terminal in reservadas:
            self.assertIn('i', terminal.pattern.flags)
            self.assertIn(r'\b', terminal.pattern.value)

    def test_tres_validos(self):
        for nome, texto in p1.CASOS_RASTREIO.items():
            if nome.startswith('Válido'):
                with self.subTest(nome=nome):
                    ts = p1.tokenizar_rastreio(texto)
                    self.assertGreater(len(ts), 0)
                    self.assertGreater(p1.resumo_rastreio(ts)['encomendas'], 0)

    def test_invalidos_posicoes_e_dicas(self):
        esperados = [(1, 31, '"'), (1, 45, '0'), (1, 85, '@')]
        invalidos = [v for k, v in p1.CASOS_RASTREIO.items() if k.startswith('Inválido')]
        for texto, esperado in zip(invalidos, esperados):
            with self.subTest(texto=texto):
                with self.assertRaises(UnexpectedCharacters) as ctx:
                    p1.tokenizar_rastreio(texto)
                e = ctx.exception
                self.assertEqual((e.line, e.column, e.char), esperado)
                self.assertGreater(len(e.dica), 30)

    def test_conflitos_documentados(self):
        self.assertEqual(p1.tokenizar_rastreio('em@exemplo.com')[0].type, 'EMAIL')
        self.assertEqual(p1.tokenizar_rastreio('BR123456789BR')[0].type, 'COD_RASTREIO')
        ruim = p1.GRAMATICA_RASTREIO.replace('EMAIL.5:', 'EMAIL.3:')
        with self.assertRaises(UnexpectedCharacters):
            p1.analisar('em@exemplo.com', ruim)
        ruim = p1.GRAMATICA_RASTREIO.replace('COD_RASTREIO.3:', 'COD_RASTREIO:')
        self.assertEqual(p1.analisar('BR123456789BR', ruim)[0].type, 'IDENTIFICADOR')

    def test_fronteira_de_palavra(self):
        ts = p1.tokenizar_rastreio('RASTREIOS Em empresa 3 3kg')
        self.assertEqual([t.type for t in ts], ['IDENTIFICADOR', 'EM', 'IDENTIFICADOR', 'NUMERO', 'PESO_VALOR'])

    def test_comentarios_e_posicoes(self):
        texto = '# início\n\trastreio BR123456789BR # fim\nSTATUS "# dentro do texto"'
        ts = p1.tokenizar_rastreio(texto)
        self.assertEqual((ts[0].line, ts[0].column), (2, 2))
        self.assertEqual(str(ts[-1]), '"# dentro do texto"')
        for t in ts:
            self.assertEqual(texto[t.start_pos:t.end_pos], str(t))

    def test_conversoes_e_frete_sem_duplicar(self):
        r = p1.resumo_rastreio(p1.tokenizar_rastreio(p1.CASOS_RASTREIO['Válido 2: completo e minúsculas']))
        e = r['eventos'][0]
        self.assertEqual(e['peso'], Decimal('1.250'))
        self.assertEqual(e['prazo'], 3)
        self.assertIsInstance(e['instante'], datetime)
        r = p1.resumo_rastreio(p1.tokenizar_rastreio(p1.CASOS_RASTREIO['Válido 3: vários eventos']))
        self.assertEqual((r['encomendas'], len(r['eventos']), r['frete_total']), (2, 3, Decimal('35.90')))

    def test_lexico_nao_garante_estrutura(self):
        for texto in ('STATUS RASTREIO', p1.CASOS_RASTREIO['Válido 1: entrega'].replace('BR123456789BR', 'CODIGOERRADO')):
            ts = p1.tokenizar_rastreio(texto)
            with self.assertRaises(ValueError):
                p1.resumo_rastreio(ts)

    def test_rejeita_campos_duplicados(self):
        texto = p1.CASOS_RASTREIO['Válido 1: entrega'] + ' FRETE R$ 1,00 FRETE R$ 2,00'
        with self.assertRaises(ValueError):
            p1.resumo_rastreio(p1.tokenizar_rastreio(texto))


class Apresentacao(unittest.TestCase):
    def test_escape_html(self):
        texto = '"<script>alert(1)</script>"'
        ts = p1.tokenizar_rastreio(texto)
        for saida in (p1.texto_colorido_html(texto, ts), p1.tabela_tokens_html(ts)):
            self.assertNotIn('<script>', saida)
            self.assertIn('&lt;script&gt;', saida)

    def test_mascara_preserva_tokens(self):
        texto = 'CONTATO em@exemplo.com DESTINATARIO 123.456.789-09 # anotação'
        ts = p1.tokenizar_rastreio(texto)
        antes = [(str(t), t.start_pos, t.end_pos) for t in ts]
        for saida in (p1.texto_colorido_html(texto, ts, True), p1.tabela_tokens_html(ts, True)):
            self.assertNotIn('em@exemplo.com', saida)
            self.assertNotIn('123.456.789-09', saida)
        self.assertEqual(antes, [(str(t), t.start_pos, t.end_pos) for t in ts])

    def test_interfaces_callbacks_e_limpeza(self):
        for dominio, funcao, casos in [('a1', p1.tokenizar_a1, p1.CASOS_A1), ('a2', p1.tokenizar_a2, p1.CASOS_A2),
                                       ('b1', p1.tokenizar_b1, p1.CASOS_B1), ('b2', p1.tokenizar_b2, p1.CASOS_B2),
                                       ('rastreio', p1.tokenizar_rastreio, p1.CASOS_RASTREIO)]:
            with self.subTest(dominio=dominio), redirect_stdout(io.StringIO()):
                ui = p1.interface_lexer(dominio, funcao, casos, dominio, dominio == 'b1')
                for nome in casos:
                    ui['seletor'].value = nome
                    ui['botao'].click()
                    self.assertTrue(ui['status'].value)
                    if nome.startswith('Inválido'):
                        self.assertIn('Erro léxico', ui['status'].value)
                        self.assertTrue(all(not pagina.value for pagina in ui['abas'].children))
                    else:
                        self.assertIn('tokens reconhecidos', ui['status'].value)
                ui['mascara'].value = not ui['mascara'].value
                if dominio == 'b1':
                    ui['seletor'].value = 'Conflito pix@'
                    ui['prioridade'].value = 2
                    self.assertIn('Erro léxico', ui['status'].value)
                    ui['prioridade'].value = 4
                    self.assertIn('tokens reconhecidos', ui['status'].value)
                ui['painel'].close()


if __name__ == '__main__':
    unittest.main(verbosity=2)
