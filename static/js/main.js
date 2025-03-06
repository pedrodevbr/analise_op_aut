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
    $('#infoRTP1').text(material['Qtd. RTP1'] || '0');
    $('#infoRTP2').text(material['Qtd. RTP2'] || '0');
    $('#infoRTP3').text(material['Qtd. RTP3'] || '0');
    $('#infoRTP6').text(material['Qtd. RTP6'] || '0');

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
                    <td>${reserva['Nome do usuário'] || ''}</td>
                    <td>${formatDate(reserva['Data base'])}</td>
                    <td>${reserva['Motivo da Reserva'] || ''}</td>
                    <td>${reserva['Qtd.retirada'] || '0'}</td>
                    <td>${reserva['Descrição do Equipamento'] || '0'}</td>
                    
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

// Função para carregar material e seus dados associados
function carregarMaterial(materialId) {
    // Mostrar modal de carregamento
    $('#loadingModal').modal('show');
    $('#loadingMessage').text('Carregando dados do material...');
    
    // Fazer requisição AJAX para obter dados do material
    $.ajax({
        url: `/material/${materialId}`,
        method: 'GET',
        dataType: 'json',
        success: function(response) {
            if (response.success) {
                // Preencher os dados do material na interface
                preencherDadosMaterial(response.data);
                
                // Carregar o gráfico LTD
                carregarDadosGraficoLTD(materialId);
                
                // Esconder modal de carregamento
                $('#loadingModal').modal('hide');
            } else {
                // Mostrar erro
                $('#loadingModal').modal('hide');
                mostrarAlerta('Erro', response.message || 'Erro ao carregar dados do material');
            }
        },
        error: function() {
            $('#loadingModal').modal('hide');
            mostrarAlerta('Erro', 'Falha na comunicação com o servidor');
        }
    });
}

// Função revisada para inicializar o gráfico LTD com log de debug
function initLTDChart() {
    console.log("Inicializando gráfico LTD");
    
    // Verifica se o elemento do canvas existe
    const chartCanvas = document.getElementById('ltdChartCanvas');
    if (!chartCanvas) {
        console.error("Elemento ltdChartCanvas não encontrado no DOM");
        return;
    }
    
    console.log("Canvas encontrado, criando objeto Chart");
    
    try {
        // Inicializa o gráfico vazio
        window.ltdChart = new Chart(chartCanvas, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Consumo LTD',
                    data: [],
                    borderColor: '#4361ee',
                    backgroundColor: 'rgba(67, 97, 238, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.3
                }, {
                    label: 'Média',
                    data: [],
                    borderColor: '#f72585',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    pointRadius: 0,
                    fill: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Quantidade'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Período'
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'top'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.dataset.label + ': ' + context.raw.toFixed(2);
                            }
                        }
                    }
                }
            }
        });
        console.log("Gráfico inicializado com sucesso");
    } catch (error) {
        console.error("Erro ao inicializar o gráfico:", error);
    }
}

// Função revisada para atualizar o gráfico LTD com dados de um material
function updateLTDChart(chartData) {
    console.log("Atualizando gráfico LTD com dados:", chartData);
    
    if (!window.ltdChart) {
        console.error("Objeto ltdChart não está inicializado");
        return;
    }
    
    if (!chartData) {
        console.error("Dados do gráfico não fornecidos");
        return;
    }
    
    try {
        // Atualizar labels e dados do gráfico
        window.ltdChart.data.labels = chartData.labels;
        window.ltdChart.data.datasets[0].data = chartData.valores;
        
        // Criar array com a média para todos os pontos
        const mediaArray = chartData.labels.map(() => chartData.media);
        window.ltdChart.data.datasets[1].data = mediaArray;
        
        // Atualizar o gráfico
        window.ltdChart.update();
        console.log("Gráfico atualizado com sucesso");
        
        // Exibir informação sobre a tendência
        const tendenciaEl = document.getElementById('ltdTendencia');
        if (tendenciaEl) {
            let tendenciaClass = 'text-info';
            let tendenciaIcon = 'fa-equals';
            
            if (chartData.tendencia === 'crescente') {
                tendenciaClass = 'text-success';
                tendenciaIcon = 'fa-arrow-trend-up';
            } else if (chartData.tendencia === 'decrescente') {
                tendenciaClass = 'text-danger';
                tendenciaIcon = 'fa-arrow-trend-down';
            }
            
            tendenciaEl.className = tendenciaClass;
            tendenciaEl.innerHTML = `<i class="fas ${tendenciaIcon}"></i> Tendência: ${chartData.tendencia.charAt(0).toUpperCase() + chartData.tendencia.slice(1)}`;
        } else {
            console.warn("Elemento ltdTendencia não encontrado");
        }
    } catch (error) {
        console.error("Erro ao atualizar o gráfico:", error);
    }
}

