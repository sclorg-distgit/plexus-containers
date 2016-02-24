%global pkg_name plexus-containers
%{?scl:%scl_package %{pkg_name}}
%{?maven_find_provides_and_requires}


%global with_maven 1

%global parent plexus
%global subname containers

# this needs to be exact version of maven-javadoc-plugin for
# integration tests
%global javadoc_plugin_version 2.9

Name:           %{?scl_prefix}%{pkg_name}
Version:        1.5.5
Release:        14.21%{?dist}
Summary:        Containers for Plexus
License:        ASL 2.0 and MIT
URL:            http://plexus.codehaus.org/
# svn export \
#  http://svn.codehaus.org/plexus/plexus-containers/tags/plexus-containers-1.5.5
# tar caf plexus-containers-1.5.5.tar.xz plexus-containers-1.5.5
Source0:        %{pkg_name}-%{version}.tar.xz
Source1:        plexus-container-default-build.xml
Source2:        plexus-component-annotations-build.xml
Source3:        plexus-containers-settings.xml

Patch0:         0001-Fix-test-oom.patch
Patch1:         0002-Update-to-Plexus-Classworlds-2.5.patch
Patch2:         0003-Port-to-objectweb-asm-5.patch

BuildArch:      noarch

BuildRequires:  %{?scl_prefix_java_common}maven-local
BuildRequires:  %{?scl_prefix}maven-invoker-plugin
BuildRequires:  %{?scl_prefix}maven-javadoc-plugin = %{javadoc_plugin_version}
BuildRequires:  %{?scl_prefix}maven-resources-plugin
BuildRequires:  %{?scl_prefix}maven-site-plugin
BuildRequires:  %{?scl_prefix}maven-invoker
BuildRequires:  %{?scl_prefix}maven-release
BuildRequires:  %{?scl_prefix}maven-plugin-plugin
BuildRequires:  %{?scl_prefix}plexus-classworlds
BuildRequires:  %{?scl_prefix}plexus-utils
BuildRequires:  %{?scl_prefix}plexus-cli
BuildRequires:  %{?scl_prefix_java_common}xbean
BuildRequires:  %{?scl_prefix_java_common}guava
BuildRequires:  %{?scl_prefix_java_common}objectweb-asm5

Requires:       %{?scl_prefix}plexus-classworlds >= 2.2.3
Requires:       %{?scl_prefix}plexus-utils
Requires:       %{?scl_prefix_java_common}xbean
Requires:       %{?scl_prefix_java_common}guava


%description
The Plexus project seeks to create end-to-end developer tools for
writing applications. At the core is the container, which can be
embedded or for a full scale application server. There are many
reusable components for hibernate, form processing, jndi, i18n,
velocity, etc. Plexus also includes an application server which
is like a J2EE application server, without all the baggage.

%package component-metadata
Summary:        Component metadata from %{pkg_name}

%description component-metadata
%{summary}.

%package component-javadoc
Summary:        Javadoc component from %{pkg_name}

%description component-javadoc
%{summary}.

%package component-annotations
Summary:        Component API from %{pkg_name}

%description component-annotations
%{summary}.

%package container-default
Summary:        Default Container from %{pkg_name}

%description container-default
%{summary}.

%package javadoc
Summary:        API documentation for all plexus-containers packages

%description javadoc
%{summary}.

%prep
%setup -q -n plexus-containers-%{version}
%{?scl:scl enable %{scl} - <<"EOF"}
set -e -x

cp %{SOURCE1} plexus-container-default/build.xml
cp %{SOURCE2} plexus-component-annotations/build.xml

%patch0 -p1
%patch1 -p1
%patch2 -p1

# For Maven 3 compat
%pom_add_dep org.apache.maven:maven-core plexus-component-metadata

# Remove dependency on system-scoped tools.jar
%pom_remove_dep com.sun:tools plexus-component-javadoc
%pom_add_dep com.sun:tools plexus-component-javadoc

# to prevent ant from failing
mkdir -p plexus-component-annotations/src/test/java

