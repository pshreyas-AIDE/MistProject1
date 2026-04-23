import re
import itertools
import json
from library.jira_integrator import *
from library.s3_library import *
import difflib



def grouping(commands,mac_wise_commands):
    # parent_child ->      key ( parent_word, child_word ) Value = Middle    eg :   set vlans vlan_id 10    ----> { (set,vlan_id) : vlans }
    parent_child = {}

    # token_dict  ->      key ( parent_word, child_word ) Value = Unique_token  eg :   set vlans vlan_id 10    ----> { (set,vlan_id) : $RENAME_TOKEN$1 }
    token_dict = {}

    # Took some random string to get tokens
    token = "$RENAME_TOKEN$"

    # token_content ->      key ( token_name ) Value = Middle    eg :   set vlans vlan_id 10    ----> { $RENAME_TOKEN$1 : vlans }
    token_content = {}

    # This is count appended to token to get new unique token for unique (parent,child) combo
    token_count = 0

    # Iterate over all commands in list and populate above variables as per description - parent_child, token_dict, token_content
    for command in commands:
        command_split = command.split(" ")
        for ind in range(len(command_split)):
            if (ind - 1 < 0):
                parent = None
            else:
                parent = command_split[ind - 1]
            if (ind + 1 >= len(command_split)):
                child = None
            else:
                child = command_split[ind + 1]
            if ((parent, child) not in parent_child):

                parent_child[(parent, child)] = [command_split[ind]]
            else:
                parent_child[(parent, child)].append(command_split[ind])
            if ((parent, child) not in token_dict):
                token_dict[(parent, child)] = token + str(token_count)
                token_content[token_dict[(parent, child)]] = [command_split[ind]]
                token_count += 1
            else:
                if (command_split[ind] not in token_content[token_dict[(parent, child)]]):
                    token_content[token_dict[(parent, child)]].append(command_split[ind])

    # Replace with Token i.e for each command in list , instead of word replace with token
    # eg : set vlans vlan_id 10    ----> [ $RENAME_TOKEN$1 $RENAME_TOKEN$2 $RENAME_TOKEN$3 $RENAME_TOKEN$4 ]
    new_command_list = []
    for command in commands:
        command_split = command.split(" ")
        new_command = []
        for ind in range(len(command_split)):
            if (ind - 1 < 0):
                parent = None
            else:
                parent = command_split[ind - 1]
            if (ind + 1 >= len(command_split)):
                child = None
            else:
                child = command_split[ind + 1]
            new_command.append(token_dict[(parent, child)])
        new_command_list.append(new_command)

    # For the same above commands make it set so that no repetitions are present
    # eg : set vlans vlan_id 10    ----> $RENAME_TOKEN$1 $RENAME_TOKEN$2 $RENAME_TOKEN$3 $RENAME_TOKEN$4
    token_command_set = set()
    for i in new_command_list:
        command = " ".join(i)
        token_command_set.add(command)

    # Generate res dict of below format
    # eg : $RENAME_TOKEN$1 $RENAME_TOKEN$2 $RENAME_TOKEN$3 $RENAME_TOKEN$4 ---> ,set ,vlans ,vlan_id,vni_id ,10,20,30,40
    # i.e each token can be mapped to more than 1 words because these words might have same parent and child eg: 10,20,30,40
    res = {}
    for i in token_command_set:
        new = ""
        for j in i.split(" "):
            new += ",".join(token_content[j]) + " "
        res[new] = 1

    def print_grouped_configs(str_list, res, ind, group):
        # ( ,set ,vlans ,vlan_id,vni_id ,10,20,30,40     , ""    , 0 )
        # "" is the set command
        # 0 - index of the nth word in the set command
        # Base condition is when ind is length of str_list - meaning the whole set command generation is complete
        # res_final - just removed the extra " " which was present
        if (ind >= len(str_list)):
            res_final = res[:len(res) - 2]
            # If the new command formed is in the json commands we add it to group and write to file
            if (res_final in commands_all):
                if (res_final not in grouped_commands):
                    # print(group)
                    command_group_mapping[res_final] = group
                    grouped_commands[res_final] = 1
                    #f.write(res + '\n')
            return

        # if ind<len(str_list) then it means whole command is not formed yet
        # Now spilt the words by ,
        # eg : if ind = 3
        # ,10,20,30,40 is split to [10,20,30,40]
        # Each element in list is appened to set command string and recursion is done with ind + 1 since ind th word in set command we added
        for i in str_list[ind].split(","):
            print_grouped_configs(str_list, res + i + " ", ind + 1, group)

    count = 1
    # List search is taking O(N) hence making this as hash function for faster search in print_grouped_configs function
    # i.e commands is of type list and search for this takes O(n)
    # Below code makes commands_all of type dict for which time is O(1)
    commands_all = {}
    # Dict with key = Command and Value = 1 - To indicate that this command is already visited and present as part of some group
    grouped_commands = {}
    # Dict with key = Command and Value = group number - To indicate that this command is part of that group
    command_group_mapping = {}
    for command in commands:
        commands_all[command] = 1

    # The lenghth of res keys is the number of unique groups present
    # Well be passing this which is in form of token to print out the actual command
    # i.e print_grouped_configs converts token format code to set command code
    for i in res:
        #f.write("Group " + str(count) + "\n")

        # ( ,set ,vlans ,vlan_id,vni_id ,10,20,30,40      , ""    , 0 )
        print_grouped_configs(i.split(" "), "", 0, str(count))
        count += 1
        #f.write("\n")
        #f.write("\n")

    # Commands which are not present in any group , just for reassurence checking if some commands did not get mapped to any group
    #f.write("Group " + " Excluded from any groups " + "\n")

    for command in commands_all:
        if (command not in grouped_commands):
            pass
            #f.write(command)
    #f.write("\n")
    #f.write("\n")

    # Now try merging groups
    # For each device set commands , store the group to which it belongs
    '''
    eg : 
    "5886700a5200": {
        "model": "EX4400-48MP",
        "added_config": [
            "set protocols l2-learning global-mac-ip-snooping"
        ],
        "removed_config": []
    }

    if set protocols l2-learning global-mac-ip-snooping is in group 1

    device_group_set(5886700a5200) = {group 1, ...}
    '''
    # print(command_group_mapping.values())
    device_group_set = {}
    for command_iterate in commands:
        mac_list_with_command = mac_wise_commands[command_iterate]
        for mac in mac_list_with_command:
            if (mac not in device_group_set):
                device_group_set[mac] = [command_group_mapping[command_iterate]]
            else:
                if (command_group_mapping[command_iterate] not in device_group_set[mac]):
                    device_group_set[mac].append(command_group_mapping[command_iterate])

    temp_list = {}
    for mac in device_group_set:
        g = tuple(sorted(device_group_set[mac]))
        if (g not in temp_list):
            temp_list[g] = [mac]
        else:
            temp_list[g].append(mac)
    return temp_list, command_group_mapping

