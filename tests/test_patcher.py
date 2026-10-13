from pathlib import Path
from tempfile import TemporaryDirectory
from importlib.util import spec_from_file_location, module_from_spec

src = Path(__file__).resolve().parents[1]
spec = spec_from_file_location('v1patch', src / 'patches/apply_v1.py')
patcher = module_from_spec(spec)
spec.loader.exec_module(patcher)

# Mock source is used for fast unit checks; CI additionally tests real pinned
# upstream files. Neither test implies a successful Windows/Xbox build.
mock_device = '''// The embedded renderer has one strict device contract
const D3D_FEATURE_LEVEL featureLevels[] = { D3D_FEATURE_LEVEL_11_0 };
if (FAILED(hr))
	{
		// Se a inicialização falhar, retorne para o dispositivo WARP.
		SOME_WARP_CODE();
	}

	// Armazene ponteiros para o dispositivo da API do Direct3D 11.3'''
mock_page = '''#include "pch.h"
#include "DirectXPage.xaml.h"
namespace
{
const auto VisibleValue = static_cast<int>(0);
void DirectXPage::InitializeEmulator(float width, float height)
{
	if (m_main || width <= 0.0f || height <= 0.0f)
		return;

	// Creating the template swap chain
}
if (settings.graphics_api != 3)
settings.graphics_api = 3;
rendererMetricsText->Text = "Renderer         D3D11";
settings.graphics_api = 3;
'''
vcx = '''<Project><ItemDefinitionGroup Condition="'$(Configuration)|$(Platform)'=='Debug|x64'"><ClCompile><PreprocessorDefinitions>_DEBUG;%(PreprocessorDefinitions)</PreprocessorDefinitions></ClCompile></ItemDefinitionGroup><ItemDefinitionGroup Condition="'$(Configuration)|$(Platform)'=='Release|x64'"><ClCompile><PreprocessorDefinitions>NDEBUG;%(PreprocessorDefinitions)</PreprocessorDefinitions></ClCompile></ItemDefinitionGroup></Project>'''
manifest = '''<Package><Properties><DisplayName>Cemu_UWP_Host</DisplayName></Properties><Applications><Application><VisualElements DisplayName="Cemu_UWP_Host" Description="Cemu_UWP_Host"/></Application></Applications></Package>'''

with TemporaryDirectory() as tmp:
    host = Path(tmp)
    for key, value in {
        'Common/DeviceResources.cpp': mock_device,
        'DirectXPage.xaml.cpp': mock_page,
        'Cemu-UWP-Host.vcxproj': vcx,
        'Package.appxmanifest': manifest,
    }.items():
        p = host / key
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(value, encoding='utf-8')
    changes = patcher.validate_data(host)
    assert len(changes) == 5
    for p, data in changes.items():
        p.write_bytes(data)
    assert all(p.read_bytes() == data for p, data in patcher.validate_data(host).items())
    d = (host / 'Common/DeviceResources.cpp').read_text()
    assert d.count('#if defined(CEMU_XBOX_ONE_V1)') == 2
    assert 'DX::ThrowIfFailed(hr);' in d
    page = (host / 'DirectXPage.xaml.cpp').read_text()
    assert page.count('settings.graphics_api = kHostGraphicsApi;') == 2
    assert 'ProbeD3D12' in page
    print('V1 patcher tests passed; compile/runtime remain unverified.')
