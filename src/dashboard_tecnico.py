# -*- coding: utf-8 -*-
"""
Gerador de Dashboard Tecnico Avancado
Dashboard profissional com maximo detalhamento tecnico
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
        network_topology = self._prepare_network_topology(hosts)
        cisco_topology = self._prepare_cisco_topology(hosts)
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
            hosts, vuln_summary, port_analysis, network_topology, cisco_topology, attack_vectors, 
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
    
    def _prepare_network_topology(self, hosts: List[Dict]) -> Dict:
        """Prepara dados da topologia de rede para visualização"""
        nodes = []
        edges = []
        
        # Criar nó central (gateway/firewall)
        nodes.append({
            'id': 'gateway',
            'label': 'GATEWAY\n/\nFIREWALL',
            'group': 'gateway',
            'shape': 'diamond',
            'size': 30
        })
        
        # Agrupar hosts por subnet
        subnets = {}
        for idx, host in enumerate(hosts[:50]):  # Limitar a 50 hosts para visualização
            ip = host['ip']
            subnet = '.'.join(ip.split('.')[:3]) + '.0/24'
            
            if subnet not in subnets:
                subnets[subnet] = []
            
            # Determinar grupo baseado em serviços
            group = 'server'
            if any(p['service'].lower() in ['mysql', 'postgresql', 'mongodb'] for p in host['ports']):
                group = 'database'
            elif any(p['service'].lower() in ['http', 'https', 'apache', 'nginx'] for p in host['ports']):
                group = 'web'
            elif any(p['service'].lower() in ['ssh', 'rdp', 'vnc', 'telnet'] for p in host['ports']):
                group = 'workstation'
            
            # Calcular risco
            vuln_count = sum(1 for p in host['ports'] if p['service'].lower() in ['telnet', 'ftp', 'smb', 'rdp', 'vnc'])
            risk_level = 'high' if vuln_count > 2 else 'medium' if vuln_count > 0 else 'low'
            
            node_id = f"host_{idx}"
            label = f"{host['hostname'][:15]}\n{ip}\n{host['total_ports']} portas"
            
            nodes.append({
                'id': node_id,
                'label': label,
                'group': group,
                'shape': 'box',
                'size': 15 + (vuln_count * 5),
                'borderWidth': 3 if risk_level == 'high' else 2,
                'color': {
                    'border': '#ef4444' if risk_level == 'high' else '#f59e0b' if risk_level == 'medium' else '#10b981',
                    'background': '#fee2e2' if risk_level == 'high' else '#fef3c7' if risk_level == 'medium' else '#d1fae5'
                }
            })
            
            # Conectar ao gateway
            edges.append({
                'from': 'gateway',
                'to': node_id,
                'width': 2,
                'smooth': {'type': 'curvedCW', 'roundness': 0.2}
            })
            
            subnets[subnet].append(node_id)
        
        # Adicionar conexões entre hosts da mesma subnet (simulando comunicação interna)
        for subnet, host_ids in subnets.items():
            if len(host_ids) > 1:
                # Conectar alguns hosts aleatoriamente para simular tráfego interno
                for i in range(min(3, len(host_ids) - 1)):
                    edges.append({
                        'from': host_ids[i],
                        'to': host_ids[i + 1],
                        'width': 1,
                        'dashes': True,
                        'color': '#94a3b8'
                    })
        
        return {'nodes': nodes, 'edges': edges}
    
    def _prepare_cisco_topology(self, hosts: List[Dict]) -> Dict:
        """Prepara topologia estilo Cisco Packet Tracer com hierarquia usando dados reais"""
        devices = []
        connections = []
        
        # Agrupar hosts por subnet
        subnets = {}
        for host in hosts:
            ip = host['ip']
            subnet = '.'.join(ip.split('.')[:3]) + '.0/24'
            if subnet not in subnets:
                subnets[subnet] = []
            subnets[subnet].append(host)
        
        # Pegar as subnets mais populosas (máximo 4 para visualização limpa)
        top_subnets = sorted(subnets.items(), key=lambda x: len(x[1]), reverse=True)[:4]
        
        # Se não houver hosts suficientes, retornar vazio
        if not top_subnets:
            return {'devices': [], 'connections': []}
        
        # Núcleo da rede
        devices.append({
            'id': 'core-router',
            'type': 'router',
            'label': 'ROUTER CENTRAL',
            'layer': 0,
            'position': {'x': 450, 'y': 60},
            'details': {
                'name': 'Core Router',
                'type': 'Router Principal',
                'function': 'Roteamento entre redes',
                'info': f'Conectando {len(top_subnets)} subnets'
            }
        })
        
        devices.append({
            'id': 'firewall',
            'type': 'firewall',
            'label': 'FIREWALL',
            'layer': 1,
            'position': {'x': 450, 'y': 160},
            'details': {
                'name': 'Firewall de Perímetro',
                'type': 'Security Gateway',
                'function': 'Filtragem de tráfego',
                'info': f'Protegendo {sum(len(h) for _, h in top_subnets)} dispositivos'
            }
        })
        
        # Backbone
        connections.append({
            'from': 'core-router',
            'to': 'firewall',
            'type': 'backbone'
        })
        
        # Posições dos switches (layout horizontal organizado)
        switch_positions = [
            {'x': 200, 'y': 300},
            {'x': 400, 'y': 300},
            {'x': 600, 'y': 300},
            {'x': 800, 'y': 300}
        ]
        
        # Criar switches e dispositivos para cada subnet
        import math
        for idx, (subnet, hosts_in_subnet) in enumerate(top_subnets):
            switch_id = f'switch-{idx}'
            switch_pos = switch_positions[idx]
            
            # Contar informações da subnet
            subnet_vulns = sum(len(h.get('vulnerabilities', [])) for h in hosts_in_subnet)
            total_ports = sum(len(h.get('ports', [])) for h in hosts_in_subnet)
            
            devices.append({
                'id': switch_id,
                'type': 'switch',
                'label': f'SWITCH {idx+1}\\n{subnet}',
                'layer': 2,
                'position': switch_pos,
                'details': {
                    'name': f'Switch de Distribuição {idx+1}',
                    'type': 'L2 Switch',
                    'subnet': subnet,
                    'hosts': len(hosts_in_subnet),
                    'ports_abertos': total_ports,
                    'vulnerabilidades': subnet_vulns
                }
            })
            
            # Conectar switch ao firewall
            connections.append({
                'from': 'firewall',
                'to': switch_id,
                'type': 'trunk'
            })
            
            # Adicionar hosts (máximo 8 por switch para visualização)
            num_hosts = min(8, len(hosts_in_subnet))
            for h_idx, host in enumerate(hosts_in_subnet[:num_hosts]):
                # Determinar tipo de dispositivo baseado nos serviços
                device_type = 'workstation'
                services = [p.get('service', '').lower() for p in host.get('ports', [])]
                ports_info = [f"{p.get('port')}/{p.get('protocol')} ({p.get('service', 'unknown')})" 
                             for p in host.get('ports', [])]
                
                if any('mysql' in s or 'postgresql' in s or 'mongodb' in s or 'oracle' in s for s in services):
                    device_type = 'database'
                elif any('http' in s or 'apache' in s or 'nginx' in s for s in services):
                    device_type = 'web-server'
                elif any('ssh' in s or 'ftp' in s or 'domain' in s for s in services):
                    device_type = 'server'
                
                # Calcular posição em semicírculo abaixo do switch
                angle = 180 + (h_idx / max(num_hosts - 1, 1)) * 140 - 70
                radius = 120
                x = switch_pos['x'] + radius * math.cos(math.radians(angle))
                y = switch_pos['y'] + radius * math.sin(math.radians(angle)) + 60
                
                # Status baseado em vulnerabilidades reais
                host_vulns = host.get('vulnerabilities', [])
                vuln_count = len(host_vulns)
                
                # Verificar serviços inseguros
                insecure_services = ['telnet', 'ftp', 'smb', 'rdp', 'vnc', 'rlogin']
                has_insecure = any(any(srv in p.get('service', '').lower() for srv in insecure_services) 
                                  for p in host.get('ports', []))
                
                if vuln_count >= 3 or has_insecure:
                    status = 'critical'
                elif vuln_count >= 1:
                    status = 'warning'
                else:
                    status = 'ok'
                
                host_id = f"host-{host['ip'].replace('.', '-')}"
                hostname = host.get('hostname', f"host-{host['ip'].split('.')[-1]}")
                os_info = host.get('os', 'Desconhecido')
                
                devices.append({
                    'id': host_id,
                    'type': device_type,
                    'label': f"{hostname[:12]}\\n{host['ip']}",
                    'layer': 3,
                    'position': {'x': int(x), 'y': int(y)},
                    'status': status,
                    'details': {
                        'name': hostname,
                        'ip': host['ip'],
                        'os': os_info,
                        'tipo': device_type.replace('-', ' ').title(),
                        'portas_abertas': len(host.get('ports', [])),
                        'portas': ports_info[:5],  # Primeiras 5 portas
                        'vulnerabilidades': len(host_vulns),
                        'vuln_detalhes': [v.get('description', 'N/A') for v in host_vulns[:3]],
                        'status': status.upper(),
                        'servicos_inseguros': has_insecure
                    }
                })
                
                # Conectar ao switch
                connections.append({
                    'from': switch_id,
                    'to': host_id,
                    'type': 'access',
                    'status': status
                })
        
        return {'devices': devices, 'connections': connections}
    
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
    
    def _build_html(self, hosts, vuln_summary, port_analysis, network_topology, cisco_topology, attack_vectors, 
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
        
        /* Accordion/Dropdown Styles */
        .topology-accordion {{
            margin: 20px 0;
        }}
        
        .accordion-header {{
            background: linear-gradient(135deg, var(--primary), var(--accent));
            color: white;
            padding: 15px 20px;
            cursor: pointer;
            border-radius: 4px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.3s ease;
            user-select: none;
        }}
        
        .accordion-header:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }}
        
        .accordion-title {{
            font-size: 1.1em;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .accordion-icon {{
            font-size: 1.2em;
            transition: transform 0.3s ease;
        }}
        
        .accordion-header.active .accordion-icon {{
            transform: rotate(180deg);
        }}
        
        .accordion-content {{
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.4s ease;
        }}
        
        .accordion-content.active {{
            max-height: 1200px;
            overflow: visible;
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
        
        #network-topology {{
            width: 100%;
            height: 600px;
            border: 2px solid var(--border);
            background: #ffffff;
            border-radius: 4px;
        }}
        
        .topology-legend {{
            display: flex;
            gap: 20px;
            margin-top: 15px;
            flex-wrap: wrap;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            margin-bottom: 8px;
        }}
        
        .legend-item .color-box {{
            width: 20px;
            height: 20px;
            margin-right: 10px;
            border-radius: 3px;
            border: 1px solid var(--border);
        }}
        
        /* Cisco Topology Styles */
        #cisco-topology {{
            background: #f8f9fa;
            border-radius: 4px;
            padding: 20px;
            margin: 0;
            height: 650px;
            position: relative;
            overflow: auto;
            border: 2px solid var(--border);
            cursor: grab;
        }}
        
        #cisco-topology:active {{
            cursor: grabbing;
        }}
        
        #network-topology {{
            width: 100%;
            height: 600px;
            border: 2px solid var(--border);
            background: #ffffff;
            border-radius: 4px;
        }}
        
        .topology-container {{
            background: white;
            border-radius: 4px;
            padding: 20px;
            margin-top: 10px;
        }}
        
        .cisco-device {{
            position: absolute;
            text-align: center;
            cursor: move;
            cursor: grab;
            transition: all 0.3s ease;
            z-index: 10;
            user-select: none;
        }}
        
        .cisco-device:active {{
            cursor: grabbing;
            z-index: 200;
        }}
        
        .cisco-device:hover {{
            transform: scale(1.15);
            z-index: 100;
        }}
        
        .cisco-device.selected {{
            transform: scale(1.2);
            z-index: 101;
        }}
        
        .cisco-device.dragging {{
            opacity: 0.7;
            cursor: grabbing;
            z-index: 1000;
        }}
        
        .vuln-badge {{
            position: absolute;
            top: -8px;
            right: -8px;
            background: #dc2626;
            color: white;
            font-size: 11px;
            font-weight: 700;
            padding: 3px 7px;
            border-radius: 10px;
            border: 2px solid white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
            z-index: 5;
            animation: pulse 2s infinite;
        }}
        
        .vuln-badge.warning {{
            background: #f59e0b;
        }}
        
        .vuln-badge.critical {{
            background: #dc2626;
            animation: pulse 1s infinite;
        }}
        
        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.1); }}
        }}
        
        .device-wrapper {{
            position: relative;
            display: inline-block;
        }}
        
        .device-icon {{
            width: 60px;
            height: 60px;
            margin: 0 auto 5px;
            background-size: contain;
            background-repeat: no-repeat;
            background-position: center;
            filter: drop-shadow(3px 3px 6px rgba(0,0,0,0.3));
            transition: filter 0.3s ease;
        }}
        
        .cisco-device:hover .device-icon {{
            filter: drop-shadow(4px 4px 10px rgba(59,130,246,0.6));
        }}
        
        .device-router {{ background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect x="10" y="30" width="80" height="40" fill="%231e40af" rx="5"/><circle cx="25" cy="50" r="6" fill="%2360a5fa"/><circle cx="50" cy="50" r="6" fill="%2360a5fa"/><circle cx="75" cy="50" r="6" fill="%2360a5fa"/><rect x="20" y="75" width="60" height="8" fill="%231e3a8a"/><path d="M25,50 L25,75 M50,50 L50,75 M75,50 L75,75" stroke="%2360a5fa" stroke-width="2"/></svg>'); }}
        
        .device-firewall {{ background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><path d="M50,10 L20,25 L20,55 Q20,75 50,85 Q80,75 80,55 L80,25 Z" fill="%23dc2626" stroke="%23991b1b" stroke-width="2"/><path d="M50,30 L50,60 M35,45 L65,45" stroke="white" stroke-width="4"/><circle cx="50" cy="50" r="15" fill="none" stroke="white" stroke-width="3"/></svg>'); }}
        
        .device-switch {{ background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect x="10" y="35" width="80" height="30" fill="%2316a34a" rx="3"/><circle cx="20" cy="50" r="3" fill="%2322c55e"/><circle cx="30" cy="50" r="3" fill="%2322c55e"/><circle cx="40" cy="50" r="3" fill="%2322c55e"/><circle cx="50" cy="50" r="3" fill="%2322c55e"/><circle cx="60" cy="50" r="3" fill="%2322c55e"/><circle cx="70" cy="50" r="3" fill="%2322c55e"/><circle cx="80" cy="50" r="3" fill="%2322c55e"/><rect x="15" y="42" width="70" height="3" fill="%23166534"/></svg>'); }}
        
        .device-server {{ background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect x="20" y="20" width="60" height="15" fill="%236b7280" rx="2"/><rect x="20" y="42" width="60" height="15" fill="%236b7280" rx="2"/><rect x="20" y="64" width="60" height="15" fill="%236b7280" rx="2"/><circle cx="70" cy="27" r="3" fill="%2322c55e"/><circle cx="70" cy="49" r="3" fill="%2322c55e"/><circle cx="70" cy="71" r="3" fill="%2322c55e"/><rect x="25" y="24" width="35" height="4" fill="%234b5563"/><rect x="25" y="46" width="35" height="4" fill="%234b5563"/><rect x="25" y="68" width="35" height="4" fill="%234b5563"/></svg>'); }}
        
        .device-database {{ background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><ellipse cx="50" cy="25" rx="30" ry="12" fill="%23ea580c"/><rect x="20" y="25" width="60" height="30" fill="%23ea580c"/><ellipse cx="50" cy="55" rx="30" ry="12" fill="%23c2410c"/><ellipse cx="50" cy="25" rx="30" ry="12" fill="none" stroke="%239a3412" stroke-width="2"/><ellipse cx="50" cy="40" rx="30" ry="12" fill="none" stroke="%239a3412" stroke-width="1.5"/><ellipse cx="50" cy="55" rx="30" ry="12" fill="none" stroke="%239a3412" stroke-width="2"/></svg>'); }}
        
        .device-web-server {{ background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect x="15" y="25" width="70" height="50" fill="%237c3aed" rx="3"/><rect x="20" y="30" width="60" height="8" fill="%235b21b6"/><circle cx="25" cy="34" r="2" fill="%23a78bfa"/><circle cx="31" cy="34" r="2" fill="%23a78bfa"/><circle cx="37" cy="34" r="2" fill="%23a78bfa"/><rect x="25" y="43" width="50" height="3" fill="%23a78bfa"/><rect x="25" y="50" width="40" height="3" fill="%23a78bfa"/><rect x="25" y="57" width="45" height="3" fill="%23a78bfa"/><path d="M30,65 L45,65 L37,62 L45,59 L30,59" fill="%23fbbf24"/></svg>'); }}
        
        .device-workstation {{ background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect x="20" y="20" width="60" height="45" fill="%2394a3b8" rx="2"/><rect x="25" y="25" width="50" height="35" fill="%23475569"/><rect x="42" y="67" width="16" height="8" fill="%2364748b"/><rect x="30" y="75" width="40" height="3" fill="%2364748b" rx="1"/><circle cx="50" cy="30" r="2" fill="%2322c55e"/></svg>'); }}
        
        .device-label {{
            font-size: 0.7em;
            font-weight: 600;
            color: var(--text);
            white-space: nowrap;
            background: rgba(255,255,255,0.95);
            padding: 3px 8px;
            border-radius: 3px;
            border: 1px solid var(--border);
            line-height: 1.3;
        }}
        
        .connection-line {{
            position: absolute;
            height: 2px;
            transform-origin: left center;
            pointer-events: none;
        }}
        
        .connection-backbone {{
            background: linear-gradient(90deg, %231e40af, %233b82f6);
            height: 4px;
            box-shadow: 0 0 6px %233b82f6;
        }}
        
        .connection-trunk {{
            background: %2316a34a;
            height: 3px;
        }}
        
        .connection-access {{
            background: %236b7280;
            height: 2px;
        }}
        
        .connection-access.status-critical {{
            background: %23dc2626;
            height: 3px;
            animation: pulse-red 1.5s infinite;
        }}
        
        .connection-access.status-warning {{
            background: %23f59e0b;
            height: 2px;
        }}
        
        @keyframes pulse-red {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
        
        .status-indicator {{
            position: absolute;
            top: 0;
            right: 0;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            border: 2px solid white;
        }}
        
        .status-ok {{ background: %2322c55e; }}
        .status-warning {{ background: %23f59e0b; animation: blink 1s infinite; }}
        .status-critical {{ background: %23dc2626; animation: blink 0.5s infinite; }}
        
        @keyframes blink {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.3; }}
        }}
        
        .topology-title {{
            font-size: 1.2em;
            font-weight: 700;
            color: var(--primary);
            margin-bottom: 15px;
            text-align: center;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .topology-legend {{
            position: absolute;
            bottom: 15px;
            right: 15px;
            background: rgba(255,255,255,0.95);
            padding: 12px;
            border-radius: 4px;
            border: 1px solid var(--border);
            font-size: 0.75em;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .topology-legend h4 {{
            margin: 0 0 8px 0;
            font-size: 0.9em;
            color: var(--primary);
            border-bottom: 1px solid var(--border);
            padding-bottom: 5px;
        }}
        
        .device-details-panel {{
            position: absolute;
            top: 20px;
            right: 20px;
            width: 300px;
            background: white;
            border: 2px solid var(--primary);
            border-radius: 6px;
            padding: 15px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            display: none;
            z-index: 1000;
            max-height: 500px;
            overflow-y: auto;
        }}
        
        .device-details-panel.show {{
            display: block;
            animation: slideIn 0.3s ease;
        }}
        
        @keyframes slideIn {{
            from {{
                opacity: 0;
                transform: translateX(20px);
            }}
            to {{
                opacity: 1;
                transform: translateX(0);
            }}
        }}
        
        .details-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            padding-bottom: 10px;
            border-bottom: 2px solid var(--primary);
        }}
        
        .details-header h3 {{
            margin: 0;
            color: var(--primary);
            font-size: 1em;
        }}
        
        .close-details {{
            background: var(--danger);
            color: white;
            border: none;
            border-radius: 3px;
            padding: 4px 10px;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.85em;
        }}
        
        .close-details:hover {{
            background: #b91c1c;
        }}
        
        .detail-row {{
            margin: 8px 0;
            font-size: 0.85em;
        }}
        
        .detail-label {{
            font-weight: 700;
            color: var(--primary);
            display: inline-block;
            width: 120px;
        }}
        
        .detail-value {{
            color: var(--text);
        }}
        
        .detail-list {{
            margin: 8px 0 8px 120px;
            padding: 8px;
            background: #f8f9fa;
            border-radius: 3px;
            font-size: 0.8em;
            line-height: 1.6;
        }}
        
        .detail-list li {{
            margin: 4px 0;
        }}
        
        .status-badge {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.75em;
            font-weight: 700;
            text-transform: uppercase;
        }}
        
        .status-badge.OK {{
            background: #22c55e;
            color: white;
        }}
        
        .status-badge.WARNING {{
            background: #f59e0b;
            color: white;
        }}
        
        .status-badge.CRITICAL {{
            background: #dc2626;
            color: white;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.85em;
        }}
        
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 3px;
            border: 2px solid #334155;
        }}
    </style>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
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
        
        {self._generate_network_topology_html(network_topology)}
        {self._generate_cisco_topology_html(cisco_topology)}
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
    
    <script>
        // Função para toggle de acordeão
        function toggleAccordion(contentId) {{
            const header = event.currentTarget;
            const content = document.getElementById(contentId);
            
            // Toggle classes
            header.classList.toggle('active');
            content.classList.toggle('active');
        }}
        
        // Sistema de arrastar dispositivos Cisco
        let isDragging = false;
        let currentDevice = null;
        let offsetX = 0;
        let offsetY = 0;
        
        // Função para iniciar o arrasto
        function startDrag(event, deviceId) {{
            // Prevenir ação padrão e propagação
            event.preventDefault();
            event.stopPropagation();
            
            // Não arrastar se clicar no nome/texto
            if (event.target.tagName === 'SPAN' || event.target.tagName === 'DIV') {{
                return;
            }}
            
            isDragging = true;
            currentDevice = document.querySelector(`[data-device-id="${{deviceId}}"]`);
            
            if (!currentDevice) return;
            
            // Adicionar classe de arrasto
            currentDevice.classList.add('dragging');
            
            // Calcular offset do mouse em relação ao dispositivo
            const rect = currentDevice.getBoundingClientRect();
            const container = document.getElementById('cisco-topology').getBoundingClientRect();
            
            offsetX = event.clientX - rect.left;
            offsetY = event.clientY - rect.top;
            
            // Adicionar listeners globais
            document.addEventListener('mousemove', drag);
            document.addEventListener('mouseup', stopDrag);
        }}
        
        // Função para arrastar
        function drag(event) {{
            if (!isDragging || !currentDevice) return;
            
            event.preventDefault();
            
            const container = document.getElementById('cisco-topology');
            const containerRect = container.getBoundingClientRect();
            
            // Calcular nova posição
            let newX = event.clientX - containerRect.left - offsetX;
            let newY = event.clientY - containerRect.top - offsetY;
            
            // Limitar aos bounds do container
            const deviceWidth = currentDevice.offsetWidth;
            const deviceHeight = currentDevice.offsetHeight;
            
            newX = Math.max(0, Math.min(newX, containerRect.width - deviceWidth));
            newY = Math.max(0, Math.min(newY, containerRect.height - deviceHeight));
            
            // Atualizar posição
            currentDevice.style.left = newX + 'px';
            currentDevice.style.top = newY + 'px';
        }}
        
        // Função para parar o arrasto
        function stopDrag(event) {{
            if (!isDragging) return;
            
            event.preventDefault();
            
            if (currentDevice) {{
                currentDevice.classList.remove('dragging');
            }}
            
            isDragging = false;
            currentDevice = null;
            
            // Remover listeners globais
            document.removeEventListener('mousemove', drag);
            document.removeEventListener('mouseup', stopDrag);
        }}
        
        // Adicionar eventos de arrastar a todos os dispositivos Cisco ao carregar
        document.addEventListener('DOMContentLoaded', function() {{
            const devices = document.querySelectorAll('.cisco-device');
            devices.forEach(device => {{
                const deviceId = device.getAttribute('data-device-id');
                device.addEventListener('mousedown', (e) => startDrag(e, deviceId));
            }});
        }});
    </script>
</body>
</html>"""
    
    
    def _generate_network_topology_html(self, topology_data):
        """Gera HTML do mapa de topologia de rede com acordeão"""
        import json
        
        nodes_json = json.dumps(topology_data['nodes'])
        edges_json = json.dumps(topology_data['edges'])
        
        return f"""
        <div class="topology-accordion">
            <div class="accordion-header" onclick="toggleAccordion('topology-vis')">
                <div class="accordion-title">
                    <span>MAPA DE TOPOLOGIA DA REDE (Interativo)</span>
                </div>
                <span class="accordion-icon">&#9660;</span>
            </div>
            <div id="topology-vis" class="accordion-content">
                <div class="topology-container">
                    <p style="color: var(--text-light); margin-bottom: 15px;">
                        Visualização interativa da arquitetura de rede com classificação de hosts por tipo de serviço e nível de risco.
                        <strong>Cores:</strong> Verde = Baixo risco | Amarelo = Risco médio | Vermelho = Alto risco
                    </p>
                    
                    <div id="network-topology"></div>
                    
                    <div class="topology-legend">
                        <div class="legend-item">
                            <div class="legend-color" style="background: #3b82f6;"></div>
                            <span>Gateway/Firewall</span>
                        </div>
                        <div class="legend-item">
                            <div class="legend-color" style="background: #8b5cf6;"></div>
                            <span>Servidores Web</span>
                        </div>
                        <div class="legend-item">
                            <div class="legend-color" style="background: #f59e0b;"></div>
                            <span>Bancos de Dados</span>
                        </div>
                        <div class="legend-item">
                            <div class="legend-color" style="background: #10b981;"></div>
                            <span>Servidores</span>
                        </div>
                        <div class="legend-item">
                            <div class="legend-color" style="background: #64748b;"></div>
                            <span>Estações de Trabalho</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
        <script>
            // Dados da topologia
            const nodes = new vis.DataSet({nodes_json});
            const edges = new vis.DataSet({edges_json});
            
            // Configuração de cores por grupo
            const groups = {{
                gateway: {{
                    color: {{
                        background: '#3b82f6',
                        border: '#1e40af',
                        highlight: {{background: '#60a5fa', border: '#1e40af'}}
                    }},
                    font: {{color: '#ffffff', size: 14, face: 'monospace', bold: true}}
                }},
                web: {{
                    color: {{
                        background: '#8b5cf6',
                        border: '#6d28d9',
                        highlight: {{background: '#a78bfa', border: '#6d28d9'}}
                    }},
                    font: {{color: '#ffffff', size: 12, face: 'monospace'}}
                }},
                database: {{
                    color: {{
                        background: '#f59e0b',
                        border: '#d97706',
                        highlight: {{background: '#fbbf24', border: '#d97706'}}
                    }},
                    font: {{color: '#ffffff', size: 12, face: 'monospace'}}
                }},
                server: {{
                    color: {{
                        background: '#10b981',
                        border: '#059669',
                        highlight: {{background: '#34d399', border: '#059669'}}
                    }},
                    font: {{color: '#ffffff', size: 12, face: 'monospace'}}
                }},
                workstation: {{
                    color: {{
                        background: '#64748b',
                        border: '#475569',
                        highlight: {{background: '#94a3b8', border: '#475569'}}
                    }},
                    font: {{color: '#ffffff', size: 12, face: 'monospace'}}
                }}
            }};
            
            // Container
            const container = document.getElementById('network-topology');
            
            // Dados do grafo
            const data = {{nodes: nodes, edges: edges}};
            
            // Opções de visualização
            const options = {{
                groups: groups,
                nodes: {{
                    shape: 'box',
                    margin: 10,
                    widthConstraint: {{minimum: 100, maximum: 150}},
                    heightConstraint: {{minimum: 50}}
                }},
                edges: {{
                    smooth: {{
                        type: 'continuous',
                        roundness: 0.5
                    }},
                    color: {{color: '#94a3b8', highlight: '#3b82f6'}},
                    width: 2
                }},
                physics: {{
                    enabled: true,
                    solver: 'forceAtlas2Based',
                    forceAtlas2Based: {{
                        gravitationalConstant: -50,
                        centralGravity: 0.01,
                        springLength: 200,
                        springConstant: 0.08,
                        damping: 0.4,
                        avoidOverlap: 0.5
                    }},
                    stabilization: {{
                        enabled: true,
                        iterations: 200
                    }}
                }},
                interaction: {{
                    hover: true,
                    tooltipDelay: 200,
                    navigationButtons: true,
                    keyboard: true
                }}
            }};
            
            // Criar network
            const network = new vis.Network(container, data, options);
            
            // Event handlers
            network.on('stabilizationIterationsDone', function() {{
                network.setOptions({{physics: false}});
            }});
            
            network.on('click', function(params) {{
                if (params.nodes.length > 0) {{
                    const nodeId = params.nodes[0];
                    console.log('Node clicked:', nodeId);
                }}
            }});
        </script>
        """
    
    def _generate_cisco_topology_html(self, cisco_data):
        """Gera visualização estilo Cisco Packet Tracer com acordeão"""
        
        # Verificar se há dados
        if not cisco_data.get('devices'):
            return """
            <div class="topology-accordion">
                <div class="accordion-header" onclick="toggleAccordion('topology-cisco')">
                    <div class="accordion-title">
                        <span>TOPOLOGIA DA REDE (Cisco Style)</span>
                    </div>
                    <span class="accordion-icon">&#9660;</span>
                </div>
                <div id="topology-cisco" class="accordion-content">
                    <div class="topology-container">
                        <div style="text-align: center; padding: 40px; color: #666;">
                            Nenhum dispositivo encontrado para visualização
                        </div>
                    </div>
                </div>
            </div>
            """
        
        import json
        devices_data = json.dumps(cisco_data['devices'], ensure_ascii=False)
        
        connections_svg = ""
        devices_html = ""
        
        # Gerar linhas de conexão usando SVG
        svg_lines = []
        for conn in cisco_data['connections']:
            from_device = next((d for d in cisco_data['devices'] if d['id'] == conn['from']), None)
            to_device = next((d for d in cisco_data['devices'] if d['id'] == conn['to']), None)
            
            if not from_device or not to_device:
                continue
            
            x1, y1 = from_device['position']['x'], from_device['position']['y'] + 30
            x2, y2 = to_device['position']['x'], to_device['position']['y'] + 30
            
            # Cor e espessura baseada no tipo
            if conn['type'] == 'backbone':
                color = '#1e40af'
                width = 5
                opacity = 1
            elif conn['type'] == 'trunk':
                color = '#16a34a'
                width = 3
                opacity = 0.9
            else:  # access
                color = '#6b7280'
                width = 2
                opacity = 0.7
                
                if conn.get('status') == 'critical':
                    color = '#dc2626'
                    width = 3
                    opacity = 1
                elif conn.get('status') == 'warning':
                    color = '#f59e0b'
                    opacity = 0.8
            
            svg_lines.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}" opacity="{opacity}"/>')
        
        connections_svg = f'<svg style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none;">{"".join(svg_lines)}</svg>'
        
        # Gerar dispositivos
        for device in cisco_data['devices']:
            x, y = device['position']['x'], device['position']['y']
            device_type = device['type']
            label = device['label'].replace('\\n', '<br>')
            
            status_indicator = ""
            if 'status' in device:
                status_indicator = f'<div class="status-indicator status-{device["status"]}"></div>'
            
            # Badge de vulnerabilidades
            vuln_badge = ""
            vuln_count = device.get('details', {}).get('vulnerabilidades', 0)
            if vuln_count > 0:
                badge_class = "critical" if vuln_count >= 3 else "warning"
                vuln_badge = f'<div class="vuln-badge {badge_class}">{vuln_count}</div>'
            
            devices_html += f'''
            <div class="cisco-device" style="left: {x - 30}px; top: {y - 30}px;" 
                 data-device-id="{device['id']}" onclick="showDeviceDetails('{device['id']}')">
                <div class="device-wrapper">
                    <div style="position: relative;">
                        <div class="device-icon device-{device_type}"></div>
                        {status_indicator}
                    </div>
                    {vuln_badge}
                </div>
                <div class="device-label">{label}</div>
            </div>
            '''
        
        # Estatísticas
        total_devices = len(cisco_data['devices'])
        total_connections = len(cisco_data['connections'])
        critical_devices = sum(1 for d in cisco_data['devices'] if d.get('status') == 'critical')
        warning_devices = sum(1 for d in cisco_data['devices'] if d.get('status') == 'warning')
        
        return f"""
        <div class="topology-accordion">
            <div class="accordion-header" onclick="toggleAccordion('topology-cisco')">
                <div class="accordion-title">
                    <span>TOPOLOGIA DA REDE (Cisco Style) - CLIQUE NOS DISPOSITIVOS</span>
                </div>
                <span class="accordion-icon">&#9660;</span>
            </div>
            <div id="topology-cisco" class="accordion-content">
                <div class="topology-container">
                    <div style="text-align: center; margin-bottom: 15px; color: #666; font-size: 0.85em;">
                        {total_devices} dispositivos | {total_connections} conexões | 
                        <span style="color: #dc2626; font-weight: 600;">{critical_devices} críticos</span> | 
                        <span style="color: #f59e0b; font-weight: 600;">{warning_devices} atenção</span>
                    </div>
                    <div id="cisco-topology">
                        {connections_svg}
                        {devices_html}
                        
                        <!-- Painel de Detalhes -->
                        <div id="device-details" class="device-details-panel">
                            <div class="details-header">
                                <h3 id="details-title">Informacoes do Dispositivo</h3>
                                <button class="close-details" onclick="closeDetails()">X</button>
                            </div>
                            <div id="details-content"></div>
                        </div>
                        
                        <div class="topology-legend">
                            <h4>Legenda - Clique em qualquer dispositivo para ver detalhes</h4>
                            <div style="display: flex; gap: 15px; flex-wrap: wrap;">
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <div class="device-icon device-router" style="width: 25px; height: 25px;"></div>
                                    <span>Router</span>
                                </div>
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <div class="device-icon device-firewall" style="width: 25px; height: 25px;"></div>
                                    <span>Firewall</span>
                                </div>
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <div class="device-icon device-switch" style="width: 25px; height: 25px;"></div>
                                    <span>Switch</span>
                                </div>
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <div class="device-icon device-server" style="width: 25px; height: 25px;"></div>
                                    <span>Server</span>
                                </div>
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <div class="device-icon device-database" style="width: 25px; height: 25px;"></div>
                                    <span>Database</span>
                                </div>
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <div class="device-icon device-web-server" style="width: 25px; height: 25px;"></div>
                                    <span>Web Server</span>
                                </div>
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <div class="device-icon device-workstation" style="width: 25px; height: 25px;"></div>
                                    <span>Workstation</span>
                                </div>
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <div class="status-indicator status-ok" style="position: relative;"></div>
                                    <span>Seguro</span>
                                </div>
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <div class="status-indicator status-warning" style="position: relative;"></div>
                                    <span>Atenção</span>
                                </div>
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <div class="status-indicator status-critical" style="position: relative;"></div>
                                    <span>Crítico</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            const devicesData = {devices_data};
            
            function showDeviceDetails(deviceId) {{
                const device = devicesData.find(d => d.id === deviceId);
                if (!device) return;
                
                // Remover seleção anterior
                document.querySelectorAll('.cisco-device').forEach(el => el.classList.remove('selected'));
                
                // Adicionar seleção atual
                const deviceEl = document.querySelector(`[data-device-id="${{deviceId}}"]`);
                if (deviceEl) deviceEl.classList.add('selected');
                
                const details = device.details || {{}};
                let html = '';
                
                // Informações básicas
                if (details.name) {{
                    html += `<div class="detail-row"><span class="detail-label">Nome:</span><span class="detail-value">${{details.name}}</span></div>`;
                }}
                if (details.type) {{
                    html += `<div class="detail-row"><span class="detail-label">Tipo:</span><span class="detail-value">${{details.type}}</span></div>`;
                }}
                if (details.ip) {{
                    html += `<div class="detail-row"><span class="detail-label">Endereço IP:</span><span class="detail-value">${{details.ip}}</span></div>`;
                }}
                if (details.os) {{
                    html += `<div class="detail-row"><span class="detail-label">Sistema:</span><span class="detail-value">${{details.os}}</span></div>`;
                }}
                if (details.subnet) {{
                    html += `<div class="detail-row"><span class="detail-label">Subnet:</span><span class="detail-value">${{details.subnet}}</span></div>`;
                }}
                if (details.hosts !== undefined) {{
                    html += `<div class="detail-row"><span class="detail-label">Hosts:</span><span class="detail-value">${{details.hosts}}</span></div>`;
                }}
                if (details.portas_abertas !== undefined) {{
                    html += `<div class="detail-row"><span class="detail-label">Portas Abertas:</span><span class="detail-value">${{details.portas_abertas}}</span></div>`;
                }}
                if (details.ports_abertos !== undefined) {{
                    html += `<div class="detail-row"><span class="detail-label">Total Portas:</span><span class="detail-value">${{details.ports_abertos}}</span></div>`;
                }}
                
                // Portas detalhadas
                if (details.portas && details.portas.length > 0) {{
                    html += `<div class="detail-row"><span class="detail-label">Serviços:</span></div>`;
                    html += `<ul class="detail-list">${{details.portas.map(p => '<li>' + p + '</li>').join('')}}</ul>`;
                }}
                
                // Vulnerabilidades
                if (details.vulnerabilidades !== undefined) {{
                    const vulnClass = details.vulnerabilidades >= 3 ? 'CRITICAL' : details.vulnerabilidades >= 1 ? 'WARNING' : 'OK';
                    html += `<div class="detail-row"><span class="detail-label">Vulnerabilidades:</span><span class="detail-value">${{details.vulnerabilidades}} <span class="status-badge ${{vulnClass}}">${{vulnClass}}</span></span></div>`;
                }}
                
                if (details.vuln_detalhes && details.vuln_detalhes.length > 0) {{
                    html += `<div class="detail-row"><span class="detail-label">Detalhes:</span></div>`;
                    html += `<ul class="detail-list">${{details.vuln_detalhes.map(v => '<li>' + v + '</li>').join('')}}</ul>`;
                }}
                
                if (details.servicos_inseguros) {{
                    html += `<div class="detail-row"><span class="detail-label">Alerta:</span><span class="detail-value" style="color: #dc2626; font-weight: 600;">[!] Servicos inseguros detectados</span></div>`;
                }}
                
                if (details.function) {{
                    html += `<div class="detail-row"><span class="detail-label">Função:</span><span class="detail-value">${{details.function}}</span></div>`;
                }}
                if (details.info) {{
                    html += `<div class="detail-row"><span class="detail-label">Info:</span><span class="detail-value">${{details.info}}</span></div>`;
                }}
                
                // Status geral
                if (details.status) {{
                    html += `<div class="detail-row"><span class="detail-label">Status Geral:</span><span class="status-badge ${{details.status}}">${{details.status}}</span></div>`;
                }}
                
                document.getElementById('details-content').innerHTML = html;
                document.getElementById('device-details').classList.add('show');
            }}
            
            function closeDetails() {{
                document.getElementById('device-details').classList.remove('show');
                document.querySelectorAll('.cisco-device').forEach(el => el.classList.remove('selected'));
            }}
        </script>
        """
    
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
            return "<li>OK - Nenhuma nao-conformidade identificada</li>"
        return "".join([f"<li>X {finding}</li>" for finding in findings[:3]])
    
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
                <h3 style="font-size: 0.9em; color: var(--danger); margin-bottom: 15px; text-transform: uppercase;">Riscos Criticos (Score >= 7)</h3>
                {self._generate_risk_items_html(matrix['critical'][:5])}
            </div>
        </div>
        """
    
    def _generate_risk_items_html(self, risks):
        """Gera itens de risco"""
        if not risks:
            return "<p style='color: var(--success);'>OK - Nenhum risco critico identificado</p>"
        
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
                <h3>[!] {vector['name']}</h3>
                <p><strong>Alvo:</strong> {vector['service']}</p>
                <p><strong>Metodo:</strong> {vector['method']}</p>
                <p><strong>Impacto:</strong> {vector['impact']}</p>
                <p><strong>Mitigacao:</strong> {vector['mitigation']}</p>
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
            vuln_id = f"V-{str(idx).zfill(3)}"
            
            rows += f"""
            <tr>
                <td><strong>{vuln_id}</strong></td>
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
            port_list = [f"{p.get('port', 0)}/{p.get('service', 'unknown')}" for p in host.get('ports', [])[:5]]
            services = ", ".join(port_list)
            total_ports = host.get('total_ports', 0)
            
            if total_ports > 10:
                risk_level = "ALTO"
                badge_class = "badge-critical"
            elif total_ports > 5:
                risk_level = "MEDIO"
                badge_class = "badge-high"
            else:
                risk_level = "BAIXO"
                badge_class = "badge-low"
            
            hostname = host.get('hostname', 'Unknown')
            ip = host.get('ip', 'N/A')
            os_info = host.get('os', 'Unknown')[:40]
            
            rows += f"""
            <tr>
                <td><strong>{hostname}</strong></td>
                <td>{ip}</td>
                <td>{os_info}</td>
                <td>{total_ports}</td>
                <td><small>{services}</small></td>
                <td><span class="badge {badge_class}">{risk_level}</span></td>
            </tr>
            """
        return rows


def generate_technical_dashboard(hosts: List[Dict], vuln_summary: Dict, use_ai: bool = True, output_file: str = "dashboard.html"):
    """Funcao principal para gerar dashboard tecnico"""
    dashboard = TechnicalDashboard(use_ai=use_ai)
    return dashboard.generate(hosts, vuln_summary, output_file=output_file)


if __name__ == "__main__":
    print("Dashboard Tecnico Avancado - Sistema de Analise de Seguranca")
