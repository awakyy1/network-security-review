# Estado atual do sistema

Este documento descreve o que o código da branch V1 realmente faz. Ele separa
capacidades operacionais, ferramentas de pesquisa e limites deliberados.

## Capacidades implementadas

### 1. Revisão de inventário Nmap

`src/nmap_to_zabbix.py` lê um XML produzido previamente por uma varredura Nmap
autorizada. O programa não executa o Nmap. Ele:

- mantém somente hosts ativos e portas abertas observadas;
- preserva IP, hostname, protocolo e fingerprints de serviço sem completar
  dados ausentes por inferência;
- aplica nove regras transparentes de revisão de configuração para Telnet,
  FTP, HTTP, SMB, bancos de dados, RDP, VNC, SSH e SMTP;
- gera relatório Markdown, JSON e dashboard HTML escapado;
- classifica resultados como perguntas de revisão, nunca como vulnerabilidades
  confirmadas e nunca inventa CVEs;
- opcionalmente cria hosts no Zabbix somente com `--zabbix`, credenciais em
  variáveis de ambiente, TLS verificado e timeout finito.

### 2. Laboratório comportamental V2

`src/telemetry.py`, `src/behavior_detector.py` e `src/v2_experiment.py` processam
telemetria JSONL inerte e normalizada. O detector aplica quatro regras fixas:

| Regra | Observação revisada | ATT&CK usado como contexto |
|---|---|---|
| `BEH-001` | conexões periódicas para um endpoint | T1071 |
| `BEH-002` | contato rápido com ao menos oito endpoints | T1046 |
| `BEH-003` | egresso volumoso e assimétrico | T1041 |
| `BEH-004` | download seguido de criação de arquivo | T1105 |

Cada achado tem identificador estável, IDs exatos das evidências, contexto de
ativo quando disponível e campos explícitos negando malware confirmado,
vulnerabilidade confirmada e autorização de resposta automática.

O runner calcula TP, FP, FN, TN, precisão, recall, F1 e especificidade sobre os
fixtures rotulados. Esses números medem conformidade funcional dos fixtures,
não acurácia de detecção de malware no mundo real.

### 3. Assessoria local com Ollama

Quando `--ollama-model` é informado, o laboratório envia somente achados e
evidências ao Ollama por loopback. O protocolo grounded:

- exige JSON sob esquema fechado;
- exige todos os `finding_id` e `event_id` fornecidos, exatamente uma vez;
- rejeita IDs desconhecidos, CVEs inventados e alegações absolutas de
  comprometimento ou malware;
- aceita apenas controles de um catálogo fixo e aplicáveis à regra;
- preserva a resposta bruta e a causa quando o validador rejeita a saída;
- não fornece ao modelo credenciais nem meios de executar uma ação.

O protocolo histórico em texto livre existe somente como controle experimental
reconstruído. `src/v2_repetitions.py` executa séries repetidas;
`src/result_preservation.py` preserva artefatos e hashes; e
`src/phase_c_analysis.py` produz a comparação automatizada final.

### 4. Validação externa CTU-13

`src/ctu13_acquire.py` limita a aquisição a dois fluxos de texto congelados e
verifica origem, tamanho e SHA-256. `src/ctu13_experiment.py` processa esses
arquivos em streaming, separa família de desenvolvimento e holdout e calcula
intervalos e métricas, incluindo MCC. Arquivos CTU-13 originais permanecem em
`data/`, ignorados pelo Git; somente resultados revisados e agregados são
versionados.

### 5. Produção e auditoria do artigo

`src/article_tables.py` gera tabelas LaTeX diretamente dos JSON preservados. O
snapshot V1.0, sua bibliografia e seus resultados permanecem versionados; o
artigo atual está congelado como V1.1. Testes unitários cobrem parser,
relatórios, telemetria, regras, Ollama, preservação, repetição, CTU-13,
comparação e tabelas.

## O que o sistema não faz

- não executa Nmap, malware, exploits ou payloads;
- não monitora uma rede continuamente e não coleta telemetria por conta própria;
- não confirma vulnerabilidades, malware, famílias ou comprometimento;
- não consulta automaticamente uma base CVE nem estima explorabilidade;
- não altera firewall, não isola host, não encerra processo e não coloca
  arquivos em quarentena;
- não transforma uma sugestão do LLM em ação;
- não é um detector de malware validado para produção.

## Mudanças em relação ao artefato de 2025

Sim, o sistema foi alterado de forma substancial. O commit pré-banca `dd63d4c`
continua sendo o registro do protótipo de 2025. O núcleo atual preservou o
parser Nmap, relatórios, dashboard e exportação explícita para Zabbix, mas
removeu do caminho principal associações CVE estáticas e alegações não
validadas. A V2 adicionou telemetria normalizada, regras comportamentais,
validação grounded do Ollama, experimentos repetidos, validação externa CTU-13,
proveniência com hashes e tabelas geradas.

Essa alteração não modifica retroativamente a monografia aprovada. Ela constitui
uma extensão pós-defesa, testada e documentada no snapshot V1.0; a revisão
V1.1 amplia a avaliação sem reescrever esse registro histórico.
