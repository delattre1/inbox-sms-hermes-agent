#!/usr/bin/env python3
# Copyright 2026 Gabriel Ribeiro
# SPDX-License-Identifier: Apache-2.0
"""mailbox.py -- busca correio novo por IMAP, SOMENTE LEITURA.

Roda sob o s6, sem modelo nenhum. Baixa o que chegou desde a ultima marca
d'agua, escreve um arquivo por mensagem na fila, e sai. Quem le e decide o que
importa e o agente, num turno separado.

Tres propriedades que existem de proposito, porque sao o que torna aceitavel
apontar isto pra caixa de entrada de um estranho:

1. `select(..., readonly=True)`. A conexao IMAP e aberta em modo somente
   leitura. Nao e uma promessa no README -- e o servidor que recusa. Nada aqui
   marca como lido, move, arquiva ou apaga, porque a sessao nao tem permissao
   pra isso.
2. Nada de senha em disco alem do `.env` que o dono escreveu. Este script le do
   ambiente e nao guarda credencial em lugar nenhum.
3. Todo texto que sai daqui vem cercado por marcadores de conteudo nao
   confiavel. Remetente, assunto e corpo sao escritos por terceiros: sao prova
   do que chegou, nunca instrucao pro agente.
"""
import email, email.utils, imaplib, json, os, re, sys, time
from email.header import decode_header, make_header

HOME = os.environ.get("HERMES_HOME", "/var/lib/hermes")
BASE = os.path.join(HOME, os.environ.get("MAILBOX_BASE", "inbox"))
QUEUE = os.path.join(BASE, "queue")
MARK = os.path.join(BASE, "watermark.json")

SNIPPET = 1500
MAX_PER_RUN = 60

OPEN = "<<<EMAIL_NAO_CONFIAVEL>>>"
CLOSE = "<<<FIM_EMAIL_NAO_CONFIAVEL>>>"
STRIP = re.compile(r"<<<\s*/?\s*(FIM_)?EMAIL_NAO_CONFIAVEL\s*>>>", re.I)


def need(name, default=None):
    value = (os.environ.get(name) or "").strip() or default
    if not value:
        sys.exit(f"mailbox: falta {name} no ambiente -- veja o .env.example do repo")
    return value


def decoded(raw):
    if not raw:
        return ""
    try:
        return str(make_header(decode_header(raw)))
    except Exception:
        return str(raw)


def body_text(message):
    """text/plain quando existe; senao o html com as tags arrancadas. Nao e um
    renderizador -- e o suficiente pra decidir se um humano precisa ver isso."""
    parts = []
    if message.is_multipart():
        for part in message.walk():
            if part.get_content_maintype() == "multipart":
                continue
            if part.get("content-disposition", "").startswith("attachment"):
                continue
            if part.get_content_type() in ("text/plain", "text/html"):
                try:
                    payload = part.get_payload(decode=True) or b""
                    text = payload.decode(part.get_content_charset() or "utf-8", "replace")
                except Exception:
                    continue
                parts.append((part.get_content_type(), text))
    else:
        try:
            payload = message.get_payload(decode=True) or b""
            parts.append((message.get_content_type(),
                          payload.decode(message.get_content_charset() or "utf-8", "replace")))
        except Exception:
            pass
    plain = next((t for kind, t in parts if kind == "text/plain"), None)
    if plain is None:
        html = next((t for kind, t in parts if kind == "text/html"), "")
        plain = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"[ \t]*\n[ \t]*", "\n", re.sub(r"[ \t]{2,}", " ", plain)).strip()


def fence(text):
    """Marcadores primeiro arrancados do proprio texto: um remetente nao fecha
    o cerco escrevendo o marcador de fechamento no corpo dele."""
    return f"{OPEN}\n{STRIP.sub('', text or '')}\n{CLOSE}"


def read_json(path, fallback):
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        return fallback
    except (OSError, ValueError):
        return fallback


def write_json(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


def connect():
    host = need("IMAP_HOST")
    port = int(os.environ.get("IMAP_PORT") or 993)
    user = need("IMAP_USER")
    password = need("IMAP_PASSWORD")
    folder = os.environ.get("IMAP_FOLDER") or "INBOX"
    client = imaplib.IMAP4_SSL(host, port)
    try:
        client.login(user, password)
    except imaplib.IMAP4.error:
        # Sem eco da senha e sem traceback: a excecao do imaplib carrega a
        # resposta do servidor, que em varios provedores ecoa o usuario.
        sys.exit("mailbox: o servidor IMAP recusou o login. Se a conta tem 2FA, "
                 "e preciso uma senha de app -- nao a senha normal da conta.")
    # readonly=True: a garantia e do servidor, nao deste arquivo.
    status, _ = client.select(folder, readonly=True)
    if status != "OK":
        sys.exit(f"mailbox: nao consegui abrir a pasta {folder!r}")
    return client


def main():
    client = connect()
    mark = read_json(MARK, {})
    last = int(mark.get("uid") or 0)
    status, data = client.uid("search", None, f"UID {last + 1}:*")
    if status != "OK":
        sys.exit("mailbox: a busca IMAP falhou")
    uids = [int(u) for u in (data[0] or b"").split() if int(u) > last]
    uids = sorted(uids)[-MAX_PER_RUN:]
    if not uids:
        print("mailbox: nada novo")
        client.logout()
        return 0

    os.makedirs(QUEUE, exist_ok=True)
    written = 0
    for uid in uids:
        status, payload = client.uid("fetch", str(uid), "(RFC822)")
        if status != "OK" or not payload or not isinstance(payload[0], tuple):
            continue
        message = email.message_from_bytes(payload[0][1])
        sender = decoded(message.get("From"))
        subject = decoded(message.get("Subject"))
        body = body_text(message)
        record = {
            "uid": uid,
            "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "date": decoded(message.get("Date")),
            "from": sender,
            "from_addr": email.utils.parseaddr(message.get("From") or "")[1].lower(),
            "to": decoded(message.get("To")),
            "message_id": (message.get("Message-ID") or "").strip(),
            "list_unsubscribe": decoded(message.get("List-Unsubscribe")),
            "has_attachments": any(
                (p.get("content-disposition") or "").startswith("attachment")
                for p in (message.walk() if message.is_multipart() else [])),
            # Tudo que um terceiro escreveu, cercado junto: um assunto e tao
            # escrito pelo remetente quanto um paragrafo.
            "untrusted": fence(f"De: {sender}\nAssunto: {subject}\n\n{body[:SNIPPET]}"),
            "state": "novo",
        }
        write_json(os.path.join(QUEUE, f"{uid:09d}.json"), record)
        written += 1

    write_json(MARK, {"uid": max(uids), "at": time.strftime("%Y-%m-%dT%H:%M:%S%z")})
    client.logout()
    print(f"mailbox: {written} mensagens novas na fila")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
