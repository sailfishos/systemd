%global pkgdir %{_prefix}/lib/systemd
%global system_unit_dir %{pkgdir}/system
%global user_unit_dir %{pkgdir}/user

Name:           systemd
Url:            http://www.freedesktop.org/wiki/Software/systemd
Version:        225
Release:        1
# For a breakdown of the licensing, see README
License:        LGPLv2+ and MIT and GPLv2+
Summary:        A System and Service Manager

Source0:        https://github.com/systemd/systemd/archive/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source2:        tests.xml
Source3:        systemctl-user
# We need to disable false positive rpmlint's error in systemd.pc.
# Can be removed after fixing: https://bugs.merproject.org/show_bug.cgi?id=1341
Source4:        systemd-rpmlintrc

Patch0:         systemd-208-video.patch
Patch1:         systemd-208-pkgconfigdir.patch
Patch2:         systemd-187-remove-display-manager.service.patch
Patch4:         systemd-208-install-test-binaries.patch
Patch8:         systemd-208-count-only-restarts.patch
Patch9:         systemd-208-do-not-pull-4-megs-from-stack-for-journal-send-test.patch
Patch10:        systemd-227-sd_pid_notify_with_fds-fix-computing-msg_controllen.patch
Patch11:        systemd-228-core-simplify-handling-of-u-U-s-and-h-unit-file-spec.patch
Patch12:        systemd-228-tmpfiles-set-acls-on-system.journal-explicitly.patch
Patch20:        systemd-Define-__NR_kcmp-if-it-is-not-defined.patch
Patch21:        systemd-backport-Revert-usage-of-ln-relative.patch
# These 2 patches backport udev-based firmware loading.
# Should be removed after switching to proper kernel-based way.
Patch22:        systemd-backport-Revert-udev-remove-userspace-firmware-loading-suppor.patch
Patch23:        systemd-backport-Revert-rules-remove-firmware-loading-rules.patch
# Workaround for JB#36605. Should be removed after implementing UDEV events
# handling in initramfs.
Patch24:        systemd-udev-lvm-workaround.patch
Patch25:        systemd-225-add-pam-systemd-timeout-argument.patch
Patch26:        systemd-227-sd-event-fix-prepare-priority-queue-comparison-function.patch
Patch27:        systemd-233-core-downgrade-time-has-been-changed-to-debug.patch
Patch28:        systemd-backport-when-deserializing-always-use-read_line.patch
Patch29:        systemd-backport-enforce-a-limit-on-status-texts-recvd-from-services.patch
Patch30:        systemd-backport-fix-deserialization-of-dev_t.patch
Patch31:        systemd-backport-rework-serialization.patch
Patch32:        systemd-239-dhcp6-client-CVE-2018-15688-fix.patch
Patch33:        systemd-backport-Remove-extra-BindsTo.patch
Patch34:        systemd-234-udev-fix-some-incorrect-usages-of-CLOCK_BOOTTIME-619.patch
Patch35:        systemd-backport-journald-set-a-limit-on-the-number-of-fields-1k.patch
Patch36:        systemd-backport-fuzz-decrease-DATA_SIZE_MAX.patch
Patch37:        systemd-backport-journal-fix-syslog_parse_identifier.patch
Patch38:        systemd-backport-If-the-notification-message-length-is-0-ignore-the-m.patch
Patch39:        systemd-backport-pam-systemd-use-secure_getenv-rather-than-getenv.patch
Patch40:        systemd-234-sd-login-read-list-of-uids-of-sessions-from-UIDS-not.patch
# JB#49681 related patches
Patch41:        0001-aarch64-Force-udev-path.-Contributes-to-JB-49681.patch
Patch42:	0002-We-do-not-have-a-clean-environment-where-HAVE_SPIT_U.patch
# end
Patch99:        systemd-225_fix_build_with_glibc228.patch

