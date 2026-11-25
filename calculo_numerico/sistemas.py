"""Métodos diretos e iterativos para sistemas lineares Ax=b."""

import math
from .erros import ErroNumerico, ResultadoMetodo
from .validacao import validar_sistema, validar_tolerancia


def _norma_inf_vetor(v: list[float]) -> float:
    return max((abs(valor) for valor in v), default=0.0)


def _residuo_inf(a: list[list[float]], x: list[float], b: list[float]) -> float:
    return max(
        (abs(math.fsum(a[i][j] * x[j] for j in range(len(x))) - b[i]) for i in range(len(b))),
        default=0.0,
    )


def eliminacao_gauss(a: list[list[float]], b: list[float]) -> ResultadoMetodo:
    """Eliminação de Gauss com pivoteamento parcial e substituição retroativa."""
    matriz, vetor = validar_sistema(a, b)
    n = len(matriz)
    escala = max(1.0, max(abs(v) for linha in matriz for v in linha))
    limite = 1e-12 * escala
    aumentada = [matriz[i][:] + [vetor[i]] for i in range(n)]
    linhas: list[list[object]] = []

    linha_pivo = 0
    colunas_pivo: list[int] = []
    for coluna in range(n):
        melhor = max(range(linha_pivo, n), key=lambda i: abs(aumentada[i][coluna]), default=linha_pivo)
        if linha_pivo >= n or abs(aumentada[melhor][coluna]) <= limite:
            continue
        if melhor != linha_pivo:
            aumentada[linha_pivo], aumentada[melhor] = aumentada[melhor], aumentada[linha_pivo]
            linhas.append([f"Troca L{linha_pivo + 1} ↔ L{melhor + 1}", "Pivoteamento parcial"])
        pivo = aumentada[linha_pivo][coluna]
        for i in range(linha_pivo + 1, n):
            multiplicador = aumentada[i][coluna] / pivo
            aumentada[i][coluna] = 0.0
            for j in range(coluna + 1, n + 1):
                aumentada[i][j] -= multiplicador * aumentada[linha_pivo][j]
            linhas.append([f"L{i + 1} ← L{i + 1} - ({multiplicador:.6g})·L{linha_pivo + 1}", f"Pivô da coluna {coluna + 1}: {pivo:.6g}"])
        colunas_pivo.append(coluna)
        linha_pivo += 1
        if linha_pivo == n:
            break

    # Classifica sistemas singulares: incompatível ou compatível indeterminado.
    for linha in aumentada:
        if all(abs(linha[j]) <= limite for j in range(n)) and abs(linha[n]) > limite:
            raise ErroNumerico("Sistema incompatível: a eliminação produziu uma linha 0 = c, com c diferente de zero.")
    if len(colunas_pivo) < n:
        raise ErroNumerico("Sistema compatível indeterminado ou matriz singular: não existe solução única para calcular por Gauss.")

    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        soma = math.fsum(aumentada[i][j] * x[j] for j in range(i + 1, n))
        pivo = aumentada[i][i]
        if abs(pivo) <= limite:
            raise ErroNumerico("Pivô nulo durante a substituição retroativa.")
        x[i] = (aumentada[i][n] - soma) / pivo
        linhas.append([f"Substituição: x{i + 1}", f"{x[i]:.12g}"])

    residuo = _residuo_inf(matriz, x, vetor)
    resumo = "Solução única encontrada pelo método de Eliminação de Gauss.\n"
    resumo += "\n".join(f"x{i + 1} = {valor:.12g}" for i, valor in enumerate(x))
    resumo += f"\nResíduo ||Ax-b||∞ = {residuo:.3e}"
    return ResultadoMetodo(resumo, ["Foi utilizado pivoteamento parcial: em cada coluna, escolhe-se como pivô o maior elemento em módulo abaixo da diagonal."], ["Operação", "Detalhe"], linhas, True, len(colunas_pivo))


