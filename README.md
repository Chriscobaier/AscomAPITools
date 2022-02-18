### NOTE THIS HAS ONLY BEEN TESTED ON UPS 4.14 - this uses StaffSearch API which was introduced in this version. Other versions should work - will need to verify
This AutoBadge exe is used to import a csv file through the Unite API and assign the badge to a user that matches the name in the CSV file.

Requires you to update the appsettings within quotes like the examples in the .json

   "UniteFQDN":"Enter FQDN of UPS Server Here"
   
   "BadgeCSVFile":"Enter badgefile.csv (with .csv)"
   
   "UniteUserName(admin)":"admin username"
   
   "UnitePassword":"password for admin"
   "BadgesOnly" defaults to "False".  Setting this to "True" will only read the first item in the badges.csv
   file which should be the badgeID.
