FROM --platform=linux/amd64 ubuntu:latest
# platform set b/c odbc-mariadb is not available for arm64

# Install slapd & netcat, empty the default configuration
RUN apt-get -y update && \
	echo "slapd slapd/no_configuration boolean true" | debconf-set-selections && \
	apt-get install -y slapd odbc-mariadb netcat && \
	apt-get clean && \
	rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* && \
	rm -rf /etc/ldap/slapd.d /var/lib/ldap

# add wait-for-it
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /wait-for-it.sh
RUN chmod 0755 /wait-for-it.sh

# add ODBC config file
ADD odbc.ini /etc/

# prepare new config
RUN mkdir -p /etc/ldap/slapd.d /var/lib/ldap /var/run/slapd && \
	chown -R openldap.openldap /etc/ldap/slapd.d /var/lib/ldap /var/run/slapd

USER openldap:openldap

RUN mkdir -p /tmp/ldap-config/add-schema

ADD --chown=openldap:openldap config.ldif /tmp/ldap-config
ADD --chown=openldap:openldap add-schema /tmp/ldap-config/add-schema

# bootstrap from config.ldif
RUN slapadd -n0 -F /etc/ldap/slapd.d -l /tmp/ldap-config/config.ldif || true

# add schema
ARG LDAP_SCHEMA="core cosine nis inetorgperson"
RUN for i in ${LDAP_SCHEMA} ; do slapadd -n0 -F /etc/ldap/slapd.d -l /etc/ldap/schema/${i}.ldif || true ; done
RUN for i in /tmp/ldap-config/add-schema/*.ldif ; do slapadd -n0 -F /etc/ldap/slapd.d -l ${i} || true ; done

RUN rm -rf /tmp/ldap-config

EXPOSE 389

CMD [ "/usr/sbin/slapd", "-d", "320" ]

