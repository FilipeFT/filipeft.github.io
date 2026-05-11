<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Construtor de Projetos Habana - Modular</title>
    <style>
        :root {
            --azul-cnpq: #004a80;
            --verde-sucesso: #28a745;
            --alerta: #dc3545;
            --papel: #ffffff;
            --cinza-claro: #f8f9fa;
        }

        body {
            font-family: 'Times New Roman', Times, serif;
            background-color: #525659;
            margin: 0;
            padding: 40px 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .folha-a4 {
            background: var(--papel);
            width: 210mm;
            min-height: 297mm;
            padding: 25mm;
            box-shadow: 0 0 15px rgba(0,0,0,0.5);
            box-sizing: border-box;
            position: relative;
            margin-bottom: 50px;
        }

        /* Hover para áreas editáveis e removíveis */
        .secao-container { position: relative; margin-bottom: 20px; border: 1px solid transparent; transition: 0.2s; }
        .secao-container:hover { border: 1px dashed #ccc; }
        
        [contenteditable="true"]:hover { background: #fff9c4; }
        [contenteditable="true"]:focus { background: #fffde7; outline: 2px solid var(--azul-cnpq); }

        h1 { color: var(--azul-cnpq); text-align: center; font-size: 24px; text-transform: uppercase; border-bottom: 2px solid var(--azul-cnpq); padding-bottom: 10px; }
        h2 { color: var(--azul-cnpq); font-size: 18px; border-left: 5px solid var(--azul-cnpq); padding-left: 10px; margin: 20px 0 10px 0; }

        .dashboard-fixo {
            background: var(--cinza-claro);
            border: 1px solid #ddd;
            padding: 15px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-around;
            border-radius: 4px;
            font-family: Arial, sans-serif;
        }

        .stat-value { font-size: 18px; font-weight: bold; color: var(--azul-cnpq); }
        .alerta-bolsa { color: var(--alerta); font-weight: bold; text-align: center; padding: 10px; border: 1px solid var(--alerta); margin-top: 10px; display: none; font-family: Arial; }

        table { width: 100%; border-collapse: collapse; margin: 15px 0; font-family: Arial; font-size: 12px; }
        th { background: var(--azul-cnpq); color: white; padding: 10px; border: 1px solid #ddd; }
        td { padding: 8px; border: 1px solid #ddd; }

        /* Botões de deletar */
        .btn-del {
            position: absolute; right: -40px; top: 0;
            background: var(--alerta); color: white; border: none;
            width: 30px; height: 30px; border-radius: 50%;
            cursor: pointer; font-weight: bold; display: flex; align-items: center; justify-content: center;
        }
        .btn-del-row { background: var(--alerta); color: white; border: none; padding: 2px 8px; cursor: pointer; border-radius: 3px; }

        .controles {
            position: fixed; top: 20px; right: 20px;
            display: flex; flex-direction: column; gap: 10px; z-index: 1000;
        }

        .btn {
            padding: 12px 20px; border: none; border-radius: 5px;
            color: white; font-weight: bold; cursor: pointer;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2); font-family: Arial;
        }
        .btn-snapshot { background: var(--verde-sucesso); }
        .btn-add-secao { background: #6f42c1; }
        .btn-add-item { background: var(--azul-cnpq); }

        @media print {
            .controles, .btn-del, .btn-del-row, .dashboard-fixo { display: none !important; }
            body { background: white; padding: 0; }
            .folha-a4 { box-shadow: none; margin: 0; border: none; }
        }
    </style>
</head>
<body>

<div class="controles">
    <button class="btn btn-snapshot" onclick="gerarSnapshot()">Gerar Link Snapshot</button>
    <button class="btn btn-add-secao" onclick="adicionarSecao()">+ Nova Seção Texto</button>
    <button class="btn btn-add-item" onclick="adicionarLinha('tabela-bolsas')">+ Adicionar Bolsa</button>
    <button class="btn btn-add-item" onclick="adicionarLinha('tabela-custeio')">+ Adicionar Custeio</button>
</div>

<div class="folha-a4" id="relatorio">
    <h1 contenteditable="true" id="titulo-projeto">Projeto Habana: Edital PROSUL 02/2026</h1>
    
    <div class="dashboard-fixo">
        <div style="text-align:center">
            <span style="display:block; font-size:10px">VALOR TOTAL</span>
            <span class="stat-value" id="resumo-total">R$ 0,00</span>
        </div>
        <div style="text-align:center">
            <span style="display:block; font-size:10px">% BOLSAS</span>
            <span class="stat-value" id="resumo-perc">0%</span>
        </div>
    </div>
    <div id="aviso-regra" class="alerta-bolsa">Atenção: O investimento em bolsas deve ser ≥ 50%.</div>

    <div id="conteudo-dinamico">
        <div class="secao-container" id="secao-1">
            <button class="btn-del" onclick="this.parentElement.remove(); calcular();">X</button>
            <h2 contenteditable="true">1. Resumo e Justificativa</h2>
            <p contenteditable="true">Clique aqui para descrever a fundamentação científica e a necessidade do projeto...</p>
        </div>

        <h2>2. Planilha de Bolsas</h2>
        <table id="tabela-bolsas">
            <thead>
                <tr>
                    <th>Especialista / Nível Bolsa</th>
                    <th width="80">Vlr (R$)</th>
                    <th width="50">Meses</th>
                    <th width="40">Qtd</th>
                    <th width="100">Subtotal</th>
                    <th width="30"></th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td contenteditable="true">Pesquisador Principal (DTI-A)</td>
                    <td contenteditable="true" class="edit-val">5000</td>
                    <td contenteditable="true" class="edit-mes">24</td>
                    <td contenteditable="true" class="edit-qtd">1</td>
                    <td class="item-subtotal">0</td>
                    <td><button class="btn-del-row" onclick="this.closest('tr').remove(); calcular();">X</button></td>
                </tr>
            </tbody>
        </table>

        <h2>3. Custeio e Capital</h2>
        <table id="tabela-custeio">
            <thead>
                <tr>
                    <th>Descrição do Item</th>
                    <th width="80">Unit. (R$)</th>
                    <th width="50">-</th>
                    <th width="40">Qtd</th>
                    <th width="100">Subtotal</th>
                    <th width="30"></th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td contenteditable="true">Missão Técnica: Cuba</td>
                    <td contenteditable="true" class="edit-val">12000</td>
                    <td class="edit-mes">1</td>
                    <td contenteditable="true" class="edit-qtd">2</td>
                    <td class="item-subtotal">0</td>
                    <td><button class="btn-del-row" onclick="this.closest('tr').remove(); calcular();">X</button></td>
                </tr>
            </tbody>
        </table>
    </div>
</div>

<script>
    function utoa(str) { return window.btoa(unescape(encodeURIComponent(str))); }
    function atou(str) { return decodeURIComponent(escape(window.atob(str))); }

    function adicionarSecao() {
        const container = document.getElementById('conteudo-dinamico');
        const div = document.createElement('div');
        div.className = 'secao-container';
        div.innerHTML = `
            <button class="btn-del" onclick="this.parentElement.remove();">X</button>
            <h2 contenteditable="true">Novo Título de Seção</h2>
            <p contenteditable="true">Insira o conteúdo aqui...</p>
        `;
        container.appendChild(div);
        aplicarOuvintes();
    }

    function adicionarLinha(tabelaId) {
        const tbody = document.querySelector(`#${tabelaId} tbody`);
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td contenteditable="true">Novo Item</td>
            <td contenteditable="true" class="edit-val">0</td>
            <td contenteditable="true" class="edit-mes">${tabelaId === 'tabela-bolsas' ? 12 : 1}</td>
            <td contenteditable="true" class="edit-qtd">1</td>
            <td class="item-subtotal">0</td>
            <td><button class="btn-del-row" onclick="this.closest('tr').remove(); calcular();">X</button></td>
        `;
        tbody.appendChild(tr);
        aplicarOuvintes();
        calcular();
    }

    function calcular() {
        let totalBolsas = 0; let totalCusteio = 0;

        document.querySelectorAll('#tabela-bolsas tbody tr').forEach(row => {
            const v = parseFloat(row.querySelector('.edit-val').innerText) || 0;
            const m = parseFloat(row.querySelector('.edit-mes').innerText) || 0;
            const q = parseFloat(row.querySelector('.edit-qtd').innerText) || 0;
            const sub = v * m * q;
            totalBolsas += sub;
            row.querySelector('.item-subtotal').innerText = sub.toLocaleString('pt-br');
        });

        document.querySelectorAll('#tabela-custeio tbody tr').forEach(row => {
            const v = parseFloat(row.querySelector('.edit-val').innerText) || 0;
            const q = parseFloat(row.querySelector('.edit-qtd').innerText) || 0;
            const sub = v * q;
            totalCusteio += sub;
            row.querySelector('.item-subtotal').innerText = sub.toLocaleString('pt-br');
        });

        const total = totalBolsas + totalCusteio;
        const perc = total > 0 ? (totalBolsas / total) * 100 : 0;

        document.getElementById('resumo-total').innerText = total.toLocaleString('pt-br', {style: 'currency', currency: 'BRL'});
        document.getElementById('resumo-perc').innerText = perc.toFixed(1) + '%';
        document.getElementById('aviso-regra').style.display = perc < 50 ? 'block' : 'none';
    }

    function gerarSnapshot() {
        const dados = {
            titulo: document.getElementById('titulo-projeto').innerText,
            secoes: [],
            bolsas: [],
            custeio: []
        };

        // Captura todas as seções de texto dinâmicas
        document.querySelectorAll('.secao-container').forEach(sec => {
            dados.secoes.push({
                h: sec.querySelector('h2').innerText,
                p: sec.querySelector('p').innerText
            });
        });

        // Captura tabelas
        document.querySelectorAll('#tabela-bolsas tbody tr').forEach(row => {
            dados.bolsas.push({ d: row.cells[0].innerText, v: row.cells[1].innerText, m: row.cells[2].innerText, q: row.cells[3].innerText });
        });
        document.querySelectorAll('#tabela-custeio tbody tr').forEach(row => {
            dados.custeio.push({ d: row.cells[0].innerText, v: row.cells[1].innerText, q: row.cells[3].innerText });
        });

        const encoded = utoa(JSON.stringify(dados));
        const url = window.location.origin + window.location.pathname + '?data=' + encoded;
        
        navigator.clipboard.writeText(url).then(() => {
            alert("Snapshot modular gerado! Link copiado para transferência.");
            window.history.pushState({}, '', url);
        });
    }

    function carregarSnapshot() {
        const params = new URLSearchParams(window.location.search);
        const data = params.get('data');
        if (!data) { calcular(); return; }

        try {
            const d = JSON.parse(atou(data));
            document.getElementById('titulo-projeto').innerText = d.titulo;
            
            // Reconstrói Seções
            const container = document.getElementById('conteudo-dinamico');
            // Remove as seções padrão antes de carregar
            document.querySelectorAll('.secao-container').forEach(s => s.remove());
            
            d.secoes.forEach(sec => {
                const div = document.createElement('div');
                div.className = 'secao-container';
                div.innerHTML = `<button class="btn-del" onclick="this.parentElement.remove();">X</button>
                                 <h2 contenteditable="true">${sec.h}</h2><p contenteditable="true">${sec.p}</p>`;
                container.prepend(div); // Adiciona antes das tabelas
            });

            // Reconstrói Tabelas
            const montarTab = (id, lista, isB) => {
                const b = document.querySelector(`#${id} tbody`);
                b.innerHTML = '';
                lista.forEach(i => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `<td contenteditable="true">${i.d}</td><td contenteditable="true" class="edit-val">${i.v}</td>
                                    <td contenteditable="true" class="edit-mes">${isB ? i.m : 1}</td><td contenteditable="true" class="edit-qtd">${i.q}</td>
                                    <td class="item-subtotal">0</td><td><button class="btn-del-row" onclick="this.closest('tr').remove(); calcular();">X</button></td>`;
                    b.appendChild(tr);
                });
            };
            montarTab('tabela-bolsas', d.bolsas, true);
            montarTab('tabela-custeio', d.custeio, false);

            calcular();
            aplicarOuvintes();
        } catch(e) { console.error(e); }
    }

    function aplicarOuvintes() {
        document.querySelectorAll('[contenteditable="true"]').forEach(el => {
            el.addEventListener('input', calcular);
        });
    }

    window.onload = carregarSnapshot;
</script>
</body>
</html>
