"""
This module provides user matching functionality.
"""

__all__ = [
    'n_rand_matches', 'n_best_matches'
]

import random

import sqldb

from typing import List


def n_rand_matches(cur, uid: int, n: int = 1) -> List:
    """
    Fetches n other random users.
    """
    
    query = '''SELECT userId FROM UsersInterestsJoin
    INNER JOIN Users ON UsersInterestsJoin.userId = Users.id
    INNER JOIN Interests ON UsersInterestsJoin.interestId = Interests.id
    WHERE userId <> ?;'''

    others = sqldb.do_sql(cur, query, (uid,))

    return [tup[0] for tup in random.sample(others, n)]


def update_priority_queue(queue, new_user, new_score):
    new_tuple = (new_user, new_score)

    for i in range(len(queue)-1, -1, -1):
        # if an empty space is found, fill it
        if queue[i] is None:
            queue[i] = (new_user, new_score)
            break

        # if the space is not empty, and we have a higher value than the current
        # occupant, insert into this space and shuffle other entries down
        if new_score > queue[i][1]:
            prev = queue[i]
            queue[i] = new_tuple

            # shuffle down the remaining entries
            for j in range(i-1, -1, -1):
                # if there is still space, fill it
                if queue[j] is None:
                    queue[j] = prev
                    break

                # otherwise swap the values and continue shuffling
                if prev[1] > queue[j][1]:
                    prev, queue[j] = queue[j], prev

            break

    return queue


def n_best_matches(cur, uid: int, user_interests: List[int], n: int = 1) -> List:
    """
    Fetches the n other users who have the most matching interests from the 
    given list. The list is of the format [(user-id, matching_interests)*].
    """
    user_matching_interests = {}

    query = '''SELECT userId FROM UsersInterestsJoin
    INNER JOIN Users ON UsersInterestsJoin.userId = Users.id 
    INNER JOIN Interests ON UsersInterestsJoin.interestId = Interests.id
    WHERE userId <> ? AND interestId LIKE ?;'''


    # stores uid-score tuples (e.g. (uid('John Doe'), 42)) in worst-first order
    n_best = [None for i in range(n)]

    for interest in user_interests:
        matching_users = sqldb.do_sql(cur, query, (uid, interest))

        if matching_users is not None:
            for other in matching_users:
                other_id = other[0]

                new_other_score = user_matching_interests.get(other_id, 0) + 1
                user_matching_interests[other_id] = new_other_score

                n_best = update_priority_queue(n_best, other_id, new_other_score)

    return n_best


if __name__ == '__main__':
    queue = [('Foo', 1), ('Bar', 2), ('Baz', 3), None]
    print(f'Inserting (John Doe, 4) into {queue}')
    print(update_priority_queue(queue, 'John Doe', 4))

    queue = [('Foo', 10)]
    print(f'Inserting (John Doe, 1) into {queue}')
    print(update_priority_queue(queue, 'John Doe', 1))

    queue = [('Foo', 1)]
    print(f'Inserting (John Doe, 2) into {queue}')
    print(update_priority_queue(queue, 'John Doe', 2))

    queue = [('Foo', 1), ('Bar', 2)]
    print(f'Inserting (John Doe, 3) into {queue}')
    print(update_priority_queue(queue, 'John Doe', 3))

    conn = sqldb.try_open_conn()
    cur = conn.cursor()

    user = sqldb.do_sql(cur, 'SELECT id FROM Users;')[0]
    user_interests = sqldb.do_sql(cur, 'SELECT interestId FROM UsersInterestsJoin INNER JOIN Users ON UsersInterestsJoin.userId = Users.id INNER JOIN Interests ON UsersInterestsJoin.interestId = Interests.id WHERE userId LIKE ?;', (user[0],))

    print(f'Finding 1 random match for user {user}')
    print(n_rand_matches(cur, user[0], 1))

    print(f'Finding 3 best matches for user {user} with interests {user_interests}')
    print(n_best_matches(cur, user[0], [interest[0] for interest in user_interests], 3))

