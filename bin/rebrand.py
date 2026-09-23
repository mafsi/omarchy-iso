#!/usr/bin/env python3
"""Rebranding omarchy-iso -> arch-deploy.

Ce se redenumeste: tot ce e al ISO-ului asta — nume vizibile, cai proprii,
variabile de mediu proprii, numele scripturilor din bin/.

Ce NU se atinge, si de ce: orice nume care traverseaza granita catre pachetele
semnate ale celor de la omarchy. Le pastram (decizie explicita), deci numele lor
trebuie sa ramina EXACT cum sint, altfel pacman nu mai gaseste nimic.
"""
import os, re, sys

ROOT = os.getcwd()

# --- ce ramine neatins -------------------------------------------------------
PROTEJAT = [
    # Pachetele lor, din depoul lor semnat.
    r'omarchy-settings-dev', r'omarchy-settings', r'omarchy-keyring',
    r'omarchy-nvim', r'omarchy-base', r'omarchy-other',
    r'build-omarchy-packages', r'omarchy\.gpg',
    # Binarele livrate de pachetul lor de runtime in /usr/bin. Nu exista in
    # repoul asta — sint apelate din el. Lista e explicita, nu un tipar: tot ce
    # NU e aici trebuie sa fie un fisier din repo, si se redenumeste.
    r'omarchy-(apply-system|build-uki|hibernation-setup|provision-owner'
    r'|provision-user|sign-uki|upload-log|system-factory-reset)',
    # Numele sectiunii de repo din pacman.conf — trebuie sa fie cel de pe server.
    r'\[omarchy\]',
    # Serverele lor.
    r'[a-z0-9-]*\.omarchy\.org',
    # Calea unde se instaleaza pachetul lor de runtime, si variabilele pe care
    # le citesc scripturile DIN acel pachet.
    # Slash-ul e optional intentionat: in build-iso.sh calea apare si RELATIVA,
    # ca specificatie de membru pentru bsdtar in arhiva pachetului lor
    # (`usr/share/omarchy/install/omarchy-base.packages`). Fara asta a fost
    # redenumita si extragerea n-ar mai fi gasit nimic.
    r'/?usr/share/omarchy(?![-\w])',
    r'LOCAL_OMARCHY_PATH', r'OMARCHY_PATH',
    r'OMARCHY_RUNTIME_PACKAGE', r'OMARCHY_SETTINGS_PACKAGE', r'OMARCHY_NVIM_PACKAGE',
    r'OMARCHY_INSTALL(?![_\w])',
    # Montarile din containerul de build catre checkout-urile lor.
    r'/omarchy-source', r'/omarchy-pkgs',
    # Pachetul de runtime, ca valoare implicita.
    r'(?<=[:=-])omarchy(?=[\}"\'\s])',
]

# --- ce se redenumeste, in ordine (cele mai lungi intii) ---------------------
REDENUMIRI = [
    (r'omarchy-iso', 'arch-deploy'),
    (r'omarchy_iso', 'arch_deploy'),
    # Identificatori si chei JSON: cratima e ilegala intr-un nume Python.
    # `omarchy_install` devenit `arch-deploy_install` a rupt context.py cu
    # "illegal target for annotation" — prins la compileall, inainte de build.
    (r'omarchy_', 'arch_deploy_'),
    # Si sufixul: `_install_limine_omarchy` ar fi devenit `..._arch-deploy`,
    # la fel de nevalid. Orice `omarchy` lipit de un underscore e un
    # identificator, nu un nume de brand.
    (r'(?<=_)omarchy\b', 'arch_deploy'),
    (r'OMARCHY_ISO', 'ARCH_DEPLOY'),
    (r'Omarchy ISO', 'arch-deploy'),
    (r'OMARCHY_', 'ARCH_DEPLOY_'),
    (r'OMARCHY', 'ARCH_DEPLOY'),
    (r'Omarchy', 'arch-deploy'),
    (r'omarchy', 'arch-deploy'),
]

SARI_PESTE = {'.git', 'archiso', 'manifests', 'node_modules'}
FISIERE_INTACTE = {'LICENSE'}          # MIT cere pastrarea notei de copyright

def proceseaza(text):
    depozit = []
    def masca(m):
        depozit.append(m.group(0))
        return '\x00%d\x00' % (len(depozit) - 1)
    for p in PROTEJAT:
        text = re.sub(p, masca, text)
    for vechi, nou in REDENUMIRI:
        text = re.sub(vechi, nou, text)
    return re.sub(r'\x00(\d+)\x00', lambda m: depozit[int(m.group(1))], text)

schimbate, redenumite = [], []
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in SARI_PESTE]
    for fn in filenames:
        if fn in FISIERE_INTACTE:
            continue
        cale = os.path.join(dirpath, fn)
        try:
            with open(cale, encoding='utf-8') as f:
                vechi = f.read()
        except (UnicodeDecodeError, IsADirectoryError):
            continue
        nou = proceseaza(vechi)
        if nou != vechi:
            with open(cale, 'w', encoding='utf-8') as f:
                f.write(nou)
            schimbate.append(os.path.relpath(cale, ROOT))

# Numele fisierelor si directoarelor, de la adinc spre suprafata.
for dirpath, dirnames, filenames in os.walk(ROOT, topdown=False):
    if any(s in dirpath.split(os.sep) for s in SARI_PESTE):
        continue
    for nume in filenames + dirnames:
        if 'omarchy' not in nume or nume in FISIERE_INTACTE:
            continue
        nou_nume = proceseaza(nume)
        if nou_nume != nume:
            os.rename(os.path.join(dirpath, nume), os.path.join(dirpath, nou_nume))
            redenumite.append('%s -> %s' % (nume, nou_nume))

print('fisiere cu continut schimbat: %d' % len(schimbate))
print('fisiere/directoare redenumite: %d' % len(redenumite))
for r in sorted(redenumite):
    print('  ' + r)
