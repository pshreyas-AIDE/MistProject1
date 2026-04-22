import json
import hashlib # To get unique Token name which will not be used in payload

from boto3.dynamodb.types import LIST

from library.s3_library import S3StorageManager
from library.postgresql import *
import os
import math


# use Cosine similarity to find top 10% of words which are similar - Import library as below
# Will be used in one single method
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


f=open("temporary.json","w")
'''
Phase 1: Implement a recursive script that turns any nested dict into a list of "Path-Value" tuples.


'''

excluded_keys={
"role":1,
"notes":1,
"id":1,
"name":1,
"site_id":1,
"org_id":1,
"created_time":1,
"modified_time":1,
"map_id":1,
"mac":1,
"serial":1,
"model":1,
"hw_rev":1,
"tag_uuid":1,
"tag_id":1,
"deviceprofile_id":1
}
# excluded_keys={}
# parents_of_keys_which_are_user_input={}
parents_of_keys_which_are_user_input={"port_usages":1,
                                      "networks":1,"other_ip_configs":1}

empty_parent_or_empty_child_hash_value="@#$%^&*(Empty Empty Empty)*&^%$#@"
# PostGre SQL new row addition class
class TokenDatabase(Base):
    __tablename__ = os.environ.get("env_id")+"_token_mapping_table"
    token_id = Column(String)
    parent_child_value= Column(String,primary_key=True)
    current_node_value=Column(String)

# Postgresql Tokenized sentence to Mac list
class TokenSentence(Base):
    __tablename__ = os.environ.get("env_id")+"_token_sentence_mac_table"
    tokenized_sentence = Column(String,primary_key=True)
    mac_list=Column(ARRAY(MACADDR),default=[])

# Postgresql Token and Token_parent|token_children mapping
class TokenParentChildReltation(Base):
    __tablename__ = os.environ.get("env_id")+"_token_parent_child_relation_table"
    token_id = Column(String,primary_key=True)
    parent_child_relation= Column(String)

class nested_dict_to_list:
    # payload - Is the nested dictionary structure
    def __init__(self):
        self.list = []
    def __iter__(self,payload,l):
        # Base condition
        # If the type of payload is list or str or int or float or boolean -- Break
        # Else if payload is dictionary continue
        t=type(payload)
        if(t == dict):
            for key in payload:
                l.append(key)
                self.__iter__(payload[key],l)
                l.pop()
        elif(isinstance(payload,list)):
            if(len(payload)):
                type_of_list_element=type(payload[0])
            else:
                #empty list
                type_of_list_element="empty list"
            if(type_of_list_element == dict):
                for element in payload:
                    if(type(element) == dict):
                        l.append("%|List_Of_Dictionary|%")
                        self.__iter__(element, l)
                        l.pop()
            elif(type_of_list_element == list):
                for element in payload:
                    # List of List has ||
                    list_to_string=str(element).replace(", ","$|List of Lists|$")[1:len(str(element))-1]
                    l.append(list_to_string)
                    self.list.append(l.copy())
                    l.pop()
            else:

                if(type_of_list_element=="empty list"):
                    # Empty list
                    l.append("$|Empty List|$")
                    self.list.append(l.copy())
                    l.pop()
                else:
                    # This can be list of int, list of str , list of float
                    l.append("%[[[[[[%"+str(payload)+"%]]]]]]%")
                    self.list.append(l.copy())
                    l.pop()
        else:
            # This is impossible since in https payload its not allowed
            if(isinstance(payload,tuple) or isinstance(payload,set)):
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
        for key in self.list:
            l.append(key)

class reverse_list_to_dict:
    def __init__(self,list):
        self.list=list
        self.result={}
        self.key_dictionary_mapping={} # key - Keys in final payload , value - Datatype of value

    def reverse_function(self):
        def nest_sentence(sentence):
            words = sentence
            nested_dict = {}

            # Iterate through words in reverse
            for word in reversed(words):
                # The current word becomes a key, and the previous
                # nested structure becomes its value
                nested_dict = {word: nested_dict}

            return nested_dict
        def traverse_dictionary(sentence):
            new_sentence=""
            for content in sentence:
                # List of list
                word=str(content)
                sentence=" ".join(word)
                if("$|List of Lists|$" in word):
                    content=word.split("$|List of Lists|$")
                    new_sentence+=" ["+str(content).replace(" ","")+"]"
                elif("$|Empty List|$" in word):
                    new_sentence += " []"
                elif("%[[[[[[%" in word and "%]]]]]]%" in word):
                    word=word.replace("%[[[[[[%","")
                    word=word.replace("%]]]]]]%","")
                    word.replace(" ","")
                    new_sentence += " "+word
                elif("%|List_Of_Dictionary|%" in word):
                    new_sentence += "["
                else:
                    new_sentence += " "+word

            # f.write("\n"+new_sentence+"\n")
            # f.write("#"*10+"\n")
            print(new_sentence)
            return new_sentence






        for sentence in self.list:
            # f.write("\n" + str(sentence) + "\n")
            print(traverse_dictionary(sentence))

