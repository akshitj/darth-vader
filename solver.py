import numpy as np
from scipy.optimize import linprog

max_rating = -1
final_assignment = []
iter_count = 0


def alter_bins_items_for_gap(items, bins, AD_SPOT_GAP):
    weights = [item[0] for item in items]

    min_weight = min(weights)
    max_weight = max(weights)

    # decrease cost per second by this factor
    gamma_cps = 1 / (1 + float(AD_SPOT_GAP) / min_weight)

    # decrease rating per second by this factor
    gamma_rps = 1 / (1 + float(AD_SPOT_GAP) / max_weight)

    for idx, bin in enumerate(bins):
        # increase capacity by filler amount
        bins[idx][0] += AD_SPOT_GAP
        # decrease rating for the accomodated fillers
        bins[idx][2] *= gamma_rps
        # decrease cost for the accomodated fillers
        bins[idx][1] *= gamma_cps

    # add filler to each ad
    for idx, item in enumerate(items):
        # add filler to duration
        items[idx][0] += AD_SPOT_GAP


def relaxed_soln(items, bins, max_cost):
    M = len(bins)
    N = len(items)
    if N == 0:
        return 0

    # alter_bins_items_for_gap(items, bins)

    capacity = [bin[0] for bin in bins]
    rate = [bin[1] for bin in bins]
    ratings = [bin[2] for bin in bins]
    weights = [item[0] for item in items]

    # demand meet
    b_eq = weights[:]
    A_eq = np.zeros((N, N * M))
    for i in range(0, N):
        mat = np.zeros((N, M))
        mat[i, :] = 1
        mat = mat.flatten()
        A_eq[i, :] = mat[:]

    # supply upper bound and cost upper bound
    b_ub = np.array(capacity[:] + [max_cost])
    A_ub = np.zeros((M + 1, N * M))
    # print A_ub.shape, b_ub.shape
    for i in range(0, M):
        mat = np.zeros((N, M))
        mat[:, i] = 1
        mat = mat.flatten()
        A_ub[i, :] = mat[:]

    # cost should not exceed
    mat = np.zeros((N, M))
    for i in range(0, M):
        mat[:, i] = rate[i]
    A_ub[M, :] = mat.flatten()

    # optimization coefficients
    opt_coeff = np.zeros((N, M))
    for i in range(0, M):
        opt_coeff[:, i] = -1 * ratings[i]
    c = opt_coeff.flatten()

    res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq)
    if not res.success:
        print "unsuccessful with items: ", items, ", bins: ", bins, ", avl_cost: ", max_cost, " res: ", res
        # return negative rating for not possible
        return -1
    print "maximum ratings achieved ", res.fun, "  with assignment \n", np.reshape(res.x, (N, M))
    return -1 * res.fun


def branch_and_bound(items, cur_item_idx, bins, cur_val, assignment, cur_cost, max_cost, plan_data):
    """

    :param items:
    :param cur_item_idx: int
    :param bins:
    :param cur_val: int
    :param assignment: []int
    :param cur_cost: int
    :param max_cost: int
    :param plan_data: globals.PlanData
    :return:
    """
    # global iter_count
    plan_data.iter_count += 1

    if cur_item_idx >= len(items):
        # we have reached leaf
        if cur_val > plan_data.max_rating:
            plan_data.max_rating = cur_val
            plan_data.final_assignment = assignment[:]
            print "rating increased to ", cur_val, " with assignment ", assignment, " cost: ", cur_cost
        return

    cur_item = items[cur_item_idx]

    # try to fit item into every bin
    for idx, bin in enumerate(bins):
        # check space is remaining
        if bin[0] < cur_item[0]:
            continue

        cur_cost += bin[1] * cur_item[0]
        if max_cost <= cur_cost:
            return

        bins[idx][0] -= cur_item[0]
        assignment[cur_item_idx] = idx
        cur_val += cur_item[0] * bin[2]

        if plan_data.BOUND_TREE:
            upper_bound = relaxed_soln(items[cur_item_idx + 1:], bins[:], max_cost - cur_cost)
        else:
            # some large value
            upper_bound = 1000

        if upper_bound < 0:
            # no feasible soln found
            return
        upper_bound += cur_val

        if cur_cost <= max_cost and upper_bound >= max_rating:
            print "tentative hike of rating to: ", upper_bound
            branch_and_bound(items, cur_item_idx + 1, bins, cur_val, assignment, cur_cost, max_cost, plan_data)

        bins[idx][0] += cur_item[0]
        assignment[cur_item_idx] = -1
        cur_val -= cur_item[0] * bin[2]
        cur_cost -= bin[1] * cur_item[0]

    return


def get_item_key(item):
    # duration
    return item[0]


def get_bin_key(bin):
    # rating
    return bin[2]


def get_max_rating(bins, items, max_val, plan_data):
    """

    :param bins:
    :param items:
    :param max_val:
    :param plan_data: globals.PlanData
    :return:
    """
    # reorder items according to duration
    items = sorted(items, key=get_item_key, reverse=True)
    print "sorted items are: ", items

    # sort bins by their rating
    bins = sorted(bins, key=get_bin_key, reverse=True)
    print "sorted bins are: ", bins

    # relaxed_soln(items, bins, max_val)

    # return
    assignment = [-1] * len(items)
    branch_and_bound(items, 0, bins, 0, assignment, 0, max_val, plan_data)
    print "max rating for non relaxed constraints is ", plan_data.max_rating, " with assignment ", \
        plan_data.final_assignment
