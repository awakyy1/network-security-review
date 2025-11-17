# Sistema de Análise de Segurança de Redes

**TCC - Segurança de Redes**

Sistema automatizado de análise de vulnerabilidades de rede com geração de relatórios técnicos e dashboard profissional para identificação, classificação e priorização de riscos em infraestruturas de TI.

---

## CARACTERÍSTICAS PRINCIPAIS

### Análise e Detecção
- Parser de Nmap XML com detecção automática de vulnerabilidades
- Identificação de CVEs conhecidos para serviços críticos
- Vetores de ataque mapeados automaticamente
- Categorização de portas segundo padrão IANA
- Detecção de serviços criptografados vs não-criptografados

### Relatórios e Visualização
- Dashboard técnico avançado com detalhamento completo
- Relatórios em formato Markdown e JSON
- Matriz de risco técnico com scores CVSS
- Inventário completo de hosts e vulnerabilidades

### Compliance e Frameworks
- Análise de conformidade CIS Controls v8
- Verificação OWASP Top 10
- Conformidade PCI-DSS 3.2.1
- Framework NIST Cybersecurity

### Integração
- API Zabbix para criação de topologia de rede
- Integração com Ollama para análises contextuais via IA
- Suporte a múltiplos formatos de saída

---

## ESTRUTURA DO PROJETO

```
integração/
├── src/                          # Código fonte principal
│   ├── nmap_to_zabbix.py        # Sistema principal
│   ├── dashboard_tecnico.py     # Gerador de dashboard
│   └── config.json              # Configurações
│
├── docs/                         # Documentação
│   ├── README.md                # Guia principal
│   ├── DASHBOARD_TECNICO_GUIA.md # Guia do dashboard
│   └── GUIA_USO.md              # Manual de uso
│
├── tests/                        # Testes e dados de teste
│   ├── teste_ollama.py          # Teste de IA
│   ├── teste_rapido.py          # Teste rápido
│   ├── teste_sistema.py         # Teste completo
│   └── test_*.xml               # Cenários de teste
│
├── examples/                     # Exemplos de uso
│   └── demo_dashboard.py        # Demo do dashboard
│
├── data/                         # Dados de entrada
│   ├── scan_result.xml          # Scan principal
│   └── scan_backup.xml          # Backup de scan
│
├── output/                       # Arquivos gerados
│   ├── dashboard.html           # Dashboard técnico
│   ├── relatorio_seguranca.md   # Relatório markdown
│   └── relatorio_seguranca.json # Relatório JSON
│
├── .venv/                        # Ambiente virtual Python
├── requirements.txt              # Dependências
└── .gitignore                    # Arquivos ignorados
```

---

## INSTALAÇÃO E CONFIGURAÇÃO

### Passo 1: Clonar o Repositório
```bash
git clone <seu-repositorio>
cd integração
```

### Passo 2: Configurar Ambiente Virtual Python
```powershell
# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente virtual
.venv\Scripts\activate
```

### Passo 3: Instalar Dependências
```powershell
pip install -r requirements.txt
```

### Passo 4 (Opcional): Configurar Ollama para Análises com IA

**Instalação:**
```powershell
winget install Ollama.Ollama
```

**Download do Modelo:**
```powershell
ollama pull llama3.2
```

**Iniciar Servidor:**
```powershell
ollama serve
```

O sistema detecta automaticamente a disponibilidade do Ollama e ativa as análises contextuais.

---

## USO DO SISTEMA

## USO DO SYSTEM

### Execução Completa
```powershell
# Ativar ambiente virtual
.venv\Scripts\activate

# Executar análise
python src/nmap_to_zabbix.py
```

**O sistema executará as seguintes etapas:**

1. Processamento do scan Nmap (arquivo `data/scan_result.xml`)
2. Identificação e categorização de vulnerabilidades
3. Geração de relatórios em Markdown e JSON
4. Criação do dashboard técnico HTML
5. Tentativa de integração com Zabbix (se configurado)
6. Geração de análises contextuais com IA (se Ollama disponível)

### Arquivos Gerados

Após a execução, os seguintes arquivos serão criados em `output/`:

```
output/
├── dashboard.html              # Dashboard técnico profissional interativo
├── relatorio_seguranca.md      # Relatório detalhado em Markdown
└── relatorio_seguranca.json    # Dados estruturados em formato JSON
```

---

## EXECUÇÃO DE SCANS NMAP

### Scan Básico (Recomendado para Testes)
```bash
nmap -sV -O <IP_ou_RANGE> -oX data/scan_result.xml
```

