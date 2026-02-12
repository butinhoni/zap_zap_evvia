from planilhas import os_mt
from numeros import numeros
import subprocess

df = os_mt()
telefones = numeros()

mandar_para = ["Kassia", "Diogo", "Romilson"]

df = df[df["STATUS DE ENTREGA"] != "CONCLUÍDA ✅"]
df = df[["DATA PRAZO", "ASSUNTO", "STATUS DE ENTREGA"]]
df.columns = ["data_prazo", "assunto", "status"]
df["data_prazo"] = df["data_prazo"].fillna("*NÃO PREENCHIDA*")

text = "Olá --fulano--, aqui está um resumo das ordens de serviço em aberto no contrato *Supervisão-MT* \n \n"

for i, row in df.iterrows():
    try:
        data = row["data_prazo"].strftime("%d/%m/%Y")
    except AttributeError:
        data = row["data_prazo"]
    prazo = f"*Prazo:* {data} \n"
    desc = f"*Descrição:* {row['assunto']} \n"
    status = f"*Status:* {row['status']} \n"
    sep = "--------------------------------- --------------------------------\n\n"
    text = text + desc + prazo + status + sep

for k, v in telefones.items():
    if k in mandar_para:
        final_text = text.replace("--fulano--", k)
        print(final_text)
        msg = subprocess.run(
            ["./send_message.sh", "send_message", v, final_text],
            capture_output=True,
            text=True,
        )
        print(msg.stdout)
