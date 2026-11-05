"""Conexão com o Postgres: pool de conexões e controle de transação.
Não conhece nenhuma tabela nem regra de negócio."""
import logging
import time
from contextlib import contextmanager

from psycopg2 import pool

from app.config import DB_CONFIG

_pool = None


def iniciar_pool():
    """Cria o pool e tenta até o banco responder (útil no K3s, onde não existe depends_on)."""
    global _pool
    while True:
        try:
            _pool = pool.ThreadedConnectionPool(minconn=1, maxconn=10, **DB_CONFIG)
            logging.info(f"[BANCO] Conectado ao Postgres em {DB_CONFIG['host']}:{DB_CONFIG['port']}")
            return
        except Exception as e:
            logging.warning(f"Aguardando o Postgres estar disponível... ({e})")
            time.sleep(3)


def fechar_pool():
    if _pool is not None:
        _pool.closeall()


@contextmanager
def transacao():
    """Entrega um cursor dentro de uma transação: commit se o bloco terminar bem,
    rollback se levantar exceção. A conexão volta pro pool no final."""
    if _pool is None:
        raise RuntimeError("Pool de conexões não foi iniciado")
    conn = _pool.getconn()
    try:
        with conn:  # commit / rollback
            with conn.cursor() as cur:
                yield cur
    finally:
        _pool.putconn(conn)