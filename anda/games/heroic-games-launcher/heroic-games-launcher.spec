%global debug_package %{nil}
%global __provides_exclude ^((libffmpeg[.]so.*)|(lib.*\\.so.*))$
%global __requires_exclude ^((libffmpeg[.]so.*)|(lib.*\\.so.*))$
%define _build_id_links none
%global git_name HeroicGamesLauncher

Name:          heroic-games-launcher
Version:       2.16.0
Release:       2%?dist
Summary:       A games launcher for GOG, Amazon, and Epic Games
License:       GPL-3.0-only AND MIT AND BSD-3-Clause
URL:           https://heroicgameslauncher.com
Source0:       https://raw.githubusercontent.com/Heroic-Games-Launcher/%{git_name}/refs/heads/main/flatpak/com.heroicgameslauncher.hgl.desktop
### Makes it actually sign the package, though will say it was skipped first.
Patch0:        afterPack.diff
BuildRequires: anda-srpm-macros
BuildRequires: desktop-file-utils
### Electron builder builds some things with GCC(++), Git, and Make
BuildRequires: gcc
BuildRequires: gcc-c++
BuildRequires: git
BuildRequires: make
BuildRequires: nodejs
BuildRequires: pnpm
BuildRequires: python3
Requires:      alsa-lib
Requires:      atk
Requires:      at-spi2-core
Requires:      gtk3
Requires:      hicolor-icon-theme
Requires:      libXext
Requires:      libXfixes
Requires:      nss
Requires:      python3
Requires:      which
Recommends:    gamemode
Recommends:    mangohud
Recommends:    umu-launcher
# Workaround for GNOME issues with libei
Recommends:    (extest if gnome-shell)
Provides:      bundled(gogdl)
Provides:      bundled(legendary)
Provides:      bundled(nile)
AutoReq:       no
Packager:      Gilver E. <rockgrub@disroot.org>

%description
Heroic is a Free and Open Source Epic, GOG, and Amazon Prime Games launcher for Linux, Windows, and macOS.

%prep
rm -rf ./*
%git_clone https://github.com/Heroic-Games-Launcher/%{git_name}.git v%{version}
%autopatch -p1
sed -i 's/Exec=.*%u/Exec=\/usr\/share\/heroic\/heroic %U/g' %{SOURCE0}
sed -i 's/Icon=.*/Icon=heroic/g' %{SOURCE0}

%build
pnpm install
pnpm run download-helper-binaries
pnpm dist:linux

%install
mkdir -p %{buildroot}%{_datadir}/heroic
%ifarch aarch64
mv $(find dist/linux-arm64-unpacked -name "*LICENSE*") .
mv dist/linux-arm64-unpacked/* %{buildroot}%{_datadir}/heroic
%else
mv $(find dist/linux-unpacked -name "*LICENSE*") .
mv dist/linux-unpacked/* %{buildroot}%{_datadir}/heroic
%endif
mkdir -p %{buildroot}%{_bindir}
# Make names executable
ln -sr %{_datadir}/heroic/heroic %{buildroot}%{_bindir}/%{name}
ln -sr %{_datadir}/heroic/heroic %{buildroot}%{_bindir}/heroic
install -Dm644 public/icon.png %{buildroot}%{_datadir}/pixmaps/heroic.png
install -Dm644 dist/.icon-set/icon_16x16.png %{buildroot}%{_iconsdir}/hicolor/16x16/heroic.png
install -Dm644 dist/.icon-set/icon_32x32.png %{buildroot}%{_iconsdir}/hicolor/32x32/heroic.png
install -Dm644 dist/.icon-set/icon_48x48.png %{buildroot}%{_iconsdir}/hicolor/48x48/heroic.png
install -Dm644 dist/.icon-set/icon_64x64.png %{buildroot}%{_iconsdir}/hicolor/64x64/heroic.png
install -Dm644 dist/.icon-set/icon_128x128.png %{buildroot}%{_iconsdir}/hicolor/128x128/heroic.png
install -Dm644 dist/.icon-set/icon_256x256.png %{buildroot}%{_iconsdir}/hicolor/256x256/heroic.png
install -Dm644 dist/.icon-set/icon_512x512.png %{buildroot}%{_iconsdir}/hicolor/512x512/heroic.png
install -Dm644 dist/.icon-set/icon_1024.png %{buildroot}%{_iconsdir}/hicolor/1024x1024/heroic.png
install -Dm644 %{SOURCE1} %{buildroot}%{_datadir}/applications/heroic.desktop

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/heroic.desktop

%files
%doc     README.md
%doc     CODE_OF_CONDUCT.md
%license COPYING
%license LICENSE
%license LICENSE.electron.txt
%license LICENSES.chromium.html
%dir %{_datadir}/heroic
%{_datadir}/heroic/*
%{_datadir}/pixmaps/heroic.png
%{_bindir}/heroic
%{_bindir}/heroic-games-launcher
%{_datadir}/applications/heroic.desktop
%{_iconsdir}/hicolor/16x16/heroic.png
%{_iconsdir}/hicolor/32x32/heroic.png
%{_iconsdir}/hicolor/48x48/heroic.png
%{_iconsdir}/hicolor/64x64/heroic.png
%{_iconsdir}/hicolor/128x128/heroic.png
%{_iconsdir}/hicolor/256x256/heroic.png
%{_iconsdir}/hicolor/512x512/heroic.png
%{_iconsdir}/hicolor/1024x1024/heroic.png

%changelog
* Sun Mar 02 2025 Gilver E. <rockgrub@disroot.org>
- Update to 2.16.0
- Fix incorrect RPM dependencies
* Thu Jan 30 2025 Gilver E. <rockgrub@disroot.org>
- Initial package
