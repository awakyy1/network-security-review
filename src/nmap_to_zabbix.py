"""
Sistema de Análise de Segurança de Redes
Processa logs do Nmap, cria topologia no Zabbix e gera relatório de vulnerabilidades
Autor: TCC - Segurança de Redes
"""

import xml.etree.ElementTree as ET
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional
import os


class ZabbixAPI:
    """Classe para interação com a API do Zabbix"""
    
    def __init__(self, url: str, user: str, password: str):
        self.url = url
        self.user = user
        self.password = password
        self.auth_token = None
        self.request_id = 1
        
    def _make_request(self, method: str, params: dict) -> dict:
        """Faz requisição à API do Zabbix"""
        headers = {'Content-Type': 'application/json'}
        
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": self.request_id,
        }
        
        if self.auth_token:
            payload["auth"] = self.auth_token
            
        self.request_id += 1
        
        try:
            response = requests.post(self.url, json=payload, headers=headers, verify=False)
            response.raise_for_status()
            result = response.json()
            
            if 'error' in result:
                raise Exception(f"Erro Zabbix API: {result['error']}")
                
            return result.get('result')
        except Exception as e:
            print(f"Erro na requisição: {e}")
            return None
    
    def login(self) -> bool:
        """Autentica no Zabbix"""
        result = self._make_request("user.login", {
            "user": self.user,
            "password": self.password
        })
        
        if result:
            self.auth_token = result
            print("[OK] Autenticado no Zabbix com sucesso")
            return True
        return False
    
    def create_host(self, hostname: str, ip: str, group_id: str = "2") -> Optional[str]:
        """Cria um host no Zabbix"""
        params = {
            "host": hostname,
            "interfaces": [{
                "type": 1,  # Agent
                "main": 1,
                "useip": 1,
                "ip": ip,
                "dns": "",
                "port": "10050"
            }],
            "groups": [{"groupid": group_id}]
        }
        
        result = self._make_request("host.create", params)
        if result and 'hostids' in result:
            return result['hostids'][0]
        return None
    
    def create_map(self, name: str, hosts: List[Dict]) -> Optional[str]:
        """Cria um mapa de rede no Zabbix"""
        # Preparar elementos do mapa
        selements = []
        links = []
        
        # Adicionar hosts ao mapa
        for idx, host in enumerate(hosts):
            selements.append({
                "selementid": str(idx + 1),
                "elementtype": 0,  # Host
                "elements": [{"hostid": host.get('hostid', '0')}],
                "x": (idx % 5) * 150 + 100,
                "y": (idx // 5) * 150 + 100,
                "iconid_off": "1"
            })
        
        params = {
            "name": name,
            "width": 800,
            "height": 600,
            "selements": selements,
            "links": links
        }
        
        result = self._make_request("map.create", params)
        if result and 'sysmapids' in result:
            return result['sysmapids'][0]
        return None


class NmapParser:
    """Classe para análise de logs do Nmap"""
    
    def __init__(self, nmap_file: str):
        self.nmap_file = nmap_file
        self.hosts = []
        self.vulnerabilities = []
        
    def parse_xml(self) -> bool:
        """Processa arquivo XML do Nmap"""
        try:
            tree = ET.parse(self.nmap_file)
            root = tree.getroot()
            
            for host in root.findall('.//host'):
                host_data = self._parse_host(host)
                if host_data:
                    self.hosts.append(host_data)
            
            print(f"[OK] Processados {len(self.hosts)} hosts do scan Nmap")
            return True
        except Exception as e:
            print(f"[ERRO] Erro ao processar XML: {e}")
            return False
    
    def _parse_host(self, host_elem) -> Optional[Dict]:
        """Extrai informações de um host"""
        # Obter IP
        address = host_elem.find('address')
        if address is None:
            return None
            
        ip = address.get('addr')
        
        # Obter hostname
        hostnames = host_elem.find('hostnames')
        hostname = ip
        if hostnames is not None:
            hostname_elem = hostnames.find('hostname')
            if hostname_elem is not None:
                hostname = hostname_elem.get('name', ip)
        
        # Obter status
        status = host_elem.find('status')
        if status is None or status.get('state') != 'up':
            return None
        
        # Obter portas e serviços
        ports = []
        ports_elem = host_elem.find('ports')
        if ports_elem is not None:
            for port in ports_elem.findall('port'):
                port_data = self._parse_port(port, ip)
                if port_data:
                    ports.append(port_data)
        
        # Obter sistema operacional
        os_info = "Desconhecido"
        os_elem = host_elem.find('os')
        if os_elem is not None:
            osmatch = os_elem.find('osmatch')
            if osmatch is not None:
                os_info = osmatch.get('name', 'Desconhecido')
        
        # Vincular vulnerabilidades deste host específico
        host_vulnerabilities = [v for v in self.vulnerabilities if v['ip'] == ip]
        
        return {
            'ip': ip,
            'hostname': hostname,
            'os': os_info,
            'ports': ports,
            'total_ports': len(ports),
            'vulnerabilities': host_vulnerabilities
        }
    
    def _parse_port(self, port_elem, host_ip: str) -> Optional[Dict]:
        """Extrai informações de uma porta"""
        port_id = port_elem.get('portid')
        protocol = port_elem.get('protocol')
        
        state = port_elem.find('state')
        if state is None or state.get('state') != 'open':
            return None
        
        service = port_elem.find('service')
        service_name = "unknown"
        service_product = ""
        service_version = ""
        
        if service is not None:
            service_name = service.get('name', 'unknown')
            service_product = service.get('product', '')
            service_version = service.get('version', '')
        
        # Análise de vulnerabilidades
        self._check_vulnerabilities(host_ip, port_id, service_name, service_product, service_version)
        
        return {
            'port': port_id,
            'protocol': protocol,
            'service': service_name,
            'product': service_product,
            'version': service_version
        }
    
    def _check_vulnerabilities(self, ip: str, port: str, service: str, product: str, version: str):
        """Identifica possíveis vulnerabilidades"""
        vuln_db = {
            'ftp': {'ports': ['21'], 'severity': 'MÉDIA', 'description': 'Serviço FTP detectado - transmissão não criptografada'},
            'telnet': {'ports': ['23'], 'severity': 'ALTA', 'description': 'Telnet detectado - protocolo inseguro sem criptografia'},
            'smtp': {'ports': ['25'], 'severity': 'BAIXA', 'description': 'SMTP aberto - possível relay não autorizado'},
            'http': {'ports': ['80'], 'severity': 'MÉDIA', 'description': 'HTTP sem criptografia detectado'},
            'netbios-ssn': {'ports': ['139', '445'], 'severity': 'ALTA', 'description': 'SMB/NetBIOS exposto - vulnerável a ataques'},
            'mysql': {'ports': ['3306'], 'severity': 'ALTA', 'description': 'MySQL exposto publicamente'},
            'postgresql': {'ports': ['5432'], 'severity': 'ALTA', 'description': 'PostgreSQL exposto publicamente'},
            'rdp': {'ports': ['3389'], 'severity': 'ALTA', 'description': 'RDP exposto - alvo comum de ataques'},
            'vnc': {'ports': ['5900'], 'severity': 'ALTA', 'description': 'VNC exposto - acesso remoto sem autenticação forte'},
            'ssh': {'ports': ['22'], 'severity': 'BAIXA', 'description': 'SSH exposto - verificar configuração de autenticação'},
        }
        
        for service_key, vuln_info in vuln_db.items():
            if service == service_key or port in vuln_info['ports']:
                self.vulnerabilities.append({
                    'ip': ip,
                    'port': port,
                    'service': service,
                    'product': product,
                    'version': version,
                    'severity': vuln_info['severity'],
                    'description': vuln_info['description'],
                    'recommendation': self._get_recommendation(service)
                })
    
    def _get_recommendation(self, service: str) -> str:
        """Retorna recomendações de segurança"""
        recommendations = {
            'ftp': 'Migrar para SFTP ou FTPS',
            'telnet': 'Substituir por SSH',
            'smtp': 'Configurar autenticação e usar TLS',
            'http': 'Implementar HTTPS com certificado SSL/TLS',
            'netbios-ssn': 'Restringir acesso via firewall',
            'mysql': 'Restringir acesso apenas a IPs confiáveis',
            'postgresql': 'Restringir acesso apenas a IPs confiáveis',
            'rdp': 'Usar VPN e implementar MFA',
            'vnc': 'Usar túnel SSH ou VPN',
            'ssh': 'Desabilitar autenticação por senha, usar apenas chaves'
        }
        return recommendations.get(service, 'Revisar configurações de segurança')
    
    def get_vulnerability_summary(self) -> Dict:
        """Gera resumo de vulnerabilidades"""
        summary = {
            'total': len(self.vulnerabilities),
            'alta': len([v for v in self.vulnerabilities if v['severity'] == 'ALTA']),
            'media': len([v for v in self.vulnerabilities if v['severity'] == 'MÉDIA']),
            'baixa': len([v for v in self.vulnerabilities if v['severity'] == 'BAIXA']),
            'vulnerabilities': self.vulnerabilities
        }
        return summary


class ReportGenerator:
    """Classe para geração de relatórios"""
    
    @staticmethod
    def generate_markdown_report(hosts: List[Dict], vuln_summary: Dict, output_file: str):
        """Gera relatório em Markdown"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Relatório de Análise de Segurança de Rede\n\n")
            f.write(f"**Data da Análise:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
            
            # Resumo Executivo
            f.write("## RESUMO EXECUTIVO\n\n")
            f.write(f"- **Total de Hosts Descobertos:** {len(hosts)}\n")
            f.write(f"- **Total de Vulnerabilidades:** {vuln_summary['total']}\n")
            f.write(f"  - **Alta (Crítica):** {vuln_summary['alta']}\n")
            f.write(f"  - **Média:** {vuln_summary['media']}\n")
            f.write(f"  - **Baixa:** {vuln_summary['baixa']}\n\n")
            
            # Hosts Descobertos
            f.write("## HOSTS DESCOBERTOS\n\n")
            for idx, host in enumerate(hosts, 1):
                f.write(f"### {idx}. {host['hostname']}\n\n")
                f.write(f"- **IP:** {host['ip']}\n")
                f.write(f"- **Sistema Operacional:** {host['os']}\n")
                f.write(f"- **Portas Abertas:** {host['total_ports']}\n\n")
                
                if host['ports']:
                    f.write("**Serviços Detectados:**\n\n")
                    f.write("| Porta | Protocolo | Serviço | Produto | Versão |\n")
                    f.write("|-------|-----------|---------|---------|--------|\n")
                    for port in host['ports']:
                        f.write(f"| {port['port']} | {port['protocol']} | {port['service']} | "
                               f"{port['product']} | {port['version']} |\n")
                    f.write("\n")
            
            # Vulnerabilidades Detalhadas
            f.write("## 🔒 Vulnerabilidades Identificadas\n\n")
            
            if vuln_summary['vulnerabilities']:
                # Agrupar por severidade
                for severity in ['ALTA', 'MÉDIA', 'BAIXA']:
                    vulns = [v for v in vuln_summary['vulnerabilities'] if v['severity'] == severity]
                    if vulns:
                        icon = '🔴' if severity == 'ALTA' else '🟡' if severity == 'MÉDIA' else '🟢'
                        f.write(f"### {icon} Severidade {severity}\n\n")
                        
                        for vuln in vulns:
                            f.write(f"#### {vuln['ip']}:{vuln['port']} - {vuln['service']}\n\n")
                            f.write(f"- **Descrição:** {vuln['description']}\n")
                            if vuln['product']:
                                f.write(f"- **Produto:** {vuln['product']} {vuln['version']}\n")
                            f.write(f"- **Recomendação:** {vuln['recommendation']}\n\n")
            else:
                f.write("Nenhuma vulnerabilidade crítica identificada.\n\n")
            
            # Recomendações Gerais
            f.write("## 💡 Recomendações Gerais de Segurança\n\n")
            f.write("1. **Minimizar Superfície de Ataque:** Fechar portas desnecessárias\n")
            f.write("2. **Implementar Criptografia:** Usar protocolos seguros (HTTPS, SSH, SFTP)\n")
            f.write("3. **Autenticação Forte:** Implementar MFA onde possível\n")
            f.write("4. **Segmentação de Rede:** Isolar serviços críticos\n")
            f.write("5. **Monitoramento Contínuo:** Implementar IDS/IPS\n")
            f.write("6. **Atualizações Regulares:** Manter sistemas e serviços atualizados\n")
            f.write("7. **Firewall:** Configurar regras restritivas\n")
            f.write("8. **Backup:** Implementar política de backup regular\n\n")
            
            f.write("---\n")
            f.write("*Relatório gerado automaticamente pelo Sistema de Análise de Segurança de Redes*\n")
        
        print(f"[OK] Relatório gerado: {output_file}")
    
    @staticmethod
    def generate_json_report(hosts: List[Dict], vuln_summary: Dict, output_file: str):
        """Gera relatório em JSON"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_hosts': len(hosts),
                'total_vulnerabilities': vuln_summary['total'],
                'high_severity': vuln_summary['alta'],
                'medium_severity': vuln_summary['media'],
                'low_severity': vuln_summary['baixa']
            },
            'hosts': hosts,
            'vulnerabilities': vuln_summary['vulnerabilities']
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=4, ensure_ascii=False)
        
        print(f"[OK] Relatório JSON gerado: {output_file}")


