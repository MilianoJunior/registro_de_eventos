# criar_schema_5tabelas.py
# -*- coding: utf-8 -*-
from textwrap import dedent
from mysql.connector import Error

# Importe sua classe Database
from libs.models.database import Database  # <<< TROQUE PELO NOME DO ARQUIVO/MÓDULO


def schema_statements_5():
    stmts = []

    # Charset/collation
    stmts.append("SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;")

    # 1) usina
    stmts.append(dedent("""
        CREATE TABLE IF NOT EXISTS op_usina (
          id BIGINT PRIMARY KEY AUTO_INCREMENT,
          nome VARCHAR(120) NOT NULL,
          sigla VARCHAR(40) UNIQUE,
          timezone VARCHAR(40) NOT NULL DEFAULT 'America/Sao_Paulo',
          ativo TINYINT(1) NOT NULL DEFAULT 1,
          created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
          updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
                     ON UPDATE CURRENT_TIMESTAMP(6)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
    """))

    # 2) usuario
    stmts.append(dedent("""
        CREATE TABLE IF NOT EXISTS op_usuario (
          id BIGINT PRIMARY KEY AUTO_INCREMENT,
          nome VARCHAR(120) NOT NULL,
          email VARCHAR(160),
          perfil ENUM('operador','engenharia','gestor','admin') NOT NULL DEFAULT 'operador',
          ativo TINYINT(1) NOT NULL DEFAULT 1,
          created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
          updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
                     ON UPDATE CURRENT_TIMESTAMP(6),
          UNIQUE KEY uk_usuario_email (email)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
    """))

    # 3) ocorrencia (campos da tela)
    stmts.append(dedent("""
        CREATE TABLE IF NOT EXISTS op_ocorrencia (
          id BIGINT PRIMARY KEY AUTO_INCREMENT,
          usina_id BIGINT NOT NULL,
          operador_id BIGINT NOT NULL,

          -- Campos da UI:
          tipo VARCHAR(60) NOT NULL,               -- Ex.: Evento, Alarme, Trip
          categoria VARCHAR(80) NOT NULL,          -- Ex.: Operação/Humano, Elétrica...
          unidade VARCHAR(120) NOT NULL,           -- Ex.: UG-01, Vertedouro...
          tags VARCHAR(255) NULL,                  -- CSV: "trip, vibração"
          playbook TEXT NULL,                      -- instruções/guia aplicado
          template_texto TEXT NULL,                -- texto-base aplicado
          descricao LONGTEXT NOT NULL,             -- descrição detalhada

          -- Controles simples
          status ENUM('aberta','em_andamento','resolvida','cancelada')
                 NOT NULL DEFAULT 'aberta',
          severidade ENUM('baixa','média','alta','crítica')
                 NOT NULL DEFAULT 'média',
          origem ENUM('humano','scada','api','importacao')
                 NOT NULL DEFAULT 'humano',

          metadata JSON NULL,                      -- livre p/ IDs SCADA, leituras, etc.

          created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
          updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
                     ON UPDATE CURRENT_TIMESTAMP(6),
          resolved_at DATETIME(6) NULL,

          CONSTRAINT fk_oc_usina    FOREIGN KEY (usina_id)    REFERENCES op_usina(id),
          CONSTRAINT fk_oc_operador FOREIGN KEY (operador_id) REFERENCES op_usuario(id),

          KEY ix_ocorrencia_busca (usina_id, operador_id, status, created_at),
          FULLTEXT KEY ft_descricao (descricao)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
    """))

    # 4) ocorrencia_hist (auditoria simples)
    stmts.append(dedent("""
        CREATE TABLE IF NOT EXISTS op_ocorrencia_hist (
          id BIGINT PRIMARY KEY AUTO_INCREMENT,
          ocorrencia_id BIGINT NOT NULL,
          usuario_id BIGINT NULL,
          acao ENUM('criado','atualizado','status','comentario','anexo') NOT NULL,
          detalhe TEXT NULL,
          created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
          CONSTRAINT fk_ochist_oc  FOREIGN KEY (ocorrencia_id) REFERENCES op_ocorrencia(id) ON DELETE CASCADE,
          CONSTRAINT fk_ochist_usr FOREIGN KEY (usuario_id)    REFERENCES op_usuario(id),
          KEY ix_ochist_oc (ocorrencia_id, created_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
    """))

    # 5) anexo
    stmts.append(dedent("""
        CREATE TABLE IF NOT EXISTS op_anexo (
          id BIGINT PRIMARY KEY AUTO_INCREMENT,
          ocorrencia_id BIGINT NOT NULL,
          nome_arquivo VARCHAR(255) NOT NULL,
          mime_type VARCHAR(120),
          tamanho_bytes BIGINT,
          url_armazenamento VARCHAR(512) NOT NULL, -- S3/MinIO/FS
          created_by BIGINT NULL,
          created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
          CONSTRAINT fk_anexo_oc   FOREIGN KEY (ocorrencia_id) REFERENCES op_ocorrencia(id) ON DELETE CASCADE,
          CONSTRAINT fk_anexo_user FOREIGN KEY (created_by)     REFERENCES op_usuario(id),
          KEY ix_anexo_oc (ocorrencia_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
    """))

    return stmts


