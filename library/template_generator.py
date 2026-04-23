from collections import deque
import json
import hashlib # To get unique Token name which will not be used in payload
import ast
from boto3.dynamodb.types import LIST

from library.s3_library import S3StorageManager
from library.postgresql import *
import os
import math

empty_parent_or_empty_child_hash_value="@#$%^&*(Empty Empty Empty)*"
f=open("new.json","w")
# use Cosine similarity to find top 10% of words which are similar - Import library as below
# Will be used in one single method
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class SentenceNode:
    def __init__(self, word):
        self.word = word
        self.children = {}  # Dictionary mapping word -> SentenceNode




class TokenDatabase(Base):
    __tablename__ = os.environ.get("env_id") + "_token_to_s3_file_table"
    token_id = Column(String, primary_key=True)
    parent_child_value = Column(String)
    s3_file_path=Column(String)


class Build_Splice_tree:

    def __init__(self, payload):
        list_of_sentences = []
        for i in payload:
            mac = payload[i]["mac"]
            l = []
            obj = nested_dict_to_list()
            obj.__iter__(payload[i], l)
            list_of_sentences.extend(obj.list)
        self.create_postgresql_database()
        self.create_s3_storage()
        self.node = self.build_sentence_tree(list_of_sentences)
        self.token_to_node_storage={}    # Key=token_id and value=Node associated with the storage
        self.token_to_word_mapping = self.bfs_and_grouping()
        self.grouping_of_keys_with_same_parent_and_child()


        self.get_all_postgresql_rows()
        vis={}
        self.final_template_sentences={}
        self.dfs(self.node,vis,[],self.final_template_sentences)
        print(len(self.final_template_sentences))
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.generalized_sentences_list=self.get_template()
        self.reverse_engineering()


    def create_postgresql_database(self):
        # If already present with the name - Ignore / Not create Just use same
        # Else create

        # Fixed format
        database_table_name=os.environ.get("env_id")+"_token_to_s3_file_table"
        user_name=os.environ.get("postgresql_username")
        password=os.environ.get("postgresql_password")
        host=os.environ.get("postgresql_host")
        port=os.environ.get("postgresql_port")
        database_schema=os.environ.get("postgresql_schema")

        database_url=f"postgresql://{user_name}:{password}@{host}:{port}/{database_schema}"

        self.postgresql_obj=DatabaseManager(database_url)

        # This is standard format of table
        cols={"token_id": String,"parent_child_value": String,"s3_file_path": String}
        self.postgresql_obj.create_custom_table(database_table_name,cols,primary_key_defined="token_id")
        self.postgresql_obj.session_local()

        # Object is ready to be used to read or write etc

    def create_s3_storage(self):

        schema_name=os.environ.get("s3_schema_name")
        self.s3_object = S3StorageManager(schema_name)

    def build_sentence_tree(self, sentences):
        root = SentenceNode("ROOT")
        for sentence in sentences:
            current = root
            words = sentence
            for word_original in words:
                word = str(word_original)
                if word not in current.children:
                    current.children[word] = SentenceNode(word)
                current = current.children[word]
        return root

    def get_structural_hash(self):
        """
        Creates a fingerprint based ONLY on the identity of children.
        We use the memory address (id) of the children to ensure
        we are checking for the EXACT same objects.
        """
        # 1. Get sorted keys to ensure deterministic hashing
        sorted_keys = sorted(self.node.children.keys())

        # 2. Build a signature: "child_word:memory_address"
        # id(c) is the pointer. If two parents point to the same id, they share a child.
        child_signatures = [f"{w}:{id(self.node.children[w])}" for w in sorted_keys]

        # 3. Join and hash. We exclude node.words from this string!
        data = "|".join(child_signatures)
        return hashlib.md5(data.encode()).hexdigest()

    def get_sentences_dfs(self, node,current_path, results):
        """Traverses the tree using DFS to yield sentences."""
        # If the node is not the root, add its word to the path
        if self.node.word != "ROOT":
            current_path.append(self.node.word)

        # If it's a leaf node (no children), we've found a full sentence
        if not self.node.children:
            # results.append(" ".join(current_path))
            results.append(" ".join(str(current_path)))
        else:
            # Recurse into children
            for child_word in self.node.children:
                self.get_sentences_dfs(self.node.children[child_word], current_path, results)

        # Backtrack: remove the word before going up to explore other branches
        if self.node.word != "ROOT":
            current_path.pop()

    def bfs_and_grouping(self):
        parent_child_relation = {}
        d = deque()
        d.append([self.node, 0, self.node, self.node.children.values()])
        # node,level,parent node,list of child nodes )
        levels = {}
        parent_child_mapping = {}
        while len(d) > 0:

            current = d.popleft()
            parent_child_tuple = (current[2].word, current[1] - 1, tuple(sorted(current[0].children.keys())),
                                  current[1] + 1)
            if (parent_child_tuple not in parent_child_relation):
                parent_child_relation[parent_child_tuple] = [current[0].word]
            else:
                parent_child_relation[parent_child_tuple].append(current[0].word)
            list_of_children = current[0].children.values()
            if (current[1] not in levels):
                levels[current[1]] = [current[0].word]
            else:
                levels[current[1]].append(current[0].word)
            for child in list_of_children:
                d.append([child, current[1] + 1, current[0], child.children.values()])

        # for i in parent_child_relation:
        #     print(i)
        #     print(set(parent_child_relation[i]))
        #     print("##"*10)
        # print("$$$$$$$$"*10)
        # print("ShreyasShreya"*10)
        return parent_child_relation

    def to_hex_key(self, index):
        """Converts 1 to 'c4ca4238a0b923820dcc509a6f75849b'"""
        # Using md5 analysis
        return hashlib.md5(str(index).encode()).hexdigest()

    def grouping_of_keys_with_same_parent_and_child(self):





        # Do BFS traversal
        d = deque()
        d.append([self.node, 0, self.node, self.node.children.values()])
        level_parent_child_list=[]
        while len(d) > 0:
            current = d.popleft()
            list_of_children = current[0].children.values()
            for child in list_of_children:
                d.append([child, current[1] + 1, current[0], child.children.values()])
            if(current[1]>1):
                level_parent_child_list.append([current[1],current[0],current[2],current[3]])
        level_parent_child_list.sort(key=lambda x: x[0],reverse=True)
        for node in level_parent_child_list:
            current_level=node[0]
            current_node = node[1]
            parent_node = node[2]
            child_nodes = current_node.children.values()
            child_node_key=tuple(sorted(current_node.children.keys()))

            # parent_child_tuple = (current[2].word, current[1] - 1, tuple(sorted(current[0].children.keys())),
            #                       current[1] + 1)
            parent_child_representation = (parent_node.word, current_level - 1, child_node_key, current_level + 1)
            token_id = self.to_hex_key(parent_child_representation)
            value = json.dumps(list(parent_child_representation))
            if (token_id not in self.token_to_node_storage):
                new_node = SentenceNode(token_id)
                new_node.children = current_node.children
                self.token_to_node_storage[token_id] = new_node
                if(parent_child_representation not in self.token_to_word_mapping):
                    self.token_to_word_mapping[parent_child_representation]=[current_node.word]
                else:
                    self.token_to_word_mapping[parent_child_representation].append(current_node.word)
            else:
                self.token_to_node_storage[token_id].children = self.token_to_node_storage[
                                                                    token_id].children | current_node.children
            parent_node.children[token_id] = self.token_to_node_storage[token_id]
            if (current_node.word in parent_node.children):
                del parent_node.children[current_node.word]

        # Update the grouped Token to word mapping to database
        for key in self.token_to_word_mapping:
            token_id=self.to_hex_key(key)

            # S3 Update
            s3_file_path=os.environ.get("env_id") + "/token_to_word_mapping/" + token_id + ".jsonl"
            data_present_in_s3 = self.s3_object.get_data(s3_file_path)
            # If None is returned it means it is empty else we need to append
            if (data_present_in_s3):
                for word in self.token_to_word_mapping[key]:
                    if (word not in data_present_in_s3):
                        data_present_in_s3.append(word)
            else:
                data_present_in_s3 = self.token_to_word_mapping[key]
            self.s3_object.upload_data(s3_file_path, json.dumps(data_present_in_s3))


            # Postgresql update
            existing_row = self.postgresql_obj.find_row_by_column("token_id",token_id)
            if (existing_row):
                pass
            else:
                cleaned_value = json.dumps(list(key))
                row_obj = TokenDatabase(
                    token_id=token_id,
                    parent_child_value=cleaned_value,
                    s3_file_path=os.environ.get("env_id") + "/token_to_word_mapping/" + token_id + ".jsonl",
                )
                self.postgresql_obj.add_row(row_obj)





    def dfs(self,node,vis,l,result):
        if(node==None):
            print(l)
            return


        vis[node]=1
        for child in node.children.values():
            if(child not in vis):
                l.append(node)
                self.dfs(child,vis,l,result)
                l.pop()


        if(len(node.children)==0):
            sentence=[]
            for i in l:
                sentence.append(i.word)
            sentence.append(node.word)
            # If last element is a token then we need to add another token
            last_element_token=self.postgresql_obj.find_row_by_column("token_id",sentence[-1])
            if(last_element_token):
                s3_file_path = os.environ.get("env_id") + "/token_to_word_mapping/" + sentence[-1]+ ".jsonl"
                s3_data = self.s3_object.get_data(s3_file_path)
                if (s3_data != None):
                    for word in s3_data:
                        word_for_token=[word,len(sentence)-1,[],len(sentence)+1]
                        cleaned_value=json.dumps(list(word_for_token))
                        if(cleaned_value in self.postgre_sql_mapping):
                            sentence.append(self.postgre_sql_mapping[cleaned_value])

            if(tuple(sentence) not in self.final_template_sentences):
                self.final_template_sentences[tuple(sentence)]=1

    def get_top_10_percent_non_similar_words(self,target_word, word_list):

        # First group it based on database
        # 1. Group by datatype
        database_group = {}
        for word in word_list:
            t = type(word)
            if t not in database_group:
                database_group[t] = []
            database_group[t].append(word)

        top_10_percent = []

        # 2. Process Strings using Cosine Similarity
        if str in database_group:
            model = self.model
            str_list = list(set(database_group[str]))

            # FIX: Ensure target_word is encoded as a 2D array (1, vector_dim)
            # Wrapping it in [target_word] does this automatically
            target_vec = model.encode([str_list[0]])
            list_vecs = model.encode(str_list)

            # Calculate Similarity
            similarities = cosine_similarity(target_vec, list_vecs)[0]

            # Pair strings with scores and sort (Ascending for "non-similar")
            str_score_pairs = list(zip(str_list, similarities))
            str_score_pairs.sort(key=lambda x: x[1])

            # 3. Calculate the 50% cutoff for strings


            # if length of all words > 10 ------------> 10% of the most non-similar words are used
            # else all elements in list of words is selected

            # Ensure we get at least one if the list isn't empty
            if len(str_score_pairs) > 0:
                if(len(str_score_pairs)<=10):
                    cutoff=len(str_score_pairs)
                else:
                    cutoff = math.ceil(len(str_score_pairs) * 0.1)
            top_10_percent= [word for word, score in str_score_pairs[:cutoff]]


        # Add 10 words of each other datatype

        for datatype in database_group:
            if(datatype!=str):
                ind=min(len(database_group[datatype]), 10)  # 10 of each datatype or length if there are no 10 elements
                top_10_percent.extend(database_group[datatype][:ind])
        return top_10_percent

    def get_template(self):
        result = {}
        def recursion(sentence,index,l):
            if(index>=len(sentence)):
                if(sentence not in result):
                    result[sentence]=[l.copy()]
                else:
                    result[sentence].append(l.copy())
                return

            s3_file_path=os.environ.get("env_id") + "/token_to_word_mapping/" + sentence[index] + ".jsonl"
            s3_data=self.s3_object.get_data(s3_file_path)
            if(s3_data==None):
                l.append(sentence[index])
                recursion(sentence,index+1,l)
                l.pop()
            else:
                top_10_percent=self.get_top_10_percent_non_similar_words(s3_data[0],s3_data)
                for word in top_10_percent:
                    l.append(word)
                    recursion(sentence, index + 1, l)
                    l.pop()


        for sentence in self.final_template_sentences:
            print("###############################")
            recursion(sentence, 0, [])
            print("###############################")
        return result

    def get_all_postgresql_rows(self):
        self.postgre_sql_mapping={} # Parent_child - Key and Value=token-id
        for row in self.postgresql_obj.list_all_rows():
            token_id=row[0]
            parent_child="".join(row[1])

            if(parent_child not in self.postgre_sql_mapping):
                self.postgre_sql_mapping[parent_child]=token_id


    def reverse_engineering(self):

        def nest_sentence(sentence):
            words = sentence
            nested_dict = words[-1]
            if nested_dict == "$|Empty List|$":
                nested_dict = []
            elif "%[[[[[[%" in str(nested_dict) and "%]]]]]]%" in str(nested_dict):
                clean_val = str(nested_dict).replace("%[[[[[[%", "").replace("%]]]]]]%", "")
                nested_dict = ast.literal_eval(clean_val)

            elif ("$|List of Lists|$" in str(nested_dict)):
                words = str(nested_dict).split("$|List of Lists|$")
                nested_dict = []
                for w in words:
                    nested_dict.append(ast.literal_eval(w))
            # Iterate through words in reverse

            for word in reversed(words[:len(words) - 1]):
                # The current word becomes a key, and the previous
                # nested structure becomes its value
                if (word == "%|List_Of_Dictionary|%"):
                    nested_dict = [nested_dict]
                elif (word == "$|Empty List|$"):
                    nested_dict = []
                elif ("%[[[[[[%" in word and "%]]]]]]%" in word):
                    word = word.replace("%[[[[[[%", "")
                    word = word.replace("%]]]]]]%", "")
                    actual_list = ast.literal_eval(word)
                    nested_dict = actual_list
                elif ("$|List of Lists|$" in word):
                    words = word.split("$|List of Lists|$")
                    nested_dict = []
                    for w in words:
                        nested_dict.append(ast.literal_eval(w))
                else:
                    nested_dict = {word: nested_dict}

            return nested_dict

        def deep_merge(dict1, dict2):
            """
            Recursively merges dict2 into dict1, specifically handling
            lists of dictionaries found in your network templates.
            """
            for key, value in dict2.items():
                if key in dict1:
                    # Case 1: Both are dictionaries - Recurse
                    if isinstance(dict1[key], dict) and isinstance(value, dict):
                        deep_merge(dict1[key], value)

                    # Case 2: Both are lists - Merge internal dictionaries
                    elif isinstance(dict1[key], list) and isinstance(value, list):
                        # For network configs, we usually merge the first elements
                        # if they represent the same configuration block.
                        if len(dict1[key]) > 0 and len(value) > 0:
                            if isinstance(dict1[key][0], dict) and isinstance(value[0], dict):
                                deep_merge(dict1[key][0], value[0])
                            else:
                                dict1[key].extend(value)
                        else:
                            dict1[key].extend(value)
                    else:
                        dict1[key] = value
                else:
                    # Case 3: Key doesn't exist - Add it
                    dict1[key] = value
            return dict1

        result={}
        l={}
        for sentence in self.generalized_sentences_list:
            for i in range(len(self.generalized_sentences_list[sentence])):
                if(i not in l):
                    l[i]=[self.generalized_sentences_list[sentence][i]]
                else:
                    l[i].append(self.generalized_sentences_list[sentence][i])

        for i in l:
            res={}
            for sentence in l[i]:
                result=deep_merge(result,nest_sentence(sentence))
        f.write("\n"+str(result)+"\n")
        pass# Replace words with meaningful


