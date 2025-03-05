/**
 * Script para cálculos e análises no frontend
 */

// Funções para cálculos específicos
function calcularTMD(consumos) {
    // Remover valores vazios
    const valores = consumos.filter(v => v !== null && v !== undefined && v !== '');
    
    if (valores.length === 0) {
        return null;
    }
    
    // Contar valores maiores que zero
    const valoresPositivos = valores.filter(v => parseFloat(v) > 0).length;
    
    if (valoresPositivos === 0) {
        return Infinity;
    }
    
    return valores.length / valoresPositivos;
}

function calcularCoeficienteVariacao(consumos) {
    // Remover valores vazios
    const valores = consumos.filter(v => v !== null && v !== undefined && v !== '').map(parseFloat);
    
    if (valores.length === 0) {
        return null;
    }
    
    // Calcular média
    const media = valores.reduce((acc, val) => acc + val, 0) / valores.length;
    
    if (media === 0) {
        return Infinity;
    }
    
    // Calcular desvio padrão
    const variancia = valores.reduce((acc, val) => acc + Math.pow(val - media, 2), 0) / valores.length;
    const desvioPadrao = Math.sqrt(variancia);
    
    return desvioPadrao / media;
}

function classificarConsumo(tmd, cv) {
    if (tmd === null || cv === null || tmd === Infinity || cv === Infinity) {
        return 'Consumo Zero';
    }
    
    if (tmd < 1.32) {  // Consumo frequente
        if (cv < 0.7) {
            return 'Suave';
        } else {
            return 'Errático';
        }
    } else {  // Consumo intermitente
        if (cv < 0.7) {
            return 'Intermitente';
        } else {
            return 'Esporádico';
        }
    }
}

function verificarOutlier(valores, valor) {
    // Remover valores vazios
    const valoresLimpos = valores.filter(v => v !== null && v !== undefined && v !== '').map(parseFloat);
    
    if (valoresLimpos.length < 5) {
        return false;
    }
    
    // Calcular quartis
    valoresLimpos.sort((a, b) => a - b);
    
    const q1Idx = Math.floor(valoresLimpos.length * 0.25);
    const q3Idx = Math.floor(valoresLimpos.length * 0.75);
    
    const q1 = valoresLimpos[q1Idx];
    const q3 = valoresLimpos[q3Idx];
    
    const iqr = q3 - q1;
    
    // Limites para outliers
    const lowerLimit = q1 - 1.5 * iqr;
    const upperLimit = q3 + 1.5 * iqr;
    
    return valor < lowerLimit || valor > upperLimit;
}

// Funções para cálculos específicos de estoque

function calcularNivelServico(faltas, total) {
    if (total === 0) {
        return 0;
    }
    
    return 100 * (1 - (faltas / total));
}

function calcularEstoqueSeguranca(demandaMedia, leadTime, desvioLeadTime, desvioDemanda, nivelServico) {
    // Fator de segurança baseado no nível de serviço (para distribuição normal)
    const fatoresSeguranca = {
        90: 1.28,
        95: 1.64,
        99: 2.33,
        99.9: 3.09
    };
    
    // Obter fator de segurança mais próximo
    const niveisPossiveis = Object.keys(fatoresSeguranca).map(parseFloat);
    const nivelMaisProximo = niveisPossiveis.reduce((prev, curr) => {
        return (Math.abs(curr - nivelServico) < Math.abs(prev - nivelServico) ? curr : prev);
    });
    
    const fatorSeguranca = fatoresSeguranca[nivelMaisProximo];
    
    // Calcular estoque de segurança
    const varianciaLeadTime = Math.pow(desvioLeadTime, 2);
    const varianciaDemanda = Math.pow(desvioDemanda, 2);
    
    const estoqueSeguranca = fatorSeguranca * Math.sqrt(
        (leadTime * varianciaDemanda) + (Math.pow(demandaMedia, 2) * varianciaLeadTime)
    );
    
    return Math.ceil(estoqueSeguranca);
}

function calcularPontoReposicao(demandaMedia, leadTime, estoqueSeguranca) {
    return Math.ceil(demandaMedia * leadTime) + estoqueSeguranca;
}

function calcularEstoqueMaximo(pr, qtdReposicao) {
    return pr + qtdReposicao;
}

// Funções para validação de campos

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