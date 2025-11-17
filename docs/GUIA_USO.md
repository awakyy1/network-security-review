# 🚀 GUIA PRÁTICO DE USO

## Como o Sistema Funciona?

### 📊 Fluxo de Trabalho

```
1. NMAP SCAN          2. PROCESSAMENTO       3. ANÁLISE           4. SAÍDA
   ┌─────────┐           ┌──────────┐          ┌─────────┐         ┌──────────┐
   │  Nmap   │──XML──>   │  Parser  │───>      │ Detector│───>     │Relatórios│
   │  -sV -O │           │   XML    │          │  Vulns  │         │ MD + JSON│
   └─────────┘           └──────────┘          └─────────┘         └──────────┘
                                                     │
                                                     v
                                              ┌──────────┐
                                              │ Zabbix   │
                                              │   API    │
                                              └──────────┘
```

### 🔧 Componentes do Sistema

#### 1️⃣ **NmapParser** - Analisador de Scan
- Lê arquivo XML do Nmap
- Extrai informações de hosts, portas e serviços
- Identifica vulnerabilidades baseado em:
  - Portas abertas conhecidas por serem inseguras
  - Serviços rodando sem criptografia
  - Versões de software desatualizadas

#### 2️⃣ **ZabbixAPI** - Integração com Zabbix
- Conecta via API REST do Zabbix
- Cria hosts automaticamente
- Gera mapas de topologia de rede
- Permite monitoramento contínuo

#### 3️⃣ **ReportGenerator** - Gerador de Relatórios
- Cria relatório Markdown formatado
- Gera arquivo JSON estruturado
- Classifica vulnerabilidades por severidade

---

## 🎯 COMO USAR - PASSO A PASSO

### OPÇÃO 1: Teste Rápido (SEM Nmap instalado)

```powershell
# Apenas execute - o sistema cria arquivo de exemplo automaticamente
python nmap_to_zabbix.py
```

**O que acontece:**
- ✅ Cria `scan_result.xml` de exemplo
- ✅ Processa 2 hosts fictícios
- ✅ Gera relatórios de vulnerabilidades
- ✅ Tenta conectar no Zabbix (opcional)

---

### OPÇÃO 2: Uso Real com Nmap

#### Passo 1: Instalar Nmap
- Windows: https://nmap.org/download.html
- Ou use: `choco install nmap` (se tiver Chocolatey)

#### Passo 2: Fazer Scan da Rede

```powershell
# Scan básico de uma rede local
nmap -sV -O -oX scan_result.xml 192.168.1.0/24

# Scan de um IP específico
nmap -sV -O -oX scan_result.xml 192.168.1.1

# Scan mais completo (demora mais)
nmap -sV -sC -O -A -oX scan_result.xml 192.168.1.0/24

# Scan rápido (apenas portas comuns)
nmap -T4 -F -sV -oX scan_result.xml 192.168.1.0/24
```

**Parâmetros explicados:**
- `-sV` = Detecta versão dos serviços
- `-O` = Detecta sistema operacional  
- `-sC` = Executa scripts padrão
- `-A` = Modo agressivo (tudo)
- `-oX` = Salva em formato XML
- `-T4` = Velocidade (0=lento, 5=rápido)
- `-F` = Fast (top 100 portas)

#### Passo 3: Executar o Sistema

```powershell
python nmap_to_zabbix.py
```

#### Passo 4: Ver os Resultados

```powershell
# Ver relatório formatado
notepad relatorio_seguranca.md

# Ver dados estruturados
notepad relatorio_seguranca.json
```

---

## 📋 Configuração do Zabbix (OPCIONAL)

### Se você TEM Zabbix instalado:

1. **Edite config.json:**
```json
{
  "zabbix": {
    "url": "http://localhost/zabbix/api_jsonrpc.php",
    "user": "Admin",
    "password": "zabbix"
  }
}
```

2. **Execute normalmente:**
```powershell
python nmap_to_zabbix.py
```

### Se você NÃO TEM Zabbix:
- Sem problema! O sistema funciona sem ele
- Você ainda terá os relatórios completos
- A integração Zabbix é apenas um extra

---

## 📊 Exemplos de Saída