BuildRequires:  audit-libs-devel
BuildRequires:  fdupes
BuildRequires:  glib2-devel
BuildRequires:  gperf
BuildRequires:  intltool >= 0.40.0
BuildRequires:  kmod-devel >= 15
BuildRequires:  libacl-devel
BuildRequires:  libcap-devel
BuildRequires:  libgcrypt-devel
BuildRequires:  libmount-devel
BuildRequires:  libselinux-devel
BuildRequires:  libtool
BuildRequires:  libxslt
BuildRequires:  pam-devel
BuildRequires:  pkgconfig(blkid) >= 2.20
BuildRequires:  pkgconfig(dbus-1) >= 1.3.2
BuildRequires:  pkgconfig(dbus-glib-1)
BuildRequires:  pkgconfig(libcryptsetup) >= 1.6.0
BuildRequires:  xz-devel
Requires(post): /sbin/ldconfig
Requires(postun): /sbin/ldconfig
Requires:       %{name}-libs = %{version}-%{release}
Requires:       dbus
Requires:       filesystem >= 3
Requires:       systemd-config
# fsck with -l option was introduced in 2.21.2 packaging
Requires:       util-linux >= 2.21.2
Requires:       which
# pidof command
Requires:       psmisc
# For vgchange tool and LVM udev rules. Workaround for JB#36605.
# Should be removed after implementing UDEV events handling in initramfs.
Requires:       lvm2

Provides:       udev = %{version}
Obsoletes:      udev < 184
Provides:       systemd-sysv = %{version}
Obsoletes:      systemd-sysv < %{version}

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

Provides:       libgudev1 = %{version}
Obsoletes:      libgudev1 <= 209

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
Requires:   %{name} = %{version}-%{release}
Provides:   systemd-config

%description config-mer
This package provides default configuration for systemd

%package analyze
Summary:    Analyze systemd startup timing
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
Requires:       pam >= 1.3.1

%description libs
Libraries for systemd and udev, as well as the systemd PAM module.

%package compat-libs
Summary:        systemd compatibility libraries
License:        LGPLv2+ and MIT
# To reduce confusion, this package can only be installed in parallel
# with the normal systemd-libs, same version.
Requires:       systemd-libs = %{version}-%{release}

%description compat-libs
Compatibility libraries for systemd. If your package requires this
package, you need to update your link options and build.

%package devel
Summary:        Development headers for systemd
License:        LGPLv2+ and MIT
# We need both libsystemd and libsystemd-<compat> libraries
Requires:       %{name}-libs = %{version}-%{release}
Requires:       %{name}-compat-libs = %{version}-%{release}
# For macros.systemd
Requires:       %{name} = %{version}-%{release}
Provides:       libudev-devel = %{version}
Obsoletes:      libudev-devel < %{version}

%description devel
Development headers and auxiliary files for developing applications linking
to libudev or libsystemd.

%package doc
Summary:   System and session manager documentation
Requires:  %{name} = %{version}-%{release}
Obsoletes: %{name}-docs

%description doc
%{summary}.

%package tests
Summary:   Systemd tests
Requires:  %{name} = %{version}-%{release}
Requires:  blts-tools

%description tests
This package includes tests for systemd.

%prep
%setup -q -n %{name}-%{version}/systemd

%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch4 -p1
%patch8 -p1
%patch9 -p1
%patch10 -p1
%patch11 -p1
%patch12 -p1
%patch20 -p1
%patch21 -p1
# Udev firmware loading workaround.
%patch22 -p1
%patch23 -p1
# JB#36605 LVM/UDEV workaround.
%patch24 -p1
%patch25 -p1
# occasional boot hang fix
%patch26 -p1
# shutup 'Time has been changed messages' in journal info
%patch27 -p1
%patch28 -p1
%patch29 -p1
%patch30 -p1
%patch31 -p1
# DHCP6 client CVE-2018-15688 fix
%patch32 -p1
# home encryption related patches
%patch33 -p1
%patch34 -p1
%patch35 -p1
%patch36 -p1
%patch37 -p1
%patch38 -p1
%patch39 -p1
# multiuser fixes
%patch40 -p1
# udev path temporary fix
%patch41 -p1
%patch42 -p1
#systemd-225_fix_build_with_glibc228.patch
%patch99 -p1

%build
./autogen.sh

CONFIGURE_OPTS=(
        --disable-kdbus
)

