---
name: ib-digest
description: O resumo do dia. Sempre tem conteudo, entao a resposta final e a propria entrega.
---

# O resumo do dia

Uma vez por dia. Leia a fila desde o ultimo resumo -- tudo, inclusive o que a
triagem ja avisou (mencione de passagem que ja avisou, nao esconda).

## A forma

Duas partes, sem cabecalho, sem marcador:

Primeiro o que **precisa de voce**: quem, o que quer, ate quando. Uma linha
cada, no maximo tres. Se tem mais de tres, escolha os tres e diga quantos
sobraram.

Depois o que **so aconteceu**: uma linha so, agregada. "mais 14: newsletters,
dois recibos e a fatura do cartao."

```
tres pedem resposta hoje: a Ana quer o orcamento revisado ate as 18h, o
banco pede confirmacao de um debito de R$ 240, e o Pedro perguntou se
voce vai na quinta.
mais 14 chegaram e nao pedem nada: newsletters, dois recibos, a fatura.
quer responder algum? e so dizer o que dizer.
```

Se nao chegou nada que preste, diga isso em uma linha e pare. Um resumo honesto
e curto vale mais que um inflado.

## A entrega

Este cron roda com `--deliver`, entao **a sua resposta final e a mensagem**.
Nao chame o `notify.py` aqui: isso mandaria o resumo duas vezes.

Depois marque tudo que entrou no resumo como `"state": "resumido"`.
