from __future__ import annotations

import socket
import threading
import sys


HOST = "127.0.0.1"
PORT = 5050


def receiver_loop(sock: socket.socket) -> None:
    try:
        while True:
            data = sock.recv(4096)
            if not data:
                print("[INFO] Conexión cerrada por el servidor.")
                break
            try:
                print(data.decode(errors="ignore"), end="")
            except Exception:
                pass
    except Exception:
        pass
    finally:
        try:
            sock.close()
        except Exception:
            pass


def main() -> None:
    nickname = input("Ingrese su NickName: ").strip()
    if not nickname:
        print("NickName no puede estar vacío.")
        return

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((HOST, PORT))
    except Exception:
        print("El soporte técnico no se encuentra activo en este momento")
        try:
            sock.close()
        except Exception:
            pass
        return

    # Enviar NickName como primer mensaje
    try:
        sock.sendall((nickname + "\n").encode())
    except Exception:
        print("No se pudo enviar el NickName.")
        try:
            sock.close()
        except Exception:
            pass
        return

    # Hilo para recibir mensajes
    t = threading.Thread(target=receiver_loop, args=(sock,), daemon=True)
    t.start()

    try:
        while True:
            line = sys.stdin.readline()
            if not line:
                break
            if line.strip() == "/salir":
                break
            try:
                sock.sendall(line.encode())
            except Exception:
                print("[WARN] No se pudo enviar el mensaje.")
                break
    except KeyboardInterrupt:
        pass
    finally:
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        try:
            sock.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()

