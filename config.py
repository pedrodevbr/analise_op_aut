import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env (se existir)
load_dotenv()

class Config:
    """Classe de configuração base"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'chave-secreta-padrao'
    
    # Configurações para API do Anthropic (Claude)
    ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
    
    # Configurações gerais da aplicação
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Limite de 16MB para uploads

    # Constantes para cálculos
    ALTO_VALOR = 10000  # Valor considerado alto para análise
    ALTO_VOLUME = 1000  # Volume considerado alto para análise

class DevelopmentConfig(Config):
    """Configuração para ambiente de desenvolvimento"""
    DEBUG = True

class ProductionConfig(Config):
    """Configuração para ambiente de produção"""
    DEBUG = False

# Dicionário de configurações
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# Configuração ativa
active_config = config[os.environ.get('FLASK_ENV', 'default')]