"""
Gerador de Dashboard Técnico Avançado
Dashboard profissional com máximo detalhamento técnico
"""

import json
import requests
from datetime import datetime
from typing import Dict, List
import socket


class OllamaAI:
    """Classe para integração com Ollama"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model = "llama3.2"
        
    def is_available(self) -> bool:
        """Verifica se Ollama está disponível"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def generate(self, prompt: str) -> str:
        """Gera resposta usando Ollama"""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9
                    }
                },
                timeout=120
            )
            
            if response.status_code == 200:
                return response.json().get('response', '').strip()
            return ""
        except Exception as e:
            print(f"Erro ao gerar com IA: {e}")
            return ""


class TechnicalDashboard:
    """Gerador de Dashboard Técnico Avançado"""
    
    # Mapeamento de portas e serviços conhecidos
    WELL_KNOWN_PORTS = {
        '21': {'name': 'FTP', 'protocol': 'TCP', 'description': 'File Transfer Protocol'},
        '22': {'name': 'SSH', 'protocol': 'TCP', 'description': 'Secure Shell'},
        '23': {'name': 'Telnet', 'protocol': 'TCP', 'description': 'Unencrypted text communications'},
        '25': {'name': 'SMTP', 'protocol': 'TCP', 'description': 'Simple Mail Transfer Protocol'},
        '53': {'name': 'DNS', 'protocol': 'TCP/UDP', 'description': 'Domain Name System'},
        '80': {'name': 'HTTP', 'protocol': 'TCP', 'description': 'Hypertext Transfer Protocol'},
        '110': {'name': 'POP3', 'protocol': 'TCP', 'description': 'Post Office Protocol v3'},
        '143': {'name': 'IMAP', 'protocol': 'TCP', 'description': 'Internet Message Access Protocol'},
        '443': {'name': 'HTTPS', 'protocol': 'TCP', 'description': 'HTTP Secure'},
        '445': {'name': 'SMB', 'protocol': 'TCP', 'description': 'Server Message Block'},
        '3306': {'name': 'MySQL', 'protocol': 'TCP', 'description': 'MySQL Database'},
        '3389': {'name': 'RDP', 'protocol': 'TCP', 'description': 'Remote Desktop Protocol'},
        '5432': {'name': 'PostgreSQL', 'protocol': 'TCP', 'description': 'PostgreSQL Database'},
        '5900': {'name': 'VNC', 'protocol': 'TCP', 'description': 'Virtual Network Computing'},
        '8080': {'name': 'HTTP-Alt', 'protocol': 'TCP', 'description': 'HTTP Alternate'},
    }
    
    # CVEs conhecidas por serviço
    KNOWN_CVES = {
        'telnet': ['CVE-2020-10188', 'CVE-2019-0053'],
        'ftp': ['CVE-2015-1427', 'CVE-2011-2523'],
        'smb': ['MS17-010 (EternalBlue)', 'CVE-2017-0144'],
        'rdp': ['CVE-2019-0708 (BlueKeep)', 'CVE-2020-0609'],
        'mysql': ['CVE-2016-6662', 'CVE-2012-2122'],
        'postgresql': ['CVE-2018-1058', 'CVE-2019-10130'],
        'vnc': ['CVE-2019-15681', 'CVE-2018-7225'],
    }
    
    def __init__(self, use_ai: bool = True):
        self.use_ai = use_ai
        self.ai = OllamaAI() if use_ai else None
        
    def generate(self, hosts: List[Dict], vuln_summary: Dict, output_file: str = "dashboard.html"):
        """Gera dashboard técnico avançado"""
        
        print("\nGerando Dashboard Técnico Avançado...")
        print("Incluindo: análise de portas, CVEs, vetores de ataque, compliance")
        
        # Análises adicionais
        port_analysis = self._analyze_ports(hosts)
        attack_vectors = self._identify_attack_vectors(vuln_summary)
        compliance_check = self._check_compliance(vuln_summary)
        risk_matrix = self._calculate_risk_matrix(vuln_summary)
        
        # Gerar análises com IA
        ai_technical_analysis = ""
        ai_penetration_test = ""
        ai_compliance_report = ""
        
        if self.use_ai and self.ai and self.ai.is_available():
            print("IA Detectada: Gerando análises técnicas detalhadas...")
            print("(Aguarde 60-90 segundos)")
            
            ai_technical_analysis = self._generate_technical_analysis(hosts, vuln_summary)
            ai_penetration_test = self._generate_penetration_test_scenario(vuln_summary)
            ai_compliance_report = self._generate_compliance_report(vuln_summary)
            
            print("Análises técnicas de IA concluídas!")
        else:
            print("Gerando dashboard sem análises de IA")
        
        # Gerar HTML
        html = self._build_html(
            hosts, vuln_summary, port_analysis, attack_vectors, 
            compliance_check, risk_matrix, ai_technical_analysis,
            ai_penetration_test, ai_compliance_report
        )
        
        # Salvar
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"Dashboard técnico gerado: {output_file}")
        return output_file
    
    def _analyze_ports(self, hosts: List[Dict]) -> Dict:
        """Analisa distribuição e categorização de portas"""
        analysis = {
            'total_ports': 0,
            'by_category': {'low': 0, 'registered': 0, 'dynamic': 0},
            'by_service': {},
            'encrypted': 0,
            'unencrypted': 0,
            'database_services': 0,
            'remote_access': 0
        }
        
        for host in hosts:
            for port_info in host['ports']:
                port_num = int(port_info['port'])
                service = port_info['service'].lower()
                
                analysis['total_ports'] += 1
                
                # Categorizar por faixa
                if port_num < 1024:
                    analysis['by_category']['low'] += 1
                elif port_num < 49152:
                    analysis['by_category']['registered'] += 1
                else:
                    analysis['by_category']['dynamic'] += 1
                
                # Contar por serviço
                if service not in analysis['by_service']:
                    analysis['by_service'][service] = 0
                analysis['by_service'][service] += 1
                
                # Classificar segurança
                if service in ['https', 'ssh', 'sftp']:
                    analysis['encrypted'] += 1
                elif service in ['http', 'ftp', 'telnet']:
                    analysis['unencrypted'] += 1
                
                # Serviços críticos
                if service in ['mysql', 'postgresql', 'mongodb', 'redis']:
                    analysis['database_services'] += 1
                if service in ['ssh', 'rdp', 'vnc', 'telnet']:
                    analysis['remote_access'] += 1
        
        return analysis
    
    def _identify_attack_vectors(self, vuln_summary: Dict) -> List[Dict]:
        """Identifica vetores de ataque baseados nas vulnerabilidades"""
        vectors = []
        
        for vuln in vuln_summary['vulnerabilities']:
            service = vuln['service'].lower()
            port = vuln['port']
            
            # Definir vetores específicos
            if service == 'telnet':
                vectors.append({
                    'name': 'Credential Interception',
                    'service': f'{service}:{port}',
                    'method': 'Man-in-the-Middle Attack',
                    'impact': 'CRÍTICO - Captura de credenciais em texto claro',
                    'mitigation': 'Desativar Telnet, migrar para SSH'
                })
            
            elif service in ['mysql', 'postgresql']:
                vectors.append({
                    'name': 'SQL Injection / Data Exfiltration',
                    'service': f'{service}:{port}',
                    'method': 'Direct database access',
                    'impact': 'CRÍTICO - Acesso não autorizado a dados',
                    'mitigation': 'Firewall rules, autenticação forte'
                })
            
            elif service == 'rdp':
                vectors.append({
                    'name': 'Brute Force Attack',
                    'service': f'{service}:{port}',
                    'method': 'Automated credential guessing',
                    'impact': 'ALTO - Acesso remoto ao sistema',
                    'mitigation': 'VPN, MFA, rate limiting'
                })
            
            elif service in ['smb', 'netbios-ssn']:
                vectors.append({
                    'name': 'Lateral Movement / Ransomware',
                    'service': f'{service}:{port}',
                    'method': 'SMB exploits (EternalBlue)',
                    'impact': 'CRÍTICO - Propagação de malware',
                    'mitigation': 'Patches de segurança, desativar SMBv1'
                })
        
        return vectors
    
    def _check_compliance(self, vuln_summary: Dict) -> Dict:
        """Verifica compliance com padrões de segurança"""
        compliance = {
            'CIS': {'score': 0, 'findings': []},
            'OWASP': {'score': 0, 'findings': []},
            'PCI-DSS': {'score': 0, 'findings': []},
            'NIST': {'score': 0, 'findings': []}
        }
        
        for vuln in vuln_summary['vulnerabilities']:
            service = vuln['service'].lower()
            severity = vuln['severity']
            
            # CIS Benchmarks
            if service in ['telnet', 'ftp'] and severity == 'ALTA':
                compliance['CIS']['findings'].append(
                    f"CIS Control 4.1: Protocolo inseguro detectado ({service})"
                )
            
            # OWASP
            if service in ['http'] and severity == 'MÉDIA':
                compliance['OWASP']['findings'].append(
                    "OWASP A02:2021 - Cryptographic Failures: HTTP sem TLS"
                )
            
            # PCI-DSS
            if service in ['mysql', 'postgresql'] and severity == 'ALTA':
                compliance['PCI-DSS']['findings'].append(
                    f"PCI-DSS 1.3: Database exposto sem segmentação adequada"
                )
            
            # NIST
            if service == 'rdp' and severity == 'ALTA':
                compliance['NIST']['findings'].append(
                    "NIST AC-17: Controle de acesso remoto inadequado"
                )
        
        # Calcular scores
        compliance['CIS']['score'] = max(0, 100 - len(compliance['CIS']['findings']) * 10)
        compliance['OWASP']['score'] = max(0, 100 - len(compliance['OWASP']['findings']) * 15)
        compliance['PCI-DSS']['score'] = max(0, 100 - len(compliance['PCI-DSS']['findings']) * 20)
        compliance['NIST']['score'] = max(0, 100 - len(compliance['NIST']['findings']) * 12)
        
        return compliance
    
    def _calculate_risk_matrix(self, vuln_summary: Dict) -> Dict:
        """Calcula matriz de risco técnica"""
        matrix = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': []
        }
        
        for vuln in vuln_summary['vulnerabilities']:
            # Calcular impacto e probabilidade
            impact = 3 if vuln['severity'] == 'ALTA' else 2 if vuln['severity'] == 'MÉDIA' else 1
            
            # Probabilidade baseada no tipo de serviço
            service = vuln['service'].lower()
            if service in ['telnet', 'ftp']:
                probability = 3  # Exploits públicos
            elif service in ['rdp', 'smb']:
                probability = 3  # Alvos comuns
            elif service in ['mysql', 'postgresql']:
                probability = 2  # Requer conhecimento
            else:
                probability = 1
            
            risk_score = impact * probability
            
            vuln_risk = {
                'service': f"{vuln['service']}:{vuln['port']}",
                'ip': vuln['ip'],
                'impact': impact,
                'probability': probability,
                'score': risk_score,
                'description': vuln['description']
            }
            
            if risk_score >= 7:
                matrix['critical'].append(vuln_risk)
            elif risk_score >= 5:
                matrix['high'].append(vuln_risk)
            elif risk_score >= 3:
                matrix['medium'].append(vuln_risk)
            else:
                matrix['low'].append(vuln_risk)
        
        return matrix
    
    def _generate_technical_analysis(self, hosts: List[Dict], vuln_summary: Dict) -> str:
        """Gera análise técnica profunda com IA"""
        
        services_list = []
        for host in hosts:
            for port in host['ports']:
                services_list.append(f"{port['service']}:{port['port']}")
        
        prompt = f"""Como analista de segurança sênior certificado (CISSP, CEH), forneça uma análise técnica DETALHADA desta infraestrutura:

INFRAESTRUTURA:
- {len(hosts)} hosts ativos
- Serviços: {', '.join(set(services_list[:10]))}
- {vuln_summary['total']} vulnerabilidades ({vuln_summary['alta']} críticas)

Forneça análise técnica em 3 seções:

1. ANÁLISE DE SUPERFÍCIE DE ATAQUE
   - Portas expostas e implicações
   - Serviços vulneráveis identificados
   
2. ANÁLISE DE EXPLOITABILIDADE
   - Facilidade de exploração
   - Ferramentas/técnicas de ataque aplicáveis
   
3. IMPACTO TÉCNICO
   - Consequências de comprometimento
   - Escalação de privilégios possível

Use terminologia técnica de infosec. Máximo 200 palavras. Sem formatação markdown."""
        
        return self.ai.generate(prompt)
    
    def _generate_penetration_test_scenario(self, vuln_summary: Dict) -> str:
        """Gera cenário de teste de penetração com IA"""
        
        critical_vulns = [v for v in vuln_summary['vulnerabilities'] if v['severity'] == 'ALTA'][:3]
        vulns_text = "\n".join([f"- {v['service']} ({v['ip']}:{v['port']})" for v in critical_vulns])
        
        prompt = f"""Como pentester certificado (OSCP), descreva um cenário de teste de penetração para estas vulnerabilidades:

{vulns_text}

Forneça:

1. FASE DE RECONHECIMENTO
   - Comandos e ferramentas

2. FASE DE EXPLORAÇÃO  
   - Técnicas específicas
   - Payloads/exploits

3. PÓS-EXPLORAÇÃO
   - Movimento lateral
   - Persistência

Use sintaxe de comandos reais (nmap, metasploit, etc). Máximo 180 palavras."""
        
        return self.ai.generate(prompt)
    
    def _generate_compliance_report(self, vuln_summary: Dict) -> str:
        """Gera relatório de compliance com IA"""
        
        prompt = f"""Como auditor de compliance (CISA, CISM), avalie o compliance baseado em {vuln_summary['total']} vulnerabilidades:

Críticas: {vuln_summary['alta']}
Médias: {vuln_summary['media']}  
Baixas: {vuln_summary['baixa']}

Avalie compliance com:

1. CIS Controls v8
2. NIST Cybersecurity Framework
3. ISO 27001

Para cada framework:
- Status de conformidade
- Controles falhando
- Prioridade de remediação

Linguagem de auditoria formal. Máximo 150 palavras."""
        
        return self.ai.generate(prompt)
    
    def _calculate_security_score(self, vuln_summary: Dict) -> int:
        """Calcula score de segurança"""
        penalties = {'alta': 15, 'media': 5, 'baixa': 2}
        total_penalty = (
            vuln_summary['alta'] * penalties['alta'] +
            vuln_summary['media'] * penalties['media'] +
            vuln_summary['baixa'] * penalties['baixa']
        )
        return max(0, 100 - total_penalty)
    
    def _get_score_color(self, score: int) -> str:
        """Retorna cor do score"""
        if score >= 80: return '#10b981'
        elif score >= 50: return '#f59e0b'
        else: return '#ef4444'
    
    def _get_score_status(self, score: int) -> str:
        """Retorna status do score"""
        if score >= 80: return 'SEGURO'
        elif score >= 50: return 'ATENÇÃO NECESSÁRIA'
        else: return 'CRÍTICO'
    
    def _build_html(self, hosts, vuln_summary, port_analysis, attack_vectors, 
                    compliance, risk_matrix, ai_technical, ai_pentest, ai_compliance):
        """Constrói HTML técnico avançado"""
        
        total_hosts = len(hosts)
        total_ports = port_analysis['total_ports']
        total_vulns = vuln_summary['total']
        security_score = self._calculate_security_score(vuln_summary)
        score_color = self._get_score_color(security_score)
        score_status = self._get_score_status(security_score)
        
        high_pct = (vuln_summary['alta'] / max(1, total_vulns)) * 100
        med_pct = (vuln_summary['media'] / max(1, total_vulns)) * 100
        low_pct = (vuln_summary['baixa'] / max(1, total_vulns)) * 100
        
        return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório Técnico de Segurança - {datetime.now().strftime('%d/%m/%Y')}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        :root {{
            --primary: #0f172a;
            --secondary: #1e293b;
            --accent: #3b82f6;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --text: #0f172a;
            --text-light: #64748b;
            --border: #e2e8f0;
            --bg: #f8fafc;
        }}
        
        body {{
            font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', monospace;
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            color: var(--text);
            line-height: 1.6;
            padding: 20px;
            font-size: 14px;
        }}
        
        .container {{
            max-width: 1600px;
            margin: 0 auto;
        }}
        
        header {{
            background: white;
            padding: 30px 40px;
            margin-bottom: 20px;
            border-radius: 4px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-left: 4px solid var(--primary);
        }}
        
        h1 {{
            font-size: 1.8em;
            color: var(--primary);
            margin-bottom: 8px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .subtitle {{
            color: var(--text-light);
            font-size: 0.9em;
            font-weight: 400;
        }}
        
        .classification {{
            display: inline-block;
            background: var(--danger);
            color: white;
            padding: 4px 12px;
            border-radius: 3px;
            font-size: 0.75em;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 10px;
        }}
        
        .meta-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid var(--border);
        }}
        
        .meta-item {{
            display: flex;
            flex-direction: column;
        }}
        
        .meta-label {{
            font-size: 0.7em;
            text-transform: uppercase;
            color: var(--text-light);
            letter-spacing: 0.5px;
            font-weight: 600;
        }}
        
        .meta-value {{
            font-size: 1em;
            font-weight: 600;
            color: var(--primary);
            font-family: monospace;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 4px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-top: 3px solid var(--accent);
        }}
        
        .stat-header {{
            font-size: 0.7em;
            text-transform: uppercase;
            color: var(--text-light);
            letter-spacing: 0.5px;
            margin-bottom: 10px;
            font-weight: 600;
        }}
        
        .stat-value {{
            font-size: 2.5em;
            font-weight: 700;
            color: var(--primary);
            font-family: monospace;
            margin-bottom: 5px;
        }}
        
        .stat-desc {{
            font-size: 0.75em;
            color: var(--text-light);
        }}
        
        .score-visual {{
            display: flex;
            align-items: center;
            gap: 20px;
        }}
        
        .score-circle {{
            width: 90px;
            height: 90px;
            border-radius: 50%;
            background: conic-gradient({score_color} {security_score * 3.6}deg, #e2e8f0 0deg);
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .score-inner {{
            width: 70px;
            height: 70px;
            background: white;
            border-radius: 50%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }}
        
        .score-number {{
            font-size: 1.6em;
            font-weight: 700;
            color: {score_color};
            font-family: monospace;
        }}
        
        .score-label {{
            font-size: 0.6em;
            color: var(--text-light);
        }}
        
        .score-status {{
            flex: 1;
        }}
        
        .score-badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 3px;
            font-size: 0.7em;
            font-weight: 600;
            background: {score_color};
            color: white;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 5px;
        }}
        
        .card {{
            background: white;
            padding: 25px;
            border-radius: 4px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .card h2 {{
            font-size: 1.1em;
            color: var(--primary);
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid var(--border);
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .grid-2 {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}
        
        .grid-3 {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}
        
        @media (max-width: 968px) {{
            .grid-2, .grid-3 {{
                grid-template-columns: 1fr;
            }}
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85em;
        }}
        
        th {{
            background: var(--bg);
            padding: 10px;
            text-align: left;
            font-size: 0.75em;
            font-weight: 700;
            color: var(--primary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 2px solid var(--border);
        }}
        
        td {{
            padding: 10px;
            border-bottom: 1px solid var(--border);
            font-family: monospace;
        }}
        
        tr:hover {{
            background: var(--bg);
        }}
        
        .badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 0.7em;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.3px;
        }}
        
        .badge-critical {{
            background: var(--danger);
            color: white;
        }}
        
        .badge-high {{
            background: var(--warning);
            color: white;
        }}
        
        .badge-medium {{
            background: var(--accent);
            color: white;
        }}
        
        .badge-low {{
            background: var(--success);
            color: white;
        }}
        
        .technical-block {{
            background: #1e293b;
            color: #e2e8f0;
            padding: 20px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 0.85em;
            margin: 15px 0;
            border-left: 4px solid var(--accent);
        }}
        
        .technical-block h3 {{
            color: #60a5fa;
            font-size: 0.9em;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .technical-block p {{
            margin-bottom: 10px;
            line-height: 1.6;
        }}
        
        .vuln-item {{
            padding: 15px;
            margin-bottom: 12px;
            border-radius: 4px;
            border-left: 4px solid;
            background: var(--bg);
        }}
        
        .vuln-item.critical {{
            border-color: var(--danger);
        }}
        
        .vuln-item.high {{
            border-color: var(--warning);
        }}
        
        .vuln-item.low {{
            border-color: var(--success);
        }}
        
        .vuln-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        
        .vuln-title {{
            font-weight: 700;
            color: var(--primary);
            font-family: monospace;
            font-size: 0.9em;
        }}
        
        .vuln-details {{
            font-size: 0.85em;
            color: var(--text-light);
            margin-bottom: 8px;
        }}
        
        .vuln-tech {{
            background: white;
            padding: 10px;
            border-radius: 3px;
            font-size: 0.8em;
            margin-top: 10px;
        }}
        
        .vuln-tech strong {{
            color: var(--accent);
            text-transform: uppercase;
            font-size: 0.75em;
            letter-spacing: 0.5px;
        }}
        
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        
        .metric-box {{
            text-align: center;
            padding: 15px;
            background: var(--bg);
            border-radius: 4px;
            border-top: 3px solid var(--accent);
        }}
        
        .metric-value {{
            font-size: 2em;
            font-weight: 700;
            color: var(--primary);
            font-family: monospace;
        }}
        
        .metric-label {{
            font-size: 0.7em;
            color: var(--text-light);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-top: 5px;
        }}
        
        .progress-bar {{
            width: 100%;
            height: 25px;
            background: #e2e8f0;
            border-radius: 4px;
            overflow: hidden;
            margin: 10px 0;
        }}
        
        .progress-fill {{
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 0.75em;
            font-weight: 600;
            transition: width 0.5s ease;
        }}
        
        .ai-section {{
            background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
            color: white;
            padding: 25px;
            border-radius: 4px;
            margin-bottom: 20px;
        }}
        
        .ai-section h2 {{
            color: white;
            border-bottom-color: rgba(255,255,255,0.3);
        }}
        
        .ai-content {{
            font-size: 0.9em;
            line-height: 1.8;
        }}
        
        .ai-content p {{
            margin-bottom: 12px;
        }}
        
        .command-block {{
            background: #0f172a;
            color: #10b981;
            padding: 12px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 0.8em;
            margin: 8px 0;
            overflow-x: auto;
        }}
        
        .command-block code {{
            color: #60a5fa;
        }}
        
        footer {{
            text-align: center;
            padding: 30px;
            color: white;
            margin-top: 40px;
        }}
        
        .timestamp {{
            background: rgba(255,255,255,0.1);
            padding: 8px 16px;
            border-radius: 4px;
            display: inline-block;
            font-size: 0.85em;
            font-family: monospace;
        }}
        
        .risk-matrix {{
            display: grid;
            grid-template-columns: auto 1fr 1fr 1fr;
            gap: 2px;
            background: var(--border);
            margin: 20px 0;
        }}
        
        .risk-cell {{
            background: white;
            padding: 15px;
            text-align: center;
            font-size: 0.85em;
        }}
        
        .risk-header {{
            background: var(--bg);
            font-weight: 700;
            color: var(--primary);
            text-transform: uppercase;
            font-size: 0.75em;
            letter-spacing: 0.5px;
        }}
        
        .risk-high {{
            background: #fee2e2;
            color: var(--danger);
            font-weight: 700;
        }}
        
        .risk-med {{
            background: #fef3c7;
            color: #92400e;
            font-weight: 600;
        }}
        
        .risk-low {{
            background: #dcfce7;
            color: #166534;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Relatório Técnico de Segurança de Infraestrutura</h1>
            <p class="subtitle">Análise Técnica Avançada de Vulnerabilidades e Riscos Cibernéticos</p>
            <span class="classification">CONFIDENCIAL - USO INTERNO</span>
            
            <div class="meta-grid">
                <div class="meta-item">
                    <span class="meta-label">Data de Scan</span>
                    <span class="meta-value">{datetime.now().strftime('%d/%m/%Y')}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Timestamp</span>
                    <span class="meta-value">{datetime.now().strftime('%H:%M:%S UTC')}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Scanner</span>
                    <span class="meta-value">Nmap 7.94 + NSE</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Metodologia</span>
                    <span class="meta-value">OWASP + NIST</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Scope</span>
                    <span class="meta-value">{total_hosts} Hosts Ativos</span>
                </div>
            </div>
        </header>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-header">Total de Hosts</div>
                <div class="stat-value">{total_hosts}</div>
                <div class="stat-desc">Dispositivos ativos identificados</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-header">Portas Abertas</div>
                <div class="stat-value">{total_ports}</div>
                <div class="stat-desc">Serviços em execução na rede</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-header">Vulnerabilidades</div>
                <div class="stat-value" style="color: var(--danger);">{total_vulns}</div>
                <div class="stat-desc">
                    <span class="badge badge-critical">{vuln_summary['alta']} Críticas</span>
                    <span class="badge badge-high">{vuln_summary['media']} Médias</span>
                    <span class="badge badge-low">{vuln_summary['baixa']} Baixas</span>
                </div>
            </div>
            
            <div class="stat-card">
                <div class="stat-header">Security Posture Score</div>
                <div class="score-visual">
                    <div class="score-circle">
                        <div class="score-inner">
                            <div class="score-number">{security_score}</div>
                            <div class="score-label">/100</div>
                        </div>
                    </div>
                    <div class="score-status">
                        <span class="score-badge">{score_status}</span>
                        <div class="stat-desc">Avaliação baseada em CVSS v3.1</div>
                    </div>
                </div>
            </div>
        </div>
        
        {self._generate_port_analysis_html(port_analysis)}
        {self._generate_compliance_html(compliance)}
        {self._generate_risk_matrix_html(risk_matrix)}
        {self._generate_attack_vectors_html(attack_vectors)}
        {self._generate_ai_sections_html(ai_technical, ai_pentest, ai_compliance)}
        {self._generate_vulnerabilities_detailed_html(vuln_summary)}
        {self._generate_hosts_technical_html(hosts)}
        
        <footer>
            <div class="timestamp">
                GENERATED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')} | CLASSIFICATION: CONFIDENTIAL
            </div>
            <p style="margin-top: 15px; font-size: 0.85em;">
                TCC - Segurança de Redes | Sistema Automatizado de Análise de Vulnerabilidades v2.0
            </p>
        </footer>
    </div>
</body>
</html>"""
    
    def _generate_port_analysis_html(self, analysis):
        """Gera HTML da análise de portas"""
        return f"""
        <div class="card">
            <h2>Análise Técnica de Portas e Serviços</h2>
            
            <div class="metric-grid">
                <div class="metric-box">
                    <div class="metric-value">{analysis['total_ports']}</div>
                    <div class="metric-label">Total de Portas</div>
                </div>
                <div class="metric-box">
                    <div class="metric-value">{analysis['encrypted']}</div>
                    <div class="metric-label">Serviços Criptografados</div>
                </div>
                <div class="metric-box">
                    <div class="metric-value">{analysis['unencrypted']}</div>
                    <div class="metric-label">Serviços Sem Criptografia</div>
                </div>
                <div class="metric-box">
                    <div class="metric-value">{analysis['database_services']}</div>
                    <div class="metric-label">Bancos de Dados Expostos</div>
                </div>
                <div class="metric-box">
                    <div class="metric-value">{analysis['remote_access']}</div>
                    <div class="metric-label">Acesso Remoto Ativo</div>
                </div>
            </div>
            
            <h3 style="margin-top: 20px; font-size: 0.9em; color: var(--primary); text-transform: uppercase;">Distribuição por Categoria IANA</h3>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {(analysis['by_category']['low'] / max(1, analysis['total_ports'])) * 100}%; background: var(--danger);">
                    Well-Known (0-1023): {analysis['by_category']['low']}
                </div>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {(analysis['by_category']['registered'] / max(1, analysis['total_ports'])) * 100}%; background: var(--warning);">
                    Registered (1024-49151): {analysis['by_category']['registered']}
                </div>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {(analysis['by_category']['dynamic'] / max(1, analysis['total_ports'])) * 100}%; background: var(--success);">
                    Dynamic/Private (49152+): {analysis['by_category']['dynamic']}
                </div>
            </div>
            
            <h3 style="margin-top: 20px; font-size: 0.9em; color: var(--primary); text-transform: uppercase;">Serviços Identificados</h3>
            <table>
                <thead>
                    <tr>
                        <th>Serviço</th>
                        <th>Instâncias</th>
                        <th>Status de Segurança</th>
                    </tr>
                </thead>
                <tbody>
                    {self._generate_service_rows_html(analysis['by_service'])}
                </tbody>
            </table>
        </div>
        """
    
    def _generate_service_rows_html(self, services):
        """Gera linhas de serviços"""
        rows = ""
        for service, count in sorted(services.items(), key=lambda x: x[1], reverse=True):
            security_status = "SEGURO" if service in ['https', 'ssh'] else "ATENÇÃO" if service in ['http', 'ftp'] else "CRÍTICO" if service in ['telnet'] else "REVISAR"
            badge_class = "badge-low" if security_status == "SEGURO" else "badge-high" if security_status == "ATENÇÃO" else "badge-critical"
            
            rows += f"""
            <tr>
                <td><strong>{service.upper()}</strong></td>
                <td>{count}</td>
                <td><span class="badge {badge_class}">{security_status}</span></td>
            </tr>
            """
        return rows
    
    def _generate_compliance_html(self, compliance):
        """Gera HTML de compliance"""
        return f"""
        <div class="card">
            <h2>Análise de Compliance e Conformidade</h2>
            
            <div class="grid-2">
                <div>
                    <h3 style="font-size: 0.9em; color: var(--primary); margin-bottom: 10px;">CIS Controls v8</h3>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {compliance['CIS']['score']}%; background: {self._get_score_color(compliance['CIS']['score'])};">
                            {compliance['CIS']['score']}% Conformidade
                        </div>
                    </div>
                    <ul style="margin-top: 10px; font-size: 0.85em; color: var(--text-light);">
                        {self._generate_findings_list(compliance['CIS']['findings'])}
                    </ul>
                </div>
                
                <div>
                    <h3 style="font-size: 0.9em; color: var(--primary); margin-bottom: 10px;">OWASP Top 10</h3>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {compliance['OWASP']['score']}%; background: {self._get_score_color(compliance['OWASP']['score'])};">
                            {compliance['OWASP']['score']}% Conformidade
                        </div>
                    </div>
                    <ul style="margin-top: 10px; font-size: 0.85em; color: var(--text-light);">
                        {self._generate_findings_list(compliance['OWASP']['findings'])}
                    </ul>
                </div>
            </div>
            
            <div class="grid-2" style="margin-top: 20px;">
                <div>
                    <h3 style="font-size: 0.9em; color: var(--primary); margin-bottom: 10px;">PCI-DSS 3.2.1</h3>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {compliance['PCI-DSS']['score']}%; background: {self._get_score_color(compliance['PCI-DSS']['score'])};">
                            {compliance['PCI-DSS']['score']}% Conformidade
                        </div>
                    </div>
                    <ul style="margin-top: 10px; font-size: 0.85em; color: var(--text-light);">
                        {self._generate_findings_list(compliance['PCI-DSS']['findings'])}
                    </ul>
                </div>
                
                <div>
                    <h3 style="font-size: 0.9em; color: var(--primary); margin-bottom: 10px;">NIST CSF</h3>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {compliance['NIST']['score']}%; background: {self._get_score_color(compliance['NIST']['score'])};">
                            {compliance['NIST']['score']}% Conformidade
                        </div>
                    </div>
                    <ul style="margin-top: 10px; font-size: 0.85em; color: var(--text-light);">
                        {self._generate_findings_list(compliance['NIST']['findings'])}
                    </ul>
                </div>
            </div>
        </div>
        """
    
    def _generate_findings_list(self, findings):
        """Gera lista de findings"""
        if not findings:
            return "<li>✓ Nenhuma não-conformidade identificada</li>"
        return "".join([f"<li>✗ {finding}</li>" for finding in findings[:3]])
    
    def _generate_risk_matrix_html(self, matrix):
        """Gera matriz de risco"""
        return f"""
        <div class="card">
            <h2>Matriz de Risco Técnico</h2>
            
            <div class="risk-matrix">
                <div class="risk-cell risk-header"></div>
                <div class="risk-cell risk-header">Baixa Probabilidade</div>
                <div class="risk-cell risk-header">Média Probabilidade</div>
                <div class="risk-cell risk-header">Alta Probabilidade</div>
                
                <div class="risk-cell risk-header">Alto Impacto</div>
                <div class="risk-cell risk-med">{len([r for r in matrix['medium'] if r['impact'] == 3])}</div>
                <div class="risk-cell risk-high">{len([r for r in matrix['high'] if r['impact'] == 3])}</div>
                <div class="risk-cell risk-high">{len([r for r in matrix['critical'] if r['impact'] == 3])}</div>
                
                <div class="risk-cell risk-header">Médio Impacto</div>
                <div class="risk-cell risk-low">{len([r for r in matrix['low'] if r['impact'] == 2])}</div>
                <div class="risk-cell risk-med">{len([r for r in matrix['medium'] if r['impact'] == 2])}</div>
                <div class="risk-cell risk-high">{len([r for r in matrix['high'] if r['impact'] == 2])}</div>
                
                <div class="risk-cell risk-header">Baixo Impacto</div>
                <div class="risk-cell risk-low">{len([r for r in matrix['low'] if r['impact'] == 1])}</div>
                <div class="risk-cell risk-low">{len([r for r in matrix['medium'] if r['impact'] == 1])}</div>
                <div class="risk-cell risk-med">{len([r for r in matrix['high'] if r['impact'] == 1])}</div>
            </div>
            
            <div style="margin-top: 20px;">
                <h3 style="font-size: 0.9em; color: var(--danger); margin-bottom: 15px; text-transform: uppercase;">Riscos Críticos (Score ≥ 7)</h3>
                {self._generate_risk_items_html(matrix['critical'][:5])}
            </div>
        </div>
        """
    
    def _generate_risk_items_html(self, risks):
        """Gera itens de risco"""
        if not risks:
            return "<p style='color: var(--success);'>✓ Nenhum risco crítico identificado</p>"
        
        html = ""
        for risk in risks:
            html += f"""
            <div class="vuln-item critical">
                <div class="vuln-header">
                    <span class="vuln-title">{risk['service']} @ {risk['ip']}</span>
                    <span class="badge badge-critical">SCORE: {risk['score']}</span>
                </div>
                <div class="vuln-details">
                    <strong>Impacto:</strong> {risk['impact']}/3 | <strong>Probabilidade:</strong> {risk['probability']}/3
                </div>
                <div class="vuln-details">{risk['description']}</div>
            </div>
            """
        return html
    
    def _generate_attack_vectors_html(self, vectors):
        """Gera HTML de vetores de ataque"""
        if not vectors:
            return ""
        
        return f"""
        <div class="card">
            <h2>Vetores de Ataque Identificados</h2>
            
            {self._generate_vector_items_html(vectors[:10])}
        </div>
        """
    
    def _generate_vector_items_html(self, vectors):
        """Gera itens de vetores"""
        html = ""
        for vector in vectors:
            html += f"""
            <div class="technical-block">
                <h3>⚠ {vector['name']}</h3>
                <p><strong>Alvo:</strong> {vector['service']}</p>
                <p><strong>Método:</strong> {vector['method']}</p>
                <p><strong>Impacto:</strong> {vector['impact']}</p>
                <p><strong>Mitigação:</strong> {vector['mitigation']}</p>
            </div>
            """
        return html
    
    def _generate_ai_sections_html(self, technical, pentest, compliance):
        """Gera seções de IA"""
        if not technical and not pentest and not compliance:
            return ""
        
        html = ""
        
        if technical:
            html += f"""
            <div class="ai-section">
                <h2>Análise Técnica Avançada (IA)</h2>
                <div class="ai-content">{self._format_text(technical)}</div>
            </div>
            """
        
        if pentest:
            html += f"""
            <div class="ai-section">
                <h2>Cenário de Teste de Penetração (IA)</h2>
                <div class="ai-content">{self._format_pentest(pentest)}</div>
            </div>
            """
        
        if compliance:
            html += f"""
            <div class="ai-section">
                <h2>Relatório de Compliance (IA)</h2>
                <div class="ai-content">{self._format_text(compliance)}</div>
            </div>
            """
        
        return html
    
    def _format_text(self, text):
        """Formata texto"""
        paragraphs = text.strip().split('\n\n')
        return "".join([f"<p>{p.strip()}</p>" for p in paragraphs if p.strip()])
    
    def _format_pentest(self, text):
        """Formata texto de pentest"""
        lines = text.strip().split('\n')
        formatted = ""
        in_command = False
        
        for line in lines:
            if 'nmap' in line.lower() or 'metasploit' in line.lower() or '$' in line or '#' in line:
                formatted += f'<div class="command-block">{line}</div>'
            elif line.strip():
                formatted += f'<p>{line}</p>'
        
        return formatted
    
    def _generate_vulnerabilities_detailed_html(self, vuln_summary):
        """Gera HTML detalhado de vulnerabilidades"""
        return f"""
        <div class="card">
            <h2>Inventário Completo de Vulnerabilidades</h2>
            
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Host:Porta</th>
                        <th>Serviço</th>
                        <th>Versão</th>
                        <th>Severidade</th>
                        <th>CVE Relacionados</th>
                        <th>Recomendação</th>
                    </tr>
                </thead>
                <tbody>
                    {self._generate_vuln_rows_html(vuln_summary['vulnerabilities'])}
                </tbody>
            </table>
        </div>
        """
    
    def _generate_vuln_rows_html(self, vulnerabilities):
        """Gera linhas de vulnerabilidades"""
        rows = ""
        for idx, vuln in enumerate(vulnerabilities, 1):
            badge_class = "badge-critical" if vuln['severity'] == 'ALTA' else "badge-high" if vuln['severity'] == 'MÉDIA' else "badge-low"
            service = vuln['service'].lower()
            cves = ', '.join(self.KNOWN_CVES.get(service, ['N/A'])[:2])
            
            rows += f"""
            <tr>
                <td><strong>V-{idx:03d}</strong></td>
                <td>{vuln['ip']}:{vuln['port']}</td>
                <td>{vuln['service'].upper()}</td>
                <td>{vuln['product']} {vuln['version']}</td>
                <td><span class="badge {badge_class}">{vuln['severity']}</span></td>
                <td><small>{cves}</small></td>
                <td><small>{vuln['recommendation'][:50]}...</small></td>
            </tr>
            """
        return rows
    
    def _generate_hosts_technical_html(self, hosts):
        """Gera HTML técnico de hosts"""
        return f"""
        <div class="card">
            <h2>Inventário Técnico de Hosts</h2>
            
            <table>
                <thead>
                    <tr>
                        <th>Hostname</th>
                        <th>IP Address</th>
                        <th>Operating System</th>
                        <th>Open Ports</th>
                        <th>Services</th>
                        <th>Risk Level</th>
                    </tr>
                </thead>
                <tbody>
                    {self._generate_host_rows_html(hosts)}
                </tbody>
            </table>
        </div>
        """
    
    def _generate_host_rows_html(self, hosts):
        """Gera linhas de hosts"""
        rows = ""
        for host in hosts:
            services = ", ".join([f"{p['port']}/{p['service']}" for p in host['ports'][:5]])
            risk_level = "ALTO" if host['total_ports'] > 10 else "MÉDIO" if host['total_ports'] > 5 else "BAIXO"
            badge_class = "badge-critical" if risk_level == "ALTO" else "badge-high" if risk_level == "MÉDIO" else "badge-low"
            
            rows += f"""
            <tr>
                <td><strong>{host['hostname']}</strong></td>
                <td>{host['ip']}</td>
                <td>{host['os'][:40]}</td>
                <td>{host['total_ports']}</td>
                <td><small>{services}</small></td>
                <td><span class="badge {badge_class}">{risk_level}</span></td>
            </tr>
            """
        return rows


def generate_technical_dashboard(hosts: List[Dict], vuln_summary: Dict, use_ai: bool = True, output_file: str = "dashboard.html"):
    """Função principal para gerar dashboard técnico"""
    dashboard = TechnicalDashboard(use_ai=use_ai)
    return dashboard.generate(hosts, vuln_summary, output_file=output_file)


if __name__ == "__main__":
    print("Dashboard Técnico Avançado - Sistema de Análise de Segurança")
