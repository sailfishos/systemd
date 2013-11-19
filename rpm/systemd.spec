Name:           systemd
URL:            http://www.freedesktop.org/wiki/Software/systemd
Version:        208
Release:        1
License:        LGPLv2+ and MIT and GPLv2+
Group:          System/System Control
Summary:        A System and Service Manager
BuildRequires:  libcap-devel
BuildRequires:  pam-devel
BuildRequires:  pkgconfig(dbus-1) >= 1.3.2
BuildRequires:  pkgconfig(dbus-glib-1)
BuildRequires:  libxslt
BuildRequires:  libacl-devel
BuildRequires:  glib2-devel
BuildRequires:  libgcrypt-devel
BuildRequires:  pkgconfig(usbutils) >= 0.82
BuildRequires:  pkgconfig(blkid) >= 2.20
BuildRequires:  intltool >= 0.40.0
BuildRequires:  gperf
BuildRequires:  xz-devel
BuildRequires:  kmod-devel >= 15
BuildRequires:  fdupes
Requires(post): /sbin/ldconfig
Requires(postun): /sbin/ldconfig
Requires:       dbus
Requires:       filesystem >= 3
Requires:       systemd-config
# fsck with -l option was introduced in 2.21.2 packaging
Requires:       util-linux >= 2.21.2
Source0:        http://www.freedesktop.org/software/systemd/%{name}-%{version}.tar.xz
Source1:        systemd-stop-user-sessions.service
Source2:        tests.xml
Source3:        systemctl-user
Patch0:         systemd-208-video.patch
Patch1:         systemd-208-pkgconfigdir.patch
Patch2:         systemd-187-remove-display-manager.service.patch
Patch3:         systemd-187-make-readahead-depend-on-sysinit.patch
Patch4:         systemd-208-install-test-binaries.patch
Provides:       udev = %{version}
Obsoletes:      udev < 184 
Provides:       systemd-sysv = %{version}
Obsoletes:      systemd-sysv < %{version}
Provides:       systemd-sysv-docs = %{version}
Obsoletes:      systemd-sysv-docs < %{version}

Provides:       systemd-console-ttyMFD2 = %{version}
Obsoletes:      systemd-console-ttyMFD2 <= 187
Provides:       systemd-console-ttyS0 = %{version}
Obsoletes:      systemd-console-ttyS0 <= 187
Provides:       systemd-console-ttyS1 = %{version}
Obsoletes:      systemd-console-ttyS1 <= 187
Provides:       systemd-console-tty01 = %{version}
Obsoletes:      systemd-console-tty01 <= 187
Provides:       systemd-console-ttyO2 = %{version}
Obsoletes:      systemd-console-ttyO2 <= 187
Provides:       systemd-console-ttyAMA0 = %{version}
Obsoletes:      systemd-console-ttyAMA0 <= 187

%description
systemd is a system and service manager for Linux, compatible with
SysV and LSB init scripts. systemd provides aggressive parallelization
capabilities, uses socket and D-Bus activation for starting services,
offers on-demand starting of daemons, keeps track of processes using
Linux cgroups, supports snapshotting and restoring of the system
state, maintains mount and automount points and implements an
elaborate transactional dependency-based service control logic. It can
work as a drop-in replacement for sysvinit.

%package config-mer
Summary:    Default configuration for systemd
Group:      System/System Control
Requires:   %{name} = %{version}-%{release}
Provides:   systemd-config

%description config-mer
This package provides default configuration for systemd

%package analyze
Summary:    Analyze systemd startup timing
Group:      Development/Tools
Requires:   dbus-python
Requires:   python-cairo
Requires:   %{name} = %{version}-%{release}
Provides:   %{name}-tools = %{version}
Obsoletes:  %{name}-tools <= 187

%description analyze
This package installs the systemd-analyze tool, which allows one to
inspect and graph service startup timing in table or graph format.

%package libs
Summary:        systemd libraries
License:        LGPLv2+ and MIT
Provides:       libudev = %{version}
Obsoletes:      libudev < %{version}
Obsoletes:      systemd <= 187
Conflicts:      systemd <= 187

