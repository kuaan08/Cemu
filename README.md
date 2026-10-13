<div align="center">
  <img src="https://raw.githubusercontent.com/cemu-project/Cemu/main/src/resource/logo_icon.png" alt="Cemu logo" width="104">
  <h1>Cemu for Xbox One</h1>
  <p>An experimental Wii U emulation project for the original Xbox One.</p>
  <p>Built around <a href="https://github.com/cemu-project/Cemu">Cemu</a> and its community-developed <a href="https://github.com/rodrigoandrigo/Cemu-UWP-Host">UWP host</a>.</p>
  <p><strong>Xbox One (2013) · x64 · Developer Mode</strong></p>
</div>

---

## About the project

Cemu for Xbox One explores bringing Wii U emulation to the original Xbox One through the Universal Windows Platform (UWP). The focus is on compatible graphics initialization, a controller-friendly experience, and performance work tailored to Xbox One hardware.

This repository provides the Xbox One-specific **source patches, build scripts, and development tests**. It retrieves the required Cemu and UWP host source code during setup rather than duplicating those repositories.

**Development status:** V1 Experimental. The source patches pass automated validation, but a working Xbox One application has **not** been compiled or tested on the console. Game compatibility and performance are not established. There is currently **no downloadable APPX release**.

## Current work

| Area | V1 implementation |
| --- | --- |
| **Xbox One graphics initialization** | Uses Direct3D 11 Feature Level 10.1 for the host presentation device, with a separate experimental Direct3D 12 rendering path in Cemu. |
| **Hardware detection** | Checks for a non-software Direct3D 12 Feature Level 11.0 device before starting the emulator. |
| **Renderer configuration** | Selects the experimental Direct3D 12 backend for this Xbox One build profile. |
| **Platform-specific changes** | Isolates Xbox One modifications behind an x64 build definition, keeping the original UWP host behavior separate. |
| **Build preparation** | Scripts obtain the required sources, apply the patches, and invoke the Windows UWP build tools. |
| **Quality checks** | GitHub Actions tests patch syntax, application against the intended UWP host, and repeat application. |

These are **development features**, not confirmation that Wii U games can run on Xbox One. Rendering, PowerPC recompilation, memory use, and long-session stability still require hardware testing.

## Building from source

You need a Windows x64 development PC with Git, Python 3, CMake, the Windows SDK, and Visual Studio with MSVC and UWP C++ development tools. The build scripts currently target **Visual Studio 2026 (MSVC v145)** and **Windows SDK 10.0.26100.0**.

### Prepare the project

Clone this repository and run the preparation script from PowerShell:

```powershell
git clone https://github.com/kuaan08/Cemu.git
cd Cemu

.\scripts\prepare.ps1 -Workspace C:\CemuXboxOneWorkspace
```

The script checks out the modified Cemu core, Cemu UWP Host, and SDL3 UWP dependency, then applies the Xbox One changes to the host.

### Build the application

Open a **Developer PowerShell for Visual Studio** and run:

```powershell
.\scripts\build.ps1 -Workspace C:\CemuXboxOneWorkspace
```

The build attempts to compile Cemu for x64 and package the modified UWP host. If your Visual Studio installation differs from the default path, pass the appropriate `-MSBuild` argument. Build requirements and extra development notes are available in [the technical guide](docs/PLANO_PT-BR.md).

**Note:** The automated workflow in [GitHub Actions](https://github.com/kuaan08/Cemu/actions/workflows/patch-validation.yml) validates the source patches only. It does not currently build or distribute an Xbox package.

## Running on Xbox One

The target is the **original Xbox One**, running in Developer Mode.

1. Build and sign the x64 UWP package on Windows.
2. Install the package through the Xbox developer deployment tools.
3. In Xbox Dev Home, configure the installed application as **Game**, not App.
4. Launch the application and inspect its diagnostics for the hardware Direct3D 12 check.
5. Once initialization works, test a simple, legally obtained Wii U homebrew application before trying more demanding software.

Game mode is important because the Xbox One's UWP graphics capabilities differ between application and game contexts. A successful Direct3D 12 detection check alone does not guarantee that the emulator will render correctly.

## Development priorities

- **Graphics:** Validate Direct3D 12 device creation, presentation, shader translation, and GPU compatibility.
- **CPU:** Review the PowerPC-to-x64 recompilation path for the Xbox One's AMD Jaguar instruction set.
- **Memory:** Measure and control runtime memory usage within Xbox UWP Game limits.
- **Input and usability:** Verify Xbox controller input and the embedded UI on real hardware.
- **Compatibility:** Establish repeatable homebrew tests and document issues before making gameplay claims.
- **Performance:** Profile frame timing, shader compilation, and CPU/GPU bottlenecks after basic operation is stable.

## Troubleshooting

**The application cannot initialize graphics.** Confirm it is configured as **Game** in Developer Mode. The V1 diagnostics distinguish missing hardware Direct3D 12 support from later emulator initialization failures.

**The Windows build fails.** Check the installed Visual Studio toolset, UWP components, SDK, and availability of the required Cemu libraries. See the build output for the failing dependency or target.

**The emulator opens but a title does not launch.** This is an experimental port. Gather logs before changing renderer options or disabling safety checks. A game launching on a PC or Xbox Series console does not establish Xbox One compatibility.

**A patch cannot be applied.** Use the pinned source revisions downloaded by `prepare.ps1`. If you modified those files yourself, back up your changes and inspect the reported mismatch before applying anything manually.

## Credits and licenses

This project builds on the work of the [Cemu development team](https://github.com/cemu-project/Cemu) and its contributors, the [Cemu UWP Host project](https://github.com/rodrigoandrigo/Cemu-UWP-Host), the [modified Cemu runtime](https://github.com/rodrigoandrigo/Cemu), and [SDL3 UWP](https://github.com/rodrigoandrigo/SDL3_UWP).

- **Xbox One adaptation:** [kuaan08](https://github.com/kuaan08).
- **Cemu emulator:** Mozilla Public License 2.0; original copyright and license obligations remain applicable.
- **Cemu UWP Host:** Apache License 2.0; preserve original license and attribution notices.
- **Dependencies:** Third-party components remain subject to their respective licenses.

This repository does not provide commercial games, Nintendo firmware, console keys, or proprietary content. Use software and game backups you are legally entitled to use.

This is an independent community project and is not affiliated with or endorsed by Nintendo or Microsoft.