class template_generator:
    def __init__(self,l1,mac):
        self.l=l1 # List of sentences parsed from nested_dict_to_list
        self.mac=mac
        self.create_postgresql_database()
        self.postgre_sql_tokenized_sentence()
        self.postgre_sql_token_parent_child_relation()
        self.create_s3_storage()
        self.parse_dictionary_final()

    def create_postgresql_database(self):
        # If already present with the name - Ignore / Not create Just use same
        # Else create

        # Fixed format
        database_table_name=os.environ.get("env_id")+"_token_mapping_table"
        user_name=os.environ.get("postgresql_username")
        password=os.environ.get("postgresql_password")
        host=os.environ.get("postgresql_host")
        port=os.environ.get("postgresql_port")
        database_schema=os.environ.get("postgresql_schema")

        database_url=f"postgresql://{user_name}:{password}@{host}:{port}/{database_schema}"

        self.postgresql_obj=DatabaseManager(database_url)

        # This is standard format of table
        cols={"token_id": String,"parent_child_value": String,"current_node_value": String}
        self.postgresql_obj.create_custom_table(database_table_name,cols,primary_key_defined="parent_child_value")
        self.postgresql_obj.session_local()

        # Object is ready to be used to read or write etc

    def postgre_sql_tokenized_sentence(self):
        # If already present with the name - Ignore / Not create Just use same
        # Else create

        # Fixed format
        database_table_name=os.environ.get("env_id")+"_token_sentence_mac_table"
        user_name=os.environ.get("postgresql_username")
        password=os.environ.get("postgresql_password")
        host=os.environ.get("postgresql_host")
        port=os.environ.get("postgresql_port")
        database_schema=os.environ.get("postgresql_schema")

        database_url=f"postgresql://{user_name}:{password}@{host}:{port}/{database_schema}"

        self.postgresql_tokenized_obj=DatabaseManager(database_url)



        # This is standard format of table
        cols={"tokenized_sentence": String,"mac_list": ARRAY(MACADDR)}
        self.postgresql_tokenized_obj.create_custom_table(database_table_name,cols,primary_key_defined="tokenized_sentence")
        self.postgresql_tokenized_obj.session_local()

        # Object is ready to be used to read or write etc

    def postgre_sql_token_parent_child_relation(self):
        # If already present with the name - Ignore / Not create Just use same
        # Else create

        # Fixed format
        database_table_name=os.environ.get("env_id")+"_token_parent_child_relation_table"
        user_name=os.environ.get("postgresql_username")
        password=os.environ.get("postgresql_password")
        host=os.environ.get("postgresql_host")
        port=os.environ.get("postgresql_port")
        database_schema=os.environ.get("postgresql_schema")

        database_url=f"postgresql://{user_name}:{password}@{host}:{port}/{database_schema}"

        self.postgresql_token_parent_child_relation=DatabaseManager(database_url)



        # This is standard format of table
        cols={"token_id": String,"parent_child_relation": String}
        self.postgresql_token_parent_child_relation.create_custom_table(database_table_name,cols,primary_key_defined="token_id")
        self.postgresql_token_parent_child_relation.session_local()

        # Object is ready to be used to read or write etc


    def create_s3_storage(self):

        schema_name=os.environ.get("s3_schema_name")
        self.s3_object = S3StorageManager(schema_name)

    def to_hex_key(self,index):
        """Converts 1 to 'c4ca4238a0b923820dcc509a6f75849b'"""
        # Using md5 analysis
        return hashlib.md5(str(index).encode()).hexdigest()

    def parse_dictionary(self):

        # This will iterate over sentence and if a word already has token then replace it with the single word in token ---
        '''
        generate_new_sentence

    1, This will take a sentence and for each word calculate its parent and child value
    2. checks if token id of word is in database
    3. If not present , add a data row in database (token_id, parent_child , single_word_value).
                            single_word_value - Will represent all the words belonging to token id
                                                In this way customer configs can have 1000's of port profile name , but we map all 1000s of name to one single name
        Else ,
                        Row already present , we just need to replace current wor with the word in row

        eg:

        port_usages customer1profile interface mode access
        port_usages customer2profile interface mode access
        port_usages customer3profile interface mode access
        port_usages customer4profile interface mode access
        port_usages customer5profile interface mode access

        Row - (######token######,port_usage|interface,customer1profile)


        The above 5 rows will be quivalent to 1 row - port_usages customer1profile interface mode access

        port_usages customer1profile interface mode access. ----after_function--- port_usages customer1profile interface mode access
        port_usages customer2profile interface mode access  ----after_function--- port_usages customer1profile interface mode access
        port_usages customer3profile interface mode access  ----after_function--- port_usages customer1profile interface mode access
        port_usages customer4profile interface mode access  ----after_function--- port_usages customer1profile interface mode access
        port_usages customer5profile interface mode access  ----after_function--- port_usages customer1profile interface mode access
        :return:
        '''
        token_s3_mapping={}
        token_wise_sentence = {}
        def generate_new_sentence(item):

            # Step 1 : Get the token mapping based on word parent and child mapping
            word_parent_child=[]
            for i in range(len(item)):
                current_element =item[i]
                if(i-1<0):
                    parent=empty_parent_or_empty_child_hash_value
                else:
                    parent=item[i-1]
                if(i+1>=len(item)):
                    child=empty_parent_or_empty_child_hash_value
                else:
                    child=item[i+1]
                parent_child_representation = f"{parent}|{child}"
                token_id = self.to_hex_key(parent_child_representation)
                row_present_or_not = self.postgresql_obj.find_row_by_column("parent_child_value",
                                                                            parent_child_representation)
                if(row_present_or_not):
                    pass











            # Iterate over all words and replace the words with tokens if already present
            new_item=[]
            sentence=[]
            for i in range(len(item)):
                current_element =item[i]
                if(i-1<0):
                    parent=empty_parent_or_empty_child_hash_value
                else:
                    parent=item[i-1]
                if(i+1>=len(item)):
                    child=empty_parent_or_empty_child_hash_value
                else:
                    child=item[i+1]
                parent_child_representation = f"{parent}|{child}"
                token_id = self.to_hex_key(parent_child_representation)

                if (token_id not in token_s3_mapping):
                    token_s3_mapping[token_id] = [current_element]
                else:
                    if (current_element not in token_s3_mapping[token_id]):
                        token_s3_mapping[token_id].append(current_element)

                row_present_or_not=self.postgresql_obj.find_row_by_column("parent_child_value",parent_child_representation)
                # If row not present , add it
                if(row_present_or_not==None):
                    row_obj = TokenDatabase(
                        token_id=token_id,
                        parent_child_value=parent_child_representation,
                        current_node_value=current_element
                    )
                    self.postgresql_obj.add_row(row_obj)
                    new_item.append(current_element)
                    sentence.append(str(token_id))
                else:
                    new_item.append(row_present_or_not[2])
                    sentence.append(str(row_present_or_not[0]))
            sentence.sort()
            if(tuple(sentence) not in token_wise_sentence):
                token_wise_sentence[tuple(sentence)] = [self.mac]
            else:
                token_wise_sentence[tuple(sentence)].append(self.mac)
                # Make token sentence
            return new_item

        for ind in range(len(self.l)):
            original_item=self.l[ind]
            item = generate_new_sentence(original_item)
            self.l[ind]=item.copy()
        # Add S3 data in bulk
        # s3 update
        for key in token_s3_mapping:

            token_id=key
            value=token_s3_mapping[key]
            token_word_mapping_s3 = os.environ.get("env_id") + "/token_mapping_s3/" + token_id + ".jsonl"
            data_present_in_s3 = self.s3_object.get_data(token_word_mapping_s3)
            # If None is returned it means it is empty else we need to append
            if (data_present_in_s3):
                for word in value:
                    if(word not in data_present_in_s3):
                        data_present_in_s3.append(word)
            else:
                data_present_in_s3 = value
            self.s3_object.upload_data(token_word_mapping_s3, json.dumps(data_present_in_s3))

        # token_wise_sentence={}
        # for item in self.l:
        #     sentence=[]
        #     for word in item:
        #         print(word)
        #         if(word==None):
        #             row = self.postgresql_obj.find_row_by_column("current_node_value", word)
        #         else:
        #             row=self.postgresql_obj.find_row_by_column("current_node_value",str(word))
        #         print(row)
        #         sentence.append(str(row[0]))
        #     # if(tuple(sentence) not in token_wise_sentence):
        #     #     token_wise_sentence[tuple(sentence)]=[self.mac]
        #     # else:
        #     #     token_wise_sentence[tuple(sentence)].append(self.mac)

        # Add the token_wise_sentence to s3 and satabase
        # s3 update
        for key in token_wise_sentence:
            new_sentence=key # This is a tuple
            mac_list=token_wise_sentence[key] # This is list
            f.write("\n" + str(new_sentence)+"\n")
            s=""
            for i in new_sentence:
                s+=str(token_s3_mapping[i])+" "
            f.write("\n" + s + "\n")
            f.write("##"*10)

            # S3 -- Key_name = token_sentence_mac_mapping     File_content=Mac_list
            token_sentence_mac_mapping = os.environ.get("env_id") + "/token_sentence_to_mac/" + "|".join(new_sentence) + ".jsonl"
            data_present_in_s3 = self.s3_object.get_data(token_sentence_mac_mapping)
            # If None is returned it means it is empty else we need to append
            if (data_present_in_s3):
                for mac in mac_list:
                    if(mac not in data_present_in_s3):
                        data_present_in_s3.append(mac)
            else:
                data_present_in_s3 = mac_list
            self.s3_object.upload_data(token_sentence_mac_mapping, json.dumps(data_present_in_s3))

            # Postgresql key

            existing_row=self.postgresql_tokenized_obj.find_row_by_column("tokenized_sentence","|".join(new_sentence))
            if(existing_row):
                for mac in mac_list:
                    mac_with_colon=":".join(mac[i:i+2] for i in range(0, len(mac), 2))
                    if(mac_with_colon not in existing_row[1]):
                        existing_row[1].append(mac_with_colon)
                update={"mac_list":existing_row[1]}
                self.postgresql_tokenized_obj.upsert_tokenized_data("|".join(new_sentence),existing_row[1])
            else:
                existing_row=[]
                for mac in mac_list:
                    mac_with_colon = ":".join(mac[i:i + 2] for i in range(0, len(mac), 2))
                    if(mac_with_colon not in existing_row):
                        existing_row.append(mac_with_colon)
                row_obj=TokenSentence(
                    tokenized_sentence="|".join(new_sentence),
                    mac_list=existing_row
                )
                self.postgresql_tokenized_obj.add_row(row_obj)

    def parse_dictionary_new(self):

        # This will iterate over sentence and if a word already has token then replace it with the single word in token ---
        '''
        generate_new_sentence

    1, This will take a sentence and for each word calculate its parent and child value
    2. checks if token id of word is in database
    3. If not present , add a data row in database (token_id, parent_child , single_word_value).
                            single_word_value - Will represent all the words belonging to token id
                                                In this way customer configs can have 1000's of port profile name , but we map all 1000s of name to one single name
        Else ,
                        Row already present , we just need to replace current wor with the word in row

        eg:

        port_usages customer1profile interface mode access
        port_usages customer2profile interface mode access
        port_usages customer3profile interface mode access
        port_usages customer4profile interface mode access
        port_usages customer5profile interface mode access

        Row - (######token######,port_usage|interface,customer1profile)


        The above 5 rows will be quivalent to 1 row - port_usages customer1profile interface mode access

        port_usages customer1profile interface mode access. ----after_function--- port_usages customer1profile interface mode access
        port_usages customer2profile interface mode access  ----after_function--- port_usages customer1profile interface mode access
        port_usages customer3profile interface mode access  ----after_function--- port_usages customer1profile interface mode access
        port_usages customer4profile interface mode access  ----after_function--- port_usages customer1profile interface mode access
        port_usages customer5profile interface mode access  ----after_function--- port_usages customer1profile interface mode access
        :return:
        '''
        token_s3_mapping={}
        token_wise_sentence = {}
        def generate_new_sentence(item):

            # Step 1 : Get the token mapping based on word parent and child mapping
            word_parent_child=[]
            for i in range(len(item)):
                current_element =item[i]
                if(i-1<0):
                    parent=empty_parent_or_empty_child_hash_value
                else:
                    parent=item[i-1]
                if(i+1>=len(item)):
                    child=empty_parent_or_empty_child_hash_value
                else:
                    child=item[i+1]
                parent_child_representation = f"{parent}|{child}"
                token_id = self.to_hex_key(parent_child_representation)


                row_present_or_not = self.postgresql_obj.find_row_by_column("parent_child_value",
                                                                            parent_child_representation)
                if(row_present_or_not==None):
                    word_parent_child.append(None)
                else:
                    word_parent_child.append(row_present_or_not[0])

            # Token wise parent child relation
            token_parent_child_relation=[None for i in range(len(word_parent_child))]
            for ind in range(len(word_parent_child)):
                if(word_parent_child[ind]!=None):
                    token_parent_child_relation[ind]=word_parent_child[ind]
                    continue
                current_token=None
                if(ind-1<0):
                    if(word_parent_child[ind+1]!=None):
                        row_exist=self.postgresql_token_parent_child_relation.find_row_by_column("parent_child_relation",
                                                                                       empty_parent_or_empty_child_hash_value + "|" +
                                                                                       word_parent_child[ind + 1])
                        if(row_exist):
                            current_token=row_exist[0]
                elif(ind+1>=len(word_parent_child)):
                    if(word_parent_child[ind-1]!=None):
                        row_exist = self.postgresql_token_parent_child_relation.find_row_by_column(
                            "parent_child_relation",word_parent_child[ind - 1]+"|"+empty_parent_or_empty_child_hash_value)
                        if (row_exist):
                            current_token = row_exist[0]
                else:
                    if(word_parent_child[ind-1]!=None and word_parent_child[ind+1]!=None):
                        row_exist=self.postgresql_token_parent_child_relation.find_row_by_column("parent_child_relation",word_parent_child[ind-1]+"|"+word_parent_child[ind+1])
                        if (row_exist):
                            current_token = row_exist[0]
                    else:
                        current_token=None

                token_parent_child_relation.append(current_token)

            finalized_token_list=[]
            for i in range(len(item)):
                if(token_parent_child_relation[i]!=None):
                    finalized_token_list.append(token_parent_child_relation[i])
                    continue
                current_element =item[i]
                if(i-1<0):
                    parent=empty_parent_or_empty_child_hash_value
                else:
                    parent=item[i-1]
                if(i+1>=len(item)):
                    child=empty_parent_or_empty_child_hash_value
                else:
                    child=item[i+1]
                parent_child_representation = f"{parent}|{child}"
                token_id = self.to_hex_key(parent_child_representation)
                row_present_or_not = self.postgresql_obj.find_row_by_column("parent_child_value",
                                                                            parent_child_representation)

                if(row_present_or_not==None):
                    row_obj = TokenDatabase(
                        token_id=token_id,
                        parent_child_value=parent_child_representation,
                        current_node_value=current_element
                    )
                    self.postgresql_obj.add_row(row_obj)
                    finalized_token_list.append(token_id)
                else:
                    finalized_token_list.append(row_present_or_not[0])

            # Add token table
            for i in range(len(finalized_token_list)):
                token_id=finalized_token_list[i]
                curent_word=item[i]
                if (token_id not in token_s3_mapping):
                    token_s3_mapping[token_id] = [curent_word]
                else:
                    if (curent_word not in token_s3_mapping[token_id]):
                        token_s3_mapping[token_id].append(curent_word)


                token_id_present_or_not=self.postgresql_token_parent_child_relation.find_row_by_column("token_id",token_id)
                if(token_id_present_or_not!=None):
                    continue
                if(i-1<0):
                    parent=empty_parent_or_empty_child_hash_value
                    child=finalized_token_list[i+1]
                elif(i+1>=len(finalized_token_list)):
                    child=empty_parent_or_empty_child_hash_value
                    parent=finalized_token_list[i-1]
                else:
                    parent = finalized_token_list[i - 1]
                    child = finalized_token_list[i + 1]

                row_present_or_not=self.postgresql_token_parent_child_relation.find_row_by_column("parent_child_relation",str(parent)+"|"+str(child))

                if (row_present_or_not == None):

                    row_obj = TokenParentChildReltation(
                        token_id=token_id,
                        parent_child_relation=str(parent)+"|"+str(child)
                    )
                    self.postgresql_token_parent_child_relation.add_row(row_obj)



            if(tuple(finalized_token_list) not in token_wise_sentence):
                token_wise_sentence[tuple(finalized_token_list)]=[self.mac]
            else:
                token_wise_sentence[tuple(finalized_token_list)].append(self.mac)



        for ind in range(len(self.l)):
            original_item=self.l[ind]
            generate_new_sentence(original_item)

        # Add S3 data in bulk
        # s3 update
        for key in token_s3_mapping:

            token_id=key
            value=token_s3_mapping[key]
            token_word_mapping_s3 = os.environ.get("env_id") + "/token_mapping_s3/" + token_id + ".jsonl"
            data_present_in_s3 = self.s3_object.get_data(token_word_mapping_s3)
            # If None is returned it means it is empty else we need to append
            if (data_present_in_s3):
                for word in value:
                    if(word not in data_present_in_s3):
                        data_present_in_s3.append(word)
            else:
                data_present_in_s3 = value
            self.s3_object.upload_data(token_word_mapping_s3, json.dumps(data_present_in_s3))

        # token_wise_sentence={}
        # for item in self.l:
        #     sentence=[]
        #     for word in item:
        #         print(word)
        #         if(word==None):
        #             row = self.postgresql_obj.find_row_by_column("current_node_value", word)
        #         else:
        #             row=self.postgresql_obj.find_row_by_column("current_node_value",str(word))
        #         print(row)
        #         sentence.append(str(row[0]))
        #     # if(tuple(sentence) not in token_wise_sentence):
        #     #     token_wise_sentence[tuple(sentence)]=[self.mac]
        #     # else:
        #     #     token_wise_sentence[tuple(sentence)].append(self.mac)

        # Add the token_wise_sentence to s3 and satabase
        # s3 update
        for key in token_wise_sentence:
            new_sentence=key # This is a tuple
            mac_list=token_wise_sentence[key] # This is list

            # S3 -- Key_name = token_sentence_mac_mapping     File_content=Mac_list
            token_sentence_mac_mapping = os.environ.get("env_id") + "/token_sentence_to_mac/" + "|".join(new_sentence) + ".jsonl"
            data_present_in_s3 = self.s3_object.get_data(token_sentence_mac_mapping)
            # If None is returned it means it is empty else we need to append
            if (data_present_in_s3):
                for mac in mac_list:
                    if(mac not in data_present_in_s3):
                        data_present_in_s3+=mac
            else:
                data_present_in_s3 = mac_list
            self.s3_object.upload_data(token_sentence_mac_mapping, json.dumps(data_present_in_s3))

            # Postgresql key

            existing_row=self.postgresql_tokenized_obj.find_row_by_column("tokenized_sentence","|".join(new_sentence))
            if(existing_row):
                for mac in mac_list:
                    mac_with_colon=":".join(mac[i:i+2] for i in range(0, len(mac), 2))
                    if(mac_with_colon not in existing_row[1]):
                        existing_row[1].append(mac_with_colon)
                print("####",existing_row[1])
                update={"mac_list":existing_row[1]}
                self.postgresql_tokenized_obj.upsert_tokenized_data("|".join(new_sentence),existing_row[1])
            else:
                existing_row=[]
                for mac in mac_list:
                    mac_with_colon = ":".join(mac[i:i + 2] for i in range(0, len(mac), 2))
                    if(mac_with_colon not in existing_row):
                        existing_row.append(mac_with_colon)
                print("####", existing_row)
                row_obj=TokenSentence(
                    tokenized_sentence="|".join(new_sentence),
                    mac_list=existing_row
                )
                self.postgresql_tokenized_obj.add_row(row_obj)

    def parse_dictionary_final(self):
        '''
        Steps :
        1. Iterate over all the sentences
        2. unique_sentence={}
        3. For each sentence :
                token_sentence=[]
                a.
                    Create List already_existing_token
                    Iterate over words
                    Get (parent,child) and check if it is available in database , if yes add [True,(parent,child),token_id] in list
                                                                                  else just add [False,original_word,None] in list
                b.
                    Iterate over already_existing_token
                    If item[0] is false --- Create a token with (item[i-1][1],item[i+1][1]) if it does not exist else dont create just get token_id. Add token_id to token_sentence
                    Else --- Dont create token. Add token_id to token_sentence

                add tuple(token_sentence) to unique_sentence


        :return:
        '''
        unique_sentence={}
        token_word_s3_mapping={}

        def each_sentence_parsing(sentence):
            token_sentence=[]
            already_existing_token=[]

            for ind in range(len(sentence)):
                parent=None
                child=None
                myself=sentence[ind]
                if(ind-1<0):
                    parent=empty_parent_or_empty_child_hash_value
                    child=sentence[ind+1]
                elif(ind+1>=len(sentence)):
                    child=empty_parent_or_empty_child_hash_value
                    parent=sentence[ind-1]
                else:
                    child = sentence[ind + 1]
                    parent = sentence[ind - 1]

                parent_child_representation = f"{parent}|{child}"



                token_already_present=self.postgresql_obj.find_row_by_column("parent_child_value",parent_child_representation)
                if(token_already_present):
                    already_existing_token.append([True,token_already_present[1],token_already_present[0]])
                else:
                    already_existing_token.append([False, sentence[ind], None])

            for ind in range(len(already_existing_token)):
                if(already_existing_token[ind][0]==True):
                    token_sentence.append(already_existing_token[ind][2])
                    if(already_existing_token[ind][2] not in token_word_s3_mapping):
                        token_word_s3_mapping[already_existing_token[ind][2]]=[sentence[ind]]
                    else:
                        token_word_s3_mapping[already_existing_token[ind][2]].append(sentence[ind])
                    continue

                if(ind-1<0):
                    parent=empty_parent_or_empty_child_hash_value
                    child=already_existing_token[ind+1][1]
                elif(ind+1>=len(already_existing_token)):
                    child=empty_parent_or_empty_child_hash_value
                    parent=already_existing_token[ind-1][1]
                else:
                    child = already_existing_token[ind+1][1]
                    parent = already_existing_token[ind-1][1]

                parent_child_representation = f"{parent}|{child}"
                token_id=self.to_hex_key(parent_child_representation)

                if(already_existing_token[ind][1]=="networks"):
                    print(parent_child_representation)

                token_exist=self.postgresql_obj.find_row_by_column("parent_child_value",parent_child_representation)
                if(token_exist):
                    token_sentence.append(token_exist[0])
                    # Add current word to s3 file
                    if(token_exist[0] not in token_word_s3_mapping):
                        token_word_s3_mapping[token_exist[0]]=[sentence[ind]]
                    else:
                        token_word_s3_mapping[token_exist[0]].append(sentence[ind])
                else:

                    row=TokenDatabase(
                        token_id=token_id,
                        parent_child_value=parent_child_representation,
                        current_node_value=sentence[ind]
                        )
                    self.postgresql_obj.add_row(row)
                    token_sentence.append(token_id)
                    if(token_id not in token_word_s3_mapping):
                        token_word_s3_mapping[token_id]=[sentence[ind]]
                    else:
                        token_word_s3_mapping[token_id].append(sentence[ind])
                f.write("\n" + "$$" * 10 + "\n")
                f.write(str(token_exist)+" "+parent_child_representation+"\n")
                f.write("\n\n")
            if(tuple(token_sentence) not in unique_sentence):
                unique_sentence[tuple(token_sentence)]=[self.mac]
            else:
                unique_sentence[tuple(token_sentence)].append(self.mac)

            f.write("\n" + str("|".join(token_sentence)) + "\n")
            f.write("\n" + str(sentence) + "\n")
            f.write("\n" + "$$" * 10 + "\n")

        for sentence in self.l:
            if(sentence[0] in excluded_keys):
                continue
            each_sentence_parsing(sentence)

        # Write to s3 - Token to all words mapping
        for key in token_word_s3_mapping:

            token_id=key
            value=token_word_s3_mapping[key]
            token_word_mapping_s3 = os.environ.get("env_id") + "/token_mapping_s3/" + token_id + ".jsonl"
            data_present_in_s3 = self.s3_object.get_data(token_word_mapping_s3)
            # If None is returned it means it is empty else we need to append
            if (data_present_in_s3):
                for word in value:
                    if(word not in data_present_in_s3):
                        data_present_in_s3.append(word)
            else:
                data_present_in_s3 = value
            self.s3_object.upload_data(token_word_mapping_s3, json.dumps(data_present_in_s3))



        for key in unique_sentence:
            new_sentence=key # This is a tuple
            mac_list=unique_sentence[key] # This is list
            # S3 -- Key_name = token_sentence_mac_mapping     File_content=Mac_list
            token_sentence_mac_mapping = os.environ.get("env_id") + "/token_sentence_to_mac/" + "|".join(new_sentence) + ".jsonl"
            data_present_in_s3 = self.s3_object.get_data(token_sentence_mac_mapping)
            # If None is returned it means it is empty else we need to append
            if (data_present_in_s3):
                for mac in mac_list:
                    if(mac not in data_present_in_s3):
                        data_present_in_s3.append(mac)
            else:
                data_present_in_s3 = mac_list
            self.s3_object.upload_data(token_sentence_mac_mapping, json.dumps(data_present_in_s3))

            # Postgresql key

            existing_row=self.postgresql_tokenized_obj.find_row_by_column("tokenized_sentence","|".join(new_sentence))
            if(existing_row):
                for mac in mac_list:
                    mac_with_colon=":".join(mac[i:i+2] for i in range(0, len(mac), 2))
                    if(mac_with_colon not in existing_row[1]):
                        existing_row[1].append(mac_with_colon)
                update={"mac_list":existing_row[1]}
                self.postgresql_tokenized_obj.upsert_tokenized_data("|".join(new_sentence),existing_row[1])
            else:
                existing_row=[]
                for mac in mac_list:
                    mac_with_colon = ":".join(mac[i:i + 2] for i in range(0, len(mac), 2))
                    if(mac_with_colon not in existing_row):
                        existing_row.append(mac_with_colon)
                row_obj=TokenSentence(
                    tokenized_sentence="|".join(new_sentence),
                    mac_list=existing_row
                )
                self.postgresql_tokenized_obj.add_row(row_obj)



        # all_sentences={}
        # for i in self.l:
        #     all_sentences[" ".join(i)]=1
        #
        # def recur(token_sentence,index,l):
        #     if(index>=len(token_sentence)):
        #         print(l)
        #         return
        #
        #     for word in token_word_s3_mapping[token_sentence[index]]:
        #
        #





