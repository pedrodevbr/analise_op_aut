import pandas as pd
import os
from datetime import datetime

class ExportService:
    """
    Serviço para exportação de relatórios
    """
    
    @staticmethod
    def exportar_relatorio(materiais_analisados, resultados_analise):
        """
        Exporta relatório com análises dos materiais
        
        Args:
            materiais_analisados (list): Lista de materiais analisados
            resultados_analise (dict): Resultados das análises por material
        
        Returns:
            str: Caminho do arquivo exportado
        """
        # Criar diretório de exportação se não existir
        export_dir = "exports"
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
        
        # Preparar dados para exportação
        data = []
        
        for material in materiais_analisados:
            material_id = material['Material']
            analise = resultados_analise.get(material_id, {})
            
            # Extrair sugestões e pesquisa de mercado
            sugestoes = analise.get('sugestoes', [])
            sugestoes_str = "\n".join(sugestoes) if sugestoes else ""
            
            pesquisa = analise.get('pesquisa', {})
            
            # Formatar pesquisa de mercado
            pesquisa_str = ""
            if pesquisa:
                ref_atende = pesquisa.get('referencia_atende')
                if ref_atende is False:
                    pesquisa_str += "- Referência não atende texto\n"
                
                refs_sugeridas = pesquisa.get('referencias_sugeridas', [])
                if refs_sugeridas:
                    pesquisa_str += "- Referências disponíveis:\n"
                    for ref in refs_sugeridas:
                        pesquisa_str += f"  * {ref}\n"
                
                preco = pesquisa.get('preco_mercado')
                if preco:
                    pesquisa_str += f"- Preço estimado mercado: {preco}\n"
                
                obs = pesquisa.get('observacoes')
                if obs:
                    pesquisa_str += f"- Observações: {obs}\n"
            
            # Adicionar à lista de dados
            data.append({
                'Material': material_id,
                'Descrição': material.get('Texto', ''),
                'Grupo MRP': material.get('Grupo_MRP', ''),
                'Tipo MRP': material.get('Tipo_MRP', ''),
                'Classificação': material.get('Classificacao', ''),
                'Política Sugerida': analise.get('politica_sugerida', ''),
                'Sugestões': sugestoes_str,
                'Pesquisa Mercado': pesquisa_str,
                'Decisão Analista': analise.get('decisao', ''),
                'Observações Analista': analise.get('observacoes_analista', '')
            })
        
        # Criar DataFrame e exportar para Excel
        df = pd.DataFrame(data)
        
        # Nome do arquivo com timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"relatorio_analise_{timestamp}.xlsx"
        filepath = os.path.join(export_dir, filename)
        
        # Exportar para Excel
        with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Análise', index=False)
            
            # Ajustar largura das colunas
            worksheet = writer.sheets['Análise']
            for i, col in enumerate(df.columns):
                max_len = max(
                    df[col].astype(str).map(len).max(),
                    len(col)
                ) + 2
                worksheet.set_column(i, i, max_len)
        
        return filepath
    
    @staticmethod
    def gerar_template_cotacao(material_data, quantidade):
        """
        Gera um template de e-mail para cotação
        
        Args:
            material_data (dict): Dados do material
            quantidade (int): Quantidade para cotação
        
        Returns:
            str: Template de e-mail
        """
        texto_material = material_data.get('Txt.brv.material', '')
        
        template = f"""Prezado,

Favor cotar {quantidade} unidades do seguinte material 

{texto_material} 

Atenciosamente,"""
        
        return template
    
    @staticmethod
    def gerar_template_material_fracassado(material_data):
        """
        Gera um template de e-mail para material com licitação fracassada
        
        Args:
            material_data (dict): Dados do material
        
        Returns:
            str: Template de e-mail
        """
        material_id = material_data.get('Material', '')
        referencia = material_data.get('Nº peça fabricante', '')
        
        # Obter reservas
        reservas = material_data.get('reservas', [])
        reservas_str = ""
        
        for reserva in reservas:
            reserva_num = reserva.get('Nº reserva', '')
            qtd = reserva.get('Quantidade necessária total', 0)
            motivo = reserva.get('Motivo da Reserva', '')
            
            if reserva_num and qtd:
                reservas_str += f"- Reserva {reserva_num}: {qtd} unidades ({motivo})\n"
        
        template = f"""Prezados,

A referência {referencia} do código {material_id} não foi encontrada no mercado.

Favor indicar uma referência ou um fornecedor que tenha esse material disponível

Ultimas reservas: 
{reservas_str}

Atenciosamente,"""
        
        return template