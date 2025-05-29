%global tinkworkergitpath github.com/tinkerbell/tink

%define pkidir %{_sysconfdir}/pki
%define catrustdir %{pkidir}/ca-trust

Summary:        In-memory Operating System Installation Environment for Executing Tinkerbell Workflows
Name:           tink-worker
Version:        0.10.0
Release:        15%{?dist}
Distribution:   Tiber Microvisor
Vendor:         Intel Corporation
License:        Apache-2.0
URL:            https://tinkerbell.org
Source0:        https://%{tinkworkergitpath}/archive/v%{version}/tink-%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:        tink-worker.service
Source2:        tink-worker-%{version}-vendor.tar.gz
Source3:        Intel.crt
Patch0:         tink-worker.patch

%{?systemd_requires}

BuildRequires:  golang >= 1.23
BuildRequires:  systemd-rpm-macros


%description
The tink-worker will parse the /proc/cmdline in order to retrieve the specific configuration to start for the current/correct machine.
It will begin to execute the workflow/actions associated with that machine.


%prep
%setup -q -n tink-%{version}
%patch 0 -p1

%build
tar -xzvf %{SOURCE2} -C .
CGO_ENABLED=0 go build -buildmode=pie -mod=vendor -trimpath -ldflags '-extldflags "-static"' -o tink-worker ./cmd/tink-worker

%install
# command
install -D -p -m 0755 -t %{buildroot}%{_bindir} ./tink-worker

mkdir -p -m 755 %{buildroot}%{catrustdir}/source/anchors
cp %{SOURCE3} %{buildroot}%{catrustdir}/source/anchors/Intel.crt

# systemd units
mkdir -p %{buildroot}%{_unitdir}
cp %{SOURCE1} %{buildroot}%{_unitdir}

%post
%systemd_post tink-worker.service

%files
%{_bindir}/tink-worker
%{_unitdir}/tink-worker.service
%attr(0644, -, -) %{catrustdir}/source/anchors/Intel.crt

%changelog
* Wed Apr 9 2025 Andy <andy.peng@intel.com> - 0.10.0-1
- Initial package