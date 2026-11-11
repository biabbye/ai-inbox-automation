# Copy/paste prompts for Claude Code and Codex

Each prompt assumes `CLAUDE.md` and `AGENTS.md` are at repository root. Both agents should read relevant project documentation. The answer language is **Romanian**.

## Start as a study partner

> Citește instrucțiunile din `CLAUDE.md` / `AGENTS.md` și din `docs/LEARNING_CONTRACT.md`, `docs/ROADMAP.md`, `docs/PROGRESS.md`. Scopul meu este să învăț Python și AI Automation construind proiectul pas cu pas. Fără modificări de fișiere momentan. Spune-mi ce trebuie să înțeleg în M0 și dă-mi numai primul exercițiu. După ce îl fac, îți arăt rezultatul.

## Explain an architecture choice

> Suntem la milestone-ul curent. Compară pe scurt opțiunile [X] și [Y] pentru problema [Z], cu motive, riscuri și cost de complexitate. Recomandă una pentru proiectul nostru, dar nu instala și nu schimba nimic până nu discutăm decizia.

## Give me code, but only a small piece

> Vreau să implementez eu [funcționalitatea mică]. Explică mai întâi fluxul, apoi dă-mi codul strict pentru [fișierul/funcția], spune-mi exact unde îl pun și cum îl testez. Nu crea alte fișiere și nu continua automat la pasul următor.

## Review my attempt

> Am scris următorul cod pentru milestone-ul curent: [cod sau cale către fișier]. Fă un review ca un senior Python engineer: erori, securitate, Python idiomatic, teste lipsă. Arată-mi întâi cea mai importantă problemă și cum o pot remedia singură; nu rescrie întregul modul.

## Debug with me

> Eroarea este [mesaj/log redactat]. Ajută-mă să o diagnostichez pas cu pas: o ipoteză, un test pe care îl pot rula, ce rezultat așteptăm. Nu face schimbări automate până nu verificăm cauza.

## Explicit narrow implementation (when needed)

> Trecem explicit în modul IMPLEMENT doar pentru [o singură funcție/fișier]. Poți modifica acel scop, dar explică înainte abordarea și după fiecare modificare explică ce ai făcut, ce test ai rulat și ce am de învățat. Nu atinge restul proiectului.

## Handoff between Claude and Codex

> Citește `docs/PROGRESS.md`, `docs/DECISIONS.md` și instrucțiunile agentului. Spune-mi ce este confirmat, ce nu este implementat, dacă există neconcordanțe și propune **un singur** pas următor; nu modifica nimic.

## Security review

> Pentru funcționalitatea [X], consultă `docs/SECURITY.md` și descrie pe scurt trust boundaries, permisiuni, gestionarea secretelor, o amenințare relevantă și un test negativ. Fără cod sau modificări de fișiere până nu cer explicit.