### Console:
```
============================================================
Sistema de Análise de Segurança de Redes
TCC - Segurança de Redes
============================================================

📡 Processando scan do Nmap...
✓ Processados 2 hosts do scan Nmap

📝 Gerando relatórios...
✓ Relatório gerado: relatorio_seguranca.md
✓ Relatório JSON gerado: relatorio_seguranca.json

============================================================
✅ Análise concluída com sucesso!
============================================================

📊 Estatísticas:
   - Hosts analisados: 2
   - Vulnerabilidades encontradas: 6
     • Alta: 4
     • Média: 2
     • Baixa: 0
```

### Relatório Markdown:
```markdown
# Relatório de Análise de Segurança de Rede

## 📊 Resumo Executivo
- Total de Hosts: 2
- Total de Vulnerabilidades: 6
  - 🔴 Alta: 4
  - 🟡 Média: 2
  - 🟢 Baixa: 0

## 🖥️ Hosts Descobertos

### 1. server01.local
- IP: 192.168.1.100
- Sistema: Linux 4.15
- Portas: 3

### 2. server02.local  
- IP: 192.168.1.101
- Sistema: Windows Server 2016
- Portas: 4

## 🔒 Vulnerabilidades Identificadas
...
```

---

## 🎓 Casos de Uso para TCC

### 1. Análise de Segurança Doméstica
```powershell
# Escanear sua própria rede
nmap -sV -O -oX scan_home.xml 192.168.0.0/24
python nmap_to_zabbix.py
```

### 2. Análise de Servidor Específico
```powershell
# Analisar um servidor específico
nmap -sV -sC -O -A -oX scan_server.xml 192.168.1.100
python nmap_to_zabbix.py
```

### 3. Scan Periódico Automatizado
```powershell
# Criar script para executar periodicamente
# Coloque no Agendador de Tarefas do Windows
```

---

## 🔍 O Que o Sistema Detecta?

### Vulnerabilidades de Alta Severidade 🔴
- ✅ Telnet (porta 23) - Sem criptografia
- ✅ RDP exposto (porta 3389) - Alvo de ataques
- ✅ MySQL/PostgreSQL públicos - Dados expostos
- ✅ SMB/NetBIOS (portas 139/445) - EternalBlue
- ✅ VNC sem senha - Acesso remoto inseguro

### Vulnerabilidades de Média Severidade 🟡
- ✅ HTTP sem HTTPS (porta 80)
- ✅ FTP não criptografado (porta 21)
- ✅ SMTP aberto (porta 25)

### Baixa Severidade 🟢
- ✅ SSH exposto (porta 22) - Verificar config

---

## 💡 Dicas Importantes

### ⚠️ AVISOS LEGAIS
```
⚠️ ATENÇÃO: Só escaneie redes que você tem permissão!
⚠️ Escanear redes sem autorização é ILEGAL
⚠️ Use apenas para fins educacionais/autorizados
```

### 🎯 Para Melhor Resultado
1. Execute como Administrador (PowerShell)
2. Desabilite firewall temporariamente (se necessário)
3. Use `-A` para scan mais completo
4. Salve múltiplos scans com datas diferentes

### 📚 Para o TCC
- Faça scans em diferentes horários
- Compare resultados ao longo do tempo
- Documente as vulnerabilidades encontradas
- Proponha soluções específicas
- Apresente antes/depois das correções

---

## ❓ Resolução de Problemas

### Erro: "Nmap não encontrado"
```powershell
# Instale o Nmap primeiro
# Baixe de: https://nmap.org/download.html
```

### Erro: "Arquivo XML não encontrado"
```powershell
# Verifique se o scan foi salvo corretamente
ls scan_result.xml
```

### Erro: "Módulo requests não encontrado"
```powershell
pip install -r requirements.txt
```

### Erro: "Zabbix connection failed"
```
# Normal se você não tem Zabbix instalado
# O sistema continua funcionando sem ele
# Só não terá a integração com Zabbix
```

---

## 🚀 Comandos Rápidos

```powershell
# Setup inicial
pip install -r requirements.txt

# Teste rápido (sem Nmap)
python nmap_to_zabbix.py

# Uso real
nmap -sV -O -oX scan_result.xml 192.168.1.0/24
python nmap_to_zabbix.py

# Ver resultados
notepad relatorio_seguranca.md
```

---

## 📞 Precisa de Ajuda?

1. Leia o README.md completo
2. Verifique os exemplos neste guia
3. Consulte a documentação do Nmap: https://nmap.org/book/
4. Consulte seu orientador de TCC

---

**Desenvolvido para TCC - Segurança de Redes** 🎓🔒
