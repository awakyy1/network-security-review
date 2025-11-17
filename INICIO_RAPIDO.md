# GUIA DE INÍCIO RÁPIDO
## Sistema de Análise de Segurança de Redes

---

## EXECUÇÃO EM 3 PASSOS

### PASSO 1: Ativar Ambiente Virtual
```powershell
.venv\Scripts\activate
```

### PASSO 2: Executar Sistema
```powershell
python src/nmap_to_zabbix.py
```

### PASSO 3: Visualizar Resultado
```powershell
start output/dashboard.html
```

---

## ESTRUTURA DO PROJETO

```
integração/
├── src/          # Código principal
├── docs/         # Documentação
├── tests/        # Testes e validações
├── data/         # Scans do Nmap (entrada)
├── output/       # Relatórios gerados (saída)
└── examples/     # Exemplos de uso
```

---

## PRIMEIRA EXECUÇÃO

Se esta é a primeira vez que está utilizando o sistema:
## PRIMEIRA EXECUÇÃO

Se esta é a primeira vez que está utilizando o sistema:

```powershell
# 1. Criar ambiente virtual Python
python -m venv .venv

# 2. Ativar ambiente virtual
.venv\Scripts\activate

# 3. Instalar dependências necessárias
pip install -r requirements.txt

# 4. Executar sistema
python src/nmap_to_zabbix.py
```

---

## ARQUIVOS GERADOS

Após a execução, você encontrará em `output/`:

### 1. dashboard.html
Dashboard técnico profissional interativo
- Abrir no navegador para visualização completa
- Inclui gráficos, tabelas e análises

### 2. relatorio_seguranca.md
Relatório detalhado em Markdown
- Formato texto para documentação
- Fácil conversão para outros formatos

### 3. relatorio_seguranca.json
Dados estruturados em JSON
- Integração com outras ferramentas
- Processamento automatizado

---

## TESTES RÁPIDOS

### Teste Básico do Sistema
```powershell
python tests/teste_rapido.py
```
Executa teste com dados de exemplo pré-configurados.

### Teste Completo
```powershell
python tests/teste_sistema.py
```
Validação completa de todas as funcionalidades.

### Teste de IA (Ollama)
```powershell
python tests/teste_ollama.py
```
Verifica instalação e funcionamento do Ollama.

---

## FAZER UM NOVO SCAN

Para analisar sua própria rede:

### Scan Básico
```bash
nmap -sV -O <IP_ou_RANGE> -oX data/scan_result.xml
```

### Scan Detalhado (Recomendado)
```bash
nmap -sV -sC -O -A <IP_ou_RANGE> -oX data/scan_result.xml
```

**Exemplos:**
```bash
# Scan de uma máquina
nmap -sV -O 192.168.1.100 -oX data/scan_result.xml

# Scan de uma rede
nmap -sV -sC -O 192.168.1.0/24 -oX data/scan_result.xml

# Scan completo de servidor
nmap -sV -sC -O -A -p- 10.0.0.50 -oX data/scan_result.xml
```

Após criar o scan, execute novamente:
```powershell
python src/nmap_to_zabbix.py
```

---

## USAR IA (OPCIONAL)

Para ativar análises contextuais com Inteligência Artificial:

## USAR IA (OPCIONAL)

Para ativar análises contextuais com Inteligência Artificial:

### Instalação do Ollama
```powershell
winget install Ollama.Ollama
```

### Download do Modelo
```powershell
ollama pull llama3.2
```

### Iniciar Servidor (em outro terminal)
```powershell
ollama serve
```

### Executar Sistema com IA
```powershell
python src/nmap_to_zabbix.py
```

O sistema detectará automaticamente o Ollama e gerará análises adicionais:
- Análise técnica profunda de vulnerabilidades
- Cenários de teste de penetração
- Relatórios de compliance

---

## SOLUÇÃO DE PROBLEMAS

### Erro: "Arquivo scan_result.xml não encontrado"
**Solução:** Execute um scan Nmap primeiro:
```bash
nmap -sV -O <IP> -oX data/scan_result.xml
```

### Erro: "No module named 'requests'"
**Solução:** Instale as dependências:
```powershell
.venv\Scripts\activate
pip install -r requirements.txt
```

### Erro: "Ollama não está instalado"
**Solução:** IA é opcional. O sistema funciona sem ela. Para ativar:
```powershell
winget install Ollama.Ollama
ollama pull llama3.2
ollama serve
```

### Dashboard não abre
**Solução:** Abra manualmente:
```powershell
start output/dashboard.html
```

---

## DOCUMENTAÇÃO COMPLETA

Para informações detalhadas, consulte:

### Manuais Principais
- `README.md` - Documentação completa do projeto
- `docs/GUIA_USO.md` - Manual detalhado de uso
- `docs/DASHBOARD_TECNICO_GUIA.md` - Guia do dashboard

### Testes e Exemplos
- `tests/teste_rapido.py` - Teste rápido
- `tests/teste_sistema.py` - Teste completo
- `tests/teste_ollama.py` - Teste de IA
- `examples/demo_dashboard.py` - Demonstração

---

## COMANDOS ÚTEIS

### Ativar Ambiente
```powershell
.venv\Scripts\activate
```

### Desativar Ambiente
```powershell
deactivate
```

### Atualizar Dependências
```powershell
pip install -r requirements.txt --upgrade
```

### Listar Pacotes Instalados
```powershell
pip list
```

### Verificar Versão Python
```powershell
python --version
```

---

## FLUXO COMPLETO DE TRABALHO

**1. Preparação:**
```powershell
.venv\Scripts\activate
```

**2. Scan da Rede:**
```bash
nmap -sV -sC -O 192.168.1.0/24 -oX data/scan_result.xml
```

**3. Análise:**
```powershell
python src/nmap_to_zabbix.py
```

**4. Visualização:**
```powershell
start output/dashboard.html
```

**5. Revisão:**
- Abrir `output/relatorio_seguranca.md` para detalhes
- Usar `output/relatorio_seguranca.json` para integração

---

## PRÓXIMOS PASSOS

Após executar o sistema com sucesso:

1. **Revisar Dashboard**: Analise os resultados no `dashboard.html`
2. **Ler Relatórios**: Consulte o `relatorio_seguranca.md`
3. **Priorizar Riscos**: Use a matriz de risco para decisões
4. **Implementar Correções**: Siga as recomendações técnicas
5. **Re-scan**: Execute novo scan após correções

---

## CONFIGURAÇÃO PERSONALIZADA

Para customizar caminhos e configurações, edite:
```
src/config.json
```

Veja exemplos em:
```
README.md (seção CONFIGURAÇÃO AVANÇADA)
```

---

**Sistema Pronto Para Uso!**

Para suporte adicional, consulte a documentação em `docs/` ou execute os testes em `tests/`.

---

**Última Atualização:** Novembro 2025

**Versão:** 2.0