class nested_dict_to_list:
    # payload - Is the nested dictionary structure
    def __init__(self):
        self.list = []

    def __iter__(self, payload, l):
        # Base condition
        # If the type of payload is list or str or int or float or boolean -- Break
        # Else if payload is dictionary continue
        t = type(payload)
        if (t == dict):
            for key in payload:
                l.append(key)
                self.__iter__(payload[key], l)
                l.pop()
        elif (isinstance(payload, list)):
            if (len(payload)):
                type_of_list_element = type(payload[0])
            else:
                # empty list
                type_of_list_element = "empty list"
            if (type_of_list_element == dict):
                for element in payload:
                    if (type(element) == dict):
                        l.append("%|List_Of_Dictionary|%")
                        self.__iter__(element, l)
                        l.pop()
            elif (type_of_list_element == list):
                for element in payload:
                    # List of List has ||
                    list_to_string = str(element).replace(", ", "$|List of Lists|$")[1:len(str(element)) - 1]
                    l.append(list_to_string)
                    self.list.append(l.copy())
                    l.pop()
            else:

                if (type_of_list_element == "empty list"):
                    # Empty list
                    l.append("$|Empty List|$")
                    self.list.append(l.copy())
                    l.pop()
                else:
                    # This can be list of int, list of str , list of float
                    l.append("%[[[[[[%" + str(payload) + "%]]]]]]%")
                    self.list.append(l.copy())
                    l.pop()
        else:
            # This is impossible since in https payload its not allowed
            if (isinstance(payload, tuple) or isinstance(payload, set)):
                for element in payload:
                    l.append(element)
                    self.list.append(l.copy())
                    l.pop()
            else:
                l.append(payload)
                self.list.append(l.copy())
                l.pop()
            return self.list

    def print_list_equivalent_of_dict(self):
        l = []
        for key in self.list:
            l.append(key)


