FROM --platform=linux/amd64 ubuntu:latest
# platform set b/c odbc-mariadb is not available for arm64

# Install slapd
RUN apt-get -y update
RUN LC_ALL=C DEBIAN_FRONTEND=noninteractive apt-get install -y slapd odbc-mariadb

# netcat & wait-for-it
RUN LC_ALL=C DEBIAN_FRONTEND=noninteractive apt-get install -y netcat
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /wait-for-it.sh
RUN chmod 0755 /wait-for-it.sh

RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# empty the default configuration
RUN rm -rf /etc/ldap/slapd.d /var/lib/ldap
RUN mkdir /etc/ldap/slapd.d /var/lib/ldap

# add ODBC config file
ADD odbc.ini /etc/

# prepare new config
RUN chown -R openldap.openldap /etc/ldap/slapd.d /var/lib/ldap

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

