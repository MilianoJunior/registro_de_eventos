# criar_schema_5tabelas.py
# -*- coding: utf-8 -*-
import sys
import os

# Adiciona o diretório raiz ao path para imports funcionarem
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
sys.path.insert(0, ROOT_DIR)

from textwrap import dedent
from mysql.connector import Error

# Importe sua classe Database
from libs.models.database import Database


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

    # 6) paradas (snapshots JSON de status das usinas)
    stmts.append(dedent("""
        CREATE TABLE IF NOT EXISTS op_paradas (
          id BIGINT PRIMARY KEY AUTO_INCREMENT,
          timestamp DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
          dados JSON NOT NULL,
          KEY ix_timestamp (timestamp)
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
        db.execute_many(schema_statements_5())   # cria 6 tabelas
        db.execute_many(trigger_statements())    # cria gatilhos
        print("\n✅ Esquema (6 tabelas) criado/atualizado com sucesso.")
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


# ============================================================
# MIGRAÇÕES - Campos de Resolução de Ocorrências
# ============================================================

def add_campos_resolucao():
    """
    Adiciona os campos necessários para registro e resolução de ocorrências:
    - requer_acao: Se a ocorrência requer ação urgente
    - data_ocorrencia: Data/hora quando a ocorrência aconteceu
    - resolvida_por: ID do usuário que resolveu
    - resolucao_descricao: Descrição de como foi resolvida
    """
    db = Database()
    try:
        conn = db.connect()
        cur = conn.cursor()
        
        print("\n" + "="*60)
        print("ADICIONANDO CAMPOS DE RESOLUÇÃO")
        print("="*60)
        
        # Lista de campos a adicionar
        campos = [
            ('requer_acao', 'TINYINT(1)', 'NOT NULL DEFAULT 0', 'Se requer ação urgente'),
            ('data_ocorrencia', 'DATETIME(6)', 'NULL', 'Data/hora quando ocorreu'),
            ('resolvida_por', 'BIGINT', 'NULL', 'Usuário que resolveu'),
            ('resolucao_descricao', 'LONGTEXT', 'NULL', 'Como foi resolvida')
        ]
        
        for campo, tipo, restricao, descricao in campos:
            # Verifica se a coluna já existe
            cur.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                  AND TABLE_NAME = 'op_ocorrencia' 
                  AND COLUMN_NAME = %s
            """, (campo,))
            
            exists = cur.fetchone()[0]
            
            if not exists:
                sql = f"ALTER TABLE op_ocorrencia ADD COLUMN {campo} {tipo} {restricao} COMMENT '{descricao}'"
                cur.execute(sql)
                print(f"✅ Campo '{campo}' adicionado com sucesso")
            else:
                print(f"ℹ️  Campo '{campo}' já existe, pulando...")
        
        conn.commit()
        cur.close()
        print("\n✅ Todos os campos foram processados!")
        
    except Exception as e:
        print(f"\n❌ Erro ao adicionar campos: {e}")
        raise
    finally:
        db.close()


def add_constraints_resolucao():
    """
    Adiciona as constraints (foreign keys) para os campos de resolução
    """
    db = Database()
    try:
        conn = db.connect()
        cur = conn.cursor()
        
        print("\n" + "="*60)
        print("ADICIONANDO CONSTRAINTS")
        print("="*60)
        
        # Verifica se a constraint já existe
        cur.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS 
            WHERE CONSTRAINT_SCHEMA = DATABASE() 
              AND TABLE_NAME = 'op_ocorrencia' 
              AND CONSTRAINT_NAME = 'fk_oc_resolvedor'
        """)
        
        exists = cur.fetchone()[0]
        
        if not exists:
            cur.execute("""
                ALTER TABLE op_ocorrencia
                ADD CONSTRAINT fk_oc_resolvedor 
                FOREIGN KEY (resolvida_por) REFERENCES op_usuario(id)
                ON DELETE SET NULL
            """)
            conn.commit()
            print("✅ Constraint 'fk_oc_resolvedor' adicionada com sucesso")
        else:
            print("ℹ️  Constraint 'fk_oc_resolvedor' já existe, pulando...")
        
        cur.close()
        print("\n✅ Constraints processadas!")
        
    except Exception as e:
        print(f"\n❌ Erro ao adicionar constraints: {e}")
        raise
    finally:
        db.close()


def add_indices_resolucao():
    """
    Adiciona índices para melhorar a performance das consultas
    """
    db = Database()
    try:
        conn = db.connect()
        cur = conn.cursor()
        
        print("\n" + "="*60)
        print("ADICIONANDO ÍNDICES")
        print("="*60)
        
        # Lista de índices a adicionar
        indices = [
            ('ix_requer_acao', ['requer_acao', 'status'], 'Índice para filtrar por ações urgentes'),
            ('ix_data_ocorrencia', ['data_ocorrencia'], 'Índice para ordenação por data de ocorrência')
        ]
        
        for nome_indice, colunas, descricao in indices:
            # Verifica se o índice já existe
            cur.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.STATISTICS 
                WHERE TABLE_SCHEMA = DATABASE() 
                  AND TABLE_NAME = 'op_ocorrencia' 
                  AND INDEX_NAME = %s
            """, (nome_indice,))
            
            exists = cur.fetchone()[0]
            
            if not exists:
                colunas_str = ', '.join(colunas)
                sql = f"ALTER TABLE op_ocorrencia ADD INDEX {nome_indice} ({colunas_str})"
                cur.execute(sql)
                print(f"✅ Índice '{nome_indice}' criado: {descricao}")
            else:
                print(f"ℹ️  Índice '{nome_indice}' já existe, pulando...")
        
        conn.commit()
        cur.close()
        print("\n✅ Índices processados!")
        
    except Exception as e:
        print(f"\n❌ Erro ao adicionar índices: {e}")
        raise
    finally:
        db.close()