%configure \
        "${CONFIGURE_OPTS[@]}" \
        --enable-compat-libs \
        --with-rootprefix=/usr \
        --disable-coredump \
        --disable-static \
        --with-firmware-path=/lib/firmware/updates:/lib/firmware:/system/etc/firmware:/etc/firmware:/vendor/firmware:/firmware/image \
        --disable-manpages \
        --disable-libcurl \
        --disable-timesyncd \
        --disable-resolved \
        --disable-rfkill \
        --disable-machined \
        --disable-importd \
        --disable-zlib \
        --without-python \
        --disable-xkbcommon \
        --disable-seccomp \
        --disable-apparmor \
        --enable-pam \
        --enable-acl \
        --enable-audit \
        --disable-elfutils \
        --disable-qrencode \
        --disable-microhttpd \
        --disable-gnutls \
        --disable-libcurl \
        --disable-libidn \
        --disable-libiptc \
        --disable-quotacheck \
        --disable-firstboot \
        --disable-backlight \
        --disable-timedated \
        --disable-networkd \
        --disable-localed \
        --disable-myhostname \
        --with-sysvinit-path="" \
        --with-sysvrcnd-path="" \
        --disable-hibernate \
        --with-zshcompletiondir=no \
        --with-ntp-servers="0.sailfishos.pool.ntp.org 1.sailfishos.pool.ntp.org 2.sailfishos.pool.ntp.org 3.sailfishos.pool.ntp.org" \
        --enable-tests \
        --enable-selinux \
        CFLAGS=-fno-lto

make %{?_smp_mflags} GCC_COLORS="" V=1

%install
%make_install

# udev links
mkdir -p %{buildroot}/%{_sbindir}
ln -sf ..%{_bindir}/udevadm %{buildroot}%{_sbindir}/udevadm
# legacy link to keep things working while we move to bindir
mkdir -p %{buildroot}/bin
ln -sf ..%{_bindir}/udevadm %{buildroot}/bin/udevadm

# Compatiblity and documentation files
touch %{buildroot}/%{_sysconfdir}/crypttab
chmod 600 %{buildroot}/%{_sysconfdir}/crypttab

# Create SysV compatibility symlinks. systemctl/systemd are smart
# enough to detect in which way they are called.
mkdir -p %{buildroot}/sbin
ln -s ..%{pkgdir}/systemd %{buildroot}/sbin/init
ln -s ../..%{_bindir}/systemctl %{buildroot}%{_sbindir}/reboot
ln -s ../..%{_bindir}/systemctl %{buildroot}%{_sbindir}/halt
ln -s ../..%{_bindir}/systemctl %{buildroot}%{_sbindir}/poweroff
ln -s ../..%{_bindir}/systemctl %{buildroot}%{_sbindir}/shutdown
ln -s ../..%{_bindir}/systemctl %{buildroot}%{_sbindir}/telinit
ln -s ../..%{_bindir}/systemctl %{buildroot}%{_sbindir}/runlevel

# Make sure these directories are properly owned
mkdir -p %{buildroot}%{system_unit_dir}/basic.target.wants
mkdir -p %{buildroot}%{system_unit_dir}/default.target.wants
mkdir -p %{buildroot}%{system_unit_dir}/dbus.target.wants
mkdir -p %{buildroot}%{system_unit_dir}/getty.target.wants
mkdir -p %{buildroot}%{system_unit_dir}/syslog.target.wants
mkdir -p %{buildroot}%{system_unit_dir}/graphical.target.wants
mkdir -p %{buildroot}%{system_unit_dir}/network.target.wants

# Require network to be enabled with multi-user.target
mkdir -p %{buildroot}%{system_unit_dir}/multi-user.target.wants/
ln -s ../network.target %{buildroot}%{system_unit_dir}/multi-user.target.wants/network.target

# Install Fedora default preset policy
mkdir -p %{buildroot}%{pkgdir}/system-preset/
mkdir -p %{buildroot}%{pkgdir}/user-preset/

# Make sure the shutdown/sleep drop-in dirs exist
mkdir -p %{buildroot}%{pkgdir}/system-shutdown/
mkdir -p %{buildroot}%{pkgdir}/system-sleep/

# Make sure the NTP units dir exists
mkdir -p %{buildroot}%{pkgdir}/ntp-units.d/

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

mv %{buildroot}/%{_docdir}/systemd{,-%{version}}/

mkdir -p %{buildroot}/etc/systemd/system/basic.target.wants

# Add systemctl-user helper script
install -D -m 754 %{SOURCE3} %{buildroot}%{_bindir}/systemctl-user

%fdupes  %{buildroot}/%{_datadir}/man/

# Install tests.xml
install -d -m 755 %{buildroot}/opt/tests/systemd-tests
install -m 644 %{SOURCE2} %{buildroot}/opt/tests/systemd-tests

