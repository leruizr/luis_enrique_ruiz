from __future__ import annotations

import socket
import threading
import sys
from typing import Dict, Tuple


HOST = "127.0.0.1"
PORT = 5050


class SupportServer:
    def __init__(self, host: str = HOST, port: int = PORT) -> None:
        self.host = host
        self.port = port
        self.server_sock: socket.socket | None = None
        self.clients: Dict[socket.socket, Tuple[str, Tuple[str, int]]] = {}
        self.lock = threading.Lock()
        self.stop_event = threading.Event()

    def start(self) -> None:
        try:
            self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_sock.bind((self.host, self.port))
            self.server_sock.listen()
        except Exception as e:
            print(f"[ERROR] No se pudo iniciar el servidor: {e}")
            # Asegurar cierre si algo se creó
            try:
                if self.server_sock:
                    self.server_sock.close()
            finally:
                self.server_sock = None
            raise

        print(f"[INFO] Servidor de soporte activo en {self.host}:{self.port}")
        print("[INFO] Comandos: /usuarios, /salir")

        threading.Thread(target=self._accept_loop, daemon=True).start()
        # Hilo de entrada por consola para el operador
        self._operator_loop()

    def _accept_loop(self) -> None:
        assert self.server_sock is not None
        while not self.stop_event.is_set():
            try:
                self.server_sock.settimeout(1.0)
                conn, addr = self.server_sock.accept()
            except socket.timeout:
                continue
            except OSError:
                # Socket cerrado durante apagado
                break
            except Exception as e:
                print(f"[WARN] Error aceptando conexión: {e}")
                continue

            threading.Thread(target=self._handle_client, args=(conn, addr), daemon=True).start()

    def _handle_client(self, conn: socket.socket, addr: Tuple[str, int]) -> None:
        try:
            conn.settimeout(10.0)
            nickname_bytes = conn.recv(1024)
            if not nickname_bytes:
                conn.close()
                return
            nickname = nickname_bytes.decode(errors="ignore").strip()
            conn.settimeout(None)

            with self.lock:
                self.clients[conn] = (nickname, addr)
            print(f"[INFO] {nickname} conectado desde {addr}")
            self._broadcast(f"[SISTEMA] {nickname} se ha unido al chat", exclude=None)

            while not self.stop_event.is_set():
                data = conn.recv(4096)
                if not data:
                    break
                msg = data.decode(errors="ignore").rstrip("\n")
                # Reenviar con prefijo del usuario
                self._broadcast(f"[{nickname}] {msg}", exclude=None)

        except (ConnectionResetError, ConnectionAbortedError):
            pass
        except socket.timeout:
            pass
        except Exception as e:
            print(f"[WARN] Error con cliente {addr}: {e}")
        finally:
            with self.lock:
                info = self.clients.pop(conn, None)
            try:
                conn.close()
            except Exception:
                pass
            if info:
                print(f"[INFO] {info[0]} desconectado")
                self._broadcast(f"[SISTEMA] {info[0]} ha salido del chat", exclude=None)

    def _broadcast(self, message: str, exclude: socket.socket | None) -> None:
        data = (message + "\n").encode()
        with self.lock:
            conns = list(self.clients.keys())
        for c in conns:
            if exclude is not None and c is exclude:
                continue
            try:
                c.sendall(data)
            except Exception:
                # En caso de error, cerrar ese cliente
                try:
                    c.close()
                except Exception:
                    pass
                with self.lock:
                    self.clients.pop(c, None)

    def _operator_loop(self) -> None:
        try:
            for line in sys.stdin:
                line = line.rstrip("\n")
                if line.strip() == "/usuarios":
                    with self.lock:
                        usuarios = ", ".join(n for (n, _) in self.clients.values()) or "(ninguno)"
                    print(f"[INFO] Conectados: {usuarios}")
                elif line.strip() == "/salir":
                    print("[INFO] Cerrando servidor...")
                    break
                elif line.strip():
                    self._broadcast(f"[SOPORTE] {line}", exclude=None)
        except KeyboardInterrupt:
            print("\n[INFO] Interrumpido por el usuario.")
        finally:
            self.shutdown()

    def shutdown(self) -> None:
        self.stop_event.set()
        # Avisar a clientes
        try:
            self._broadcast("[SOPORTE] Servidor cerrándose", exclude=None)
        except Exception:
            pass
        # Cerrar socket de escucha
        if self.server_sock is not None:
            try:
                self.server_sock.close()
            except Exception:
                pass
            self.server_sock = None
        # Cerrar clientes
        with self.lock:
            conns = list(self.clients.keys())
        for c in conns:
            try:
                c.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            try:
                c.close()
            except Exception:
                pass
        with self.lock:
            self.clients.clear()
        print("[INFO] Servidor detenido.")


def main() -> None:
    srv = SupportServer()
    try:
        srv.start()
    except Exception:
        # Ya se informó el error en start(); salir con código distinto de cero
        sys.exit(1)


if __name__ == "__main__":
    main()