payload = {
    "shreyas2": {
        "adopted": False,
        "disable_auto_config": False,
        "managed": True,
        "role": "",
        "notes": "",
        "networks": {
            "marvisvlan2": {
                "vlan_id": 2,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan3": {
                "vlan_id": 3,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan4": {
                "vlan_id": 4,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan5": {
                "vlan_id": 5,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan6": {
                "vlan_id": 6,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan7": {
                "vlan_id": 7,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan8": {
                "vlan_id": 8,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan9": {
                "vlan_id": 9,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan10": {
                "vlan_id": 10,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan11": {
                "vlan_id": 11,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan12": {
                "vlan_id": 12,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan13": {
                "vlan_id": 13,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan14": {
                "vlan_id": 14,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan15": {
                "vlan_id": 15,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan16": {
                "vlan_id": 16,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan17": {
                "vlan_id": 17,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan18": {
                "vlan_id": 18,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan19": {
                "vlan_id": 19,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan20": {
                "vlan_id": 20,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan21": {
                "vlan_id": 21,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan22": {
                "vlan_id": 22,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan23": {
                "vlan_id": 23,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan24": {
                "vlan_id": 24,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan25": {
                "vlan_id": 25,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan26": {
                "vlan_id": 26,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan27": {
                "vlan_id": 27,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan28": {
                "vlan_id": 28,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan29": {
                "vlan_id": 29,
                "subnet": "",
                "subnet6": ""
            },
            "vlan100": {
                "vlan_id": "100",
                "subnet": "",
                "subnet6": ""
            }
        },
        "port_usages": {
            "new": {
                "mode": "access",
                "disabled": False,
                "port_network": "default",
                "voip_network": None,
                "stp_edge": False,
                "stp_disable": False,
                "stp_required": False,
                "stp_p2p": False,
                "stp_no_root_port": False,
                "use_vstp": False,
                "port_auth": None,
                "allow_multiple_supplicants": None,
                "enable_mac_auth": None,
                "mac_auth_only": None,
                "mac_auth_preferred": None,
                "guest_network": None,
                "bypass_auth_when_server_down": None,
                "bypass_auth_when_server_down_for_unknown_client": None,
                "dynamic_vlan_networks": None,
                "server_reject_network": None,
                "server_fail_network": None,
                "mac_auth_protocol": None,
                "reauth_interval": None,
                "all_networks": False,
                "networks": None,
                "speed": "100m",
                "duplex": "auto",
                "mac_limit": 0,
                "persist_mac": False,
                "poe_disabled": False,
                "enable_qos": False,
                "storm_control": {},
                "mtu": None,
                "description": "",
                "disable_autoneg": False
            },
            "access10": {
                "mode": "access",
                "disabled": False,
                "port_network": "marvisvlan10",
                "voip_network": None,
                "stp_edge": False,
                "stp_disable": False,
                "stp_required": False,
                "stp_p2p": False,
                "stp_no_root_port": False,
                "use_vstp": False,
                "port_auth": None,
                "allow_multiple_supplicants": None,
                "enable_mac_auth": None,
                "mac_auth_only": None,
                "mac_auth_preferred": None,
                "guest_network": None,
                "bypass_auth_when_server_down": None,
                "bypass_auth_when_server_down_for_unknown_client": None,
                "dynamic_vlan_networks": None,
                "server_reject_network": None,
                "server_fail_network": None,
                "mac_auth_protocol": None,
                "reauth_interval": None,
                "all_networks": False,
                "networks": None,
                "speed": "auto",
                "duplex": "auto",
                "mac_limit": 0,
                "persist_mac": False,
                "poe_disabled": False,
                "enable_qos": False,
                "storm_control": {},
                "mtu": None,
                "description": "",
                "disable_autoneg": False,
                "poe_legacy_pd": False
            },
            "vl1n20": {
                "name": "vl1n20",
                "mode": "access",
                "disabled": False,
                "port_network": "marvisvlan20",
                "voip_network": None,
                "stp_edge": False,
                "stp_disable": False,
                "stp_required": False,
                "stp_p2p": False,
                "stp_no_root_port": False,
                "use_vstp": False,
                "port_auth": None,
                "allow_multiple_supplicants": None,
                "enable_mac_auth": None,
                "mac_auth_only": None,
                "mac_auth_preferred": None,
                "guest_network": None,
                "bypass_auth_when_server_down": None,
                "bypass_auth_when_server_down_for_unknown_client": None,
                "dynamic_vlan_networks": None,
                "server_reject_network": None,
                "server_fail_network": None,
                "mac_auth_protocol": None,
                "reauth_interval": None,
                "all_networks": False,
                "networks": None,
                "speed": "auto",
                "duplex": "auto",
                "mac_limit": 0,
                "persist_mac": False,
                "poe_disabled": False,
                "poe_legacy_pd": False,
                "enable_qos": False,
                "storm_control": {},
                "mtu": None,
                "description": "",
                "disable_autoneg": False
            },
            "predpc10": {
                "mode": "access",
                "disabled": False,
                "port_network": "marvisvlan10",
                "voip_network": None,
                "stp_edge": False,
                "stp_disable": False,
                "stp_required": False,
                "stp_p2p": False,
                "stp_no_root_port": False,
                "use_vstp": False,
                "port_auth": None,
                "allow_multiple_supplicants": None,
                "enable_mac_auth": None,
                "mac_auth_only": None,
                "mac_auth_preferred": None,
                "guest_network": None,
                "bypass_auth_when_server_down": None,
                "bypass_auth_when_server_down_for_unknown_client": None,
                "dynamic_vlan_networks": None,
                "server_reject_network": None,
                "server_fail_network": None,
                "mac_auth_protocol": None,
                "reauth_interval": None,
                "all_networks": False,
                "networks": None,
                "speed": "auto",
                "duplex": "auto",
                "mac_limit": 0,
                "persist_mac": False,
                "poe_disabled": False,
                "poe_legacy_pd": False,
                "enable_qos": False,
                "storm_control": {},
                "mtu": None,
                "description": "",
                "disable_autoneg": False
            },
            "postdpc20": {
                "mode": "access",
                "disabled": False,
                "port_network": "marvisvlan20",
                "voip_network": None,
                "stp_edge": False,
                "stp_disable": False,
                "stp_required": False,
                "stp_p2p": False,
                "stp_no_root_port": False,
                "use_vstp": False,
                "port_auth": None,
                "allow_multiple_supplicants": None,
                "enable_mac_auth": None,
                "mac_auth_only": None,
                "mac_auth_preferred": None,
                "guest_network": None,
                "bypass_auth_when_server_down": None,
                "bypass_auth_when_server_down_for_unknown_client": None,
                "dynamic_vlan_networks": None,
                "server_reject_network": None,
                "server_fail_network": None,
                "mac_auth_protocol": None,
                "reauth_interval": None,
                "all_networks": False,
                "networks": None,
                "speed": "auto",
                "duplex": "auto",
                "mac_limit": 0,
                "persist_mac": False,
                "poe_disabled": False,
                "poe_legacy_pd": False,
                "enable_qos": False,
                "storm_control": {},
                "mtu": None,
                "description": "",
                "disable_autoneg": False
            },
            "dot1x_heb_issue": {
                "mode": "access",
                "disabled": False,
                "port_network": "default",
                "voip_network": None,
                "stp_edge": False,
                "stp_disable": False,
                "stp_required": False,
                "stp_p2p": False,
                "stp_no_root_port": False,
                "use_vstp": False,
                "port_auth": "dot1x",
                "allow_multiple_supplicants": False,
                "enable_mac_auth": False,
                "mac_auth_only": False,
                "mac_auth_preferred": False,
                "guest_network": None,
                "bypass_auth_when_server_down": True,
                "bypass_auth_when_server_down_for_unknown_client": None,
                "dynamic_vlan_networks": None,
                "server_reject_network": None,
                "server_fail_network": None,
                "mac_auth_protocol": None,
                "reauth_interval": "65000",
                "all_networks": False,
                "networks": None,
                "speed": "auto",
                "duplex": "auto",
                "mac_limit": 0,
                "persist_mac": False,
                "poe_disabled": False,
                "poe_legacy_pd": False,
                "enable_qos": False,
                "storm_control": {},
                "mtu": None,
                "description": "",
                "disable_autoneg": False
            },
            "access7": {
                "name": "access7",
                "mode": "access",
                "disabled": False,
                "port_network": "marvisvlan7",
                "voip_network": None,
                "stp_edge": False,
                "stp_disable": False,
                "stp_required": False,
                "stp_p2p": False,
                "stp_no_root_port": False,
                "use_vstp": False,
                "port_auth": None,
                "allow_multiple_supplicants": None,
                "enable_mac_auth": None,
                "mac_auth_only": None,
                "mac_auth_preferred": None,
                "guest_network": None,
                "bypass_auth_when_server_down": None,
                "bypass_auth_when_server_down_for_unknown_client": None,
                "dynamic_vlan_networks": None,
                "server_reject_network": None,
                "server_fail_network": None,
                "mac_auth_protocol": None,
                "reauth_interval": None,
                "all_networks": False,
                "networks": None,
                "speed": "auto",
                "duplex": "auto",
                "mac_limit": 0,
                "persist_mac": False,
                "poe_disabled": False,
                "poe_legacy_pd": False,
                "enable_qos": False,
                "storm_control": {},
                "mtu": None,
                "description": "",
                "disable_autoneg": False
            },
            "port-mirror": {
                "mode": "access",
                "disabled": False,
                "port_network": "marvisvlan10",
                "voip_network": None,
                "stp_edge": False,
                "stp_disable": False,
                "stp_required": False,
                "stp_p2p": False,
                "stp_no_root_port": False,
                "use_vstp": False,
                "port_auth": None,
                "allow_multiple_supplicants": None,
                "enable_mac_auth": None,
                "mac_auth_only": None,
                "mac_auth_preferred": None,
                "guest_network": None,
                "bypass_auth_when_server_down": None,
                "bypass_auth_when_server_down_for_unknown_client": None,
                "dynamic_vlan_networks": None,
                "server_reject_network": None,
                "server_fail_network": None,
                "mac_auth_protocol": None,
                "reauth_interval": None,
                "all_networks": False,
                "networks": None,
                "speed": "auto",
                "duplex": "auto",
                "mac_limit": 0,
                "persist_mac": False,
                "poe_disabled": False,
                "poe_legacy_pd": False,
                "enable_qos": False,
                "storm_control": {},
                "mtu": None,
                "description": "",
                "disable_autoneg": False
            },
            "access-ravi": {
                "mode": "access",
                "disabled": False,
                "port_network": "marvisvlan18",
                "voip_network": None,
                "stp_edge": False,
                "stp_disable": False,
                "stp_required": False,
                "stp_p2p": False,
                "stp_no_root_port": False,
                "use_vstp": False,
                "port_auth": None,
                "allow_multiple_supplicants": None,
                "enable_mac_auth": None,
                "mac_auth_only": None,
                "mac_auth_preferred": None,
                "guest_network": None,
                "bypass_auth_when_server_down": None,
                "bypass_auth_when_server_down_for_unknown_client": None,
                "dynamic_vlan_networks": None,
                "server_reject_network": None,
                "server_fail_network": None,
                "mac_auth_protocol": None,
                "reauth_interval": None,
                "all_networks": False,
                "networks": None,
                "speed": "auto",
                "duplex": "auto",
                "mac_limit": 0,
                "persist_mac": False,
                "poe_disabled": False,
                "poe_legacy_pd": False,
                "enable_qos": False,
                "storm_control": {},
                "mtu": None,
                "description": "",
                "disable_autoneg": False
            },
            "dot1x_vlan20": {
                "mode": "access",
                "disabled": False,
                "port_network": "marvisvlan20",
                "voip_network": None,
                "stp_edge": False,
                "stp_disable": False,
                "stp_required": False,
                "stp_p2p": False,
                "stp_no_root_port": False,
                "use_vstp": False,
                "port_auth": "dot1x",
                "allow_multiple_supplicants": False,
                "enable_mac_auth": False,
                "mac_auth_only": False,
                "mac_auth_preferred": False,
                "guest_network": None,
                "bypass_auth_when_server_down": None,
                "bypass_auth_when_server_down_for_unknown_client": None,
                "dynamic_vlan_networks": None,
                "server_reject_network": None,
                "server_fail_network": None,
                "mac_auth_protocol": None,
                "reauth_interval": "65000",
                "all_networks": False,
                "networks": None,
                "speed": "auto",
                "duplex": "auto",
                "mac_limit": 0,
                "persist_mac": False,
                "poe_disabled": False,
                "poe_legacy_pd": False,
                "enable_qos": False,
                "storm_control": {},
                "mtu": None,
                "description": "",
                "disable_autoneg": False
            },
            "mtu-lesser": {
                "mode": "access",
                "disabled": False,
                "port_network": "default",
                "voip_network": None,
                "stp_edge": False,
                "stp_disable": False,
                "stp_required": False,
                "stp_p2p": False,
                "stp_no_root_port": False,
                "use_vstp": False,
                "port_auth": None,
                "allow_multiple_supplicants": None,
                "enable_mac_auth": None,
                "mac_auth_only": None,
                "mac_auth_preferred": None,
                "guest_network": None,
                "bypass_auth_when_server_down": None,
                "bypass_auth_when_server_down_for_unknown_client": None,
                "dynamic_vlan_networks": None,
                "server_reject_network": None,
                "server_fail_network": None,
                "mac_auth_protocol": None,
                "reauth_interval": None,
                "all_networks": False,
                "networks": None,
                "speed": "auto",
                "duplex": "auto",
                "mac_limit": 0,
                "persist_mac": False,
                "poe_disabled": False,
                "poe_legacy_pd": False,
                "enable_qos": False,
                "storm_control": {},
                "mtu": 1279,
                "description": "",
                "disable_autoneg": False
            },
            "mtuvalid": {
                "mode": "access",
                "disabled": False,
                "port_network": "default",
                "voip_network": None,
                "stp_edge": False,
                "stp_disable": False,
                "stp_required": False,
                "stp_p2p": False,
                "stp_no_root_port": False,
                "use_vstp": False,
                "port_auth": None,
                "allow_multiple_supplicants": None,
                "enable_mac_auth": None,
                "mac_auth_only": None,
                "mac_auth_preferred": None,
                "guest_network": None,
                "bypass_auth_when_server_down": None,
                "bypass_auth_when_server_down_for_unknown_client": None,
                "dynamic_vlan_networks": None,
                "server_reject_network": None,
                "server_fail_network": None,
                "mac_auth_protocol": None,
                "reauth_interval": None,
                "all_networks": False,
                "networks": None,
                "speed": "auto",
                "duplex": "auto",
                "mac_limit": 0,
                "persist_mac": False,
                "poe_disabled": False,
                "poe_legacy_pd": False,
                "enable_qos": False,
                "storm_control": {},
                "mtu": 1514,
                "description": "",
                "disable_autoneg": False
            },
            "port_mirror_profile": {
                "mode": "access",
                "disabled": False,
                "port_network": "marvisvlan12",
                "voip_network": None,
                "stp_edge": False,
                "stp_disable": False,
                "stp_required": False,
                "stp_p2p": False,
                "stp_no_root_port": False,
                "use_vstp": False,
                "port_auth": None,
                "allow_multiple_supplicants": None,
                "enable_mac_auth": None,
                "mac_auth_only": None,
                "mac_auth_preferred": None,
                "guest_network": None,
                "bypass_auth_when_server_down": None,
                "bypass_auth_when_server_down_for_unknown_client": None,
                "dynamic_vlan_networks": None,
                "server_reject_network": None,
                "server_fail_network": None,
                "mac_auth_protocol": None,
                "reauth_interval": None,
                "all_networks": False,
                "networks": None,
                "speed": "auto",
                "duplex": "auto",
                "mac_limit": 0,
                "persist_mac": False,
                "poe_disabled": False,
                "poe_legacy_pd": False,
                "enable_qos": False,
                "storm_control": {},
                "mtu": None,
                "description": "",
                "disable_autoneg": False
            },
            "devicedpc": {
                "mode": "access",
                "disabled": False,
                "port_network": "default",
                "voip_network": None,
                "stp_edge": False,
                "stp_disable": False,
                "stp_required": False,
                "stp_p2p": False,
                "stp_no_root_port": False,
                "use_vstp": False,
                "port_auth": None,
                "allow_multiple_supplicants": None,
                "enable_mac_auth": None,
                "mac_auth_only": None,
                "mac_auth_preferred": None,
                "guest_network": None,
                "bypass_auth_when_server_down": None,
                "bypass_auth_when_server_down_for_unknown_client": None,
                "dynamic_vlan_networks": None,
                "server_reject_network": None,
                "server_fail_network": None,
                "mac_auth_protocol": None,
                "reauth_interval": None,
                "all_networks": False,
                "networks": None,
                "speed": "auto",
                "duplex": "auto",
                "mac_limit": 0,
                "persist_mac": False,
                "poe_disabled": False,
                "poe_legacy_pd": False,
                "poe_priority": None,
                "enable_qos": False,
                "storm_control": {},
                "mtu": None,
                "description": "",
                "disable_autoneg": False
            },
            "dynamic": {
                "mode": "dynamic",
                "rules": [
                    {
                        "src": "lldp_chassis_id",
                        "usage": "postdpc20",
                        "equals": "3c:94:fd:09:91:f6",
                        "expression": "[0:17]"
                    }
                ]
            },
            "vc-4400-profile": {
                "mode": "trunk",
                "disabled": False,
                "port_network": None,
                "voip_network": None,
                "stp_edge": False,
                "stp_disable": False,
                "stp_required": False,
                "stp_p2p": False,
                "stp_no_root_port": False,
                "use_vstp": False,
                "port_auth": None,
                "allow_multiple_supplicants": None,
                "enable_mac_auth": None,
                "mac_auth_only": None,
                "mac_auth_preferred": None,
                "guest_network": None,
                "bypass_auth_when_server_down": None,
                "bypass_auth_when_server_down_for_unknown_client": None,
                "dynamic_vlan_networks": None,
                "server_reject_network": None,
                "server_fail_network": None,
                "mac_auth_protocol": None,
                "reauth_interval": None,
                "all_networks": False,
                "networks": [
                    "marvisvlan2",
                    "marvisvlan3",
                    "marvisvlan4",
                    "marvisvlan5",
                    "marvisvlan6",
                    "marvisvlan7",
                    "marvisvlan8",
                    "marvisvlan9",
                    "marvisvlan10",
                    "marvisvlan11"
                ],
                "speed": "auto",
                "duplex": "auto",
                "mac_limit": 0,
                "persist_mac": False,
                "poe_disabled": False,
                "poe_legacy_pd": False,
                "poe_priority": None,
                "enable_qos": False,
                "storm_control": {},
                "mtu": None,
                "description": "vc-4400-profile",
                "disable_autoneg": False
            },
            "stormcontrolandqos": {
                "name": "stormcontrolandqos",
                "mode": "access",
                "disabled": False,
                "port_network": "default",
                "voip_network": None,
                "stp_edge": True,
                "stp_disable": False,
                "stp_required": False,
                "stp_p2p": True,
                "stp_no_root_port": False,
                "use_vstp": False,
                "port_auth": None,
                "allow_multiple_supplicants": None,
                "enable_mac_auth": None,
                "mac_auth_only": None,
                "mac_auth_preferred": None,
                "guest_network": None,
                "bypass_auth_when_server_down": None,
                "bypass_auth_when_server_down_for_unknown_client": None,
                "dynamic_vlan_networks": None,
                "server_reject_network": None,
                "server_fail_network": None,
                "mac_auth_protocol": None,
                "reauth_interval": None,
                "all_networks": False,
                "networks": None,
                "speed": "auto",
                "duplex": "auto",
                "mac_limit": 0,
                "persist_mac": False,
                "poe_disabled": False,
                "poe_legacy_pd": False,
                "poe_priority": None,
                "enable_qos": True,
                "storm_control": {
                    "percentage": 80,
                    "no_broadcast": True,
                    "no_multicast": True,
                    "no_unknown_unicast": False,
                    "disable_port": False
                },
                "mtu": None,
                "description": "",
                "disable_autoneg": False
            },
            "valn11": {
                "mode": "access",
                "disabled": False,
                "port_network": "marvisvlan11",
                "voip_network": None,
                "stp_edge": False,
                "stp_disable": False,
                "stp_required": False,
                "stp_p2p": False,
                "stp_no_root_port": False,
                "use_vstp": False,
                "port_auth": None,
                "allow_multiple_supplicants": None,
                "enable_mac_auth": None,
                "mac_auth_only": None,
                "mac_auth_preferred": None,
                "guest_network": None,
                "bypass_auth_when_server_down": None,
                "bypass_auth_when_server_down_for_unknown_client": None,
                "dynamic_vlan_networks": None,
                "server_reject_network": None,
                "server_fail_network": None,
                "mac_auth_protocol": None,
                "reauth_interval": None,
                "all_networks": False,
                "networks": None,
                "speed": "auto",
                "duplex": "auto",
                "mac_limit": 0,
                "persist_mac": False,
                "poe_disabled": False,
                "poe_legacy_pd": False,
                "poe_priority": None,
                "enable_qos": False,
                "storm_control": {},
                "mtu": None,
                "description": "",
                "disable_autoneg": False
            },
            "uplink": {
                "mode": "trunk",
                "all_networks": False,
                "stp_edge": False,
                "port_network": "default",
                "voip_network": None,
                "isDeletable": True,
                "disabled": False,
                "stp_disable": False,
                "stp_required": False,
                "stp_p2p": False,
                "stp_no_root_port": False,
                "use_vstp": False,
                "port_auth": None,
                "allow_multiple_supplicants": None,
                "enable_mac_auth": None,
                "mac_auth_only": None,
                "mac_auth_preferred": None,
                "guest_network": None,
                "bypass_auth_when_server_down": None,
                "bypass_auth_when_server_down_for_unknown_client": None,
                "dynamic_vlan_networks": None,
                "server_reject_network": None,
                "server_fail_network": None,
                "mac_auth_protocol": None,
                "reauth_interval": None,
                "networks": [
                    "default",
                    "marvisvlan2",
                    "marvisvlan3",
                    "marvisvlan4",
                    "marvisvlan5",
                    "marvisvlan6",
                    "marvisvlan7",
                    "marvisvlan8",
                    "marvisvlan9",
                    "marvisvlan10",
                    "marvisvlan11",
                    "marvisvlan12",
                    "marvisvlan13",
                    "marvisvlan14",
                    "marvisvlan15",
                    "marvisvlan16",
                    "marvisvlan17",
                    "marvisvlan18",
                    "marvisvlan19",
                    "marvisvlan20",
                    "marvisvlan21",
                    "marvisvlan22",
                    "marvisvlan23",
                    "marvisvlan24",
                    "marvisvlan25",
                    "marvisvlan26",
                    "marvisvlan27",
                    "marvisvlan28",
                    "marvisvlan29"
                ],
                "speed": "auto",
                "duplex": "auto",
                "mac_limit": 0,
                "persist_mac": False,
                "poe_disabled": False,
                "poe_legacy_pd": False,
                "poe_priority": None,
                "poe_keep_state_when_reboot": False,
                "enable_qos": False,
                "storm_control": {},
                "mtu": None,
                "description": "",
                "disable_autoneg": False
            },
            "acccessvlan100": {
                "mode": "access",
                "disabled": False,
                "port_network": "vlan100",
                "voip_network": None,
                "stp_edge": False,
                "stp_disable": False,
                "stp_required": False,
                "stp_p2p": False,
                "stp_no_root_port": False,
                "use_vstp": False,
                "port_auth": None,
                "allow_multiple_supplicants": None,
                "enable_mac_auth": None,
                "mac_auth_only": None,
                "mac_auth_preferred": None,
                "guest_network": None,
                "bypass_auth_when_server_down": None,
                "bypass_auth_when_server_down_for_unknown_client": None,
                "dynamic_vlan_networks": None,
                "server_reject_network": None,
                "server_fail_network": None,
                "mac_auth_protocol": None,
                "reauth_interval": None,
                "all_networks": False,
                "networks": None,
                "speed": "auto",
                "duplex": "auto",
                "mac_limit": 0,
                "persist_mac": False,
                "poe_disabled": False,
                "poe_legacy_pd": False,
                "poe_priority": None,
                "enable_qos": False,
                "storm_control": {},
                "mtu": None,
                "description": "",
                "disable_autoneg": False,
                "poe_keep_state_when_reboot": False
            },
            "edge_port": {
                "mode": "access",
                "disabled": False,
                "port_network": "default",
                "voip_network": None,
                "stp_edge": True,
                "family": "junos",
                "stp_disable": False,
                "stp_required": False,
                "stp_p2p": False,
                "stp_no_root_port": False,
                "use_vstp": False,
                "port_auth": None,
                "allow_multiple_supplicants": None,
                "enable_mac_auth": None,
                "mac_auth_only": None,
                "mac_auth_preferred": None,
                "guest_network": None,
                "bypass_auth_when_server_down": None,
                "bypass_auth_when_server_down_for_unknown_client": None,
                "dynamic_vlan_networks": None,
                "server_reject_network": None,
                "server_fail_network": None,
                "mac_auth_protocol": None,
                "reauth_interval": None,
                "all_networks": False,
                "networks": None,
                "speed": "auto",
                "duplex": "auto",
                "mac_limit": 0,
                "persist_mac": False,
                "poe_disabled": False,
                "poe_legacy_pd": False,
                "poe_priority": None,
                "poe_keep_state_when_reboot": False,
                "enable_qos": False,
                "storm_control": {},
                "mtu": None,
                "description": "",
                "disable_autoneg": False
            }
        },
        "additional_config_cmds": [
            "delete protocols l2-learning global-mac-ip-snooping"
        ],
        "bgp_config": None,
        "routing_policies": {},
        "optic_port_config": {},
        "other_ip_configs": {
            "marvisvlan2": {
                "type": "dhcp"
            },
            "marvisvlan3": {
                "type": "dhcp"
            },
            "marvisvlan4": {
                "type": "dhcp"
            },
            "marvisvlan5": {
                "type": "dhcp"
            },
            "marvisvlan6": {
                "type": "dhcp"
            },
            "marvisvlan7": {
                "type": "dhcp"
            },
            "marvisvlan8": {
                "type": "dhcp"
            },
            "marvisvlan9": {
                "type": "dhcp"
            },
            "marvisvlan10": {
                "type": "dhcp"
            },
            "marvisvlan11": {
                "type": "dhcp"
            },
            "marvisvlan12": {
                "type": "dhcp"
            },
            "marvisvlan13": {
                "type": "dhcp"
            },
            "marvisvlan14": {
                "type": "dhcp"
            },
            "marvisvlan15": {
                "type": "dhcp"
            },
            "marvisvlan16": {
                "type": "dhcp"
            },
            "marvisvlan17": {
                "type": "dhcp"
            },
            "marvisvlan18": {
                "type": "dhcp"
            },
            "marvisvlan19": {
                "type": "dhcp"
            },
            "marvisvlan20": {
                "type": "dhcp"
            },
            "marvisvlan21": {
                "type": "dhcp"
            },
            "marvisvlan22": {
                "type": "dhcp"
            },
            "marvisvlan23": {
                "type": "dhcp"
            },
            "marvisvlan24": {
                "type": "dhcp"
            },
            "marvisvlan25": {
                "type": "dhcp"
            },
            "marvisvlan26": {
                "type": "dhcp"
            },
            "marvisvlan27": {
                "type": "dhcp"
            },
            "marvisvlan28": {
                "type": "dhcp"
            },
            "marvisvlan29": {
                "type": "dhcp"
            }
        },
        "port_config": {
            "ge-0/0/11": {
                "usage": "ap",
                "dynamic_usage": None,
                "critical": False,
                "description": "",
                "no_local_overwrite": True
            },
            "ge-0/0/10": {
                "usage": "ap",
                "dynamic_usage": None,
                "critical": False,
                "description": "",
                "no_local_overwrite": True
            },
            "ge-0/0/1-4, ge-0/0/6-9": {
                "usage": "default",
                "dynamic_usage": None,
                "critical": False,
                "description": "",
                "no_local_overwrite": True
            },
            "ge-0/0/5": {
                "usage": "dot1x_heb_issue",
                "dynamic_usage": None,
                "critical": False,
                "description": "",
                "no_local_overwrite": True
            },
            "ge-0/0/0": {
                "usage": "uplink",
                "dynamic_usage": None,
                "critical": False,
                "description": "",
                "no_local_overwrite": True
            }
        },
        "vars": {},
        "switch_mgmt": {
            "root_password": "mist123",
            "local_accounts": {
                "deviceuser": {
                    "role": "admin",
                    "password": "abcdfg"
                },
                "newuser": {
                    "role": "admin",
                    "password": "mist&123"
                },
                "new": {
                    "role": "admin",
                    "password": "abcdef{}[]'~"
                },
                "new1": {
                    "role": "admin",
                    "password": "abcdef{}[]'~sad&:"
                }
            }
        },
        "radius_config": {
            "enabled": False,
            "auth_servers": [],
            "acct_servers": [],
            "auth_servers_timeout": 5,
            "auth_servers_retries": 3,
            "fast_dot1x_timers": False,
            "acct_interim_interval": 0,
            "auth_server_selection": "ordered",
            "coa_enabled": False,
            "coa_port": ""
        },
        "mist_nac": {
            "enabled": True,
            "auth_servers_timeout": 5,
            "auth_servers_retries": 3,
            "fast_dot1x_timers": False,
            "acct_interim_interval": 0,
            "network": None,
            "coa_enabled": False,
            "coa_port": ""
        },
        "remote_syslog": {
            "enabled": True,
            "time_format": "",
            "source_address": None,
            "routing_instance": None,
            "archive": {
                "files": "",
                "size": ""
            },
            "files": [
                {
                    "file": "asd",
                    "match": "dsf",
                    "archive": {
                        "files": "",
                        "size": ""
                    },
                    "explicit_priority": False,
                    "structured_data": False,
                    "contents": []
                }
            ],
            "servers": [],
            "users": [],
            "console": {}
        },
        "snmp_config": {
            "enabled": True,
            "name": "asd",
            "location": "",
            "description": "",
            "contact": "",
            "views": [],
            "network": None,
            "client_list": [],
            "trap_groups": [],
            "v2c_config": []
        },
        "dhcpd_config": {
            "enabled": False
        },
        "oob_ip_config": {
            "type": "static",
            "ip": "10.216.194.60",
            "netmask": "/26",
            "use_mgmt_vrf": True,
            "use_mgmt_vrf_for_host_out": True,
            "gateway": "10.216.194.1"
        },
        "vrf_instances": {
            "vrf1": {
                "networks": [
                    "marvisvlan20",
                    "marvisvlan21",
                    "marvisvlan22"
                ],
                "extra_routes": {},
                "extra_routes6": {}
            }
        },
        "port_mirroring": {
            "latency": {
                "output_port_id": "ge-0/0/11",
                "input_port_ids_ingress": [
                    "ge-0/0/0"
                ],
                "input_port_ids_egress": [
                    "ge-0/0/0"
                ],
                "input_networks_ingress": []
            }
        },
        "extra_routes": {
            "0.0.0.0/0": {
                "via": [
                    "10.216.194.1"
                ],
                "discard": False
            }
        },
        "extra_routes6": {},
        "id": "00000000-0000-0000-1000-209339051400",
        "name": "Temp-new-name-change",
        "site_id": "e0863444-2933-4e70-a778-ee17da87eaa7",
        "org_id": "a85ecd8b-95e9-4ce7-88e0-356b27e2486f",
        "created_time": 1772613575,
        "modified_time": 1776425993,
        "map_id": None,
        "mac": "209339051400",
        "serial": "FJ3824AV0219",
        "model": "EX4100-F-12P",
        "hw_rev": "A",
        "type": "switch",
        "tag_uuid": "a85ecd8b-95e9-4ce7-88e0-356b27e2486f",
        "tag_id": 638460,
        "evpn_scope": None,
        "evpntopo_id": None,
        "st_ip_base": "",
        "deviceprofile_id": None,
        "bundled_mac": None,
        "mist_configured": True
    },
    "shreyas": {
        "adopted": False,
        "disable_auto_config": False,
        "networks": {
            "marvisvlan2": {
                "vlan_id": 2,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan3": {
                "vlan_id": 3,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan4": {
                "vlan_id": 4,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan5": {
                "vlan_id": 5,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan6": {
                "vlan_id": 6,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan7": {
                "vlan_id": 7,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan8": {
                "vlan_id": 8,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan9": {
                "vlan_id": 9,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan10": {
                "vlan_id": 10,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan11": {
                "vlan_id": 11,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan12": {
                "vlan_id": 12,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan13": {
                "vlan_id": 13,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan14": {
                "vlan_id": 14,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan15": {
                "vlan_id": 15,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan16": {
                "vlan_id": 16,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan17": {
                "vlan_id": 17,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan18": {
                "vlan_id": 18,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan19": {
                "vlan_id": 19,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan20": {
                "vlan_id": 20,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan21": {
                "vlan_id": 21,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan22": {
                "vlan_id": 22,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan23": {
                "vlan_id": 23,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan24": {
                "vlan_id": 24,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan25": {
                "vlan_id": 25,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan26": {
                "vlan_id": 26,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan27": {
                "vlan_id": 27,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan28": {
                "vlan_id": 28,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan29": {
                "vlan_id": 29,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan30": {
                "vlan_id": 30,
                "subnet": "",
                "subnet6": ""
            },
            "marvisvlan31": {
                "vlan_id": 31,
                "subnet": "",
                "subnet6": ""
            },
            "Relay": {
                "vlan_id": "",
                "subnet": "192.168.200.2/24",
                "subnet6": ""
            }
        },
        "other_ip_configs": {
            "marvisvlan4": {
                "type": "static",
                "ip": "192.168.4.2",
                "netmask": "/24"
            },
            "marvisvlan5": {
                "type": "static",
                "ip": "192.168.5.2",
                "netmask": "/24"
            },
            "marvisvlan6": {
                "type": "static",
                "ip": "192.168.6.2",
                "netmask": "/24"
            },
            "marvisvlan7": {
                "type": "static",
                "ip": "192.168.7.2",
                "netmask": "/24"
            },
            "marvisvlan8": {
                "type": "static",
                "ip": "192.168.8.2",
                "netmask": "/24"
            },
            "marvisvlan9": {
                "type": "static",
                "ip": "192.168.9.2",
                "netmask": "/24"
            },
            "marvisvlan11": {
                "type": "dhcp"
            },
            "marvisvlan12": {
                "type": "dhcp"
            },
            "marvisvlan13": {
                "type": "dhcp"
            },
            "marvisvlan14": {
                "type": "dhcp"
            },
            "marvisvlan15": {
                "type": "dhcp"
            },
            "marvisvlan16": {
                "type": "dhcp"
            },
            "marvisvlan17": {
                "type": "dhcp"
            },
            "marvisvlan18": {
                "type": "dhcp"
            },
            "marvisvlan20": {
                "type": "dhcp"
            },
            "marvisvlan21": {
                "type": "dhcp"
            },
            "marvisvlan22": {
                "type": "dhcp"
            },
            "marvisvlan23": {
                "type": "dhcp"
            },
            "marvisvlan24": {
                "type": "dhcp"
            },
            "marvisvlan25": {
                "type": "dhcp"
            },
            "marvisvlan26": {
                "type": "dhcp"
            },
            "marvisvlan27": {
                "type": "dhcp"
            },
            "marvisvlan28": {
                "type": "dhcp"
            },
            "marvisvlan29": {
                "type": "dhcp"
            },
            "marvisvlan30": {
                "type": "dhcp"
            },
            "marvisvlan31": {
                "type": "dhcp"
            },
            "marvisvlan3": {
                "type": "static",
                "ip": "192.168.3.2",
                "netmask": "/24"
            },
            "Relay": {
                "type": "static",
                "ip": "192.168.200.2",
                "netmask": "/24"
            },
            "marvisvlan2": {
                "type": "static",
                "ip": "192.168.2.2",
                "netmask": "/24"
            },
            "marvisvlan10": {
                "type": "static",
                "ip": "192.168.10.2",
                "netmask": "/24"
            },
            "marvisvlan19": {
                "type": "static",
                "ip": "192.168.19.14",
                "netmask": "/24"
            }
        },
        "role": "",
        "notes": "",
        "port_usages": {
            "vlan3": {
                "name": "vlan3",
                "mode": "access",
                "disabled": False,
                "port_network": "marvisvlan3",
                "voip_network": None,
                "stp_edge": False,
                "stp_disable": False,
                "stp_required": False,
                "stp_p2p": False,
                "stp_no_root_port": False,
                "use_vstp": False,
                "port_auth": None,
                "allow_multiple_supplicants": None,
                "enable_mac_auth": None,
                "mac_auth_only": None,
                "mac_auth_preferred": None,
                "guest_network": None,
                "bypass_auth_when_server_down": None,
                "bypass_auth_when_server_down_for_unknown_client": None,
                "dynamic_vlan_networks": None,
                "server_reject_network": None,
                "server_fail_network": None,
                "mac_auth_protocol": None,
                "reauth_interval": None,
                "all_networks": False,
                "networks": None,
                "speed": "auto",
                "duplex": "auto",
                "mac_limit": 0,
                "persist_mac": False,
                "poe_disabled": False,
                "poe_legacy_pd": False,
                "poe_priority": None,
                "enable_qos": False,
                "storm_control": {},
                "mtu": None,
                "description": "",
                "disable_autoneg": False
            },
            "vlan30_profile": {
                "mode": "access",
                "disabled": False,
                "port_network": "marvisvlan30",
                "voip_network": None,
                "stp_edge": False,
                "stp_disable": False,
                "stp_required": False,
                "stp_p2p": False,
                "stp_no_root_port": False,
                "use_vstp": False,
                "port_auth": None,
                "allow_multiple_supplicants": None,
                "enable_mac_auth": None,
                "mac_auth_only": None,
                "mac_auth_preferred": None,
                "guest_network": None,
                "bypass_auth_when_server_down": None,
                "bypass_auth_when_server_down_for_unknown_client": None,
                "dynamic_vlan_networks": None,
                "server_reject_network": None,
                "server_fail_network": None,
                "mac_auth_protocol": None,
                "reauth_interval": None,
                "all_networks": False,
                "networks": None,
                "speed": "auto",
                "duplex": "auto",
                "mac_limit": 0,
                "persist_mac": False,
                "poe_disabled": False,
                "poe_legacy_pd": False,
                "poe_priority": None,
                "enable_qos": False,
                "storm_control": {},
                "mtu": None,
                "description": "",
                "disable_autoneg": False
            },
            "dot1x": {
                "mode": "access",
                "disabled": False,
                "port_network": "default",
                "voip_network": None,
                "stp_edge": False,
                "family": "junos",
                "stp_disable": False,
                "stp_required": False,
                "stp_p2p": False,
                "stp_no_root_port": False,
                "use_vstp": False,
                "port_auth": "dot1x",
                "allow_multiple_supplicants": False,
                "enable_mac_auth": False,
                "mac_auth_only": False,
                "mac_auth_preferred": False,
                "guest_network": None,
                "bypass_auth_when_server_down": None,
                "bypass_auth_when_server_down_for_unknown_client": None,
                "dynamic_vlan_networks": None,
                "server_reject_network": None,
                "server_fail_network": None,
                "mac_auth_protocol": None,
                "reauth_interval": "65000",
                "all_networks": False,
                "networks": None,
                "speed": "auto",
                "duplex": "auto",
                "mac_limit": 0,
                "persist_mac": False,
                "poe_disabled": False,
                "poe_legacy_pd": False,
                "poe_priority": None,
                "poe_keep_state_when_reboot": False,
                "enable_qos": False,
                "storm_control": {},
                "mtu": None,
                "description": "",
                "disable_autoneg": False
            },
            "vinod": {
                "mode": "access",
                "disabled": False,
                "port_network": "marvisvlan27",
                "voip_network": None,
                "stp_edge": False,
                "family": "junos",
                "stp_disable": False,
                "stp_required": False,
                "stp_p2p": False,
                "stp_no_root_port": False,
                "use_vstp": False,
                "port_auth": None,
                "allow_multiple_supplicants": None,
                "enable_mac_auth": None,
                "mac_auth_only": None,
                "mac_auth_preferred": None,
                "guest_network": None,
                "bypass_auth_when_server_down": None,
                "bypass_auth_when_server_down_for_unknown_client": None,
                "dynamic_vlan_networks": None,
                "server_reject_network": None,
                "server_fail_network": None,
                "mac_auth_protocol": None,
                "reauth_interval": None,
                "all_networks": False,
                "networks": None,
                "speed": "auto",
                "duplex": "auto",
                "mac_limit": 0,
                "persist_mac": False,
                "poe_disabled": False,
                "poe_legacy_pd": False,
                "poe_priority": None,
                "poe_keep_state_when_reboot": False,
                "enable_qos": False,
                "storm_control": {},
                "mtu": None,
                "description": "",
                "disable_autoneg": False
            }
        },
        "additional_config_cmds": [
            "delete protocols l2-learning global-mac-ip-snooping"
        ],
        "bgp_config": None,
        "routing_policies": {},
        "port_config": {
            "ge-0/0/0": {
                "usage": "uplink",
                "dynamic_usage": None,
                "critical": False,
                "description": "",
                "no_local_overwrite": True
            },
            "ge-0/0/11": {
                "usage": "inet",
                "dynamic_usage": None,
                "critical": False,
                "description": "",
                "no_local_overwrite": True,
                "speed": "auto",
                "duplex": "auto",
                "poe_disabled": False,
                "disable_autoneg": False,
                "port_network": "Relay"
            },
            "ge-0/0/4-5, ge-0/0/8": {
                "usage": "vlan3",
                "dynamic_usage": None,
                "critical": False,
                "description": "",
                "no_local_overwrite": True
            },
            "ge-0/0/3": {
                "usage": "uplink",
                "dynamic_usage": None,
                "critical": False,
                "description": "",
                "no_local_overwrite": True
            },
            "ge-0/0/7": {
                "usage": "uplink",
                "dynamic_usage": None,
                "critical": False,
                "description": "",
                "no_local_overwrite": True
            },
            "ge-0/0/9": {
                "usage": "disabled",
                "dynamic_usage": None,
                "critical": False,
                "description": "",
                "no_local_overwrite": True
            },
            "ge-0/0/10": {
                "usage": "vinod",
                "dynamic_usage": None,
                "critical": False,
                "description": "",
                "no_local_overwrite": True
            },
            "ge-0/0/1": {
                "usage": "uplink",
                "dynamic_usage": None,
                "critical": False,
                "description": "",
                "no_local_overwrite": True
            },
            "ge-0/0/2": {
                "usage": "uplink",
                "dynamic_usage": None,
                "critical": False,
                "description": "",
                "no_local_overwrite": True
            }
        },
        "optic_port_config": {},
        "dhcpd_config": {
            "enabled": False
        },
        "vars": {},
        "oob_ip_config": {
            "type": "static",
            "ip": "10.216.194.101",
            "netmask": "/26",
            "use_mgmt_vrf": True,
            "use_mgmt_vrf_for_host_out": False,
            "gateway": "10.216.194.1"
        },
        "radius_config": {
            "enabled": True,
            "auth_servers": [
                {
                    "port": 1812,
                    "host": "10.216.197.209",
                    "secret": "mist123",
                    "id": "70bb6748-6a65-446e-bc35-462a9ea6ef70"
                }
            ],
            "acct_servers": [],
            "auth_servers_timeout": 5,
            "auth_servers_retries": 3,
            "fast_dot1x_timers": False,
            "acct_interim_interval": 0,
            "auth_server_selection": "ordered",
            "coa_enabled": False,
            "coa_port": ""
        },
        "mist_nac": {
            "enabled": False,
            "auth_servers_timeout": 5,
            "auth_servers_retries": 3,
            "fast_dot1x_timers": False,
            "acct_interim_interval": 0,
            "network": None,
            "coa_enabled": False,
            "coa_port": ""
        },
        "id": "00000000-0000-0000-1000-a4e11abcad00",
        "name": "Jma-new-change",
        "site_id": "e0863444-2933-4e70-a778-ee17da87eaa7",
        "org_id": "a85ecd8b-95e9-4ce7-88e0-356b27e2486f",
        "created_time": 1770631310,
        "modified_time": 1775807324,
        "map_id": None,
        "mac": "a4e11abcad00",
        "serial": "FJ0223AV0853",
        "model": "EX4100-F-12P",
        "hw_rev": "A",
        "type": "switch",
        "tag_uuid": "a85ecd8b-95e9-4ce7-88e0-356b27e2486f",
        "tag_id": 587474,
        "evpn_scope": None,
        "evpntopo_id": None,
        "st_ip_base": "",
        "deviceprofile_id": None,
        "bundled_mac": None,
        "mist_configured": True
    },
    "ravi1": {
        "vars": {},
        "notes": "",
        "role": "",
        "ntp_servers": [
            "66.129.233.81",
            "66.129.233.82"
        ],
        "networks": {
            "v10": {
                "vlan_id": "10",
                "subnet": "",
                "subnet6": ""
            },
            "v20": {
                "vlan_id": "20",
                "subnet": "",
                "subnet6": ""
            }
        },
        "extra_routes": {
            "0.0.0.0/0": {
                "via": [
                    "10.216.201.1"
                ],
                "discard": False
            }
        },
        "dhcpd_config": {
            "enabled": False
        },
        "dns_servers": [
            "66.129.233.81",
            "10.215.194.50",
            "66.129.233.82"
        ],
        "dns_suffix": [
            "englab.juniper.net"
        ],
        "additional_config_cmds": [],
        "router_id": "172.16.254.1",
        "routing_policies": {},
        "port_usages": {
            "dot1x_test_10": {
                "mode": "access",
                "disabled": False,
                "port_network": "v10",
                "voip_network": None,
                "stp_edge": False,
                "use_vstp": False,
                "port_auth": "dot1x",
                "allow_multiple_supplicants": False,
                "enable_mac_auth": True,
                "mac_auth_only": True,
                "guest_network": None,
                "bypass_auth_when_server_down": False,
                "dynamic_vlan_networks": None,
                "stp_p2p": False,
                "stp_no_root_port": False,
                "mac_auth_protocol": None,
                "reauth_interval": "65000",
                "all_networks": False,
                "networks": None,
                "speed": "auto",
                "duplex": "auto",
                "mac_limit": 0,
                "persist_mac": False,
                "poe_disabled": False,
                "enable_qos": False,
                "storm_control": {},
                "mtu": None,
                "description": "",
                "disable_autoneg": False
            },
            "dot1x_test_20": {
                "disabled": False,
                "mode": "access",
                "port_network": "v20",
                "voip_network": None,
                "stp_edge": False,
                "use_vstp": False,
                "port_auth": "dot1x",
                "allow_multiple_supplicants": False,
                "enable_mac_auth": True,
                "mac_auth_only": True,
                "guest_network": None,
                "bypass_auth_when_server_down": False,
                "dynamic_vlan_networks": None,
                "stp_p2p": False,
                "stp_no_root_port": False,
                "mac_auth_protocol": None,
                "reauth_interval": "65000",
                "all_networks": False,
                "networks": None,
                "speed": "auto",
                "duplex": "auto",
                "mac_limit": 0,
                "persist_mac": False,
                "poe_disabled": False,
                "enable_qos": False,
                "storm_control": {},
                "mtu": None,
                "description": "",
                "disable_autoneg": False
            },
            "trunk_srx": {
                "mode": "trunk",
                "disabled": False,
                "port_network": "default",
                "voip_network": None,
                "stp_edge": False,
                "stp_disable": False,
                "stp_required": False,
                "stp_p2p": False,
                "stp_no_root_port": False,
                "use_vstp": False,
                "port_auth": None,
                "allow_multiple_supplicants": None,
                "enable_mac_auth": None,
                "mac_auth_only": None,
                "guest_network": None,
                "bypass_auth_when_server_down": None,
                "dynamic_vlan_networks": None,
                "server_reject_network": None,
                "server_fail_network": None,
                "mac_auth_protocol": None,
                "reauth_interval": None,
                "all_networks": False,
                "networks": [
                    "default"
                ],
                "speed": "auto",
                "duplex": "auto",
                "mac_limit": 0,
                "persist_mac": False,
                "poe_disabled": False,
                "enable_qos": False,
                "storm_control": {},
                "mtu": None,
                "description": "",
                "disable_autoneg": False
            },
            "trunk": {
                "mode": "trunk",
                "disabled": False,
                "port_network": "default",
                "voip_network": None,
                "stp_edge": False,
                "stp_disable": False,
                "stp_required": False,
                "stp_p2p": False,
                "stp_no_root_port": False,
                "use_vstp": False,
                "port_auth": None,
                "allow_multiple_supplicants": None,
                "enable_mac_auth": None,
                "mac_auth_only": None,
                "mac_auth_preferred": None,
                "guest_network": None,
                "bypass_auth_when_server_down": None,
                "bypass_auth_when_server_down_for_unknown_client": None,
                "dynamic_vlan_networks": None,
                "server_reject_network": None,
                "server_fail_network": None,
                "mac_auth_protocol": None,
                "reauth_interval": None,
                "all_networks": False,
                "networks": [
                    "v10"
                ],
                "speed": "auto",
                "duplex": "auto",
                "mac_limit": 0,
                "persist_mac": False,
                "poe_disabled": False,
                "enable_qos": False,
                "storm_control": {},
                "mtu": None,
                "description": "",
                "disable_autoneg": False
            },
            "loop": {
                "mode": "access",
                "disabled": False,
                "port_network": "v10",
                "voip_network": None,
                "stp_edge": False,
                "stp_disable": False,
                "stp_required": False,
                "stp_p2p": False,
                "stp_no_root_port": False,
                "use_vstp": False,
                "port_auth": None,
                "allow_multiple_supplicants": None,
                "enable_mac_auth": None,
                "mac_auth_only": None,
                "guest_network": None,
                "bypass_auth_when_server_down": None,
                "dynamic_vlan_networks": None,
                "server_reject_network": None,
                "server_fail_network": None,
                "mac_auth_protocol": None,
                "reauth_interval": None,
                "all_networks": False,
                "networks": None,
                "speed": "auto",
                "duplex": "auto",
                "mac_limit": 0,
                "persist_mac": False,
                "poe_disabled": False,
                "enable_qos": False,
                "storm_control": {},
                "mtu": None,
                "description": "",
                "disable_autoneg": False,
                "mac_auth_preferred": None,
                "bypass_auth_when_server_down_for_unknown_client": None
            }
        },
        "optic_port_config": {},
        "disable_auto_config": False,
        "stp_config": {},
        "bgp_config": None,
        "extra_routes6": {},
        "switch_mgmt": {
            "root_password": "Embe1mpls"
        },
        "adopted": False,
        "oob_ip_config": {
            "type": "static",
            "ip": "10.216.201.161",
            "netmask": "/24",
            "use_mgmt_vrf": False
        },
        "evpn_config": {
            "role": "core",
            "evpn_id": 1,
            "downlink2ip": {
                "58867018a500": "10.255.240.2"
            },
            "downlink_ips": [
                "10.255.240.2"
            ],
            "uplinks": [],
            "suggested_uplinks": [],
            "downlinks": [
                "58867018a500"
            ],
            "suggested_downlinks": [
                "58867018a500"
            ]
        },
        "port_config": {
            "ge-0/0/20": {
                "usage": "evpn_downlink"
            }
        },
        "other_ip_configs": {
            "testjh": {
                "type": "static",
                "ip": "190.134.11.2",
                "netmask": "255.255.255.0"
            }
        },
        "vrf_config": {
            "enabled": False
        },
        "id": "00000000-0000-0000-1000-fc9643b962d0",
        "name": "core1",
        "site_id": "b566aeaa-800a-4eba-bd8c-6a70e4a6465f",
        "org_id": "41b1a3f1-e94c-4ae5-b15e-3c76794e9e63",
        "created_time": 1757305856,
        "modified_time": 1774515485,
        "map_id": None,
        "mac": "fc9643b962d0",
        "serial": "AK44000521",
        "model": "QFX5120-32C",
        "hw_rev": "M",
        "type": "switch",
        "tag_uuid": "41b1a3f1-e94c-4ae5-b15e-3c76794e9e63",
        "tag_id": 451821,
        "evpn_scope": "site",
        "evpntopo_id": "1bc91b62-b660-4ea0-86f3-69a23bba7864",
        "st_ip_base": "",
        "deviceprofile_id": None,
        "bundled_mac": None,
        "mist_configured": True
    }
    ,
    "ravi2": {
        "disable_auto_config": False,
        "managed": False,
        "role": "",
        "notes": "",
        "networks": {},
        "port_usages": {},
        "additional_config_cmds": [],
        "bgp_config": None,
        "routing_policies": {},
        "optic_port_config": {
            "xe-0/2/0": {
                "speed": "10g"
            }
        },
        "router_id": "172.16.254.4",
        "dhcpd_config": {
            "enabled": False
        },
        "vars": {},
        "adopted": False,
        "stp_config": {},
        "extra_routes": {
            "0.0.0.0/0": {
                "via": [
                    "10.216.201.1"
                ],
                "discard": False
            }
        },
        "extra_routes6": {},
        "oob_ip_config": {
            "type": "static",
            "ip": "10.216.201.163",
            "netmask": "/24",
            "use_mgmt_vrf": False
        },
        "evpn_config": {
            "role": "esilag-access",
            "evpn_id": 4,
            "esilaglinks": [
                "58867018a500"
            ],
            "suggested_esilaglinks": [
                "58867018a500"
            ]
        },
        "port_config": {
            "ge-0/0/14": {
                "usage": "profile12",
                "aggregated": True,
                "ae_idx": 0
            }
        },
        "other_ip_configs": {},
        "id": "00000000-0000-0000-1000-f8c1164a8a00",
        "name": "dist1",
        "site_id": "b566aeaa-800a-4eba-bd8c-6a70e4a6465f",
        "org_id": "41b1a3f1-e94c-4ae5-b15e-3c76794e9e63",
        "created_time": 1756793057,
        "modified_time": 1774515486,
        "map_id": None,
        "mac": "f8c1164a8a00",
        "serial": "ZE4322310009",
        "model": "EX4400-24P",
        "hw_rev": "A",
        "type": "switch",
        "tag_uuid": "41b1a3f1-e94c-4ae5-b15e-3c76794e9e63",
        "tag_id": 561175,
        "evpn_scope": "site",
        "evpntopo_id": "1bc91b62-b660-4ea0-86f3-69a23bba7864",
        "st_ip_base": "",
        "deviceprofile_id": None,
        "bundled_mac": None,
        "mist_configured": True
    },
    "ravi3": {
        "disable_auto_config": False,
        "managed": False,
        "role": "",
        "notes": "",
        "networks": {},
        "port_usages": {
            "dot1x_heb_issue": {
                "mode": "access",
                "disabled": False,
                "port_network": "default",
                "voip_network": None,
                "stp_edge": False,
                "stp_disable": False,
                "stp_required": False,
                "stp_p2p": False,
                "stp_no_root_port": False,
                "use_vstp": False,
                "port_auth": "dot1x",
                "allow_multiple_supplicants": True,
                "enable_mac_auth": True,
                "mac_auth_only": False,
                "mac_auth_preferred": False,
                "guest_network": None,
                "bypass_auth_when_server_down": True,
                "bypass_auth_when_server_down_for_unknown_client": None,
                "dynamic_vlan_networks": None,
                "server_reject_network": None,
                "server_fail_network": None,
                "mac_auth_protocol": None,
                "reauth_interval": "65000",
                "all_networks": False,
                "networks": None,
                "speed": "auto",
                "duplex": "auto",
                "mac_limit": 0,
                "persist_mac": False,
                "poe_disabled": False,
                "poe_legacy_pd": False,
                "enable_qos": False,
                "storm_control": {},
                "mtu": None,
                "description": "",
                "disable_autoneg": False
            },
            "pp_vrf_red": {
                "mode": "trunk",
                "disabled": False,
                "port_network": "v11",
                "voip_network": None,
                "stp_edge": False,
                "stp_disable": False,
                "stp_required": False,
                "stp_p2p": False,
                "stp_no_root_port": False,
                "use_vstp": False,
                "port_auth": None,
                "allow_multiple_supplicants": None,
                "enable_mac_auth": None,
                "mac_auth_only": None,
                "guest_network": None,
                "bypass_auth_when_server_down": None,
                "dynamic_vlan_networks": None,
                "server_reject_network": None,
                "server_fail_network": None,
                "mac_auth_protocol": None,
                "reauth_interval": None,
                "all_networks": False,
                "networks": [
                    "v12",
                    "v13"
                ],
                "speed": "auto",
                "duplex": "auto",
                "mac_limit": 0,
                "persist_mac": False,
                "poe_disabled": False,
                "enable_qos": False,
                "storm_control": {},
                "mtu": None,
                "description": "",
                "disable_autoneg": False,
                "mac_auth_preferred": None,
                "bypass_auth_when_server_down_for_unknown_client": None,
                "poe_legacy_pd": False
            },
            "pp_vrf_green": {
                "mode": "trunk",
                "disabled": False,
                "port_network": "v21",
                "voip_network": None,
                "stp_edge": False,
                "stp_disable": False,
                "stp_required": False,
                "stp_p2p": False,
                "stp_no_root_port": False,
                "use_vstp": False,
                "port_auth": None,
                "allow_multiple_supplicants": None,
                "enable_mac_auth": None,
                "mac_auth_only": None,
                "mac_auth_preferred": None,
                "guest_network": None,
                "bypass_auth_when_server_down": None,
                "bypass_auth_when_server_down_for_unknown_client": None,
                "dynamic_vlan_networks": None,
                "server_reject_network": None,
                "server_fail_network": None,
                "mac_auth_protocol": None,
                "reauth_interval": None,
                "all_networks": False,
                "networks": [
                    "v22",
                    "v23"
                ],
                "speed": "auto",
                "duplex": "auto",
                "mac_limit": 0,
                "persist_mac": False,
                "poe_disabled": False,
                "poe_legacy_pd": False,
                "enable_qos": False,
                "storm_control": {},
                "mtu": None,
                "description": "",
                "disable_autoneg": False
            },
            "pp_vrf_blue": {
                "mode": "trunk",
                "disabled": False,
                "port_network": "v31",
                "voip_network": None,
                "stp_edge": False,
                "stp_disable": False,
                "stp_required": False,
                "stp_p2p": False,
                "stp_no_root_port": False,
                "use_vstp": False,
                "port_auth": None,
                "allow_multiple_supplicants": None,
                "enable_mac_auth": None,
                "mac_auth_only": None,
                "mac_auth_preferred": None,
                "guest_network": None,
                "bypass_auth_when_server_down": None,
                "bypass_auth_when_server_down_for_unknown_client": None,
                "dynamic_vlan_networks": None,
                "server_reject_network": None,
                "server_fail_network": None,
                "mac_auth_protocol": None,
                "reauth_interval": None,
                "all_networks": False,
                "networks": [
                    "v32",
                    "v33"
                ],
                "speed": "auto",
                "duplex": "auto",
                "mac_limit": 0,
                "persist_mac": False,
                "poe_disabled": False,
                "poe_legacy_pd": False,
                "enable_qos": False,
                "storm_control": {},
                "mtu": None,
                "description": "",
                "disable_autoneg": False
            }
        },
        "additional_config_cmds": [],
        "stp_config": {},
        "bgp_config": None,
        "routing_policies": {},
        "optic_port_config": {},
        "port_config": {
            "ge-0/0/0": {
                "usage": "pp_vrf_red",
                "dynamic_usage": None,
                "critical": False,
                "description": "",
                "no_local_overwrite": True
            }
        },
        "router_id": "172.16.254.4",
        "dhcpd_config": {
            "enabled": False
        },
        "adopted": False,
        "oob_ip_config": {
            "type": "static",
            "ip": "10.216.201.165",
            "netmask": "/24",
            "use_mgmt_vrf": True,
            "use_mgmt_vrf_for_host_out": True,
            "gateway": "10.216.201.1"
        },
        "id": "00000000-0000-0000-1000-c0dfed348300",
        "name": "access1",
        "site_id": "b566aeaa-800a-4eba-bd8c-6a70e4a6465f",
        "org_id": "41b1a3f1-e94c-4ae5-b15e-3c76794e9e63",
        "created_time": 1757564381,
        "modified_time": 1774513530,
        "map_id": None,
        "mac": "c0dfed348300",
        "serial": "FC1625AX1024",
        "model": "EX4100-24P",
        "hw_rev": "A",
        "type": "switch",
        "tag_uuid": "41b1a3f1-e94c-4ae5-b15e-3c76794e9e63",
        "tag_id": 571313,
        "evpn_scope": None,
        "evpntopo_id": None,
        "st_ip_base": "",
        "deviceprofile_id": None,
        "bundled_mac": None,
        "mist_configured": True
    },

    "hammad": {
        "adopted": False,
        "managed": True,
        "role": "",
        "notes": "",
        "disable_auto_config": False,
        "networks": {},
        "port_usages": {},
        "additional_config_cmds": [],
        "bgp_config": None,
        "routing_policies": {},
        "optic_port_config": {},
        "id": "00000000-0000-0000-1000-a4e11abb6a00",
        "name": "HK-S11-Switch-01",
        "site_id": "a1184ff1-6a67-4660-b1b0-cdd413d2f95c",
        "org_id": "8dc44280-48cc-4f40-bc9a-fdb446409620",
        "created_time": 1776368364,
        "modified_time": 1776368380,
        "map_id": None,
        "mac": "a4e11abb6a00",
        "serial": "FJ0223AV0404",
        "model": "EX4100-F-12P",
        "hw_rev": "A",
        "type": "switch",
        "tag_uuid": "8dc44280-48cc-4f40-bc9a-fdb446409620",
        "tag_id": 703694,
        "evpn_scope": None,
        "evpntopo_id": None,
        "st_ip_base": "",
        "deviceprofile_id": None,
        "bundled_mac": None,
        "mist_configured": True
    }
}
Build_Splice_tree(payload)

# list_of_sentences=[]
# for i in payload:
#     mac=payload[i]["mac"]
#     l=[]
#     obj=nested_dict_to_list()
#     obj.__iter__(payload[i], l)
#     list_of_sentences.extend(obj.list)


# tree_root = build_sentence_tree(list_of_sentences)
# visualize_tree(tree_root)


# all_found_sentences = []
# get_sentences_dfs(tree_root, [], all_found_sentences)
# for s in all_found_sentences:
#     f.write(str(s))


# import pickle
#
# # To SAVE the tree
# with open('device_tree.pkl', 'wb') as f:
#     pickle.dump(tree_root, f)
#
# # To LOAD the tree later
# with open('device_tree.pkl', 'rb') as f:
#     loaded_tree = pickle.load(f)