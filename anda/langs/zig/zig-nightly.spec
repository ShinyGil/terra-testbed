%global build_cflags %{__build_flags_lang_c} %{?_distro_extra_cflags} -std=gnu18
%global build_cxxflags %{__build_flags_lang_cxx} %{?_distro_extra_cxxflags} -std=gnu++20
%global         zig_arches x86_64 aarch64 riscv64 %{mips64}
# Signing key from https://ziglang.org/download/
%global         public_key RWSGOq2NVecA2UPNdBUZykf1CCb147pkmdtYxgb3Ti+JO/wCYvhbAb/U
%global         llvm_version 19.0.0
%bcond bootstrap 1
%bcond docs     %{without bootstrap}
%bcond macro    %{without bootstrap}
%bcond test     1
%define prerelease dev.2851+b074fb7dd

Name:           zig-nightly
Version:        0.14.0
%if "%{prerelease}" == "1"
Release:        1%{?dist}
%else
Release:        0^%{prerelease}%{?dist}
%endif
Summary:        Programming language for maintaining robust, optimal, and reusable software
License:        MIT and NCSA and LGPLv2+ and LGPLv2+ with exceptions and GPLv2+ and GPLv2+ with exceptions and BSD and Inner-Net and ISC and Public Domain and GFDL and ZPLv2.1
URL:            https://ziglang.org
%if "%{prerelease}" == "1"
Source0:        %{url}/builds/zig-%{version}.tar.xz
Source1:        %{url}/builds/zig-%{version}.tar.xz.minisig
%else
Source0:        %{url}/builds/zig-%{version}-%{prerelease}.tar.xz
Source1:        %{url}/builds/zig-%{version}-%{prerelease}.tar.xz.minisig
%endif
Source2:        macros.zig
### Support clean build of stage3 with temporary bootstrapped package | Modified to fix Rawhide/GCC 15 builds
Patch0:         0000-Fedora-bootstrap-and-extra-build-flags-support.patch
### There's no global option for build-id so enable it by default instead of patching every project's build.zig
Patch1:         0001-Enable-build-id-by-default.patch
### Zig fetch will recurse onto the cache directory, prevent that from happening.
# https://github.com/ziglang/zig/pull/19951
#Patch2:         0002-fetch-prevent-global-cache-from-being-copied.patch
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  llvm-devel
BuildRequires:  clang-devel
BuildRequires:  lld-devel
BuildRequires:  zlib-devel
BuildRequires:  libxml2-devel
BuildRequires:  help2man
BuildRequires:  minisign
%if %{without bootstrap}
BuildRequires:  %{name} = %{version}
%endif
%if %{with test}
BuildRequires:  elfutils-libelf-devel
BuildRequires:  libstdc++-static
%endif
Requires:       %{name}-libs = %{version}
Conflicts:	    zig
### These packages are bundled as source
# Apache-2.0 WITH LLVM-exception OR NCSA OR MIT
Provides:      bundled(compiler-rt) = %{llvm_version}
# LGPLv2+, LGPLv2+ with exceptions, GPLv2+, GPLv2+ with exceptions, BSD, Inner-Net, ISC, Public Domain and GFDL
Provides:      bundled(glibc) = 2.34
# Apache-2.0 WITH LLVM-exception OR MIT OR NCSA
Provides:      bundled(libcxx) = %{llvm_version}
# Apache-2.0 WITH LLVM-exception OR MIT OR NCSA
Provides:      bundled(libcxxabi) = %{llvm_version}
# NCSA
Provides:      bundled(libunwind) = %{llvm_version}
# BSD, LGPG, ZPL
Provides:      bundled(mingw) = 10.0.0
# MIT
Provides:      bundled(musl) = 1.2.4
# Apache-2.0 WITH LLVM-exception AND Apache-2.0 AND MIT AND BSD-2-Clause
Provides:      bundled(wasi-libc) = 3189cd1ceec8771e8f27faab58ad05d4d6c369ef
Provides:      zig-dev = %{version}-%{release}
ExclusiveArch: %{zig_arches}
Packager:      ShinyGil <rockgrub@protonmail.com>

