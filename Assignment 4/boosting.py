import decisionTree as dt
from decisionTree import DNASequence
from random import random
from bisect import bisect
from math import log

NUMBER_OF_ROUNDS = 75

"""
Takes a training set and an array of the weight of each example and generates a weighted set
"""
def weighted_bootstrap_set(training, weights):
    sample = []
    cum_weights = []
    total = 0.0
    for w in weights:
        total += w
        cum_weights.append(total)
    for i in range(0, len(training)):
        selectedIndex = bisect(cum_weights, total * random())
        sample.append(training[selectedIndex])
    return sample

def construct_boosted_tree(training):
    weights = map(lambda x: 1.0 / len(training), training)
    decisionTrees = []
    for roundIdx in range(0, NUMBER_OF_ROUNDS):
        weights_sum = sum(weights)
        weights = map(lambda weight: weight / weights_sum, weights)
        tree = dt.construct_tree(weighted_bootstrap_set(training, weights))
        error = 0.0
        for i in range(0, len(training)):
            example = training[i]
            if example.promoter != dt.classify_sequence(tree, example.sequence):
                error += weights[i]
        if error > .5:
            return decisionTrees
        beta = error / (1 - error)
        for i in range(0, len(training)):
            example = training[i]
            if example.promoter == dt.classify_sequence(tree, example.sequence):
                weights[i] = weights[i] * beta
        decisionTrees.append((tree, beta))
    return decisionTrees

def classify_instance(boosted_tree, example):
    trueVotes = 0.0
    falseVotes = 0.0
    for model in boosted_tree:
        if dt.classify_sequence(model[0], example.sequence):
            trueVotes += 1.0 * log(1 / model[1])
        else:
            falseVotes += 1.0 * log(1/ model[1])
    return trueVotes >= falseVotes

def run_accuracy_test(boosted_tree, validation):
    num_correct = 0
    for example in validation:
        if classify_instance(boosted_tree, example) == example.promoter:
            num_correct += 1.0
    return num_correct / float(len(validation))

if __name__ == "__main__":
    training = dt.get_sequences_from_file("training.txt")
    validation = dt.get_sequences_from_file("validation.txt")
    boosted_tree = construct_boosted_tree(training)
    print run_accuracy_test(boosted_tree, validation)