%description libs
Libraries for systemd and udev, as well as the systemd PAM module.

%package devel
Group:          System Environment/Base
Summary:        Development headers for systemd
License:        LGPLv2+ and MIT
Requires:       %{name} = %{version}-%{release}
Provides:       libudev-devel = %{version}
Obsoletes:      libudev-devel < %{version}

%description devel
Development headers and auxiliary files for developing applications for systemd.

%package docs
Summary:   System and session manager man pages
Group:     Development/Libraries
Requires:  %{name} = %{version}-%{release}

%description docs
This package includes the man pages for systemd.

%package tests
Summary:   Systemd tests
Group:     System/System Control
Requires:  %{name} = %{version}-%{release}
Requires:  blts-tools

%description tests
This package includes tests for systemd.

%package -n libgudev1
Summary:        Libraries for adding libudev support to applications that use glib
Group:          Development/Libraries
Conflicts:      filesystem < 3
Requires:       %{name} = %{version}-%{release}
License:        LGPLv2+

%description -n libgudev1
This package contains the libraries that make it easier to use libudev
functionality from applications that use glib.

%package -n libgudev1-devel
Summary:        Header files for adding libudev support to applications that use glib
Group:          Development/Libraries
Requires:       libgudev1 = %{version}-%{release}
License:        LGPLv2+

%description -n libgudev1-devel
This package contains the header and pkg-config files for developing
glib-based applications using libudev functionality.

%prep
%setup -q -n %{name}-%{version}/systemd
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1

%build
./autogen.sh
%configure \
  --with-rootprefix= \
  --disable-coredump \
  --disable-static \
  --with-firmware-path=/lib/firmware/updates:/lib/firmware:/system/etc/firmware:/etc/firmware:/vendor/firmware:/firmware/image \
  --disable-manpages \
  --disable-python-devel \
  --enable-tests

make %{?_smp_mflags}

%install
%make_install

# Create SysV compatibility symlinks. systemctl/systemd are smart
# enough to detect in which way they are called.
mkdir -p %{buildroot}/{%{_sbindir},sbin}
ln -s ../lib/systemd/systemd %{buildroot}/sbin/init
ln -s ../../bin/systemctl %{buildroot}%{_sbindir}/reboot
ln -s ../../bin/systemctl %{buildroot}%{_sbindir}/halt
ln -s ../../bin/systemctl %{buildroot}%{_sbindir}/poweroff
ln -s ../../bin/systemctl %{buildroot}%{_sbindir}/shutdown
ln -s ../../bin/systemctl %{buildroot}%{_sbindir}/telinit
ln -s ../../bin/systemctl %{buildroot}%{_sbindir}/runlevel

ln -sf ../bin/udevadm %{buildroot}%{_sbindir}/udevadm

# Make sure these directories are properly owned
mkdir -p %{buildroot}/lib/systemd/system/basic.target.wants
mkdir -p %{buildroot}/lib/systemd/system/default.target.wants
mkdir -p %{buildroot}/lib/systemd/system/dbus.target.wants
mkdir -p %{buildroot}/lib/systemd/system/getty.target.wants
mkdir -p %{buildroot}/lib/systemd/system/syslog.target.wants

# enable readahead by default
ln -s ../systemd-readahead-collect.service %{buildroot}/lib/systemd/system/sysinit.target.wants/systemd-readahead-collect.service
ln -s ../systemd-readahead-replay.service %{buildroot}/lib/systemd/system/sysinit.target.wants/systemd-readahead-replay.service

# Require network to be enabled with multi-user.target
mkdir -p %{buildroot}/lib/systemd/system/multi-user.target.wants/
ln -s ../network.target %{buildroot}/lib/systemd/system/multi-user.target.wants/network.target

# Install Fedora default preset policy
mkdir -p %{buildroot}%{_prefix}/lib/systemd/system-preset/
mkdir -p %{buildroot}%{_prefix}/lib/systemd/user-preset/

