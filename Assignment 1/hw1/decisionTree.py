"""
So What will happen is at each node we figure out which attribute is the best to split on (based on the formulas)
We then split on that attribute, send each data on its way (taking into account if there is no data, just assigning majority)
Before we split on the best attribute, we use a chi squared test to ensure that the split is significant (going for majoroity when no split is necessary)
There are 57 attributes each with 4 values, 'a', 'c', 'g', 't',
because all the attributes have the same valueset we don't need to worry about the gain criterion favoring attributes with lots of values
"""
from math import log

NUMBER_ATTRIBUTES = 57
CHI_SQUARED_CONFIDENCE_VALS = [6.63, 3.84, 0]
CHI_SQUARED_THRESHOLD = CHI_SQUARED_CONFIDENCE_VALS[0]

class AttributeTreeNode():
    def __init__(self, attribute_index):
        self.children = []
        self.attribute_index = attribute_index

class DecisionTreeLeaf():
    def __init__(self, promoter):
        self.promoter = promoter

class DNASequence():
    def __init__(self, sequence, promoter):
        self.sequence = sequence
        self.promoter = (promoter == '+')

def get_sequences_from_file(file_name):
    with open(file_name) as f:
        dna_sequences = map(lambda line: DNASequence(line.split(" ")[0], line.split(" ")[1]), f.read().splitlines())
        return dna_sequences

def is_homogenous(training):
    assert len(training) > 0, "THIS SHOULD NOT BE CALLED ON AN EMPTY TRAINING SET"
    promoter_value = training[0].promoter
    for example in training:
        if example.promoter != promoter_value:
            return False
    return True

def get_majority_class(training):
    num_promoters = 0
    for example in training:
        if example.promoter:
            num_promoters += 1
    return num_promoters > len(training) / 2

def chi_squared_test(training, attribute_idx):
    p = 0
    n = 0
    for example in training:
        if example.promoter:
            p += 1.0
        else:
            n += 1.0
    partions = partion_data(training, attribute_idx)
    sum = 0
    for partion in partions:
        expected_p = float(p * (float(len(partion)) / float(len(training))))
        expected_n = float(float(len(partion)) - expected_p)
        actual_p = 0
        actual_n = 0
        for example in partion:
            if example.promoter:
                actual_p += 1.0
            else:
                actual_n += 1.0

        if expected_p > 0 and expected_n > 0:
            sum += (pow(actual_p - expected_p, 2) / expected_p) + (pow(actual_n - expected_n, 2) / expected_n)
    return sum >= CHI_SQUARED_THRESHOLD

"""
partions the training array into 4 different arrays based on the value of the attribute at the index
"""
def partion_data(training, idx):
    aList = []
    cList = []
    gList = []
    tList = []
    for example in training:
        if example.sequence[idx] == 'a':
            aList.append(example)
        elif example.sequence[idx] == 'c':
            cList.append(example)
        elif example.sequence[idx] == 'g':
            gList.append(example)
        else:
            tList.append(example)
    return [aList, cList, gList, tList]

def training_I(training):
    p = 0
    n = 0
    for example in training:
        if example.promoter:
            p += 1
        else:
            n += 1
    return I(p, n)

def I(p, n):
    if p == 0 or n == 0:
        return 0
    p = float(p)
    n = float(n)
    return -(p/(p+n))*log(p/(p+n), 2) - (n/(p+n))*log(n/(p+n), 2)

def E(training, attribute_idx):
    p = 0
    n = 0
    for example in training:
        if example.promoter:
            p += 1.0
        else:
            n += 1.0
    sum = 0
    partions = partion_data(training, attribute_idx)
    for partion in partions:
        pi = 0
        ni = 0
        for example in partion:
            if example.promoter:
                pi += 1.0
            else:
                ni += 1.0
        sum += ((pi + ni)/(p + n)) * I(pi, ni)
    return sum

def gain(training, attribute_idx):
    return training_I(training) - E(training, attribute_idx)

def best_attribute_index(training):
    best_gain = 0
    best_attribute = 0
    for i in range(0, NUMBER_ATTRIBUTES):
        current_gain = gain(training, i)
        if current_gain > best_gain:
            best_gain = current_gain
            best_attribute = i
    return best_attribute
    #getting the best attribute via method in the original id3 paper

def construct_tree(training):
    if is_homogenous(training):
        return DecisionTreeLeaf(training[0].promoter)
    best_attribute_idx = best_attribute_index(training)
    if not chi_squared_test(training, best_attribute_idx):
        print "chi-squared failed"
        return DecisionTreeLeaf(get_majority_class(training))
    current_node = AttributeTreeNode(best_attribute_idx)
    partions = partion_data(training, best_attribute_idx)
    for partion in partions:
        if len(partion) == 0:
            current_node.children.append(DecisionTreeLeaf(get_majority_class(training)))
        else:
            current_node.children.append(construct_tree(partion))
    return current_node

def get_training_tree():
    training_sequences = get_sequences_from_file('training.txt')
    return construct_tree(training_sequences)

def classify_sequence(node, seq):
    if node.__class__ == DecisionTreeLeaf:
        return node.promoter
    character = seq[node.attribute_index]
    if character == 'a':
        return classify_sequence(node.children[0], seq)
    elif character == 'c':
        return classify_sequence(node.children[1], seq)
    elif character == 'g':
        return classify_sequence(node.children[2], seq)
    else:
        return classify_sequence(node.children[3], seq)

def run_accuracy_test(tree, validation):
    num_correct = 0
    for example in validation:
        if classify_sequence(tree, example.sequence) == example.promoter:
            num_correct += 1.0
    print num_correct / float(len(validation))

def depth(node):
    if node.__class__ == DecisionTreeLeaf:
        return 1
    return 1 + max(depth(node.children[0]), depth(node.children[1]), depth(node.children[2]), depth(node.children[3]))

if __name__ == "__main__":
    training_sequences = get_sequences_from_file('training.txt')
    validation_sequences = get_sequences_from_file('validation.txt')
    tree = construct_tree(training_sequences)
    print depth(tree)
    print "training accuracy"
    run_accuracy_test(tree, training_sequences)
    print "validation accuraccy"
    run_accuracy_test(tree, validation_sequences)
#STILL TODO, IMPLEMENT IN GRAPHLAB AS WELL
