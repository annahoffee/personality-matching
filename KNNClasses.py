

import sys, os
import math
import numpy as np
import scipy
import pandas as pd
import random
import sklearn
from neuralNetClasses import RunNeuralNet




class FindMatchQualities(object):

    def __init__(self, nearest_neighbors_dict, speed_daters_list, input_person_fans, testing):
        self.nearest_neighbors_dict = nearest_neighbors_dict
        ## nearest_neighbors_dict := {iid: distance, ...}
        self.speed_daters_list = speed_daters_list
        self.for_counting_purposes = []
        self.input_person_fans = input_person_fans
        self.testing = testing



    def identifyInterestedPeople(self):

        self.interested_people = []

        ## create a list of the people who liked at least one person in the nearest_neighbors_dict
        nearest_neighbor_iids = set(self.nearest_neighbors_dict.keys())
        for speed_dater in self.speed_daters_list:
            #iids = []
            #decisions = []
            thing=False
            speed_dater_likes_iids = []

            for key, value in speed_dater.partner_dict.items():

                if value == 0 and key in nearest_neighbor_iids:
                    thing=True
                    break
                elif value == 1:
                    speed_dater_likes_iids.append(key)
            if thing:
                continue


            distances = []
            for iid in speed_dater_likes_iids:
                try:
                    distances.append(self.nearest_neighbors_dict[iid])
                    ## a KeyError will be thrown if the  person the speed_dater likes is not the the nearest_neighbors list
                except KeyError:
                    pass


            if(len(distances) > 0): ## if the speed_dater did like at least of the  nearest_neighbors
                speed_dater.calculateWeight(distances)
                ## add the speed_dater to the list of interested people

                self.interested_people.append(speed_dater)

    def combineNumericVariable(self, samples):
        ## use a simple weighted sum of the variable
        output = 0
        ## first create the weights (currently just thier distances )
        distance_sum = 0
        for sample in samples:
            distance_sum += sample[1]

        for sample in samples:
            if math.isnan(sample[0]) or math.isnan(sample[1]):
                continue
            weight = 1 - (sample[1]/distance_sum)
            ## add up a weighted  sum of the variales
            output = output + sample[0]*weight
        ## divide  the sum by the number  of samples
        output = round(float(output/len(samples)), 2)

        return(output)

    def combineCategoricalVariable(self, samples):

        labels = {}
        for sample in samples:
            if sample[0] in labels.keys():
                labels[sample[0]] += sample[1]
            else:
                labels[sample[0]] = sample[1]

        max_label = None
        max_weight = 0
        for key in labels.keys():
            if(labels[key] >= max_weight):
                max_label = key
                max_weight = labels[key]
        return(max_label)

    def usePickledNN(self):
        difference_tracker = 10000
        id_of_nn = 0
        for key in nn_dictionary:
            length = len(self.interested_iids.symmetric_difference(nn_dictionary[key]))
            if length < difference_tracker:
                id_of_nn = key
        print("made it here")




    def identifyOutputQualities(self, trait_list, neural_net, nn_counter):
        self.interested_iids = set()
        
        self.nn_counter = nn_counter
        for person in self.interested_people:
            self.interested_iids.add(person.iid)


        categorical_variables = ["gender", 'black', 'white', 'latino', 'asian', 'native_american', 'other']

        if neural_net == 1:
            trait_list = ["gender", 'black', 'white', 'latino', 'asian', 'native_american', 'other', "age",  "field_cd", "career_c", "go_out", "sports", "tvsports", "exercise", "dining", "art", "hiking", "gaming", "clubbing", "reading", "movies", "concerts", "music", "yoga"]
            self.output_qualities = {q:0 for q in trait_list}
            nn_input = np.empty([ len(trait_list), len(self.interested_people)])
            for x, trait in enumerate(trait_list):
                for y, person in enumerate(self.interested_people):
                    nn_input[x, y] = self.interested_people[y].trait_vector[trait]

            if self.testing:
                usePickledNN()
                return
            nn = RunNeuralNet(nn_input, self.input_person_fans, self.nn_counter)
            ########### if the neural net failed #################
            if nn.test == 0:
                self.output_qualities = {q:0 for q in trait_list}
                for t in trait_list: # loop over all output traits
                    samples = []
                    for person in self.interested_people: # loop over all "likely" interested people
                        samples.append([person.trait_vector[t], person.weight])
                        if t in categorical_variables:
                            self.output_qualities[t] = self.combineCategoricalVariable(samples)

                        else:
                            self.output_qualities[t] = self.combineNumericVariable(samples)
            #########################################################################
            else:
                for x, trait in enumerate(trait_list):
                    self.output_qualities[trait] = nn.output_traits[x]


        else:

            self.output_qualities = {q:0 for q in trait_list}
            for t in trait_list: # loop over all output traits
                samples = []
                for person in self.interested_people: # loop over all "likely" interested people
                    samples.append([person.trait_vector[t], person.weight])

                    if t in categorical_variables:
                        self.output_qualities[t] = self.combineCategoricalVariable(samples)

                    else:
                        self.output_qualities[t] = self.combineNumericVariable(samples)
