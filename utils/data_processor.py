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
        
    def carregar_dados(self, file_paths, use_mock=False):
        """
        Carrega os dados das planilhas ou usa dados mockup para desenvolvimento
        
        Args:
            file_paths (dict): Dicionário com os caminhos dos arquivos
            use_mock (bool): Se True, usa dados mockup ao invés de carregar arquivos
        
        Returns:
            bool: True se os dados foram carregados com sucesso, False caso contrário
        """
        try:
            if use_mock:
                print("Usando dados mockup para desenvolvimento")
                self._carregar_dados_mockup()
                return True
                
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
            
    def _carregar_dados_mockup(self):
        """
        Cria dados mockup para desenvolvimento sem necessidade de arquivos externos
        """
        import pandas as pd
        import numpy as np
        import datetime
        
        # Mock para OP data
        self.op_data = pd.DataFrame({
            "Data abertura plan.": [datetime.datetime.now() - datetime.timedelta(days=i*30) for i in range(10)],
            "Material": [f"MAT{i:06d}" for i in range(1, 11)],
            "Txt.brv.material": [f"Material de teste {i}" for i in range(1, 11)],
            "Grupo de mercadorias": np.random.choice(['GM001', 'GM002', 'GM003'], 10),
            "Setor de atividade": np.random.choice(['SA01', 'SA02', 'SA03'], 10),
            "Nº peça fabricante": [f"PF{i:05d}" for i in range(1, 11)],
            "Planejador MRP": np.random.choice(['P001', 'P002', 'P003'], 10),
            "Grupo MRP": np.random.choice(['GMRP1', 'GMRP2'], 10),
            "Tipo de MRP": np.random.choice(['ND', 'PD', 'VB'], 10),
            "Prz.entrg.prev.": np.random.randint(1, 30, 10),
            "Estoque total": np.random.randint(0, 1000, 10),
            "Ponto reabastec.": np.random.randint(10, 100, 10),
            "Estoque máximo": np.random.randint(100, 2000, 10),
            "Estoque de segurança": np.random.randint(5, 50, 10),
            "Valor total": np.random.uniform(1000, 50000, 10),
            "CMM": np.random.randint(1, 100, 10),
            "Demanda": np.random.randint(0, 200, 10),
            "Demanda Med.": np.random.uniform(10, 150, 10),
            "Preço Unit.": np.random.uniform(10, 500, 10),
            "Qtd. RTP1": np.random.randint(0, 10, 10),
            "Qtd. RTP2": np.random.randint(0, 10, 10),
            "Qtd. RTP3": np.random.randint(0, 10, 10),
            "Qtd. RTP6": np.random.randint(0, 10, 10),
            "Sld. Virtual": np.random.randint(-50, 100, 10),
            "Qtd.ordem planejada": np.random.randint(0, 200, 10),
            "Valor Total": np.random.uniform(1000, 50000, 10),
            "Responsável": [f"RESP{i:02d}" for i in range(1, 11)],
            "Criticidade": np.random.choice(['Alta', 'Média', 'Baixa'], 10),
            "Qtd. LMR": np.random.randint(0, 50, 10),
            "Dem. Pro.": np.random.randint(0, 100, 10),
            "Dt. Ult. Pedido": [datetime.datetime.now() - datetime.timedelta(days=i*15) for i in range(10)],
            "Fornecedor": [f"FORN{i:03d}" for i in range(1, 11)],
            "Nome": [f"Fornecedor Nome {i}" for i in range(1, 11)],
            "Dt. Ult. Requisição": [datetime.datetime.now() - datetime.timedelta(days=i*7) for i in range(10)],
            "Qtd. Pedido": np.random.randint(0, 50, 10),
            "Qtd. Requisição": np.random.randint(0, 30, 10),
            "Qtd. RemCG": np.random.randint(0, 20, 10),
            "Dt. Ult. 201": [datetime.datetime.now() - datetime.timedelta(days=i*45) for i in range(10)],
            "Qt. 201 - 12 Meses": np.random.randint(0, 100, 10)
        })
        
        # Mock para INFO data
        self.info_data = pd.DataFrame({
            "Material": [f"MAT{i:06d}" for i in range(1, 11)],
            "Volume": np.random.uniform(0.1, 10, 10)
        })
        
        # Mock para CONSUMO data
        self.consumo_data = pd.DataFrame({
            "Material": [f"MAT{i:06d}" for i in range(1, 11)]
        })
        
        # Adicionar colunas LTD
        for i in range(1, 16):
            self.consumo_data[f"{i} LTD"] = np.random.randint(0, 50, 10)
        
        # Mock para TEXTOS data
        self.textos_data = pd.DataFrame({
            "Material": [f"MAT{i:06d}" for i in range(1, 11)],
            "Texto OBS - pt": [f"Observação em português {i}" for i in range(1, 11)],
            "Texto OBS - es": [f"Observación en español {i}" for i in range(1, 11)],
            "Texto DB - pt": [f"Texto DB em português {i}" for i in range(1, 11)],
            "Texto DB - es": [f"Texto DB en español {i}" for i in range(1, 11)],
            "Texto - pt": [f"Texto em português {i}" for i in range(1, 11)],
            "Texto - es": [f"Texto en español {i}" for i in range(1, 11)],
            "Texto REF LMR": [f"Referência LMR {i}" for i in range(1, 11)]
        })
        
        # Mock para RESERVAS data
        self.reservas_data = pd.DataFrame({
            "Material": np.random.choice([f"MAT{i:06d}" for i in range(1, 11)], 20),
            "Tipo de reserva": np.random.choice(['TR01', 'TR02', 'TR03'], 20),
            "Centro custo": np.random.choice(['CC001', 'CC002', 'CC003'], 20),
            "Data base": [datetime.datetime.now() - datetime.timedelta(days=i*3) for i in range(20)],
            "Nome do usuário": np.random.choice(['User01', 'User02', 'User03', 'User04'], 20),
            "Cód. Localização": np.random.choice(['LOC01', 'LOC02', 'LOC03'], 20),
            "Descrição do Equipamento": [f"Equipamento {i}" for i in range(1, 21)],
            "Texto": [f"Descrição da reserva {i}" for i in range(1, 21)],
            "Com registro final": np.random.choice([True, False], 20),
            "Item foi eliminado": np.random.choice([True, False], 20, p=[0.1, 0.9]),
            "Motivo da Reserva": [f"Motivo {i}" for i in range(1, 21)],
            "Qtd.retirada": np.random.randint(1, 10, 20)
        })
        
        # Mock para MOVIMENTAÇÃO data
        self.movimentacao_data = pd.DataFrame({
            "Material": np.random.choice([f"MAT{i:06d}" for i in range(1, 11)], 30),
            "Data Movimento": [datetime.datetime.now() - datetime.timedelta(days=i*2) for i in range(30)],
            "Tipo Movimento": np.random.choice(['Entrada', 'Saída'], 30),
            "Quantidade": np.random.randint(1, 50, 30),
            "Usuário": np.random.choice(['User01', 'User02', 'User03', 'User04'], 30),
            "Destino": [f"Destino {i}" for i in range(1, 31)]
        })
        
        print("Dados mockup criados com sucesso")
        print(f"OP mockup: {len(self.op_data)} linhas")
        print(f"INFO mockup: {len(self.info_data)} linhas")
        print(f"CONSUMO mockup: {len(self.consumo_data)} linhas")
        print(f"TEXTOS mockup: {len(self.textos_data)} linhas")
        print(f"RESERVAS mockup: {len(self.reservas_data)} linhas")
        print(f"MOVIMENTAÇÃO mockup: {len(self.movimentacao_data)} linhas")
        
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
            textos_agrupados = self.textos_data.groupby('Material')[texto_cols].agg(lambda x: '\n'.join(x.dropna().astype(str))).reset_index()
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