# Make sure the shutdown/sleep drop-in dirs exist
mkdir -p %{buildroot}%{_prefix}/lib/systemd/system-shutdown/
mkdir -p %{buildroot}%{_prefix}/lib/systemd/system-sleep/

# Make sure the NTP units dir exists
mkdir -p %{buildroot}%{_prefix}/lib/systemd/ntp-units.d/

# Make sure directories in /var exist
mkdir -p %{buildroot}%{_localstatedir}/lib/systemd/coredump
mkdir -p %{buildroot}%{_localstatedir}/lib/systemd/catalog
mkdir -p %{buildroot}%{_localstatedir}/log/journal
touch %{buildroot}%{_localstatedir}/lib/systemd/catalog/database
touch %{buildroot}%{_sysconfdir}/udev/hwdb.bin
touch %{buildroot}%{_localstatedir}/lib/systemd/random-seed

mkdir -p %{buildroot}%{_sysconfdir}/sysctl.d
mkdir -p %{buildroot}%{_sysconfdir}/modules-load.d
mkdir -p %{buildroot}%{_sysconfdir}/binfmt.d

# Don't ship documentation in the wrong place
rm %{buildroot}/%{_docdir}/systemd/*

mkdir -p %{buildroot}/etc/systemd/system/basic.target.wants

# Fix shutdown hang problem with user-serssions
install -D -m 644 %{SOURCE1} %{buildroot}/lib/systemd/system/systemd-stop-user-sessions.service
mkdir -p %{buildroot}/lib/systemd/system/shutdown.target.wants
ln -s ../systemd-stop-user-sessions.service %{buildroot}/lib/systemd/system/shutdown.target.wants/systemd-stop-user-sessions.service

# Add systemctl-user helper script
install -D -m 755 %{SOURCE3} %{buildroot}/bin/systemctl-user

%fdupes  %{buildroot}/%{_datadir}/man/

# Install tests.xml
install -d -m 755 %{buildroot}/opt/tests/systemd-tests
install -m 644 %{SOURCE2} %{buildroot}/opt/tests/systemd-tests

mkdir -p %{buildroot}/lib/security/
mv %{buildroot}%{_libdir}/security/pam_systemd.so %{buildroot}/lib/security/pam_systemd.so

%pre
getent group cdrom >/dev/null 2>&1 || groupadd -r -g 11 cdrom >/dev/null 2>&1 || :
getent group tape >/dev/null 2>&1 || groupadd -r -g 33 tape >/dev/null 2>&1 || :
getent group dialout >/dev/null 2>&1 || groupadd -r -g 18 dialout >/dev/null 2>&1 || :
getent group floppy >/dev/null 2>&1 || groupadd -r -g 19 floppy >/dev/null 2>&1 || :
getent group systemd-journal >/dev/null 2>&1 || groupadd -r -g 190 systemd-journal 2>&1 || :

systemctl stop systemd-udevd-control.socket systemd-udevd-kernel.socket systemd-udevd.service >/dev/null 2>&1 || :

%post
systemd-machine-id-setup >/dev/null 2>&1 || :
/usr/lib/systemd/systemd-random-seed save >/dev/null 2>&1 || :
systemctl daemon-reexec >/dev/null 2>&1 || :
systemctl start systemd-udevd.service >/dev/null 2>&1 || :
udevadm hwdb --update >/dev/null 2>&1 || :
journalctl --update-catalog >/dev/null 2>&1 || :

%post libs -p /sbin/ldconfig
%postun libs -p /sbin/ldconfig

%post -n libgudev1 -p /sbin/ldconfig
%postun -n libgudev1 -p /sbin/ldconfig

%files
%defattr(-,root,root,-)
%dir %{_sysconfdir}/systemd
%dir %{_sysconfdir}/systemd/system
%exclude %{_sysconfdir}/systemd/system/getty.target.wants/getty@tty1.service
%dir %{_sysconfdir}/systemd/user
%dir %{_sysconfdir}/tmpfiles.d
%dir %{_sysconfdir}/sysctl.d
%dir %{_sysconfdir}/modules-load.d
%dir %{_sysconfdir}/binfmt.d
%dir %{_sysconfdir}/udev
%dir %{_sysconfdir}/udev/rules.d
%dir %{_prefix}/lib/systemd
%dir %{_prefix}/lib/systemd/catalog
%dir %{_prefix}/lib/tmpfiles.d
%dir %{_prefix}/lib/sysctl.d
%dir %{_prefix}/lib/modules-load.d
%dir %{_prefix}/lib/binfmt.d
%dir %{_datadir}/systemd
%dir %{_localstatedir}/log/journal
%dir %{_localstatedir}/lib/systemd
%dir %{_localstatedir}/lib/systemd/catalog
%dir %{_localstatedir}/lib/systemd/coredump
%ghost %{_localstatedir}/lib/systemd/random-seed
%ghost %{_localstatedir}/lib/systemd/catalog/database

%{_localstatedir}/log/README
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/org.freedesktop.systemd1.conf
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/org.freedesktop.hostname1.conf
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/org.freedesktop.login1.conf
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/org.freedesktop.locale1.conf
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/org.freedesktop.timedate1.conf
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/org.freedesktop.machine1.conf
%config(noreplace) %{_sysconfdir}/systemd/bootchart.conf
%config(noreplace) %{_sysconfdir}/pam.d/systemd-user
%ghost %{_sysconfdir}/udev/hwdb.bin
%{_libdir}/rpm/macros.d/macros.systemd
%{_sysconfdir}/init.d/README
%config(noreplace) %{_sysconfdir}/xdg/systemd/user
%{_sysconfdir}/systemd/system/*
%{_libdir}/tmpfiles.d/*
%{_libdir}/sysctl.d/50-default.conf
%{_libdir}/systemd/user/*
%dir /lib/udev/

/lib/udev/*

/bin/systemctl
/bin/systemctl-user
/bin/systemd-notify
/bin/systemd-ask-password
/bin/systemd-tty-ask-password-agent
/bin/systemd-machine-id-setup
/bin/loginctl
/bin/journalctl
/bin/machinectl
/bin/systemd-tmpfiles
%{_bindir}/systemd-run
/bin/udevadm
%{_bindir}/kernel-install
%{_bindir}/systemd-nspawn
%{_bindir}/systemd-stdio-bridge
%{_bindir}/systemd-cat
%{_bindir}/systemd-cgls
%{_bindir}/systemd-cgtop
%{_bindir}/systemd-delta
%{_bindir}/systemd-detect-virt
/bin/systemd-inhibit
%{_bindir}/hostnamectl
%{_bindir}/localectl
%{_bindir}/timedatectl
%{_bindir}/bootctl
%{_sbindir}/udevadm
/%{_lib}/systemd
%{_datadir}/dbus-1/*/org.freedesktop.systemd1.*
%{_defaultdocdir}/systemd
%{_datadir}/dbus-1/system-services/org.freedesktop.hostname1.service
%{_datadir}/dbus-1/system-services/org.freedesktop.login1.service
%{_datadir}/dbus-1/system-services/org.freedesktop.locale1.service
%{_datadir}/dbus-1/system-services/org.freedesktop.timedate1.service
%{_datadir}/dbus-1/system-services/org.freedesktop.machine1.service
%{_datadir}/dbus-1/interfaces/org.freedesktop.hostname1.xml
%{_datadir}/dbus-1/interfaces/org.freedesktop.locale1.xml
%{_datadir}/dbus-1/interfaces/org.freedesktop.timedate1.xml
%{_datadir}/polkit-1/actions/org.freedesktop.systemd1.policy
%{_datadir}/polkit-1/actions/org.freedesktop.hostname1.policy
%{_datadir}/polkit-1/actions/org.freedesktop.login1.policy
%{_datadir}/polkit-1/actions/org.freedesktop.locale1.policy
%{_datadir}/polkit-1/actions/org.freedesktop.timedate1.policy
%{_datadir}/bash-completion/completions/hostnamectl
%{_datadir}/bash-completion/completions/journalctl
%{_datadir}/bash-completion/completions/localectl
%{_datadir}/bash-completion/completions/loginctl
%{_datadir}/bash-completion/completions/systemctl
%{_datadir}/bash-completion/completions/timedatectl
%{_datadir}/bash-completion/completions/udevadm
%{_datadir}/bash-completion/completions/systemd-analyze
%{_datadir}/bash-completion/completions/kernel-install
%{_datadir}/bash-completion/completions/systemd-run
%{_datadir}/zsh/site-functions/*

/usr/lib/systemd/catalog/systemd.catalog
/usr/lib/kernel/install.d/50-depmod.install
/usr/lib/kernel/install.d/90-loaderentry.install

%{_sbindir}/halt
/sbin/init
%{_sbindir}/poweroff
%{_sbindir}/reboot
%{_sbindir}/runlevel
%{_sbindir}/shutdown
%{_sbindir}/telinit

%{_datadir}/systemd/kbd-model-map
# Just make sure we don't package these by default
%exclude /lib/systemd/system/default.target
%exclude %{_libdir}/systemd/user/default.target
%exclude %{_sysconfdir}/systemd/system/multi-user.target.wants/remote-fs.target
%exclude /lib/systemd/system/user@.service

%files config-mer
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/systemd/journald.conf
%config(noreplace) %{_sysconfdir}/systemd/logind.conf
%config(noreplace) %{_sysconfdir}/systemd/system.conf
%config(noreplace) %{_sysconfdir}/systemd/user.conf
%config(noreplace) %{_sysconfdir}/udev/udev.conf
/lib/systemd/system/default.target
/lib/systemd/system/user@.service

%files docs
%defattr(-,root,root,-)
#%doc %{_mandir}/man?/*

%files tests
%defattr(-,root,root,-)
/opt/tests/systemd-tests/tests.xml
/opt/tests/systemd-tests/bin/test-*

%files analyze
%defattr(-,root,root,-)
%{_bindir}/systemd-analyze

%files libs
/lib/security/pam_systemd.so
%{_libdir}/libnss_myhostname.so.2
%{_libdir}/libsystemd-daemon.so.*
%{_libdir}/libsystemd-login.so.*
%{_libdir}/libsystemd-journal.so.*
%{_libdir}/libsystemd-id128.so.*
%{_libdir}/libudev.so.*

%files devel
%dir %{_includedir}/systemd
%{_libdir}/libsystemd-daemon.so
%{_libdir}/libsystemd-login.so
%{_libdir}/libsystemd-journal.so
%{_libdir}/libsystemd-id128.so
%{_libdir}/libudev.so
%{_includedir}/systemd/sd-daemon.h
%{_includedir}/systemd/sd-login.h
%{_includedir}/systemd/sd-journal.h
%{_includedir}/systemd/sd-id128.h
%{_includedir}/systemd/sd-messages.h
%{_includedir}/systemd/sd-shutdown.h
%{_includedir}/libudev.h
%{_libdir}/pkgconfig/libsystemd-daemon.pc
%{_libdir}/pkgconfig/libsystemd-login.pc
%{_libdir}/pkgconfig/libsystemd-journal.pc
%{_libdir}/pkgconfig/libsystemd-id128.pc
%{_libdir}/pkgconfig/libudev.pc
%{_libdir}/pkgconfig/systemd.pc
%{_libdir}/pkgconfig/udev.pc

%files -n libgudev1
%defattr(-,root,root,-)
%attr(0755,root,root) %{_libdir}/libgudev-1.0.so.*

%files -n libgudev1-devel
%defattr(-,root,root,-)
%attr(0755,root,root) %{_libdir}/libgudev-1.0.so
%dir %attr(0755,root,root) %{_includedir}/gudev-1.0
%dir %attr(0755,root,root) %{_includedir}/gudev-1.0/gudev
%attr(0644,root,root) %{_includedir}/gudev-1.0/gudev/*.h
%attr(0644,root,root) %{_libdir}/pkgconfig/gudev-1.0.pc

