import decisionTree as dt
from decisionTree import DNASequence
from random import randint

def bootstrap_set(training):
    sample = []
    for i in range(0, len(training)):
        sample.append(training[randint(0, len(training) - 1)])
    return sample

def construct_ensemble(sampling_number, training):
    ensemble = []
    for i in range(0, sampling_number):
        ensemble.append(dt.construct_tree(bootstrap_set(training)))
    return ensemble

def classify_instance(ensemble, example):
    trueVotes = 0
    for model in ensemble:
        if dt.classify_sequence(model, example.sequence):
            trueVotes += 1
    return trueVotes > len(ensemble) / 2

def run_accuracy_test(ensemble, validation):
    num_correct = 0
    for example in validation:
        if classify_instance(ensemble, example) == example.promoter:
            num_correct += 1.0
    return num_correct / float(len(validation))

if __name__ == "__main__":
    training = dt.get_sequences_from_file("training.txt")
    validation = dt.get_sequences_from_file("validation.txt")
    ensemble = construct_ensemble(100, training)
    print run_accuracy_test(ensemble, validation)
