"""
This module provides user matching functionality.
"""

__all__ = [
    'n_rand_matches', 'n_best_matches'
]

import random

import sqldb

from typing import List, Tuple


def n_rand_matches(cur, uid: int, n: int = 1) -> List[Tuple[int]]:
    """
    Fetches n other random users. The returned list may be smaller than 
    n (if not enough random matches exist to fill it).
    """
    
    query = '''SELECT userId FROM UsersInterestsJoin WHERE userId <> ?;'''

    others = sqldb.do_sql(cur, query, (uid,))

    if others is None:
        return []

    others = set(others)

    # using a set deduplicates the user list for us, but we have to convert 
    # back to a list to pass to random.sample without a deprecation warning
    return random.sample(list(others), min(n, len(others)))


def n_best_matches(cur, uid: int, user_interests: List[int], n: int = 1) -> List[Tuple[int, int]]:
    """
    Fetches the n other users who have the most matching interests from the 
    given list. The list is of the format [(user-id, matching_interests)*], 
    and may be smaller than n (if not enough matches exist to fill it).
    """
    user_matching_interests = {}

    interest_category = '''SELECT categoryId FROM Interests
    INNER JOIN InterestCategories ON Interests.categoryId = InterestCategories.id
    WHERE Interests.id LIKE ?;'''

    user_interest_categories = set()
    for interest in user_interests:
        category = sqldb.do_sql(cur, interest_category, (interest,))[0][0]
        if category not in user_interest_categories:
            user_interest_categories.add(category)

    matching_categories = '''SELECT userId FROM UsersInterestsJoin
    INNER JOIN Users ON UsersInterestsJoin.userId = Users.id
    INNER JOIN Interests ON UsersInterestsJoin.interestId = Interests.id
    INNER JOIN InterestCategories ON Interests.categoryId = InterestCategories.id
    WHERE userId <> ? AND categoryId LIKE ?;'''

    matching_interests = '''SELECT userId FROM UsersInterestsJoin
    INNER JOIN Users ON UsersInterestsJoin.userId = Users.id 
    INNER JOIN Interests ON UsersInterestsJoin.interestId = Interests.id
    INNER JOIN InterestCategories ON Interests.categoryId = InterestCategories.id
    WHERE userId <> ? AND interestId LIKE ?;'''

    matched_interest_score = 10
    matched_category_score = 1

    # search based on interest categories (to establish a baseline)
    for category in user_interest_categories:
        matching_users = sqldb.do_sql(cur, matching_categories, (uid, category))

        if matching_users is not None:
            matching_users = set(matching_users)

            for other in matching_users:
                other_id = other[0]

                old_score = user_matching_interests.get(other_id, 0)
                new_score = old_score + matched_category_score
                user_matching_interests[other_id] = new_score

    # search based on more granular interest
    for interest in user_interests:
        matching_users = sqldb.do_sql(cur, matching_interests, (uid, interest))

        if matching_users is not None:
            matching_users = set(matching_users)

            for other in matching_users:
                other_id = other[0]

                old_score = user_matching_interests.get(other_id, 0)
                new_score = old_score + matched_interest_score
                user_matching_interests[other_id] = new_score

    random_matches = n_rand_matches(cur, uid, n)

    score_key = lambda user: user_matching_interests[user]
    best_matches = sorted(user_matching_interests, key=score_key, reverse=True)[:n]

    matches = [(user, user_matching_interests[user]) for user in best_matches]

    # fill the remainder of the match list with random matches
    previously_matched = set(best_matches)
    while len(matches) < n and 0 < len(random_matches):
        random = random_matches.pop()[0]

        if random not in previously_matched:
            previously_matched.add(random)
            matches.append((random, 0))
            break

    return matches


if __name__ == '__main__':
    conn = sqldb.try_open_conn()
    cur = conn.cursor()

    select_interests = '''SELECT interestId FROM UsersInterestsJoin
    INNER JOIN Users ON UsersInterestsJoin.userId = Users.id
    INNER JOIN Interests ON UsersInterestsJoin.interestId = Interests.id
    WHERE userId LIKE ?;'''

    user = sqldb.do_sql(cur, 'SELECT id FROM Users;')[2]
    user_interests = sqldb.do_sql(cur, select_interests, (user[0],))

    print(f'Finding 1 random match for user {user}')
    print(n_rand_matches(cur, user[0], 1))

    print(f'Finding 10 random match for user {user}')
    print(n_rand_matches(cur, user[0], 10))

    print(f'Finding 3 best matches for user {user} with interests {user_interests}')
    print(n_best_matches(cur, user[0], [interest[0] for interest in user_interests], 3))

    print(f'Finding 10 best matches for user {user} with interests {user_interests}')
    print(n_best_matches(cur, user[0], [interest[0] for interest in user_interests], 10))