# integration tests fix
sed -i "s|<version>2.3</version>|<version> %{javadoc_plugin_version}</version>|" plexus-component-javadoc/src/it/basic/pom.xml

# plexus-component-api has been merged into plexus-container-default
%mvn_alias ":plexus-container-default" "org.codehaus.plexus:containers-component-api"

# keep compat symlink for maven's sake
%mvn_file ":plexus-component-annotations" %{pkg_name}/plexus-component-annotations plexus/containers-component-annotations
%{?scl:EOF}

%build
%{?scl:scl enable %{scl} - <<"EOF"}
set -e -x
%mvn_build -f -s
%{?scl:EOF}

%install
%{?scl:scl enable %{scl} - <<"EOF"}
set -e -x
%mvn_install


# plexus-containers pom goes into main package
%{?scl:EOF}
%files -f .mfiles-plexus-containers
%{_javadir}/%{pkg_name}
%dir %{_mavenpomdir}/%{pkg_name}
%files component-annotations -f .mfiles-plexus-component-annotations
%dir %{_javadir}/%{pkg_name}
%dir %{_mavenpomdir}/%{pkg_name}
%dir %{_mavenpomdir}/plexus
%dir %{_javadir}/plexus
%files container-default -f .mfiles-plexus-container-default
%dir %{_javadir}/%{pkg_name}
%dir %{_mavenpomdir}/%{pkg_name}
%files component-metadata -f .mfiles-plexus-component-metadata
%dir %{_javadir}/%{pkg_name}
%dir %{_mavenpomdir}/%{pkg_name}
%files component-javadoc -f .mfiles-plexus-component-javadoc
%dir %{_javadir}/%{pkg_name}
%dir %{_mavenpomdir}/%{pkg_name}

%files javadoc -f .mfiles-javadoc

%changelog
* Wed Jan 20 2016 Michal Srb <msrb@redhat.com> - 1.5.5-14.21
- Apply patches from Fedora (port to plexus-classworlds 2.5 and asm5)

* Tue Jan 12 2016 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.5.5-14.20
- Change dependency order to fix ASM classpath problem

* Mon Jan 11 2016 Michal Srb <msrb@redhat.com> - 1.5.5-14.19
- maven33 rebuild #2

* Sat Jan 09 2016 Michal Srb <msrb@redhat.com> - 1.5.5-14.18
- maven33 rebuild

* Fri Jan 16 2015 Michal Srb <msrb@redhat.com> - 1.5.5-14.17
- Fix directory ownership

* Fri Jan 16 2015 Michal Srb <msrb@redhat.com> - 1.5.5-14.16
- Fix directory ownership

* Thu Jan 15 2015 Michael Simacek <msimacek@redhat.com> - 1.5.5-14.15
- Add common dirs to subpackages

* Thu Jan 15 2015 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.5.5-14.14
- Add directory ownership on %%{_mavenpomdir} subdir

* Tue Jan 13 2015 Michael Simacek <msimacek@redhat.com> - 1.5.5-14.13
- Mass rebuild 2015-01-13

* Mon Jan 12 2015 Michael Simacek <msimacek@redhat.com> - 1.5.5-14.12
- BR/R on packages from rh-java-common

* Thu Jan 08 2015 Michal Srb <msrb@redhat.com> - 1.5.5-14.11
- Fix FTBFS

* Tue Jan 06 2015 Michael Simacek <msimacek@redhat.com> - 1.5.5-14.10
- Mass rebuild 2015-01-06

* Mon May 26 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.5.5-14.9
- Mass rebuild 2014-05-26

* Wed Feb 19 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.5.5-14.8
- Mass rebuild 2014-02-19

* Wed Feb 19 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.5.5-14.7
- Rebuild to get rid of auto-requires on java-devel

* Wed Feb 19 2014 Michal Srb <msrb@redhat.com> - 1.5.5-14.6
- Rebuild to fix auto-requires on com.sun:tools

* Tue Feb 18 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.5.5-14.5
- Mass rebuild 2014-02-18

* Mon Feb 17 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.5.5-14.4
- Rebuild to fix incorrect auto-requires

