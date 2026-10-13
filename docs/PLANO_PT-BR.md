# Cemu Xbox One original — V1 experimental

Esta versão é um **kit de alterações no código-fonte**, não um emulador compilado ou comprovadamente funcional.

## Alterações da V1

1. Teste do DirectX 12 Feature Level 11.0 exclusivamente em GPU física, sem WARP.
2. Dispositivo DirectX 11 10.1 apenas para a superfície gráfica do host UWP.
3. Seleção forçada do backend experimental DirectX 12 do Cemu.
4. Perfil de compilação x64 CEMU_XBOX_ONE_V1, limitado ao host e isolado das builds Series S.
5. Diagnósticos para ausência de D3D12 e instruções para Windows/Dev Mode.

## Testes

Primeiro compile o runtime e o host no Windows com Visual Studio, SDK e ferramentas UWP. Depois instale o pacote no Xbox One original em **Developer Mode** e configure o aplicativo como **Game** (não App). Inicie o host e confirme a detecção de D3D12 por hardware. Só então teste um homebrew Wii U ELF/RPX e recolha logs.

## Ainda pendente

O backend D3D12 é experimental. A inicialização de pipelines, shaders, swapchain, JIT e uso de RAM podem falhar mesmo após a deteção da GPU. O AMD Jaguar não possui AVX2/BMI2; dependências e código JIT precisam ser validados. Ainda não foram realizados testes em hardware, nem há garantia de desempenho ou compatibilidade com jogos.

## Comandos no PowerShell

    .\scripts\prepare.ps1 -Workspace C:\CemuXboxOneWorkspace
    .\scripts\build.ps1 -Workspace C:\CemuXboxOneWorkspace

Não execute esses comandos no Xbox ou Termux. Não inclua BIOS, chaves ou jogos proprietários no repositório.