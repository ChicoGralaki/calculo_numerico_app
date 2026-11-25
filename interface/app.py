"""Interface gráfica Tkinter para os métodos de Cálculo Numérico."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any

from calculo_numerico.erros import ErroNumerico, ResultadoMetodo
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
from calculo_numerico.validacao import inteiro, lista_numeros, matriz_numerica, numero


class AplicacaoCalculoNumerico(tk.Tk):
    """Janela principal e controladora dos quatro grupos de métodos."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Laboratório de Cálculo Numérico")
        self.geometry("1180x790")
        self.minsize(980, 680)
        self._configurar_estilo()
        self._construir_interface()

    def _configurar_estilo(self) -> None:
        estilo = ttk.Style(self)
        try:
            estilo.theme_use("clam")
        except tk.TclError:
            pass
        estilo.configure("TFrame", padding=5)
        estilo.configure("TLabelframe", padding=10)
        estilo.configure("TLabelframe.Label", font=("Segoe UI", 10, "bold"))
        estilo.configure("TLabel", font=("Segoe UI", 10))
        estilo.configure("TButton", font=("Segoe UI", 10, "bold"), padding=(12, 7))
        estilo.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=(16, 9))
        estilo.configure("Title.TLabel", font=("Segoe UI", 19, "bold"))
        estilo.configure("Subtitle.TLabel", font=("Segoe UI", 10))
        estilo.configure("Hint.TLabel", font=("Segoe UI", 9), foreground="#555555")
        estilo.configure("Run.TButton", font=("Segoe UI", 10, "bold"), padding=(16, 9))

    def _construir_interface(self) -> None:
        cabecalho = ttk.Frame(self, padding=(18, 14, 18, 8))
        cabecalho.pack(fill="x")
        ttk.Label(cabecalho, text="LABORATÓRIO DE CÁLCULO NUMÉRICO", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            cabecalho,
            text="Métodos de raízes • Sistemas lineares • Interpolação • Integração numérica",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(3, 0))

        self.abas = ttk.Notebook(self)
        self.abas.pack(fill="both", expand=True, padx=14, pady=(4, 12))
        self._criar_aba_raizes()
        self._criar_aba_sistemas()
        self._criar_aba_interpolacao()
        self._criar_aba_integracao()

        rodape = ttk.Frame(self, padding=(16, 0, 16, 8))
        rodape.pack(fill="x")
        ttk.Label(
            rodape,
            text="Entradas são lidas como texto e validadas antes dos cálculos. Resultados em ponto flutuante são aproximações numéricas.",
            style="Hint.TLabel",
        ).pack(anchor="w")

    # ------------------------------------------------------------------
    # Componentes reutilizáveis da interface
    # ------------------------------------------------------------------
    @staticmethod
    def _criar_painel_saida(parent: ttk.Frame) -> tk.Text:
        painel = ttk.LabelFrame(parent, text="Resultado e desenvolvimento")
        painel.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        painel.rowconfigure(0, weight=1)
        painel.columnconfigure(0, weight=1)
        area = ttk.Frame(painel)
        area.grid(row=0, column=0, sticky="nsew")
        area.rowconfigure(0, weight=1)
        area.columnconfigure(0, weight=1)
        saida = tk.Text(
            area,
            wrap="none",
            font=("Consolas", 9),
            padx=10,
            pady=10,
            height=25,
            state="disabled",
        )
        barra_vertical = ttk.Scrollbar(area, orient="vertical", command=saida.yview)
        barra_horizontal = ttk.Scrollbar(area, orient="horizontal", command=saida.xview)
        saida.configure(yscrollcommand=barra_vertical.set, xscrollcommand=barra_horizontal.set)
        saida.grid(row=0, column=0, sticky="nsew")
        barra_vertical.grid(row=0, column=1, sticky="ns")
        barra_horizontal.grid(row=1, column=0, sticky="ew")
        return saida

    @staticmethod
    def _criar_campo(parent: ttk.Frame, rotulo: str, valor: str = "", largura: int = 28) -> tk.StringVar:
        linha = parent.grid_size()[1]
        ttk.Label(parent, text=rotulo).grid(row=linha, column=0, sticky="w", pady=(5, 2))
        variavel = tk.StringVar(value=valor)
        entrada = ttk.Entry(parent, textvariable=variavel, width=largura)
        entrada.grid(row=linha, column=1, sticky="ew", pady=(5, 2), padx=(8, 0))
        parent.columnconfigure(1, weight=1)
        return variavel

    @staticmethod
    def _criar_texto(parent: ttk.Frame, rotulo: str, valor: str, altura: int = 5) -> tk.Text:
        linha = parent.grid_size()[1]
        ttk.Label(parent, text=rotulo).grid(row=linha, column=0, sticky="nw", pady=(6, 2))
        caixa = tk.Text(parent, height=altura, width=28, font=("Consolas", 9), wrap="none")
        caixa.insert("1.0", valor)
        caixa.grid(row=linha, column=1, sticky="ew", pady=(6, 2), padx=(8, 0))
        parent.columnconfigure(1, weight=1)
        return caixa

    @staticmethod
    def _texto_entrada(caixa: tk.Text) -> str:
        return caixa.get("1.0", "end-1c").strip()

    @staticmethod
    def _formatar_celula(valor: Any) -> str:
        if isinstance(valor, float):
            return f"{valor:.6g}"
        return str(valor)

    @classmethod
    def _formatar_tabela(cls, colunas: list[str], linhas: list[list[Any]]) -> str:
        if not colunas or not linhas:
            return ""
        largura = [len(str(c)) for c in colunas]
        for linha in linhas:
            for i, valor in enumerate(linha[: len(largura)]):
                largura[i] = min(25, max(largura[i], len(cls._formatar_celula(valor))))
        separador = "-+-".join("-" * w for w in largura)
        cabecalho = " | ".join(str(c)[:largura[i]].ljust(largura[i]) for i, c in enumerate(colunas))
        partes = [cabecalho, separador]
        for linha in linhas:
            celulas = []
            for i, w in enumerate(largura):
                valor = cls._formatar_celula(linha[i]) if i < len(linha) else ""
                if len(valor) > w:
                    valor = valor[: w - 1] + "…"
                celulas.append(valor.ljust(w))
            partes.append(" | ".join(celulas))
        return "\n".join(partes)

    @classmethod
    def _mostrar_resultado(cls, caixa: tk.Text, resultado: ResultadoMetodo) -> None:
        partes = ["=" * 76, "RESULTADO", "=" * 76, resultado.resumo]
        if resultado.detalhes:
            partes += ["", "OBSERVAÇÕES"]
            partes += [f"• {item}" for item in resultado.detalhes]
        if resultado.iteracoes:
            partes += ["", f"TABELA DE ITERAÇÕES / VALORES INTERMEDIÁRIOS ({len(resultado.iteracoes)} linhas)"]
            partes.append(cls._formatar_tabela(resultado.colunas, resultado.iteracoes))
        texto = "\n".join(partes)
        caixa.configure(state="normal")
        caixa.delete("1.0", "end")
        caixa.insert("1.0", texto)
        caixa.configure(state="disabled")

    @staticmethod
    def _mostrar_erro(caixa: tk.Text, mensagem: str) -> None:
        caixa.configure(state="normal")
        caixa.delete("1.0", "end")
        caixa.insert("1.0", "ERRO NA ENTRADA OU NO CÁLCULO\n" + "-" * 48 + "\n" + mensagem)
        caixa.configure(state="disabled")

    # ------------------------------------------------------------------
    # A) Métodos para determinação de raízes
    # ------------------------------------------------------------------
    def _criar_aba_raizes(self) -> None:
        aba = ttk.Frame(self.abas, padding=10)
        aba.columnconfigure(0, weight=0, minsize=355)
        aba.columnconfigure(1, weight=1)
        aba.rowconfigure(0, weight=1)
        self.abas.add(aba, text="A. Raízes")

        formulario = ttk.LabelFrame(aba, text="Dados de entrada")
        formulario.grid(row=0, column=0, sticky="nsew")
        formulario.columnconfigure(1, weight=1)
        ttk.Label(formulario, text="Método").grid(row=0, column=0, sticky="w", pady=4)
        self.raiz_metodo = tk.StringVar(value="Bissecção")
        seletor = ttk.Combobox(
            formulario, textvariable=self.raiz_metodo, state="readonly",
            values=["Bissecção", "Newton-Raphson", "Secante", "Falsa Posição (Regula Falsi)"],
        )
        seletor.grid(row=0, column=1, sticky="ew", pady=4, padx=(8, 0))
        seletor.bind("<<ComboboxSelected>>", lambda _e: self._atualizar_formulario_raizes())
        self.raiz_campos = ttk.Frame(formulario)
        self.raiz_campos.grid(row=1, column=0, columnspan=2, sticky="ew")
        ttk.Label(
            formulario,
            text="Funções: sin/sen, cos, tan, exp, ln/log, sqrt, abs, pi e e. Use * para multiplicar, ^ para potência e ponto decimal.",
            style="Hint.TLabel", wraplength=320,
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(10, 8))
        ttk.Button(formulario, text="Executar método", style="Run.TButton", command=self._executar_raiz).grid(
            row=3, column=0, columnspan=2, sticky="ew", pady=(8, 0)
        )
        self.raiz_saida = self._criar_painel_saida(aba)
        self._atualizar_formulario_raizes()

    def _atualizar_formulario_raizes(self) -> None:
        for widget in self.raiz_campos.winfo_children():
            widget.destroy()
        metodo = self.raiz_metodo.get()
        self.raiz_vars: dict[str, tk.StringVar] = {}
        self.raiz_vars["f"] = self._criar_campo(self.raiz_campos, "Função f(x)", "x^3 - x - 2", 24)
        if metodo == "Newton-Raphson":
            self.raiz_vars["df"] = self._criar_campo(self.raiz_campos, "Derivada f'(x)", "3*x^2 - 1", 24)
            self.raiz_vars["x0"] = self._criar_campo(self.raiz_campos, "Aproximação inicial x₀", "1.5")
        elif metodo == "Secante":
            self.raiz_vars["x0"] = self._criar_campo(self.raiz_campos, "Aproximação inicial x₀", "1")
            self.raiz_vars["x1"] = self._criar_campo(self.raiz_campos, "Aproximação inicial x₁", "2")
        else:
            self.raiz_vars["a"] = self._criar_campo(self.raiz_campos, "Limite inferior a", "1")
            self.raiz_vars["b"] = self._criar_campo(self.raiz_campos, "Limite superior b", "2")
        self.raiz_vars["tol"] = self._criar_campo(self.raiz_campos, "Tolerância δ", "0.000001")
        self.raiz_vars["iter"] = self._criar_campo(self.raiz_campos, "Máximo de iterações", "100")

    def _executar_raiz(self) -> None:
        try:
            valores = self.raiz_vars
            f = compilar_funcao(valores["f"].get())
            tolerancia = numero(valores["tol"].get(), "tolerância")
            max_iter = inteiro(valores["iter"].get(), "máximo de iterações")
            metodo = self.raiz_metodo.get()
            if metodo == "Bissecção":
                resultado = bisseccao(f, numero(valores["a"].get(), "a"), numero(valores["b"].get(), "b"), tolerancia, max_iter)
            elif metodo == "Newton-Raphson":
                df = compilar_funcao(valores["df"].get())
                resultado = newton_raphson(f, df, numero(valores["x0"].get(), "x₀"), tolerancia, max_iter)
            elif metodo == "Secante":
                resultado = secante(f, numero(valores["x0"].get(), "x₀"), numero(valores["x1"].get(), "x₁"), tolerancia, max_iter)
            else:
                resultado = falsa_posicao(f, numero(valores["a"].get(), "a"), numero(valores["b"].get(), "b"), tolerancia, max_iter)
            self._mostrar_resultado(self.raiz_saida, resultado)
        except (ErroNumerico, ValueError, ArithmeticError) as exc:
            self._mostrar_erro(self.raiz_saida, str(exc))
        except Exception as exc:  # evita que uma entrada inesperada encerre a interface
            self._mostrar_erro(self.raiz_saida, f"Falha inesperada: {exc}")

    # ------------------------------------------------------------------
    # B) Sistemas lineares
    # ------------------------------------------------------------------
    def _criar_aba_sistemas(self) -> None:
        aba = ttk.Frame(self.abas, padding=10)
        aba.columnconfigure(0, weight=0, minsize=385)
        aba.columnconfigure(1, weight=1)
        aba.rowconfigure(0, weight=1)
        self.abas.add(aba, text="B. Sistemas lineares")
        formulario = ttk.LabelFrame(aba, text="Sistema A·x = b")
        formulario.grid(row=0, column=0, sticky="nsew")
        formulario.columnconfigure(1, weight=1)
        ttk.Label(formulario, text="Método").grid(row=0, column=0, sticky="w", pady=4)
        self.sistema_metodo = tk.StringVar(value="Eliminação de Gauss")
        seletor = ttk.Combobox(
            formulario, textvariable=self.sistema_metodo, state="readonly",
            values=["Eliminação de Gauss", "Fatoração LU", "Gauss-Seidel"],
        )
        seletor.grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=4)
        self.matriz_texto = self._criar_texto(formulario, "Matriz A", "10 2 1\n1 5 1\n2 3 10", 6)
        self.vetor_texto = self._criar_texto(formulario, "Vetor b", "14\n11\n8", 3)
        self.sistema_x0 = self._criar_campo(formulario, "Aproximação x(0), GS", "0; 0; 0")
        self.sistema_tol = self._criar_campo(formulario, "Tolerância, GS", "0.0001")
        self.sistema_iter = self._criar_campo(formulario, "Máximo de iterações, GS", "100")
        ttk.Label(
            formulario,
            text="Uma linha por equação. Separe coeficientes por espaço ou ;. O vetor b pode usar quebras de linha ou ;.",
            style="Hint.TLabel", wraplength=345,
        ).grid(row=formulario.grid_size()[1], column=0, columnspan=2, sticky="w", pady=(8, 6))
        ttk.Button(formulario, text="Resolver sistema", style="Run.TButton", command=self._executar_sistema).grid(
            row=formulario.grid_size()[1], column=0, columnspan=2, sticky="ew", pady=(6, 0)
        )
        self.sistema_saida = self._criar_painel_saida(aba)

    def _executar_sistema(self) -> None:
        try:
            a = matriz_numerica(self._texto_entrada(self.matriz_texto))
            b = lista_numeros(self._texto_entrada(self.vetor_texto), "vetor b")
            metodo = self.sistema_metodo.get()
            if metodo == "Eliminação de Gauss":
                resultado = eliminacao_gauss(a, b)
            elif metodo == "Fatoração LU":
                resultado = fatoracao_lu(a, b)
            else:
                x0_texto = self.sistema_x0.get().strip()
                x0 = lista_numeros(x0_texto, "aproximação inicial x(0)") if x0_texto else [0.0] * len(a)
                tolerancia = numero(self.sistema_tol.get(), "tolerância")
                max_iter = inteiro(self.sistema_iter.get(), "máximo de iterações")
                resultado = gauss_seidel(a, b, x0, tolerancia, max_iter)
            self._mostrar_resultado(self.sistema_saida, resultado)
        except (ErroNumerico, ValueError, ArithmeticError) as exc:
            self._mostrar_erro(self.sistema_saida, str(exc))
        except Exception as exc:
            self._mostrar_erro(self.sistema_saida, f"Falha inesperada: {exc}")

    # ------------------------------------------------------------------
    # C) Interpolação
    # ------------------------------------------------------------------
    def _criar_aba_interpolacao(self) -> None:
        aba = ttk.Frame(self.abas, padding=10)
        aba.columnconfigure(0, weight=0, minsize=365)
        aba.columnconfigure(1, weight=1)
        aba.rowconfigure(0, weight=1)
        self.abas.add(aba, text="C. Interpolação")
        formulario = ttk.LabelFrame(aba, text="Pontos conhecidos")
        formulario.grid(row=0, column=0, sticky="nsew")
        formulario.columnconfigure(1, weight=1)
        ttk.Label(formulario, text="Forma").grid(row=0, column=0, sticky="w", pady=4)
        self.interp_metodo = tk.StringVar(value="Lagrange")
        ttk.Combobox(formulario, textvariable=self.interp_metodo, state="readonly", values=["Lagrange", "Newton"]).grid(
            row=0, column=1, sticky="ew", padx=(8, 0), pady=4
        )
        self.interp_x = self._criar_texto(formulario, "Valores de x", "-1; 0; 2", 4)
        self.interp_y = self._criar_texto(formulario, "Valores de f(x)", "4; 1; -1", 4)
        self.interp_alvo = self._criar_campo(formulario, "Ponto desejado x*", "0.5")
        ttk.Label(
            formulario,
            text="Informe x e f(x) na mesma ordem. Separe os valores por ; ou por quebras de linha. Os valores de x precisam ser distintos.",
            style="Hint.TLabel", wraplength=325,
        ).grid(row=formulario.grid_size()[1], column=0, columnspan=2, sticky="w", pady=(8, 6))
        ttk.Button(formulario, text="Interpolar", style="Run.TButton", command=self._executar_interpolacao).grid(
            row=formulario.grid_size()[1], column=0, columnspan=2, sticky="ew", pady=(6, 0)
        )
        self.interp_saida = self._criar_painel_saida(aba)

    def _executar_interpolacao(self) -> None:
        try:
            xs = lista_numeros(self._texto_entrada(self.interp_x), "valores de x")
            ys = lista_numeros(self._texto_entrada(self.interp_y), "valores de f(x)")
            alvo = numero(self.interp_alvo.get(), "ponto x*")
            resultado = lagrange(xs, ys, alvo) if self.interp_metodo.get() == "Lagrange" else newton(xs, ys, alvo)
            self._mostrar_resultado(self.interp_saida, resultado)
        except (ErroNumerico, ValueError, ArithmeticError) as exc:
            self._mostrar_erro(self.interp_saida, str(exc))
        except Exception as exc:
            self._mostrar_erro(self.interp_saida, f"Falha inesperada: {exc}")

    # ------------------------------------------------------------------
    # D) Integração numérica
    # ------------------------------------------------------------------
    def _criar_aba_integracao(self) -> None:
        aba = ttk.Frame(self.abas, padding=10)
        aba.columnconfigure(0, weight=0, minsize=365)
        aba.columnconfigure(1, weight=1)
        aba.rowconfigure(0, weight=1)
        self.abas.add(aba, text="D. Integração")
        formulario = ttk.LabelFrame(aba, text="Dados de integração")
        formulario.grid(row=0, column=0, sticky="nsew")
        formulario.columnconfigure(1, weight=1)
        ttk.Label(formulario, text="Tipo de entrada").grid(row=0, column=0, sticky="w", pady=4)
        self.integracao_tipo = tk.StringVar(value="Função f(x)")
        seletor_tipo = ttk.Combobox(formulario, textvariable=self.integracao_tipo, state="readonly", values=["Função f(x)", "Caso discreto (tabela)"])
        seletor_tipo.grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=4)
        seletor_tipo.bind("<<ComboboxSelected>>", lambda _e: self._atualizar_formulario_integracao())
        ttk.Label(formulario, text="Método").grid(row=1, column=0, sticky="w", pady=4)
        self.integracao_metodo = tk.StringVar(value="Trapézio Repetido")
        self.integracao_seletor_metodo = ttk.Combobox(formulario, textvariable=self.integracao_metodo, state="readonly")
        self.integracao_seletor_metodo.grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=4)
        self.integracao_campos = ttk.Frame(formulario)
        self.integracao_campos.grid(row=2, column=0, columnspan=2, sticky="ew")
        self.integracao_ajuda = ttk.Label(formulario, text="", style="Hint.TLabel", wraplength=325)
        self.integracao_ajuda.grid(row=3, column=0, columnspan=2, sticky="w", pady=(10, 6))
        ttk.Button(formulario, text="Calcular integral", style="Run.TButton", command=self._executar_integracao).grid(
            row=4, column=0, columnspan=2, sticky="ew", pady=(8, 0)
        )
        self.integracao_saida = self._criar_painel_saida(aba)
        self._atualizar_formulario_integracao()

    def _atualizar_formulario_integracao(self) -> None:
        for widget in self.integracao_campos.winfo_children():
            widget.destroy()
        discreto = self.integracao_tipo.get() == "Caso discreto (tabela)"
        if discreto:
            self.integracao_seletor_metodo.configure(values=["Trapézios (dados discretos)", "Simpson 1/3 (dados discretos)"])
            self.integracao_metodo.set("Trapézios (dados discretos)")
            self.integracao_vars = {
                "x": self._criar_texto(self.integracao_campos, "Valores de x", "0; 1; 2; 3; 4", 4),
                "y": self._criar_texto(self.integracao_campos, "Valores de f(x)", "0; 1; 4; 9; 16", 4),
            }
            self.integracao_ajuda.configure(
                text="Use os dados tabelados na ordem crescente de x. Trapézios aceita espaçamentos irregulares; Simpson exige espaçamento uniforme e número par de segmentos."
            )
        else:
            self.integracao_seletor_metodo.configure(values=["Trapézio Repetido", "Simpson 1/3 Repetida"])
            self.integracao_metodo.set("Trapézio Repetido")
            self.integracao_vars = {
                "f": self._criar_campo(self.integracao_campos, "Função f(x)", "exp(x)", 24),
                "a": self._criar_campo(self.integracao_campos, "Limite inferior a", "0"),
                "b": self._criar_campo(self.integracao_campos, "Limite superior b", "1"),
                "n": self._criar_campo(self.integracao_campos, "Subintervalos n", "10"),
            }
            self.integracao_ajuda.configure(
                text="A Regra 1/3 de Simpson Repetida exige n par. As duas regras usam pontos igualmente espaçados no intervalo."
            )

    def _executar_integracao(self) -> None:
        try:
            metodo = self.integracao_metodo.get()
            if self.integracao_tipo.get() == "Caso discreto (tabela)":
                xs = lista_numeros(self._texto_entrada(self.integracao_vars["x"]), "valores de x")  # type: ignore[arg-type]
                ys = lista_numeros(self._texto_entrada(self.integracao_vars["y"]), "valores de f(x)")  # type: ignore[arg-type]
                resultado = trapezio_discreto(xs, ys) if metodo.startswith("Trapézios") else simpson_discreto(xs, ys)
            else:
                f = compilar_funcao(self.integracao_vars["f"].get())  # type: ignore[union-attr]
                a = numero(self.integracao_vars["a"].get(), "limite inferior a")  # type: ignore[union-attr]
                b = numero(self.integracao_vars["b"].get(), "limite superior b")  # type: ignore[union-attr]
                n = inteiro(self.integracao_vars["n"].get(), "número de subintervalos")  # type: ignore[union-attr]
                resultado = trapezio_repetido(f, a, b, n) if metodo == "Trapézio Repetido" else simpson_repetida(f, a, b, n)
            self._mostrar_resultado(self.integracao_saida, resultado)
        except (ErroNumerico, ValueError, ArithmeticError) as exc:
            self._mostrar_erro(self.integracao_saida, str(exc))
        except Exception as exc:
            self._mostrar_erro(self.integracao_saida, f"Falha inesperada: {exc}")


def iniciar() -> None:
    app = AplicacaoCalculoNumerico()
    app.mainloop()
