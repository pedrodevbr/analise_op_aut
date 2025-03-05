/**
 * Script principal para a aplicação
 */

// Definições globais
let materiaisData = [];

// Funções para manipulação de modais
function showLoading(message = 'Processando, por favor aguarde...') {
    $('#loadingMessage').text(message);
    $('#loadingModal').modal('show');
}

function hideLoading() {
    $('#loadingModal').modal('hide');
}

function showAlert(title, message) {
    $('#alertTitle').text(title);
    $('#alertMessage').text(message);
    $('#alertModal').modal('show');
}

// Funções para carregamento de dados
$(document).ready(function() {
    // Verificar se estamos na página inicial
    if ($('#uploadForm').length > 0) {
        initUploadPage();
        
        // Carregar dados automaticamente para depuração se o parâmetro debug estiver presente
        if (window.location.search.includes('debug')) {
            carregarDadosDebug();
        }
    }
    
    // Verificar se estamos na página de análise
    if ($('#materialId').length > 0) {
        initAnalisePage();
    }
    
    // Botão de exportação
    $('#exportarBtn').on('click', exportarRelatorio);
});

function carregarDadosDebug() {
    showLoading('Carregando dados em modo de depuração...');
    
    $.ajax({
        url: '/debug-load',
        type: 'GET',
        success: function(response) {
            hideLoading();
            
            if (response.success) {
                showAlert('Sucesso', response.message);
                loadMateriais(response.materiais);
            } else {
                showAlert('Erro', response.message);
            }
        },
        error: function(xhr, status, error) {
            hideLoading();
            showAlert('Erro', 'Ocorreu um erro ao carregar os dados: ' + error);
        }
    });
}

function initUploadPage() {
    // Botão de carregamento automático para depuração
    $('#debugLoadBtn').on('click', function() {
        carregarDadosDebug();
    });
    
    // Formulário de upload
    $('#uploadForm').on('submit', function(e) {
        e.preventDefault();
        
        showLoading('Carregando e processando os dados, por favor aguarde...');
        
        const formData = new FormData(this);
        
        $.ajax({
            url: '/upload',
            type: 'POST',
            data: formData,
            contentType: false,
            processData: false,
            success: function(response) {
                hideLoading();
                
                if (response.success) {
                    showAlert('Sucesso', response.message);
                    loadMateriais(response.materiais);
                } else {
                    showAlert('Erro', response.message);
                }
            },
            error: function(xhr, status, error) {
                hideLoading();
                showAlert('Erro', 'Ocorreu um erro ao carregar os dados: ' + error);
            }
        });
    });
    
    // Filtro de materiais
    $('#filtroMaterial').on('keyup', function() {
        const filtro = $(this).val().toLowerCase();
        
        $('#materiaisTableBody tr').filter(function() {
            const material = $(this).find('td:first').text().toLowerCase();
            const descricao = $(this).find('td:nth-child(2)').text().toLowerCase();
            
            $(this).toggle(material.indexOf(filtro) > -1 || descricao.indexOf(filtro) > -1);
        });
    });
}

function loadMateriais(materiais) {
    materiaisData = materiais;
    
    // Limpar tabela
    $('#materiaisTableBody').empty();
    
    if (materiais.length === 0) {
        $('#materiaisTableBody').append(`
            <tr>
                <td colspan="6" class="text-center">Nenhum material encontrado</td>
            </tr>
        `);
        return;
    }
    
    // Preencher tabela
    materiais.forEach(function(material) {
        $('#materiaisTableBody').append(`
            <tr>
                <td>${material.Material}</td>
                <td>${material.Texto || ''}</td>
                <td>${material.Grupo_MRP || ''}</td>
                <td>${material.Tipo_MRP || ''}</td>
                <td>${material.Classificacao || ''}</td>
                <td>
                    <a href="/analisar/${material.Material}" class="btn btn-sm btn-primary">
                        <i class="fas fa-search"></i> Analisar
                    </a>
                </td>
            </tr>
        `);
    });
}

