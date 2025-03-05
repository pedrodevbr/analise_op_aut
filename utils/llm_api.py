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
        self.perplexity_api_key = active_config.PERPLEXITY_API_KEY
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
    
    def pesquisar_mercado(self, material_data, use_perplexity=True):
        """
        Realiza pesquisa de mercado para o material
        
        Args:
            material_data (dict): Dados do material
            use_perplexity (bool): Se True, usa a API do Perplexity ao invés do Anthropic
            
        Returns:
            dict: Resultado da pesquisa
        """
        # Verificar qual cliente está disponível
        if use_perplexity:
            if not hasattr(self, 'perplexity_api_key') or not self.perplexity_api_key:
                return {"erro": "API key do Perplexity não configurada"}
        else:
            if not self.client:  # Cliente Anthropic
                return {"erro": "API key do Anthropic não configurada"}
        
        texto_material = material_data.get("Txt.brv.material", "")
        num_peca_fabricante = material_data.get("Nº peça fabricante", "")
        preco_estimado = material_data.get("Preço Unit.", 0)
        
        # Obter textos completos se disponíveis
        textos_pt = material_data.get("Texto - pt")
        
        prompt = f"""Realize uma pesquisa de mercado para o seguinte material:
        
    Descrição: {texto_material}
    Número de peça do fabricante: {num_peca_fabricante}
    Preço estimado(USD): {preco_estimado}
    Descrição técnica adicional: {textos_pt}

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
    - observacoes: (texto com observações gerais)"""
        
        system_prompt = "Você é um assistente especializado em análise de mercado para materiais de engenharia, manutenção e suprimentos industriais. Ajude a identificar referências de mercado, disponibilidade e preços estimados. Responda sempre em formato JSON."
        
        try:
            if not use_perplexity:
                # Usando Anthropic API
                response = self.client.messages.create(
                    model="claude-3-opus-20240229",
                    max_tokens=1500,
                    temperature=0,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                
                # Extrair o JSON da resposta
                result = response.content[0].text
                
            else:
                # Usando Perplexity API
                import requests
                
                url = "https://api.perplexity.ai/chat/completions"
                payload = {
                    "model": "sonar",  # ou o modelo adequado
                    "messages": [
                        {
                            "role": "system",
                            "content": system_prompt
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "max_tokens": 1500,
                    "temperature": 0,
                    "top_p": 0.9,
                    "stream": False,
                    "response_format": None
                }
                
                headers = {
                    "Authorization": f"Bearer {self.perplexity_api_key}",
                    "Content-Type": "application/json"
                }
                
                response = requests.post(url, json=payload, headers=headers)
                response.raise_for_status()  # Lança exceção para erros HTTP
                
                response_data = response.json()
                result = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Procurar por conteúdo JSON na resposta
            try:
                # Tentar extrair apenas o JSON, caso tenha texto adicional
                import re
                import json
                
                json_match = re.search(r'```json\n(.*?)\n```', result, re.DOTALL)
                if json_match:
                    result = json_match.group(1)
                
                return json.loads(result)
            except json.JSONDecodeError:
                # Se falhar, retornar o texto bruto
                return {"resultado": result}
        
        except Exception as e:
            return {"erro": str(e), "use_perplexity": use_perplexity}