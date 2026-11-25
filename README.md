# Laboratório de Cálculo Numérico

Aplicação desktop em Python para executar os 12 métodos exigidos no Trabalho Prático de Cálculo Numérico. A interface foi desenvolvida com **Tkinter**, que acompanha as instalações convencionais do Python para Windows, macOS e muitas distribuições Linux.

## 1. Como executar

**Requisito:** Python 3.10 ou superior, com Tkinter disponível.

1. Extraia a pasta do projeto.
2. Abra o terminal dentro da pasta `calculo_numerico_app`.
3. Execute:

```bash
python main.py
```

Não é necessário instalar bibliotecas externas. Os métodos foram implementados em Python puro, usando a biblioteca padrão.

Para executar os testes automatizados:

```bash
python -m unittest discover -s tests -v
```

## 2. Métodos implementados

| Grupo | Método | Implementação |
|---|---|---|
| Raízes | Bissecção | Mantém um intervalo com mudança de sinal e o divide ao meio. |
| Raízes | Newton-Raphson | Usa `x(k+1) = x(k) - f(x(k))/f'(x(k))`. |
| Raízes | Secante | Aproxima a derivada pelo quociente das diferenças entre duas aproximações. |
| Raízes | Falsa Posição (Regula Falsi) | Usa a interseção da secante com o eixo x, mantendo o intervalo de isolamento. |
| Sistemas | Eliminação de Gauss | Triangulariza a matriz aumentada, com pivoteamento parcial, e aplica substituição retroativa. |
| Sistemas | Fatoração LU | Decompõe com pivoteamento parcial (`P·A = L·U`), resolve `L·y = P·b` e depois `U·x = y`. |
| Sistemas | Gauss-Seidel | Atualiza cada incógnita usando imediatamente os valores mais recentes da iteração. |
| Interpolação | Lagrange | Calcula os polinômios básicos `Lᵢ(x)` e a soma `Σ yᵢLᵢ(x)`. |
| Interpolação | Newton | Monta a tabela de diferenças divididas e avalia o polinômio na forma encaixada. |
| Integração | Trapézio Repetido | Aplica a regra dos trapézios em subintervalos uniformes. |
| Integração | Simpson 1/3 Repetida | Usa os pesos 1, 4 e 2; exige quantidade par de subintervalos. |
| Integração | Caso discreto | Integra diretamente os pares `(xᵢ, f(xᵢ))`, sem exigir expressão da função. |

### Caso discreto

O usuário pode escolher entre duas quadraturas. A regra dos trapézios aceita espaçamentos irregulares e soma os trapézios entre pontos consecutivos. Simpson 1/3 exige pontos igualmente espaçados e quantidade par de segmentos. A interface verifica essas condições antes do cálculo.

## 3. Entrada de funções

A expressão da função deve usar `x` como variável e multiplicação explícita (`2*x`, não `2x`). São aceitos:

- Operadores: `+`, `-`, `*`, `/`, `^` ou `**`;
- Funções: `sin`, `sen`, `cos`, `tan`, `asin`, `acos`, `atan`, `exp`, `ln`, `log`, `log10`, `sqrt` e `abs`;
- Constantes: `pi` e `e`.

As funções trigonométricas usam ângulos em radianos. Em expressões, use ponto decimal (por exemplo, `0.5`); os campos numéricos comuns também aceitam vírgula decimal.

Exemplos:

```text
x^3 - 9*x + 3
exp(-x) - cos(x)
sin(x)^2 + cos(x)^2
ln(x) + x
```

A leitura da expressão é feita por análise sintática restrita (`ast`), sem executar `eval()` ou comandos Python arbitrários.

## 4. Entrada dos dados numéricos

- Campos numéricos aceitam ponto ou vírgula decimal (ex.: `0.25` ou `0,25`).
- Listas de valores podem ser separadas por ponto e vírgula, espaços ou quebras de linha.
- Para matrizes, use uma linha por equação e separe os coeficientes por espaço ou ponto e vírgula.
- Em interpolação e integração discreta, mantenha cada `xᵢ` alinhado com o respectivo `f(xᵢ)` na mesma posição.

