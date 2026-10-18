import subprocess
import ctypes
import sys
import time


ADAPTADOR = "Wi-Fi"


def executar_powershell(comando):
    resultado = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy", "Bypass",
            "-Command", comando
        ],
        capture_output=True,
        text=True
    )

    if resultado.returncode != 0:
        print("\nERRO:")
        print(resultado.stderr)
        return None

    return resultado.stdout.strip()


def obter_modo_atual():
    comando = f'''
(Get-NetAdapterAdvancedProperty -Name "{ADAPTADOR}" -RegistryKeyword "WirelessMode").DisplayValue
'''

    resultado = executar_powershell(comando)

    if not resultado:
        return "Desconhecido"

    return resultado


def mostrar_modo_atual():
    modo = obter_modo_atual()

    if "b/g/n" in modo:
        estado = "MODO MIRACAST"
    elif "Automático" in modo or "Automatic" in modo:
        estado = "MODO AUTOMÁTICO"
    else:
        estado = "OUTRO MODO"

    print()
    print("Estado atual:")
    print(f"  {estado}")
    print(f"Wireless Mode: {modo}")
    print()


def reiniciar_wifi():
    print("Reiniciando adaptador Wi-Fi...")
    print()

    comando = f'''
Disable-NetAdapter -Name "{ADAPTADOR}" -Confirm:$false
Start-Sleep -Seconds 2
Enable-NetAdapter -Name "{ADAPTADOR}" -Confirm:$false
'''

    resultado = executar_powershell(comando)

    if resultado is not None:
        time.sleep(4)
        print("Adaptador Wi-Fi reiniciado.")
        print()


def alterar_modo(valor, nome):
    print()
    print("========================================")
    print("       ALTERANDO MODO WI-FI")
    print("========================================")
    print()
    print(f"Novo modo: {nome}")
    print(f"WirelessMode: {valor}")
    print()

    comando = f'''
Set-NetAdapterAdvancedProperty `
    -Name "{ADAPTADOR}" `
    -RegistryKeyword "WirelessMode" `
    -RegistryValue {valor}
'''

    resultado = executar_powershell(comando)

    if resultado is None:
        return

    print("Configuração alterada.")
    print()

    reiniciar_wifi()

    print("========================================")
    print("       CONFIGURAÇÃO APLICADA")
    print("========================================")

    mostrar_modo_atual()


def modo_miracast():
    alterar_modo(
        16,
        "IEEE 802.11b/g/n (2.4 GHz)"
    )


def modo_automatico():
    alterar_modo(
        8,
        "Automático"
    )


def verificar_administrador():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def iniciar_como_administrador():
    parametros = " ".join(
        f'"{arg}"' for arg in sys.argv
    )

    ctypes.windll.shell32.ShellExecuteW(
        None,
        "runas",
        sys.executable,
        parametros,
        None,
        1
    )


def menu():

    while True:

        print()
        print("========================================")
        print("          CONFIGURADOR WI-FI")
        print("========================================")

        mostrar_modo_atual()

        print("----------------------------------------")
        print("1 - Modo Miracast")
        print("    802.11b/g/n (2.4 GHz)")
        print()
        print("2 - Modo Automático")
        print("    Automático")
        print()
        print("0 - Sair")
        print("========================================")

        opcao = input("Escolha: ").strip()

        if opcao == "1":
            modo_miracast()

        elif opcao == "2":
            modo_automatico()

        elif opcao == "0":
            print()
            print("Saindo...")
            break

        else:
            print()
            print("Opção inválida.")


if __name__ == "__main__":

    if not verificar_administrador():
        print("Solicitando permissão de administrador...")

        iniciar_como_administrador()

        sys.exit()

    menu()