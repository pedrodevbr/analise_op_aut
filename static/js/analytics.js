/**
 * Script para cálculos e análises no frontend
 */

// Funções para validação de campos [Mantido o código original]
function validarCampoNumerico(valor) {
    if (valor === null || valor === undefined || valor === '') {
        return false;
    }
    
    return !isNaN(parseFloat(valor));
}

function formatarNumero(valor, decimais = 2) {
    if (valor === null || valor === undefined || valor === '') {
        return '0';
    }
    
    if (isNaN(parseFloat(valor))) {
        return '0';
    }
    
    if (valor === Infinity || valor === -Infinity) {
        return 'N/A';
    }
    
    return parseFloat(valor).toFixed(decimais);
}

// Modificações na função initLTDChart para utilizar largura total
function initLTDChart() {
    console.log("Inicializando gráfico LTD com largura total");
    
    // Verifica se o elemento do canvas existe
    const chartCanvas = document.getElementById('ltdChartCanvas');
    if (!chartCanvas) {
        console.error("Elemento ltdChartCanvas não encontrado no DOM");
        return;
    }
    
    console.log("Canvas encontrado, criando objeto Chart");
    
    // Ajustar dimensões do canvas para largura total
    const chartContainer = document.getElementById('ltdChartContainer');
    if (chartContainer) {
        // Forçar largura total
        chartContainer.style.width = '100%';
        
        // Remover qualquer largura máxima que possa estar limitando
        chartContainer.style.maxWidth = 'none';
    }
    
    try {
        // Inicializa o gráfico vazio com múltiplos tipos de dataset
        window.ltdChart = new Chart(chartCanvas, {
            type: 'bar',  // Tipo principal é barra
            data: {
                labels: [],
                datasets: [
                    // Dataset principal - barras para os LTDs
                    {
                        type: 'bar',
                        label: 'Consumo agrupado LTD',
                        data: [],
                        backgroundColor: 'rgba(67, 97, 238, 0.6)',
                        borderColor: 'rgba(67, 97, 238, 1)',
                        borderWidth: 1,
                        order: 1,
                        barPercentage: 0.8,  // Ajustar largura das barras para melhor visual
                        categoryPercentage: 0.9  // Ajustar espaçamento entre categorias
                    },
                    // Dataset para linha de PR sugerido
                    {
                        type: 'line',
                        label: 'PR sugerido',
                        data: [],
                        borderColor: '#f72585',
                        borderWidth: 2,
                        borderDash: [5, 5],
                        pointRadius: 0,
                        fill: false,
                        order: 0
                    },
                     // Dataset para linha de PR sugerido
                     {
                        type: 'line',
                        label: 'Max sugerido',
                        data: [],
                        borderColor: '#f72585',
                        borderWidth: 2,
                        borderDash: [5, 5],
                        pointRadius: 0,
                        fill: false,
                        order: 0
                    },
                    // Dataset para linha de Estoque Máximo
                    {
                        type: 'line',
                        label: 'Estoque Máximo',
                        data: [],
                        borderColor: 'rgba(255, 99, 132, 1)',
                        borderWidth: 2,
                        pointRadius: 0,
                        fill: false,
                        order: 0
                    },
                    // Dataset para linha de Ponto de Reabastecimento
                    {
                        type: 'line',
                        label: 'Ponto Reabastec.',
                        data: [],
                        borderColor: 'rgba(255, 159, 64, 1)',
                        borderWidth: 2,
                        pointRadius: 0,
                        fill: false,
                        order: 0
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                aspectRatio: 2.5,  // Proporção mais panorâmica para largura total
                plugins: {
                    legend: {
                        position: 'top',
                        align: 'center',
                        labels: {
                            boxWidth: 15,
                            padding: 10,
                            font: {
                                size: 11  // Fonte menor para a legenda
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const dataset = context.dataset;
                                const value = context.parsed.y || 0;
                                
                                if (dataset.type === 'line') {
                                    return `${dataset.label}: ${value.toFixed(1)}`;
                                }
                                
                                return `LTD ${context.label}: ${value.toFixed(1)}`;
                            }
                        }
                    },
                    title: {
                        display: true,
                        text: 'Análise de Lead Time Diário (LTD)',
                        font: {
                            size: 16
                        },
                        padding: {
                            top: 5,
                            bottom: 10
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Quantidade'
                        },
                        ticks: {
                            padding: 5
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'LTD (Período)'
                        },
                        ticks: {
                            padding: 5,
                            maxRotation: 0,  // Evitar rotação para textos longos
                            autoSkip: true,  // Pular labels se necessário
                            autoSkipPadding: 15  // Espaçamento entre labels mostrados
                        }
                    }
                },
                layout: {
                    padding: {
                        left: 5,
                        right: 10,
                        top: 0,
                        bottom: 0
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
        
        // Criar arrays com valores constantes para todos os pontos
        const numPontos = chartData.labels.length;
        const estoqueMaximoArray = Array(numPontos).fill(chartData.estoque_maximo);
        const pontoReabastecArray = Array(numPontos).fill(chartData.ponto_reabastecimento);
        
        // Atualizar datasets
        window.ltdChart.data.datasets[2].data = estoqueMaximoArray;
        window.ltdChart.data.datasets[3].data = pontoReabastecArray;
        
        // Ajustar espaçamento das barras baseado no número de pontos
        if (numPontos > 15) {
            window.ltdChart.data.datasets[0].barPercentage = 0.7;
            window.ltdChart.data.datasets[0].categoryPercentage = 0.8;
        } else if (numPontos > 10) {
            window.ltdChart.data.datasets[0].barPercentage = 0.8;
            window.ltdChart.data.datasets[0].categoryPercentage = 0.9;
        } else {
            window.ltdChart.data.datasets[0].barPercentage = 0.9;
            window.ltdChart.data.datasets[0].categoryPercentage = 0.95;
        }
        
        // Atualizar o gráfico
        window.ltdChart.update();
        console.log("Gráfico atualizado com sucesso");
        
        // Exibir informação sobre a tendência
        /*const tendenciaEl = document.getElementById('ltdTendencia');
        if (tendenciaEl) {
            let tendenciaClass = 'text-info';
            
            if (chartData.tendencia === 'crescente') {
                tendenciaClass = 'text-success';
            } else if (chartData.tendencia === 'decrescente') {
                tendenciaClass = 'text-danger';
            }
            
            tendenciaEl.className = `${tendenciaClass} fw-bold`;
            tendenciaEl.innerHTML = formatarTendencia(chartData.tendencia);
        } else {
            console.warn("Elemento ltdTendencia não encontrado");
        }*/
        
        
    } catch (error) {
        console.error("Erro ao atualizar o gráfico:", error);
    }
}

// Nova função para atualizar as informações do material
function atualizarInfoMaterial(infoMaterial) {
    // Verificar se os elementos existem antes de tentar atualizar
    const elementos = {
        'materialCodigo': infoMaterial.codigo,
        'materialDescricao': infoMaterial.descricao,
        'materialFornecedor': `${infoMaterial.fornecedor} - ${infoMaterial.nome_fornecedor}`,
        'materialGrupo': infoMaterial.grupo_mercadorias,
        'materialGrupoMRP': infoMaterial.grupo_mrp,
        'materialPlanejador': infoMaterial.planejador_mrp,
        'materialEstoqueTotal': infoMaterial.estoque_total
    };
    
    for (const [elementId, valor] of Object.entries(elementos)) {
        const elemento = document.getElementById(elementId);
        if (elemento) {
            elemento.textContent = valor || '-';
        }
    }
}

// Função revisada para carregar os dados do gráfico
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
    
    // Preservar a altura original do container para evitar redimensionamento indesejado
    const alturaOriginal = ltdChartContainer.style.height || '300px';
    
    // Ajusta a altura e define o indicador de carregamento
    ltdChartContainer.style.height = alturaOriginal;
    ltdChartContainer.innerHTML = '<div class="text-center my-4"><i class="fas fa-spinner fa-spin"></i> Carregando dados do gráfico...</div>';
    
    // Fazer requisição AJAX para obter dados do gráfico
    console.log("Enviando requisição AJAX para:", `/grafico-ltd/${materialId}`);
    
    $.ajax({
        url: `/grafico-ltd/${materialId}`,
        method: 'GET',
        dataType: 'json',
        success: function(response) {
            console.log("Resposta da API recebida:", response);
            
            if (response.success && response.data) {
                // Restaurar o container do gráfico, mantendo a altura definida
                ltdChartContainer.style.height = alturaOriginal;
                ltdChartContainer.innerHTML = '<canvas id="ltdChartCanvas"></canvas>' + 
                                            '<div id="ltdTendencia" class="text-center"></div>';
                
                // Garantir que o canvas tenha altura adequada
                const canvas = document.getElementById('ltdChartCanvas');
                if (canvas) {
                    // Ajusta a altura para dar espaço à legenda e tendência
                    canvas.style.height = 'calc(100% - 40px)';
                }
                
                // Inicializar e atualizar o gráfico
                initLTDChart();
                updateLTDChart(response.data);
                
                // Adicionar classe ao container para aplicar os estilos CSS específicos
                ltdChartContainer.classList.add('ltd-chart-fixed-height');
            } else {
                console.warn("API retornou erro ou sem dados:", response.message);
                ltdChartContainer.innerHTML = `<div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle"></i> 
                    Não foi possível carregar os dados de consumo LTD para este material.
                    <br><small>${response.message || 'Sem mensagem de erro'}</small>
                </div>`;
                // Restaurar altura para acomodar a mensagem de erro
                ltdChartContainer.style.height = 'auto';
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
            // Restaurar altura para acomodar a mensagem de erro
            ltdChartContainer.style.height = 'auto';
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
            }, 100); // Esperar 100ms para o novo material ser carregado
        };
    }

    // Adicionar manipulador para botão de atualizar, se existir
    const atualizarBtn = document.getElementById('atualizarBtn');
    if (atualizarBtn) {
        console.log("Botão 'Atualizar' encontrado, adicionando manipulador de evento");
        
        atualizarBtn.onclick = function(event) {
            const materialAtualId = document.getElementById('materialId')?.textContent?.trim();
            if (materialAtualId) {
                carregarDadosGraficoLTD(materialAtualId);
            }
        };
    }
});