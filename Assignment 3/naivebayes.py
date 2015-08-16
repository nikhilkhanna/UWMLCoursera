from sets import Set
from math import log

class EmailExample():
    def __init__(self, id, spam, wordmap):
        self.id = id
        self.spam = spam
        self.wordmap = wordmap

def get_emails_from_file(file_name):
    emails = []
    with open(file_name) as f:
        lines = f.read().splitlines()
        for line in lines:
            tokens = line.split(' ')
            id = tokens[0]
            spam = tokens[1] == 'spam'
            wordmap = {}
            for i in range(2, len(tokens) - 1, 2):
                wordmap[tokens[i]] = int(tokens[i + 1])
            emails.append(EmailExample(id, spam, wordmap))
    return emails

def get_vocab_set(training):
    vocab = Set([])
    for example in training:
        for word in example.wordmap.keys():
            vocab.add(word)
    return vocab

def get_spam_prior(training):
    number_spam = 0.0
    for email in training:
        if email.spam:
            number_spam += 1.0
    return number_spam / float(len(training))

def get_total_word_map_for_spam_value(training, spam):
    total_word_map = {}
    for example in training:
        if example.spam != spam:
            continue
        for word in example.wordmap:
            if word not in total_word_map:
                total_word_map[word] = 0
            total_word_map[word] += example.wordmap[word]
    return total_word_map

def get_total_word_count(word_map):
    count = 0
    for word in word_map:
        count += word_map[word]
    return count

def get_word_probablility_map(word_map, word_count, vocabulary):
    word_probability_map = {}
    for word in vocabulary:
        number_of_occurences = 0
        if word in word_map:
            number_of_occurences = word_map[word]
        word_probability_map[word] = float(number_of_occurences + 10) / float(word_count + 10 * len(vocabulary))
    return word_probability_map

def document_is_spam(example, spam_word_prob_map, ham_word_prob_map, spam_prior, ham_prior, vocabulary):
    spam_sum = log(spam_prior)
    for word in example.wordmap:
        if word in vocabulary:
            spam_sum += example.wordmap[word] * log(spam_word_prob_map[word])
    ham_sum = log(ham_prior)
    for word in example.wordmap:
        if word in vocabulary:
            ham_sum += example.wordmap[word] * log(ham_word_prob_map[word])
    return spam_sum > ham_sum

if __name__ == "__main__":
    training_emails = get_emails_from_file('train')
    validation_emails = get_emails_from_file('test')
    spam_prior = get_spam_prior(training_emails)
    ham_prior = 1 - spam_prior
    vocabulary = get_vocab_set(training_emails)
    spam_word_map = get_total_word_map_for_spam_value(training_emails, True)
    ham_word_map = get_total_word_map_for_spam_value(training_emails, False)
    spam_word_count = get_total_word_count(spam_word_map)
    ham_word_count = get_total_word_count(ham_word_map)
    spam_word_prob_map = get_word_probablility_map(spam_word_map, spam_word_count, vocabulary)
    ham_word_prob_map = get_word_probablility_map(ham_word_map, ham_word_count, vocabulary)
    number_correct = 0.0
    for example in validation_emails:
        if document_is_spam(example, spam_word_prob_map, ham_word_prob_map, spam_prior, ham_prior, vocabulary) == example.spam:
            number_correct += 1.0
    print number_correct/float(len(validation_emails))
