%global debug_package %{nil}
%global modulename v4l2loopback
%global _description %{expand:
This module allows you to create \"virtual video devices.\" Normal \(v4l2\) applications will read these devices as if they were ordinary video devices, but the video will not be read from e.g. a capture card but instead it is generated by another application.}

Name:           dkms-%{modulename}
Version:        0.14.0
Release:        1%?dist
Summary:        Utils for V4L2 loopback devices
License:        GPL-2.0-or-later
URL:            https://github.com/v4l2loopback/v4l2loopback
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
Source1:        no-weak-modules.conf
BuildRequires:  systemd-rpm-macros
Requires:       %{modulename} = %{?epoch:%{epoch}:}%{version}
Requires:       dkms
Conflicts:      akmod-%{modulename}
BuildArch:      noarch
Packager:       Gilver E. <rockgrub@disroot.org>

%description %_description

%prep
%autosetup -p1 -n %{modulename}-%{version}

%build

%install
mkdir -p %{buildroot}%{_usrsrc}/%{modulename}-%{version}
cp -fr v4l2loopback.h v4l2loopback.c v4l2loopback_formats.h dkms.conf Kbuild Makefile %{buildroot}%{_usrsrc}/%{modulename}-%{version}/

%if 0%{?fedora}
# Do not enable weak modules support in Fedora (no kABI):
install -Dpm644 %{SOURCE1} %{buildroot}%{_sysconfdir}/dkms/%{modulename}.conf
%endif

%post
dkms add -m %{modulename} -v %{version} -q --rpm_safe_upgrade || :
# Rebuild and make available for the currently running kernel:
dkms build -m %{modulename} -v %{version} -q || :
dkms install -m %{modulename} -v %{version} -q --force || :

%preun
# Remove all versions from DKMS registry:
dkms remove -m %{modulename} -v %{version} -q --all --rpm_safe_upgrade || :

%files
%{_usrsrc}/%{modulename}-%{version}
%if 0%{?fedora}
%{_sysconfdir}/dkms/%{modulename}.conf
%endif

%changelog
* Fri Mar 07 2025 Gilver E. <rockgrub@disroot.org>
- Initial package