### Scan Completo (Recomendado para Produção)
```bash
nmap -sV -sC -O -A -p- <IP_ou_RANGE> -oX data/scan_result.xml
```

### Parâmetros Explicados

| Parâmetro | Descrição | Necessário |
|-----------|-----------|------------|
| `-sV` | Detecção de versões de serviços | Sim |
| `-O` | Detecção de sistema operacional | Sim |
| `-sC` | Execução de scripts NSE padrão | Recomendado |
| `-A` | Análise agressiva (OS, versão, scripts, traceroute) | Recomendado |
| `-p-` | Scan de todas as 65535 portas | Opcional |
| `-oX` | Salvar saída em formato XML | Obrigatório |

### Exemplos Práticos

**Scan de uma única máquina:**
```bash
nmap -sV -O 192.168.1.100 -oX data/scan_result.xml
```

**Scan de uma rede completa:**
```bash
nmap -sV -sC -O 192.168.1.0/24 -oX data/scan_result.xml
```

**Scan detalhado de servidor:**
```bash
nmap -sV -sC -O -A -p- 192.168.1.50 -oX data/scan_result.xml
```

---

## TESTES E VALIDAÇÃO

## TESTES E VALIDAÇÃO

### Teste Rápido com Dados de Exemplo
```powershell
python tests/teste_rapido.py
```
Executa teste com dados pré-configurados para validação rápida do sistema.

### Teste Completo do Sistema
```powershell
python tests/teste_sistema.py
```
Executa bateria completa de testes incluindo parsing, análise e geração de relatórios.

### Teste de Integração com IA (Ollama)
```powershell
python tests/teste_ollama.py
```
Verifica instalação e funcionamento do Ollama, testa geração de análises contextuais.

---

## DASHBOARD TÉCNICO AVANÇADO

O dashboard gerado oferece visualização completa e profissional dos resultados da análise.

### Componentes Principais

**1. Análises Técnicas de Infraestrutura**
- Análise detalhada de portas com categorização IANA
- Identificação de serviços criptografados versus não-criptografados
- Mapeamento de bancos de dados expostos à rede
- Inventário de serviços de acesso remoto ativos

**2. Inventário de Vulnerabilidades**
- Listagem completa com IDs únicos de rastreamento
- CVEs conhecidos mapeados para cada serviço
- Classificação de severidade baseada em CVSS v3.1
- Recomendações técnicas específicas de mitigação

**3. Análise de Compliance**
- Conformidade com CIS Controls v8
- Verificação OWASP Top 10
- Análise PCI-DSS 3.2.1
- Framework NIST Cybersecurity

**4. Matriz de Risco Técnico**
- Avaliação bidimensional Impacto x Probabilidade
- Cálculo de scores individuais por vulnerabilidade
- Priorização automática de riscos
- Classificação em níveis: Crítico, Alto, Médio, Baixo

**5. Análises Contextuais com IA (Ollama)**
- Análise técnica profunda de superfície de ataque
- Cenários detalhados de teste de penetração
- Relatórios de compliance com frameworks reconhecidos

### Acesso ao Dashboard

Após execução do sistema, abrir o arquivo:
```
output/dashboard.html
```

Para documentação completa do dashboard, consultar:
```
docs/DASHBOARD_TECNICO_GUIA.md
```

---

## CONFIGURAÇÃO AVANÇADA

O arquivo de configuração `src/config.json` permite customização dos caminhos e credenciais:

```json
{
    "nmap": {
        "xml_file": "data/scan_result.xml"
    },
    "zabbix": {
        "url": "http://localhost/zabbix/api_jsonrpc.php",
        "user": "Admin",
        "password": "zabbix"
    },
    "output": {
        "markdown_report": "output/relatorio_seguranca.md",
        "json_report": "output/relatorio_seguranca.json",
        "dashboard": "output/dashboard.html"
    }
}
```

### Parâmetros Configuráveis

**Nmap:**
- `xml_file`: Caminho para o arquivo XML de saída do Nmap

**Zabbix (Opcional):**
- `url`: Endpoint da API JSON-RPC do Zabbix
- `user`: Usuário com permissões de administração
- `password`: Senha do usuário

**Output:**
- `markdown_report`: Caminho para o relatório em Markdown
- `json_report`: Caminho para o relatório em JSON
- `dashboard`: Caminho para o dashboard HTML

---

## INTEGRAÇÃO COM OLLAMA (IA)

### Verificação de Instalação
```powershell
ollama --version
ollama list
```

