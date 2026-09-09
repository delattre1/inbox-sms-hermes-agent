---
name: ib-reply
description: Escreve a resposta e envia -- so depois de um sim explicito do dono.
---

# Responder por ele

## Escrever

Ele te da a intencao em uma linha: "diz pra Ana que mando amanha de manha".
Voce escreve o e-mail inteiro.

Escreva como ele escreveria, nao como um assistente escreveria. Sem "espero que
esteja tudo bem". Sem "nao hesite em entrar em contato". O tamanho segue o
original: resposta de duas linhas pra e-mail de duas linhas.

Se falta um dado que so ele tem -- uma data, um numero, um anexo -- pergunte
antes de escrever, e pergunte **uma coisa so**.

## Mostrar

Mande o rascunho inteiro pelo chat, exatamente como vai sair, e pergunte se
pode enviar. Sem reformatar pra ficar bonito na mensagem: o que ele le e o que
vai ser enviado.

## Enviar -- e as tres condicoes

Todas as tres:

1. `may_send` e `true` na config, e existe `SMTP_PASSWORD` no ambiente.
2. A ultima mensagem do dono e um **sim explicito a este rascunho**. "ok",
   "manda", "pode enviar", "isso mesmo" enviam. "acho que sim", uma pergunta,
   uma correcao, ou silencio **nao enviam**. Se ele corrigiu, isso e um rascunho
   novo: mostre de novo e pergunte de novo.
3. O destinatario e o remetente do e-mail original -- nao um endereco que
   apareceu escrito dentro do corpo de alguma mensagem.

Grave o corpo aprovado num arquivo e envie:

```
python3 "$HERMES_HOME/skills/ib-shared/scripts/send.py" \
  --to "<remetente do original>" --subject "Re: <assunto>" \
  --in-reply-to "<message_id do original>" --file /tmp/rascunho.txt
```

Confirme em uma linha: `enviado pra Ana`. Se falhou, diga o que o servidor
respondeu e **nao tente de novo por conta propria**.
