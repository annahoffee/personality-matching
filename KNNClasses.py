

import sys, os
import math
import numpy as np
import scipy
import pandas as pd
import random
import sklearn



class FindMatchQualities(object):

    def __init__(self, nearest_neighbors_dict, speed_daters_list):
        self.nearest_neighbors_dict = nearest_neighbors_dict
        ## nearest_neighbors_dict := {iid: distance, ...}
        self.speed_daters_list = speed_daters_list
        self.for_counting_purposes = []



    def identifyInterestedPeople(self):

        self.interested_people = []

        ## create a list of the people who liked at least one person in the nearest_neighbors_dict
        nearest_neighbor_iids = self.nearest_neighbors_dict.keys()

        for speed_dater in self.speed_daters_list:
            iids = []
            decisions = []
            for key in speed_dater.partner_dict.keys():
                iids.append(key)
                decisions.append(speed_dater.partner_dict[key])

            ## multiply the  two arrays  so the people  that the dater didn't like will get  multiplied by 0, and the others by 1

            speed_dater_likes_iids = pd.Series(np.multiply(iids, decisions))
            ## remove the 0 elements
            speed_dater_likes_iids = speed_dater_likes_iids[speed_dater_likes_iids != 0 ] # list of iids of people that speed_dater likes
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
                #self.for_counting_purposes.append(speed_dater.iid)
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


    def identifyOutputQualities(self, trait_list):

        self.output_qualities = {q:0 for q in trait_list}
        categorical_variables = ["gender", 'black', 'white', 'latino', 'asian', 'native_american', 'other']
        for t in trait_list: # loop over all output traits
            samples = []
            for person in self.interested_people: # loop over all "likely" interested people
                samples.append([person.trait_vector[t], person.weight])

            if t in categorical_variables:
                self.output_qualities[t] = self.combineCategoricalVariable(samples)

            else:
                self.output_qualities[t] = self.combineNumericVariable(samples)
