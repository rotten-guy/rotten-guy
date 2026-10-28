<div align="center">

<a href="https://rotten-guy.github.io"><img src="assets/banner.svg" alt="Joshua Gillet · rotten_guy · networks & telecoms student, Arch + Hyprland, split keyboards" width="100%"></a>

<a href="https://rotten-guy.github.io"><img src="https://img.shields.io/badge/portfolio-rotten--guy.github.io-00f0ff?style=for-the-badge&labelColor=070914" alt="Portfolio"></a>
<a href="https://github.com/rotten-guy/dotfiles"><img src="https://img.shields.io/badge/rice-nebula-e600ff?style=for-the-badge&labelColor=070914" alt="Nebula rice"></a>
<a href="https://www.keybr.com/profile/752ae7r"><img src="https://img.shields.io/badge/keybr-profile-ffb800?style=for-the-badge&labelColor=070914" alt="keybr"></a>
<a href="https://monkeytype.com/profile/rotten_guy"><img src="https://img.shields.io/badge/monkeytype-rotten__guy-ffb800?style=for-the-badge&labelColor=070914" alt="Monkeytype"></a>
<a href="https://www.root-me.org/rotten-guy?lang=en"><img src="https://img.shields.io/badge/root--me-rotten--guy-00ff66?style=for-the-badge&labelColor=070914" alt="Root-Me"></a>

</div>

---

## ✨ whoami

| | | |
|---|---|---|
| 🎓 | **Studying** | BUT Networks & Telecoms (R&T) at the IUT of Montbéliard |
| 🐧 | **Daily driver** | Arch Linux + Hyprland, a neon cyan / magenta rice called **Nebula** |
| ⌨️ | **Typing on** | A wireless Lily58 running my own ZMK firmware, with a bongo cat on the screen |
| 🎯 | **Training** | Root-Me (security) and typing on keybr / Monkeytype, live stats below |
| 🌐 | **Portfolio** | [rotten-guy.github.io](https://rotten-guy.github.io), the same theme as a website (press `K` there) |

---

## 🗂️ Projects

<a href="https://github.com/rotten-guy/dotfiles"><img src="assets/card-dotfiles.svg" alt="rotten_dotfiles: a neon cyan / magenta Hyprland rice" width="49%"></a>
<a href="https://github.com/rotten-guy/rotten_lily58_keymap_config"><img src="assets/card-lily58.svg" alt="rotten Lily58: wireless split keyboard, custom ZMK screens" width="49%"></a>
<a href="https://github.com/rotten-guy/rotten-guy.github.io"><img src="assets/card-portfolio.svg" alt="rotten_portfolio: this theme, as a website" width="49%"></a>
<a href="https://github.com/rotten-guy/dotfiles/tree/main/docs"><img src="assets/card-guides.svg" alt="Write-ups: ZMK dongle, IKEv2 VPN, tablet as a monitor, Arch notes" width="49%"></a>

---

## 🎯 Training

<a href="https://www.root-me.org/rotten-guy?lang=en"><img src="assets/card-rootme.svg" alt="Root-Me: score, solved challenges and position" width="49%"></a>
<a href="https://www.keybr.com/profile/752ae7r"><img src="assets/card-typing.svg" alt="Typing: keybr and Monkeytype stats" width="49%"></a>

<a href="https://monkeytype.com/profile/rotten_guy"><img src="assets/typing.svg" alt="My Lily58 typing i use arch btw, sudo pacman -Syu and ping -c 1 8.8.8.8 at my real speed" width="100%"></a>

<a href="https://rotten-guy.github.io/#skills"><img src="assets/activity.svg" alt="Typing calendar: minutes typed per day" width="100%"></a>

---

## ⌨️ Skills

<img src="assets/skills.svg" alt="Skills: Linux, Arch, systemd, SSH, TCP/IP, VPN, Bash, Python, Lua, C, C++, PHP, SQL, HTML, CSS, JavaScript, TypeScript, QML, Git, GitHub, Neovim, GitHub Actions, ZMK, Zephyr RTOS" width="100%">

---

## 📊 Stats

<img src="assets/stats.svg" alt="GitHub stats: contributions, streak, repositories and languages" width="100%">

<sub>Redrawn every day by <a href=".github/workflows/stats.yml">GitHub Actions</a>, no third-party stats service.</sub>

---

<details>
<summary>🔧 How this profile is made</summary>

<br>

Every picture is an SVG drawn by a Python script, in the colors of the [Nebula rice](https://github.com/rotten-guy/dotfiles): background `#070914`, cyan `#00f0ff`, magenta `#e600ff`, fonts JetBrains Mono and Outfit. Text is turned into paths (`fontTools`) so it looks the same on every machine, and the borders spin like the Hyprland ones.

```bash
pip install fonttools
python3 scripts/make-cards.py                          # banner, cards, skills
python3 scripts/make-logo.py                           # logos
python3 scripts/make-stats.py --sample /tmp/stats.svg  # stats preview with made-up numbers
python3 scripts/make-training.py --sample /tmp/training # typing / Root-Me preview with made-up numbers
```

| File | Purpose |
|---|---|
| `scripts/nebula.py` | Palette, text-to-path, starry background, animated border, keycaps |
| `scripts/make-cards.py` | `banner.svg`, the `card-*.svg` and `skills.svg` |
| `scripts/make-logo.py` | `assets/logo/`: the personal logo (`avatar-*`, "rotten / guy>_") and the website logo (`site`, ">_"), with 1024 px PNG exports |
| `scripts/make-training.py` | `training.json`, `typing.svg` (the Lily58 typing three phrases at my real speed), `activity.svg`, `card-typing.svg`, `card-rootme.svg`, from keybr, Monkeytype and Root-Me (run by the same workflow) |
| `scripts/make-stats.py` | `stats.svg` from the GitHub API (run by `.github/workflows/stats.yml`) |
| `scripts/fonts/` | JetBrains Mono and Outfit (SIL Open Font License) |

</details>