class Diff_Analyzer:

    def __init__(self):
        self.create_jira_object()
        self.create_s3_storage()

    def create_jira_object(self):
        server_url = "https://mistsys.atlassian.net/"
        jira_email = os.environ.get("jira_email_id")
        jjir_token = os.environ.get("jira_token")

        self.jira_obj = JiraToolkit(server_url, jira_email, jjir_token)

    def create_s3_storage(self):

        schema_name=os.environ.get("s3_schema_name")
        self.s3_object = S3StorageManager(schema_name)

    def get_related_jira(self,mac_payload):
        commands_all=[]
        if("added_config" in mac_payload):
            commands_all.extend(mac_payload["added_config"])
        if("removed_config" in mac_payload):
            commands_all.extend(mac_payload["removed_config"])
        if("add_error" in mac_payload):
            commands_all.extend(mac_payload["add_error"])
        if("remove_error" in mac_payload):
            commands_all.extend(mac_payload["remove_error"])
        related_jira=[]
        for command in commands_all:
            try :
                jiras=self.jira_obj.search_by_keyword("MIST",command)
                if(type(jiras)==list):
                    related_jira.extend(jiras)
                else:
                    related_jira.extend(jiras.keys())
            except:
                pass
        return related_jira

    def get_create_jira_contents(self,mac_payload,mac_id):


        env=os.environ.get("env_id")
        papi_pilot=f"Papi Pilot Version = {os.environ.get("papi_pilot_version")}"
        papi_internal=f"Papi internal Version = {os.environ.get("papi_internal_version")}"

        type = "BUG"
        issues=self.get_related_jira(mac_payload)
        related_jira = "\n".join(issues)

        assigne=os.environ.get("jira_assigne")
        title=f"[Papi Diff - {papi_pilot}  {papi_internal}] "

        step1=f'1. Versions\n{papi_pilot}\n{papi_internal}\n\n'
        step2=f'2. Envs\n{env}\n\n'
        step3=f'3. Sample diff\n{json.dumps(mac_payload, indent=4)}\n\n'
        step4=f'4. Internal APIs :\npapi-pilot : http://papi-pilot-{env}.mist.pvt/internal/devices/{mac_id}/config_with_qs\npapi-pilot : http://papi-pilot-{env}.mist.pvt/internal/devices/{mac_id}/config_with_qs\n\n'
        step5=f'5. Related Jiras :\n{related_jira}\n\n'
        step6=f'6: Conclusion :\n\n\n'

        description=step1+step2+step3+step4+step5+step6

        return [type,assigne,title,description]
    def analyze_diff(self,file_name):

        mac_wise_commands_added = {}
        mac_wise_commands_removed = {}
        mac_wise_error_added = {}
        mac_wise_error_removed = {}

        # These are keys which needs to be ignored while we are analysing / doing grouping since these keys are variable
        exclude_keys = {
            'papi_pilot_version': 1,
            'papi_internal_version': 1,
            'Environment': 1,
            'devices selection aproach': 1,
            'unique_commands_added_overall': 1,
            'unique_commands_removed_overall': 1,
            'ignored device macs': 1
        }
        diff_list_added = []
        diff_list_removed = []
        error_list_added = []
        error_list_removed = []

        # Opening the Papi Diff Jspm file and parsing it into Dictionary object
        # with open(file_name) as json_file:
        #     payload = json.load(json_file)
        payload=self.s3_object.get_data(file_name)
        if(payload==None):
            print("S3 Storage file for the below version is not present and cant be analyzed")
        else:
            print("Starting analysis")
        # Return list of all the
        # diff commands added - diff_list_added
        # diff commands removed - diff_list_removed
        # diff commands error added - error_list_added
        # diff commands error removed - error_list_removed
        # mac_wise_commands Dict where - Key = Command ( either added / removed / error_added / error_removed ) and Value = Mac Id
        for mac in payload:
            if (mac in exclude_keys):
                continue
            if (type(payload[mac]) == int):
                continue
            # print(mac,payload[mac])
            if ('added_config' in payload[mac]):
                for added in payload[mac]['added_config']:
                    if (added not in mac_wise_commands_added):
                        mac_wise_commands_added[added] = [mac]
                    else:
                        mac_wise_commands_added[added].append(mac)
                    diff_list_added.append(added)
            if ('removed_config' in payload[mac]):
                for added in payload[mac]['removed_config']:
                    if (added not in mac_wise_commands_removed):
                        mac_wise_commands_removed[added] = [mac]
                    else:
                        mac_wise_commands_removed[added].append(mac)
                    diff_list_removed.append(added)
            if ('add_error' in payload[mac]):
                for added in payload[mac]['add_error']:
                    if (added not in mac_wise_error_added):
                        mac_wise_error_added[added] = [mac]
                    else:
                        mac_wise_error_added[added].append(mac)
                    error_list_added.append(added)
            if ('remove_error' in payload[mac]):
                for added in payload[mac]['remove_error']:
                    if (added not in mac_wise_error_removed):
                        mac_wise_error_removed[added] = [mac]
                    else:
                        mac_wise_error_removed[added].append(mac)
                    error_list_removed.append(added)

        # Call grouping to make groups for respective partitions and store it to file name mentioned

        # For added config group
        added_summary_grouping, added_grouped_config_mapping = grouping(diff_list_added,mac_wise_commands_added)

        # Key Group A1 , Value - List of all commands in group eg { A1 : ['set interfaces interface-range default member mge-1/0/40', 'set interfaces interface-range default member mge-1/0/42', 'set interfaces interface-range default member mge-1/0/45', 'set interfaces interface-range default member mge-1/0/[26-32] ]
        added_commands_per_group = {}
        for command in added_grouped_config_mapping:
            if ("A" + str(added_grouped_config_mapping[command]) not in added_commands_per_group):
                added_commands_per_group["A" + str(added_grouped_config_mapping[command])] = [command]
            else:
                added_commands_per_group["A" + str(added_grouped_config_mapping[command])].append(command)
            added_grouped_config_mapping[command] = "A" + str(added_grouped_config_mapping[command])

        # For removed config group
        removed_summary_grouping, removed_grouped_config_mapping = grouping(diff_list_removed,mac_wise_commands_removed)

        # Key Group A1 , Value - List of all commands in group eg { A1 : ['set interfaces interface-range default member mge-1/0/40', 'set interfaces interface-range default member mge-1/0/42', 'set interfaces interface-range default member mge-1/0/45', 'set interfaces interface-range default member mge-1/0/[26-32] ]
        removed_commands_per_group = {}
        for command in removed_grouped_config_mapping:
            if ("R" + str(removed_grouped_config_mapping[command]) not in removed_commands_per_group):
                removed_commands_per_group["R" + str(removed_grouped_config_mapping[command])] = [command]
            else:
                removed_commands_per_group["R" + str(removed_grouped_config_mapping[command])].append(command)
            removed_grouped_config_mapping[command] = "R" + str(removed_grouped_config_mapping[command])

        # New Summary Optimization Code
        # Store the mac neighbors of added configs and removed configs for each mac
        '''
        eg : ('3', '3', '3', '3', '3'): ['00cc34b0c283','00cc34b0c2aa']
        added_config_neighbor[00cc34b0c283]=[00cc34b0c2aa]

        '''
        added_config_neighbor = {}
        removed_config_neighbor = {}
        for group_tuple in added_summary_grouping:
            for mac in added_summary_grouping[group_tuple]:
                mac_list_set = set(added_summary_grouping[group_tuple])
                added_config_neighbor[mac] = mac_list_set.difference(set(mac))

        for group_tuple in removed_summary_grouping:
            for mac in removed_summary_grouping[group_tuple]:
                mac_list_set = set(removed_summary_grouping[group_tuple])
                removed_config_neighbor[mac] = mac_list_set.difference(set(mac))

        # For added error group
        # f = open(file_name + "- newly_added_error", "w")
        f = open( "newly_added_error", "w")
        f.write("Newly Added Error\n")
        for error in error_list_added:
            f.write(error + "\n")

        # For removed error group
        # f = open(file_name + "- newly_removed_error", "w")
        f = open("newly_removed_error", "w")
        f.write("Newly Added Removed\n")
        for error in error_list_removed:
            f.write(error + "\n")


        # Combining Added and Removed summary -

        added_removed_parent = {} # Key [Added_group_tuple, Removed_group_tuple] , Value - List of all macs with this mapping
        mac_added_removed_parent = {} # Key Mac , Value [Added_group_tuple, Removed_group_tuple]

        for i in added_summary_grouping:

            for mac in added_summary_grouping[i]:

                if (mac not in mac_added_removed_parent):
                    mac_added_removed_parent[mac] = [(), ()]
                mac_added_removed_parent[mac][0] = i
        for i in removed_summary_grouping:

            for mac in removed_summary_grouping[i]:
                if (mac not in mac_added_removed_parent):
                    mac_added_removed_parent[mac] = [(), ()]
                mac_added_removed_parent[mac][1] = i

        for mac in mac_added_removed_parent:
            if (tuple(mac_added_removed_parent[mac]) not in added_removed_parent):
                added_removed_parent[tuple(mac_added_removed_parent[mac])] = []
            added_removed_parent[tuple(mac_added_removed_parent[mac])].append(mac)

        f = open("Consolidated_analysis_file", "w")
        f.write("Consolidated Grouping Analysis \n\n\n")
        group_subgroup_mapping_with_command_added = {}  # key - Command   Value [ (added_group,added_subgroup), (removed_group,removed_subgroup)]
        group_subgroup_mapping_with_command_removed = {} # key - Command   Value [ (added_group,added_subgroup), (removed_group,removed_subgroup)]

        # This is to make a list of all commands which are part of any group so that we dont miss any commands
        commands_visited_added = {}
        commands_visited_removed = {}

        group_count = 1
        for i in sorted(added_removed_parent.keys()):
            f.write("\n Group : " + str(group_count) + "\n")
            f.write(" Mac List :" + ",".join(added_removed_parent[i]) + "\n\n")
            f.write("\tAdded configs list : \n")
            subgroup_count_added = 1
            for added in i[0]:
                sample_command_for_subgroup = added_commands_per_group["A" + str(added)][0]
                if (sample_command_for_subgroup not in group_subgroup_mapping_with_command_added):
                    f.write("\t\t\t\t" + "Subgroup : " + str(
                        subgroup_count_added) + " ------> " + sample_command_for_subgroup + "\n\t\t\t\t\t\t Status - Pending analysis \n\n")
                else:
                    f.write("\t\t\t\t" + "Subgroup : " + str(
                        subgroup_count_added) + " ------> " + sample_command_for_subgroup + "\n\t\t\t\t\t\t Status - Already Analyzed as Part of Group: " +
                            group_subgroup_mapping_with_command_added[sample_command_for_subgroup][0][
                                0] + "  Subgroup: " +
                            group_subgroup_mapping_with_command_added[sample_command_for_subgroup][0][
                                1] + "\n\n")


                for added_command in added_commands_per_group["A" + str(added)]:
                    commands_visited_added[added_command] = 1
                    if (added_command not in group_subgroup_mapping_with_command_added):
                        group_subgroup_mapping_with_command_added[added_command] = [["", ""]]
                    group_subgroup_mapping_with_command_added[added_command][0][0] = str(group_count)
                    group_subgroup_mapping_with_command_added[added_command][0][1] = str(subgroup_count_added)
                f.write("")
                subgroup_count_added += 1

            f.write("\n\n\tRemoved configs list : \n")
            subgroup_count_removed = 1
            for removed in i[1]:
                sample_command_for_subgroup = removed_commands_per_group["R" + str(removed)][0]
                if (sample_command_for_subgroup not in group_subgroup_mapping_with_command_removed):
                    f.write("\t\t\t\t" + "Subgroup : " + str(
                        subgroup_count_removed) + " ------> " + sample_command_for_subgroup + "\n\t\t\t\t\t\t Status - Pending analysis \n\n")
                else:
                    f.write("\t\t\t\t" + "Subgroup : " + str(
                        subgroup_count_added) + " ------> " + sample_command_for_subgroup + "\n\t\t\t\t\t\t Status - Already Analyzed as Part of Group: " +
                            group_subgroup_mapping_with_command_removed[sample_command_for_subgroup][0][
                                0] + "  Subgroup: " +
                            group_subgroup_mapping_with_command_removed[sample_command_for_subgroup][0][
                                1] + "\n\n")
                for removed_command in removed_commands_per_group["R" + str(removed)]:
                    commands_visited_removed[removed_command] = 1
                    if (removed_command not in group_subgroup_mapping_with_command_removed):
                        group_subgroup_mapping_with_command_removed[removed_command] = [["", ""]]
                    group_subgroup_mapping_with_command_removed[removed_command][0][0] = str(group_count)
                    group_subgroup_mapping_with_command_removed[removed_command][0][1] = str(subgroup_count_removed)
                f.write("")
                subgroup_count_removed += 1

            mac_id = added_removed_parent[i][0]
            jira_creation_data = self.get_create_jira_contents(payload[mac_id], mac_id)
            f.write("\n Jira Creation Objects \n\n")
            f.write(f"Type : {jira_creation_data[0]}\n")
            f.write(f"Assigne : {jira_creation_data[1]}\n")
            f.write(f"Title : {jira_creation_data[2]}\n")
            f.write(f"Description : \n{jira_creation_data[3]}\n\n")

            f.write("$$"*30)

            group_count += 1




        # The below snippet is to make sure we are not missing any of the commands in file and we are adding all commands in file to some group
        # Here diff_list_added is all added commands taken from original Json file
        # commands_visited_added - Is calculated when we are parsing the groups, all commands belonging to group is added to this
        # Similarly to commands_visited_removed and diff_list_removed

        f.write("\n" + "\n" + "*" * 30)
        f.write("\n\nCommands added belonging to no group : \n")
        for commands in set(diff_list_added).difference(set(commands_visited_added)):
            f.write(commands + "\n")
        f.write("\n\nCommands belonging to group but not in added configs : \n")
        for commands in set(commands_visited_added).difference(set(diff_list_added)):
            f.write(commands + "\n")
        f.write("\n" + "\n" + "*" * 30)

        f.write("\n" + "\n" + "*" * 30)
        f.write("\n\nCommands removed belonging to no group : \n")
        for commands in set(diff_list_removed).difference(set(commands_visited_removed)):
            f.write(commands + "\n")
        f.write("\n\nCommands belonging to group but not in removed configs : \n")
        for commands in set(commands_visited_removed).difference(set(commands_visited_removed)):
            f.write(commands + "\n")
        f.write("\n" + "\n" + "*" * 30)


        analyzed_result={}
        analyzed_result["diff_list_added"]=diff_list_added   # List of all added commands
        analyzed_result["diff_list_removed"]=diff_list_removed # List of all removed commands
        analyzed_result["added_summary_grouping"]=added_summary_grouping # Key Tuples ( Group number ), Value - All macs belonging to group eg : { ('1',) : ['408f9dc8e256', '68f38efbd468', '04698ffaeba8'] )
        analyzed_result["removed_summary_grouping"]=removed_summary_grouping # Key Tuples ( Group number ), Value - All macs belonging to group eg : { ('1',) : ['408f9dc8e256', '68f38efbd468', '04698ffaeba8'] )
        analyzed_result["added_grouped_config_mapping"]=added_grouped_config_mapping # Dict with key = Command and Value = group number - eg : { set interfaces interface-range default member mge-1/0/40 : A1}
        analyzed_result["removed_grouped_config_mapping"]=removed_grouped_config_mapping # Dict with key = Command and Value = group number - eg : { set interfaces interface-range default member mge-1/0/40 : A1}
        analyzed_result["added_commands_per_group"]=added_commands_per_group # Key Group A1 , Value - List of all commands in group eg { A1 : ['set interfaces interface-range default member mge-1/0/40', 'set interfaces interface-range default member mge-1/0/42', 'set interfaces interface-range default member mge-1/0/45', 'set interfaces interface-range default member mge-1/0/[26-32] ]
        analyzed_result["removed_commands_per_group"]=removed_commands_per_group # Key Group A1 , Value - List of all commands in group eg { A1 : ['set interfaces interface-range default member mge-1/0/40', 'set interfaces interface-range default member mge-1/0/42', 'set interfaces interface-range default member mge-1/0/45', 'set interfaces interface-range default member mge-1/0/[26-32] ]
        analyzed_result["mac_wise_commands_added"]=mac_wise_commands_added # key Command , Value - List of macs which have these commands eg set interfaces interface-range default member mge-1/0/40 ['408f9dc8e256', '68f38efbd468', '04698ffaeba8', '4c734f490b28', '0c8126b712a2', 'ec94d5dc93a0']
        analyzed_result["mac_wise_commands_removed"]=mac_wise_commands_removed # key Command , Value - List of macs which have these commands eg set interfaces interface-range default member mge-1/0/40 ['408f9dc8e256', '68f38efbd468', '04698ffaeba8', '4c734f490b28', '0c8126b712a2', 'ec94d5dc93a0']
        return analyzed_result



obj=Diff_Analyzer()
file_name=os.environ['env_id']+"/"+os.environ['papi_pilot_version']+"|"+os.environ['papi_internal_version']+"/papi_config_compare_data_switch_euwe1prod3.json"

res=obj.analyze_diff(file_name=file_name)