### Download e Configuração de Modelo
```powershell
# Download do modelo Llama 3.2 (recomendado - 2GB)
ollama pull llama3.2

# Alternativas
ollama pull llama3.2:1b  # Versão menor (1GB)
ollama pull mistral      # Modelo alternativo
```

### Execução do Servidor
```powershell
# Iniciar servidor Ollama (necessário antes de executar a análise)
ollama serve
```

### Funcionamento

O sistema detecta automaticamente a disponibilidade do Ollama através de requisição HTTP para `http://localhost:11434/api/tags`. Se disponível, três análises adicionais são geradas:

1. **Análise Técnica Profunda**: Superfície de ataque, exploitabilidade e impacto técnico
2. **Cenário de Teste de Penetração**: Fases de reconhecimento, exploração e pós-exploração
3. **Relatório de Compliance**: Avaliação de frameworks e controles

---

## VULNERABILIDADES DETECTADAS AUTOMATICAMENTE

## VULNERABILIDADES DETECTADAS AUTOMATICAMENTE

O sistema possui capacidade de identificação automática das seguintes categorias de vulnerabilidades:

| Vulnerabilidade | Severidade | CVEs Conhecidos | Impacto |
|----------------|-----------|-----------------|---------|
| Telnet Ativo | ALTA | CVE-2020-10188, CVE-2019-0053 | Interceptação de credenciais em texto claro |
| FTP Anônimo | ALTA | CVE-2015-1427, CVE-2011-2523 | Acesso não autorizado a arquivos |
| MySQL Exposto | ALTA | CVE-2016-6662, CVE-2012-2122 | Exfiltração de dados, SQL Injection |
| RDP Acessível | ALTA | CVE-2019-0708 (BlueKeep) | Execução remota de código |
| SMB v1 Ativo | ALTA | MS17-010 (EternalBlue) | Propagação de ransomware |
| PostgreSQL Exposto | ALTA | CVE-2018-1058, CVE-2019-10130 | Comprometimento de banco de dados |
| VNC sem Autenticação | ALTA | CVE-2019-15681, CVE-2018-7225 | Acesso remoto não autorizado |
| HTTP sem TLS | MÉDIA | N/A | Interceptação de dados em trânsito |
| Versões Desatualizadas | MÉDIA | Variados | Exploração de vulnerabilidades conhecidas |
| Portas Desnecessárias | BAIXA | N/A | Ampliação da superfície de ataque |

### Critérios de Classificação

**ALTA (CVSS 7.0-10.0):**
- Exploração remota sem autenticação
- Impacto em confidencialidade, integridade ou disponibilidade
- CVEs críticos conhecidos

**MÉDIA (CVSS 4.0-6.9):**
- Exploração com pré-requisitos
- Impacto parcial em segurança
- Exposição de informações sensíveis

**BAIXA (CVSS 0.1-3.9):**
- Requer acesso local ou credenciais
- Impacto mínimo em segurança
- Configurações sub-ótimas

---

## DOCUMENTAÇÃO COMPLEMENTAR

### Manuais Técnicos
- `docs/GUIA_USO.md` - Manual completo de utilização do sistema
- `docs/DASHBOARD_TECNICO_GUIA.md` - Documentação detalhada do dashboard
- `docs/README.md` - Documentação do projeto

### Exemplos e Demonstrações
- `examples/demo_dashboard.py` - Demonstração de geração de dashboard
- `tests/teste_rapido.py` - Teste rápido com dados de exemplo
- `tests/teste_sistema.py` - Bateria completa de testes

---

## APLICAÇÃO ACADÊMICA (TCC)

Este sistema foi desenvolvido como componente principal de um Trabalho de Conclusão de Curso (TCC) em Segurança de Redes.

### Fundamentação Técnica

**Metodologia:**
- Análise baseada em frameworks reconhecidos internacionalmente
- Utilização de padrões CVSS v3.1 para scoring de vulnerabilidades
- Classificação IANA para categorização de portas e serviços
- Mapeamento de CVEs através de bases públicas (NVD, MITRE)

**Frameworks de Compliance:**
- CIS Controls v8 (Center for Internet Security)
- OWASP Top 10 (Open Web Application Security Project)
- PCI-DSS 3.2.1 (Payment Card Industry Data Security Standard)
- NIST CSF (National Institute of Standards and Technology Cybersecurity Framework)

### Diferenciais Técnicos

