--
-- Drop column prefLang from view
--

UPDATE `ldap_attr_mappings` SET `from_tbls` = 'ldap_contacts' WHERE `id` = 0;

ALTER DEFINER=`admin`@`%` SQL SECURITY INVOKER VIEW `ldap_contacts` AS select if(`contact_organisation`.`oid` is null,0,`contact_organisation`.`oid` * 100000) + `contact`.`cid` AS `id`,`contact`.`firstName` AS `firstName`,`contact`.`lastName` AS `lastName`,`contact`.`person` AS `person`,if(`organisation`.`oid` is null,`contact`.`person`,concat(`contact`.`person`,'',' (',if(`organisation`.`acronym` is null,`organisation`.`longname`,`organisation`.`acronym`),')')) AS `nameOrganisation`,`contact_organisation`.`function` AS `function`,`organisation`.`alt_name` AS `organisation`,`contact`.`nameEmail` AS `nameEmail`,`contact`.`email` AS `email`,`contact`.`phone` AS `phone`,`contact`.`mobile` AS `mobile`,`contact`.`brussels` AS `brussels`,`contact`.`postal` AS `postal`,`contact`.`addressExtension` AS `addressExtension`,if(octet_length(`contact`.`address1`) > 0,`contact`.`address1`,`organisation`.`address1`) AS `address1`,if(octet_length(`contact`.`address2`) > 0,`contact`.`address2`,`organisation`.`address2`) AS `address2`,if(octet_length(`contact`.`postcode`) > 0,`contact`.`postcode`,`organisation`.`postcode`) AS `postcode`,if(octet_length(`contact`.`city`) > 0,`contact`.`city`,`organisation`.`city`) AS `city`,`country`.`name` AS `country` from (((`contact` left join `contact_organisation` on(`contact`.`cid` = `contact_organisation`.`cid`)) left join `organisation` on(`contact_organisation`.`oid` = `organisation`.`oid`)) left join `country` on(`country`.`iso2` = coalesce(`contact`.`country`, `organisation`.`country`)));

