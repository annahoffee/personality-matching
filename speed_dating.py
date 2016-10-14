#!/usr/bin/env python3

import sys, os
import math
import numpy as np
import scipy
import pandas as pd
import sklearn
from sklearn.preprocessing import Imputer
from sklearn.neighbors import NearestNeighbors
from preprocessingClasses import ImportData, Person
from KNNClasses import FindMatchQualities
from sklearn.svm import SVC
from runModel import RunTest
from findKNN import findKNearestNeighbors
from testingClasses import CompareSimilarPersonTest, SVMClassification
from neuralNetClasses import RunNeuralNet
import copy
import pickle
import datetime



def findInputPersonFans( input_person_iid, speed_daters_list):

    ## create list of people that liked the input_person
    input_person_fans = {}
    input_person_not_fans = {}

    for speed_dater in speed_daters_list:
        speed_dater_likes_iids = []
        speed_dater_dislikes_iids = []
        ##  split up the iid's by weather  or not the speed_dater liked them
        for iid in speed_dater.partner_dict.keys():
            if speed_dater.partner_dict[iid] == 0:
                speed_dater_dislikes_iids.append(iid)
            else:
                speed_dater_likes_iids.append(iid)

        if input_person_iid in list(speed_dater_likes_iids): # if this speed dater liked the input_person
            categorical_variables  = list(speed_dater.trait_vector.get(["gender", 'black', 'white', 'latino', 'asian', 'native_american', 'other']))
            numeric_variables = list(speed_dater.trait_vector.get(["age",  "field_cd", "career_c", "go_out", "sports", "tvsports", "exercise", "dining", "art", "hiking", "gaming", "clubbing", "reading", "movies", "concerts", "music", "yoga"]))
            input_person_fans[speed_dater.iid] = [categorical_variables,  numeric_variables]

        elif input_person_iid in list(speed_dater_dislikes_iids):
            categorical_variables  = list(speed_dater.trait_vector.get(["gender", 'black', 'white', 'latino', 'asian', 'native_american', 'other']))
            numeric_variables = list(speed_dater.trait_vector.get(["age", "field_cd", "career_c", "go_out", "sports", "tvsports", "exercise", "dining", "art", "hiking", "gaming", "clubbing", "reading", "movies", "concerts", "music", "yoga"]))
            input_person_not_fans[speed_dater.iid] =  [categorical_variables, numeric_variables]

    return([[input_person_fans], [input_person_not_fans]])



def main():

    args = sys.argv
    testing = int(args[1])

    ## initialize the ImportData class, upload the csv file, create the list of speed dater Person objects
    speed_date_data = ImportData("speed_dating_data.csv")
    speed_date_data.uploadFile()

    if testing == 1: ## if the user is just running the model for an input person, not training it

        input_trait_vector = args[2:22]
        pickle_file_name = args[23]
        testing_object = RunTest(pickle_file_name, input_trait_vector, testing)
        predicted_qualities = testing_object.predicted_qualities_dict
        print(predicted_qualities)
        return

    speed_daters_list_additions = []
    all_real_iids = speed_date_data.distinct_iids
    svm = "no"
    results = np.zeros(2)
    nn_counter = 0
    nn_dictionary = {}
    for IID in all_real_iids: #loop through all the people in the speed dating data
        if IID < 0: ## if this is a fake person
            continue
        ###################################################################
        ################## data pre-processing/set up #####################
        ###################################################################
        print(IID)
        ## set aside a person to be the input
        speed_date_data.seperateInputPerson(IID)

        ## create a list of Person objects corresponding to every person except the input person
        speed_date_data.createSpeedDatersList()

        ## retrieve the input person Person object
        speed_daters_list = speed_date_data.speed_daters_list

        ## add in any speed_daters that were added previously
        for x in range(len(speed_daters_list_additions)):

            speed_daters_list.append(speed_daters_list_additions[x])

        ## create a Person object out of the speed_dater with IID
        input_person = speed_date_data.input_person

        ## make dictionary for the people that disliked  the input person and one for
        ## the people that liked the input person
        ############## THE PROBLEM IS HERE BIG FUCKING SUPRISE
        opinions_of_input_person = findInputPersonFans(input_person.iid, speed_daters_list)

        ## WLOG input_person_fans is a dictionary with keys = iid's of  people  that liked the input person, and values are
        ## their trait_vector split into numeric and categorical data
        input_person_fans = opinions_of_input_person[0][0]
        input_person_not_fans = opinions_of_input_person[1][0]

        ## if a speed_dater had only fans or not fans then I can't create an SVM
        if len(input_person_fans.keys()) == 0 or len(input_person_not_fans.keys()) == 0:
            continue

        #############################################################################
        ################# create the KNN model ######################################
        #############################################################################

        ## combine the ImportData class and the input_person object to do a knn search
        nearest_neighbors_dict = findKNearestNeighbors(speed_daters_list,  input_person)

        ## combine the list of neighbors of the  input person with the speed_daters_list  to find the
        ## personality qualities most likely to be found in people that like the input_person

        match_qualities = FindMatchQualities(nearest_neighbors_dict, speed_daters_list, input_person_fans, testing)
        match_qualities.identifyInterestedPeople()

        ## retrieve the trait_list variable from the ImportData class

        trait_names_helper = speed_daters_list[0]
        trait_names_helper.returnTraitList()
        trait_list = trait_names_helper.trait_names


        match_qualities.identifyOutputQualities(trait_list, 1, nn_counter)
        nn_counter += 1
        nn_dictionary[nn_counter] =  match_qualities.interested_iids

        ## calculate predicted variable labels/values
        predicted_qualities_dict  = match_qualities.output_qualities


        ##############################################################################
        #################### create the SVM ##########################################
        ##############################################################################

        if svm != "no":
            svm_classification_model = SVMClassification(input_person_fans, input_person_not_fans, IID)
            svm_classification_model.prepareInputVectors()
            svm_classification_model.runSVM(predicted_qualities_dict, trait_list)
            for x in range(len(svm_classification_model.additions_to_speed_daters_list)):
                speed_daters_list_additions.append(svm_classification_model.additions_to_speed_daters_list[x])

        elif svm == "no":
            test = CompareSimilarPersonTest(input_person_fans, input_person_not_fans, predicted_qualities_dict, input_person.iid, trait_list )
            results[0] += test.count_results[0]
            results[1] += test.count_results[1]
            for x in range(len(test.additions_to_speed_daters_list)):
                speed_daters_list_additions.append(test.additions_to_speed_daters_list[x])


    print("the results are...")
    print(results)
    ## now store the "trained" speed_daters_list
    final_speed_date_data = ImportData("speed_dating_data.csv")
    final_speed_date_data.uploadFile()
    final_speed_date_data.createSpeedDatersList()
    final_speed_daters_list = final_speed_date_data.speed_daters_list

    for x in range(len(speed_daters_list_additions)):
        final_speed_daters_list.append(speed_daters_list_additions[x])

    today = datetime.date.today()
    filename = "%d%d%d_speed_daters_list.pickle" % (today.year, today.month, today.day)
    pickle.dump(final_speed_daters_list, open(filename, "wb"))



if __name__ == "__main__":
    main()
