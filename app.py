from flask import Flask, render_template, request, jsonify, send_file, session, url_for
import os
import json
from werkzeug.utils import secure_filename
import pandas as pd

# Importar módulos próprios
from config import active_config
from utils.data_processor import DataProcessor
from utils.calc import AnaliseCalculos
from utils.llm_api import LLMService
from utils.export import ExportService

app = Flask(__name__)
app.config.from_object(active_config)
app.secret_key = app.config['SECRET_KEY']


# Criar diretório de uploads se não existir
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Inicializar serviços
data_processor = DataProcessor()
llm_service = LLMService()
export_service = ExportService()

# Armazenar resultados das análises
resultados_analise = {}

# Verificar extensão de arquivo permitida
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    """Rota para página inicial"""
    return render_template('index.html')

@app.route('/debug-load')
def debug_load():
    """Rota para carregar arquivos automaticamente durante a depuração"""
    file_paths = {
        'op': 'OP.XLSX',
        'info': '0053.XLSX',
        'consumo': '0130.XLSX',
        'textos': '0127.XLSX',
        'reservas': '0028.XLSX',
        'movimentacao': 'MB51.XLSX'
    }
    
    # Carregar e processar dados
    success = data_processor.carregar_dados(file_paths)
    
    if success:
        processed_data = data_processor.processar_dados()
        
        if processed_data is not None:
            return jsonify({
                'success': True, 
                'message': 'Dados carregados e processados com sucesso em modo de depuração',
                'materiais': data_processor.obter_todos_materiais()
            })
        else:
            return jsonify({'success': False, 'message': 'Erro ao processar dados'})
    else:
        return jsonify({'success': False, 'message': 'Erro ao carregar dados'})

@app.route('/upload', methods=['POST'])
def upload_files():
    """Rota para upload de arquivos"""
    if request.method == 'POST':
        file_paths = {}
        
        # Verificar cada arquivo
        for file_type in ['op', 'info', 'consumo', 'textos', 'reservas', 'movimentacao']:
            if file_type in request.files:
                file = request.files[file_type]
                
                if file and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    file_paths[file_type] = filepath
        
        # Carregar e processar dados
        success = data_processor.carregar_dados(file_paths)
        
        if success:
            processed_data = data_processor.processar_dados()
            
            if processed_data is not None:
                return jsonify({
                    'success': True, 
                    'message': 'Dados carregados e processados com sucesso',
                    'materiais': data_processor.obter_todos_materiais()
                })
            else:
                return jsonify({'success': False, 'message': 'Erro ao processar dados'})
        else:
            return jsonify({'success': False, 'message': 'Erro ao carregar dados'})
        
    return jsonify({'success': False, 'message': 'Método não permitido'})

@app.route('/material/<material_id>')
def get_material(material_id):
    """Rota para obter dados de um material"""
    material_data = data_processor.obter_material(material_id)
    
    if material_data:
        return jsonify({
            'success': True,
            'data': material_data
        })
    else:
        return jsonify({
            'success': False,
            'message': f'Material {material_id} não encontrado'
        })

@app.route('/analisar/<material_id>', methods=['GET'])
def analisar_material(material_id):
    """Rota para página de análise de material"""
    return render_template('analise.html', material_id=material_id)

@app.route('/api/sugestoes/<material_id>')
def get_sugestoes(material_id):
    """Rota para obter sugestões para um material"""
    material_data = data_processor.obter_material(material_id)
    
    if not material_data:
        return jsonify({
            'success': False,
            'message': f'Material {material_id} não encontrado'
        })
    
    # Gerar sugestões
    sugestoes = AnaliseCalculos.gerar_sugestoes(material_data)
    
    # Armazenar para relatório final
    if material_id not in resultados_analise:
        resultados_analise[material_id] = {}
    
    resultados_analise[material_id]['sugestoes'] = sugestoes.get('sugestoes', [])
    resultados_analise[material_id]['politica_sugerida'] = sugestoes.get('politica_sugerida')
    
    return jsonify({
        'success': True,
        'sugestoes': sugestoes
    })

@app.route('/api/pesquisar/<material_id>')
def pesquisar_mercado(material_id):
    """Rota para pesquisar mercado para um material usando LLM"""
    material_data = data_processor.obter_material(material_id)
    
    if not material_data:
        return jsonify({
            'success': False,
            'message': f'Material {material_id} não encontrado'
        })
    
    # Realizar pesquisa de mercado
    resultado_pesquisa = llm_service.pesquisar_mercado(material_data)
    
    # Armazenar para relatório final
    if material_id not in resultados_analise:
        resultados_analise[material_id] = {}
    
    resultados_analise[material_id]['pesquisa'] = resultado_pesquisa
    
    return jsonify({
        'success': True,
        'pesquisa': resultado_pesquisa
    })

