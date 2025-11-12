//-------------------------------------------------------------------
// Atualização do status operacional das usinas via Socket.IO
//-------------------------------------------------------------------
/*
Estrutura geral:

    1. Configura variáveis de controle
    2. Declaração das funções de execução
    3. Fluxo de execução

Passos:
    1. Carregamento inicial do status das usinas
        - initStatusUsinas()

    1. Tenta conectar ao Socket.IO, com reconexões periódicas
        - connectSocket()

    2. Se conectado, registra o listener para o evento 'status_usinas_dados'
        - registerStatusListener(socket)

    3. Solicita os dados iniciais e configura atualizações periódicas
        - requestData()

    4. Processa os dados recebidos e atualiza o DOM
        - processStatusData(data)
        - updateDOM(data_processed)
*/
//-------------------------------------------------------------------
// 1. Configurações das variáveis de controle
//-------------------------------------------------------------------
let CONT_TENT = 0;                                     // contador de tentativas
const MAX_TENTATIVAS = 50;                             // máximo de tentativas
const POLL_MS = 400;                                   // tempo de polling
const EVENTO = 'status_usinas_dados';                  // nome do evento Socket.IO
const SELECTOR = '[data-role="status-operacional"]';   // seletor do DOM
const STATUS_COLORS_MAP = {
        'sincronizado': { bg: 'bg-green-500/20', text: 'text-green-500', dot: 'bg-green-500' },
        'u.m.d': { bg: 'bg-green-600/20', text: 'text-green-600', dot: 'bg-green-600' },
        'u.p.s': { bg: 'bg-yellow-500/20', text: 'text-yellow-500', dot: 'bg-yellow-500' },
        'sincronização': { bg: 'bg-yellow-500/20', text: 'text-yellow-500', dot: 'bg-yellow-500' },
        'u.p.g.m': { bg: 'bg-orange-500/20', text: 'text-orange-500', dot: 'bg-orange-500' },
        'giro': { bg: 'bg-orange-500/20', text: 'text-orange-500', dot: 'bg-orange-500' },
        'parada': { bg: 'bg-slate-500/20', text: 'text-slate-500', dot: 'bg-slate-500' },
        'u.p.': { bg: 'bg-slate-500/20', text: 'text-slate-500', dot: 'bg-slate-500' },
        'carregando': { bg: 'bg-blue-500/20', text: 'text-blue-500', dot: 'bg-blue-500 animate-pulse' },
        'sem conexão': { bg: 'bg-red-500/20', text: 'text-red-500', dot: 'bg-red-500' }
    };                                                   // mapa de cores por status

//-------------------------------------------------------------------
// 2. Declaração das funções de execução
//-------------------------------------------------------------------
function initStatusUsinas() {
    // Função principal para inicializar o módulo de status das usinas
}

function connectSocket() {
    // Função para tentar conectar ao Socket.IO
    const POLL_MS = 400;
    const socket = window.socket;

    if (!socket) {
        if (++CONT_TENT === 1) console.log('[Status] `CONT_TENT` Aguardando Socket.IO...');
        if (CONT_TENT >= MAX_TENTATIVAS)
        return console.error('[Status] Abortado: não encontrou Socket.');
        return setTimeout(connectSocket, POLL_MS);
    }
    console.log('[Status] Socket.IO encontrado após', CONT_TENT, 'tentativas.');
    if (!window.__statusUsinasCleanupRegistered) {
        window.__statusUsinasCleanupRegistered = true;
        window.addEventListener('beforeunload', () => {
        const s = window.socket;
        if (s?.__statusUsinasInterval) clearInterval(s.__statusUsinasInterval);
        });
    }

    return socket;
}

function registerStatusListener(socket) {
    // Função para registrar o listener do evento 'status_usinas_dados'
}

function requestData() {
    // Função para solicitar os dados iniciais e configurar atualizações periódicas
}

function processStatusData(data) {
    // Função para processar os dados recebidos e atualizar o DOM
}

function updateDOM(data_processed) {
    // Função para atualizar o DOM com os dados processados
}

