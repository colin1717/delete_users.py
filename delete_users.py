#This script expects your Box App settings information saved in a file in this folder called config.json.  
#You can get this file from your App's configuraiton settings in the Box dev console -  "Add and manage public keys"
#Application Access for the App needs to be set to "Enterprise"
#Advanced Features: "Perfom actions as users" should be enabled. 
#This app will need to be authorized by an admin under Enterprise settings > Apps

# Install SDK via pip
# $ pip install boxsdk

# Install JWT auth SDK
# $pip install boxsdk[jwt]

from boxsdk import JWTAuth
from boxsdk import Client
from boxsdk.exception import BoxAPIException
import csv

#configure JWT auth object
sdk = JWTAuth.from_settings_file("./config.json")
client = Client(sdk)

############################################################
#edit delete_group_name below
############################################################

#define group to delete
delete_group_name = "Test"


##############################################################
#Edit delete_group_name above
##############################################################

#color definition
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

############################################################
#start logic
############################################################

#get list of groups from Box and search for a group with a matching name. 
delete_group_id = None

groups = client.get_groups()
group_exists = False

for group in groups:
	if group.name == delete_group_name:
		delete_group_id = group.id
		group_exists = True
		print(bcolors.WARNING + "Group to delete has been found: Group '{0}' has ID {1}".format(delete_group_name, delete_group_id) + bcolors.ENDC)
	

if group_exists == False:
	print(bcolors.FAIL + "\n A group matching the name {0} could not be found \n".format(delete_group_name) + bcolors.ENDC) 
	exit()


#get memebers of group
delete_group_members = client.group(group_id=delete_group_id).get_memberships()

print(delete_group_members)

delete_group_members_size = 0
users_to_delete = {}

for membership in delete_group_members:
	print("{0} is a {1} of the {2} group. User ID: {3}".format(membership.user.login, membership.role, membership.group.name, membership.user.id))
	delete_group_members_size += 1
	users_to_delete[membership.user.login] = membership.user.id


#print warnign of users that will be deteled.  require user input to move forward. 
print("Box group {0} has {1} members".format(delete_group_name, delete_group_members_size))
print(bcolors.FAIL + "!!!!!!!!!!!!!!!!! THIS CAN NOT BE UNDONE !!!!!!!!!!!!!!!!!!!!!" + bcolors.ENDC)
print(bcolors.WARNING + '=========================================================== \nTo proceed with deleting all {0} members of Box groups {1}: Type "DELETE" and press return. \nTyping anything else and pressing return will abort. \n==========================================================='.format(delete_group_members_size, delete_group_name) + bcolors.ENDC)

confirmation = input()

if confirmation == "DELETE":
	print("were deleting here")
else:
	print(bcolors.OKBLUE + "Delete users script aborted" + bcolors.ENDC)
	exit()


#create csv of deleted user info
with open('deleted_users.csv', 'w', newline='') as output:
	csv_writer = csv.writer(output)

	csv_writer.writerow(["Email", "BOX ID"])

	print(delete_group_members)

	for user_to_delete in users_to_delete:
		csv_writer.writerow([user_to_delete, users_to_delete[user_to_delete]])


#delete users
print("deleting for real")
for user in users_to_delete:
	print("email {0}, id: {1}".format(user, users_to_delete[user]))