@app.route('/api/template/<tipo>/<material_id>')
def gerar_template(tipo, material_id):
    """Rota para gerar templates de e-mail"""
    material_data = data_processor.obter_material(material_id)
    
    if not material_data:
        return jsonify({
            'success': False,
            'message': f'Material {material_id} não encontrado'
        })
    
    if tipo == 'cotacao':
        # Obter quantidade da requisição
        quantidade = request.args.get('quantidade', 1)
        template = export_service.gerar_template_cotacao(material_data, quantidade)
        
        return jsonify({
            'success': True,
            'template': template,
            'tipo': 'Cotação'
        })
        
    elif tipo == 'fracassado':
        template = export_service.gerar_template_material_fracassado(material_data)
        
        return jsonify({
            'success': True,
            'template': template,
            'tipo': 'Material Fracassado'
        })
    
    else:
        return jsonify({
            'success': False,
            'message': f'Tipo de template {tipo} não suportado'
        })

@app.route('/api/validar_textos/<material_id>')
def validar_textos(material_id):
    """Rota para validar textos em português e espanhol"""
    material_data = data_processor.obter_material(material_id)
    
    if not material_data:
        return jsonify({
            'success': False,
            'message': f'Material {material_id} não encontrado'
        })
    
    # Obter textos completos
    texto_pt = material_data.get('Texto - pt', [])
    
    if not texto_pt:
        return jsonify({
            'success': False,
            'message': 'Texto PT não encontrados para este material'
        })
    
    # Obter textos completos
    texto_es = material_data.get('Texto - es', [])
    
    if not texto_es:
        return jsonify({
            'success': False,
            'message': 'Texto ES não encontrados para este material'
        })
    
    # Obter descrições em pt e es
    texto_pt = material_data.get('Texto - pt')
    texto_es = material_data.get('Texto - es')

    # Validar textos
    resultado_validacao = llm_service.validar_textos(texto_pt, texto_es)
    
    return jsonify({
        'success': True,
        'validacao': resultado_validacao
    })

@app.route('/api/salvar_decisao/<material_id>', methods=['POST'])
def salvar_decisao(material_id):
    """Rota para salvar decisão do analista"""
    if request.method == 'POST':
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'Dados não fornecidos'
            })
        
        # Armazenar decisão
        if material_id not in resultados_analise:
            resultados_analise[material_id] = {}
        
        resultados_analise[material_id]['decisao'] = data.get('decisao')
        resultados_analise[material_id]['observacoes_analista'] = data.get('observacoes')
        
        return jsonify({
            'success': True,
            'message': 'Decisão salva com sucesso'
        })
    
    return jsonify({
        'success': False,
        'message': 'Método não permitido'
    })

@app.route('/api/download/<path:filename>')
def download_file(filename):
    """Rota para download de arquivo"""
    directory = os.path.join(app.root_path, 'exports')
    return send_file(os.path.join(directory, filename), as_attachment=True)

@app.route('/api/exportar')
def exportar_relatorio():
    """Rota para exportar relatório"""
    materiais = data_processor.obter_todos_materiais()
    
    if not materiais:
        return jsonify({
            'success': False,
            'message': 'Nenhum material para exportar'
        })
    
    # Exportar relatório
    filepath = export_service.exportar_relatorio(materiais, resultados_analise)
    
    if os.path.exists(filepath):
        filename = os.path.basename(filepath)
        download_url = url_for('download_file', filename=filename)
        
        return jsonify({
            'success': True,
            'download_url': download_url,
            'filename': filename
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Erro ao exportar relatório'
        })

@app.route('/api/proximo_material/<material_id>')
def proximo_material(material_id):
    """Rota para obter o próximo material"""
    materiais = data_processor.obter_todos_materiais()
    material_ids = [m['Material'] for m in materiais]
    
    try:
        idx = material_ids.index(material_id)
        if idx < len(material_ids) - 1:
            proximo_id = material_ids[idx + 1]
            return jsonify({
                'success': True,
                'proximo_material': proximo_id
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Este é o último material'
            })
    except ValueError:
        return jsonify({
            'success': False,
            'message': f'Material {material_id} não encontrado'
        })

@app.route('/relatorio')
def relatorio():
    """Rota para página de relatório"""
    return render_template('relatorio.html')
    
