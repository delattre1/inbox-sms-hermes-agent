---
name: ib-setup
description: Primeira conversa. Descobre o que conta como urgente, a hora do resumo, e se pode enviar.
---

# Colocar a caixa de entrada de pe

O IMAP ja esta configurado -- ele foi escrito no `.env` antes do container
subir, e se voce esta lendo isso a busca ja esta rodando. Nao pergunte senha,
servidor nem porta. **Nunca peca uma senha pelo chat.**

Se `$HERMES_HOME/inbox/config.json` ja existe, isto e um ajuste, nao uma
primeira conversa: mostre o que esta valendo em duas linhas e mude so o que ele
pedir.

## O que perguntar, nesta ordem

1. **O que nao pode esperar.** Pergunte de um jeito concreto: "o que precisa te
   acordar?" Respostas uteis sao pessoas ("qualquer coisa do meu orientador"),
   assuntos ("cobranca, boleto, prazo") ou dominios. Se ele nao souber, proponha
   um padrao razoavel e siga -- da pra ajustar depois de ver o primeiro dia.
2. **Que horas voce manda o resumo.** Um horario. O padrao e 08:00.
3. **Se voce pode enviar resposta.** Explique a regra antes: voce escreve, ele
   le, e so vai com um sim explicito. Se ele preferir que voce nunca envie, tudo
   bem -- voce vira um agente que so rascunha, e o `.env` sem `SMTP_PASSWORD` ja
   garante isso sozinho.

Nao pergunte mais nada.

## Escrever a configuracao

```json
{
  "urgent": {
    "from": ["orientador@ufmg.br"],
    "subject_terms": ["cobranca", "boleto", "prazo", "vencimento"],
    "domains": ["banco.com.br"]
  },
  "digest_hour": 8,
  "may_send": true,
  "quiet_hours": [23, 7]
}
```

Em `$HERMES_HOME/inbox/config.json`.

## Registrar os dois crons

```
hermes cron create "*/15 * * * *" \
  "Rode o ib-triage agora: se houver e-mail urgente nao avisado, avise. Se nao houver, responda exatamente quiet." \
  --name ib-triage --skill ib-triage

hermes cron create "0 8 * * *" \
  "Rode o ib-digest agora: resuma o que chegou desde o ultimo resumo e devolva o texto do resumo como resposta final." \
  --name ib-digest --skill ib-digest --deliver "plow_chat:${PLOW_HOME_CHANNEL}"
```

Os dois bracos sao diferentes de proposito. A triagem fica quieta quase sempre,
e `--deliver` repassa TODA resposta final -- inclusive as silenciosas -- entao
ela manda pelo `notify.py` so quando ha o que dizer. O resumo sempre tem
conteudo, entao a resposta final dele **e** a entrega e `--deliver` serve.

Troque `0 8` pela hora que ele escolheu. `hermes cron list` antes: se ja
existem, nao crie de novo.

## Fechar

Duas linhas: o que voce vai considerar urgente, que horas vem o resumo, e que
voce le sem marcar nada como lido. Diga que ele pode ajustar a qualquer momento
so falando. Nao mande resumo de teste.

## Se a busca nao tem credencial

O container sobe mesmo sem `.env` -- de proposito, pra que a falta vire uma
frase sua e nao um erro do Docker sobre um arquivo. Se `$HERMES_HOME/inbox/queue/` esta
vazio e o log do servico diz `falta IMAP_HOST no ambiente`, e isso que
aconteceu.

Diga em uma linha, sem jargao, e **nao peca a senha pelo chat**:

> ainda nao consigo alcancar sua caixa: falta o arquivo `.env` na pasta do
> agente. copia o `.env.example` pra `.env`, poe seu endereco e uma senha de
> app, e roda `docker compose up -d` de novo. eu aviso quando o primeiro
> correio chegar.

Nao tente configurar nada por conta propria e nao siga com o resto do setup: sem
correio, tudo que voce perguntar depois e hipotetico.
