%define VERSION %{version}

%define bind_version 32:9.11.1-1.P1

Name:           bind-dyndb-ldap
Version:        11.1
Release:        6%{?dist}
Summary:        LDAP back-end plug-in for BIND

Group:          System Environment/Libraries
License:        GPLv2+
URL:            https://releases.pagure.org/bind-dyndb-ldap
Source0:        https://releases.pagure.org/%{name}/%{name}-%{VERSION}.tar.bz2
Source1:        https://releases.pagure.org/%{name}/%{name}-%{VERSION}.tar.bz2.asc
Patch4:         bind-dyndb-ldap-pemensik-0002-Treat-passwords-like-ordinary-text-bind-does-not-sup.patch
Patch5:         bind-dyndb-ldap-pemensik-0003-Replace-unsupported-autoreallocating-buffer-by-custo.patch
Patch6:         bind-dyndb-ldap-tkrizek-0005-Setting-skip-unconfigured-values.patch
Patch7:         bind-dyndb-ldap-tkrizek-0006-Coverity-fix-REVERSE_INULL-for-pevent-inst.patch
Patch8:         bind-dyndb-ldap-pemensik-0007-Add-empty-callback-for-getsize.patch
Patch9:         bind-dyndb-ldap-pemensik-0008-Support-for-BIND-9.11.3.patch
Patch10:        bind-dyndb-ldap-pemensik-0009-Support-for-BIND-9.11.5.patch
Patch11:        bind-dyndb-ldap-pemensik-0010-Use-correct-dn-value.patch

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  bind-devel >= %{bind_version}, bind-lite-devel >= %{bind_version}, bind-pkcs11-devel >= %{bind_version}
BuildRequires:  krb5-devel
BuildRequires:  openldap-devel
BuildRequires:  openssl-devel
BuildRequires:  libuuid-devel
BuildRequires:  automake, autoconf, libtool

Requires:       bind-pkcs11 >= %{bind_version}, bind-pkcs11-utils >= %{bind_version}
Requires(post):  sed

%description
This package provides an LDAP back-end plug-in for BIND. It features
support for dynamic updates and internal caching, to lift the load
off of your LDAP server.


%prep
%autosetup -p1

%build
autoreconf -fiv
%configure --disable-werror
make %{?_smp_mflags}


%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}
mkdir -m 770 -p %{buildroot}/%{_localstatedir}/named/dyndb-ldap

# Remove unwanted files
rm %{buildroot}%{_libdir}/bind/ldap.la
rm -r %{buildroot}%{_datadir}/doc/%{name}


%post
# Transform named.conf if it still has old-style API.
PLATFORM=$(uname -m) 

if [ $PLATFORM == "x86_64" ] ; then
    LIBPATH=/usr/lib64
else
    LIBPATH=/usr/lib
fi

# The following sed script:
#   - scopes the named.conf changes to dynamic-db
#   - replaces arg "name value" syntax with name "value"
#   - changes dynamic-db header to dyndb
#   - uses the new way the define path to the library
#   - removes no longer supported arguments (library, cache_ttl,
#       psearch, serial_autoincrement, zone_refresh)
while read -r PATTERN
do
    SEDSCRIPT+="$PATTERN"
