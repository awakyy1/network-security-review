"""
Script de Teste - Sistema de Análise de Segurança
Cria cenários de teste realistas para demonstração
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
import os


def create_test_scenario(scenario_name: str, hosts_data: list, output_file: str):
    """Cria arquivo XML do Nmap para teste"""
    
    # Criar estrutura XML
    root = ET.Element('nmaprun')
    root.set('scanner', 'nmap')
    root.set('args', f'nmap -sV -O {scenario_name}')
    root.set('start', '1700000000')
    root.set('version', '7.94')
    
    for host_data in hosts_data:
        host = ET.SubElement(root, 'host')
        host.set('starttime', '1700000000')
        host.set('endtime', '1700000100')
        
        # Status
        status = ET.SubElement(host, 'status')
        status.set('state', 'up')
        status.set('reason', 'echo-reply')
        
        # Endereço IP
        address = ET.SubElement(host, 'address')
        address.set('addr', host_data['ip'])
        address.set('addrtype', 'ipv4')
        
        # Hostname
        hostnames = ET.SubElement(host, 'hostnames')
        hostname = ET.SubElement(hostnames, 'hostname')
        hostname.set('name', host_data['hostname'])
        hostname.set('type', 'PTR')
        
        # Portas
        ports = ET.SubElement(host, 'ports')
        for port_data in host_data['ports']:
            port = ET.SubElement(ports, 'port')
            port.set('protocol', 'tcp')
            port.set('portid', port_data['port'])
            
            state = ET.SubElement(port, 'state')
            state.set('state', 'open')
            state.set('reason', 'syn-ack')
            
            service = ET.SubElement(port, 'service')
            service.set('name', port_data['service'])
            if 'product' in port_data:
                service.set('product', port_data['product'])
            if 'version' in port_data:
                service.set('version', port_data['version'])
        
        # Sistema Operacional
        os_elem = ET.SubElement(host, 'os')
        osmatch = ET.SubElement(os_elem, 'osmatch')
        osmatch.set('name', host_data['os'])
        osmatch.set('accuracy', '95')
    
    # Formatar XML
    xml_str = ET.tostring(root, encoding='utf-8')
    dom = minidom.parseString(xml_str)
    pretty_xml = dom.toprettyxml(indent='  ')
    
    # Remover linha em branco extra
    pretty_xml = '\n'.join([line for line in pretty_xml.split('\n') if line.strip()])
    
    # Salvar arquivo
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)
    
    print(f"✓ Cenário '{scenario_name}' criado: {output_file}")


def test_scenario_1_empresa_insegura():
    """Cenário 1: Empresa com várias vulnerabilidades críticas"""
    
    print("\n" + "="*60)
    print("🔴 CENÁRIO 1: Empresa com Segurança CRÍTICA")
    print("="*60)
    print("Simulando uma rede corporativa mal configurada...")
    
    hosts = [
        {
            'ip': '10.0.1.10',
            'hostname': 'servidor-web.empresa.local',
            'os': 'Ubuntu Linux 20.04',
            'ports': [
                {'port': '21', 'service': 'ftp', 'product': 'vsftpd', 'version': '3.0.3'},
                {'port': '22', 'service': 'ssh', 'product': 'OpenSSH', 'version': '8.2p1'},
                {'port': '23', 'service': 'telnet'},
                {'port': '80', 'service': 'http', 'product': 'Apache', 'version': '2.4.41'},
                {'port': '3306', 'service': 'mysql', 'product': 'MySQL', 'version': '5.7.33'},
            ]
        },
        {
            'ip': '10.0.1.20',
            'hostname': 'servidor-arquivos.empresa.local',
            'os': 'Microsoft Windows Server 2012 R2',
            'ports': [
                {'port': '135', 'service': 'msrpc', 'product': 'Microsoft Windows RPC'},
                {'port': '139', 'service': 'netbios-ssn'},
                {'port': '445', 'service': 'netbios-ssn', 'product': 'Samba', 'version': '3.6.25'},
                {'port': '3389', 'service': 'rdp', 'product': 'Microsoft Terminal Services'},
            ]
        },
        {
            'ip': '10.0.1.30',
            'hostname': 'servidor-bd.empresa.local',
            'os': 'CentOS 7',
            'ports': [
                {'port': '22', 'service': 'ssh', 'product': 'OpenSSH', 'version': '7.4'},
                {'port': '3306', 'service': 'mysql', 'product': 'MySQL', 'version': '5.6.51'},
                {'port': '5432', 'service': 'postgresql', 'product': 'PostgreSQL', 'version': '9.6'},
            ]
        },
        {
            'ip': '10.0.1.40',
            'hostname': 'servidor-backup.empresa.local',
            'os': 'Debian 10',
            'ports': [
                {'port': '21', 'service': 'ftp', 'product': 'ProFTPD', 'version': '1.3.6'},
                {'port': '22', 'service': 'ssh', 'product': 'OpenSSH', 'version': '7.9'},
                {'port': '5900', 'service': 'vnc', 'product': 'VNC', 'version': '4.1.2'},
            ]
        }
    ]
    
    create_test_scenario('Empresa Insegura', hosts, 'test_cenario1.xml')
    print("\n📊 Expectativa: ~15-20 vulnerabilidades críticas")
    print("   - Telnet ativo")
    print("   - Múltiplos bancos de dados expostos")
    print("   - RDP sem proteção")
    print("   - VNC vulnerável")


def test_scenario_2_casa_comum():
    """Cenário 2: Rede doméstica típica"""
    
    print("\n" + "="*60)
    print("🟡 CENÁRIO 2: Rede Doméstica Típica")
    print("="*60)
    print("Simulando uma rede residencial...")
    
    hosts = [
        {
            'ip': '192.168.0.1',
            'hostname': 'router.home',
            'os': 'Linux 3.x',
            'ports': [
                {'port': '80', 'service': 'http', 'product': 'lighttpd', 'version': '1.4.35'},
                {'port': '443', 'service': 'https', 'product': 'lighttpd', 'version': '1.4.35'},
            ]
        },
        {
            'ip': '192.168.0.10',
            'hostname': 'desktop-home',
            'os': 'Microsoft Windows 10',
            'ports': [
                {'port': '135', 'service': 'msrpc', 'product': 'Microsoft Windows RPC'},
                {'port': '139', 'service': 'netbios-ssn'},
                {'port': '445', 'service': 'netbios-ssn'},
            ]
        },
        {
            'ip': '192.168.0.15',
            'hostname': 'nas.home',
            'os': 'Linux 4.x',
            'ports': [
                {'port': '22', 'service': 'ssh', 'product': 'OpenSSH', 'version': '8.4'},
                {'port': '80', 'service': 'http', 'product': 'nginx', 'version': '1.18.0'},
                {'port': '445', 'service': 'netbios-ssn', 'product': 'Samba', 'version': '4.13.3'},
            ]
        }
    ]
    
    create_test_scenario('Casa Comum', hosts, 'test_cenario2.xml')
    print("\n📊 Expectativa: ~5-7 vulnerabilidades médias/baixas")
    print("   - HTTP sem HTTPS em alguns dispositivos")
    print("   - SMB exposto na rede local")


def test_scenario_3_servidor_seguro():
    """Cenário 3: Servidor bem configurado"""
    
    print("\n" + "="*60)
    print("🟢 CENÁRIO 3: Servidor com Boa Segurança")
    print("="*60)
    print("Simulando um servidor bem configurado...")
    
    hosts = [
        {
            'ip': '203.0.113.50',
            'hostname': 'web-producao.empresa.com',
            'os': 'Ubuntu Linux 22.04 LTS',
            'ports': [
                {'port': '22', 'service': 'ssh', 'product': 'OpenSSH', 'version': '9.0'},
                {'port': '443', 'service': 'https', 'product': 'nginx', 'version': '1.22.0'},
            ]
        },
        {
            'ip': '203.0.113.51',
            'hostname': 'api-producao.empresa.com',
            'os': 'Ubuntu Linux 22.04 LTS',
            'ports': [
                {'port': '22', 'service': 'ssh', 'product': 'OpenSSH', 'version': '9.0'},
                {'port': '443', 'service': 'https', 'product': 'nginx', 'version': '1.22.0'},
            ]
        }
    ]
    
    create_test_scenario('Servidor Seguro', hosts, 'test_cenario3.xml')
    print("\n📊 Expectativa: ~2-3 vulnerabilidades baixas")
    print("   - Apenas SSH exposto (configurado corretamente)")
    print("   - HTTPS implementado")


def run_analysis(xml_file: str, output_prefix: str):
    """Executa a análise em um arquivo XML"""
    
    print(f"\n{'='*60}")
    print(f"🔍 EXECUTANDO ANÁLISE: {xml_file}")
    print(f"{'='*60}\n")
    
    # Renomear arquivo temporariamente
    if os.path.exists('scan_result.xml'):
        os.rename('scan_result.xml', 'scan_result.xml.bak')
    
    os.rename(xml_file, 'scan_result.xml')
    
    # Executar análise
    os.system('C:/Users/Windows/Desktop/TCC/integração/.venv/Scripts/python.exe nmap_to_zabbix.py')
    
    # Renomear relatórios
    if os.path.exists('relatorio_seguranca.md'):
        os.rename('relatorio_seguranca.md', f'{output_prefix}_relatorio.md')
    if os.path.exists('relatorio_seguranca.json'):
        os.rename('relatorio_seguranca.json', f'{output_prefix}_relatorio.json')
    
    # Restaurar
    os.rename('scan_result.xml', xml_file)
    if os.path.exists('scan_result.xml.bak'):
        os.rename('scan_result.xml.bak', 'scan_result.xml')
    
    print(f"\n✅ Relatórios salvos como:")
    print(f"   - {output_prefix}_relatorio.md")
    print(f"   - {output_prefix}_relatorio.json")


def main():
    """Função principal de teste"""
    
    print("\n" + "="*60)
    print("🧪 SISTEMA DE TESTES - ANÁLISE DE SEGURANÇA DE REDES")
    print("="*60)
    print("\nCriando cenários de teste realistas...\n")
    
    # Criar cenários
    print("📝 Gerando arquivos XML de teste...")
    test_scenario_1_empresa_insegura()
    test_scenario_2_casa_comum()
    test_scenario_3_servidor_seguro()
    
    print("\n" + "="*60)
    print("ESCOLHA UM TESTE PARA EXECUTAR:")
    print("="*60)
    print("\n1. 🔴 Empresa Insegura (CRÍTICO)")
    print("   - Múltiplas vulnerabilidades graves")
    print("   - Ideal para demonstrar detecção")
    print()
    print("2. 🟡 Casa Comum (MODERADO)")
    print("   - Cenário realista doméstico")
    print("   - Problemas típicos de segurança")
    print()
    print("3. 🟢 Servidor Seguro (BOM)")
    print("   - Configuração adequada")
    print("   - Poucas vulnerabilidades")
    print()
    print("4. 🔄 TODOS os cenários")
    print("   - Executa análise completa")
    print()
    print("0. ❌ Sair")
    print()
    
    choice = input("Digite sua escolha (0-4): ").strip()
    
    if choice == '1':
        run_analysis('test_cenario1.xml', 'cenario1_empresa')
    elif choice == '2':
        run_analysis('test_cenario2.xml', 'cenario2_casa')
    elif choice == '3':
        run_analysis('test_cenario3.xml', 'cenario3_seguro')
    elif choice == '4':
        print("\n🔄 Executando TODOS os cenários...\n")
        run_analysis('test_cenario1.xml', 'cenario1_empresa')
        input("\nPressione ENTER para continuar...")
        run_analysis('test_cenario2.xml', 'cenario2_casa')
        input("\nPressione ENTER para continuar...")
        run_analysis('test_cenario3.xml', 'cenario3_seguro')
        print("\n✅ Todos os testes concluídos!")
    elif choice == '0':
        print("\n👋 Saindo...")
        return
    else:
        print("\n❌ Opção inválida!")
        return
    
    print("\n" + "="*60)
    print("✅ TESTE CONCLUÍDO COM SUCESSO!")
    print("="*60)
    print("\n📁 Arquivos gerados:")
    print("   - test_cenario1.xml (Empresa Insegura)")
    print("   - test_cenario2.xml (Casa Comum)")
    print("   - test_cenario3.xml (Servidor Seguro)")
    print("   - *_relatorio.md (Relatórios de cada cenário)")
    print()
    print("💡 Dica: Abra os relatórios .md para ver os resultados!")
    print()


if __name__ == "__main__":
    main()
