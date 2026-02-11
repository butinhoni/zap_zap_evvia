import pandas as pd
import subprocess
from numeros import numeros
from planilhas import os_go

df = os_go()
telefones = numeros()

df = df[["DESCRIÇÃO", "DATA\nVENCIMENTO", "STATUS"]]
df = df[df["STATUS"] != "Atendido"]
df = df[df["STATUS"] != "Cancelada"]
df.columns = ["desc", "vencimento", "status"]
df["vencimento"] = pd.to_datetime(df["vencimento"], errors="coerce")
df = df.dropna(subset="desc")
df = df.dropna(subset="vencimento")

text = "Olá equipe, segue relação das ordens de serviço em aberto no contrato GO Lote 3 \n\n"
for i, row in df.iterrows():
    desc = f"*Descrição:* {row['desc']}\n"
    venc = f"*Vencimento:* {row['vencimento']}\n"
    status = f"*Status:* {row['status']}\n"
    sep = "----------------------------- -------------------------------\n\n"
    text = text + desc + venc + status + sep
print(text)

msg = subprocess.run(
    ["./send_message.sh", "send_message", telefones["Diogo"], text],
    capture_output=True,
    text=True,
)
print(msg.stdout)