done <<EOF
/^\s*dynamic-db/,/};/ {

  s/\(\s*\)arg\s\+\(["']\)\([a-zA-Z_]\+\s\)/\1\3\2/g;

  s/^dynamic-db/dyndb/;

  s@\(dyndb "[^"]\+"\)@\1 "$LIBPATH/bind/ldap.so"@;
  s@\(dyndb '[^']\+'\)@\1 '$LIBPATH/bind/ldap.so'@;

  /\s*library[^;]\+;/d;
  /\s*cache_ttl[^;]\+;/d;
  /\s*psearch[^;]\+;/d;
  /\s*serial_autoincrement[^;]\+;/d;
  /\s*zone_refresh[^;]\+;/d;
}
EOF

sed -i.bak -e "$SEDSCRIPT" /etc/named.conf

%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%doc NEWS README.md COPYING doc/{example,schema}.ldif
%dir %attr(770, root, named) %{_localstatedir}/named/dyndb-ldap
%{_libdir}/bind/ldap.so


%changelog
* Tue Feb 12 2019 Petr Menšík <pemensik@redhat.com> - 11.1-6
- Bump BIND version and fix library dependecies
- Rebuild for bind 9.11.3. Minor tweaks to compile.
- Support for bind 9.11.5 headers

* Mon May 28 2018 Petr Menšík <pemensik@redhat.com> - 11.1-5
- Resolves: #1580389 depend on bind with writeable home

* Wed Jul 12 2017 Tomas Krizek <tkrizek@redhat.com> - 11.1-4
- Resolves: #1469563 required bind version doesn't have the dyndb interface

* Wed Apr 26 2017 Tomas Krizek <tkrizek@redhat.com> - 11.1-3
- resolves: #1436268 crash when server_id is not present in named.conf
- coverity fixes

* Wed Mar 15 2017 Tomas Krizek <tkrizek@redhat.com> - 11.1-2
- bump NVR to fix bind dependencies

* Wed Mar 15 2017 Tomas Krizek <tkrizek@redhat.com> - 11.1-1
- update to letest upstream version
- resolves: #1393889 Rebase to bind-dyndb-ldap 11+
- resolves: #1165796 bind-dyndb-ldap crashes if server is shutting down and connection to LDAP is down
- resolves: #1413805 bind-dyndb-ldap default schema is shipped with syntax error

* Wed Sep 21 2016 Petr Spacek <pspacek@redhat.com> - 10.0-5
- resolves: #1376851 Unable to set named_write_master_zones boolean on upgrade

* Tue Aug 16 2016 Petr Spacek <pspacek@redhat.com> - 10.0-4
- resolves: #1366565 Deletion of DNS root zone breaks global forwarding

* Thu Jul 28 2016 Petr Spacek <pspacek@redhat.com> - 10.0-3
- rebuild against redhat-rpm-config-9.1.0-71.el7 to fix /usr/share/doc naming
- related: #1057327

* Wed Jul 27 2016 Petr Spacek <pspacek@redhat.com> - 10.0-2
- resolves: #1359220 prevent crash while reloading previously invalid
  but now valid DNS zone

* Tue Jun 21 2016 Petr Spacek <pspacek@redhat.com> - 10.0-1
- update to latest upstream version
- resolves: #1292145 Rebase bind-dyndb-ldap to latest upstream version

* Thu May 12 2016 Petr Spacek <pspacek@redhat.com> - 9.0-1
- update to latest upstream version
- related: #1292145 Rebase bind-dyndb-ldap to latest upstream version

* Tue Jun 23 2015 Petr Spacek <pspacek redhat com> - 8.0-1
- update to latest upstream version
- resolves: #1204110 Rebase bind-dyndb-ldap to latest upstream version

* Mon Jun 08 2015 Petr Spacek <pspacek redhat com> - 7.99-1
- preliminary update to latests snapshot of upstream Git: 158e95e (#1204110)
- resolves: #829395  DNSSEC support
- resolves: #1139776 LDAP MODRDN (rename) is not supported
- resolves: #1139778 Records deleted when connection to LDAP is down are not refreshed properly
- resolves: #1184065 PTR record synchronization for A/AAAA record tuple can fail mysteriously
- resolves: #1207539 Add support for TLSA resource records (DANE)
- resolves: #1207540 Plugin will crash if idnsForwardZone object is in the wrong place
- resolves: #1207541 Generic support for unknown DNS RR types (RFC 3597)

* Tue Dec 02 2014 Petr Spacek <pspacek redhat com> - 6.0-2
- fix bug 1161635: send DNS NOTIFY message after any modification to the zone
- fix bug 1168131: crash caused by interaction between forward and master zones

* Tue Sep 23 2014 Petr Spacek <pspacek redhat com> - 6.0-1
- update to 6.0
- resolves bugs 1138317, 1144599, 1142176

* Fri Sep 12 2014 Petr Spacek <pspacek redhat com> - 5.3-1
- update to 5.3
- fixes several random crashes

* Mon Sep 08 2014 Petr Spacek <pspacek redhat com> - 5.2-1
- update to 5.2
- adds DNSSEC support and supports root zone in LDAP
- idnsZoneActive attribute is not supported anymore

* Fri Jan 24 2014 Daniel Mach <dmach@redhat.com> - 3.5-4
- Mass rebuild 2014-01-24

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 3.5-3
- Mass rebuild 2013-12-27

* Tue Sep 24 2013 Tomas Hozza <thozza@redhat.com> 3.5-2
- rebuild against new bind (Related: #1010200) (#1011118)

* Thu Jul 18 2013 Petr Spacek <pspacek redhat com> 3.5-1
- update to 3.5

* Tue Jun 25 2013 Petr Spacek <pspacek redhat com> 3.4-1
- update to 3.4

* Tue Jun 04 2013 Petr Spacek <pspacek redhat com> 3.3-1
- update to 3.3
- patch bind-dyndb-ldap-tbabej-0001-Build-fixes-for-Fedora-19.patch merged

* Tue May 14 2013 Petr Spacek <pspacek redhat com> 3.2-1
- update to 3.2

* Tue Apr 16 2013 Adam Tkac <atkac redhat com> 3.1-2
- rebuild against new bind
- build with --disable-werror

* Fri Apr 12 2013 Petr Spacek <pspacek redhat com> 3.1-1
- update to 3.1

* Tue Apr 02 2013 Petr Spacek <pspacek redhat com> 3.0-1
- update to 3.0

* Tue Mar 26 2013 Petr Spacek <pspacek redhat com> 2.6-1
- update to 2.6

* Mon Feb 04 2013 Petr Spacek <pspacek redhat com> 2.5-1
- update to 2.5

* Tue Jan 15 2013 Petr Spacek <pspacek redhat com> 2.4-1
- update to 2.4

* Thu Nov  8 2012 Petr Spacek <pspacek redhat com> 2.3-2
- rebuild with proper changelog

* Thu Nov  8 2012 Petr Spacek <pspacek redhat com> 2.3-1
- update to 2.3

* Mon Oct 29 2012 Adam Tkac <atkac redhat com> 2.1-1
- update to 2.1

* Thu Oct 11 2012 Adam Tkac <atkac redhat com> 2.0-0.3.20121009git6a86b1
- rebuild against new bind-libs

* Tue Oct  9 2012 Petr Spacek <pspacek redhat com> 2.0-0.2.20121009git6a86b1
- update to the latest master

* Fri Sep 21 2012 Adam Tkac <atkac redhat com> 2.0-0.1.20120921git7710d89
- update to the latest master
- bind-dyndb-ldap110-master.patch was merged

* Thu Aug 16 2012 Adam Tkac <atkac redhat com> 1.1.0-0.16.rc1
- update to the latest git

* Thu Aug 02 2012 Adam Tkac <atkac redhat com> 1.1.0-0.15.rc1
- update to the latest git
  - fix for CVE-2012-3429 has been merged

* Thu Aug 02 2012 Adam Tkac <atkac redhat com> 1.1.0-0.14.rc1
- fix CVE-2012-3429

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.0-0.13.rc1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Thu Jun 07 2012 Adam Tkac <atkac redhat com> - 1.1.0-0.12.rc1
- update to the latest master (#827401)

* Thu Apr 26 2012 Adam Tkac <atkac redhat com> - 1.1.0-0.11.rc1
- update to 1.1.0rc1 (CVE-2012-2134)

* Tue Mar 27 2012 Adam Tkac <atkac redhat com> - 1.1.0-0.10.b2
- update to 1.1.0b2

* Tue Mar 06 2012 Adam Tkac <atkac redhat com> - 1.1.0-0.9.b1
- update to 1.1.0b1

* Mon Feb 13 2012 Adam Tkac <atkac redhat com> - 1.1.0-0.8.a2
- update to 1.1.0a2

* Thu Feb 02 2012 Adam Tkac <atkac redhat com> - 1.1.0-0.7.a1
- rebuild against new bind

* Wed Jan 18 2012 Adam Tkac <atkac redhat com> - 1.1.0-0.6.a1
- update to 1.1.0a1

* Thu Jan 12 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.0-0.5.rc1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Mon Nov 14 2011 Adam Tkac <atkac redhat com> - 1.0.0-0.4.rc1
- update to 1.0.0rc1

* Mon Nov 14 2011 Adam Tkac <atkac redhat com> - 1.0.0-0.3.b1
- rebuild against new bind

* Fri Sep 09 2011 Adam Tkac <atkac redhat com> - 1.0.0-0.2.b1
- rebuild against new bind

* Wed Aug 31 2011 Adam Tkac <atkac redhat com> - 1.0.0-0.1.b1
- update to 1.0.0b1 (psearch + bugfixes)
- bind-dyndb-ldap-rh727856.patch merged

* Wed Aug 03 2011 Adam Tkac <atkac redhat com> - 0.2.0-4
- fix race condition in semaphore_wait (#727856)

* Mon Feb 21 2011 Adam Tkac <atkac redhat com> - 0.2.0-3
- rebuild against new bind

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.2.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Wed Jan 12 2011 Adam Tkac <atkac redhat com> - 0.2.0-1
- update to 0.2.0
- patches merged
  - 0001-Bugfix-Improve-LDAP-schema-to-be-loadable-by-OpenLDA.patch
  - 0004-Bugfix-Fix-loading-of-child-zones-from-LDAP.patch

* Wed Dec 15 2010 Adam Tkac <atkac redhat com> - 0.1.0-0.17.b
- fix LDAP schema (#622604)
- load child zones from LDAP correctly (#622617)

* Fri Oct 22 2010 Adam Tkac <atkac redhat com> - 0.1.0-0.16.b
- build with correct RPM_OPT_FLAGS (#645529)

* Wed Oct 20 2010 Adam Tkac <atkac redhat com> - 0.1.0-0.15.b
- use "isc-config.sh" utility to get correct BIND9 CFLAGS

* Thu Sep 30 2010 Adam Tkac <atkac redhat com> - 0.1.0-0.14.b
- rebuild against new bind

* Fri Aug 27 2010 Adam Tkac <atkac redhat com> - 0.1.0-0.13.b
- rebuild against new bind

* Tue Aug 17 2010 Adam Tkac <atkac redhat com> - 0.1.0-0.12.b
- rebuild against new bind

* Tue Aug 03 2010 Adam Tkac <atkac redhat com> - 0.1.0-0.11.b
- rebuild against new bind

* Mon May 31 2010 Adam Tkac <atkac redhat com> - 0.1.0-0.10.b
- rebuild against new bind

* Wed Mar 24 2010 Martin Nagy <mnagy@redhat.com> - 0.1.0-0.9.b
- update to the latest upstream release

* Thu Jan 28 2010 Adam Tkac <atkac redhat com> - 0.1.0-0.8.a1.20091210git
- rebuild against new bind

* Tue Dec 15 2009 Adam Tkac <atkac redhat com> - 0.1.0-0.7.a1.20091210git
- rebuild against new bind

* Thu Dec 10 2009 Martin Nagy <mnagy@redhat.com> - 0.1.0-0.6.a1.20091210git
- update to the latest git snapshot
- change upstream URL, project moved to fedorahosted
- change license to GPL version 2 or later
- add epoch to versioned requires
- add krb5-devel to the list of build requires

* Tue Dec 01 2009 Adam Tkac <atkac redhat com> - 0.1.0-0.5.a1
- rebuild against new bind

* Thu Nov 26 2009 Adam Tkac <atkac redhat com> - 0.1.0-0.4.a1
- rebuild against new bind

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.1.0-0.3.a1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Fri Jun 19 2009 Caolán McNamara <caolanm@redhat.com> - 0.1.0-0.2.a1
- rebuild for dependencies

* Sun May 03 2009 Martin Nagy <mnagy@redhat.com> - 0.1.0-0.1.a1
- initial packaging
