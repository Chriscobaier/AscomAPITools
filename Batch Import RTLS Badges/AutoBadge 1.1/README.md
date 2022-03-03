### NOTE THIS HAS ONLY BEEN TESTED ON UPS 4.14 - this uses StaffSearch API which was introduced in this version. Newer versions should work - will need to verify
### Use RTLS Badge CSV Creator (Credit- Sean Fisher) to assist in creating badge csv file
This AutoBadge exe is used to import a csv file through the Unite API and assign the badge to a user that matches the name in the CSV file.

Requires you to update the appsettings within quotes like the examples in the .json

   "UniteFQDN":"Enter FQDN of UPS Server Here"
   
   "BadgeCSVFile":"Enter badgefile.csv (with .csv)"
   
   "UniteUserName(admin)":"admin username"
   
   "UnitePassword":"password for admin"
   
   
   "BadgesOnly" defaults to "False".  This will determine if the program should try to associate the badges with a Unite User in the system.  Having this set to True will only import the badges into the system, with no user association. 