function initAnalisePage() {
    const materialId = $('#materialId').text();
    
    // Carregar dados do material
    carregarMaterial(materialId);
    
    // Botões
    $('#gerarSugestoesBtn').on('click', function() {
        gerarSugestoes(materialId);
    });
    
    $('#pesquisarMercadoBtn').on('click', function() {
        pesquisarMercado(materialId);
    });
    
    $('#validarTextoBtn').on('click', function() {
        validarTextos(materialId);
    });
    
    $('#salvarBtn').on('click', function() {
        salvarDecisao(materialId);
    });
    
    $('#proximoBtn').on('click', function() {
        proximoMaterial(materialId);
    });
    
    $('#templateCotacaoBtn').on('click', function() {
        gerarTemplateCotacao(materialId);
    });
    
    $('#templateFracassadoBtn').on('click', function() {
        gerarTemplateFracassado(materialId);
    });
    
    // Copiar template
    $('#copyTemplateBtn').on('click', function() {
        const content = $('#templateContent').val();
        
        navigator.clipboard.writeText(content)
            .then(() => {
                showAlert('Sucesso', 'Texto copiado para a área de transferência');
            })
            .catch(() => {
                // Fallback para navegadores que não suportam clipboard API
                $('#templateContent').select();
                document.execCommand('copy');
                showAlert('Sucesso', 'Texto copiado para a área de transferência');
            });
    });
}

function carregarMaterial(materialId) {
    //showLoading('Carregando dados do material...');
    
    $.ajax({
        url: `/material/${materialId}`,
        type: 'GET',
        success: function(response) {
            hideLoading();
            
            if (response.success) {
                preencherDadosMaterial(response.data);
            } else {
                showAlert('Erro', response.message);
            }
        },
        error: function(xhr, status, error) {
            hideLoading();
            showAlert('Erro', 'Ocorreu um erro ao carregar os dados: ' + error);
        }
    });
}

function preencherDadosMaterial(material) {
    // Atualizar título e descrição
    $('#materialDesc').text(material['Txt.brv.material'] || '');
    
    // Informações básicas
    $('#infoMaterial').text(material['Material'] || '');
    $('#infoGrupoMRP').text(material['Grupo MRP'] || '');
    $('#infoTipoMRP').text(material['Tipo de MRP'] || '');
    $('#infoGrupoMercadorias').text(material['Grupo de mercadorias'] || '');
    $('#infoClassificacao').text(material['Classificacao'] || '');
    
    $('#infoEstoqueTotal').text(material['Estoque total'] || '0');
    $('#infoPontoReabastec').text(material['Ponto reabastec.'] || '0');
    $('#infoEstoqueMaximo').text(material['Estoque máximo'] || '0');
    $('#infoPrecoUnit').text(material['Preço Unit.'] || '0');
    $('#infoSaldoVirtual').text(material['Sld. Virtual'] || '0');
    $('#infoQtdOrdemPlanejada').text(material['Qtd.ordem planejada'] || '0');
    
    // Textos
    if (material['Texto - pt'] && material['Texto - pt'].length > 0) {
        const textoPT = material['Texto - pt'];
        const textoES = material['Texto - es'];
        
        $('#textoPT').text(textoPT);
        $('#textoES').text(textoES);
    } else {
        $('#textoPT').text('');
        $('#textoES').text('');
    }
    
    // Reservas
    $('#reservasTableBody').empty();
    
    if (material['reservas'] && material['reservas'].length > 0) {
        material['reservas'].forEach(function(reserva) {
            $('#reservasTableBody').append(`
                <tr>
                    <td>${reserva['Nº reserva'] || ''}</td>
                    <td>${formatDate(reserva['Data base'])}</td>
                    <td>${reserva['Motivo da Reserva'] || ''}</td>
                    <td>${reserva['Quantidade necessária total'] || '0'}</td>
                </tr>
            `);
        });
    } else {
        $('#reservasTableBody').append(`
            <tr>
                <td colspan="4" class="text-center">Nenhuma reserva encontrada</td>
            </tr>
        `);
    }
}

function formatDate(dateStr) {
    if (!dateStr) return '';
    
    try {
        const date = new Date(dateStr);
        return date.toLocaleDateString('pt-BR');
    } catch (e) {
        return dateStr;
    }
}