def migrate_all_resolucao():
    """
    Executa todas as migrações relacionadas à resolução de ocorrências:
    1. Adiciona campos
    2. Adiciona constraints
    3. Adiciona índices
    """
    print("\n" + "="*60)
    print("INICIANDO MIGRAÇÃO COMPLETA - RESOLUÇÃO DE OCORRÊNCIAS")
    print("="*60 + "\n")
    
    try:
        add_campos_resolucao()
        add_constraints_resolucao()
        add_indices_resolucao()
        
        print("\n" + "="*60)
        print("✅ MIGRAÇÃO COMPLETA REALIZADA COM SUCESSO!")
        print("="*60 + "\n")
        
    except Exception as e:
        print("\n" + "="*60)
        print("❌ ERRO NA MIGRAÇÃO")
        print("="*60)
        print(f"Erro: {e}\n")
        raise


def populate_data_ocorrencia():
    """
    (OPCIONAL) Popula o campo data_ocorrencia com created_at para registros existentes
    """
    db = Database()
    try:
        conn = db.connect()
        cur = conn.cursor()
        
        print("\n" + "="*60)
        print("POPULANDO DATA DE OCORRÊNCIA")
        print("="*60)
        
        # Conta registros sem data_ocorrencia
        cur.execute("""
            SELECT COUNT(*) 
            FROM op_ocorrencia 
            WHERE data_ocorrencia IS NULL
        """)
        count = cur.fetchone()[0]
        
        if count > 0:
            print(f"\nEncontrados {count} registros sem data_ocorrencia")
            print("Copiando created_at para data_ocorrencia...")
            
            cur.execute("""
                UPDATE op_ocorrencia 
                SET data_ocorrencia = created_at 
                WHERE data_ocorrencia IS NULL
            """)
            
            conn.commit()
            print(f"✅ {count} registros atualizados com sucesso!")
        else:
            print("ℹ️  Todos os registros já possuem data_ocorrencia")
        
        cur.close()
        
    except Exception as e:
        print(f"\n❌ Erro ao popular data_ocorrencia: {e}")
        raise
    finally:
        db.close()


