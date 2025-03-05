import pandas as pd
import numpy as np
import json, math
from datetime import datetime, timedelta

# Função para converter DataFrame para dicionário com tratamento de NaN
def dataframe_to_dict(df):
    if df is None:
        return {}
    
    # Substituir NaN por None para serialização
    return df.replace({np.nan: None}).to_dict(orient='records')

# Função para substituir NaN em um objeto Python (dict, list, etc.)
def replace_nan_with_none(obj):
    if isinstance(obj, dict):
        return {k: replace_nan_with_none(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_nan_with_none(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(replace_nan_with_none(item) for item in obj)
    elif pd.isna(obj) or obj is np.nan:
        return None
    elif isinstance(obj, (np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.float64, np.float32)):
        return float(obj) if not np.isnan(obj) else None
    elif isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    elif isinstance(obj, np.ndarray):
        return replace_nan_with_none(obj.tolist())
    return obj

class DataProcessor:
    """
    Classe para processamento dos dados das planilhas
    """
    def __init__(self):
        self.op_data = None
        self.info_data = None
        self.consumo_data = None
        self.textos_data = None
        self.reservas_data = None
        self.movimentacao_data = None
        self.dados_processados = None
        self.materiais_analisados = []
        
        # Constantes para limpeza de dados
        self.STRING_COLUMNS = [
            'Grupo de mercadorias', 'Setor de atividade', 'Nº peça fabricante',
            'Planejador MRP', 'Grupo MRP', 'Tipo de MRP', 'Responsável',
            'Fornecedor', 'Nome'
        ]
        self.DATE_COLUMNS = [
            'Data abertura plan.', 'Dt. Ult. Pedido', 'Dt. Ult. 201',
            'Dt. Ult. Requisição'
        ]
        self.LT_COLUMNS = [f'{i} LTD' for i in range(1, 16)]
        self.DEMAND_WINDOW = 3  # Anos para janela de demanda
        
    def carregar_dados(self, file_paths):
        """
        Carrega os dados das planilhas
        
        Args:
            file_paths (dict): Dicionário com os caminhos dos arquivos
        
        Returns:
            bool: True se os dados foram carregados com sucesso, False caso contrário
        """
        try:
            # Carregar cada planilha se o caminho estiver definido
            if 'op' in file_paths and file_paths['op']:
                print(f"Carregando arquivo OP: {file_paths['op']}")
                self.op_data = pd.read_excel(file_paths['op'], 
                    usecols=["Data abertura plan.","Material","Txt.brv.material",
                            "Grupo de mercadorias","Setor de atividade","Nº peça fabricante",
                            "Planejador MRP","Grupo MRP","Tipo de MRP","Prz.entrg.prev.",
                            "Estoque total","Ponto reabastec.","Estoque máximo",
                            "Estoque de segurança","Valor total","CMM","Demanda",
                            "Demanda Med.","Preço Unit.","Qtd. RTP1","Qtd. RTP2",
                            "Qtd. RTP3","Qtd. RTP6","Sld. Virtual","Qtd.ordem planejada",
                            "Valor Total","Responsável","Criticidade","Qtd. LMR",
                            "Dem. Pro.","Dt. Ult. Pedido","Fornecedor","Nome",
                            "Dt. Ult. Requisição","Qtd. Pedido","Qtd. Requisição",
                            "Qtd. RemCG","Dt. Ult. 201","Qt. 201 - 12 Meses"])
                print(f"OP carregado com sucesso. Linhas: {len(self.op_data)}")
                
            if 'info' in file_paths and file_paths['info']:
                print(f"Carregando arquivo INFO: {file_paths['info']}")
                self.info_data = pd.read_excel(file_paths['info'],
                    thousands='.', decimal=',', 
                    usecols=['Material','Volume'])
                print(f"INFO carregado com sucesso. Linhas: {len(self.info_data)}")
                
            if 'consumo' in file_paths and file_paths['consumo']:
                print(f"Carregando arquivo CONSUMO: {file_paths['consumo']}")
                self.consumo_data = pd.read_excel(file_paths['consumo'],
                    nrows=10000, thousands='.', decimal=',',
                    usecols=['Material'] + [f'{i} LTD' for i in range(1, 16)])
                print(f"CONSUMO carregado com sucesso. Linhas: {len(self.consumo_data)}")
                
            if 'textos' in file_paths and file_paths['textos']:
                print(f"Carregando arquivo TEXTOS: {file_paths['textos']}")
                self.textos_data = pd.read_excel(file_paths['textos'],
                    usecols=['Material','Texto OBS - pt','Texto OBS - es',
                            'Texto DB - pt','Texto DB - es','Texto - pt',
                            'Texto - es','Texto REF LMR'])
                print(f"TEXTOS carregado com sucesso. Linhas: {len(self.textos_data)}")
                
            if 'reservas' in file_paths and file_paths['reservas']:
                print(f"Carregando arquivo RESERVAS: {file_paths['reservas']}")
                self.reservas_data = pd.read_excel(file_paths['reservas'],
                    usecols=['Material','Tipo de reserva','Centro custo',
                            'Data base','Nome do usuário','Cód. Localização',
                            'Descrição do Equipamento','Material','Texto',
                            'Com registro final','Item foi eliminado',
                            'Motivo da Reserva','Qtd.retirada'])
                print(f"RESERVAS carregado com sucesso. Linhas: {len(self.reservas_data)}")
                
            if 'movimentacao' in file_paths and file_paths['movimentacao']:
                print(f"Carregando arquivo MOVIMENTAÇÃO: {file_paths['movimentacao']}")
                self.movimentacao_data = pd.read_excel(file_paths['movimentacao'])
                print(f"MOVIMENTAÇÃO carregado com sucesso. Linhas: {len(self.movimentacao_data)}")
            
            print("Todos os arquivos foram carregados com sucesso")
            return True
            
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def processar_dados(self):
        """
        Processa os dados carregados
        
        Returns:
            pd.DataFrame: DataFrame com os dados processados
        """
        try:
            # Verifica se os dados foram carregados
            if self.op_data is None and self.info_data is None:
                return None
                
            # Utiliza os dados das ordens planejadas como base
            if self.op_data is not None:
                base_data = self.op_data.copy()
            else:
                base_data = self.info_data.copy()
            
            # Limpar e transformar dados
            self._limpar_dados()
            
            # Mesclar dados
            merged_data = self._merge_data()
            
            # Adicionar dados calculados
            processed_data = self._add_calculated_data(merged_data)
            
            self.dados_processados = processed_data
            self.materiais_analisados = processed_data['Material'].unique().tolist()
            
            return processed_data
            
        except Exception as e:
            print(f"Erro ao processar dados: {e}")
            return None
            
    def _limpar_dados(self):
        """
        Limpa e converte os dados para os tipos apropriados
        """
        # Converter coluna Material para string em todos os DataFrames
        if self.op_data is not None:
            self.op_data['Material'] = self.op_data['Material'].astype(str)
            
        if self.info_data is not None:
            self.info_data['Material'] = self.info_data['Material'].astype(str)
            # Limpar códigos de material
            self.info_data['Material'] = self.info_data['Material'].str.replace('.0', '')
            
        if self.consumo_data is not None:
            self.consumo_data['Material'] = self.consumo_data['Material'].astype(str)
            
        if self.textos_data is not None:
            self.textos_data['Material'] = self.textos_data['Material'].astype(str)
            
        if self.reservas_data is not None:
            self.reservas_data['Material'] = self.reservas_data['Material'].astype(str)
            # Converter datas e filtrar reservas para janela de análise
            try:
                self.reservas_data['Data base'] = pd.to_datetime(self.reservas_data['Data base'], errors='coerce')
                self.reservas_data = self.reservas_data[
                    self.reservas_data['Data base'] > datetime.now() - pd.DateOffset(years=self.DEMAND_WINDOW)
                ]
            except Exception as e:
                print(f"Erro ao processar datas de reservas: {e}")
        
        # Limpar e converter dados das ordens planejadas
        if self.op_data is not None:
            # Converter colunas para strings
            for col in self.STRING_COLUMNS:
                if col in self.op_data.columns:
                    self.op_data[col] = self.op_data[col].astype(str)
            
            # Converter colunas de data
            for col in self.DATE_COLUMNS:
                if col in self.op_data.columns:
                    try:
                        self.op_data[col] = pd.to_datetime(self.op_data[col], errors='coerce')
                    except Exception as e:
                        print(f"Erro ao converter coluna de data {col}: {e}")
        
        # Limpar e converter dados de consumo
        if self.consumo_data is not None:
            # Processar colunas de lead time
            for col in self.LT_COLUMNS:
                if col in self.consumo_data.columns:
                    # Substituir '-' por vazio
                    self.consumo_data[col] = self.consumo_data[col].replace('-', '')
                    
                    # Converter para numérico e arredondar para cima
                    try:
                        self.consumo_data[col] = pd.to_numeric(self.consumo_data[col], errors='coerce')
                        self.consumo_data[col] = np.ceil(self.consumo_data[col])
                    except Exception as e:
                        print(f"Erro ao processar coluna {col}: {e}")
        
        # Calcular volume para ordens planejadas
        if self.op_data is not None and self.info_data is not None and 'Volume' in self.info_data.columns:
            merged_temp = pd.merge(self.op_data, self.info_data[['Material', 'Volume']], on='Material', how='left')
            if 'Qtd.ordem planejada' in merged_temp.columns:
                merged_temp['Volume da OP'] = (merged_temp['Volume'] * merged_temp['Qtd.ordem planejada']).fillna(0)
                merged_temp['Volume da OP'] = merged_temp['Volume da OP'].astype(int)
                
                # Adicionar coluna calculada de volta para o DataFrame base
                self.op_data = merged_temp.copy()
    
    def _merge_data(self):
        """
        Mescla os dados das diferentes tabelas
        
        Returns:
            pd.DataFrame: DataFrame com dados mesclados
        """
        # Começar com dados das ordens planejadas ou info geral
        if self.op_data is not None:
            merged_data = self.op_data.copy()
        else:
            merged_data = self.info_data.copy()
            
        # Mesclar com info geral se os dois existirem
        if self.op_data is not None and self.info_data is not None:
            merged_data = pd.merge(
                merged_data, 
                self.info_data, 
                on='Material', 
                how='left', 
                suffixes=('', '_info')
            )
            
        # Mesclar com dados de consumo
        if self.consumo_data is not None:
            merged_data = pd.merge(
                merged_data, 
                self.consumo_data, 
                on='Material', 
                how='left',
                suffixes=('', '_consumo')
            )
            
        # Mesclar com dados de textos
        """
        if self.textos_data is not None:
            # Agrupar textos por material para casos com múltiplas linhas por material
            textos_agrupados = self.textos_data.groupby('Material').first().reset_index()
            
            merged_data = pd.merge(
                merged_data, 
                textos_agrupados, 
                on='Material', 
                how='left',
                suffixes=('', '_texto')
            )
        """
        
        if self.textos_data is not None:
            texto_cols = ['Texto OBS - pt','Texto OBS - es','Texto DB - pt',
                          'Texto DB - es','Texto - pt','Texto - es','Texto REF LMR']
            textos_agrupados = self.textos_data.groupby('Material')[texto_cols]\
                .agg(lambda x: '\n'.join(x.dropna().astype(str))).reset_index()
            merged_data = pd.merge(merged_data, textos_agrupados, on='Material', how='left', suffixes=('', '_texto'))

        return merged_data
    
    def _add_calculated_data(self, data):
        """
        Adiciona colunas calculadas ao DataFrame
        
        Args:
            data (pd.DataFrame): DataFrame com dados mesclados
        
        Returns:
            pd.DataFrame: DataFrame com colunas calculadas
        """
        df = data.copy()
        
        # Calcular tempo médio entre demandas (TMD)
        if self.consumo_data is not None:
            # Filtrar apenas colunas LTD
            ltd_cols = [col for col in self.consumo_data.columns if 'LTD' in col and col != 'Prz.entrg.prev.']
            
            if ltd_cols:
                # Calcular TMD para cada material
                tmd_dict = {}
                
                for _, row in self.consumo_data.iterrows():
                    material = row['Material']
                    consumo_vals = [row[col] for col in ltd_cols if pd.notna(row[col])]
                    
                    # Converter strings para float
                    consumo_vals = [float(str(val).strip().replace(',', '.')) if isinstance(val, str) else val 
                                    for val in consumo_vals]
                    
                    # Contar ocorrências de consumo > 0
                    consumo_count = sum(1 for val in consumo_vals if val > 0)
                    
                    # Calcular TMD
                    if consumo_count > 0:
                        tmd = len(consumo_vals) / consumo_count
                    else:
                        # Usar um valor numérico grande, mas não infinito
                        tmd = 9999.0
                        
                    tmd_dict[material] = tmd
                
                # Adicionar TMD ao DataFrame
                df['TMD'] = df['Material'].map(tmd_dict)
                
                # Calcular coeficiente de variação
                cv_dict = {}
                
                for _, row in self.consumo_data.iterrows():
                    material = row['Material']
                    consumo_vals = [row[col] for col in ltd_cols if pd.notna(row[col])]
                    
                    # Converter strings para float
                    consumo_vals = [float(str(val).strip().replace(',', '.')) if isinstance(val, str) else val 
                                    for val in consumo_vals]
                    
                    # Calcular coeficiente de variação
                    if consumo_vals and np.mean(consumo_vals) > 0:
                        cv = np.std(consumo_vals) / np.mean(consumo_vals)
                        # Limitar CV a um valor máximo de 9999 para evitar Infinity
                        cv = min(cv, 9999.0)
                    else:
                        # Usar um valor numérico grande, mas não infinito
                        cv = 9999.0
                        
                    cv_dict[material] = cv
                    
                # Adicionar coeficiente de variação ao DataFrame
                df['CV'] = df['Material'].map(cv_dict)
                
                # Classificar com base no TMD e CV
                df['Classificacao'] = df.apply(self._classificar_consumo, axis=1)
        
        return df
    
    def _classificar_consumo(self, row):
        """
        Classifica o consumo com base no TMD e Coeficiente de Variação
        
        Args:
            row (pd.Series): Linha do DataFrame
        
        Returns:
            str: Classificação do consumo
        """
        try:
            tmd = row.get('TMD', float('inf'))
            cv = row.get('CV', float('inf'))
            
            # Verificar se os valores são válidos
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
                    
        except Exception as e:
            print(f"Erro ao classificar consumo: {e}")
            return 'Indefinido'
    def obter_material(self, material_id):
        """
        Retorna os dados de um material específico
        
        Args:
            material_id (str): ID do material
        
        Returns:
            dict: Dicionário com dados do material
        """
        if self.dados_processados is None:
            return None
            
        # Filtrar dados pelo material
        material_data = self.dados_processados[self.dados_processados['Material'] == str(material_id)]
        
        if material_data.empty:
            return None
            
        # Convertendo para dicionário e tratando NaN
        result = replace_nan_with_none(material_data.iloc[0].to_dict())
        
        # Adicionar dados de reservas
        if self.reservas_data is not None:
            reservas = self.reservas_data[self.reservas_data['Material'] == str(material_id)]
            result['reservas'] = replace_nan_with_none(reservas.to_dict('records')) if not reservas.empty else []
        else:
            result['reservas'] = []
            
        # Adicionar dados de movimentação
        if self.movimentacao_data is not None:
            movimentacoes = self.movimentacao_data[self.movimentacao_data['Material'] == str(material_id)]
            result['movimentacoes'] = replace_nan_with_none(movimentacoes.to_dict('records')) if not movimentacoes.empty else []
        else:
            result['movimentacoes'] = []
            
        return result

    def obter_todos_materiais(self):
        """
        Retorna lista de todos os materiais
        
        Returns:
            list: Lista de materiais
        """
        if self.dados_processados is None:
            return []
            
        materiais = []
        for material in self.materiais_analisados:
            material_data = self.dados_processados[self.dados_processados['Material'] == material].iloc[0]
            
            # Tratando NaN antes de converter para dict
            material_dict = replace_nan_with_none({
                'Material': material,
                'Texto': material_data.get('Txt.brv.material', ''),
                'Grupo_MRP': material_data.get('Grupo MRP', ''),
                'Tipo_MRP': material_data.get('Tipo de MRP', ''),
                'Classificacao': material_data.get('Classificacao', '')
            })
            
            materiais.append(material_dict)
            
        return materiais