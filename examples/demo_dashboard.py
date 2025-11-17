"""
Demo Completa - Dashboard com IA
Demonstra todas as funcionalidades do sistema
"""

import os
import subprocess
import time
import webbrowser


def check_ollama():
    """Verifica se Ollama está instalado e rodando"""
    print("\n🔍 Verificando Ollama...")
    
    # Verificar instalação
    try:
        result = subprocess.run(
            ['ollama', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"✅ Ollama instalado: {result.stdout.strip()}")
            ollama_installed = True
        else:
            ollama_installed = False
    except:
        ollama_installed = False
        print("❌ Ollama não encontrado")
    
    # Verificar se está rodando
    try:
        import requests
        response = requests.get('http://localhost:11434/api/tags', timeout=2)
        if response.status_code == 200:
            print("✅ Ollama está rodando")
            models = response.json().get('models', [])
            if models:
                print(f"✅ Modelos disponíveis:")
                for model in models:
                    print(f"   - {model['name']}")
                return True
            else:
                print("⚠️  Nenhum modelo instalado")
                return False
        else:
            print("⚠️  Ollama não está respondendo")
            return False
    except:
        if ollama_installed:
            print("⚠️  Ollama instalado mas não está rodando")
            print("   Execute: ollama serve")
        return False


def install_ollama_guide():
    """Mostra guia de instalação do Ollama"""
    print("\n" + "="*60)
    print("📥 COMO INSTALAR OLLAMA")
    print("="*60)
    print()
    print("Opção 1: Download direto")
    print("  → https://ollama.ai/download")
    print()
    print("Opção 2: Winget (Windows)")
    print("  → winget install Ollama.Ollama")
    print()
    print("Após instalar:")
    print("  1. ollama pull llama3.2")
    print("  2. ollama serve")
    print("="*60)
    
    choice = input("\nDeseja abrir o site de download? (s/n): ").strip().lower()
    if choice == 's':
        webbrowser.open('https://ollama.ai/download')
        print("✅ Site aberto no navegador")


def run_demo():
    """Executa demonstração completa"""
    print("\n" + "="*60)
    print("🎬 DEMONSTRAÇÃO COMPLETA - DASHBOARD COM IA")
    print("="*60)
    
    # Verificar Ollama
    has_ollama = check_ollama()
    
    if not has_ollama:
        print("\n⚠️  Ollama não detectado - Dashboard será gerado SEM IA")
        print("   (Ainda assim, o dashboard visual completo será criado)")
        print()
        choice = input("Deseja ver o guia de instalação do Ollama? (s/n): ").strip().lower()
        if choice == 's':
            install_ollama_guide()
            print("\nApós instalar o Ollama, execute este script novamente!")
            return
    
    # Executar análise
    print("\n" + "="*60)
    print("🚀 EXECUTANDO ANÁLISE COMPLETA")
    print("="*60)
    
    print("\n1️⃣ Processando scan do Nmap...")
    print("2️⃣ Analisando vulnerabilidades...")
    print("3️⃣ Gerando relatórios...")
    print("4️⃣ Criando dashboard HTML...")
    
    if has_ollama:
        print("5️⃣ Gerando análise com IA (pode demorar ~30-60s)...")
    
    print()
    
    # Executar sistema principal
    result = subprocess.run(
        ['C:/Users/Windows/Desktop/TCC/integração/.venv/Scripts/python.exe', 'nmap_to_zabbix.py'],
        capture_output=False,
        text=True
    )
    
    if result.returncode != 0:
        print("\n❌ Erro na execução")
        return
    
    # Verificar arquivos gerados
    print("\n" + "="*60)
    print("📁 ARQUIVOS GERADOS")
    print("="*60)
    
    files = [
        ('relatorio_seguranca.md', 'Relatório Markdown'),
        ('relatorio_seguranca.json', 'Dados JSON'),
        ('dashboard.html', 'Dashboard Interativo ⭐')
    ]
    
    for filename, description in files:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"✅ {filename:<30} - {description} ({size:,} bytes)")
        else:
            print(f"❌ {filename:<30} - NÃO ENCONTRADO")
    
    # Abrir dashboard
    print("\n" + "="*60)
    print("🌐 ABRINDO DASHBOARD NO NAVEGADOR")
    print("="*60)
    
    if os.path.exists('dashboard.html'):
        print("\n🎨 Dashboard será aberto no seu navegador padrão...")
        time.sleep(2)
        
        # Abrir no navegador
        webbrowser.open(os.path.abspath('dashboard.html'))
        
        print("\n✅ Dashboard aberto!")
        print()
        print("📊 O que você verá:")
        print("   • Estatísticas gerais (hosts, portas, vulnerabilidades)")
        print("   • Score de segurança visual")
        print("   • Gráfico de distribuição de vulnerabilidades")
        
        if has_ollama:
            print("   • 🤖 Análise inteligente gerada por IA")
            print("   • 💡 Plano de ação personalizado")
        
        print("   • Lista completa de hosts e vulnerabilidades")
        print("   • Recomendações específicas para cada problema")
        
    else:
        print("\n❌ Arquivo dashboard.html não encontrado")
    
    # Mostrar próximos passos
    print("\n" + "="*60)
    print("🎓 PARA O SEU TCC")
    print("="*60)
    print()
    print("Você agora tem:")
    print("  ✅ Sistema de análise automatizada")
    print("  ✅ Relatórios em múltiplos formatos")
    print("  ✅ Dashboard visual interativo")
    
    if has_ollama:
        print("  ✅ Análise inteligente com IA")
        print("  ✅ Recomendações personalizadas")
    else:
        print("  ⚠️  Instale Ollama para análise com IA")
    
    print()
    print("Próximos passos:")
    print("  1. Fazer scan da SUA rede real")
    print("  2. Gerar relatórios para diferentes cenários")
    print("  3. Comparar antes/depois de correções")
    print("  4. Usar no TCC para demonstrar eficácia")
    print()


def main():
    """Função principal"""
    print("="*60)
    print("🎬 DEMONSTRAÇÃO - DASHBOARD COM IA")
    print("="*60)
    print()
    print("Este script irá:")
    print("  1. Verificar se Ollama está instalado")
    print("  2. Executar análise completa da rede")
    print("  3. Gerar dashboard HTML interativo")
    print("  4. Abrir dashboard no navegador")
    print()
    
    choice = input("Pressione ENTER para continuar ou 'q' para sair: ").strip().lower()
    
    if choice == 'q':
        print("\n👋 Saindo...")
        return
    
    run_demo()
    
    print("\n" + "="*60)
    print("✅ DEMONSTRAÇÃO CONCLUÍDA!")
    print("="*60)
    print()


if __name__ == "__main__":
    main()