class summary_template:
    def __init__(self):
        self.create_postgresql_database()
        self.postgre_sql_tokenized_sentence()
        self.create_s3_storage()
        #self.model = SentenceTransformer('all-MiniLM-L6-v2')
        #self.get_unique_sentences()

    def create_postgresql_database(self):
        # If already present with the name - Ignore / Not create Just use same
        # Else create

        # Fixed format
        database_table_name = os.environ.get("env_id") + "_token_mapping_table"
        user_name = os.environ.get("postgresql_username")
        password = os.environ.get("postgresql_password")
        host = os.environ.get("postgresql_host")
        port = os.environ.get("postgresql_port")
        database_schema = os.environ.get("postgresql_schema")

        database_url = f"postgresql://{user_name}:{password}@{host}:{port}/{database_schema}"

        self.postgresql_obj = DatabaseManager(database_url)

        # This is standard format of table
        cols = {"token_id": String, "parent_child_value": String}
        self.postgresql_obj.create_custom_table(database_table_name, cols, primary_key_defined="parent_child_value")
        self.postgresql_obj.session_local()

        # Object is ready to be used to read or write etc

    def postgre_sql_tokenized_sentence(self):
        # If already present with the name - Ignore / Not create Just use same
        # Else create

        # Fixed format
        database_table_name = os.environ.get("env_id") + "_token_sentence_mac_table"
        user_name = os.environ.get("postgresql_username")
        password = os.environ.get("postgresql_password")
        host = os.environ.get("postgresql_host")
        port = os.environ.get("postgresql_port")
        database_schema = os.environ.get("postgresql_schema")

        database_url = f"postgresql://{user_name}:{password}@{host}:{port}/{database_schema}"

        self.postgresql_tokenized_obj = DatabaseManager(database_url)

        # This is standard format of table
        cols = {"tokenized_sentence": String, "mac_list": ARRAY(MACADDR)}
        self.postgresql_tokenized_obj.create_custom_table(database_table_name, cols,
                                                          primary_key_defined="tokenized_sentence")
        self.postgresql_tokenized_obj.session_local()

        # Object is ready to be used to read or write etc

    def create_s3_storage(self):
        schema_name = os.environ.get("s3_schema_name")
        self.s3_object = S3StorageManager(schema_name)

    def to_hex_key(self, index):
        """Converts 1 to 'c4ca4238a0b923820dcc509a6f75849b'"""
        # Using md5 analysis
        return hashlib.md5(str(index).encode()).hexdigest()


    def get_unique_sentences(self):
        self.new_token_to_words_mapping={}
        for token in self.postgresql_obj.list_all_rows():
            f.write("\n"+str(token[0])+"   "+str(token[1])+"\n")
            url=os.environ.get("env_id") + "/token_mapping_s3/" + token[0] + ".jsonl"
            sen=self.s3_object.get_data(url)
            # f.write("\n"+str(set(sen))+"\n")
            # f.write("\n"+str(self.get_top_10_percent_non_similar_words(sen[0],set(sen)))+"\n")
            # f.write("\n" + "#" * 20 + "\n")
            self.new_token_to_words_mapping[str(token[0])]=self.get_top_10_percent_non_similar_words(sen[0],set(sen))

        c=1
        for token_sentence in self.postgresql_tokenized_obj.list_all_rows():
            sentence=token_sentence[0].split("|")
            group={}
            self.expand_token_to_original_sentence(sentence,0,[],group)
            f.write("\n"+"Group :"+str(c)+"\n")
            f.write("\n"+token_sentence[0]+"\n")
            c+=1
            for i in group:
                f.write("|=\n"+str(i)+"\n")
            f.write("\n"+"##"*10+"\n")



    def expand_token_to_original_sentence(self,sentence,index,l,group):
        if(index>=len(sentence)):
            group[tuple(l)]=sentence.copy()
            return

        list_of_words=self.new_token_to_words_mapping[sentence[index]]
        if(len(l)>0):
            if(l[-1] in parents_of_keys_which_are_user_input):
                new_list=list(self.new_token_to_words_mapping[sentence[index]])
                list_of_words=new_list[:min(len(new_list),2)]
        for word in list_of_words:
            l.append(word)
            self.expand_token_to_original_sentence(sentence,index+1,l,group)
            l.pop()


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



