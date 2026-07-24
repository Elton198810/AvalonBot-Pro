import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


NOME_APP = "AvalonBot Pro"
VERSAO = "1.0"


def limitar(valor, minimo, maximo):
    return max(minimo, min(valor, maximo))


def converter_numero(texto, nome):
    try:
        return float(texto.replace(",", "."))
    except ValueError:
        raise ValueError(f"Digite um valor válido no campo {nome}.")


def analisar_operacao():
    try:
        ativo = entrada_ativo.get().strip().upper()
        timeframe = combo_timeframe.get()
        tendencia = combo_tendencia.get()
        candle = combo_candle.get()
        regiao = combo_regiao.get()
        volatilidade = combo_volatilidade.get()

        rsi = converter_numero(entrada_rsi.get(), "RSI")
        ema_rapida = converter_numero(entrada_ema9.get(), "EMA 9")
        ema_lenta = converter_numero(entrada_ema21.get(), "EMA 21")
        macd = converter_numero(entrada_macd.get(), "MACD")

        if not ativo:
            raise ValueError("Digite o nome do ativo.")

        if not 0 <= rsi <= 100:
            raise ValueError("O RSI deve estar entre 0 e 100.")

        pontos_call = 0
        pontos_put = 0
        motivos_call = []
        motivos_put = []
        alertas = []

        # 1. Tendência principal
        if tendencia == "Alta":
            pontos_call += 25
            motivos_call.append("tendência principal de alta")
        elif tendencia == "Baixa":
            pontos_put += 25
            motivos_put.append("tendência principal de baixa")
        else:
            alertas.append("mercado lateral")

        # 2. Cruzamento das médias
        if ema_rapida > ema_lenta:
            pontos_call += 20
            motivos_call.append("EMA 9 acima da EMA 21")
        elif ema_rapida < ema_lenta:
            pontos_put += 20
            motivos_put.append("EMA 9 abaixo da EMA 21")
        else:
            alertas.append("médias móveis empatadas")

        # 3. MACD
        if macd > 0:
            pontos_call += 15
            motivos_call.append("MACD positivo")
        elif macd < 0:
            pontos_put += 15
            motivos_put.append("MACD negativo")
        else:
            alertas.append("MACD neutro")

        # 4. RSI
        if 52 <= rsi <= 68:
            pontos_call += 15
            motivos_call.append("RSI favorecendo continuação de alta")
        elif 32 <= rsi <= 48:
            pontos_put += 15
            motivos_put.append("RSI favorecendo continuação de baixa")
        elif rsi >= 75:
            pontos_put += 8
            alertas.append("ativo muito sobrecomprado")
        elif rsi <= 25:
            pontos_call += 8
            alertas.append("ativo muito sobrevendido")
        else:
            alertas.append("RSI sem direção forte")

        # 5. Confirmação do candle
        if candle == "Alta forte":
            pontos_call += 15
            motivos_call.append("candle forte de alta")
        elif candle == "Baixa forte":
            pontos_put += 15
            motivos_put.append("candle forte de baixa")
        elif candle == "Doji/Indecisão":
            pontos_call -= 5
            pontos_put -= 5
            alertas.append("candle de indecisão")

        # 6. Região do preço
        if regiao == "Suporte":
            pontos_call += 10
            motivos_call.append("preço próximo ao suporte")
        elif regiao == "Resistência":
            pontos_put += 10
            motivos_put.append("preço próximo à resistência")
        else:
            alertas.append("preço fora de suporte ou resistência")

        # 7. Volatilidade
        if volatilidade == "Muito alta":
            pontos_call -= 10
            pontos_put -= 10
            alertas.append("volatilidade muito alta")
        elif volatilidade == "Baixa":
            pontos_call -= 5
            pontos_put -= 5
            alertas.append("mercado com pouca movimentação")
        elif volatilidade == "Normal":
            pontos_call += 5
            pontos_put += 5

        # Ajuste por timeframe
        ajustes_timeframe = {
            "M1": -12,
            "M5": -5,
            "M15": 5,
            "M30": 7,
            "H1": 10,
        }

        ajuste = ajustes_timeframe.get(timeframe, 0)
        pontos_call += ajuste
        pontos_put += ajuste

        pontos_call = limitar(pontos_call, 0, 95)
        pontos_put = limitar(pontos_put, 0, 95)

        diferenca = abs(pontos_call - pontos_put)
        melhor_pontuacao = max(pontos_call, pontos_put)

        if melhor_pontuacao < 60 or diferenca < 15:
            sinal = "AGUARDAR"
            confianca = melhor_pontuacao
            motivos = ["indicadores sem concordância suficiente"]
        elif pontos_call > pontos_put:
            sinal = "CALL"
            confianca = pontos_call
            motivos = motivos_call
        else:
            sinal = "PUT"
            confianca = pontos_put
            motivos = motivos_put

        if confianca >= 90:
            classificacao = "MUITO FORTE"
        elif confianca >= 80:
            classificacao = "FORTE"
        elif confianca >= 70:
            classificacao = "MODERADA"
        elif confianca >= 60:
            classificacao = "FRACA"
        else:
            classificacao = "SEM ENTRADA"

        horario = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")

        texto_motivos = "\n".join(f"• {item}" for item in motivos)
        texto_alertas = (
            "\n".join(f"• {item}" for item in alertas)
            if alertas
            else "• Nenhum alerta adicional"
        )

        resultado = (
            f"{NOME_APP} — Análise manual\n"
            f"{'=' * 42}\n\n"
            f"Ativo: {ativo}\n"
            f"Timeframe: {timeframe}\n"
            f"Horário: {horario}\n\n"
            f"SINAL: {sinal}\n"
            f"CONFIANÇA TÉCNICA: {confianca:.0f}%\n"
            f"CLASSIFICAÇÃO: {classificacao}\n\n"
            f"Pontuação CALL: {pontos_call:.0f}\n"
            f"Pontuação PUT: {pontos_put:.0f}\n\n"
            f"Motivos principais:\n{texto_motivos}\n\n"
            f"Alertas:\n{texto_alertas}\n\n"
            f"AVISO:\n"
            f"A pontuação não representa garantia de lucro.\n"
            f"Use primeiro em conta demonstrativa."
        )

        caixa_resultado.config(state="normal")
        caixa_resultado.delete("1.0", tk.END)
        caixa_resultado.insert(tk.END, resultado)
        caixa_resultado.config(state="disabled")

        if sinal == "CALL":
            label_sinal.config(text="CALL ▲", foreground="#16a34a")
        elif sinal == "PUT":
            label_sinal.config(text="PUT ▼", foreground="#dc2626")
        else:
            label_sinal.config(text="AGUARDAR", foreground="#d97706")

        label_confianca.config(text=f"Confiança técnica: {confianca:.0f}%")

    except ValueError as erro:
        messagebox.showerror("Dados incorretos", str(erro))
    except Exception as erro:
        messagebox.showerror(
            "Erro inesperado",
            f"Ocorreu um erro durante a análise:\n{erro}",
        )


