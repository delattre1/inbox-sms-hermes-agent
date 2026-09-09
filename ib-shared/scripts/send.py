#!/usr/bin/env python3
# Copyright 2026 Gabriel Ribeiro
# SPDX-License-Identifier: Apache-2.0
"""send.py -- envia UMA resposta de e-mail que o dono aprovou no chat.

Separado do mailbox.py de proposito. A busca e somente leitura e roda sozinha a
cada 5 minutos; o envio nunca roda sozinho, nunca esta num cron, e so existe
como um comando que o agente dispara depois de um sim explicito. Manter as duas
capacidades em arquivos diferentes e o que torna essa frase verificavel por quem
le o repo em vez de uma promessa no README.

Le o corpo do rascunho de --file. Responde em thread quando ha In-Reply-To.
"""
import argparse, os, smtplib, ssl, sys
from email.message import EmailMessage


def need(name, default=None):
    value = (os.environ.get(name) or "").strip() or default
    if not value:
        sys.exit(f"send: falta {name} no ambiente -- veja o .env.example do repo")
    return value


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--to", required=True)
    parser.add_argument("--subject", required=True)
    parser.add_argument("--file", required=True, help="arquivo com o corpo aprovado")
    parser.add_argument("--in-reply-to", default="", help="Message-ID do original")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    body = open(args.file, encoding="utf-8").read().strip()
    if not body:
        sys.exit("send: o rascunho esta vazio -- nao envio mensagem em branco")

    user = need("IMAP_USER")
    message = EmailMessage()
    message["From"] = os.environ.get("SMTP_FROM", "").strip() or user
    message["To"] = args.to
    message["Subject"] = args.subject
    if args.in_reply_to:
        message["In-Reply-To"] = args.in_reply_to
        message["References"] = args.in_reply_to
    message.set_content(body)

    if args.dry_run:
        print(f"dry-run: enviaria pra {args.to} | {args.subject} | {len(body)} chars")
        return 0

    host = need("SMTP_HOST", os.environ.get("IMAP_HOST", "").replace("imap.", "smtp."))
    port = int(os.environ.get("SMTP_PORT") or 587)
    password = need("SMTP_PASSWORD", os.environ.get("IMAP_PASSWORD"))
    try:
        with smtplib.SMTP(host, port, timeout=30) as server:
            server.starttls(context=ssl.create_default_context())
            server.login(user, password)
            server.send_message(message)
    except smtplib.SMTPAuthenticationError:
        sys.exit("send: o servidor SMTP recusou o login (conta com 2FA precisa de senha de app)")
    except Exception as exc:
        sys.exit(f"send: nao consegui enviar ({type(exc).__name__})")
    print(f"send: enviado pra {args.to}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
