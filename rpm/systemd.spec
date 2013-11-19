Name:           systemd
URL:            http://www.freedesktop.org/wiki/Software/systemd
Version:        187
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
BuildRequires:  hwdata
BuildRequires:  pkgconfig(usbutils) >= 0.82
BuildRequires:  pkgconfig(blkid) >= 2.20
BuildRequires:  intltool >= 0.40.0
BuildRequires:  gperf
BuildRequires:  xz-devel
BuildRequires:  kmod-devel >= 5
BuildRequires:  fdupes
Requires(post): /sbin/ldconfig
Requires(postun): /sbin/ldconfig
Requires:       dbus
Requires:       hwdata
Requires:       filesystem >= 3
Requires:       systemd-config
# fsck with -l option was introduced in 2.21.2 packaging
Requires:       util-linux >= 2.21.2
Source0:        http://www.freedesktop.org/software/systemd/%{name}-%{version}.tar.xz
Source1:        systemd-stop-user-sessions.service
Source2:        tests.xml
Source3:        systemctl-user
Patch0:         systemd-185-pkgconfigdir.patch
Patch1:	        systemd-187-reintroduce-support-for-deprecated-oom.patch
Patch2:		systemd-187-video.patch
Patch3:         systemd-187-make-readahead-depend-on-sysinit.patch
Patch4:         systemd-187-support-glob-EnvironmentFile.patch
Patch5:         systemd-187-install-test-bin.patch
Patch6:         systemd-187-remove-display-manager.service.patch
Patch7:		systemd-187-fix-ftbfs.patch
Provides:       udev = %{version}
Obsoletes:      udev < 184 

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

%package devel
Group:          System Environment/Base
Summary:        Development headers for systemd
License:        LGPLv2+ and MIT
Requires:       %{name} = %{version}-%{release}

%description devel
Development headers and auxiliary files for developing applications for systemd.

%package console-ttyS0
Summary:    Systemd console ttyS0
Group:      System/System Control
Requires:   %{name}

%description console-ttyS0
This package will setup a serial getty for ttyS0 is desired.


%package console-ttyS1
Summary:    Systemd console ttyS1
Group:      System/System Control
Requires:   %{name}

%description console-ttyS1
This package will setup a serial getty for ttyS1 is desired.


%package console-tty01
Summary:    Systemd console tty01
Group:      System/System Control
Requires:   %{name}

%description console-tty01
This package will setup a serial getty for tty01 is desired.


%package console-ttyO2
Summary:    Systemd console ttyO2
Group:      System/System Control
Requires:   %{name}

%description console-ttyO2
This package will setup a serial getty for ttyO2 is desired.

%package console-ttyMFD2
Summary:    Systemd console ttyMFD2
Group:      System/System Control
Requires:   %{name}

%description console-ttyMFD2
This package will setup a serial getty for ttyMFD2 is desired.

%package console-ttyAMA0
Summary:    Systemd console ttyAMA0
Group:      System/System Control
Requires:   %{name}

%description console-ttyAMA0
This package will setup a serial getty for ttyAMA0 is desired.

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

%package sysv-docs
Summary:   System and session manager man pages - SysV links
Group:     Development/Libraries
Requires:  %{name} = %{version}-%{release}

%description sysv-docs
This package provides the manual pages needed for systemd
to replace sysvinit.

%package sysv
Summary:   System and session manager - SysV links
Group:     System/Startup Services
Requires:  %{name} = %{version}-%{release}

%package -n libgudev1
Summary:        Libraries for adding libudev support to applications that use glib
Group:          Development/Libraries
Conflicts:      filesystem < 3
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

%package -n libudev
Summary: Library for accessing udev functionality
Group: Development/Libraries

%description -n libudev
This package contains a shared library for accesing libudev functionality.

%package -n libudev-devel
Summary: Headers for libudev
Group: Development/Libraries
Requires: libudev = %{version}-%{release}

%description -n libudev-devel
This package contains libraries and include files, 
which needed to link against libudev.


%description sysv
Systemd is a replacement for sysvinit.  It is dependency-based and
able to read the LSB init script headers in addition to parsing rcN.d
links as hints.

It also provides process supervision using cgroups and the ability to
not only depend on other init script being started, but also
availability of a given mount point or dbus service.

This package provides the links needed for systemd
to replace sysvinit.

%prep
%setup -q -n %{name}-%{version}
%patch0 -p1 -b .pkgconfig
%patch1 -p1 -R 
%patch2 -p1
%patch3 -p1 
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1