# systemd macros
# Old rpm versions assume macros in /etc/rpm/
# New ones support /usr/lib/rpm/macros.d/
# Systemd naturually uses later one
# But we support both by adding link
mkdir -p %{buildroot}%{_sysconfdir}/rpm
ln -s %{_libdir}/rpm/macros.d/macros.systemd %{buildroot}%{_sysconfdir}/rpm/macros.systemd

# Remove unneeded files
rm %{buildroot}%{_sysconfdir}/X11/xinit/xinitrc.d/50-systemd-user.sh

%find_lang %{name}

%check
#make check VERBOSE=1

# Check for botched translations (https://bugzilla.redhat.com/show_bug.cgi?id=1226566)
test -z "$(grep -L xml:lang %{buildroot}%{_datadir}/polkit-1/actions/org.freedesktop.*.policy)"


%pre
getent group cdrom >/dev/null 2>&1 || groupadd -r -g 11 cdrom >/dev/null 2>&1 || :
getent group utmp >/dev/null 2>&1 || groupadd -r -g 22 utmp >/dev/null 2>&1 || :
getent group tape >/dev/null 2>&1 || groupadd -r -g 33 tape >/dev/null 2>&1 || :
getent group dialout >/dev/null 2>&1 || groupadd -r -g 18 dialout >/dev/null 2>&1 || :
getent group input >/dev/null 2>&1 || groupadd -r input >/dev/null 2>&1 || :
getent group systemd-journal >/dev/null 2>&1 || groupadd -r -g 190 systemd-journal 2>&1 || :
#getent group systemd-timesync >/dev/null 2>&1 || groupadd -r systemd-timesync 2>&1 || :
#getent passwd systemd-timesync >/dev/null 2>&1 || useradd -r -l -g systemd-timesync -d / -s /sbin/nologin -c "systemd Time Synchronization" systemd-timesync >/dev/null 2>&1 || :
getent group systemd-network >/dev/null 2>&1 || groupadd -r systemd-network 2>&1 || :
getent passwd systemd-network >/dev/null 2>&1 || useradd -r -l -g systemd-network -d / -s /sbin/nologin -c "systemd Network Management" systemd-network >/dev/null 2>&1 || :
#getent group systemd-resolve >/dev/null 2>&1 || groupadd -r systemd-resolve 2>&1 || :
#getent passwd systemd-resolve >/dev/null 2>&1 || useradd -r -l -g systemd-resolve -d / -s /sbin/nologin -c "systemd Resolver" systemd-resolve >/dev/null 2>&1 || :
getent group systemd-bus-proxy >/dev/null 2>&1 || groupadd -r systemd-bus-proxy 2>&1 || :
getent passwd systemd-bus-proxy >/dev/null 2>&1 || useradd -r -l -g systemd-bus-proxy -d / -s /sbin/nologin -c "systemd Bus Proxy" systemd-bus-proxy >/dev/null 2>&1 || :

systemctl stop systemd-udevd-control.socket systemd-udevd-kernel.socket systemd-udevd.service >/dev/null 2>&1 || :


%post
touch /etc/machine-id || :
%{pkgdir}/systemd-random-seed save >/dev/null 2>&1 || :
systemctl daemon-reexec >/dev/null 2>&1 || :
systemctl start systemd-udevd.service >/dev/null 2>&1 || :
udevadm hwdb --update >/dev/null 2>&1 || :
journalctl --update-catalog >/dev/null 2>&1 || :
systemd-tmpfiles --create >/dev/null 2>&1 || :

# Make sure new journal files will be owned by the "systemd-journal" group
chgrp systemd-journal /run/log/journal/ /run/log/journal/`cat /etc/machine-id 2> /dev/null` /var/log/journal/ /var/log/journal/`cat /etc/machine-id 2> /dev/null` >/dev/null 2>&1 || :
chmod g+s /run/log/journal/ /run/log/journal/`cat /etc/machine-id 2> /dev/null` /var/log/journal/ /var/log/journal/`cat /etc/machine-id 2> /dev/null` >/dev/null 2>&1 || :

# Apply ACL to the journal directory
setfacl -Rnm g:wheel:rx,d:g:wheel:rx,g:adm:rx,d:g:adm:rx /var/log/journal/ >/dev/null 2>&1 || :

# remove obsolete systemd-readahead file
rm -f /.readahead > /dev/null 2>&1 || :

