

import sys, os
import math
import numpy as np
import scipy
import pandas as pd
import random
import sklearn
from sklearn.svm import SVC
from sklearn.preprocessing import Imputer
from preprocessingClasses import Person



class CompareSimilarPersonTest(object):
    def __init__(self, input_person_fans, input_person_not_fans, predicted_qualities_dict, iid, trait_names):
        self.input_person_fans = input_person_fans
        self.input_person_not_fans = input_person_not_fans
        self.predicted_qualities_dict = predicted_qualities_dict
        self.trait_names = trait_names
        self.input_person_iid = iid
        self.categorical_labels = ["gender",'black', 'white', 'latino', 'asian', 'native_american', 'other']
        self.numeric_labels = ["age", "field_cd", "career_c", "go_out", "sports", "tvsports", "exercise", "dining", "art", "hiking", "gaming", "clubbing", "reading", "movies", "concerts", "music", "yoga"]
        self.comparison_scores = []
        self.count_results = np.zeros(2)
        self.additions_to_speed_daters_list = []

        for fan_key in self.input_person_fans:  ## loop through the people that liked the input_person
            categorical_vars =self.input_person_fans[fan_key][0]
            numeric_vars = self.input_person_fans[fan_key][1]
            categorical_score = 0
            numeric_score = 0
            for idx, var in enumerate(self.categorical_labels): ## loop through the categorical variables
                categorical_score += int(abs(self.predicted_qualities_dict[var] - categorical_vars[idx]))
            for idx, var in enumerate(self.numeric_labels):
                if math.isnan(abs(self.predicted_qualities_dict[var] - numeric_vars[idx] )):
                    continue
                numeric_score += abs(self.predicted_qualities_dict[var] - numeric_vars[idx] )

            total_score = categorical_score + numeric_score ## weight the scored according to their proportion of the variables
            self.comparison_scores.append([ fan_key, total_score])

        for not_fan_key in self.input_person_not_fans:  ## loop through the people that didn't like the input_person
            categorical_vars =self.input_person_not_fans[not_fan_key][0]
            numeric_vars = self.input_person_not_fans[not_fan_key][1]
            categorical_score = 0
            numeric_score = 0
            for idx, var in enumerate(self.categorical_labels): ## loop through the categorical variables
                categorical_score += int(abs(self.predicted_qualities_dict[var] - categorical_vars[idx]))
            for idx, var in enumerate(self.numeric_labels):
                if math.isnan(abs(self.predicted_qualities_dict[var] - numeric_vars[idx] )):
                    continue
                numeric_score += abs(self.predicted_qualities_dict[var] - numeric_vars[idx] )

            total_score = categorical_score + numeric_score ## weight the scored according to their proportion of the variables
            self.comparison_scores.append([ not_fan_key, total_score])

            ## compute which real person is closest to the fake person
        max_score = [1, self.comparison_scores[0][1]]
        for x in range(len(self.comparison_scores)):

            if self.comparison_scores[x][1] <= max_score[1]:
                max_score[0] = self.comparison_scores[x][0]
                max_score[1] = self.comparison_scores[x][1]

        if max_score[0] in self.input_person_fans.keys():
            # it worked!
            self.count_results[0] +=  1
            print("it worked")
            ## create a Person from the fake person to add to the data set of speed_daters
            self.createSeries()
            self.additions_to_speed_daters_list.append(Person(self.knn_predictions_series, {self.input_person_iid: 1}, float(self.input_person_iid*-1)))

        elif max_score[0] in self.input_person_not_fans.keys():
            self.count_results[1] += 1

    def createSeries(self):
        self.knn_predictions_series = []
        for var in self.trait_names:
            self.knn_predictions_series.append(self.predicted_qualities_dict[var])
        self.knn_predictions_series = pd.Series(self.knn_predictions_series, index=self.trait_names)



