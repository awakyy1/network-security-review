"""
Script de Teste - Ollama e Dashboard com IA
Testa a integração com Ollama e gera dashboard profissional
"""

import subprocess
import requests
import time
import os


def check_ollama_installation():
    """Verifica se Ollama está instalado"""
    print("\n" + "="*60)
    print("VERIFICANDO INSTALAÇÃO DO OLLAMA")
    print("="*60)
    
    try:
        result = subprocess.run(
            ['ollama', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print(f"✓ Ollama instalado: {result.stdout.strip()}")
            return True
        else:
            print("✗ Ollama não encontrado")
            return False
    except FileNotFoundError:
        print("✗ Ollama não está instalado")
        print("\nPara instalar:")
        print("  1. Acesse: https://ollama.ai/download")
        print("  2. Ou execute: winget install Ollama.Ollama")
        return False
    except Exception as e:
        print(f"✗ Erro ao verificar: {e}")
        return False


def check_ollama_running():
    """Verifica se Ollama está rodando"""
    print("\n" + "="*60)
    print("VERIFICANDO SE OLLAMA ESTÁ RODANDO")
    print("="*60)
    
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=3)
        
        if response.status_code == 200:
            print("✓ Ollama está rodando na porta 11434")
            return True
        else:
            print(f"✗ Ollama respondeu com status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Ollama não está rodando")
        print("\nPara iniciar Ollama:")
        print("  Execute em outro terminal: ollama serve")
        return False
    except Exception as e:
        print(f"✗ Erro ao conectar: {e}")
        return False


def list_models():
    """Lista modelos instalados"""
    print("\n" + "="*60)
    print("MODELOS INSTALADOS")
    print("="*60)
    
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=3)
        
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            
            if models:
                print(f"\nEncontrados {len(models)} modelo(s):")
                for model in models:
                    name = model.get('name', 'Desconhecido')
                    size = model.get('size', 0) / (1024**3)  # GB
                    print(f"  • {name} ({size:.1f} GB)")
                return True
            else:
                print("\n✗ Nenhum modelo instalado")
                print("\nPara instalar um modelo:")
                print("  ollama pull llama3.2      (Recomendado - 2GB)")
                print("  ollama pull mistral       (Alternativa - 4GB)")
                return False
        else:
            print("✗ Erro ao listar modelos")
            return False
    except Exception as e:
        print(f"✗ Erro: {e}")
        return False


def test_ollama_generation():
    """Testa geração de texto com Ollama"""
    print("\n" + "="*60)
    print("TESTANDO GERAÇÃO DE TEXTO")
    print("="*60)
    
    print("\nEnviando prompt de teste para Ollama...")
    print("(Isso pode demorar 10-30 segundos na primeira vez)")
    
    try:
        start_time = time.time()
        
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                "model": "llama3.2",
                "prompt": "Explique em uma frase o que é segurança de redes.",
                "stream": False
            },
            timeout=60
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            text = result.get('response', '').strip()
            
            print(f"\n✓ Resposta gerada em {elapsed:.1f} segundos:")
            print("-" * 60)
            print(text)
            print("-" * 60)
            return True
        else:
            print(f"✗ Erro: Status {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("✗ Timeout - A IA demorou muito para responder")
        print("  Tente novamente ou use um modelo menor")
        return False
    except Exception as e:
        print(f"✗ Erro: {e}")
        return False


def run_analysis_with_ai():
    """Executa análise completa com IA"""
    print("\n" + "="*60)
    print("EXECUTANDO ANÁLISE COMPLETA COM IA")
    print("="*60)
    
    print("\nIsso irá:")
    print("  1. Processar o scan do Nmap")
    print("  2. Analisar vulnerabilidades")
    print("  3. Gerar insights com IA")
    print("  4. Criar dashboard profissional")
    print("\n⏱️  Tempo estimado: 60-90 segundos")
    
    input("\nPressione ENTER para continuar...")
    
    print("\nExecutando...")
    
    result = subprocess.run(
        ['C:/Users/Windows/Desktop/TCC/integração/.venv/Scripts/python.exe', 'nmap_to_zabbix.py'],
        cwd='C:/Users/Windows/Desktop/TCC/integração'
    )
    
    if result.returncode == 0:
        print("\n✓ Análise concluída com sucesso!")
        
        if os.path.exists('dashboard.html'):
            print("\n" + "="*60)
            print("ABRINDO DASHBOARD")
            print("="*60)
            
            import webbrowser
            webbrowser.open(os.path.abspath('dashboard.html'))
            print("\n✓ Dashboard aberto no navegador!")
        
        return True
    else:
        print("\n✗ Erro na análise")
        return False


def main():
    """Função principal"""
    
    print("\n" + "="*70)
    print(" " * 15 + "TESTE DE INTEGRAÇÃO OLLAMA + DASHBOARD")
    print("="*70)
    
    print("\nEste script irá:")
    print("  1. Verificar se Ollama está instalado e rodando")
    print("  2. Listar modelos disponíveis")
    print("  3. Testar geração de texto com IA")
    print("  4. Executar análise completa com dashboard profissional")
    
    # Verificar instalação
    if not check_ollama_installation():
        print("\n" + "="*60)
        print("AÇÃO NECESSÁRIA")
        print("="*60)
        print("\nInstale o Ollama primeiro:")
        print("  https://ollama.ai/download")
        print("\nOu use winget:")
        print("  winget install Ollama.Ollama")
        return
    
    # Verificar se está rodando
    if not check_ollama_running():
        print("\n" + "="*60)
        print("AÇÃO NECESSÁRIA")
        print("="*60)
        print("\nInicie o Ollama em outro terminal:")
        print("  ollama serve")
        print("\nDepois execute este script novamente.")
        return
    
    # Listar modelos
    if not list_models():
        print("\n" + "="*60)
        print("AÇÃO NECESSÁRIA")
        print("="*60)
        print("\nBaixe um modelo primeiro:")
        print("  ollama pull llama3.2")
        print("\nDepois execute este script novamente.")
        return
    
    # Testar geração
    print("\n" + "="*60)
    print("TESTE 1: Geração de Texto")
    print("="*60)
    
    choice = input("\nDeseja testar a geração de texto? (s/n): ").strip().lower()
    if choice == 's':
        if not test_ollama_generation():
            print("\n⚠️  Teste de geração falhou")
            print("Mas vamos continuar com a análise...")
    
    # Executar análise
    print("\n" + "="*60)
    print("TESTE 2: Análise Completa com Dashboard")
    print("="*60)
    
    choice = input("\nDeseja executar análise completa com IA? (s/n): ").strip().lower()
    if choice == 's':
        run_analysis_with_ai()
    
    print("\n" + "="*70)
    print(" " * 20 + "TESTE CONCLUÍDO")
    print("="*70)
    
    print("\n📋 RESUMO:")
    print("  ✓ Ollama instalado e funcionando")
    print("  ✓ Modelo de IA disponível")
    print("  ✓ Sistema pronto para gerar dashboards com IA")
    
    print("\n💡 PRÓXIMOS PASSOS:")
    print("  1. Execute: python nmap_to_zabbix.py")
    print("  2. Aguarde a IA gerar as análises (~60s)")
    print("  3. Abra: dashboard.html")
    print("  4. Veja as análises inteligentes geradas!")
    
    print()


if __name__ == "__main__":
    main()
