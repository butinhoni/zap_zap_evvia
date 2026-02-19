import pandas as pd
import datetime
import sqlite3
import db_connector
from resumos import perguntar, embed

zap = sqlite3.connect("store/messages.db")


def ler_grupos():
    conn = db_connector.open_conn()
    cur = conn.cursor()
    cur.execute("select * from zap.grupos")
    colunas = ["id", "grupo", "chat_jid", "obra", "local"]
    dados = cur.fetchall()
    df = pd.DataFrame(dados, columns=colunas)
    return df


def ler_msgs(grupo_id):
    zap_cur = zap.cursor()
    zap_cur.execute(
        f"select content, timestamp, chat_jid, local_path from messages where chat_jid = '{grupo_id}'"
    )
    colunas = ["msg", "hora", "grupo", "foto"]
    dados = zap_cur.fetchall()
    df = pd.DataFrame(dados, columns=colunas)
    df["hora"] = pd.to_datetime(df["hora"])
    df["data"] = df["hora"].dt.date
    df["foto"] = df["foto"].fillna("")
    return df


def upar_resumos(resumo):
    conn = db_connector.open_conn()
    cur = conn.cursor()
    data = resumo["data"]
    obra = resumo["contrato"]
    local = resumo["local"]
    resumo = resumo["resposta"]
    ex = """
    INSERT INTO zap.resumos
    ("data", resumo, obra, "local")
    VALUES ('%s', '%s', '%s', '%s')
                """ % (data, resumo, obra, local)

    cur.execute(ex)

    conn.commit()
    cur.close()
    conn.close()


def upar_msg(msg):
    conn = db_connector.open_conn()
    cur = conn.cursor()
    data = msg["data"]
    obra = msg["local"]
    texto = msg["texto"]
    embed = msg["embed"]
    local = msg["local"]
    text = """
    INSERT INTO zap.mensagens
    ("data", obra, texto, embed, local)
    VALUES('%s','%s','%s','%s','%s')
        """ % (data, obra, texto, embed, local)

    cur.execute(text)

    conn.commit()
    cur.close()
    conn.close()


def ler_resumos():
    conn = db_connector.open_conn()
    cur = conn.cursor()
    cur.execute("select * from zap.resumos")
    dados = cur.fetchall()
    colunas = ["data", "resumo", "obra", "local"]
    df = pd.DataFrame(dados, columns=colunas)
    return df


pergunta = "me faça um resumo, como um diario de obra, de todos os acontecimentos relatados nesse dia no grupo, caso sejam citados no contexto busque separar por IC (instrumento contratual) e rodovia (MT-XXX), caso as mensagens nao incluam citacoes a IC e rodovia, nao cite nada sobre. O texto que voce mandar eu vou colocar direto pro streamlit mostrar em um site, tenha isso em mente. tambem tenha em mente que vou subir a resposta em um banco de dados, entao evite mandar coisas como ` e ' (nao use d'agua, use de agua etc.). Use apenas a data que vier na coluna DATA e ignore qualquer data no texto das mensagens"

respostas = []

grupos = ler_grupos()
for i, row in grupos.iterrows():
    msgs = ler_msgs(row["chat_jid"])
    resumos_tem = ler_resumos()
    resumos_tem = resumos_tem[resumos_tem["obra"] == row["obra"]]
    resumos_tem = resumos_tem[resumos_tem["local"] == row["local"]]

    # filtrar as fotos
    fotos = msgs[msgs["foto"] != ""]

    # filtrar as mensagens do grupo pra ver o que vai analisar
    # evitar ao maximo reanalise
    textos = msgs[msgs["msg"] != ""]
    textos = textos[textos["data"] != datetime.date.today()]
    dias = textos["data"].unique()

    for dia in dias:
        temp = textos[textos["data"] == dia]
        for _, row2 in temp.iterrows():
            msg = {
                "obra": row["obra"],
                "data": dia,
                "local": row["local"],
                "embed": embed(row2["content"]),
                "msg": row2["content"],
            }
            upar_msg(msg)
        if dia in resumos_tem["data"].unique():
            print("tem")
            continue
        context = temp.to_json()
        resposta = perguntar(context, pergunta)
        resumo = {
            "data": dia,
            "contrato": row["obra"],
            "local": row["local"],
            "resposta": resposta,
        }
        upar_resumos(resumo)

with open("file.txt", "w") as f:
    f.write(str(respostas))
