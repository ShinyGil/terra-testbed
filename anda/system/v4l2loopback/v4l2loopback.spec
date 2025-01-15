%global buildforkernels akmod
%global debug_package %{nil}

%global commit 2c9b67072b15d903fecde67c7f269abeafee4c25
%global commitdate 20230503
%global shortcommit %(c=%{commit}; echo ${c:0:7})


%global prjname v4l2loopback

Name:           %{prjname}
Summary:        Utils for V4L2 loopback devices
Version:        0.13.2
Release:        1%{?dist}
License:        GPLv2+
URL:            https://github.com/umlaeute/v4l2loopback
Source0:        %{url}/archive/v%{version}/%{prjname}-%{version}.tar.gz

Source1:        modprobe-d-98-v4l2loopback.conf
Source2:        modules-load-d-v4l2loopback.conf
BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  help2man
BuildRequires:  systemd-rpm-macros
BuildRequires:  kmodtool
BuildRequires:  systemd-rpm-macros
Requires:       kmod-v4l2loopback = %{version}-%{release}
# Required for  akmod-v4l2loopback
Requires:       help2man
### For compatibility with older names
Provides:       %{name}-utils = %{version}-%{release}
Obsoletes:      %{name}-utils < 0.12.5-2

%{expand:%(kmodtool --target %{_target_cpu} --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null) }

%description
Allows creation of virtual video devices. Normal (v4l2) applications will read these devices as if they were ordinary video devices.

%package kmod
Summary:  Kernel module (kmod) for %{name}
Requires: kernel-devel

%description kmod
This module allows you to create "virtual video devices". Normal (v4l2) applications will read these devices as if they were ordinary video devices, but the video will not be read from e.g. a capture card but instead it is generated by another application.



%prep
%{?kmodtool_check}
kmodtool --target %{_target_cpu} --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null

%autosetup -p1 -n %{name}-%{version}

# for kernel_version  in %{?kernel_versions} ; do
#   cp -av ./* _kmod_build_${kernel_version%%___*}
# done

%build

for kernel_version  in %{?kernel_versions} ; do
  make V=1 %{?_smp_mflags} M=${PWD}/_kmod_build_${kernel_version%%___*} VERSION=v%{version} v4l2loopback
done

%{set_build_flags}
%make_build utils

%install
for kernel_version in %{?kernel_versions}; do
 mkdir -p %{buildroot}%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/
 install -D -m 755 v4l2loopback.ko %{buildroot}%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/
 chmod a+x %{buildroot}%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/*.ko
done

%{set_build_flags}
%make_build utils

%{?akmod_install}
make V=1 %{?_smp_mflags} install-utils DESTDIR=%{buildroot} PREFIX=%{_prefix}
make V=1 %{?_smp_mflags} install-man DESTDIR=%{buildroot} PREFIX=%{_prefix}
install -D -m 0644 %{SOURCE1} %{buildroot}%{_modprobedir}/98-v4l2loopback.conf
install -D -m 0644 %{SOURCE2} %{buildroot}%{_modulesloaddir}/v4l2loopback.conf



%files
%doc README.md AUTHORS NEWS
%license COPYING
%attr(0755,root,root) %{_bindir}/v4l2loopback-ctl
%attr(0644,root,root) %{_mandir}/man1/v4l2loopback-ctl.1*
%{_modprobedir}/98-v4l2loopback.conf
%{_modulesloaddir}/v4l2loopback.conf

%changelog
%autochangelog