l=[]
payload={
    "shreyas2":{
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
            "speed": "10m",
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
    "shreyas":{
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
    "ravi1":{
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
    "ravi2":{
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
    "ravi3":{
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

    "hammad":{
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
payload_new={
    "p1":{
        "a1":{
            "b1":{
                "c1":1,
                "c2":"string",
                "c3":1.5,
                "c4":["new"],
                "c5":[["newstring1","newstring2"]]
            },
            "b2":{
                "c6":True,
                "c7":None
            },
            "b3":[
                {
                    "c8":8,
                    "c9":9
                },
{
                    "c10":10,
                    "c11":11
                }
            ]
        }
    },

"p2":{
        "a2":{
            "b1":{
                "c1":1,
                "c2":"string",
                "c3":1.5,
                "c4":["new"],
                "c5":[["newstring1","newstring2"]]
            },
            "b2":{
                "c6":True,
                "c7":None
            },
            "b6":[
                {
                    "c8":8,
                    "c9":9
                },
{
                    "c10":10,
                    "c11":11
                }
            ]
        }
    }
}


# for i in payload:
#     mac=payload[i]["mac"]
#     l=[]
#     obj=nested_dict_to_list()
#     obj.__iter__(payload[i],l)
#     obj_new=template_generator(obj.list,mac)



obj=summary_template()
# a=obj.postgresql_tokenized_obj.list_all_rows()
#
b=obj.postgresql_obj.list_all_rows()

# reverse_list_to_dict(obj.unique_sentences_all)


f1=open("temporary2.json","w")
token_filtered={}
for i in b:
    url=os.environ.get("env_id") + "/token_mapping_s3/" + i[0] + ".jsonl"
    f1.write("###########################")
    f1.write("\nToken :"+i[0]+"\n")
    f1.write("\n"+str(type(i[0]))+"\n")
    f1.write("\nS3 File : "+str(set(obj.s3_object.get_data(url))))
    data=set(obj.s3_object.get_data(url))
    list=[]
    for word in data:
        list.append(str(word))
    list.sort()
    if(tuple(list) not in token_filtered):
        token_filtered[tuple(list)]=[i[0]]
    else:
        token_filtered[tuple(list)].append(i[0])
    f1.write("###########################")

token_final_filtered={}
for i in token_filtered:
    for j in range(0,len(token_filtered[i])):
        token=token_filtered[i][j]
        token_final_filtered[token]=token_filtered[i][0]


token_sentence_unique_final={}
for i in obj.postgresql_tokenized_obj.list_all_rows():
    new_sentence=[]
    for j in i[0].split("|"):
        new_sentence.append(token_final_filtered[j])
    if(tuple(new_sentence) not in token_sentence_unique_final):
        token_sentence_unique_final[tuple(new_sentence)]=1
print(len(token_sentence_unique_final))



# print(len(a))
# print(len(b))
# print(len(a))
# for i in a:
#     print(i)
# obj.get_unique_sentences()