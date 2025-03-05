import requests
import json
from anthropic import Anthropic
from config import active_config

class LLMService:
    """
    Serviço para integração com LLM (Claude)
    """
    def __init__(self):
        self.api_key = active_config.ANTHROPIC_API_KEY
        self.client = None
        
        if self.api_key:
            self.client = Anthropic(api_key=self.api_key)
    
    def validar_textos(self, texto_pt, texto_es):
        """
        Verifica consistência entre textos em português e espanhol
        
        Args:
            texto_pt (str): Texto em português
            texto_es (str): Texto em espanhol
        
        Returns:
            dict: Resultado da validação
        """
        if not self.client:
            return {"erro": "API key não configurada"}
            
        if not texto_pt or not texto_es:
            return {"erro": "Textos não fornecidos"}
        
        prompt = f"""
        Compare os seguintes textos de descrição de material em português e espanhol:
        
        Texto em português: {texto_pt}
        Texto em espanhol: {texto_es}
        
        Verifique se:
        1. Os textos são traduções adequados um do outro
        2. Se há inconsistências técnicas entre os dois
        3. Se há termos técnicos mal traduzidos
        
        Responda em formato JSON com os seguintes campos:
        - sao_consistentes: (true/false)
        - inconsistencias: (lista de inconsistências encontradas, se houver)
        - recomendacoes: (sugestões para melhorar a consistência)
        """
        
        try:
            response = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1024,
                temperature=0,
                system="Você é um assistente especializado em analisar e verificar a consistência de descrições técnicas de materiais de engenharia e manutenção em português e espanhol.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extrair o JSON da resposta
            result = response.content[0].text
            
            # Procurar por conteúdo JSON na resposta
            try:
                # Tentar extrair apenas o JSON, caso tenha texto adicional
                import re
                json_match = re.search(r'```json\n(.*?)\n```', result, re.DOTALL)
                if json_match:
                    result = json_match.group(1)
                
                return json.loads(result)
            except:
                # Se falhar, retornar o texto bruto
                return {"resultado": result}
            
        except Exception as e:
            return {"erro": str(e)}
    
    def pesquisar_mercado(self, material_data):
        """
        Realiza pesquisa de mercado para o material
        
        Args:
            material_data (dict): Dados do material
        
        Returns:
            dict: Resultado da pesquisa
        """
        if not self.client:
            return {"erro": "API key não configurada"}
        
        texto_material = material_data.get("Txt.brv.material", "")
        grupo_mercadoria = material_data.get("Grupo de mercadorias", "")
        num_peca_fabricante = material_data.get("Nº peça fabricante", "")
        preco_estimado = material_data.get("Preço Unit.", 0)
        
        # Obter textos completos se disponíveis
        textos_completos = material_data.get("textos_completos", [])
        textos_pt = "\n".join([texto.get("Texto - pt", "") for texto in textos_completos if "Texto - pt" in texto])
        
        prompt = f"""
        Realize uma pesquisa de mercado para o seguinte material:
        
        Descrição: {texto_material}
        Grupo de mercadoria: {grupo_mercadoria}
        Número de peça do fabricante: {num_peca_fabricante}
        Preço estimado: {preco_estimado}
        
        Descrição técnica adicional:
        {textos_pt}
        
        Por favor, analise:
        
        1. Se a referência do fabricante (caso exista) atende ao descritivo
        2. Se o material está disponível no mercado
        3. Se não há referência, sugerir possíveis referências de mercado
        4. Se o preço estimado está de acordo com o mercado
        
        Responda em formato JSON com os seguintes campos:
        - referencia_atende: (true/false/null se não tiver referência)
        - disponivel_mercado: (true/false)
        - referencias_sugeridas: (lista de possíveis referências, com fabricantes)
        - preco_estimado_adequado: (true/false)
        - preco_mercado: (estimativa de preço de mercado, se disponível)
        - observacoes: (texto com observações gerais)
        """
        
        try:
            response = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1500,
                temperature=0,
                system="Você é um assistente especializado em análise de mercado para materiais de engenharia, manutenção e suprimentos industriais. Ajude a identificar referências de mercado, disponibilidade e preços estimados.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extrair o JSON da resposta
            result = response.content[0].text
            
            # Procurar por conteúdo JSON na resposta
            try:
                # Tentar extrair apenas o JSON, caso tenha texto adicional
                import re
                json_match = re.search(r'```json\n(.*?)\n```', result, re.DOTALL)
                if json_match:
                    result = json_match.group(1)
                
                return json.loads(result)
            except:
                # Se falhar, retornar o texto bruto
                return {"resultado": result}
            
        except Exception as e:
            return {"erro": str(e)}