# Make sure all symlinks in /etc/systemd/system point to the new units in
# /usr/lib/systemd/system and not in /lib/systemd/system
# This will find all broken symlinks and disable and enable each service
# JB#51560
for a in `find /etc/systemd/system -type l ! -exec test -e {} \; -print`; do stat -t -c%N $a | sed "s/'//g" | awk -F "/" '{print $NF" "$NF}' | xargs printf "systemctl disable %s; systemctl enable %s;\n" | sh; done || :


%post libs -p /sbin/ldconfig
%postun libs -p /sbin/ldconfig

%post compat-libs -p /sbin/ldconfig
%postun compat-libs -p /sbin/ldconfig

%files -f %{name}.lang
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
%dir %{pkgdir}
%dir %{pkgdir}/catalog
%dir %{system_unit_dir}
%dir %{_prefix}/lib/tmpfiles.d
%dir %{_prefix}/lib/sysctl.d
%dir %{_prefix}/lib/modules-load.d
%dir %{_prefix}/lib/binfmt.d
%dir %{_localstatedir}/log/journal
%dir %{_localstatedir}/lib/systemd
%dir %{_localstatedir}/lib/systemd/catalog
%dir %{_localstatedir}/lib/systemd/coredump
%ghost %{_localstatedir}/lib/systemd/random-seed
%ghost %{_localstatedir}/lib/systemd/catalog/database
%dir %{_sysconfdir}/dbus-1/system.d
%config %{_sysconfdir}/dbus-1/system.d/org.freedesktop.systemd1.conf
%config %{_sysconfdir}/dbus-1/system.d/org.freedesktop.hostname1.conf
%config %{_sysconfdir}/dbus-1/system.d/org.freedesktop.login1.conf
%config %{_sysconfdir}/pam.d/systemd-user
%ghost %{_sysconfdir}/udev/hwdb.bin
%{_rpmconfigdir}/macros.d/macros.systemd
%dir %{_sysconfdir}/xdg/systemd
%{_sysconfdir}/rpm/macros.systemd
%{_bindir}/systemctl
%{_bindir}/systemd-notify
%{_bindir}/systemd-escape
%{_bindir}/systemd-ask-password
%{_bindir}/systemd-tty-ask-password-agent
%{_bindir}/systemd-machine-id-setup
%{_bindir}/loginctl
%{_bindir}/journalctl
%config %{_sysconfdir}/xdg/systemd/user
%ghost %{_sysconfdir}/crypttab
%{_sysconfdir}/systemd/system/*
# Do we really need this? We're including individual files below
#%%{_prefix}/lib/tmpfiles.d/*
%{_prefix}/lib/sysctl.d/50-default.conf
%dir %{user_unit_dir}
%{user_unit_dir}/*
%{pkgdir}/user-generators/systemd-dbus1-generator
%dir /lib/udev/
/lib/udev/*
%{_bindir}/systemctl-user
%{_bindir}/busctl
%{_bindir}/systemd-tmpfiles
%{_bindir}/kernel-install
%{_bindir}/systemd-nspawn
%{_bindir}/systemd-stdio-bridge
%{_bindir}/systemd-cat
%{_bindir}/systemd-cgls
%{_bindir}/systemd-cgtop
%{_bindir}/systemd-delta
%{_bindir}/systemd-run
%{_bindir}/systemd-detect-virt
%{_bindir}/systemd-inhibit
%{_bindir}/systemd-path
%{_bindir}/systemd-sysusers
%{_bindir}/systemd-hwdb
%{_bindir}/hostnamectl
%{_bindir}/bootctl
%{_prefix}/lib/tmpfiles.d/systemd.conf
%{_prefix}/lib/tmpfiles.d/systemd-nologin.conf
%{_prefix}/lib/tmpfiles.d/x11.conf
%{_prefix}/lib/tmpfiles.d/tmp.conf
%{_prefix}/lib/tmpfiles.d/var.conf
%{_prefix}/lib/tmpfiles.d/etc.conf
%{_prefix}/lib/tmpfiles.d/home.conf
%{_prefix}/lib/tmpfiles.d/systemd-nspawn.conf
%{_prefix}/lib/tmpfiles.d/journal-nocow.conf
%{pkgdir}/catalog/systemd.catalog
%{_bindir}/udevadm
# legacy symlink
/bin/udevadm
%dir %{_prefix}/lib/kernel
%dir %{_prefix}/lib/kernel/install.d
%{_prefix}/lib/kernel/install.d/50-depmod.install
%{_prefix}/lib/kernel/install.d/90-loaderentry.install
/sbin/init
%{_sbindir}/reboot
%{_sbindir}/halt
%{_sbindir}/poweroff
%{_sbindir}/shutdown
%{_sbindir}/telinit
%{_sbindir}/runlevel
%{_sbindir}/udevadm
%{_datadir}/factory/etc/nsswitch.conf
%{_datadir}/factory/etc/pam.d/other
%{_datadir}/factory/etc/pam.d/system-auth
%{_prefix}/lib/systemd
%{_datadir}/dbus-1/*/org.freedesktop.systemd1.*
%{_datadir}/dbus-1/system-services/org.freedesktop.hostname1.service
%{_datadir}/dbus-1/system-services/org.freedesktop.login1.service
%{_datadir}/polkit-1/actions/org.freedesktop.systemd1.policy
%{_datadir}/polkit-1/actions/org.freedesktop.hostname1.policy
%{_datadir}/polkit-1/actions/org.freedesktop.login1.policy
%dir %{_datadir}/bash-completion
%dir %{_datadir}/bash-completion/completions
%{_datadir}/bash-completion/completions/*
%{pkgdir}/catalog/systemd.*.catalog

# Just make sure we don't package these by default
%exclude %{_prefix}/lib/systemd/system/default.target
%exclude %{user_unit_dir}/default.target
%exclude %{_sysconfdir}/systemd/system/multi-user.target.wants/remote-fs.target
%exclude %{system_unit_dir}/user@.service

%files config-mer
%defattr(-,root,root,-)
%config %{_sysconfdir}/systemd/journald.conf
%config %{_sysconfdir}/systemd/logind.conf
%config %{_sysconfdir}/systemd/system.conf
%config %{_sysconfdir}/systemd/user.conf
%config %{_sysconfdir}/udev/udev.conf
%config %{_sysconfdir}/systemd/bootchart.conf
%config %{_prefix}/lib/sysusers.d/basic.conf
%config %{_prefix}/lib/sysusers.d/systemd.conf
%{system_unit_dir}/default.target
%{system_unit_dir}/user@.service

%files doc
%defattr(-,root,root,-)
%{_docdir}/%{name}-%{version}

%files tests
%defattr(-,root,root,-)
%dir /opt/tests/systemd-tests
/opt/tests/systemd-tests/tests.xml
%dir /opt/tests/systemd-tests/bin
/opt/tests/systemd-tests/bin/test-*

%files analyze
%defattr(-,root,root,-)
%{_bindir}/systemd-analyze

%files libs
%{_libdir}/security/pam_systemd.so
%{_libdir}/libudev.so.*
%{_libdir}/libsystemd.so.*

%files compat-libs
%{_libdir}/libsystemd-daemon.so.*
%{_libdir}/libsystemd-login.so.*
%{_libdir}/libsystemd-journal.so.*
%{_libdir}/libsystemd-id128.so.*

%files devel
%dir %{_includedir}/systemd
%{_libdir}/libudev.so
%{_libdir}/libsystemd.so
%{_libdir}/libsystemd-daemon.so
%{_libdir}/libsystemd-login.so
%{_libdir}/libsystemd-journal.so
%{_libdir}/libsystemd-id128.so
%{_includedir}/systemd/sd-daemon.h
%{_includedir}/systemd/sd-login.h
%{_includedir}/systemd/sd-journal.h
%{_includedir}/systemd/sd-id128.h
%{_includedir}/systemd/sd-messages.h
%{_includedir}/systemd/sd-bus-protocol.h
%{_includedir}/systemd/sd-bus-vtable.h
%{_includedir}/systemd/sd-bus.h
%{_includedir}/systemd/sd-event.h
%{_includedir}/systemd/_sd-common.h
%{_includedir}/libudev.h
%{_libdir}/pkgconfig/libudev.pc
%{_libdir}/pkgconfig/libsystemd.pc
%{_libdir}/pkgconfig/libsystemd-daemon.pc
%{_libdir}/pkgconfig/libsystemd-login.pc
%{_libdir}/pkgconfig/libsystemd-journal.pc
%{_libdir}/pkgconfig/libsystemd-id128.pc
%{_libdir}/pkgconfig/systemd.pc
%{_libdir}/pkgconfig/udev.pc
