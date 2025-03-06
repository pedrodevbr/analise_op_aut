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

