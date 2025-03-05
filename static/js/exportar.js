/**
 * Script para exportação de relatórios
 */

// Função para exportar para Excel
function exportarExcel() {
    showLoading('Gerando arquivo Excel...');
    
    // Chamar API para exportar relatório
    $.ajax({
        url: '/api/exportar',
        type: 'GET',
        success: function(response) {
            hideLoading();
            
            if (response.success) {
                // Iniciar download
                window.location.href = response.download_url;
                showAlert('Sucesso', `Relatório '${response.filename}' exportado com sucesso!`);
            } else {
                showAlert('Erro', response.message);
            }
        },
        error: function(xhr, status, error) {
            hideLoading();
            showAlert('Erro', 'Ocorreu um erro ao exportar relatório: ' + error);
        }
    });
}

// Função para mostrar/esconder o modal de carregamento
function showLoading(message) {
    $('#loadingMessage').text(message);
    $('#loadingModal').modal('show');
}

function hideLoading() {
    $('#loadingModal').modal('hide');
}

// Função para mostrar alertas
function showAlert(title, message) {
    alert(`${title}: ${message}`);
}

// Adicionar rota para página de relatório no app.py
function adicionarRotaRelatorio() {
    /*
    Esta função é apenas um lembrete para adicionar as seguintes rotas no app.py:
    
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
    */
}