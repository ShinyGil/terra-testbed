# The reason why this package is a separate from the main one despite using the same sources
# is because akmods use the srpm to build the kmod package, and if the kmod package is included
# in the main package, akmods will reinstall the userspace package every time the kernel is updated.

# I made the mistake of combining the specs when I ported this from RPMFusion, but to be fair
# they barely document anything.

%global buildforkernels akmod
%global debug_package %{nil}

%global commit 2c9b67072b15d903fecde67c7f269abeafee4c25
%global commitdate 20230503
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global modulename v4l2loopback
Name:           %{modulename}-kmod
Summary:        Kernel module (kmod) for V4L2 loopback devices
Version:        0.14.0
Release:        2%?dist
License:        GPLv2+
URL:            https://github.com/umlaeute/v4l2loopback
Source0:        %{url}/archive/v%{version}/%{modulename}-%{version}.tar.gz
Source1:        modprobe-d-98-v4l2loopback.conf
Source2:        modules-load-d-v4l2loopback.conf
Packager:       Cappy Ishihara <cappy@fyralabs.com>

BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  help2man
BuildRequires:  systemd-rpm-macros
BuildRequires:  kmodtool
Requires:       kernel-devel

%{expand:%(kmodtool --target %{_target_cpu} --kmodname %{modulename} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null) }

%description
This module allows you to create "virtual video devices". Normal (v4l2) applications will read these devices as if they were ordinary video devices, but the video will not be read from e.g. a capture card but instead it is generated by another application.


%prep
%{?kmodtool_check}
kmodtool --target %{_target_cpu} --kmodname %{modulename} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null

%autosetup -p1 -n %{modulename}-%{version}


%build

for kernel_version  in %{?kernel_versions} ; do
  make V=1 %{?_smp_mflags} M=${PWD}/_kmod_build_${kernel_version%%___*} VERSION=v%{version} v4l2loopback
done


%install
for kernel_version in %{?kernel_versions}; do
 mkdir -p %{buildroot}%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/
 install -D -m 755 v4l2loopback.ko %{buildroot}%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/
 chmod a+x %{buildroot}%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/*.ko
done

%{?akmod_install}

install -D -m 0644 %{SOURCE1} %{buildroot}%{_modprobedir}/98-v4l2loopback.conf
install -D -m 0644 %{SOURCE2} %{buildroot}%{_modulesloaddir}/v4l2loopback.conf

%files
%doc README.md AUTHORS NEWS
%license COPYING
%{_modprobedir}/98-v4l2loopback.conf
%{_modulesloaddir}/v4l2loopback.conf

%changelog
%autochangelog