1. **Automação End-to-End**: Processo completamente automatizado desde coleta até apresentação
2. **Análise Contextual com IA**: Utilização de LLM local para análises aprofundadas
3. **Múltiplos Formatos de Saída**: MD, JSON e HTML para diferentes finalidades
4. **Matriz de Risco Bidimensional**: Avaliação quantitativa de impacto e probabilidade
5. **Vetores de Ataque Mapeados**: Identificação automática de cadeias de exploração
6. **Compliance Multi-Framework**: Verificação simultânea de múltiplos padrões
7. **Código Aberto e Reprodutível**: Totalmente documentado e disponível

### Aplicabilidade Prática

- Auditorias de segurança em ambientes corporativos
- Testes de conformidade regulatória
- Análises de risco para gestão de vulnerabilidades
- Documentação técnica para equipes de TI
- Base para processos de pentest e red team
- Monitoramento contínuo de postura de segurança

---

## TECNOLOGIAS UTILIZADAS

## TECNOLOGIAS UTILIZADAS

### Core
- **Python 3.12** - Linguagem principal de desenvolvimento
- **XML ElementTree** - Parser de arquivos XML do Nmap
- **Requests** - Cliente HTTP para APIs (Zabbix, Ollama)
- **JSON** - Processamento e geração de dados estruturados

### Ferramentas Externas
- **Nmap 7.94+** - Scanner de rede e detecção de serviços
- **Zabbix API** - Integração para criação de topologia (opcional)
- **Ollama** - Framework de LLM local para análises com IA (opcional)

### Frameworks e Padrões
- **CVSS v3.1** - Common Vulnerability Scoring System
- **CVE/NVD** - Mapeamento de vulnerabilidades conhecidas
- **IANA** - Categorização de portas e serviços
- **CIS, OWASP, PCI-DSS, NIST** - Frameworks de compliance

### Frontend
- **HTML5/CSS3** - Dashboard responsivo e profissional
- **JavaScript** - Interatividade (futuro)

---

## LICENÇA E DISTRIBUIÇÃO

**Tipo:** Projeto Acadêmico - TCC (Trabalho de Conclusão de Curso)

**Tema:** Segurança de Redes - Análise Automatizada de Vulnerabilidades

**Ano:** 2025

**Uso Permitido:**
- Fins acadêmicos e educacionais
- Estudos e pesquisas em segurança da informação
- Auditorias de segurança em ambientes autorizados

**Restrições:**
- Uso em ambientes sem autorização expressa é proibido
- Scan de redes de terceiros sem permissão é ilegal
- Responsabilidade de uso é do operador

---

## SUPORTE E CONTRIBUIÇÕES

### Documentação
Para dúvidas sobre utilização, consulte a documentação na seguinte ordem:

1. `INICIO_RAPIDO.md` - Guia rápido de início
2. `docs/GUIA_USO.md` - Manual completo
3. `docs/DASHBOARD_TECNICO_GUIA.md` - Detalhes do dashboard
4. `tests/` - Exemplos práticos de uso

### Testes
Exemplos completos de testes disponíveis em:
- `tests/teste_rapido.py` - Validação rápida
- `tests/teste_sistema.py` - Teste completo
- `tests/teste_ollama.py` - Verificação de IA

### Estrutura de Pastas
```
src/       - Código fonte principal
docs/      - Documentação técnica
tests/     - Scripts de teste
examples/  - Demonstrações
data/      - Entrada (scans XML)
output/    - Saída (relatórios e dashboard)
```

---

## AUTOR E INFORMAÇÕES

**Projeto:** Sistema de Análise de Segurança de Redes

**Contexto:** TCC - Segurança de Redes

**Instituição:** [Sua Instituição]

**Ano:** 2025

**Orientador:** [Nome do Orientador]

---

## REFERÊNCIAS TÉCNICAS

1. Lyon, G. (2023). *Nmap Network Scanning: Official Guide*. Insecure.Com LLC.

2. NIST. (2018). *Framework for Improving Critical Infrastructure Cybersecurity*. Version 1.1.

3. CIS. (2021). *CIS Controls Version 8*. Center for Internet Security.

4. OWASP. (2021). *OWASP Top Ten 2021*. Open Web Application Security Project.

5. FIRST. (2019). *Common Vulnerability Scoring System v3.1*. Forum of Incident Response and Security Teams.

6. PCI Security Standards Council. (2018). *Payment Card Industry Data Security Standard v3.2.1*.

7. MITRE Corporation. *Common Vulnerabilities and Exposures (CVE)*. https://cve.mitre.org/

8. NIST. *National Vulnerability Database (NVD)*. https://nvd.nist.gov/

---

**Última Atualização:** Novembro 2025

**Versão do Sistema:** 2.0

**Status:** Produção
