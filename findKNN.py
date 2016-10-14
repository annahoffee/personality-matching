


import sys, os
import math
import numpy as np
import scipy
import pandas as pd
import sklearn
from sklearn.preprocessing import Imputer
from sklearn.neighbors import NearestNeighbors
from preprocessingClasses import ImportData, Person
from testingClasses import SVMClassification, CompareSimilarPersonTest
from KNNClasses import FindMatchQualities
from sklearn.svm import SVC
from runModel import RunTest
import copy


def findKNearestNeighbors(speed_daters_list, input_person):

    ## initialize the NearestNeighbors object from sklearn
    knn_object = NearestNeighbors(n_neighbors=math.ceil(len(speed_daters_list)/10), algorithm="auto")

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
    #print("distances \n")
    #print(sorted(distances))


    ## now store the iid's of  the neighbors and thier corresponding distances in a dictionary
    nearest_neighbors_dict = {}

    for x in range(len(neighbors)):
        nearest_neighbors_dict[float(speed_daters_list[neighbors[x]].iid)] = distances[x]

    return(nearest_neighbors_dict)
