
import sys, os
import math
import numpy as np
import scipy
import pandas as pd
import sklearn
from sklearn.preprocessing import Imputer
from sklearn.neighbors import NearestNeighbors
import pickle
from preprocessingClasses import ImportData, Person
from KNNClasses import FindMatchQualities




def findKNearestNeighbors(speed_daters_list, input_person):

    ## initialize the NearestNeighbors object from sklearn
    knn_object = NearestNeighbors(n_neighbors=math.ceil(len(speed_daters_list)/5), algorithm="auto")


    ## initialize the Imputer object from sklearn
    fix_missing_data = Imputer( missing_values="NaN", strategy="most_frequent", axis=1)

    ## prepare the data from the speed_dater Person objects to be put into knn_object
    trait_vector_lists = []

    for speed_dater in speed_daters_list:
        if int(speed_dater.trait_vector["gender"]) !=  int(input_person.trait_vector["gender"]):
            continue
        try:
            clean_trait_vector = fix_missing_data.fit_transform(speed_dater.trait_vector.reshape(1, -1))
        except:
            print(speed_dater.trait_vector)
        clean_trait_vector = clean_trait_vector.tolist()
        clean_trait_vector = clean_trait_vector[0]
        trait_vector_lists.append(clean_trait_vector)


    ## fit the NearestNeighbors object to the data
    knn_object.fit(trait_vector_lists)

    ## finally, find the k nearest neighbors of the  input_person
     ## impute the input person's data incase some of it is missing
    clean_input_person = fix_missing_data.transform(input_person.trait_vector.reshape(1, -1))
    find_neighbors = knn_object.kneighbors([clean_input_person[0].tolist()], return_distance=True)
    distances = find_neighbors[0][0]
    neighbors = find_neighbors[1][0]

    ## now store the iid's of  the neighbors and thier corresponding distances in a dictionary
    nearest_neighbors_dict = {}

    for x in range(len(neighbors)):
        nearest_neighbors_dict[float(speed_daters_list[neighbors[x]].iid)] = distances[x]

    return(nearest_neighbors_dict)



class RunTest(object):
    def __init__(self, pickle_file_name, input_trait_vector, testing):

        self.speed_daters_list = pickle.load(open(pickle_file_name, "rb"))
        input_trait_vector = pd.Series(input_trait_vector, index=["age", "race", "gender", "field_cd", "career_c", "income", "go_out", "sports", "tvsports", "exercise", "dining", "art", "hiking", "gaming", "clubbing", "reading", "movies", "concerts", "music", "yoga"])
        self.input_person = Person(input_trait_vector, {}, -1000)
        nearest_neighbors_dict = findKNearestNeighbors(self.speed_daters_list,  self.input_person)
        match_qualities = FindMatchQualities(nearest_neighbors_dict, self.speed_daters_list, testing)
        match_qualities.identifyInterestedPeople()

        trait_names_helper = self.speed_daters_list[0]
        trait_names_helper.returnTraitList()
        trait_list = trait_names_helper.trait_names

        match_qualities.identifyOutputQualities(trait_list)

        ## calculate predicted variable labels/values
        self.predicted_qualities_dict  = match_qualities.output_qualities