class SVMClassification(object):
    def __init__(self, input_person_fans, input_person_not_fans, input_person_iid):
        self.input_person_fans = input_person_fans
        self.input_person_not_fans = input_person_not_fans
        self.input_person_iid = input_person_iid
        self.final_results_dict = {}
        self.additions_to_speed_daters_list = []
        ## initialize the SVM from sklearn
        self.svm_model = SVC(kernel="sigmoid")
        self.count_results = np.zeros(2)
        self.fixes = 0

    def prepareInputVectors(self):

        self.svm_input_vectors = []
        self.svm_input_labels =  []
        numeric_data_means = np.zeros(16)

        ### first calculate the mean of all the numeric variable so you can subtract it off
        """
        for key_iid in self.input_person_fans.keys(): # loop over  people in input_person_fans
            for x in range(16): # loop over the numeric variables
                numeric_data_means[x] += self.input_person_fans[key_iid][1][x]
        for key_iid in self.input_person_not_fans.keys(): # loop over  people in input_person_fans
            for x in range(16): # loop over the numeric variables
                numeric_data_means[x] += self.input_person_not_fans[key_iid][1][x]

        total_number_people = len(self.input_person_fans.keys()) + len(self.input_person_fans.keys())
        numeric_data_means = numeric_data_means/total_number_people
        """

        ## now prepare the vectors
        for key_iid in self.input_person_fans.keys():
            categorical_data = self.input_person_fans[key_iid][0]
            numeric_data = self.input_person_fans[key_iid][1] #- numeric_data_means
            self.svm_input_vectors.append(categorical_data + list(numeric_data))
            self.svm_input_labels.append(1)

        for key_iid in self.input_person_not_fans.keys():
            categorical_data = self.input_person_not_fans[key_iid][0]
            numeric_data = self.input_person_not_fans[key_iid][1] #- numeric_data_means
            self.svm_input_vectors.append(categorical_data + list(numeric_data))
            self.svm_input_labels.append(0)

        ## note that  we are letting 1 := speed_dater liked input person
        ## 0 := speed_dater didn't  like input person

    def svmDidNotAgreeWithKNN(self):
        max_iterations = 500
        i = 0
        while(i < max_iterations):
            variance = 1
            noise = np.random.normal(0, variance, len(self.knn_predictions_vector))
            for v in range(len(noise)):
                self.knn_predictions_vector[v] += noise[v]
            ## now check to see if the SVM will classify the vector as liking the input_person
            svm_prediction = self.svm_model.predict(np.array(self.knn_predictions_vector).reshape(1, -1))
            if svm_prediction[0] == 1:
                ## now we've found a match for the input_person
                self.fixes += 1
                self.final_results_dict[self.input_person_iid] = self.knn_predictions_vector
                break
            variance += .2
            i += 1
            if i == 500:
                self.final_results_dict[self.input_person_iid]= None


    def runSVM(self, predicted_qualities_dict, trait_list):

        ## impute the missing data before putting it in the sklearn svm
        ## initialize the imputer from sklearn
        fix_missing_data = Imputer( missing_values="NaN", strategy="mean", axis=1)
        for v in range(len(self.svm_input_vectors)):
            clean_vector = fix_missing_data.fit_transform(np.array(self.svm_input_vectors[v]).reshape(1, -1))
            clean_vector = clean_vector.tolist()
            clean_vector = clean_vector[0]
            self.svm_input_vectors[v] = clean_vector

        ## train the SVM
        self.svm_model.fit(self.svm_input_vectors, self.svm_input_labels)
        ### get the predicted_qualities_dict ready to be  classified by the now trained svm

        self.knn_predictions_vector = []
        for variable in trait_list:
            self.knn_predictions_vector.append(predicted_qualities_dict[variable])

        ## give  the imaginary person to the svm to classify
        svm_prediction = self.svm_model.predict(np.array(self.knn_predictions_vector).reshape(1, -1))
        if svm_prediction[0] ==  1:

            ## the svm predicted  that the knn model was right
            self.final_results_dict[self.input_person_iid] = self.knn_predictions_vector
            ## now add the person to the speed_dater_list
            knn_predictions_series = pd.Series(self.knn_predictions_vector, index=trait_list)
            self.additions_to_speed_daters_list.append(Person(knn_predictions_series, {self.input_person_iid: 1}, float(self.input_person_iid*-1)))
            print("svm agreed")
            self.count_results[0] += 1


            ## and we're done with this person!
        else:
            #print("svm did not agree")
            #self.svmDidNotAgreeWithKNN()
            self.count_results[1] += 1
