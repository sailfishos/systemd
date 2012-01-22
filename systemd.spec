%define udev_libdir /lib/udev
%define systemd_dir /lib/systemd/system

Name:       systemd
Summary:    System and Session Manager
Version:    37
Release:    1
Group:      System/System Control
License:    GPLv2
URL:        http://www.freedesktop.org/wiki/Software/systemd
Source0:    http://www.freedesktop.org/software/systemd/%{name}-%{version}.tar.bz2
Source1:    pamconsole-tmp.conf
Patch1:     %{name}-24-fsck-disable-l-util-linux.patch
BuildRequires:  pkgconfig(dbus-1) >= 1.3.2
BuildRequires:  pkgconfig(dbus-glib-1)
BuildRequires:  pkgconfig(gio-unix-2.0)
BuildRequires:  pkgconfig(libudev) >= 172
BuildRequires:  libcap-devel
BuildRequires:  libxslt
BuildRequires:  pam-devel
BuildRequires:  intltool >= 0.40.0
BuildRequires:  libacl-devel
BuildRequires:  fdupes
BuildRequires:  gperf
Requires(post): /sbin/ldconfig
Requires(postun): /sbin/ldconfig

%description
system and session manager for Linux, compatible with SysV and
LSB init scripts. systemd provides aggressive parallelization
capabilities, uses socket and D-Bus activation for starting
services, offers on-demand starting of daemons, keeps track of
processes using Linux cgroups, supports snapshotting and restoring
of the system state, maintains mount and automount points and
implements an elaborate transactional dependency-based service
control logic. It can work as a drop-in replacement for sysvinit.

%package tools
Summary:    Analyze systemd startup timing
Group:      Development/Tools
Requires:   pycairo
Requires:   %{name} = %{version}-%{release}

%description tools
This package installs the systemd-analyze tool, which allows one to
inspect and graph service startup timing in table or graph format.

%package devel
Summary:    Development tools for systemd
Group:      Development/Libraries
Requires:   %{name} = %{version}-%{release}

%description devel
This package includes the libraries and header files you will need
to compile applications for systemd.

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

%patch1 -p1 

%build
autoreconf 
%configure --disable-static \
    --with-rootdir=/ \
    --with-distro=meego \
    --disable-gtk \
    --disable-selinux \
    --disable-tcpwrap \
    --with-udevrulesdir=/lib/udev/rules.d/

make %{?_smp_mflags}

%install
%make_install

# Create SysV compatibility symlinks. systemctl/systemd are smart
# enough to detect in which way they are called.
install -d %{buildroot}/sbin/
ln -s ../bin/systemd %{buildroot}/sbin/init
ln -s ../bin/systemctl %{buildroot}/sbin/halt
ln -s ../bin/systemctl %{buildroot}/sbin/poweroff
ln -s ../bin/systemctl %{buildroot}/sbin/reboot
ln -s ../bin/systemctl %{buildroot}/sbin/runlevel
ln -s ../bin/systemctl %{buildroot}/sbin/shutdown
ln -s ../bin/systemctl %{buildroot}/sbin/telinit

# We need a /run directory for early systemd
mkdir %{buildroot}/run

# Make sure these directories are properly owned
mkdir -p %{buildroot}/lib/systemd/system/basic.target.wants
mkdir -p %{buildroot}/lib/systemd/system/default.target.wants
mkdir -p %{buildroot}/lib/systemd/system/dbus.target.wants
mkdir -p %{buildroot}/lib/systemd/system/getty.target.wants
mkdir -p %{buildroot}/lib/systemd/system/syslog.target.wants

# enable readahead by default
ln -s ../systemd-readahead-collect.service %{buildroot}/lib/systemd/system/sysinit.target.wants/systemd-readahead-collect.service
ln -s ../systemd-readahead-replay.service %{buildroot}/lib/systemd/system/sysinit.target.wants/systemd-readahead-replay.service

