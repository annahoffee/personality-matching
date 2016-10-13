

import sys, os
import math
import numpy as np
import scipy
import pandas as pd
import sklearn
from sklearn.neural_network import MLPClassifier


class AdmirerSet(object):
    def __init__(self, speed_daters_list, interested_people):
        self.speed_daters_list = speed_daters_list
        self.interested_people = interested_people
