

import sys, os
import math
import numpy as np
import scipy
import pandas as pd
import sklearn
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import Imputer

import pickle


class RunNeuralNet(object):
    def __init__(self, input_matrix, input_person_fans, nn_counter):
        self.input_matrix = input_matrix
        self.nn_counter = nn_counter
        keys = np.array(list(input_person_fans.keys()))
        self.target_person = input_person_fans[keys[0]] ## pick someone randomly for now
        self.field_vars= set([5, 2, 8, 10, 4, 17, 1, 16, 13, 7, 3, 11, 9, 6, 14, 15, 18, 12])
        self.career_vars = set([4, 5, 17, 1, 7, 8, 14, 12, 13, 9, 3, 11, 16, 2, 6, 10, 15])
        arr = []
        for vec in self.target_person:
            for element in vec:
                arr.append(element)
        self.target_person = np.array(arr)

        ################ now fix the missing data #################
        fix_missing_data_matrix = Imputer( missing_values="NaN", strategy="mean", axis=1)
        clean_matrix = fix_missing_data_matrix.fit_transform(self.input_matrix)
        fix_missing_data_vector = Imputer(missing_values="NaN", strategy="mean", axis=1)
        clean_vector = fix_missing_data_vector.fit_transform(self.target_person.reshape(1, -1))
        clean_vector = clean_vector.tolist()
        clean_vector = np.array(clean_vector[0])

        self.NN = MLPClassifier(hidden_layer_sizes=(2, 2), activation="identity", solver="lbfgs", max_iter=500)
        try:
            self.NN.fit(clean_matrix, clean_vector)
            self.output_traits = self.NN.predict(clean_matrix)
            self.test = 1
            self.checkNNoutput()
            self.saveNN()

        except ValueError:
            print("not using nn")
            self.test = 0

    def saveNN(self):
        filename = "neural_net_%s.pickle" % self.nn_counter
        pickle.dump(self.NN, open(filename, "wb"))


    def checkNNoutput(self):
        self.output_traits[8] = int(self.output_traits[8])
        self.output_traits[9] = int(self.output_traits[9])
        if self.output_traits[8] not in self.field_vars:
            self.output_traits[8] = 7
        if self.output_traits[9] not in self.career_vars:
            self.output_traits[9]= 7
