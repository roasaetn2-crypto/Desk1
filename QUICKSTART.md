# Solana Desk — 5 minute start (no laptop, no compiling)

You need: an Android phone with Chrome. That's it.

---

## Step 1 — Make a GitHub account (skip if you have one)

1. Open **https://github.com/signup** in Chrome.
2. Email, password, username. Verify the email.

---

## Step 2 — Make one empty repository

1. Open **https://github.com/new**
2. **Repository name:** `solana-desk`
3. Tick **Private**.
4. Tick **Add a README file**.
5. Tap **Create repository**.

---

## Step 3 — Open a Codespace (a free Linux computer in your browser)

1. On the repo page tap the green **Code** button → **Codespaces** tab → **Create codespace on main**.
2. Wait ~40 seconds. A VS Code editor opens, with a terminal at the bottom.
   If you don't see a terminal: menu ☰ → **Terminal** → **New Terminal**.

---

## Step 4 — Paste these 6 lines into that terminal

```bash
curl -L -o desk.zip https://sites.super.myninja.ai/f2e7900e-d662-4d00-9140-33301a7a3115/f9be4396/solana-desk-start.zip
unzip -o desk.zip
cp -r solana-desk/* . 2>/dev/null || cp -r solana-desk/. .
pip install -q -r requirements.txt
export DESK_TOKEN=MyDeskKey123
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

The last line prints `Uvicorn running on http://0.0.0.0:8000`.

> `pip install` here takes about 40 seconds because Codespaces is a normal
> x86 Linux machine. There is **no Rust compile** — that was only ever a
> Termux/Android problem.

---

## Step 5 — Make the port public

1. In the Codespace, open the **Ports** tab (next to Terminal).
2. Find port **8000**, right-click (long-press) → **Port Visibility** → **Public**.
3. Tap the globe 🌐 icon next to the port. A URL like
   `https://something-8000.app.github.dev` opens.

That URL is your desk. It works on any phone, anywhere.

Log in with the key you chose in Step 4 (`MyDeskKey123`), then tap
**Pair this device** so the phone stays logged in.

---

## Step 6 — Start the trading loop

On the desk, tap **Start**. The agent scans GeckoTerminal every 45 seconds.

---

## Making it permanent (optional)

A Codespace stops after ~30 minutes idle. To get a desk that never stops:

1. The code is already in your `solana-desk` repo (Step 4 copied it in —
   run `git add -A && git commit -m "desk" && git push` first).
2. Open **https://render.com** → sign up with GitHub → **New +** → **Blueprint**
   → pick `solana-desk` → it reads `render.yaml` automatically.
3. It asks for `DESK_TOKEN` — type the same key.
4. **Apply**. First build ~3 minutes. You get `https://solana-desk-xxxx.onrender.com`.

Free Render sleeps after 15 minutes with no visitors; the first visit after
that takes ~30 seconds to wake. No card needed.

---

## What NOT to do

Do **not** retry Termux. On Android, `pip install` has to compile
`pydantic-core` from Rust source. It needs more RAM than the phone will give
it and Android kills it with `Killed`. That is a hardware limit, not a mistake
you made. Codespaces and Render both run on normal x86 servers where a
prebuilt wheel exists, so nothing compiles.

---

## Safety

- The desk is **paper trading** by default. No real money, no wallet, no keys.
- Never put a real private key in this project. If you have
  `private_key.txt` / `keys.txt` files on your phone, delete them.
- `DESK_TOKEN` is the only password. Pick something long.