function gerarSugestoes(materialId) {
    showLoading('Gerando sugestões...');
    
    $.ajax({
        url: `/api/sugestoes/${materialId}`,
        type: 'GET',
        success: function(response) {
            hideLoading();
            
            if (response.success) {
                exibirSugestoes(response.sugestoes);
            } else {
                showAlert('Erro', response.message);
            }
        },
        error: function(xhr, status, error) {
            hideLoading();
            showAlert('Erro', 'Ocorreu um erro ao gerar sugestões: ' + error);
        }
    });
}

function exibirSugestoes(sugestoes) {
    $('#sugestoesContainer').removeClass('d-none');
    
    // Limpar listas
    $('#sugestoesList').empty();
    
    // Preencher sugestões
    if (sugestoes.sugestoes && sugestoes.sugestoes.length > 0) {
        sugestoes.sugestoes.forEach(function(sugestao) {
            $('#sugestoesList').append(`
                <li class="list-group-item">${sugestao}</li>
            `);
        });
    } else {
        $('#sugestoesList').append(`
            <li class="list-group-item">Nenhuma sugestão encontrada</li>
        `);
    }
    
    // Política sugerida
    if (sugestoes.politica_sugerida) {
        $('#politicaSugerida').text(sugestoes.politica_sugerida);
    } else {
        $('#politicaSugerida').text('Manter política atual');
    }
}

function pesquisarMercado(materialId) {
    $('#spinnerPesquisa').removeClass('d-none');
    $('#pesquisarMercadoBtn').prop('disabled', true);
    $('#pesquisaResultado').addClass('d-none');
    
    $.ajax({
        url: `/api/pesquisar/${materialId}`,
        type: 'GET',
        success: function(response) {
            $('#spinnerPesquisa').addClass('d-none');
            $('#pesquisarMercadoBtn').prop('disabled', false);
            
            if (response.success) {
                exibirResultadoPesquisa(response.pesquisa);
            } else {
                showAlert('Erro', response.message);
            }
        },
        error: function(xhr, status, error) {
            $('#spinnerPesquisa').addClass('d-none');
            $('#pesquisarMercadoBtn').prop('disabled', false);
            showAlert('Erro', 'Ocorreu um erro na pesquisa: ' + error);
        }
    });
}

function exibirResultadoPesquisa(pesquisa) {
    if (pesquisa.erro) {
        showAlert('Erro', pesquisa.erro);
        return;
    }
    
    $('#pesquisaResultado').removeClass('d-none');
    
    // Processar resultado
    const referenciaAtende = pesquisa.referencia_atende === null ? 'N/A' : (pesquisa.referencia_atende ? 'Sim' : 'Não');
    $('#pesquisaReferenciaAtende').text(referenciaAtende);
    
    const disponivel = pesquisa.disponivel_mercado ? 'Sim' : 'Não';
    $('#pesquisaDisponivel').text(disponivel);
    
    const precoAdequado = pesquisa.preco_estimado_adequado ? 'Sim' : 'Não';
    $('#pesquisaPrecoAdequado').text(precoAdequado);
    
    $('#pesquisaPrecoMercado').text(pesquisa.preco_mercado || 'N/A');
    
    // Referências sugeridas
    $('#pesquisaReferencias').empty();
    
    if (pesquisa.referencias_sugeridas && pesquisa.referencias_sugeridas.length > 0) {
        pesquisa.referencias_sugeridas.forEach(function(referencia) {
            $('#pesquisaReferencias').append(`
                <li class="list-group-item">${referencia}</li>
            `);
        });
    } else {
        $('#pesquisaReferencias').append(`
            <li class="list-group-item">Nenhuma referência sugerida</li>
        `);
    }
    
    // Observações
    $('#pesquisaObservacoes').text(pesquisa.observacoes || '');
}

function validarTextos(materialId) {
    showLoading('Validando textos...');
    
    $.ajax({
        url: `/api/validar_textos/${materialId}`,
        type: 'GET',
        success: function(response) {
            hideLoading();
            
            if (response.success) {
                exibirResultadoValidacao(response.validacao);
            } else {
                showAlert('Erro', response.message);
            }
        },
        error: function(xhr, status, error) {
            hideLoading();
            showAlert('Erro', 'Ocorreu um erro ao validar textos: ' + error);
        }
    });
}