## 5. Validações e critérios numéricos

- **Raízes:** validação do intervalo com mudança de sinal nos métodos que exigem isolamento; tolerância positiva; limite de iterações; detecção de derivada ou denominador próximo de zero. Newton e Secante verificam tanto o tamanho do passo quanto o resíduo da função. A continuidade da função é uma hipótese matemática dos métodos com intervalo e não pode ser provada automaticamente pela interface.
- **Sistemas:** matriz quadrada; dimensões compatíveis entre `A` e `b`; pivôs; distinção entre sistema incompatível e sistema sem solução única em Gauss; verificação do resíduo `||A·x-b||∞`.
- **Gauss-Seidel:** aproximação inicial compatível com a dimensão; diagonal não nula; erro relativo normalizado e resíduo. O programa também calcula o critério de Sassenfeld. `β < 1` é uma condição suficiente de convergência, não uma condição necessária.
- **Interpolação:** listas com o mesmo tamanho, pelo menos dois pontos e valores de `x` distintos.
- **Integração:** número positivo de subintervalos; Simpson 1/3 com número par; para dados discretos, valores de `x` crescentes e, em Simpson, espaçamento uniforme.

Os resultados são apresentados em ponto flutuante. Como discutido no Capítulo 1 da disciplina, representação finita, arredondamento e conversões numéricas podem introduzir pequenas diferenças em relação ao valor exato.

## 6. Organização do código

```text
calculo_numerico_app/
├── main.py                       # inicia a aplicação
├── README.md                     # documentação e instruções
├── calculo_numerico/
│   ├── erros.py                  # exceção e estrutura de resultado
│   ├── validacao.py              # conversão e validação de entradas
│   ├── expressoes.py             # leitura segura de f(x)
│   ├── raizes.py                 # quatro métodos de raízes
│   ├── sistemas.py               # Gauss, LU e Gauss-Seidel
│   ├── interpolacao.py           # Lagrange e Newton
│   └── integracao.py             # integração composta e caso discreto
├── interface/
│   └── app.py                    # interface Tkinter
└── tests/
    └── test_metodos.py           # testes automatizados dos métodos
```

A interface não contém as fórmulas dos métodos: ela coleta os dados, converte as entradas, chama as funções da camada `calculo_numerico` e exibe o resultado. Essa separação evita duplicação e facilita explicar, testar e manter o projeto.

## 7. Relação com os seis capítulos enviados

- **Capítulo 1 – Noções Básicas sobre Erros:** orienta a interpretação dos resultados como aproximações em aritmética de ponto flutuante, e justifica validar entradas e apresentar tolerâncias.
- **Capítulo 2 – Zeros de Funções Reais:** fundamenta os quatro métodos de raízes e a importância de localização, refinamento e critérios de parada.
- **Capítulo 3 – Resolução de Sistemas Lineares:** fundamenta eliminação de Gauss, fatoração LU, substituições e Gauss-Seidel. A implementação usa pivoteamento parcial em Gauss e uma forma pivotada da fatoração (`P·A = L·U`) para lidar com pivôs pequenos ou nulos.
- **Capítulo 4 – Interpolação:** fundamenta as formas de Lagrange e Newton, com diferenças divididas.
- **Capítulo 5 – Integração Numérica:** fundamenta trapézios e Simpson compostos. A opção de dados discretos aplica as mesmas ideias diretamente a valores tabelados, sem supor uma expressão conhecida para `f(x)`.
- **Capítulo 6 – Ajuste de Curvas por Quadrados Mínimos:** foi analisado, mas não incluído como método adicional porque não aparece na lista de métodos exigidos pelo enunciado. O “caso discreto” da entrega é o de integração com dados tabelados, não o ajuste discreto de mínimos quadrados deste capítulo.

## 8. Observação para a apresentação

Demonstre ao menos um exemplo de cada grupo. Ao explicar, destaque a diferença entre métodos diretos e iterativos, as hipóteses de cada método, as validações feitas antes do cálculo e a tabela de iterações/valores intermediários exibida pela interface.