def main():
    """Função principal"""
    print("=" * 60)
    print("Sistema de Análise de Segurança de Redes")
    print("TCC - Segurança de Redes")
    print("=" * 60)
    print()
    
    # Obter diretório do script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    
    # Carregar configurações do arquivo config.json
    config_file = os.path.join(script_dir, "config.json")
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Configurações de caminhos (relativos ao base_dir)
    NMAP_FILE = os.path.join(base_dir, config['nmap']['input_file'].lstrip('../'))
    OUTPUT_DIR = os.path.join(base_dir, "output")
    MD_REPORT = os.path.join(OUTPUT_DIR, "relatorio_seguranca.md")
    JSON_REPORT = os.path.join(OUTPUT_DIR, "relatorio_seguranca.json")
    DASHBOARD = os.path.join(OUTPUT_DIR, "dashboard.html")
    
    # Configurações do Zabbix
    ZABBIX_URL = config['zabbix']['url']
    ZABBIX_USER = config['zabbix']['user']
    ZABBIX_PASSWORD = config['zabbix']['password']
    
    # Garantir que a pasta output existe
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Verificar se arquivo Nmap existe
    if not os.path.exists(NMAP_FILE):
        print(f"[AVISO] Arquivo {NMAP_FILE} não encontrado!")
        print(f"Execute o Nmap com: nmap -sV -O -oX {NMAP_FILE} <target>")
        print()
        print("Criando arquivo de exemplo para demonstração...")
        create_example_nmap_file(NMAP_FILE)
    
    # Parsear Nmap
    print("[INFO] Processando scan do Nmap...")
    parser = NmapParser(NMAP_FILE)
    
    if not parser.parse_xml():
        print("[ERRO] Falha ao processar arquivo Nmap")
        return
    
    # Obter resumo de vulnerabilidades
    vuln_summary = parser.get_vulnerability_summary()
    
    # Gerar relatórios
    print("\n[INFO] Gerando relatórios...")
    ReportGenerator.generate_markdown_report(
        parser.hosts, 
        vuln_summary, 
        MD_REPORT
    )
    ReportGenerator.generate_json_report(
        parser.hosts, 
        vuln_summary, 
        JSON_REPORT
    )
    
    # Integração com Zabbix (opcional)
    print("\n[INFO] Integrando com Zabbix...")
    try:
        zabbix = ZabbixAPI(ZABBIX_URL, ZABBIX_USER, ZABBIX_PASSWORD)
        
        if zabbix.login():
            hosts_created = []
            for host in parser.hosts:
                host_id = zabbix.create_host(host['hostname'], host['ip'])
                if host_id:
                    print(f"  [OK] Host criado: {host['hostname']} ({host['ip']})")
                    hosts_created.append({'hostid': host_id, 'name': host['hostname']})
            
            if hosts_created:
                map_name = f"Topologia_Rede_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                map_id = zabbix.create_map(map_name, hosts_created)
                if map_id:
                    print(f"  [OK] Mapa criado: {map_name}")
    except Exception as e:
        print(f"[AVISO] Erro ao conectar com Zabbix: {e}")
        print("  Continuando sem integração Zabbix...")
    
    print("\n" + "=" * 60)
    print("[SUCESSO] Análise concluída com sucesso!")
    print("=" * 60)
    print(f"\n[ESTATÍSTICAS]")
    print(f"   - Hosts analisados: {len(parser.hosts)}")
    print(f"   - Vulnerabilidades encontradas: {vuln_summary['total']}")
    print(f"     - Alta (Crítica): {vuln_summary['alta']}")
    print(f"     - Média: {vuln_summary['media']}")
    print(f"     - Baixa: {vuln_summary['baixa']}")
    print(f"\n[RELATÓRIOS GERADOS]")
    print(f"   - {os.path.basename(MD_REPORT)}")
    print(f"   - {os.path.basename(JSON_REPORT)}")
    
    # Gerar Dashboard Técnico Avançado com IA
    print("\n[INFO] Gerando Dashboard Técnico Avançado...")
    try:
        from dashboard_tecnico import generate_technical_dashboard
        dashboard_file = generate_technical_dashboard(
            parser.hosts, 
            vuln_summary,
            use_ai=True,  # Ativa IA se Ollama estiver disponível
            output_file=DASHBOARD
        )
        print(f"   [OK] {os.path.basename(dashboard_file)}")
    except Exception as e:
        print(f"   [ERRO] Erro ao gerar dashboard: {e}")
    
    print()


