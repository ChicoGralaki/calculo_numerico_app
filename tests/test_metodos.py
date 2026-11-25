"""Testes automáticos dos métodos implementados no projeto.

Execute na pasta raiz com: python -m unittest discover -s tests -v
"""

import math
import unittest

from calculo_numerico.expressoes import compilar_funcao
from calculo_numerico.integracao import (
    simpson_discreto,
    simpson_repetida,
    trapezio_discreto,
    trapezio_repetido,
)
from calculo_numerico.interpolacao import lagrange, newton
from calculo_numerico.raizes import bisseccao, falsa_posicao, newton_raphson, secante
from calculo_numerico.sistemas import eliminacao_gauss, fatoracao_lu, gauss_seidel
from calculo_numerico.erros import ErroNumerico


class TesteExpressoes(unittest.TestCase):
    def test_operadores_e_funcoes(self):
        f = compilar_funcao("sen(x)^2 + cos(x)^2")
        self.assertAlmostEqual(f(0.73), 1.0, places=12)

    def test_bloqueia_codigo_arbitrario(self):
        with self.assertRaises(ErroNumerico):
            compilar_funcao("__import__('os').system('echo inseguro')")(0)


class TesteRaizes(unittest.TestCase):
    def setUp(self):
        self.f = lambda x: x * x - 2.0
        self.df = lambda x: 2.0 * x
        self.alvo = math.sqrt(2.0)

    def test_bisseccao(self):
        r = bisseccao(self.f, 1.0, 2.0, 1e-10, 200)
        self.assertTrue(r.convergiu)
        valor = float(r.resumo.split("x = ")[1].split("\n")[0])
        self.assertAlmostEqual(valor, self.alvo, places=8)

    def test_newton_raphson(self):
        r = newton_raphson(self.f, self.df, 1.0, 1e-10, 50)
        self.assertTrue(r.convergiu)
        self.assertLess(abs(self.f(self.alvo)), 1e-12)
        self.assertIn("1.414", r.resumo)

    def test_secante(self):
        r = secante(self.f, 1.0, 2.0, 1e-10, 100)
        self.assertTrue(r.convergiu)
        self.assertIn("1.414", r.resumo)

    def test_falsa_posicao(self):
        r = falsa_posicao(self.f, 1.0, 2.0, 1e-9, 500)
        self.assertTrue(r.convergiu)
        self.assertIn("1.414", r.resumo)


class TesteSistemas(unittest.TestCase):
    def setUp(self):
        self.a = [[10.0, 2.0, 1.0], [1.0, 5.0, 1.0], [2.0, 3.0, 10.0]]
        self.b = [14.0, 11.0, 8.0]

    def test_gauss(self):
        r = eliminacao_gauss(self.a, self.b)
        self.assertTrue(r.convergiu)
        self.assertIn("x1 =", r.resumo)
        self.assertIn("Resíduo", r.resumo)

    def test_lu(self):
        r = fatoracao_lu(self.a, self.b)
        self.assertTrue(r.convergiu)
        self.assertIn("P·A = L·U", r.resumo)
        self.assertIn("y (resolvendo", r.resumo)

    def test_gauss_seidel(self):
        r = gauss_seidel(self.a, self.b, [0.0, 0.0, 0.0], 1e-10, 500)
        self.assertTrue(r.convergiu)
        self.assertIn("x1 =", r.resumo)

    def test_gauss_detecta_sistema_incompativel(self):
        with self.assertRaises(ErroNumerico):
            eliminacao_gauss([[1.0, 1.0], [2.0, 2.0]], [1.0, 3.0])

    def test_pivoteamento_parcial_gauss_e_lu(self):
        matriz = [[0.0, 2.0], [1.0, 3.0]]
        vetor = [4.0, 5.0]
        rg = eliminacao_gauss(matriz, vetor)
        rlu = fatoracao_lu(matriz, vetor)
        self.assertIn("x1 = -1", rg.resumo)
        self.assertIn("x2 = 2", rg.resumo)
        self.assertIn("Permutação de linhas (P·A = L·U): 2, 1", rlu.resumo)
        self.assertIn("x1 = -1", rlu.resumo)


class TesteInterpolacao(unittest.TestCase):
    def test_lagrange_e_newton_coincidem(self):
        xs = [-1.0, 0.0, 2.0]
        ys = [4.0, 1.0, -1.0]
        alvo = 0.5
        rl = lagrange(xs, ys, alvo)
        rn = newton(xs, ys, alvo)
        vl = float(rl.resumo.split("P(x*) = ")[1].split("\n")[0])
        vn = float(rn.resumo.split("P(x*) = ")[1].split("\n")[0])
        self.assertAlmostEqual(vl, vn, places=10)
        self.assertAlmostEqual(vn, 0.0, places=10)


class TesteIntegracao(unittest.TestCase):
    def test_trapezio_repetido(self):
        r = trapezio_repetido(math.exp, 0.0, 1.0, 1000)
        self.assertTrue(r.convergiu)
        valor = float(r.resumo.split(": ")[1].split("\n")[0])
        self.assertAlmostEqual(valor, math.e - 1.0, delta=1e-6)

    def test_simpson_repetida(self):
        r = simpson_repetida(math.exp, 0.0, 1.0, 10)
        self.assertTrue(r.convergiu)
        valor = float(r.resumo.split(": ")[1].split("\n")[0])
        self.assertAlmostEqual(valor, math.e - 1.0, delta=1e-6)

    def test_simpson_rejeita_n_impar(self):
        with self.assertRaises(ErroNumerico):
            simpson_repetida(math.exp, 0.0, 1.0, 3)

    def test_integracao_discreta_irregular(self):
        r = trapezio_discreto([0.0, 1.0, 3.0], [0.0, 1.0, 3.0])
        valor = float(r.resumo.split(": ")[1].split("\n")[0])
        self.assertAlmostEqual(valor, 4.5)

    def test_simpson_discreta(self):
        r = simpson_discreto([0.0, 1.0, 2.0], [0.0, 1.0, 4.0])
        valor = float(r.resumo.split(": ")[1].split("\n")[0])
        self.assertAlmostEqual(valor, 8.0 / 3.0)

    def test_simpson_discreta_rejeita_espacamento_irregular(self):
        with self.assertRaises(ErroNumerico):
            simpson_discreto([0.0, 1.0, 3.0], [0.0, 1.0, 9.0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
