# Sistema de Análise de Segurança de Redes

## 📋 Descrição

Sistema desenvolvido para TCC sobre Segurança de Redes que:
- Processa logs do Nmap em formato XML
- Cria topologia automatizada no Zabbix
- Gera relatório detalhado de vulnerabilidades encontradas

## 🚀 Funcionalidades

### 1. Análise de Scan Nmap
- Lê arquivos XML gerados pelo Nmap
- Identifica hosts ativos
- Mapeia portas abertas e serviços
- Detecta sistemas operacionais

### 2. Detecção de Vulnerabilidades
- Identifica serviços inseguros (FTP, Telnet, HTTP)
- Classifica vulnerabilidades por severidade (Alta, Média, Baixa)
- Fornece recomendações de segurança específicas

### 3. Integração com Zabbix
- Cria hosts automaticamente no Zabbix
- Gera mapa de topologia da rede
- Permite monitoramento contínuo

### 4. Geração de Relatórios
- Relatório em Markdown (formato legível)
- Relatório em JSON (formato estruturado)
- Resumo executivo de vulnerabilidades

## 📦 Instalação

### Pré-requisitos
- Python 3.7 ou superior
- Nmap instalado
- Zabbix Server (opcional, para integração)

### Passos de Instalação

1. Clone ou baixe o projeto

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure o arquivo `config.json` com suas credenciais do Zabbix

## 🔧 Uso

### Passo 1: Executar Scan com Nmap

Execute um scan de rede com Nmap e salve em formato XML:

```bash
# Scan básico
nmap -sV -O -oX scan_result.xml 192.168.1.0/24

# Scan mais detalhado
nmap -sV -sC -O -A -oX scan_result.xml 192.168.1.0/24

# Scan rápido
nmap -T4 -F -sV -oX scan_result.xml 192.168.1.0/24
```

**Parâmetros importantes:**
- `-sV`: Detecção de versão de serviços
- `-O`: Detecção de sistema operacional
- `-sC`: Scripts padrão do Nmap
- `-A`: Habilita detecção de SO e versão
- `-oX`: Salva resultado em XML
- `-T4`: Velocidade de scan (0-5)
- `-F`: Scan rápido (top 100 portas)

### Passo 2: Executar o Sistema

```bash
python nmap_to_zabbix.py
```

### Passo 3: Verificar Relatórios

Serão gerados dois arquivos:
- `relatorio_seguranca.md` - Relatório formatado
- `relatorio_seguranca.json` - Dados estruturados

## 📊 Exemplo de Relatório

O relatório gerado inclui:

### Resumo Executivo
- Total de hosts descobertos
- Total de vulnerabilidades
- Classificação por severidade

### Detalhes dos Hosts
- Endereço IP
- Hostname
- Sistema Operacional
- Portas abertas e serviços

### Vulnerabilidades Identificadas

#### 🔴 Alta Severidade
- Telnet exposto (porta 23)
- RDP exposto (porta 3389)
- MySQL exposto (porta 3306)
- SMB/NetBIOS exposto (portas 139, 445)

#### 🟡 Média Severidade
- HTTP sem criptografia (porta 80)
- FTP não criptografado (porta 21)

#### 🟢 Baixa Severidade
- SSH exposto (porta 22)
- SMTP aberto (porta 25)

### Recomendações de Segurança
- Específicas para cada vulnerabilidade
- Melhores práticas gerais

## 🔐 Vulnerabilidades Detectadas

O sistema identifica:

| Serviço | Porta | Severidade | Risco |
|---------|-------|------------|-------|
| Telnet | 23 | Alta | Transmissão sem criptografia |
| FTP | 21 | Média | Credenciais em texto claro |
| HTTP | 80 | Média | Tráfego não criptografado |
| SMB | 139/445 | Alta | Vulnerável a ataques (EternalBlue) |
| MySQL | 3306 | Alta | Banco exposto publicamente |
| RDP | 3389 | Alta | Alvo de ataques de força bruta |
| VNC | 5900 | Alta | Acesso remoto inseguro |
| SSH | 22 | Baixa | Verificar configuração |

## 🔗 Integração com Zabbix

### Configuração do Zabbix

1. Acesse o Zabbix e crie um usuário com permissões de API

2. Edite `config.json`:
```json
{
  "zabbix": {
    "url": "http://seu-servidor/zabbix/api_jsonrpc.php",
    "user": "seu_usuario",
    "password": "sua_senha",
    "host_group_id": "2"
  }
}
```

3. Execute o script - os hosts serão criados automaticamente

### Recursos Criados no Zabbix
- Hosts para cada dispositivo encontrado
- Interfaces configuradas
- Mapa de topologia da rede

## 📁 Estrutura do Projeto

```
integração/
├── nmap_to_zabbix.py      # Script principal
├── requirements.txt        # Dependências Python
├── config.json            # Configurações
├── README.md              # Este arquivo
├── scan_result.xml        # Resultado do Nmap (gerado)
├── relatorio_seguranca.md # Relatório Markdown (gerado)
└── relatorio_seguranca.json # Relatório JSON (gerado)
```

## 🛠️ Personalização

### Adicionar Novas Vulnerabilidades

Edite a função `_check_vulnerabilities` em `NmapParser`:

```python
vuln_db = {
    'novo_servico': {
        'ports': ['porta'],
        'severity': 'ALTA',
        'description': 'Descrição da vulnerabilidade'
    }
}
```

### Modificar Recomendações

Edite a função `_get_recommendation`:

```python
recommendations = {
    'servico': 'Sua recomendação aqui'
}
```

## ⚠️ Avisos Importantes

1. **Uso Ético**: Use apenas em redes autorizadas
2. **Legalidade**: Obtenha permissão antes de escanear redes
3. **Precisão**: Vulnerabilidades são baseadas em heurísticas
4. **Atualização**: Mantenha o banco de vulnerabilidades atualizado

## 🎓 TCC - Segurança de Redes

Este projeto foi desenvolvido como parte de um Trabalho de Conclusão de Curso sobre Segurança de Redes.

### Objetivos do TCC
- Automatizar análise de segurança de redes
- Integrar ferramentas open source (Nmap + Zabbix)
- Facilitar identificação de vulnerabilidades
- Gerar documentação automatizada

## 📝 Licença

Projeto acadêmico - TCC Segurança de Redes

## 🤝 Contribuições

Este é um projeto acadêmico, mas sugestões são bem-vindas!

## 📧 Contato

Para dúvidas sobre o projeto, consulte seu orientador de TCC.

---

**Desenvolvido para TCC - Segurança de Redes**