* Fri Feb 14 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.5.5-14.3
- SCL-ize build-requires

* Thu Feb 13 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.5.5-14.2
- Rebuild to regenerate auto-requires

* Tue Feb 11 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.5.5-14.1
- First maven30 software collection build

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 1.5.5-14
- Mass rebuild 2013-12-27

* Wed Nov 13 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.5.5-13
- Remove dependency on system-scoped tools.jar

* Fri Jun 28 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.5.5-12
- Rebuild to regenerate API documentation
- Resolves: CVE-2013-1571

* Fri Mar 22 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.5.5-11
- Correctly place plexus-containers POM in the main package

* Thu Mar 21 2013 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1.5.5-11
- Add compat symlinks to keep Maven working

* Wed Mar 20 2013 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1.5.5-10
- Update to latest packaging guidelines
- Remove several unneeded buildrequires

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5.5-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Feb 06 2013 Java SIG <java-devel@lists.fedoraproject.org> - 1.5.5-8
- Update for https://fedoraproject.org/wiki/Fedora_19_Maven_Rebuild
- Replace maven BuildRequires with maven-local

* Wed Nov 14 2012 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1.5.5-7
- Fix license tag (Plexus license was replaced by MIT some time ago)
- Update javadoc plugin BR version

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5.5-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Feb 17 2012 Deepak Bhole <dbhole@redhat.com> - 1.5.5-5
- Resolves rhbz#791339
- Applied fix from Omair Majid <omajid at redhat dot com> to build with Java 7

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5.5-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Jun 28 2011 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1.5.5-3
- Fix maven3 build
- Use new add_maven_depmap macro

* Mon Feb 28 2011 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1.5.5-2
- Remove unneeded env var definitions

* Fri Feb 25 2011 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1.5.5-1
- Update to latest upstream
- Remove obsolete patches
- Use maven 3 to build
- Packaging fixes
- Versionless jars & javadocs

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5.4-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Oct 11 2010 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1.5.4-4
- Add plexus-cli to component-metadata Requires

* Wed Sep  8 2010 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1.5.4-3
- Use javadoc:aggregate
- Merge javadoc subpackages into one -javadoc

* Thu Jul 15 2010 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1.5.4-2
- Fix maven depmaps

* Tue Jul 13 2010 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1.5.4-1
- Version bump
- Add new sub-packages
- Cleanups

* Thu Aug 20 2009 Andrew Overholt <overholt@redhat.com> 0:1.0-0.1.a34.7
- Clean up javadoc post/postun
- Build with ant
- Remove gcj support
- Clean up groups

* Fri May 15 2009 Fernando Nasser <fnasser@redhat.com> 1.0-0.1.a34.6
- Fix license

* Tue Apr 28 2009 Yong Yang <yyang@redhat.com> 1.0-0.1.a34.5
- Add BRs maven2-plugin-surfire*, maven-doxia*
- Merge from RHEL-4-EP-5 1.0-0.1.a34.2, add plexus-containers-sourcetarget.patch
- Rebuild with new maven2 2.0.8 built in non-bootstrap mode

* Mon Mar 16 2009 Yong Yang <yyang@redhat.com> 1.0-0.1.a34.4
- rebuild with new maven2 2.0.8 built in bootstrap mode

* Wed Feb 04 2009 Yong Yang <yyang@redhat.com> - 1.0-0.1.a34.3
- re-build with maven

* Wed Feb 04 2009 Yong Yang <yyang@redhat.com> - 1.0-0.1.a34.2
- fix bulding with ant
- temporarily buid with ant

* Wed Jan 14 2009 Yong Yang <yyang@redhat.com> - 1.0-0.1.a34.1jpp.2
- re-build with maven
- disabled assert in plexus-container-default/.../UriConverter.java???

* Tue Jan 13 2009 Yong Yang <yyang@redhat.com> - 1.0-0.1.a34.1jpp.1
- Imported into devel from dbhole's maven 2.0.8 packages

* Tue Apr 08 2008 Deepak Bhole <dbhole@redhat.com> 1.0-0.1.a34.0jpp.1
- Initial build with original base spec from JPackage