function exibirResultadoValidacao(validacao) {
    if (validacao.erro) {
        showAlert('Erro', validacao.erro);
        return;
    }
    
    const resultado = $('#validacaoResultado');
    resultado.removeClass('d-none alert-info alert-success alert-warning');
    
    let html = '';
    
    if (validacao.sao_consistentes) {
        resultado.addClass('alert-success');
        html += '<strong>Os textos são consistentes.</strong>';
    } else {
        resultado.addClass('alert-warning');
        html += '<strong>Há inconsistências entre os textos:</strong><br>';
        
        if (validacao.inconsistencias && validacao.inconsistencias.length > 0) {
            html += '<ul>';
            validacao.inconsistencias.forEach(function(item) {
                html += `<li>${item}</li>`;
            });
            html += '</ul>';
        }
    }
    
    if (validacao.recomendacoes && validacao.recomendacoes.length > 0) {
        html += '<strong>Recomendações:</strong><br>';
        html += '<ul>';
        validacao.recomendacoes.forEach(function(item) {
            html += `<li>${item}</li>`;
        });
        html += '</ul>';
    }
    
    resultado.html(html);
}

function salvarDecisao(materialId) {
    const decisao = $('#decisaoSelect').val();
    const observacoes = $('#observacoesTextarea').val();
    
    if (!decisao) {
        showAlert('Atenção', 'Selecione uma decisão antes de salvar');
        return;
    }
    
    showLoading('Salvando decisão...');
    
    $.ajax({
        url: `/api/salvar_decisao/${materialId}`,
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            decisao: decisao,
            observacoes: observacoes
        }),
        success: function(response) {
            hideLoading();
            
            if (response.success) {
                showAlert('Sucesso', 'Decisão salva com sucesso');
            } else {
                showAlert('Erro', response.message);
            }
        },
        error: function(xhr, status, error) {
            hideLoading();
            showAlert('Erro', 'Ocorreu um erro ao salvar decisão: ' + error);
        }
    });
}

function proximoMaterial(materialId) {
    showLoading('Carregando próximo material...');
    
    $.ajax({
        url: `/api/proximo_material/${materialId}`,
        type: 'GET',
        success: function(response) {
            hideLoading();
            
            if (response.success) {
                window.location.href = `/analisar/${response.proximo_material}`;
            } else {
                showAlert('Informação', response.message);
            }
        },
        error: function(xhr, status, error) {
            hideLoading();
            showAlert('Erro', 'Ocorreu um erro ao carregar próximo material: ' + error);
        }
    });
}

function gerarTemplateCotacao(materialId) {
    showLoading('Gerando template...');
    
    $.ajax({
        url: `/api/template/cotacao/${materialId}?quantidade=1`,
        type: 'GET',
        success: function(response) {
            hideLoading();
            
            if (response.success) {
                // Exibir template no modal
                $('#templateTitle').text('Template de Cotação');
                $('#templateContent').val(response.template);
                $('#templateModal').modal('show');
            } else {
                showAlert('Erro', response.message);
            }
        },
        error: function(xhr, status, error) {
            hideLoading();
            showAlert('Erro', 'Ocorreu um erro ao gerar template: ' + error);
        }
    });
}

function gerarTemplateFracassado(materialId) {
    showLoading('Gerando template...');
    
    $.ajax({
        url: `/api/template/fracassado/${materialId}`,
        type: 'GET',
        success: function(response) {
            hideLoading();
            
            if (response.success) {
                // Exibir template no modal
                $('#templateTitle').text('Template de Material Fracassado');
                $('#templateContent').val(response.template);
                $('#templateModal').modal('show');
            } else {
                showAlert('Erro', response.message);
            }
        },
        error: function(xhr, status, error) {
            hideLoading();
            showAlert('Erro', 'Ocorreu um erro ao gerar template: ' + error);
        }
    });
}

function exportarRelatorio() {
    showLoading('Exportando relatório...');
    
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