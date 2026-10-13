#!/usr/bin/env python3
"""Apply the Xbox One original experimental profile to rodrigoandrigo/Cemu-UWP-Host.

Strict, idempotent source patcher. This does not modify the emulation core.
"""
import argparse
import pathlib
import sys
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
HEADER = ROOT / "patches" / "XboxOneProbe.h"


def replace_one(text, needle, replacement, path):
    count = text.count(needle)
    if count != 1:
        raise ValueError(f"{path}: expected exactly one anchor, found {count}: {needle[:90]!r}")
    return text.replace(needle, replacement, 1)


def patch_device_resources(text):
    if "CEMU_XBOX_ONE_V1" in text:
        return text
    path = "Common/DeviceResources.cpp"
    text = replace_one(text,
        "const D3D_FEATURE_LEVEL featureLevels[] = { D3D_FEATURE_LEVEL_11_0 };",
        """// Xbox One UWP D3D11 hardware exposes FL 10_1. This device is only
	// the host presentation surface; Cemu renders via its own D3D12 backend.
#if defined(CEMU_XBOX_ONE_V1)
	const D3D_FEATURE_LEVEL featureLevels[] = { D3D_FEATURE_LEVEL_10_1 };
#else
	const D3D_FEATURE_LEVEL featureLevels[] = { D3D_FEATURE_LEVEL_11_0 };
#endif""", path)
    warp_anchor = "if (FAILED(hr))\n\t{\n\t\t// Se a inicialização falhar, retorne para o dispositivo WARP."
    text = replace_one(text, warp_anchor,
        """if (FAILED(hr))
	{
#if defined(CEMU_XBOX_ONE_V1)
		// No software/WARP fallback on Xbox One.
		OutputDebugStringA("[Cemu Xbox One V1] Hardware D3D11 FL 10_1 failed.\\n");
		DX::ThrowIfFailed(hr);
#else
		// Se a inicialização falhar, retorne para o dispositivo WARP.""", path)
    end_anchor = "\n\t}\n\n\t// Armazene ponteiros para o dispositivo da API do Direct3D 11.3"
    text = replace_one(text, end_anchor,
        "\n#endif\n\t}\n\n\t// Armazene ponteiros para o dispositivo da API do Direct3D 11.3", path)
    return text


def patch_page(text):
    if "CEMU_XBOX_ONE_V1" in text:
        return text
    path = "DirectXPage.xaml.cpp"
    text = replace_one(text, '#include "DirectXPage.xaml.h"',
        '#include "DirectXPage.xaml.h"\n#include "XboxOneProbe.h"', path)
    text = replace_one(text, "namespace\n{\nconst auto VisibleValue",
        """namespace
{
#if defined(CEMU_XBOX_ONE_V1)
constexpr int kHostGraphicsApi = 4; // modified Cemu GraphicAPI::kD3D12
#else
constexpr int kHostGraphicsApi = 3; // modified Cemu GraphicAPI::kD3D11
#endif
const auto VisibleValue""", path)
    initialize = """if (m_main || width <= 0.0f || height <= 0.0f)
		return;

	// Creating the template swap chain"""
    init_repl = """if (m_main || width <= 0.0f || height <= 0.0f)
		return;

#if defined(CEMU_XBOX_ONE_V1)
	// Game mode required for DX12 hardware. Do not silently fall back to WARP.
	const auto probe = XboxOneProbe::ProbeD3D12();
	if (!probe.available)
	{
		char reason[240]{};
		sprintf_s(reason, sizeof(reason),
			"Xbox One DX12 hardware FL11_0 unavailable (HRESULT 0x%08X). Set package type to Game in Dev Home.",
			static_cast<unsigned int>(probe.status));
		AppendError(reason);
		launchStatus->Text = "D3D12 hardware unavailable. Set app type to Game in Dev Home.";
		return;
	}
	OutputDebugStringA("[Cemu Xbox One V1] DX12 hardware FL11_0 available.\\n");
#endif

	// Creating the template swap chain"""
    text = replace_one(text, initialize, init_repl, path)
    text = replace_one(text, "if (settings.graphics_api != 3)",
        "if (settings.graphics_api != kHostGraphicsApi)", path)
    if text.count("settings.graphics_api = 3;") != 2:
        raise ValueError(f"{path}: unexpected graphics_api assignments")
    text = text.replace("settings.graphics_api = 3;", "settings.graphics_api = kHostGraphicsApi;")
    text = replace_one(text,
        'rendererMetricsText->Text = "Renderer         D3D11";',
        'rendererMetricsText->Text = kHostGraphicsApi == 4 ? "Renderer         D3D12 (experimental)" : "Renderer         D3D11";',path)
    return text


