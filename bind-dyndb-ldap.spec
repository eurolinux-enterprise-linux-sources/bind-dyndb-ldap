#%define PATCHVER P4
#%define PREVER 20120925git072225
#%define VERSION %{version}-%{PATCHVER}
#%define VERSION %{version}-%{PREVER}
%define VERSION %{version}

Name:           bind-dyndb-ldap
Version:        2.3
Release:        5%{?dist}
Summary:        LDAP back-end plug-in for BIND

Group:          System Environment/Libraries
License:        GPLv2+
URL:            https://fedorahosted.org/bind-dyndb-ldap
Source0:        https://fedorahosted.org/released/%{name}/%{name}-%{VERSION}.tar.bz2
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  bind-devel >= 32:9.6.1-0.3.b1
BuildRequires:  krb5-devel
BuildRequires:  openldap-devel
BuildRequires:  autoconf, automake, libtool

Requires:       bind >= 32:9.6.1-0.3.b1

Patch0: 0001-Don-t-fail-if-idnsSOAserial-attribute-is-missing-in-.patch
Patch1: 0001-Prevent-crash-caused-by-race-condition-during-plugin.patch
Patch2: 0002-Fix-crash-caused-by-zonesub-match-type-in-update-ACL.patch
Patch3: 0003-Prevent-false-zone-serial-2012060301-unchanged-error.patch
Patch4: 0004-Prevent-deadlock-in-sync-ptr.patch

%description
This package provides an LDAP back-end plug-in for BIND. It features
support for dynamic updates and internal caching, to lift the load
off of your LDAP server.


%prep
%setup -q -n %{name}-%{VERSION}

%patch0 -p1 -b .rh895083
%patch1 -p1 -b .rh923113
%patch2 -p1 -b .rh921167
%patch3 -p1 -b .rh908780
%patch4 -p1 -b .rh1010396

%build
export CPPFLAGS=`isc-config.sh --cflags`
autoreconf -fiv
%configure
make %{?_smp_mflags}


%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}

# Remove unwanted files
rm %{buildroot}%{_libdir}/bind/ldap.la
rm -r %{buildroot}%{_datadir}/doc/%{name}


%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%doc README COPYING doc/{example.ldif,schema}
%{_libdir}/bind/ldap.so


%changelog
* Thu Sep 26 2013 Petr Spacek <pspacek redhat com> - 2.3-5
- prevent deadlock in PTR record synchronization (#1010396)

* Fri Jul 26 2013 Petr Spacek <pspacek redhat com> - 2.3-4
- update-policy with match type 'zonesub' lead to crash (#921167)
- zones without idnsUpdatePolicy attribute produced error messages (#908780)

* Fri Mar 22 2013 Adam Tkac <atkac redhat com> - 2.3-3
- processing of configuration opts too early could lead to crash (#923113)

* Tue Jan 15 2013 Adam Tkac <atkac redhat com> - 2.3-2
- idnsSOAserial attribute can be missing on LDAP replicas (#895083)

* Thu Nov 08 2012 Adam Tkac <atkac redhat com> - 2.3-1
- update to 2.3 (fixes some issues with forwarding)

* Wed Oct 31 2012 Adam Tkac <atkac redhat com> - 2.2-1
- update to 2.2

* Mon Oct 29 2012 Adam Tkac <atkac redhat com> - 2.1-1
- update to 2.1

* Tue Oct 16 2012 Adam Tkac <atkac redhat com> - 2.0-1
- update to 2.0

* Tue Sep 25 2012 Adam Tkac <atkac redhat com> - 2.0-0.1.20120925git072225
- rebase to the latest 2.0 snapshot
- patches merged
  - 0001-Fix-ticket-55-BIND-cannot-be-shutdown-correctly-if-p.patch
  - 0001-Fix-crash-on-reload-without-any-zones.patch
  - 0001-Fix-SOA-record-update.patch
  - 0001-Find-A-AAAA-delegation-glue-records-correctly.patch
  - bind-dyndb-ldap11-CVE-2012-2134.patch
  - 0001-Add-proper-DN-escaping-before-LDAP-library-calls.patch
  - bind-dyndb-ldap-CVE-2012-3429.patch

* Fri Jul 27 2012 Adam Tkac <atkac redhat com> - 1.1.0-0.10.b1
- fix CVE-2012-3429

* Wed May 09 2012 Adam Tkac <atkac redhat com> - 1.1.0-0.9.b1
- escape DNS names in queries correctly

* Wed Apr 25 2012 Adam Tkac <atkac redhat com> - 1.1.0-0.8.b1
- rebuild

* Wed Apr 25 2012 Adam Tkac <atkac redhat com> - 1.1.0-0.7.b1
- fix for CVE-2012-2134

* Tue Apr 24 2012 Adam Tkac <atkac redhat com> - 1.1.0-0.6.b1
- return delegation A/AAAA glues correctly

* Mon Mar 26 2012 Adam Tkac <atkac redhat com> - 1.1.0-0.5.b1
- don't crash on stop/reload when no zones are found in LDAP (#805814)
- compute SOA attributes correctly when modifying it (#805871)

* Wed Mar 21 2012 Adam Tkac <atkac redhat com> - 1.1.0-0.4.b1
- plugin could failed to shutdown correctly when using psearch (#802375)

* Wed Mar 07 2012 Adam Tkac <atkac redhat com> - 1.1.0-0.3.b1
- rebuild against updated bind

* Tue Mar 06 2012 Adam Tkac <atkac redhat com> - 1.1.0-0.2.b1
- update to 1.1.0b1

* Wed Feb 15 2012 Adam Tkac <atkac redhat com> - 1.1.0-0.1.a2
- update to 1.1.0a2 release
- all patches were merged to upstream

* Wed Oct 26 2011 Adam Tkac <atkac redhat com> - 0.2.0-7
- fix previous patch, it free()-ed memory when shouldn't (#748901)

* Wed Oct 19 2011 Adam Tkac <atkac redhat com> - 0.2.0-6
- fix memory leak; happened when adding of RRs to cache failed

* Wed Oct 19 2011 Adam Tkac <atkac redhat com> - 0.2.0-5
- add new ldap_hostname option

* Wed Oct 12 2011 Adam Tkac <atkac redhat com> - 0.2.0-4
- always honour selected authentication method (#742368)

* Mon Aug 15 2011 Adam Tkac <atkac redhat com> - 0.2.0-3
- fix race condition in semaphore_wait() function (#727856)

* Fri Aug 12 2011 Adam Tkac <atkac redhat com> - 0.2.0-2
- automatically load new zones runtime when zone_refresh is set (#707255)

* Fri Jan 14 2011 Adam Tkac <atkac redhat com> - 0.2.0-1
- update to 0.2.0

* Wed Mar 24 2010 Martin Nagy <mnagy@redhat.com> - 0.1.0-0.9.b
- update to the latest upstream release
- Resolves: #556554

* Thu Jan 28 2010 Adam Tkac <atkac redhat com> - 0.1.0-0.8.a1.20091210git
- rebuild against updated bind package

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