// Código revisado para carregar os dados do gráfico quando um material é selecionado
function carregarDadosGraficoLTD(materialId) {
    console.log("Carregando dados do gráfico LTD para material:", materialId);
    
    if (!materialId) {
        console.error("ID do material não fornecido");
        return;
    }
    
    // Mostrar indicador de carregamento
    const ltdChartContainer = document.getElementById('ltdChartContainer');
    if (!ltdChartContainer) {
        console.error("Container do gráfico LTD não encontrado");
        return;
    }
    
    ltdChartContainer.innerHTML = '<div class="text-center my-4"><i class="fas fa-spinner fa-spin"></i> Carregando dados do gráfico...</div>';
    
    // Fazer requisição AJAX para obter dados do gráfico
    console.log("Enviando requisição AJAX para:", `/api/grafico-ltd/${materialId}`);
    
    $.ajax({
        url: `/api/grafico-ltd/${materialId}`,
        method: 'GET',
        dataType: 'json',
        success: function(response) {
            console.log("Resposta da API recebida:", response);
            
            if (response.success && response.data) {
                // Restaurar o container do gráfico
                ltdChartContainer.innerHTML = '<canvas id="ltdChartCanvas" style="height: 300px;"></canvas><div id="ltdTendencia" class="text-center mt-2"></div>';
                
                // Inicializar e atualizar o gráfico
                initLTDChart();
                updateLTDChart(response.data);
            } else {
                console.warn("API retornou erro ou sem dados:", response.message);
                ltdChartContainer.innerHTML = `<div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle"></i> 
                    Não foi possível carregar os dados de consumo LTD para este material.
                    <br><small>${response.message || 'Sem mensagem de erro'}</small>
                </div>`;
            }
        },
        error: function(xhr, status, error) {
            console.error("Erro na requisição AJAX:", error);
            console.error("Status:", status);
            console.error("Resposta:", xhr.responseText);
            
            ltdChartContainer.innerHTML = `<div class="alert alert-danger">
                <i class="fas fa-times-circle"></i> 
                Erro ao carregar dados do gráfico. Tente novamente mais tarde.
                <br><small>Erro: ${error}</small>
            </div>`;
        }
    });
}

// Garantir que a função de carregamento seja chamada quando o documento estiver pronto
$(document).ready(function() {
    console.log("Document ready, configurando eventos para o gráfico LTD");
    
    // Obter o ID do material atual da página
    const materialId = document.getElementById('materialId')?.textContent?.trim();
    console.log("Material ID atual:", materialId);
    
    if (materialId) {
        // Carregar dados do gráfico para o material atual
        carregarDadosGraficoLTD(materialId);
    } else {
        console.warn("ID do material não encontrado na página");
    }
    
    // Certificar-se de que o carregamento do gráfico seja chamado quando um novo material for carregado
    // Isso depende de como sua aplicação carrega novos materiais
    const proximoBtn = document.getElementById('proximoBtn');
    if (proximoBtn) {
        console.log("Botão 'Próximo' encontrado, adicionando manipulador de evento");
        
        // Preservar qualquer manipulador de evento existente
        const originalOnClick = proximoBtn.onclick;
        
        proximoBtn.onclick = function(event) {
            // Chamar o manipulador original primeiro (se existir)
            if (originalOnClick) {
                originalOnClick.call(this, event);
            }
            
            // Depois que o novo material for carregado, buscaremos seu ID e carregaremos o gráfico
            setTimeout(function() {
                const novoMaterialId = document.getElementById('materialId')?.textContent?.trim();
                console.log("Novo material carregado:", novoMaterialId);
                
                if (novoMaterialId) {
                    carregarDadosGraficoLTD(novoMaterialId);
                }
            }, 100); // Esperar 1 segundo para o novo material ser carregado
        };
    }
});