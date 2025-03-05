import os
import sys
from flask import Flask
from app import app

if __name__ == '__main__':
    # Verificar se o diretório de uploads existe
    uploads_dir = os.path.join(os.getcwd(), 'uploads')
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
        
    # Verificar se o diretório de exportação existe
    exports_dir = os.path.join(os.getcwd(), 'exports')
    if not os.path.exists(exports_dir):
        os.makedirs(exports_dir)
        
    # Verificar se os arquivos Excel estão na pasta raiz
    # Se não estiverem, copiar do uploads se disponível
    excel_files = ['OP.XLSX', '0053.XLSX', '0130.XLSX', '0127.XLSX', '0028.XLSX', 'MB51.XLSX']
    
    for file in excel_files:
        if not os.path.exists(file) and os.path.exists(os.path.join(uploads_dir, file)):
            import shutil
            shutil.copy(os.path.join(uploads_dir, file), file)
            print(f"Copiado {file} de uploads/ para raiz para facilitar o debug")

    # Obter a porta da linha de comando ou usar 5000 como padrão
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    
    # Iniciar a aplicação
    app.run(host='0.0.0.0', port=port, debug=True)