%description
Zig is an open-source programming language designed for robustness, optimality,
and clarity. This package provides dev (nightly) builds of Zig.

### The Zig stdlib only contains uncompiled code
%package libs
Summary:        Zig Standard Library
BuildArch:      noarch
Conflicts:	    zig-libs

%description libs
zig Standard Library

%if %{with docs}
%package doc
Summary:        Documentation for Zig
BuildArch:      noarch
Requires:       %{name} = %{version}

%description doc
Documentation for Zig. For more information, visit %{url}
%endif

%if %{with macro}
%package        rpm-macros
Summary:        Common RPM macros for zig
Requires:       rpm
BuildArch:      noarch

%description    rpm-macros
This package contains common RPM macros for zig.
%endif

%prep
/usr/bin/minisign -V -m %{SOURCE0} -x %{SOURCE1} -P %{public_key}

%if "%{prerelease}" == "1"
%autosetup -p1 -n zig-%{version}
%else
%autosetup -p1 -n zig-%{version}-%{prerelease}
%endif

%if %{without bootstrap}
### Ensure that the pre-build stage1 binary is not used
rm -f stage1/zig1.wasm
%endif

%build
# C_FLAGS: wasm2c output generates a lot of noise with -Wunused.
# EXTRA_BUILD_ARGS: apply --build-id=sha1 even if running unpatched stage2 compiler.
mkdir -p %{buildroot}%{_bindir}
%cmake \
    -DCMAKE_BUILD_TYPE:STRING=RelWithDebInfo \
    -DCMAKE_C_FLAGS_RELWITHDEBINFO:STRING="-DNDEBUG -Wno-unused" \
    -DCMAKE_CXX_FLAGS_RELWITHDEBINFO:STRING="-DNDEBUG -Wno-unused" \
    -DZIG_EXTRA_BUILD_ARGS:STRING="--verbose" \
    -DZIG_SHARED_LLVM:BOOL=true \
    -DZIG_TARGET_MCPU:STRING=baseline \
    -DZIG_TARGET_TRIPLE:STRING=native \
    -DZIG_VERSION:STRING="%{version}" \
    %{!?with_bootstrap:-DZIG_EXECUTABLE:STRING="/usr/bin/zig"}
### Build only stage3 and dependencies. Skips stage1/2 if using /usr/bin/zig
%cmake_build --target stage3

### Zig has no official manpage
# https://github.com/ziglang/zig/issues/715
help2man --no-discard-stderr --no-info "%{__cmake_builddir}/stage3/bin/zig" --version-option=version --output=zig.1

%if %{with docs}
"%{__cmake_builddir}/stage3/bin/zig" build docs --verbose -Dversion-string="%{version}"
%endif

%install
# Ignore standard RPATH for now
export QA_RPATHS=$(( 0x0001 ))

%cmake_install

install -D -pv -m 0644 -t %{buildroot}%{_mandir}/man1/ zig.1

%if %{with macro}
install -D -pv -m 0644 %{SOURCE2} %{buildroot}%{_rpmmacrodir}/macros.zig
%endif

%if %{with test}
%check
# Run reduced set of tests, based on the Zig CI
"%{__cmake_builddir}/stage3/bin/zig" test test/behavior.zig -Itest
%endif

%files
%license LICENSE
%{_bindir}/zig
%{_mandir}/man1/zig.1.*

%files libs
%{_prefix}/lib/zig

%if %{with docs}
%files doc
%doc README.md
%doc zig-out/doc/langref.html
%doc zig-out/doc/std
%endif

%if %{with macro}
%files rpm-macros
%{_rpmmacrodir}/macros.zig
%endif

%changelog
* Wed Jan 22 2025 ShinyGil <rockgrub@protonmail.com>
- Initial package
