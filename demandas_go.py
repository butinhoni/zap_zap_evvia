import pandas as pd
import subprocess
from numeros import numeros
from planilhas import os_go

df = os_go()
telefones = numeros()

# mandar_para = ["Diogo", "Romilson"]
mandar_para = ["Engevvia-163"]

df = df[["DESCRIÇÃO", "RODOVIA", "DATA\nVENCIMENTO", "STATUS", "OBSERVAÇÕES"]]
df["RODOVIA"] = df["RODOVIA"].ffill()
df = df[df["STATUS"] != "Atendido"]
df = df[df["STATUS"] != "Cancelada"]
df.columns = ["desc", "rod", "vencimento", "status", "obs"]
df["vencimento"] = pd.to_datetime(df["vencimento"], errors="coerce")
df = df.dropna(subset="desc")
df = df.dropna(subset="vencimento")
df["obs"] = df["obs"].fillna("")

text = "Olá equipe, segue relação das ordens de serviço em aberto no contrato GO Lote 3 \n\n"
for i, row in df.iterrows():
    data_format = row["vencimento"].strftime("%d/%m/%Y")
    desc = f"*Descrição:* {row['desc']}\n"
    rod = f"*Rodovia:* {row['rod']}\n"
    venc = f"*Vencimento:* {data_format}\n"
    status = f"*Status:* {row['status']}\n"
    obs = f"*Obs:* {row['obs']}\n" if row["obs"] != "" else ""
    sep = "----------------------------- -------------------------------\n\n"
    text = text + desc + rod + venc + status + obs + sep
print(text)
for k, v in telefones.items():
    if k in mandar_para:
        msg = subprocess.run(
            ["./send_message.sh", "send_message", v, text],
            capture_output=True,
            text=True,
        )
print(msg.stdout)
