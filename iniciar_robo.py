import fcntl
import glob
import os
import select
import signal
import struct
import subprocess
import time

PASTA = "/home/capi/fetin"
PYTHON = "/home/capi/fetin/env_voz/bin/python3"
SCRIPT = "/home/capi/fetin/robo_fetin.py"
LOCK = "/tmp/capi_robo_watcher.lock"

os.environ.setdefault("XDG_RUNTIME_DIR", "/run/user/1000")
SINK_BLUETOOTH = "bluez_output.41_42_AA_44_23_14.1"

EV_KEY = 0x01
TECLA_ESC = 1
TECLA_ESPACO = 57
TAMANHO_EVENTO = struct.calcsize("llHHI")


def abrir_dispositivos():
    dispositivos = {}
    for caminho in glob.glob("/dev/input/event*"):
        try:
            dispositivos[caminho] = os.open(caminho, os.O_RDONLY | os.O_NONBLOCK)
        except OSError:
            pass
    return dispositivos


def atualizar_dispositivos(dispositivos):
    atuais = set(glob.glob("/dev/input/event*"))
    for caminho in list(dispositivos):
        if caminho not in atuais:
            os.close(dispositivos.pop(caminho))
    for caminho in atuais - set(dispositivos):
        try:
            dispositivos[caminho] = os.open(caminho, os.O_RDONLY | os.O_NONBLOCK)
        except OSError:
            pass


def ler_eventos(dispositivos, timeout):
    if not dispositivos:
        time.sleep(timeout)
        return
    try:
        prontos, _, _ = select.select(list(dispositivos.values()), [], [], timeout)
    except OSError:
        return
    for fd in prontos:
        try:
            dados = os.read(fd, TAMANHO_EVENTO * 64)
        except OSError:
            continue
        for inicio in range(0, len(dados) - TAMANHO_EVENTO + 1, TAMANHO_EVENTO):
            _, _, tipo, codigo, valor = struct.unpack(
                "llHHI", dados[inicio:inicio + TAMANHO_EVENTO]
            )
            if tipo == EV_KEY and valor == 1:
                yield codigo


def encerrar_processo(processo):
    try:
        os.killpg(os.getpgid(processo.pid), signal.SIGTERM)
    except ProcessLookupError:
        pass


def iniciar_apresentacao(dispositivos):
    print("[watcher] Espaco detectado. Iniciando apresentacao...", flush=True)
    time.sleep(0.5)

    subprocess.run(
        ["wpctl", "set-default", SINK_BLUETOOTH],
        capture_output=True,
        timeout=10,
    )

    processo = subprocess.Popen([PYTHON, SCRIPT], cwd=PASTA, start_new_session=True)

    try:
        while processo.poll() is None:
            atualizar_dispositivos(dispositivos)
            for codigo in ler_eventos(dispositivos, 0.2):
                if codigo == TECLA_ESC:
                    print("[watcher] Esc detectado. Encerrando apresentacao...", flush=True)
                    encerrar_processo(processo)
    finally:
        if processo.poll() is None:
            encerrar_processo(processo)
        processo.wait()

    print("[watcher] Apresentacao encerrada. Aguardando espaco...", flush=True)
    time.sleep(1)


def main():
    print("[watcher] Aguardando a tecla espaco para iniciar...", flush=True)
    dispositivos = abrir_dispositivos()
    while True:
        atualizar_dispositivos(dispositivos)
        for codigo in ler_eventos(dispositivos, 1):
            if codigo == TECLA_ESPACO:
                iniciar_apresentacao(dispositivos)


if __name__ == "__main__":
    trava = open(LOCK, "w")
    try:
        fcntl.flock(trava, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        print("[watcher] Ja existe uma instancia rodando. Encerrando.", flush=True)
        raise SystemExit(1)
    main()