# Don't ship documentation in the wrong place
rm %{buildroot}/%{_docdir}/systemd/*

install -m 0644 %{SOURCE1} %{buildroot}/etc/tmpfiles.d/pamconsole-tmp.conf

mkdir -p %{buildroot}/etc/systemd/system/basic.target.wants

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


%fdupes  %{buildroot}/%{_datadir}/man/

%post
if [ "`readlink /etc/mtab`" != "/proc/self/mounts" ]; then
	rm -f /etc/mtab
	ln -s /proc/self/mounts /etc/mtab
fi
/bin/systemd-machine-id-setup >/dev/null 2>&1 || :

/sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%defattr(-,root,root,-)
/run
%config %{_sysconfdir}/dbus-1/system.d/org.freedesktop.systemd1.conf
%config %{_sysconfdir}/dbus-1/system.d/org.freedesktop.hostname1.conf
%config %{_sysconfdir}/dbus-1/system.d/org.freedesktop.locale1.conf
%config %{_sysconfdir}/dbus-1/system.d/org.freedesktop.login1.conf
%config %{_sysconfdir}/dbus-1/system.d/org.freedesktop.timedate1.conf
%attr(0644,root,root) %{udev_libdir}/rules.d/70-uaccess.rules
%attr(0644,root,root) %{udev_libdir}/rules.d/71-seat.rules
%attr(0644,root,root) %{udev_libdir}/rules.d/73-seat-late.rules
%config %{_sysconfdir}/systemd
%config %{_sysconfdir}/tmpfiles.d/*
%config %{_sysconfdir}/xdg/systemd/user
%config %{_sysconfdir}/bash_completion.d/systemctl-bash-completion.sh
%{_prefix}/%{_lib}/tmpfiles.d/*
%{_prefix}/%{_lib}/systemd/user/*
/bin/systemctl
/bin/systemd
/bin/systemd-notify
/bin/systemd-ask-password
/bin/systemd-tty-ask-password-agent
/bin/systemd-machine-id-setup
/bin/systemd-loginctl
/bin/systemd-tmpfiles
/usr/bin/systemd-cgls
/usr/bin/systemd-nspawn
/usr/bin/systemd-stdio-bridge
/%{_lib}/systemd
/%{_lib}/security/pam_systemd.so
/%{_lib}/udev/rules.d/99-systemd.rules
/%{_libdir}/libsystemd-daemon.so.*
/%{_libdir}/libsystemd-login.so.*
%{_datadir}/dbus-1/*/org.freedesktop.systemd1.*
%{_defaultdocdir}/systemd
%{_datadir}/polkit-1/actions/org.freedesktop.systemd1.policy
%{_datadir}/polkit-1/actions/org.freedesktop.locale1.policy
%{_datadir}/polkit-1/actions/org.freedesktop.login1.policy
%{_datadir}/polkit-1/actions/org.freedesktop.timedate1.policy
%{_datadir}/polkit-1/actions/org.freedesktop.hostname1.policy
%{_datadir}/dbus-1/system-services/org.freedesktop.hostname1.service
%{_datadir}/dbus-1/system-services/org.freedesktop.locale1.service
%{_datadir}/dbus-1/system-services/org.freedesktop.login1.service
%{_datadir}/dbus-1/system-services/org.freedesktop.timedate1.service
%{_datadir}/dbus-1/interfaces/org.freedesktop.hostname1.xml
%{_datadir}/dbus-1/interfaces/org.freedesktop.locale1.xml
%{_datadir}/dbus-1/interfaces/org.freedesktop.timedate1.xml
%{_datadir}/systemd/kbd-model-map
%exclude %{systemd_dir}/getty.target.wants/serial-getty@tty01.service
%exclude %{systemd_dir}/getty.target.wants/serial-getty@ttyMFD2.service
%exclude %{systemd_dir}/getty.target.wants/serial-getty@ttyO2.service
%exclude %{systemd_dir}/getty.target.wants/serial-getty@ttyS0.service
%exclude %{systemd_dir}/getty.target.wants/serial-getty@ttyS1.service

%files docs
%defattr(-,root,root,-)
%doc %{_mandir}/man?/*

%files console-ttyMFD2
%defattr(-,root,root,-)
%{systemd_dir}/getty.target.wants/serial-getty@ttyMFD2.service

%files console-ttyS0
%defattr(-,root,root,-)
%{systemd_dir}/getty.target.wants/serial-getty@ttyS0.service

%files console-ttyS1
%defattr(-,root,root,-)
%{systemd_dir}/getty.target.wants/serial-getty@ttyS1.service

%files console-tty01
%defattr(-,root,root,-)
%{systemd_dir}/getty.target.wants/serial-getty@tty01.service

%files console-ttyO2
%defattr(-,root,root,-)
%{systemd_dir}/getty.target.wants/serial-getty@ttyO2.service

%files console-ttyAMA0
%defattr(-,root,root,-)
%{systemd_dir}/getty.target.wants/serial-getty@ttyAMA0.service

%files tools
%defattr(-,root,root,-)
/usr/bin/systemd-analyze

%files devel
%defattr(-,root,root,-)
%{_includedir}/systemd/sd-daemon.h
%{_includedir}/systemd/sd-login.h
%{_libdir}/libsystemd-login.so
%{_libdir}/libsystemd-daemon.so
%{_libdir}/pkgconfig/libsystemd-daemon.pc
%{_libdir}/pkgconfig/libsystemd-login.pc
%{_datadir}/pkgconfig/systemd.pc

%files sysv
%defattr(-,root,root,-)
%doc LICENSE
/sbin/halt
/sbin/init
/sbin/poweroff
/sbin/reboot
/sbin/runlevel
/sbin/shutdown
/sbin/telinit

%files sysv-docs
%defattr(-,root,root,-)
%doc %{_mandir}/man?/*
