from django.db import models

"""
LDAP view: models controlling slapd with back_sql access to this database
"""

class LdapEntryObjclasses(models.Model):
    entry_id = models.IntegerField(primary_key=True)
    oc_name = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        db_table = 'ldap_entry_objclasses'


class LdapOcMappings(models.Model):
    name = models.CharField(max_length=64)
    keytbl = models.CharField(max_length=64)
    keycol = models.CharField(max_length=64)
    create_proc = models.CharField(max_length=255, blank=True, null=True)
    delete_proc = models.CharField(max_length=255, blank=True, null=True)
    expect_return = models.IntegerField()

    class Meta:
        db_table = 'ldap_oc_mappings'
        ordering = [ 'name' ]

    def __str__(self):
        return('{} ({})'.format(self.name, self.keytbl))


class LdapAttrMappings(models.Model):
    object_class = models.ForeignKey(LdapOcMappings, on_delete=models.RESTRICT, db_column='oc_map_id')
    name = models.CharField(max_length=255)
    sel_expr = models.CharField(max_length=255)
    sel_expr_u = models.CharField(max_length=255, blank=True, null=True)
    from_tbls = models.CharField(max_length=255)
    join_where = models.CharField(max_length=255, blank=True, null=True)
    add_proc = models.CharField(max_length=255, blank=True, null=True)
    delete_proc = models.CharField(max_length=255, blank=True, null=True)
    param_order = models.IntegerField()
    expect_return = models.IntegerField()

    class Meta:
        db_table = 'ldap_attr_mappings'
        ordering = [ 'name' ]

    def __str__(self):
        return('{}.{}'.format(self.object_class, self.name))


class LdapReferrals(models.Model):
    entry_id = models.BigIntegerField(primary_key=True)
    url = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'ldap_referrals'