def limpar_campos():
    entrada_ativo.delete(0, tk.END)
    entrada_ativo.insert(0, "EUR/USD")

    combo_timeframe.set("M15")
    combo_tendencia.set("Lateral")
    combo_candle.set("Doji/Indecisão")
    combo_regiao.set("Nenhuma")
    combo_volatilidade.set("Normal")

    entrada_rsi.delete(0, tk.END)
    entrada_rsi.insert(0, "50")

    entrada_ema9.delete(0, tk.END)
    entrada_ema9.insert(0, "1.0000")

    entrada_ema21.delete(0, tk.END)
    entrada_ema21.insert(0, "1.0000")

    entrada_macd.delete(0, tk.END)
    entrada_macd.insert(0, "0")

    label_sinal.config(text="AGUARDAR", foreground="#d97706")
    label_confianca.config(text="Confiança técnica: 0%")

    caixa_resultado.config(state="normal")
    caixa_resultado.delete("1.0", tk.END)
    caixa_resultado.insert(
        tk.END,
        "Preencha os dados do gráfico e clique em ANALISAR OPERAÇÃO.",
    )
    caixa_resultado.config(state="disabled")


janela = tk.Tk()
janela.title(f"{NOME_APP} v{VERSAO}")
janela.geometry("880x720")
janela.minsize(820, 650)

estilo = ttk.Style()
estilo.configure("Titulo.TLabel", font=("Arial", 20, "bold"))
estilo.configure("Subtitulo.TLabel", font=("Arial", 11))
estilo.configure("Sinal.TLabel", font=("Arial", 25, "bold"))
estilo.configure("Confianca.TLabel", font=("Arial", 15, "bold"))
estilo.configure("Botao.TButton", font=("Arial", 11, "bold"), padding=10)

container = ttk.Frame(janela, padding=20)
container.pack(fill="both", expand=True)

ttk.Label(
    container,
    text="AVALONBOT PRO",
    style="Titulo.TLabel",
).pack()

ttk.Label(
    container,
    text="Analisador educacional de confluência técnica",
    style="Subtitulo.TLabel",
).pack(pady=(0, 15))