def fatoracao_lu(a: list[list[float]], b: list[float]) -> ResultadoMetodo:
    """Decomposição com pivoteamento parcial: P·A = L·U; depois Ly=Pb e Ux=y."""
    matriz, vetor = validar_sistema(a, b)
    n = len(matriz)
    u = [linha[:] for linha in matriz]
    l = [[0.0] * n for _ in range(n)]
    for i in range(n):
        l[i][i] = 1.0
    permutacao = list(range(n))
    escala = max(1.0, max(abs(v) for linha in matriz for v in linha))
    limite = 1e-12 * escala
    passos: list[str] = []

    for k in range(n):
        p = max(range(k, n), key=lambda i: abs(u[i][k]))
        if abs(u[p][k]) <= limite:
            raise ErroNumerico("A matriz é singular: não foi possível concluir a fatoração LU.")
        if p != k:
            u[k], u[p] = u[p], u[k]
            permutacao[k], permutacao[p] = permutacao[p], permutacao[k]
            # Os multiplicadores já calculados também acompanham a troca de linha.
            for j in range(k):
                l[k][j], l[p][j] = l[p][j], l[k][j]
            passos.append(f"Pivoteamento: troca das linhas {k + 1} e {p + 1}.")
        for i in range(k + 1, n):
            l[i][k] = u[i][k] / u[k][k]
            fator = l[i][k]
            for j in range(k, n):
                u[i][j] -= fator * u[k][j]
            u[i][k] = 0.0
        passos.append(f"Etapa {k + 1}: pivô U[{k + 1},{k + 1}] = {u[k][k]:.8g}.")

    pb = [vetor[indice] for indice in permutacao]
    y = [0.0] * n
    for i in range(n):
        y[i] = pb[i] - math.fsum(l[i][j] * y[j] for j in range(i))

    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        soma = math.fsum(u[i][j] * x[j] for j in range(i + 1, n))
        if abs(u[i][i]) <= limite:
            raise ErroNumerico("Pivô nulo na substituição retroativa de Ux=y.")
        x[i] = (y[i] - soma) / u[i][i]

    residuo = _residuo_inf(matriz, x, vetor)
    linhas = [[f"L{i + 1}", "[" + ", ".join(f"{v:.6g}" for v in l[i]) + "]", "[" + ", ".join(f"{v:.6g}" for v in u[i]) + "]"] for i in range(n)]
    resumo = "Solução única encontrada pela fatoração LU.\n"
    resumo += "Permutação de linhas (P·A = L·U): " + ", ".join(str(i + 1) for i in permutacao) + "\n"
    resumo += "Vetor intermediário y (resolvendo L·y = P·b):\n"
    resumo += "[" + ", ".join(f"{v:.12g}" for v in y) + "]\n"
    resumo += "Solução x (resolvendo U·x = y):\n"
    resumo += "\n".join(f"x{i + 1} = {valor:.12g}" for i, valor in enumerate(x))
    resumo += f"\nResíduo ||Ax-b||∞ = {residuo:.3e}"
    return ResultadoMetodo(resumo, passos + ["L é triangular inferior com diagonal unitária; U é triangular superior."], ["Linha", "L", "U"], linhas, True, n)


def _sassenfeld(a: list[list[float]]) -> list[float]:
    n = len(a)
    beta = [0.0] * n
    for i in range(n):
        diagonal = abs(a[i][i])
        if diagonal == 0:
            raise ErroNumerico(f"O coeficiente diagonal a[{i + 1},{i + 1}] é zero. Reordene as equações para aplicar Gauss-Seidel.")
        soma = math.fsum(abs(a[i][j]) * beta[j] for j in range(i))
        soma += math.fsum(abs(a[i][j]) for j in range(i + 1, n))
        beta[i] = soma / diagonal
    return beta