%build
autoreconf 
%configure \
  --with-rootprefix= \
  --with-rootlibdir=/%{_lib} \
  --with-distro=other \
  --with-pci-ids-path=/usr/share/hwdata/pci.ids \
  --disable-coredump \
  --disable-static \
  --with-firmware-path=/lib/firmware/updates:/lib/firmware:/system/etc/firmware:/etc/firmware:/vendor/firmware:/firmware/image
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

#console-ttyMFD2
ln -s ../serial-getty@.service %{buildroot}/lib/systemd/system/getty.target.wants/serial-getty@ttyMFD2.service

#console-ttyS0
ln -s ../serial-getty@.service %{buildroot}/lib/systemd/system/getty.target.wants/serial-getty@ttyS0.service

#console-ttyS1
ln -s ../serial-getty@.service %{buildroot}/lib/systemd/system/getty.target.wants/serial-getty@ttyS1.service

#console-tty01
ln -s ../serial-getty@.service %{buildroot}/lib/systemd/system/getty.target.wants/serial-getty@tty01.service

#console-ttyO2
ln -s ../serial-getty@.service %{buildroot}/lib/systemd/system/getty.target.wants/serial-getty@ttyO2.service

#console-ttyAMA0
ln -s ../serial-getty@.service %{buildroot}/lib/systemd/system/getty.target.wants/serial-getty@ttyAMA0.service

# Add systemctl-user helper script
install -D -m 755 %{SOURCE3} %{buildroot}/bin/systemctl-user

%fdupes  %{buildroot}/%{_datadir}/man/

# Install tests.xml
install -d -m 755 %{buildroot}/opt/tests/systemd-tests
install -m 644 %{SOURCE2} %{buildroot}/opt/tests/systemd-tests

%pre
getent group cdrom >/dev/null || /usr/sbin/groupadd -g 11 cdrom || :
getent group tape >/dev/null || /usr/sbin/groupadd -g 33 tape || :
getent group dialout >/dev/null || /usr/sbin/groupadd -g 18 dialout || :
getent group floppy >/dev/null || /usr/sbin/groupadd -g 19 floppy || :
systemctl stop systemd-udev.service systemd-udev-control.socket systemd-udev-kernel.socket >/dev/null 2>&1 || :

%post
/sbin/ldconfig
/bin/systemd-machine-id-setup > /dev/null 2>&1 || :
/bin/systemctl daemon-reexec > /dev/null 2>&1 || :

%postun -p /sbin/ldconfig

%post -n libudev -p /sbin/ldconfig
%postun -n libudev -p /sbin/ldconfig

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
%dir %{_sysconfdir}/bash_completion.d
%dir %{_sysconfdir}/udev
%dir %{_sysconfdir}/udev/rules.d
%dir %{_prefix}/lib/systemd
%dir %{_prefix}/lib/tmpfiles.d
%dir %{_prefix}/lib/sysctl.d
%dir %{_datadir}/systemd
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/org.freedesktop.systemd1.conf
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/org.freedesktop.hostname1.conf
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/org.freedesktop.login1.conf
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/org.freedesktop.locale1.conf
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/org.freedesktop.timedate1.conf
%config(noreplace) %{_sysconfdir}/xdg/systemd/user
%config(noreplace) %{_sysconfdir}/bash_completion.d/systemd-bash-completion.sh
%{_sysconfdir}/systemd/system/*
%{_sysconfdir}/rpm/macros.systemd
%{_libdir}/tmpfiles.d/*
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
/bin/systemd-tmpfiles
%{_bindir}/systemd-nspawn
%{_bindir}/systemd-stdio-bridge
%{_bindir}/systemd-cat
%{_bindir}/systemd-cgls
%{_bindir}/systemd-cgtop
%{_bindir}/systemd-delta
%{_bindir}/systemd-detect-virt
/bin/systemd-inhibit
%{_bindir}/udevadm
%{_sbindir}/udevadm
/%{_lib}/systemd
/%{_lib}/security/pam_systemd.so
/%{_lib}/libsystemd-daemon.so.*
/%{_lib}/libsystemd-login.so.*
/%{_lib}/libsystemd-journal.so.*
/%{_lib}/libsystemd-id128.so.*
%{_datadir}/dbus-1/*/org.freedesktop.systemd1.*
%{_defaultdocdir}/systemd
%{_datadir}/dbus-1/system-services/org.freedesktop.hostname1.service
%{_datadir}/dbus-1/system-services/org.freedesktop.login1.service
%{_datadir}/dbus-1/system-services/org.freedesktop.locale1.service
%{_datadir}/dbus-1/system-services/org.freedesktop.timedate1.service
%{_datadir}/dbus-1/interfaces/org.freedesktop.hostname1.xml
%{_datadir}/dbus-1/interfaces/org.freedesktop.locale1.xml
%{_datadir}/dbus-1/interfaces/org.freedesktop.timedate1.xml
%{_datadir}/polkit-1/actions/org.freedesktop.systemd1.policy
%{_datadir}/polkit-1/actions/org.freedesktop.login1.policy
%{_datadir}/polkit-1/actions/org.freedesktop.locale1.policy
%{_datadir}/polkit-1/actions/org.freedesktop.timedate1.policy
%{_datadir}/polkit-1/actions/org.freedesktop.hostname1.policy
%{_datadir}/systemd/kbd-model-map
# Just make sure we don't package these by default
%exclude /lib/systemd/system/getty.target.wants/serial-getty@*.service
%exclude /lib/systemd/system/default.target
%exclude %{_libdir}/systemd/user/default.target
%exclude %{_sysconfdir}/systemd/system/multi-user.target.wants/remote-fs.target

