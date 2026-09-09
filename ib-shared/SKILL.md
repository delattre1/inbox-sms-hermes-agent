---
name: ib-shared
description: Scripts compartilhados do inbox: busca somente leitura, envio, e o canal de mensagem.
---

# Ferramentas do inbox

Este diretorio nao e um procedimento -- e a caixa de ferramentas que os outros
sheets deste agente chamam. Nada aqui deve ser executado "porque o skill foi
carregado"; cada script tem um chamador nomeado.

## `scripts/mailbox.py`
A busca IMAP, **somente leitura** (`readonly=True`). Roda a cada 5 min sob o s6
pela copia de `/opt/plow`. Nao marca, nao move, nao apaga -- o servidor recusa.

## `scripts/send.py`
Envia UMA resposta ja aprovada. Nunca esta num cron, nunca roda sozinho. Chamado
so por `ib-reply`, so depois de um sim explicito do dono, so com o corpo que ele
leu. Sem `SMTP_PASSWORD` no ambiente ele nao envia nada.

## `scripts/notify.py`
A mensagem condicional. Chamado por `ib-triage`. O `ib-digest` NAO usa: aquele
cron roda com `--deliver` e a resposta final dele ja e a entrega.

## O caminho importa

Chame sempre por `$HERMES_HOME/skills/ib-shared/scripts/...`.

A imagem entrega os sheets em `/opt/hermes/skills`, o runtime os reconcilia
para `$HERMES_HOME/skills`, e e o segundo que um agente em execucao encontra.
Um sheet que nomeia o caminho da imagem funciona no dia do build e falha depois.

A copia root-owned em `/opt/plow/` existe para o que roda sozinho sob o
supervisor. Ela nao e sua para chamar: o que voce roda dentro de um turno vem da
casa; o que roda sem ninguem olhando vem de `/opt/plow`, e essa separacao e o
que impede uma unica edicao por prompt-injection de virar codigo agendado.
