import sqlite3
import pandas as pd
from openai import OpenAI
import os
import base64

conn = sqlite3.connect("bd_temp/messages.db")
conn2 = sqlite3.connect("messages2.db")

cur = conn.cursor()
cur2 = conn2.cursor()

cur2.execute("select * from imagens_descricoes")
info = cur2.fetchall()


cur.execute(
    "select content, timestamp, chat_jid from messages where chat_jid = '120363419261012009@g.us' and content is not null"
)
itens = cur.fetchall()

cur.execute("PRAGMA table_info(messages)")
colunas = cur.fetchall()
lista_colunas = [x[1] for x in colunas]


client = OpenAI()


def perguntar(contexto, pergunta):
    prompt = f"""
    use as informacoes como contexto:

            {contexto}

            pergunta: {pergunta}
    """
    resposta = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return resposta.choices[0].message.content


def gerar_descricao(caminho):
    with open(caminho, "rb") as img_file:
        img_base64 = base64.b64encode(img_file.read()).decode("utf-8")

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Descreva tecnicamente esta imagem considerando "
                                "que se trata de uma obra de infraestrutura rodoviária. "
                                "Se possível, mencione problemas visíveis, "
                                "condições do solo, equipamentos e possíveis não conformidades."
                            ),
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{img_base64}"
                            },
                        },
                    ],
                }
            ],
            temperature=0.5,
        )
        return response.choices[0].message.content


def processar_imagens():
    cur.execute("""
SELECT id, local_path, timestamp
FROM messages
where local_path is not null and chat_jid = '120363419261012009@g.us'
                """)

    fotos = cur.fetchall()

    for id_msg, caminho, data in fotos:
        if not os.path.exists(caminho):
            print(f"nao existe {caminho}")
            continue
        nome = os.path.basename(caminho)
        print(f"processando {nome}")
        try:
            descricao = gerar_descricao(caminho)
            cur2.execute(
                """
            INSERT INTO imagens_descricoes (nome, data, descricao)
            VALUES (?, ?, ?)
                         """,
                (nome, data, descricao),
            )

            conn2.commit()
            print(descricao)
        except Exception:
            print("erro")
        print("concluido")
