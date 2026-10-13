#pragma once

// Hardware-only D3D12 capability check for Xbox One Developer Game mode.
// Do not use WARP or accept software adapters for emulation.
#include <d3d12.h>
#include <dxgi1_4.h>
#include <wrl/client.h>

namespace XboxOneProbe
{
struct Result
{
    bool available{};
    HRESULT status{E_FAIL};
};
inline Result ProbeD3D12()
{
    using Microsoft::WRL::ComPtr;
    ComPtr<IDXGIFactory1> factory;
    HRESULT last = CreateDXGIFactory1(IID_PPV_ARGS(&factory));
    if (FAILED(last))
        return {false, last};

    last = DXGI_ERROR_NOT_FOUND;
    for (UINT index = 0; ; ++index)
    {
        ComPtr<IDXGIAdapter1> adapter;
        const HRESULT enumerated = factory->EnumAdapters1(index, &adapter);
        if (enumerated == DXGI_ERROR_NOT_FOUND)
            break;
        if (FAILED(enumerated))
        {
            last = enumerated;
            continue;
        }
        DXGI_ADAPTER_DESC1 desc{};
        if (FAILED(adapter->GetDesc1(&desc)) ||
            (desc.Flags & DXGI_ADAPTER_FLAG_SOFTWARE))
            continue;

        ComPtr<ID3D12Device> device;
        const HRESULT hr = D3D12CreateDevice(adapter.Get(),
            D3D_FEATURE_LEVEL_11_0, IID_PPV_ARGS(&device));
        if (SUCCEEDED(hr) && device)
            return {true, S_OK};
        last = hr;
    }
    return {false, last};
}
} // namespace XboxOneProbe