def patch_vcxproj(text):
    if "CEMU_XBOX_ONE_V1" in text:
        return text
    path = "Cemu-UWP-Host.vcxproj"
    for config, macro in [("Debug", "_DEBUG"), ("Release", "NDEBUG")]:
        tag = f'<ItemDefinitionGroup Condition="\'$(Configuration)|$(Platform)\'==\'{config}|x64\'">'
        begin = text.find(tag)
        if begin == -1:
            raise ValueError(f"{path}: no {config}|x64 group")
        end = text.find("</ItemDefinitionGroup>", begin)
        if end == -1:
            raise ValueError(f"{path}: unclosed {config}|x64 group")
        section = text[begin:end]
        needle = f"<PreprocessorDefinitions>{macro};%(PreprocessorDefinitions)</PreprocessorDefinitions>"
        if section.count(needle) != 1:
            raise ValueError(f"{path}: unexpected {config}|x64 preprocessor definitions")
        section = section.replace(needle,
            f"<PreprocessorDefinitions>{macro};CEMU_XBOX_ONE_V1;%(PreprocessorDefinitions)</PreprocessorDefinitions>")
        text = text[:begin] + section + text[end:]
    return text


def patch_manifest(text):
    # Only display-name rebrand to preserve the upstream signing publisher.
    if 'Cemu Xbox One V1 Experimental' in text:
        return text
    path = "Package.appxmanifest"
    text = replace_one(text, '<DisplayName>Cemu_UWP_Host</DisplayName>',
        '<DisplayName>Cemu Xbox One V1 Experimental</DisplayName>', path)
    text = replace_one(text, 'DisplayName="Cemu_UWP_Host"',
        'DisplayName="Cemu Xbox One V1 Experimental"', path)
    text = replace_one(text, 'Description="Cemu_UWP_Host"',
        'Description="Experimental Wii U emulator port for Xbox One in Developer Mode"', path)
    return text


def validate_data(host):
    pairs = {
        "Common/DeviceResources.cpp": patch_device_resources,
        "DirectXPage.xaml.cpp": patch_page,
        "Cemu-UWP-Host.vcxproj": patch_vcxproj,
        "Package.appxmanifest": patch_manifest,
    }
    updates = {}
    for path, fn in pairs.items():
        target = host / path
        if not target.is_file():
            raise ValueError(f"Missing upstream file: {target}")
        data = target.read_bytes()
        has_crlf = b"\r\n" in data
        decoded = data.decode('utf-8-sig').replace('\r\n', '\n')
        updated = fn(decoded)
        if path.endswith('.vcxproj') or path.endswith('.appxmanifest'):
            ET.fromstring(updated)
        result = updated.replace('\n', '\r\n') if has_crlf else updated
        if data.startswith(b"\xef\xbb\xbf"):
            encoded = b"\xef\xbb\xbf" + result.encode('utf-8')
        else:
            encoded = result.encode('utf-8')
        updates[target] = encoded
    if not HEADER.exists():
        raise ValueError(f"missing {HEADER}")
    header_path = host / "XboxOneProbe.h"
    if header_path.exists() and header_path.read_bytes() != HEADER.read_bytes():
        raise ValueError("XboxOneProbe.h exists with different content; refusing to overwrite")
    updates[header_path] = HEADER.read_bytes()
    return updates


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--host', type=pathlib.Path, required=True,
        help='Checkout of rodrigoandrigo/Cemu-UWP-Host')
    p.add_argument('--dry-run', action='store_true')
    args = p.parse_args()
    try:
        updates = validate_data(args.host.resolve())
        changed = [k for k, v in updates.items() if not k.exists() or k.read_bytes() != v]
        for path in changed:
            print(f"{'WOULD UPDATE' if args.dry_run else 'UPDATING'}: {path}")
        if not args.dry_run:
            for path in changed:
                path.write_bytes(updates[path])
        if not changed:
            print('Xbox One V1 patch already applied (no changes).')
        else:
            print(f"{'Validated' if args.dry_run else 'Updated'} {len(changed)} files.")
    except (ValueError, UnicodeError, OSError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