aviso = ttk.Label(
    container,
    text=(
        "Nenhum sinal é garantido. Use conta demonstrativa e nunca arrisque "
        "dinheiro necessário para suas despesas."
    ),
    wraplength=780,
    justify="center",
)
aviso.pack(pady=(0, 15))

area_principal = ttk.Frame(container)
area_principal.pack(fill="both", expand=True)

painel_campos = ttk.LabelFrame(
    area_principal,
    text="Dados observados no gráfico",
    padding=15,
)
painel_campos.pack(side="left", fill="both", expand=True, padx=(0, 10))

painel_resultado = ttk.LabelFrame(
    area_principal,
    text="Resultado da análise",
    padding=15,
)
painel_resultado.pack(side="right", fill="both", expand=True, padx=(10, 0))

campos = ttk.Frame(painel_campos)
campos.pack(fill="x")

ttk.Label(campos, text="Ativo:").grid(row=0, column=0, sticky="w", pady=6)
entrada_ativo = ttk.Entry(campos, width=24)
entrada_ativo.grid(row=0, column=1, sticky="ew", pady=6)

ttk.Label(campos, text="Timeframe:").grid(row=1, column=0, sticky="w", pady=6)
combo_timeframe = ttk.Combobox(
    campos,
    values=["M1", "M5", "M15", "M30", "H1"],
    state="readonly",
)
combo_timeframe.grid(row=1, column=1, sticky="ew", pady=6)

ttk.Label(campos, text="Tendência:").grid(row=2, column=0, sticky="w", pady=6)
combo_tendencia = ttk.Combobox(
    campos,
    values=["Alta", "Baixa", "Lateral"],
    state="readonly",
)
combo_tendencia.grid(row=2, column=1, sticky="ew", pady=6)

ttk.Label(campos, text="RSI:").grid(row=3, column=0, sticky="w", pady=6)
entrada_rsi = ttk.Entry(campos)
entrada_rsi.grid(row=3, column=1, sticky="ew", pady=6)

ttk.Label(campos, text="EMA 9:").grid(row=4, column=0, sticky="w", pady=6)
entrada_ema9 = ttk.Entry(campos)
entrada_ema9.grid(row=4, column=1, sticky="ew", pady=6)

ttk.Label(campos, text="EMA 21:").grid(row=5, column=0, sticky="w", pady=6)
entrada_ema21 = ttk.Entry(campos)
entrada_ema21.grid(row=5, column=1, sticky="ew", pady=6)

ttk.Label(campos, text="MACD:").grid(row=6, column=0, sticky="w", pady=6)
entrada_macd = ttk.Entry(campos)
entrada_macd.grid(row=6, column=1, sticky="ew", pady=6)

ttk.Label(campos, text="Último candle:").grid(
    row=7,
    column=0,
    sticky="w",
    pady=6,
)
combo_candle = ttk.Combobox(
    campos,
    values=["Alta forte", "Baixa forte", "Doji/Indecisão"],
    state="readonly",
)
combo_candle.grid(row=7, column=1, sticky="ew", pady=6)

ttk.Label(campos, text="Região:").grid(row=8, column=0, sticky="w", pady=6)
combo_regiao = ttk.Combobox(
    campos,
    values=["Suporte", "Resistência", "Nenhuma"],
    state="readonly",
)
combo_regiao.grid(row=8, column=1, sticky="ew", pady=6)

ttk.Label(campos, text="Volatilidade:").grid(
    row=9,
    column=0,
    sticky="w",
    pady=6,
)
combo_volatilidade = ttk.Combobox(
    campos,
    values=["Baixa", "Normal", "Muito alta"],
    state="readonly",
)
combo_volatilidade.grid(row=9, column=1, sticky="ew", pady=6)

campos.columnconfigure(1, weight=1)

ttk.Button(
    painel_campos,
    text="ANALISAR OPERAÇÃO",
    command=analisar_operacao,
    style="Botao.TButton",
).pack(fill="x", pady=(18, 8))

ttk.Button(
    painel_campos,
    text="Limpar",
    command=limpar_campos,
).pack(fill="x")

label_sinal = ttk.Label(
    painel_resultado,
    text="AGUARDAR",
    style="Sinal.TLabel",
    foreground="#d97706",
)
label_sinal.pack(pady=(5, 3))

label_confianca = ttk.Label(
    painel_resultado,
    text="Confiança técnica: 0%",
    style="Confianca.TLabel",
)
label_confianca.pack(pady=(0, 12))

caixa_resultado = tk.Text(
    painel_resultado,
    width=43,
    height=27,
    wrap="word",
    font=("Consolas", 10),
)
caixa_resultado.pack(fill="both", expand=True)
caixa_resultado.config(state="disabled")

limpar_campos()

janela.mainloop()
