
import sys
import os

# Adiciona o diretório raiz ao path para imports funcionarem
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
sys.path.insert(0, ROOT_DIR)

from libs.models.database import Database

def run_migration():
    db = Database()
    try:
        conn = db.connect()
        cur = conn.cursor()
        
        print("Adicionando coluna 'deslocamento' na tabela 'rats'...")
        
        # Check if column exists
        cur.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
              AND TABLE_NAME = 'rats' 
              AND COLUMN_NAME = 'deslocamento'
        """)
        exists = cur.fetchone()[0]
        
        if not exists:
            cur.execute("ALTER TABLE rats ADD COLUMN deslocamento VARCHAR(100) NULL COMMENT 'Km rodados ou Remoto'")
            conn.commit()
            print("✅ Coluna 'deslocamento' adicionada com sucesso!")
        else:
            print("ℹ️  Coluna 'deslocamento' já existe.")
            
        cur.close()
        
    except Exception as e:
        print(f"❌ Erro na migração: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_migration()