//-------------------------------------------------------------------
// 3. Fluxo de execução
//-------------------------------------------------------------------
initStatusUsinas();                                     // passo 1

socket_obj = connectSocket();                           // passo 2

registerStatusListener(socket_obj);                     // passo 3

data = requestData();                                   // passo 4

data_processed = processStatusData(data);               // passo 5

updateDOM(data_processed);                              // passo 6

//-------------------------------------------------------------------
// Fim
//-------------------------------------------------------------------


// Proteção contra múltiplas inicializações
if (window.__statusUsinasInitialized) {
    console.log('[Status Usinas] Já inicializado, abortando duplicação');
} else {
    window.__statusUsinasInitialized = true;
    initStatusUsinas();
}

function initStatusUsinas() {
    // Mapa de cores por tipo de descrição de status
    const STATUS_COLORS_MAP = {
        'sincronizado': { bg: 'bg-green-500/20', text: 'text-green-500', dot: 'bg-green-500' },
        'u.m.d': { bg: 'bg-green-600/20', text: 'text-green-600', dot: 'bg-green-600' },
        'u.p.s': { bg: 'bg-yellow-500/20', text: 'text-yellow-500', dot: 'bg-yellow-500' },
        'sincronização': { bg: 'bg-yellow-500/20', text: 'text-yellow-500', dot: 'bg-yellow-500' },
        'u.p.g.m': { bg: 'bg-orange-500/20', text: 'text-orange-500', dot: 'bg-orange-500' },
        'giro': { bg: 'bg-orange-500/20', text: 'text-orange-500', dot: 'bg-orange-500' },
        'parada': { bg: 'bg-slate-500/20', text: 'text-slate-500', dot: 'bg-slate-500' },
        'u.p.': { bg: 'bg-slate-500/20', text: 'text-slate-500', dot: 'bg-slate-500' },
        'carregando': { bg: 'bg-blue-500/20', text: 'text-blue-500', dot: 'bg-blue-500 animate-pulse' },
        'sem conexão': { bg: 'bg-red-500/20', text: 'text-red-500', dot: 'bg-red-500' }
    };

    function getColorByDescription(descricao) {
        if (!descricao) return STATUS_COLORS_MAP['parada'];
        
        const descLower = descricao.toLowerCase();
        
        // Verificar correspondências
        for (const [key, colors] of Object.entries(STATUS_COLORS_MAP)) {
            if (descLower.includes(key)) {
                return colors;
            }
        }
        
        return STATUS_COLORS_MAP['parada'];
    }

    function renderBadge(dispositivos) {
        if (!Array.isArray(dispositivos) || dispositivos.length === 0) {
            const colors = STATUS_COLORS_MAP['parada'];
            return `<span class="${colors.bg} ${colors.text} text-xs px-2 py-0.5 rounded inline-flex items-center gap-1">
                <span class="w-1.5 h-1.5 rounded-full ${colors.dot}"></span>Status não disponível
            </span>`;
        }
        
        // Criar badges para cada dispositivo
        return dispositivos.map(disp => {
            const nome = disp.nome || 'N/A';
            const descricao = disp.descricao || 'Status desconhecido';
            const colors = getColorByDescription(descricao);
            
            return `<span class="${colors.bg} ${colors.text} text-xs px-2 py-0.5 rounded inline-flex items-center gap-1 whitespace-nowrap">
                <span class="w-1.5 h-1.5 rounded-full ${colors.dot}"></span>${nome}: ${descricao}
            </span>`;
        }).join('');
    }

    function renderStatusDetalhes(dispositivos) {
        if (!Array.isArray(dispositivos) || dispositivos.length === 0) {
            return '<div class="text-xs text-text-muted">Status não disponível.</div>';
        }
        return dispositivos
            .map((item) => {
                const nome = item && item.nome ? item.nome : 'Dispositivo';
                const descricao = item && item.descricao ? item.descricao : 'Status não informado';
                
                // Log detalhado do texto sendo exibido
                console.log(`[Status Usinas] 📋 Exibindo: ${nome} → "${descricao}"`);
                
                return `<div class="text-xs text-text-primary"><span class="font-medium">${nome}</span><span class="text-text-muted"> - ${descricao}</span></div>`;
            })
            .join('');
    }

    function applyStatus(slug, dispositivos) {
        console.log(`[Status Usinas] Aplicando status para ${slug}...`);
        
        if (!slug) {
            console.warn('[Status Usinas] Slug não fornecido');
            return;
        }
        
        const target = document.querySelector(`[data-role="status-operacional"][data-usina-key="${slug}"]`);
        if (!target) {
            console.warn(`[Status Usinas] Elemento de status não encontrado para ${slug}`);
            return;
        }
        
        console.log(`[Status Usinas] Atualizando badges de status para ${slug}`);
        target.innerHTML = renderBadge(dispositivos);

        const detalhesTarget = document.querySelector(`[data-role="status-detalhes"][data-usina-key="${slug}"]`);
        if (detalhesTarget) {
            console.log(`[Status Usinas] Atualizando detalhes de dispositivos para ${slug}`);
            detalhesTarget.innerHTML = renderStatusDetalhes(dispositivos);
        } else {
            console.warn(`[Status Usinas] Elemento de detalhes não encontrado para ${slug}`);
        }
        
        console.log(`[Status Usinas] Status aplicado com sucesso para ${slug}`);
    }

    function handleStatusPayload(payload) {
        console.log('[Status Usinas] Dados recebidos:', payload);
        
        if (!payload || payload.success === false) {
            if (payload && payload.error) {
                console.error('[Status Usinas] Erro ao atualizar status das usinas:', payload.error);
            } else {
                console.error('[Status Usinas] Payload inválido ou sem sucesso:', payload);
            }
            return;
        }
        
        const usinas = payload.usinas || [];
        console.log(`[Status Usinas] Processando ${usinas.length} usina(s)...`);
        
        let totalDispositivos = 0;
        let statusEncontrados = new Set();
        
        usinas.forEach((item) => {
            if (!item || !item.slug) {
                console.warn('[Status Usinas] Item de usina inválido:', item);
                return;
            }
            
            const dispositivos = item.dispositivos || [];
            totalDispositivos += dispositivos.length;
            
            // Coletar todos os status encontrados
            dispositivos.forEach(disp => {
                if (disp && disp.descricao) {
                    statusEncontrados.add(disp.descricao);
                    
                    // Destacar quando encontrar o status específico
                    if (disp.descricao.includes('U.P.S.') || disp.descricao.includes('pronta para sincronização')) {
                        console.log(`[Status Usinas] 🔔 Status encontrado: "${disp.descricao}" no dispositivo ${disp.nome || 'N/A'} da usina ${item.slug}`);
                    }
                }
            });
            
            console.log(`[Status Usinas] Atualizando ${item.slug}:`, { status: item.status, dispositivos: item.dispositivos });
            applyStatus(item.slug, item.dispositivos || []);
        });
        
        console.log(`[Status Usinas] ✅ Atualização concluída: ${usinas.length} usina(s), ${totalDispositivos} dispositivo(s)`);
        console.log(`[Status Usinas] 📊 Status encontrados:`, Array.from(statusEncontrados));
    }

    let ultimaSolicitacao = 0;
    const THROTTLE_MS = 5000; // Mínimo 5 segundos entre solicitações

    function solicitarStatus(socketInstance) {
        try {
            const agora = Date.now();
            const tempoDecorrido = agora - ultimaSolicitacao;
            
            if (ultimaSolicitacao > 0 && tempoDecorrido < THROTTLE_MS) {
                console.warn(`[Status Usinas] ⚠️ Throttle ativo: aguarde ${((THROTTLE_MS - tempoDecorrido) / 1000).toFixed(1)}s antes de nova solicitação`);
                return;
            }
            
            ultimaSolicitacao = agora;
            console.log('[Status Usinas] 📤 Enviando solicitação de status das usinas...');
            socketInstance.emit('solicitar_status_usinas');
            console.log('[Status Usinas] ✅ Solicitação enviada com sucesso');
        } catch (error) {
            console.error('[Status Usinas] ❌ Erro ao solicitar status das usinas:', error);
        }
    }

    function setup() {
        let tentativas = 0;
        const MAX_TENTATIVAS = 50; // Máximo 20 segundos (50 * 400ms)

        function verificarSocket() {
            const socketInstance = window.socket;
            
            if (!socketInstance) {
                tentativas++;
                if (tentativas >= MAX_TENTATIVAS) {
                    console.error('[Status Usinas] Socket não encontrado após múltiplas tentativas. Abortando.');
                    return;
                }
                if (tentativas === 1) {
                    console.log('[Status Usinas] Aguardando Socket.IO...');
                }
                setTimeout(verificarSocket, 400);
                return;
            }

            console.log('[Status Usinas] Socket encontrado, configurando listener...');

            const possuiStatus = document.querySelector('[data-role="status-operacional"]');
            if (!possuiStatus) {
                console.warn('[Status Usinas] Elementos de status não encontrados no DOM');
                return;
            }

            console.log('[Status Usinas] Registrando handler para evento "status_usinas_dados"...');

            const handler = (payload) => {
                console.log('[Status Usinas] Evento "status_usinas_dados" recebido');
                handleStatusPayload(payload);
            };

            // Limpar handler anterior para evitar duplicação
            if (typeof socketInstance.off === 'function' && socketInstance.__statusUsinasHandler) {
                console.log('[Status Usinas] 🧹 Removendo handler anterior...');
                socketInstance.off('status_usinas_dados', socketInstance.__statusUsinasHandler);
            }

            // Limpar intervalo anterior para evitar duplicação
            if (socketInstance.__statusUsinasInterval) {
                console.log('[Status Usinas] 🧹 Limpando intervalo anterior...');
                clearInterval(socketInstance.__statusUsinasInterval);
                socketInstance.__statusUsinasInterval = null;
            }

            socketInstance.__statusUsinasHandler = handler;
            socketInstance.on('status_usinas_dados', handler);
            console.log('[Status Usinas] ✅ Handler registrado com sucesso');

            const solicitar = (tipo = 'manual') => {
                const agora = new Date().toLocaleTimeString('pt-BR');
                if (tipo === 'automatico') {
                    console.log(`[Status Usinas] ⏰ Atualização automática às ${agora}`);
                } else {
                    console.log(`[Status Usinas] 🔄 Solicitação ${tipo} às ${agora}`);
                }
                solicitarStatus(socketInstance);
            };

            // Sempre criar um novo intervalo (já limpamos o anterior acima)
            console.log('[Status Usinas] ⏱️ Configurando intervalo de 30 segundos para atualização automática');
            socketInstance.__statusUsinasInterval = setInterval(() => solicitar('automatico'), 30000);

            // Cleanup ao sair da página
            if (!window.__statusUsinasCleanupRegistered) {
                window.addEventListener('beforeunload', () => {
                    if (socketInstance.__statusUsinasInterval) {
                        console.log('[Status Usinas] 🧹 Limpando intervalo antes de sair da página...');
                        clearInterval(socketInstance.__statusUsinasInterval);
                        socketInstance.__statusUsinasInterval = null;
                    }
                });
                window.__statusUsinasCleanupRegistered = true;
            }

            if (socketInstance.connected) {
                console.log('[Status Usinas] Socket já conectado, solicitando status imediatamente');
                solicitar('inicial');
            } else {
                console.log('[Status Usinas] Socket não conectado, aguardando evento "connect"...');
                if (typeof socketInstance.once === 'function') {
                    socketInstance.once('connect', () => {
                        console.log('[Status Usinas] Socket conectado, solicitando status...');
                        solicitar('inicial');
                    });
                }
            }
        }

        verificarSocket();
    }

    console.log('[Status Usinas] Inicializando módulo statusUsinas...');
    
    if (document.readyState === 'loading') {
        console.log('[Status Usinas] Aguardando DOMContentLoaded...');
        document.addEventListener('DOMContentLoaded', setup);
    } else {
        setup();
    }
}