@app.route('/api/relatorio')
def get_relatorio():
    """Rota para obter dados do relatório"""
    materiais = data_processor.obter_todos_materiais()
    
    # Contar decisões
    total = len(materiais)
    repor = 0
    nao_repor = 0
    aguardando = 0
    
    for material_id in resultados_analise:
        decisao = resultados_analise[material_id].get('decisao')
        
        if decisao == 'Repor':
            repor += 1
        elif decisao == 'Não Repor':
            nao_repor += 1
        elif decisao == 'Aguardar':
            aguardando += 1
    
    # Formatar dados do relatório
    materiais_relatorio = []
    
    for material in materiais:
        material_id = material['Material']
        analise = resultados_analise.get(material_id, {})
        
        materiais_relatorio.append({
            'material': material_id,
            'descricao': material.get('Texto', ''),
            'grupoMRP': material.get('Grupo_MRP', ''),
            'tipoMRP': material.get('Tipo_MRP', ''),
            'classificacao': material.get('Classificacao', ''),
            'politicaSugerida': analise.get('politica_sugerida', ''),
            'decisao': analise.get('decisao', ''),
            'sugestoes': analise.get('sugestoes', []),
            'pesquisa': analise.get('pesquisa', {}),
            'observacoes': analise.get('observacoes_analista', '')
        })
    
    return jsonify({
        'success': True,
        'materiais': materiais_relatorio,
        'totais': {
            'total': total,
            'repor': repor,
            'naoRepor': nao_repor,
            'aguardando': aguardando
        }
    })

@app.route('/grafico-ltd/<material_id>', methods=['GET'])
def api_grafico_ltd(material_id):
    """
    Endpoint da API para obter dados do gráfico LTD para um material específico
    Lê os dados diretamente do sistema e cria um gráfico com LTDs como barras e linhas para estoque máximo e ponto de reabastecimento
    
    Args:
        material_id (str): Código do material
        
    Returns:
        dict: Resposta JSON com os dados do gráfico
    """
    try:
        app.logger.info(f"Requisição recebida para gráfico LTD do material: {material_id}")
        
        # Obter dados do material através do data_processor
        dados_material = data_processor.obter_material(material_id)
        
        if not dados_material:
            return jsonify({
                'success': False,
                'message': f'Material {material_id} não encontrado',
                'data': None
            }), 404
        
        # Extrair os valores de LTD do dicionário
        # Os LTDs estão no formato "1 LTD", "2 LTD", etc.
        ltd_keys = sorted([k for k in dados_material.keys() if k.endswith('LTD')], 
                         key=lambda x: int(x.split()[0]))  # Ordenar por número
        
        labels = [k.split()[0] for k in ltd_keys]  # Extrair apenas o número do LTD para o label
        valores = [dados_material[k] for k in ltd_keys]  # Valores dos LTDs
        
        # Obter valores fixos para as linhas
        estoque_maximo = dados_material.get("Estoque máximo", 0)
        ponto_reabastecimento = dados_material.get("Ponto reabastec.", 0)
        
        # Calcular a média dos LTDs para referência
        media_ltd = round(sum(valores) / len(valores), 2) if valores else 0
        
        # Determinar a tendência com base nos valores
        # Comparando o primeiro terço com o último terço dos valores
        if len(valores) >= 3:
            primeiro_terco = sum(valores[:len(valores)//3]) / (len(valores)//3)
            ultimo_terco = sum(valores[-len(valores)//3:]) / (len(valores)//3)
            
            if ultimo_terco > primeiro_terco * 1.1:  # 10% maior
                tendencia_texto = 'crescente'
            elif primeiro_terco > ultimo_terco * 1.1:  # 10% maior
                tendencia_texto = 'decrescente'
            else:
                tendencia_texto = 'estavel'
        else:
            tendencia_texto = 'estavel'
        
        # Criar o objeto de dados para o gráfico
        dados_grafico = {
            'labels': labels,
            'valores': valores,
            'media': media_ltd,
            'tendencia': tendencia_texto,
            'estoque_maximo': estoque_maximo,
            'ponto_reabastecimento': ponto_reabastecimento,
            'info_material': {
                'codigo': material_id,
                'descricao': dados_material.get('Material', ''),
                'fornecedor': dados_material.get('Fornecedor', ''),
                'nome_fornecedor': dados_material.get('Nome', ''),
                'grupo_mercadorias': dados_material.get('Grupo de mercadorias', ''),
                'grupo_mrp': dados_material.get('Grupo MRP', ''),
                'planejador_mrp': dados_material.get('Planejador MRP', ''),
                'estoque_total': dados_material.get('Estoque total', 0),
            }
        }
        
        app.logger.info(f"Dados do gráfico LTD gerados com sucesso para o material {material_id}")
        
        return jsonify({
            'success': True,
            'message': 'Dados do gráfico LTD gerados com sucesso',
            'data': dados_grafico
        })
        
    except Exception as e:
        import traceback
        app.logger.error(f"Erro ao gerar dados do gráfico LTD: {str(e)}")
        app.logger.error(traceback.format_exc())
        
        return jsonify({
            'success': False,
            'message': f'Erro ao processar solicitação: {str(e)}',
            'data': None
        }), 500
    
if __name__ == '__main__':
    app.run(debug=True)