def create_example_nmap_file(filename: str):
    """Cria arquivo XML de exemplo do Nmap para demonstração"""
    example_xml = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE nmaprun>
<nmaprun scanner="nmap" args="nmap -sV -O target" start="1700000000" version="7.94">
<host starttime="1700000000" endtime="1700000100">
<status state="up" reason="echo-reply"/>
<address addr="192.168.1.100" addrtype="ipv4"/>
<hostnames>
<hostname name="server01.local" type="PTR"/>
</hostnames>
<ports>
<port protocol="tcp" portid="22">
<state state="open" reason="syn-ack"/>
<service name="ssh" product="OpenSSH" version="8.2p1" />
</port>
<port protocol="tcp" portid="80">
<state state="open" reason="syn-ack"/>
<service name="http" product="Apache" version="2.4.41" />
</port>
<port protocol="tcp" portid="3306">
<state state="open" reason="syn-ack"/>
<service name="mysql" product="MySQL" version="5.7.33" />
</port>
</ports>
<os>
<osmatch name="Linux 4.15 - 5.6" accuracy="95"/>
</os>
</host>
<host starttime="1700000100" endtime="1700000200">
<status state="up" reason="echo-reply"/>
<address addr="192.168.1.101" addrtype="ipv4"/>
<hostnames>
<hostname name="server02.local" type="PTR"/>
</hostnames>
<ports>
<port protocol="tcp" portid="21">
<state state="open" reason="syn-ack"/>
<service name="ftp" product="vsftpd" version="3.0.3" />
</port>
<port protocol="tcp" portid="23">
<state state="open" reason="syn-ack"/>
<service name="telnet" />
</port>
<port protocol="tcp" portid="445">
<state state="open" reason="syn-ack"/>
<service name="netbios-ssn" product="Samba" version="4.11.2" />
</port>
<port protocol="tcp" portid="3389">
<state state="open" reason="syn-ack"/>
<service name="rdp" product="Microsoft Terminal Services" />
</port>
</ports>
<os>
<osmatch name="Microsoft Windows Server 2016" accuracy="92"/>
</os>
</host>
</nmaprun>"""
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(example_xml)
    
    print(f"✓ Arquivo de exemplo criado: {filename}")


if __name__ == "__main__":
    main()