def drop_tabela_paradas():
    """
    Deleta a tabela op_paradas
    """
    db = Database()
    try:
        conn = db.connect()
        cur = conn.cursor()
        
        print("\n" + "="*60)
        print("DELETANDO TABELA OP_PARADAS")
        print("="*60)
        
        # Verifica se a tabela existe
        cur.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = DATABASE() 
              AND TABLE_NAME = 'op_paradas'
        """)
        
        exists = cur.fetchone()[0]
        
        if exists:
            cur.execute("DROP TABLE op_paradas")
            conn.commit()
            print("✅ Tabela 'op_paradas' deletada com sucesso!")
        else:
            print("ℹ️  Tabela 'op_paradas' não existe, nada a fazer.")
        
        cur.close()
        
    except Exception as e:
        print(f"\n❌ Erro ao deletar tabela op_paradas: {e}")
        raise
    finally:
        db.close()


def create_tabela_paradas():
    """
    Cria apenas a tabela op_paradas (status/potência das usinas)
    """
    db = Database()
    try:
        conn = db.connect()
        cur = conn.cursor()
        
        print("\n" + "="*60)
        print("CRIANDO TABELA OP_PARADAS")
        print("="*60)
        
        # Verifica se a tabela já existe
        cur.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = DATABASE() 
              AND TABLE_NAME = 'op_paradas'
        """)
        
        exists = cur.fetchone()[0]
        
        if exists:
            print("ℹ️  Tabela 'op_paradas' já existe")
        else:
            cur.execute(dedent("""
                CREATE TABLE op_paradas (
                  id BIGINT PRIMARY KEY AUTO_INCREMENT,
                  timestamp DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
                  dados JSON NOT NULL,
                  KEY ix_timestamp (timestamp)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
            """))
            conn.commit()
            print("✅ Tabela 'op_paradas' criada com sucesso!")
        
        cur.close()
        
    except Exception as e:
        print(f"\n❌ Erro ao criar tabela op_paradas: {e}")
        raise
    finally:
        db.close()


def migrate_labels_json():
    """
    Atualiza as labels de status antigas para as novas siglas no campo JSON da tabela op_paradas.
    """
    db = Database()
    try:
        conn = db.connect()
        cur = conn.cursor()
        
        print("\n" + "="*60)
        print("MIGRANDO LABELS DE STATUS (JSON)")
        print("="*60)
        
        # Mapa de substituições (Da mais específica para a menos específica)
        replacements = [
            ("Status U.P. (parada)", "UP (parada)"),
            ("Status U.P.G.M. (pronta para giro mecânico)", "UPGM (pronta para giro mecânico)"),
            ("Status U.P.S.(pronta para sincronização)", "UPS (pronta para sincronização)"),
            ("Status U.M.D.(sincronizado)", "UMD (marcha desexcitada)"),
            ("Status sincronizado", "US (sincronizado)")
        ]
        
        # Construção da query com REPLACE aninhados
        # CAST(dados AS CHAR) converte o JSON para string para o REPLACE funcionar
        expression = "CAST(dados AS CHAR)"
        for old, new in replacements:
            expression = f"REPLACE({expression}, '{old}', '{new}')"
            
        sql = f"UPDATE op_paradas SET dados = CAST({expression} AS JSON) WHERE dados IS NOT NULL"
        
        print("Executando atualização no banco de dados...")
        cur.execute(sql)
        rows_affected = cur.rowcount
        conn.commit()
        
        print(f"✅ Atualização concluída! Registros afetados: {rows_affected}")
        
        cur.close()
        
    except Exception as e:
        print(f"\n❌ Erro ao migrar labels: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        comando = sys.argv[1]
        
        if comando == 'migrate':
            # Migração completa
            migrate_all_resolucao()
        elif comando == 'campos':
            # Apenas campos
            add_campos_resolucao()
        elif comando == 'constraints':
            # Apenas constraints
            add_constraints_resolucao()
        elif comando == 'indices':
            # Apenas índices
            add_indices_resolucao()
        elif comando == 'populate':
            # Popular data_ocorrencia
            populate_data_ocorrencia()
        elif comando == 'schema':
            # Criar schema original
            run()
        elif comando == 'paradas':
            # Criar apenas tabela op_paradas
            create_tabela_paradas()
        elif comando == 'drop_paradas':
            # Deletar tabela op_paradas
            drop_tabela_paradas()
        elif comando == 'labels':
            # Migrar labels JSON
            migrate_labels_json()
        else:
            print("Comandos disponíveis:")
            print("  python cog_schema.py schema        - Cria o schema original (6 tabelas)")
            print("  python cog_schema.py migrate       - Executa migração completa")
            print("  python cog_schema.py campos        - Adiciona apenas os campos")
            print("  python cog_schema.py constraints   - Adiciona apenas as constraints")
            print("  python cog_schema.py indices       - Adiciona apenas os índices")
            print("  python cog_schema.py populate      - Popula data_ocorrencia com created_at")
            print("  python cog_schema.py paradas       - Cria apenas a tabela op_paradas")
            print("  python cog_schema.py drop_paradas  - Deleta a tabela op_paradas")
            print("  python cog_schema.py labels        - Migra labels de status antigas para novas no JSON")
    else:
        # Comando padrão: migração completa de resolução
        print("\n💡 Dica: Use 'python cog_schema.py migrate' para migração completa")
        print("     ou 'python cog_schema.py schema' para criar schema original\n")
        migrate_all_resolucao()