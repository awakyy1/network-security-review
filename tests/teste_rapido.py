"""
TESTE RÁPIDO - Análise de Segurança
Cria e testa cenário de empresa insegura
"""

import os
import subprocess

# Criar arquivo XML de teste
xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE nmaprun>
<nmaprun scanner="nmap" args="nmap -sV -O empresa" start="1700000000" version="7.94">
  <host starttime="1700000000" endtime="1700000100">
    <status state="up" reason="echo-reply"/>
    <address addr="10.0.1.10" addrtype="ipv4"/>
    <hostnames>
      <hostname name="servidor-web.empresa.local" type="PTR"/>
    </hostnames>
    <ports>
      <port protocol="tcp" portid="21">
        <state state="open" reason="syn-ack"/>
        <service name="ftp" product="vsftpd" version="3.0.3"/>
      </port>
      <port protocol="tcp" portid="22">
        <state state="open" reason="syn-ack"/>
        <service name="ssh" product="OpenSSH" version="8.2p1"/>
      </port>
      <port protocol="tcp" portid="23">
        <state state="open" reason="syn-ack"/>
        <service name="telnet"/>
      </port>
      <port protocol="tcp" portid="80">
        <state state="open" reason="syn-ack"/>
        <service name="http" product="Apache" version="2.4.41"/>
      </port>
      <port protocol="tcp" portid="3306">
        <state state="open" reason="syn-ack"/>
        <service name="mysql" product="MySQL" version="5.7.33"/>
      </port>
    </ports>
    <os>
      <osmatch name="Ubuntu Linux 20.04" accuracy="95"/>
    </os>
  </host>
  <host starttime="1700000100" endtime="1700000200">
    <status state="up" reason="echo-reply"/>
    <address addr="10.0.1.20" addrtype="ipv4"/>
    <hostnames>
      <hostname name="servidor-arquivos.empresa.local" type="PTR"/>
    </hostnames>
    <ports>
      <port protocol="tcp" portid="139">
        <state state="open" reason="syn-ack"/>
        <service name="netbios-ssn"/>
      </port>
      <port protocol="tcp" portid="445">
        <state state="open" reason="syn-ack"/>
        <service name="netbios-ssn" product="Samba" version="3.6.25"/>
      </port>
      <port protocol="tcp" portid="3389">
        <state state="open" reason="syn-ack"/>
        <service name="rdp" product="Microsoft Terminal Services"/>
      </port>
    </ports>
    <os>
      <osmatch name="Microsoft Windows Server 2012 R2" accuracy="95"/>
    </os>
  </host>
  <host starttime="1700000200" endtime="1700000300">
    <status state="up" reason="echo-reply"/>
    <address addr="10.0.1.30" addrtype="ipv4"/>
    <hostnames>
      <hostname name="servidor-bd.empresa.local" type="PTR"/>
    </hostnames>
    <ports>
      <port protocol="tcp" portid="22">
        <state state="open" reason="syn-ack"/>
        <service name="ssh" product="OpenSSH" version="7.4"/>
      </port>
      <port protocol="tcp" portid="3306">
        <state state="open" reason="syn-ack"/>
        <service name="mysql" product="MySQL" version="5.6.51"/>
      </port>
      <port protocol="tcp" portid="5432">
        <state state="open" reason="syn-ack"/>
        <service name="postgresql" product="PostgreSQL" version="9.6"/>
      </port>
    </ports>
    <os>
      <osmatch name="CentOS 7" accuracy="95"/>
    </os>
  </host>
  <host starttime="1700000300" endtime="1700000400">
    <status state="up" reason="echo-reply"/>
    <address addr="10.0.1.40" addrtype="ipv4"/>
    <hostnames>
      <hostname name="servidor-backup.empresa.local" type="PTR"/>
    </hostnames>
    <ports>
      <port protocol="tcp" portid="21">
        <state state="open" reason="syn-ack"/>
        <service name="ftp" product="ProFTPD" version="1.3.6"/>
      </port>
      <port protocol="tcp" portid="22">
        <state state="open" reason="syn-ack"/>
        <service name="ssh" product="OpenSSH" version="7.9"/>
      </port>
      <port protocol="tcp" portid="5900">
        <state state="open" reason="syn-ack"/>
        <service name="vnc" product="VNC" version="4.1.2"/>
      </port>
    </ports>
    <os>
      <osmatch name="Debian 10" accuracy="95"/>
    </os>
  </host>
</nmaprun>"""

print("="*60)
print("🧪 TESTE: Empresa com Múltiplas Vulnerabilidades")
print("="*60)
print()
print("📝 Criando cenário de teste...")
print("   - 4 servidores")
print("   - 14 portas abertas")
print("   - Múltiplas vulnerabilidades esperadas")
print()

# Salvar XML
with open('scan_result.xml', 'w', encoding='utf-8') as f:
    f.write(xml_content)

print("✓ Arquivo scan_result.xml criado")
print()
print("🔍 Executando análise...")
print("="*60)
print()

# Executar análise
result = subprocess.run(
    ['C:/Users/Windows/Desktop/TCC/integração/.venv/Scripts/python.exe', 'nmap_to_zabbix.py'],
    capture_output=False,
    text=True
)

print()
print("="*60)
print("✅ TESTE CONCLUÍDO!")
print("="*60)
print()
print("📊 Verifique os resultados:")
print("   1. relatorio_seguranca.md - Relatório completo")
print("   2. relatorio_seguranca.json - Dados estruturados")
print()

# Mostrar preview do relatório
if os.path.exists('relatorio_seguranca.md'):
    print("📄 PREVIEW DO RELATÓRIO:")
    print("-"*60)
    with open('relatorio_seguranca.md', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for i, line in enumerate(lines[:30]):  # Primeiras 30 linhas
            print(line.rstrip())
    print("-"*60)
    print(f"\n[... restante do relatório no arquivo ...]")