def gauss_seidel(
    a: list[list[float]], b: list[float], x0: list[float] | None = None,
    tolerancia: float = 1e-6, max_iteracoes: int = 100,
) -> ResultadoMetodo:
    """Gauss-Seidel, usando na mesma iteração os valores recém-calculados."""
    matriz, vetor = validar_sistema(a, b)
    validar_tolerancia(tolerancia)
    if not isinstance(max_iteracoes, int) or max_iteracoes < 1:
        raise ErroNumerico("O número máximo de iterações deve ser um inteiro positivo.")
    if max_iteracoes > 5000:
        raise ErroNumerico("Para evitar cálculos excessivamente longos, limite o máximo a 5.000 iterações.")
    n = len(matriz)
    x = [0.0] * n if x0 is None else list(x0)
    if len(x) != n:
        raise ErroNumerico("A aproximação inicial x(0) deve ter um valor para cada incógnita.")
    if any(not math.isfinite(v) for v in x):
        raise ErroNumerico("A aproximação inicial deve conter apenas números finitos.")
    if any(matriz[i][i] == 0 for i in range(n)):
        raise ErroNumerico("Há elemento diagonal igual a zero. Reordene as equações para aplicar Gauss-Seidel.")

    beta = _sassenfeld(matriz)
    beta_max = max(beta)
    linhas: list[list[object]] = []
    escala_b = max(1.0, _norma_inf_vetor(vetor))

    for k in range(1, max_iteracoes + 1):
        anterior = x[:]
        novo = x[:]
        for i in range(n):
            soma = math.fsum(matriz[i][j] * novo[j] for j in range(i))
            soma += math.fsum(matriz[i][j] * anterior[j] for j in range(i + 1, n))
            novo[i] = (vetor[i] - soma) / matriz[i][i]
            if not math.isfinite(novo[i]):
                raise ErroNumerico("Gauss-Seidel gerou valores não finitos; verifique a convergência do sistema.")
        erro_abs = _norma_inf_vetor([novo[i] - anterior[i] for i in range(n)])
        erro_rel = erro_abs / max(1.0, _norma_inf_vetor(novo))
        residuo = _residuo_inf(matriz, novo, vetor)
        linhas.append([k, "[" + ", ".join(f"{v:.8g}" for v in novo) + "]", erro_rel, residuo])
        x = novo
        if erro_rel <= tolerancia and residuo <= tolerancia * escala_b:
            resumo = "Solução aproximada por Gauss-Seidel:\n"
            resumo += "\n".join(f"x{i + 1} = {valor:.12g}" for i, valor in enumerate(x))
            resumo += f"\nIterações: {k}\nErro relativo máximo: {erro_rel:.3e}\nResíduo ||Ax-b||∞: {residuo:.3e}"
            resumo += f"\nCritério de Sassenfeld: β = {beta_max:.6g} ({'garantia suficiente de convergência' if beta_max < 1 else 'não garante convergência'})."
            return ResultadoMetodo(resumo, ["Gauss-Seidel utiliza imediatamente os valores recém-calculados na própria iteração.", "O critério de Sassenfeld é suficiente, não necessário: β < 1 garante convergência."], ["k", "x(k)", "erro relativo", "||Ax-b||∞"], linhas, True, k)

    residuo = _residuo_inf(matriz, x, vetor)
    resumo = "O método não atingiu a tolerância antes do limite de iterações.\n"
    resumo += "Última aproximação:\n" + "\n".join(f"x{i + 1} = {valor:.12g}" for i, valor in enumerate(x))
    resumo += f"\nβ máximo de Sassenfeld = {beta_max:.6g}; resíduo = {residuo:.3e}."
    return ResultadoMetodo(resumo, ["β < 1 garante convergência; β ≥ 1 não prova divergência, apenas deixa de oferecer essa garantia suficiente."], ["k", "x(k)", "erro relativo", "||Ax-b||∞"], linhas, False, max_iteracoes)