def trigger_statements():
    """Gatilhos simples para auditar criação/atualização de ocorrência."""
    stmts = [
        "DROP TRIGGER IF EXISTS trg_ocorrencia_after_insert;",
        "DROP TRIGGER IF EXISTS trg_ocorrencia_after_update;",
        dedent("""
            CREATE TRIGGER trg_ocorrencia_after_insert
            AFTER INSERT ON op_ocorrencia
            FOR EACH ROW
            BEGIN
              INSERT INTO op_ocorrencia_hist (ocorrencia_id, usuario_id, acao, detalhe)
              VALUES (NEW.id, NEW.operador_id, 'criado',
                      JSON_OBJECT('status', NEW.status));
            END;
        """),
        dedent("""
            CREATE TRIGGER trg_ocorrencia_after_update
            AFTER UPDATE ON op_ocorrencia
            FOR EACH ROW
            BEGIN
              IF (OLD.status <> NEW.status) THEN
                INSERT INTO op_ocorrencia_hist (ocorrencia_id, usuario_id, acao, detalhe)
                VALUES (NEW.id, NEW.operador_id, 'status',
                        JSON_OBJECT('de', OLD.status, 'para', NEW.status));
              ELSE
                INSERT INTO op_ocorrencia_hist (ocorrencia_id, usuario_id, acao, detalhe)
                VALUES (NEW.id, NEW.operador_id, 'atualizado', NULL);
              END IF;
            END;
        """)
    ]
    return stmts


def run():
    db = Database()
    try:
        db.connect()
        db.execute_many(schema_statements_5())   # cria 5 tabelas
        db.execute_many(trigger_statements())    # cria gatilhos
        print("\n✅ Esquema (5 tabelas) criado/atualizado com sucesso.")
    except Exception as e:
        print(f"\n❌ Erro ao criar o esquema: {e}")
        raise
    finally:
        db.close()

def drop_tabela_sql():
    db = Database()
    try:
        conn = db.connect()
        cur = conn.cursor()

        # 1) Verifica se a coluna existe
        cur.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
              AND TABLE_NAME = 'op_usina' 
              AND COLUMN_NAME = 'tabela_sql'
        """)
        exists = cur.fetchone()[0]

        if exists:
            cur.execute("ALTER TABLE op_usina DROP COLUMN tabela_sql;")
            conn.commit()
            print("✅ Coluna 'tabela_sql' removida da tabela op_usina.")
        else:
            print("ℹ️  Coluna 'tabela_sql' não existe em op_usina, nada a fazer.")

        cur.close()
    finally:
        db.close()


if __name__ == "__main__":
    run()
