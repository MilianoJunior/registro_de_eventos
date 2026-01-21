
// Usando um IIFE (Immediately Invoked Function Expression) para criar um escopo privado
// e evitar poluir o escopo global.
(function () {
    // Proteção contra múltiplas inicializações
    if (window.__statusUsinasInitialized) return;
    window.__statusUsinasInitialized = true;

    const StatusUsinasModule = {
        // --- Configuração Centralizada ---
        config: {
            maxSocketRetries: 50,
            socketRetryIntervalMs: 400,
            throttleMs: 5000,
            autoRequestIntervalMs: 30000,
            statusColorsMap: {
                'us (sincronizado)': { bg: 'bg-green-500/20', text: 'text-green-500', dot: 'bg-green-500' },
                'umd (marcha desexcitada)': { bg: 'bg-teal-500/20', text: 'text-teal-500', dot: 'bg-teal-500' },
                'ups (pronta para sincronização)': { bg: 'bg-yellow-500/20', text: 'text-yellow-500', dot: 'bg-yellow-500' },
                'upgm (pronta para giro mecânico)': { bg: 'bg-orange-500/20', text: 'text-orange-500', dot: 'bg-orange-500' },
                'up (parada)': { bg: 'bg-slate-500/20', text: 'text-slate-500', dot: 'bg-slate-500' },
                'sem conexão': { bg: 'bg-red-500/20', text: 'text-red-500', dot: 'bg-red-500' },
                'status indeterminado': { bg: 'bg-gray-500/20', text: 'text-gray-500', dot: 'bg-gray-500' },
                'carregando': { bg: 'bg-blue-500/20', text: 'text-blue-500', dot: 'bg-blue-500 animate-pulse' },
                'manutenção (parada)': { bg: 'bg-purple-500/20', text: 'text-purple-500', dot: 'bg-purple-500' },
                'restrição da concessionária (parada)': { bg: 'bg-pink-500/20', text: 'text-pink-500', dot: 'bg-pink-500' },
            }
        },

        // --- Estado do Módulo ---
        state: {
            socket: null,
            lastRequestTime: 0,
            autoRequestIntervalId: null,
            potenciaPorUsina: {},
            temperaturasPorChave: new Map(),
        },

        // --- Métodos Principais ---
        init() {
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => this.tryConnectSocket());
            } else {
                this.tryConnectSocket();
            }
            this._carregarTemperaturasIniciais();
        },

        tryConnectSocket(retries = 0) {
            if (window.socket) {
                this.state.socket = window.socket;
                this.setupListeners();
                // Solicita dados iniciais na conexão ou se já estiver conectado
                if (this.state.socket.connected) {
                    this.requestStatusUpdate('inicial');
                } else {
                    this.state.socket.once('connect', () => this.requestStatusUpdate('conexão'));
                }
            } else if (retries < this.config.maxSocketRetries) {
                setTimeout(() => this.tryConnectSocket(retries + 1), this.config.socketRetryIntervalMs);
            } else {
                console.error('[Status Usinas] Socket não encontrado. Abortando.');
            }
        },

        setupListeners() {
            // Verifica se há algo na página que precisa de dados para decidir se registra o listener
            // (Status ou Temperaturas)
            const hasStatus = document.querySelector('[data-role="status-operacional"]');
            const hasTemps = document.querySelector('.temp-grid-container');

            if (!hasStatus && !hasTemps) return;

            // Limpa listeners e intervalos antigos para evitar duplicação
            if (this.state.socket.off) this.state.socket.off('status_usinas_dados');
            if (this.state.autoRequestIntervalId) clearInterval(this.state.autoRequestIntervalId);

            console.log('[Status Usinas] 🎧 Registrando listener para evento "status_usinas_dados"...');
            this.state.socket.on('status_usinas_dados', (payload) => {
                console.log('[Status Usinas] 📥 Evento "status_usinas_dados" RECEBIDO!', payload);
                try { localStorage.setItem('temperaturas_payload', JSON.stringify(payload)); } catch { }
                this.handleStatusPayload(payload);
            });
            console.log('[Status Usinas] ✅ Listener registrado com sucesso!');
            this.state.autoRequestIntervalId = setInterval(() => this.requestStatusUpdate('automático'), this.config.autoRequestIntervalMs);

            // Cleanup ao sair da página
            window.addEventListener('beforeunload', () => {
                if (this.state.autoRequestIntervalId) clearInterval(this.state.autoRequestIntervalId);
            });
        },

        handleStatusPayload(payload) {
            if (!payload || !payload.success) {
                console.error('[Status Usinas] Erro ao receber dados:', payload?.error || 'Payload inválido');
                return;
            }
            (payload.usinas || []).forEach(usina => {
                if (!usina || !usina.slug) return;

                const dispositivosDict = usina.dispositivos || {};
                this.updateDOMForUsina(usina.slug, dispositivosDict);
            });
            this._atualizarTemperaturas(payload);
        },

        updateDOMForUsina(slug, dispositivosDict) {
            const dispositivosArr = dispositivosDict
                ? Object.values(dispositivosDict)
                : [];

            const statusTarget = document.querySelector(`[data-role="status-operacional"][data-usina-key="${slug}"]`);
            if (statusTarget) {
                statusTarget.innerHTML = '';
                const badges = this._renderStatusBadges(dispositivosArr, slug);
                badges.forEach(badge => statusTarget.appendChild(badge));
            }

            const potenciaTarget = document.querySelector(`[data-role="potencia-operacional"][data-usina-key="${slug}"]`);
            if (potenciaTarget) {
                potenciaTarget.innerHTML = '';
                const badges = this._renderPotenciaBadges(dispositivosArr);
                badges.forEach(badge => potenciaTarget.appendChild(badge));
            }

            this.state.potenciaPorUsina[slug] = this._somarPotenciaDispositivos(dispositivosDict);
            this._atualizarCardPotenciaTotal();
        },

        // --- Temperaturas (UI dinâmica via Socket) ---
        _atualizarTemperaturas(payload) {
            const container = document.querySelector('.temp-grid-container');
            if (!container) return;
            const sensores = this._extrairTemperaturas(payload);
            if (sensores.length === 0) return;

            sensores.sort((a, b) => (b.risco || 0) - (a.risco || 0));

            sensores.forEach(s => {
                // Tenta encontrar card existente pelo ID
                // O seletor precisa escapar caracteres especiais se houver
                // Mas como usamos slugify ou nome direto, vamos tentar pelo atributo
                let card = container.querySelector(`[data-sensor-key="${CSS.escape(s.nome)}"]`);

                if (card) {
                    this._updateCard(card, s);
                } else {
                    const newCard = this._createCard(s);
                    if (newCard) container.appendChild(newCard);
                }
            });
        },

        _carregarTemperaturasIniciais() {
            const container = document.querySelector('.temp-grid-container');
            if (!container) return;
            const raw = container.getAttribute('data-temperaturas');
            if (!raw) return;
            let lista = [];
            try {
                lista = JSON.parse(raw) || [];
            } catch {
                return;
            }
            lista.forEach((item) => {
                const nome = item?.nome;
                if (!nome) return;
                const historico = this._normalizarHistorico(item.historico || {});
                this.state.temperaturasPorChave.set(nome, {
                    nome,
                    historico,
                    atual: Number(item.atual ?? 0),
                    alarme: Number(item.alarme ?? 0),
                    trip: Number(item.trip ?? 0),
                    risco: Number(item.risco ?? 0),
                });
            });
            // Ordenação inicial
            /*
            O render já vem ordenado do servidor ?
            Se sim, não precisamos reordenar agora para não mudar a ordem visual
            Se não, talvez seria bom. Mas no load inicial é melhor respeitar o HTML.
            As atualizações subsequentes usarão o sort do JS.
            */
            const sensores = Array.from(this.state.temperaturasPorChave.values());
            if (sensores.length === 0) return;
        },

        _normalizarHistorico(historicoDict) {
            const lista = Object.entries(historicoDict || {}).map(([hora, val]) => ({
                hora,
                val: Number(val ?? 0),
            }));
            return lista.slice(-10);
        },

        _extrairTemperaturas(payload) {
            if (!payload || !payload.usinas) {
                return Array.from(this.state.temperaturasPorChave.values());
            }
            const agora = new Date((payload.timestamp || Date.now() / 1000) * 1000);
            const hora = agora.toTimeString().slice(0, 5);
            const lista = [];
            (payload.usinas || []).forEach((usina) => {
                const dispositivos = usina.dispositivos || {};
                Object.values(dispositivos).forEach((disp) => {
                    const temps = (disp || {}).temperaturas || {};
                    const agrupado = {};
                    Object.entries(temps).forEach(([k, v]) => {
                        if (k.endsWith(' value')) {
                            const nome = k.slice(0, -6);
                            agrupado[nome] = agrupado[nome] || {};
                            agrupado[nome].value = v;
                        } else if (k.endsWith(' trip')) {
                            const nome = k.slice(0, -5);
                            agrupado[nome] = agrupado[nome] || {};
                            agrupado[nome].trip = v;
                        } else if (k.endsWith(' alarmes')) {
                            const nome = k.slice(0, -8);
                            agrupado[nome] = agrupado[nome] || {};
                            agrupado[nome].alarme = v;
                        }
                    });

                    Object.entries(agrupado).forEach(([sensor, vals]) => {
                        const chave = `${usina.nome} ${disp.nome} - ${sensor}`;
                        const atual = Number(vals.value ?? 0);
                        const trip = Number(vals.trip ?? 0);
                        const alarme = Number(vals.alarme ?? 0);
                        const risco = trip > 0 ? atual / trip : 0;

                        const cache = this.state.temperaturasPorChave.get(chave) || { nome: chave, historico: [] };
                        const historico = Array.isArray(cache.historico) ? cache.historico : [];
                        const ultimo = historico[historico.length - 1];
                        if (ultimo && ultimo.hora === hora) {
                            ultimo.val = atual;
                        } else {
                            historico.push({ hora, val: atual });
                        }
                        while (historico.length > 10) historico.shift();
                        this.state.temperaturasPorChave.set(chave, {
                            nome: chave,
                            historico,
                            atual,
                            alarme,
                            trip,
                            risco,
                        });

                        lista.push(this.state.temperaturasPorChave.get(chave));
                    });
                });
            });
            return lista.filter(Boolean);
        },

        _createCard(sensor) {
            const template = document.getElementById('template-card-temperatura');
            if (!template) return null;

            const clone = template.content.cloneNode(true);
            const card = clone.querySelector('.new-temp-card');
            if (!card) return null;

            // Set Identity
            card.dataset.sensorKey = sensor.nome;

            // Populate initial data
            this._updateCard(card, sensor);

            return clone; // Returns fragment
        },

        _updateCard(card, sensor) {
            // Calculation Logic (Reused)
            const trip = sensor.trip || 100;
            const riscoPct = (sensor.risco || 0) * 100;
            const isRiscoAlto = riscoPct > 80;
            const isRiscoMedio = riscoPct > 50 && riscoPct <= 80;

            let statusClass = 'bg-success';
            let statusTextClass = 'text-success';
            if (isRiscoAlto) { statusClass = 'bg-danger'; statusTextClass = 'text-danger'; }
            else if (isRiscoMedio) { statusClass = 'bg-warning'; statusTextClass = 'text-warning'; }

            // 1. Text Fields
            const setContent = (slot, val) => {
                const el = card.querySelector(`[data-slot="${slot}"]`);
                if (el) el.textContent = val;
            };

            const titleEl = card.querySelector('[data-slot="title"]');
            if (titleEl) {
                titleEl.textContent = sensor.nome;
                titleEl.title = sensor.nome;
            }

            setContent('val-atual', (sensor.atual || 0).toFixed(2));
            setContent('val-alarme', (sensor.alarme || 0).toFixed(2) + ' °C');
            setContent('val-trip', (sensor.trip || 0).toFixed(2) + ' °C');
            setContent('val-risco', riscoPct.toFixed(2) + ' %');

            // 2. Classes (Colors)
            const dot = card.querySelector('[data-slot="status-dot"]');
            if (dot) dot.className = `new-temp-status-dot ${statusClass}`;

            const valAtualEl = card.querySelector('[data-slot="val-atual"]');
            if (valAtualEl) valAtualEl.className = `new-temp-stat-main-value ${statusTextClass}`;

            const valRiscoEl = card.querySelector('[data-slot="val-risco"]');
            if (valRiscoEl) valRiscoEl.className = `new-temp-stat-value font-bold ${statusTextClass}`;

            // 3. Chart Bars
            const chartContainer = card.querySelector('[data-slot="chart-container"]');
            const barTemplate = document.getElementById('template-card-temperatura-bar');
            const historico = sensor.historico || [];

            if (chartContainer && barTemplate) {
                // Update existing bars or create new ones
                const existingBars = chartContainer.querySelectorAll('.new-temp-bar-wrapper');

                // Se não tiver dados, mostra mensagem
                if (historico.length === 0) {
                    chartContainer.innerHTML = '<div style="position:absolute;width:100%;text-align:center;color:var(--color-text-muted);font-size:0.7rem;top:50%;transform:translateY(-50%);">Sem dados</div>';
                    chartContainer.style.position = 'relative';
                    setContent('start-time', '--:--');
                    setContent('end-time', '--:--');
                    return;
                }

                // Se tinha mensagem "Sem dados", limpa
                if (existingBars.length === 0 && chartContainer.textContent.includes('Sem dados')) {
                    chartContainer.innerHTML = '';
                    chartContainer.style.position = '';
                }

                // Sync bars count
                const diff = historico.length - existingBars.length;

                if (diff > 0) {
                    for (let i = 0; i < diff; i++) {
                        const barClone = barTemplate.content.cloneNode(true);
                        chartContainer.appendChild(barClone);
                    }
                } else if (diff < 0) {
                    // Remove excess
                    for (let i = 0; i < Math.abs(diff); i++) {
                        if (chartContainer.lastElementChild) chartContainer.removeChild(chartContainer.lastElementChild);
                    }
                }

                // Update each bar
                const currentBars = chartContainer.querySelectorAll('.new-temp-bar-wrapper');
                historico.forEach((item, idx) => {
                    const wrapper = currentBars[idx];
                    if (!wrapper) return;

                    const val = Number(item.val);
                    // Escala fixa 0 a 120 (igual Jinja)
                    const pct = (val / 120) * 100;
                    const pctClamped = pct > 100 ? 100 : pct;

                    wrapper.title = `${val.toFixed(2)}°C às ${item.hora}`;
                    const bars = wrapper.querySelectorAll('.new-temp-bar');

                    bars.forEach(b => {
                        const baseClass = b.classList.contains('new-temp-bar-bg-layer') ? 'new-temp-bar-bg-layer' : 'new-temp-bar-main-layer';
                        b.className = `new-temp-bar ${baseClass} ${statusClass}`;
                        b.style.height = `${pctClamped}%`;

                        // Clean up old styles
                        b.style.opacity = '';
                        b.style.position = '';
                        b.style.bottom = '';
                        b.style.width = '';
                        b.style.zIndex = '';
                    });
                });

                // Update Times (Troncando para HH:MM)
                setContent('start-time', historico[0].hora.slice(0, 5));
                setContent('end-time', historico[historico.length - 1].hora.slice(0, 5));
            }
        },

        requestStatusUpdate(type = 'manual') {
            const now = Date.now();
            if (now - this.state.lastRequestTime < this.config.throttleMs) {
                console.warn(`[Status Usinas] Throttle: solicitação (${type}) ignorada.`);
                return;
            }
            this.state.lastRequestTime = now;
            console.log(`[Status Usinas] 📤 Emitindo evento "solicitar_status_usinas" (tipo: ${type})...`);

            this.state.socket.emit('solicitar_status_usinas');
            console.log('[Status Usinas] ✅ Evento "solicitar_status_usinas" emitido!');
        },

        // --- Métodos de Renderização (Helpers) ---
        _renderStatusBadges(dispositivos, usinaSlug) {
            const template = document.getElementById('template-status-badge');
            if (!template) return [];

            // Fallback se não houver dispositivos
            if (!dispositivos || dispositivos.length === 0) {
                const fallbackColors = this._getColorByStatus('parada');
                const clone = template.content.cloneNode(true);
                const span = clone.querySelector('span'); // root span

                // Adicionar classes de cor
                // Nota: fallbackColors traz strings completas 'bg-...' mas precisamos cuidar pra não sobrescrever
                span.className = `${fallbackColors.bg} ${fallbackColors.text} text-xs px-2 py-0.5 rounded inline-flex items-center gap-1 whitespace-nowrap transition-all`;

                clone.querySelector('.rounded-full').className = `w-1.5 h-1.5 rounded-full ${fallbackColors.dot}`;
                clone.querySelector('[data-slot="text"]').textContent = 'Indisponível';
                return [clone];
            }

            return dispositivos.map(disp => {
                const clone = template.content.cloneNode(true);

                const nome = disp.nome || 'N/A';
                const descricao = disp.descricao || 'Desconhecido';
                const colors = this._getColorByStatus(descricao);
                const deviceName = disp.nome || '';

                const descLower = descricao.toLowerCase().trim();
                const isEditable = ['up (parada)', 'manutenção (parada)', 'restrição da concessionária (parada)'].includes(descLower);

                const rootSpan = clone.querySelector('span'); // root
                rootSpan.className = `${colors.bg} ${colors.text} text-xs px-2 py-0.5 rounded inline-flex items-center gap-1 whitespace-nowrap transition-all`;

                if (isEditable) {
                    rootSpan.classList.add('cursor-pointer', 'hover:ring-1', 'hover:ring-current');
                    rootSpan.onclick = (event) => {
                        event.preventDefault();
                        event.stopPropagation();
                        this.openStatusModal(usinaSlug, deviceName, descricao);
                    };
                    rootSpan.title = 'Clique para alterar motivo da parada';
                    const icon = clone.querySelector('[data-slot="icon"]');
                    if (icon) icon.classList.remove('hidden');
                }

                clone.querySelector('.rounded-full').className = `w-1.5 h-1.5 rounded-full ${colors.dot}`;
                clone.querySelector('[data-slot="text"]').textContent = `${nome}: ${descricao}`;

                return clone; // Returns DocumentFragment
            }).map(frag => frag.firstElementChild); // Extract element
        },

        _renderPotenciaBadges(dispositivos) {
            const template = document.getElementById('template-potencia-badge');
            if (!template) {
                const sp = document.createElement('span');
                sp.className = "text-text-muted";
                sp.textContent = "N/A";
                return [sp];
            }

            if (!dispositivos || dispositivos.length === 0) {
                const sp = document.createElement('span');
                sp.className = "text-text-muted";
                sp.textContent = "N/A";
                return [sp];
            }

            return dispositivos
                .sort((a, b) => (a?.nome || '').localeCompare(b?.nome || ''))
                .map(disp => {
                    const clone = template.content.cloneNode(true);
                    const span = clone.querySelector('span');

                    const nome = disp?.nome || 'N/A';
                    const potencia = typeof disp?.potencia_ativa_mw === 'number'
                        ? `${disp.potencia_ativa_mw.toFixed(0)} MW`
                        : 'N/A';

                    span.textContent = `${nome}: ${potencia}`;
                    return clone.firstElementChild;
                });
        },

        _somarPotenciaDispositivos(dispositivosDict) {
            if (!dispositivosDict) return 0;
            return Object.values(dispositivosDict).reduce((total, disp) => {
                const potencia = typeof disp?.potencia_ativa_mw === 'number' ? disp.potencia_ativa_mw : 0;
                return total + potencia;
            }, 0);
        },

        _atualizarCardPotenciaTotal() {
            const valorMw = Object.values(this.state.potenciaPorUsina || {}).reduce((acc, val) => acc + val, 0);
            const alvo = document.getElementById('potencia-total-mw');
            if (!alvo) return;
            alvo.textContent = valorMw > 0 ? valorMw.toFixed(0) : '0';
        },

        _getColorByStatus(description) {
            const descLower = (description || '').toLowerCase();
            const map = this.config.statusColorsMap;
            if (map[descLower]) { return map[descLower]; }

            return map['up (parada)'];
        },

        // --- Modal de Intervenção ---
        openStatusModal(usinaSlug, deviceName, currentStatus) {
            // Previne propagação se necessário, mas aqui é chamada direta
            console.log(`[Status Usinas] Abrindo modal para ${usinaSlug}/${deviceName}`);

            const modal = document.getElementById('status-intervention-modal');
            if (!modal) return;

            // Popula campos ocultos
            document.getElementById('modal-usina-slug').value = usinaSlug;
            document.getElementById('modal-device-name').value = deviceName;

            // Título
            document.getElementById('modal-title-device').textContent = `${usinaSlug.toUpperCase()} - ${deviceName}`;

            // Resetar seleção
            document.querySelectorAll('input[name="status-reason"]').forEach(el => el.checked = false);
            document.getElementById('reason-normal').checked = true; // Default

            // Exibir modal
            modal.classList.remove('hidden');
        },

        closeStatusModal() {
            const modal = document.getElementById('status-intervention-modal');
            if (modal) modal.classList.add('hidden');
        },

        confirmStatusChange() {
            const usinaSlug = document.getElementById('modal-usina-slug').value;
            const deviceName = document.getElementById('modal-device-name').value;

            const selectedOption = document.querySelector('input[name="status-reason"]:checked');
            if (!selectedOption) return;

            const reason = selectedOption.value; // "MANUTENCAO", "RESTRICAO", "NORMAL"

            console.log(`[Status Usinas] Enviando intervenção para backend: ${usinaSlug}/${deviceName} -> ${reason}`);

            // Emitir evento via Socket para registrar no backend
            if (this.state.socket && this.state.socket.connected) {
                this.state.socket.emit('registrar_intervencao_status', {
                    usina: usinaSlug,
                    dispositivo: deviceName,
                    motivo: reason,
                    timestamp: Date.now()
                });

                // Feedback visual
                // O modal fecha, e a atualização virá do backend via broadcast
            } else {
                alert('Erro: Sem conexão com o servidor.');
            }

            this.closeStatusModal();
        }
    };

    StatusUsinasModule.init();

    // Expor para o escopo global para que os onclicks do HTML funcionem
    window.StatusUsinasModule = StatusUsinasModule;
})();