%files config-mer
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/systemd/journald.conf
%config(noreplace) %{_sysconfdir}/systemd/logind.conf
%config(noreplace) %{_sysconfdir}/systemd/system.conf
%config(noreplace) %{_sysconfdir}/systemd/user.conf
%config(noreplace) %{_sysconfdir}/udev/udev.conf
/lib/systemd/system/default.target

%files docs
%defattr(-,root,root,-)
%doc %{_mandir}/man?/*

%files tests
%defattr(-,root,root,-)
/opt/tests/systemd-tests/tests.xml
/opt/tests/systemd-tests/bin/*

%files console-ttyMFD2
%defattr(-,root,root,-)
/lib/systemd/system/getty.target.wants/serial-getty@ttyMFD2.service

%files console-ttyS0
%defattr(-,root,root,-)
/lib/systemd/system/getty.target.wants/serial-getty@ttyS0.service

%files console-ttyS1
%defattr(-,root,root,-)
/lib/systemd/system/getty.target.wants/serial-getty@ttyS1.service

%files console-tty01
%defattr(-,root,root,-)
/lib/systemd/system/getty.target.wants/serial-getty@tty01.service

%files console-ttyO2
%defattr(-,root,root,-)
/lib/systemd/system/getty.target.wants/serial-getty@ttyO2.service

%files console-ttyAMA0
%defattr(-,root,root,-)
/lib/systemd/system/getty.target.wants/serial-getty@ttyAMA0.service

%files analyze
%defattr(-,root,root,-)
%{_bindir}/systemd-analyze

%files devel
%defattr(-,root,root,-)
%{_includedir}/systemd/*.h
%{_libdir}/libsystemd-daemon.so
%{_libdir}/libsystemd-login.so
%{_libdir}/libsystemd-journal.so
%{_libdir}/libsystemd-id128.so
%{_libdir}/pkgconfig/libsystemd-*.pc
%{_libdir}/pkgconfig/systemd.pc

%files sysv
%defattr(-,root,root,-)
%{_sbindir}/halt
/sbin/init
%{_sbindir}/poweroff
%{_sbindir}/reboot
%{_sbindir}/runlevel
%{_sbindir}/shutdown
%{_sbindir}/telinit

%files sysv-docs
%defattr(-,root,root,-)
%doc %{_mandir}/man?/*

%files -n libudev
%defattr(0644, root, root, 0755)
%attr(0755,root,root) /%{_lib}/libudev.so.*

%files -n libudev-devel
%defattr(0644, root, root, 0755)
%attr(0644,root,root) %{_mandir}/man8/udev*.8*
%attr(0644,root,root) %{_mandir}/man7/udev*.7*
%{_includedir}/libudev.h
%{_libdir}/libudev.so
%{_libdir}/pkgconfig/libudev.pc
%{_libdir}/pkgconfig/udev.pc

%files -n libgudev1
%defattr(-,root,root,-)
%attr(0755,root,root) /%{_lib}/libgudev-1.0.so.*

%files -n libgudev1-devel
%defattr(-,root,root,-)
%attr(0755,root,root) %{_libdir}/libgudev-1.0.so
%dir %attr(0755,root,root) %{_includedir}/gudev-1.0
%dir %attr(0755,root,root) %{_includedir}/gudev-1.0/gudev
%attr(0644,root,root) %{_includedir}/gudev-1.0/gudev/*.h
%attr(0644,root,root) %{_libdir}/pkgconfig/gudev-1.0.pc

