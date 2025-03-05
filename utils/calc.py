import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from config import active_config

class AnaliseCalculos:
    """
    Classe para realizar cálculos específicos relacionados à análise de materiais
    """
    
    @staticmethod
    def calcular_tempo_medio_entre_demanda(consumos):
        """
        Calcula o tempo médio entre demandas
        
        Args:
            consumos (list): Lista de valores de consumo
        
        Returns:
            float: Tempo médio entre demandas
        """
        # Remover valores NaN
        consumos = [c for c in consumos if pd.notna(c)]
        
        # Contar ocorrências de consumo > 0
        ocorrencias = sum(1 for c in consumos if c > 0)
        
        if ocorrencias > 0:
            return len(consumos) / ocorrencias
        else:
            return float('inf')
    
    @staticmethod
    def calcular_coeficiente_variacao(consumos):
        """
        Calcula o coeficiente de variação
        
        Args:
            consumos (list): Lista de valores de consumo
        
        Returns:
            float: Coeficiente de variação
        """
        # Remover valores NaN
        consumos = [c for c in consumos if pd.notna(c)]
        
        if not consumos or np.mean(consumos) == 0:
            return float('inf')
            
        return np.std(consumos) / np.mean(consumos)
    
    @staticmethod
    def classificar_consumo(tmd, cv):
        """
        Classifica o tipo de consumo com base no TMD e CV
        
        Args:
            tmd (float): Tempo médio entre demandas
            cv (float): Coeficiente de variação
        
        Returns:
            str: Classificação do consumo
        """
        if pd.isna(tmd) or pd.isna(cv):
            return 'Consumo Zero'
            
        # Classificação
        if tmd < 1.32:  # Consumo frequente (pelo menos 3 consumos em 4 períodos)
            if cv < 0.7:
                return 'Suave'
            else:
                return 'Errático'
        else:  # Consumo intermitente
            if cv < 0.7:
                return 'Intermitente'
            else:
                return 'Esporádico'
                
    @staticmethod
    def gerar_sugestoes(material_data):
        """
        Gera sugestões para o analista com base nos dados do material
        
        Args:
            material_data (dict): Dados do material
        
        Returns:
            dict: Dicionário com sugestões
        """
        sugestoes = []
        
        # Verificar grupo de mercadoria
        if pd.isna(material_data.get('Grupo de mercadorias')) or material_data.get('Grupo de mercadorias') == "":
            sugestoes.append("Atribuir grupo de mercadoria")
        
        # Verificar classificação e sugerir política
        classificacao = material_data.get('Classificacao')
        grupo_mrp = material_data.get('Grupo MRP')
        tipo_mrp = material_data.get('Tipo de MRP')
        recuperabilidade = 'N'  # Padrão, na prática seria determinado por outro campo
        
        politica_sugerida = AnaliseCalculos.sugerir_politica(classificacao, recuperabilidade)
        if politica_sugerida and politica_sugerida != tipo_mrp:
            sugestoes.append(f"Política: Alterar para {politica_sugerida}")
        
        # Verificar última compra
        data_ult_pedido = material_data.get('Dt. Ult. Pedido')
        if data_ult_pedido:
            # Converter para datetime se for string
            if isinstance(data_ult_pedido, str):
                try:
                    data_ult_pedido = datetime.strptime(data_ult_pedido, '%Y-%m-%dT%H:%M:%S.%fZ')
                except:
                    try:
                        data_ult_pedido = datetime.strptime(data_ult_pedido, '%Y-%m-%d')
                    except:
                        data_ult_pedido = None
            
            # Verificar se última compra foi há mais de 3 anos
            if data_ult_pedido and (datetime.now() - data_ult_pedido).days > 3*365:
                sugestoes.append("Última compra a mais de 3 anos")
        
        # Verificar alto volume
        qtd_ordem = float(material_data.get('Qtd.ordem planejada', 0))
        if qtd_ordem > active_config.ALTO_VOLUME:
            sugestoes.append("OP com alto volume, verificar parcelamento")
        
        # Verificar outliers
        # Implementar lógica de outlier quando tivermos dados suficientes
        
        # Verificar PR e MAX
        pr = float(material_data.get('Ponto reabastec.', 0))
        max_estoque = float(material_data.get('Estoque máximo', 0))
        
        # Sugerir PR e MAX com base na classificação
        if classificacao in ['Intermitente', 'Esporádico']:
            # Sugerir PR baseado em consumo dos últimos períodos
            sugestoes.append("Sugestão de PR e MAX")
            
        return {
            'sugestoes': sugestoes,
            'politica_sugerida': politica_sugerida
        }
    
    @staticmethod
    def sugerir_politica(classificacao, recuperabilidade):
        """
        Sugere a política de MRP com base na classificação e recuperabilidade
        
        Args:
            classificacao (str): Classificação do consumo
            recuperabilidade (str): Recuperabilidade do material (N/R)
        
        Returns:
            str: Política sugerida
        """
        if recuperabilidade == 'R':
            return 'ZS'  # Recuperável
            
        # Para materiais não recuperáveis (N)
        if classificacao == 'Suave':
            return 'ZP'  # Para consumo A/B sem validade e baixo volume
            
        elif classificacao == 'Intermitente':
            return 'ZM'
            
        elif classificacao == 'Errático':
            return 'ZM'  # Para médio/baixo volume
            
        elif classificacao == 'Esporádico':
            return 'ZD'  # Sem criticidade
            
        # Padrão
        return None