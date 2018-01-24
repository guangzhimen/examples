Name:           apache
Version:        9.9.9 
Release:        axon%{?dist}
Summary:        http for axon

License:        axon
URL:            http://axon.com.cn
#Source0:        pcre-8.40.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root

%description


%prep
tar -zxvf /root/rpmbuild/SOURCES/pcre-8.40.tar.gz -C /root/rpmbuild/BUILD
tar -zxvf /root/rpmbuild/SOURCES/httpd-2.2.32.tar.gz -C /root/rpmbuild/BUILD
%build
cd /root/rpmbuild/BUILD/pcre-8.40
./configure --prefix=/usr/loacl/pcre
cd /root/rpmbuild/BUILD/httpd-2.2.32
./configure --prefix=/apps/usr/apache  --sysconfdir=/apps/usr/apache/httpd --enable-so --enable-cgi --enable-ssl --enable-rewrite --with-pcre=/usr/local/pcre  --with-z=/usr/lib64 --with-included-apr  --enable-modules=most --enable-mpms-shared=all --with-mpm=event
make

%install
rm -rf $RPM_BUILD_ROOT
cd /root/rpmbuild/BUILD/httpd-2.2.32
make DESTDIR=$RPM_BUILD_ROOT install
install -D -m 0755 /root/rpmbuild/SOURCES/apache $RPM_BUILD_ROOT/etc/init.d/apache
install -D -m 0755 /root/rpmbuild/SOURCES/apache.service $RPM_BUILD_ROOT/lib/systemd/system/apache.service
%post
echo "/apps/usr/apache/bin/apachectl -f /apps/usr/apache/httpd/httpd.conf" >> /etc/rc.d/rc.local
chmod 755 /etc/rc.d/rc.local
if [ `cat /etc/passwd |grep apache |wc -l` -eq 0 ]; then
	useradd -d /apps/usr/www apache
else
	mkdir -p /apps/usr/www
	usermod -d /apps/usr/www apache
fi

%clean
rm -rf $RPM_BUILD_ROOT
#make clean

%files
#%defattr (-,root,root)
/apps/usr/apache/
/apps/usr/apache/httpd
%config(noreplace) /apps/usr/apache/httpd/httpd.conf
/etc/init.d/apache
/lib/systemd/system/apache.service


%changelog
