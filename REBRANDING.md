# Rebranding: omarchy-iso → arch-deploy

Fork al [omacom/omarchy-iso](https://github.com/omacom/omarchy-iso) (MIT).
`LICENSE` rămâne neatins — licența cere păstrarea notei de copyright.

Redenumirea s-a făcut cu `bin/rebrand.py`, o singură dată, pe arborele curat.
Scriptul rămâne în repo ca să se vadă **exact** ce s-a schimbat și ce nu.

## Ce s-a redenumit

Tot ce aparține ISO-ului ăstuia: numele vizibile, scripturile din `bin/`,
căile proprii (`/usr/share/arch-deploy`, `/var/cache/arch-deploy/mirror`),
variabilele de mediu proprii (`ARCH_DEPLOY_*`), cheile JSON de configurare.

## Ce NU s-a atins, și de ce

Orice nume care trece granița către pachetele semnate ale celor de la omarchy.
Le păstrăm deocamdată, deci numele lor trebuie să rămână exact cum sunt —
altfel pacman nu mai găsește nimic.

| Ce rămâne | De ce |
|---|---|
| `omarchy-settings`, `omarchy-keyring`, `omarchy-nvim`, `omarchy-base`, `omarchy-other`, `linux-omarchy` | pachete reale din depoul lor |
| `[omarchy]`, `[linux-omarchy]` | numele secțiunilor din `pacman.conf` trebuie să fie cele de pe server |
| `*.omarchy.org` | serverele lor de pachete și de oglinzi |
| `/usr/share/omarchy`, `OMARCHY_PATH`, `OMARCHY_INSTALL`, `OMARCHY_RUNTIME_PACKAGE`, `OMARCHY_SETTINGS_PACKAGE`, `OMARCHY_NVIM_PACKAGE` | calea unde se instalează pachetul lor de runtime, plus variabilele citite de scripturile *din* acel pachet |
| `omarchy-apply-system`, `omarchy-provision-owner`, `omarchy-upload-log` ș.a.m.d. | binare livrate de pachetul lor în `/usr/bin` — nu există în repoul ăsta, doar sunt apelate din el |
| `/omarchy-source`, `/omarchy-pkgs` | punctele de montare din containerul de build către checkout-urile lor |
| `builder/omarchy.gpg`, `build-omarchy-packages.sh` | cheia lor de semnare și constructorul pachetelor lor |
| `Theme=omarchy` | tema Plymouth, livrată de `omarchy-settings` |

## Capcanele prinse la redenumire

Trei, toate găsite de verificări automate înainte de orice build:

1. **Identificatori Python.** `omarchy_install` → `arch-deploy_install` e sintaxă
   invalidă; la fel `_install_limine_omarchy`. Orice `omarchy` lipit de un
   underscore e identificator, nu brand, și devine `arch_deploy`.
   Prins cu `python3 -m compileall`.
2. **Căi relative.** În `build-iso.sh`, calea din pachetul lor apare și fără
   slash la început, ca specificație de membru pentru `bsdtar`
   (`usr/share/omarchy/install/omarchy-base.packages`). Redenumită, extragerea
   n-ar mai fi găsit nimic — și ar fi eșuat abia în build.
3. **Binare care nu sunt în repo.** `omarchy-apply-system` și frații lui sunt
   doar *apelați* de aici. Prins comparând fiecare `bin/...` invocat cu
   fișierele care există efectiv.
