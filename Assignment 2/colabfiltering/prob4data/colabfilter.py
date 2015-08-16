from sets import Set
from math import sqrt
import time

user_to_movie_set_map = None
user_map_to_movie_map_to_rating = None
user_dict = None
movie_dict = None
user_map_to_average = None

class RatingExample:
    def __init__(self, movie, user, rating=None):
        self.movie = movie
        self.user = user
        self.rating = float(rating)

def rating_examples_from_file(file_name):
    with open(file_name) as f:
        ratings = map(lambda line: RatingExample(line.split(",")[0], line.split(",")[1], line.split(",")[2]), f.read().splitlines())
        return ratings

"""
Returns a map from each movie id to any training example containing that movie
"""
def movie_map(training):
    dict = {}
    for example in training:
        if example.movie not in dict:
            dict[example.movie] = [example]
        else:
            dict[example.movie].append(example)
    return dict

"""
Returns a map from each user id to any training example containing that user
"""
def user_map(training):
    dict = {}
    for example in training:
        if example.user not in dict:
            dict[example.user] = [example]
        else:
            dict[example.user].append(example)
    return dict

def estimate_rating(example):
    average_active_rating = user_map_to_average[example.user]
    reviews_of_movie = movie_dict[example.movie]
    print example.movie
    print len(reviews_of_movie)
    #reviews of movie now contains every single movie review (aka all users we're interested in)
    current_sum = 0.0
    current_abs_weight_sum = 0.0
    for i in range(0, min(50, len(reviews_of_movie))):
        review = reviews_of_movie[i]
        weight = similarity_weight(example.user, review.user)
        current_abs_weight_sum += abs(weight)
        current_sum += weight * (review.rating - user_map_to_average[review.user])
    if current_abs_weight_sum == 0:
        return average_active_rating
    return average_active_rating + (1 / current_abs_weight_sum) * current_sum

def similarity_weight(active_user, other_user):
    average_active_rating = user_map_to_average[active_user]
    average_other_rating = user_map_to_average[other_user]
    start = time.time()
    common_movies = user_to_movie_set_map[active_user]&user_to_movie_set_map[other_user]
    end = time.time()
    numerator = 0.0
    denominator1 = 0.0
    denominator2 = 0.0
    for movie in common_movies:
        numerator += ((user_map_to_movie_map_to_rating[active_user][movie].rating - average_active_rating) *
                      (user_map_to_movie_map_to_rating[other_user][movie].rating - average_other_rating))
        denominator1 += pow(user_map_to_movie_map_to_rating[active_user][movie].rating - average_active_rating, 2)
        denominator2 += pow(user_map_to_movie_map_to_rating[other_user][movie].rating - average_other_rating, 2)
    denominator = sqrt(denominator1 * denominator2)
    if denominator == 0:
        return 0
    return numerator / denominator

def average_user_rating(user):
    return reduce(lambda current, review: current + review.rating, user_dict[user], 0) / len(user_dict[user])

def predict_ratings(testing):
    predictions = []
    for i in range(0, len(testing)):
        print i
        start = time.time()
        predictions.append(estimate_rating(testing[i]))
        end = time.time()
        print end - start
    absolute_error = 0
    rms_error = 0
    for i in range(0, len(predictions)):
        absolute_error += abs(testing[i].rating - predictions[i])
        rms_error += pow((testing[i].rating - predictions[i]), 2)
    mean_absolute_error = absolute_error / len(predictions)
    rms_error = sqrt(rms_error / len(predictions))
    print "mean absolute error"
    print mean_absolute_error
    print "rms error"
    print rms_error

if __name__ == '__main__':
    training = rating_examples_from_file("TrainingRatings.txt")
    testing = rating_examples_from_file("TestingRatings.txt")
    start = time.time()
    movie_dict = movie_map(training)
    user_dict = user_map(training)
    user_to_movie_set_map = {}
    for user in user_dict:
        user_to_movie_set_map[user] = Set()
        for rating in user_dict[user]:
            user_to_movie_set_map[user].add(rating.movie)

    user_map_to_movie_map_to_rating = {}
    for user in user_dict:
        user_map_to_movie_map_to_rating[user] = {}
        for rating in user_dict[user]:
            user_map_to_movie_map_to_rating[user][rating.movie] = rating

    user_map_to_average = {}
    for user in user_dict:
        user_map_to_average[user] = average_user_rating(user)

    predictions = predict_ratings(testing)
    end = time.time()
    print end - start
