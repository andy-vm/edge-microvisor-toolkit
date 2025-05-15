%global infraonboarding_gitpath github.com/open-edge-platform/infra-onboarding

%define pkidir %{_sysconfdir}/pki
%define catrustdir %{pkidir}/ca-trust

Summary:        Device Discovery Agent for Edge Node
Name:           device-discovery
Version:        1.17.2
Release:        1%{?dist}
Distribution:   Tiber Microvisor
Vendor:         Intel Corporation
License:        Apache-2.0
URL:            https://tinkerbell.org
Source0:        https://%{infraonboarding_gitpath}/archive/refs/tags/tinker-actions/%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:        device-discovery.service

%{?systemd_requires}

BuildRequires:  golang >= 1.23
BuildRequires:  systemd-rpm-macros

%global debug_package   %{nil}

%description
The Device Discovery Agent for Edge Node in order to retrieve the specific configuration to start for the current/correct machine.


%prep
%setup -q -n infra-onboarding-tinker-actions-%{version}

%build
cd hook-os/device_discovery
go mod vendor
CGO_ENABLED=0 go build -buildmode=pie -mod=vendor -trimpath -ldflags '-s -w -extldflags "-static"' -o device-discovery

%install
# command
install -d -m 0755 %{buildroot}%{_bindir}/device-discovery 
install -m 0755 device-discovery %{buildroot}%{_bindir}/device-discovery/device-discovery
install -m 0755 client-auth.sh %{buildroot}%{_bindir}/device-discovery/client-auth.sh

# systemd units
mkdir -p %{buildroot}%{_unitdir}
cp %{SOURCE1} %{buildroot}%{_unitdir}

%post
%systemd_post device-discovery.service
# The package is allowed to autostart:
#systemctl enable device-discovery.service >/dev/null 2>&1
#systemctl start device-discovery.service >/dev/null 2>&1

%files
%{_bindir}/device-discovery/*
%{_unitdir}/device-discovery.service

%changelog
* Fri May 16 2025 Andy <andy.peng@intel.com> - 1.17.2-1
- Initial package