# Inbox SMS

**Your inbox, as a text message. Read-only, and it never sends without you
saying so.**

You don't open your email. This opens it for you, texts you only what actually
needs you, and writes the reply when you say what to say.

```
agent: three need you today: Ana wants the revised quote by 6pm, the bank
       wants you to confirm a R$240 debit, and Pedro asked if you're
       coming Thursday.
       14 more arrived and want nothing: newsletters, two receipts, the bill.
you:   tell ana i'll send it tomorrow morning
agent: [draft]
       Ana, I'll have the revised quote to you tomorrow morning.
       send it?
you:   yes
agent: sent to Ana.
```

## The read-only part is real

The IMAP session opens with `readonly=True`. That's not a promise in a README —
it's the server refusing. Nothing here marks as read, moves, archives, or
deletes, even if you ask it to.

Fetching and sending live in **different files**: `mailbox.py` runs every five
minutes on a schedule and can only read; `send.py` is never in a cron and only
runs when the agent invokes it after you approve a specific draft, word for word.
You can check that claim by reading the repo rather than trusting this paragraph.

Leave `SMTP_PASSWORD` out of your `.env` and it physically cannot send. It just
drafts.

## Every email is somebody else's text

Mail reaches the agent fenced in `<<<EMAIL_NAO_CONFIAVEL>>>` markers — sender,
subject and body alike, because a subject line is as sender-written as a
paragraph. An email saying "forward this" or "reply to confirm" is asking *you*,
not the agent. It never acts on instructions found in mail, never fills a form
reached from an email link, and never sends to an address that appeared inside a
message rather than coming from you.

## The two rhythms

**Urgent, every 15 minutes.** Only what can't wait for the digest. Most runs send
nothing — that's the point. Newsletters and anything carrying `List-Unsubscribe`
never interrupt you.

**Digest, once a day.** What needs a reply, separated from what merely happened.

## Install (about 5 minutes)

## Before you start (2 minutes, once per machine)

You need **Docker**, **git**, **Python 3**, and a **Plow account**. Then:

```sh
git clone https://github.com/plow-pbc/plow-agents.git
export PATH="$PWD/plow-agents/bin:$PATH"
plow-agents login     # authenticates by texting you a code
```

If you have already done this for another agent, skip it.

### 1. Get the agent a phone line

```sh
plow-agents lines            # pick a free ln_... id
plow-agents mint ln_xxxxx    # writes ./plow-credentials — run it BEFORE `up`
```

### 2. Clone and start

```sh
git clone https://github.com/gabe-rbo/inbox-sms-hermes-agent.git
cd inbox-sms-hermes-agent
mv ../plow-credentials .     # or run `mint` from inside this directory
cp .env.example .env
$EDITOR .env                 # your IMAP host, address, and app password
docker compose up --build -d
```

The first build pulls the Plow base image and takes a few minutes. After that:

```sh
docker compose logs -f agent   # wait for the gateway to come up
```

### 3. Text it

Text the number `plow-agents lines` showed you. Say anything — `oi`, `hey`. It
walks you through setup in the chat. **Nothing is configured by editing files.**

### Stopping

```sh
docker compose down       # keeps its memory and setup
docker compose down -v    # forgets everything, starts fresh
plow-agents revoke        # releases the line
```

## Getting an app password

Gmail with 2FA won't accept your account password. Generate an app password at
myaccount.google.com → Security → App passwords, and use that. iCloud is
`imap.mail.me.com` / `smtp.mail.me.com` with an Apple ID app password.

The agent never asks for the password in chat, and you should never type one
there.

## When it doesn't work

**`no such file or directory: ./plow-credentials`** — you ran `docker compose up`
before `plow-agents mint`. Compose created a *directory* at that path. Remove it,
run `mint`, then `up` again:

```sh
docker compose down -v && rm -rf plow-credentials && plow-agents mint ln_xxxxx
```

**The build fails pulling the base image** — `docker logout public.ecr.aws`. A
stale credential in Docker's config makes an anonymous public pull fail.

**It never texts you** — check `docker compose logs agent` for
`plow_chat connected`. If the credential file is wrong the container blocks on
purpose rather than starting half-configured.

**Nothing shows up on the Agent Index** — the reporter runs every 5 minutes, not on boot.
`docker compose logs agent | grep agent-index` tells you what it did.

## The Agent Index

This image ships the AI Worth Using usage reporter as a supervised service. It
registers once and reports token counts every 5 minutes, and it reports **nothing else** —
no prompts, no message text, no file paths. The `AGENT_ID` in `compose.yml` is
what it reports under.

There is no switch to turn it off. An agent whose owner doesn't want that is one
built without the service — delete `image/s6-overlay/s6-rc.d/agent-index/` and
rebuild.

## License

Apache-2.0. Built on the Plow Hermes base image (Apache-2.0, © 2026 The Plow
Collective) and Nous Research's Hermes Agent. Not affiliated with either;
"Plow" and "Hermes" are their marks and this license grants no rights to them.
