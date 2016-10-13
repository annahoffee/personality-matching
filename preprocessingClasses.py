
import sys, os
import math
import numpy as np
import scipy
import pandas as pd
import random
import sklearn
import copy


class Person(object):
    def __init__(self, trait_vector, partner_dict, iid):

        self.partner_dict = partner_dict ## {partner_iid: decision , ...}
        self.iid = float(iid)
        self.trait_vector = trait_vector
        self.field_translation_dict = {5:1, 2:2, 8:3, 10:4, 4:5, 17:6, 1:7, 16:8, 13:9, 7:10, 3:11, 11:12, 9:13, 6:14, 14:15, 15:16, 18:17, 12:18}
        self.career_translation_dict = {4:1, 5:2, 17:3, 1:4, 7:5, 8:6, 14:7, 12:8, 13:9, 9:10, 3:11, 11:12, 16:13, 2:14, 6:15, 10:16, 15:17}
        if not math.isnan(self.trait_vector["field_cd"]):
            self.trait_vector["field_cd"] = self.field_translation_dict[int(self.trait_vector["field_cd"])]
        if not math.isnan(self.trait_vector["career_c"]):
            self.trait_vector["career_c"] = self.career_translation_dict[int(self.trait_vector["career_c"])]

        ## create a dummy variable for race if it wasn't already created ( it would already be  created if  this is a fake person)
        index_list = np.array(self.trait_vector.index)
        if  len(index_list) == 19 :
            self.race = self.trait_vector[1]
            race_dummy_variable = pd.Series([int(1 == self.race), int(2 == self.race), int(3 == self.race), int(4 == self.race) , int(5 ==self.race), int(6 == self.race)], index=['black', 'white', 'latino', 'asian', 'native_american', 'other'])
            self.trait_vector = self.trait_vector.append(race_dummy_variable)
            self.trait_vector = self.trait_vector.drop("race", axis=0)

    def returnTraitList(self):
        self.trait_names = list(self.trait_vector.index)


    def calculateWeight(self, distances):
         weight_output = 1
         for d in distances:
             weight_output = weight_output*d
         self.weight=weight_output


class ImportData(object):
    def __init__(self, input_filename):
        self.input_filename = input_filename
        self.trait_list = ["age", "race", "gender", "field_cd", "career_c", "go_out", "sports", "tvsports", "exercise", "dining", "art", "hiking", "gaming", "clubbing", "reading", "movies", "concerts", "music", "yoga"]


    def uploadFile(self):
        try:
            self.original_input_file = pd.read_csv(self.input_filename, encoding="latin1")
            self.distinct_iids = self.original_input_file["iid"].unique()
        except:
            print("error trying to upload %s " % self.input_filename)
            sys.exit()

    def seperateInputPerson(self, IID):

        ## remove the input person from the data set so as not to over train
        input_person_iid = IID
        self.input_file  = copy.deepcopy(self.original_input_file)
        input_indices = self.input_file.loc[self.input_file["iid"] == input_person_iid].index.tolist()
        input_person_data = self.input_file.loc[input_indices,: ]

        self.input_file = self.input_file.drop(self.input_file.index[input_indices])

        ## now use that person's information to make him a Person object

        input_trait_list = input_person_data.loc[input_person_data.index[[1]], self.trait_list].iloc[0, :]
        input_partner_information = {}
        for x in range(input_person_data.shape[0]):
            input_partner_information[list(input_person_data.loc[input_person_data.index[[x]], "pid"])[0]] = list(input_person_data.loc[input_person_data.index[[x]], "dec"])[0]

        ## now return a Person objecct that represents the input person

        self.input_person = Person(input_trait_list, input_partner_information, input_person_iid)

    def createSpeedDatersList(self):
        ## get list of distinct  person iid's from data file
        try: ## if tihs is the final speed daters list being created then it won't have this
            distinct_iids = self.input_file["iid"].unique()
        except AttributeError:
            self.input_file = self.original_input_file
            distinct_iids = self.input_file["iid"].unique()


        self.speed_daters_list = []
        # fill the  speed_daters_list with Person objects corresponding to each iid
        for iid in distinct_iids:

            row_number_traits = self.input_file[self.input_file["iid"] == iid].index[0]

            ## since a person's traits are constant, it works to just grab the 0th element
            trait_information = self.input_file.loc[row_number_traits, self.trait_list]

            row_numbers_partners = self.input_file[self.input_file["iid"] == iid].index
            ## since we need information for all the partners a person met, we must grab all the elements

            partner_information = {}
            ## partner_information := { pid: decison}

            for x in row_numbers_partners:
                partner_information[self.input_file.loc[row_numbers_partners, "pid"][x]] = self.input_file.loc[row_numbers_partners, "dec"][x]
            

            self.speed_daters_list.append(Person(trait_information, partner_information, float(iid)))
