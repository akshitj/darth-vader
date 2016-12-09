import numpy as np
from scipy.optimize import linprog
import sys
from pulp import *

max_rating = -1
final_assignment = []
iter_count = 0


def alter_cost_ratings(items, bins, plan_data):
    """

    :param items:
    :param bins:
    :param plan_data (globals.PlanData):
    :return:
    """
    weights = [item[0] for item in items]

    min_weight = min(weights) - plan_data.AD_SPOT_GAP
    max_weight = max(weights) - plan_data.AD_SPOT_GAP

    # decrease cost per second by this factor
    gamma_cps = 1 / (1 + float(plan_data.AD_SPOT_GAP) / min_weight)

    # decrease rating per second by this factor
    gamma_rps = 1 / (1 + float(plan_data.AD_SPOT_GAP) / max_weight)

    for idx, bin in enumerate(bins):
        # decrease rating for the accomodated fillers
        bins[idx][2] *= gamma_rps
        # decrease cost for the accomodated fillers
        bins[idx][1] *= gamma_cps


def add_dummy_fillers(items, bins, plan_data):
    """

    :param items:
    :param bins:
    :param plan_data: globals.PlanData
    :return:
    """

    # add filler to each ad
    for idx, item in enumerate(items):
        # add filler to duration
        items[idx][0] += plan_data.AD_SPOT_GAP

    for idx, bin in enumerate(bins):
        # increase capacity by filler amount
        bins[idx][0] += plan_data.AD_SPOT_GAP


def integer_soln(items, bins, max_cost, plan_data):
    """

    :type plan_data: globals.PlanData
    """
    M = len(bins)
    N = len(items)
    if N == 0:
        return 0

    alter_cost_ratings(items, bins, plan_data)

    capacity = [bin[0] for bin in bins]
    rate = [bin[1] for bin in bins]
    ratings = [bin[2] for bin in bins]
    weights = [item[0] for item in items]

    timeband_model = LpProblem("Ratings Maximization Problem", LpMaximize)
    lp_vars = []
    for item in range(N):
        sub_list = []
        for bin in range(M):
            entry = str(item) + "->" + str(bin)
            sub_list += [entry]
        lp_vars.append(sub_list)

    lp_vars = np.array(lp_vars)
    x = pulp.LpVariable.dicts('assign', lp_vars.flatten(), lowBound=0, upBound=1, cat=LpInteger)

    # optimization condition
    timeband_model += sum([sum([x[lp_vars[i, j]] * ratings[j] * weights[i] for i in range(N)]) for j in range(M)])

    for i in range(N):
        timeband_model += sum([x[lp_vars[i, j]] for j in range(M)]) == 1, \
                          "Assign %s item to only one timeband" % str(i)

    for j in range(M):
        timeband_model += sum([x[lp_vars[i, j]] * weights[i] for i in range(N)]) <= capacity[j], \
                          "Do not overfill %s timeband" % str(j)

    timeband_model += sum(
        [sum([x[lp_vars[i, j]] * rate[j] * weights[i] for i in range(N)]) for j in range(M)]) <= max_cost, \
                      "assigning cost should not exceed"

    # The problem data is written to an .lp file
    timeband_model.writeLP("TimeBandModel.lp")

    timeband_model.solve()

    # The status of the solution is printed to the screen
    print "Status:", LpStatus[timeband_model.status]

    for v in timeband_model.variables():
        # print v.name, '=  ', v.varValue
        if v.varValue > 0:
            print v.name

    assignment = [-1] * N
    for lp_var in lp_vars.flatten():
        if x[lp_var].value() > 0:
            loc = np.where(lp_vars == lp_var)
            assignment[loc[0][0]] = loc[1][0]
    print "maximum objective attained is:", value(timeband_model.objective)
    plan_data.final_assignment = assignment
    plan_data.max_rating = value(timeband_model.objective)


# @profile
def relaxed_soln(items, bins, max_cost, plan_data):
    M = len(bins)
    N = len(items)
    if N == 0:
        return 0

    alter_cost_ratings(items, bins, plan_data)

    capacity = [bin[0] for bin in bins]
    rate = [bin[1] for bin in bins]
    ratings = [bin[2] for bin in bins]
    weights = [item[0] for item in items]

    b_eq = [sum(weights)]
    A_eq = np.zeros((1, M))
    A_eq[0, :] = 1

    b_ub = capacity + [max_cost]
    A_ub = np.zeros((M + 1, M))

    # bin capacities
    for i in range(0, M):
        A_ub[i, i] = 1

    # cost constraint
    A_ub[-1, :] = rate[:]

    opt_coeff = [-1 * rating for rating in ratings]

    res = linprog(opt_coeff, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq)
    if not res.success:
        return -1

    if np.any(res.x < 0):
        print "alert!!!"
        sys.exit()

    return -1 * res.fun

    """
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
            # print "unsuccessful with items: ", items, ", bins: ", bins, ", avl_cost: ", max_cost, " res: ", res
            # return negative rating for not possible
            return -1
        # print "maximum ratings achieved ", res.fun, "  with assignment \n", np.reshape(res.x, (N, M))
        print "iterations: ", res.nit
        return -1 * res.fun

    """
    # demand meet


# this will give at least how much cost is required to get least ratings
def get_lower_bound(items, bins):
    if len(items) == 0:
        # no cost is required for no items
        return 0

    # todo: change logic to knapsack for better lower bound
    # start filling lowest cost bin
    bins_idx = len(bins) - 1
    total_spot_len = sum(item[0] for item in items)
    min_cost = 0
    while total_spot_len > 0 and bins_idx >= 0:
        deduction = min(total_spot_len, bins[bins_idx][0])
        total_spot_len -= deduction
        min_cost += deduction * bins[bins_idx][1]
        bins_idx -= 1
    if total_spot_len > 0:
        # not enough bins return some high no.
        return 100000000
    return min_cost


# @profile
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

        cur_cost += bin[1] * (cur_item[0] - plan_data.AD_SPOT_GAP)
        if max_cost <= cur_cost:
            continue

        bins[idx][0] -= cur_item[0]
        assignment[cur_item_idx] = idx
        cur_val += bin[2] * (cur_item[0] - plan_data.AD_SPOT_GAP)

        if plan_data.BOUND_TREE:
            upper_bound = relaxed_soln(items[cur_item_idx + 1:], bins[:], max_cost - cur_cost, plan_data)
            cost_lower_bound = get_lower_bound(items[cur_item_idx + 1:], bins[:])
        else:
            # some large value
            upper_bound = 1000
            cost_lower_bound = 0

        if upper_bound >= 0:
            # feasible soln found
            upper_bound += cur_val
            if cur_cost + cost_lower_bound <= max_cost and upper_bound >= plan_data.max_rating:
                # print "tentative hike of rating to: ", upper_bound
                branch_and_bound(items, cur_item_idx + 1, bins, cur_val, assignment, cur_cost, max_cost, plan_data)

        cur_val -= bin[2] * (cur_item[0] - plan_data.AD_SPOT_GAP)
        assignment[cur_item_idx] = -1
        bins[idx][0] += cur_item[0]
        cur_cost -= bin[1] * (cur_item[0] - plan_data.AD_SPOT_GAP)


def get_item_key(item):
    # duration
    return item[0]


def get_bin_key(bin):
    # rating
    return bin[2]


def get_item_idx(item):
    return item[2]

# @profile
def get_max_rating(bins, items, max_val, plan_data):
    """

    :param bins:
    :param items:
    :param max_val:
    :param plan_data: globals.PlanData
    :return:
    """
    print "trying to maximise rating with margin: ", plan_data.margin, "%"

    # add original index
    items = [item + [idx] for idx, item in enumerate(items)]

    # reorder items according to duration
    items = sorted(items, key=get_item_key, reverse=True)
    print "sorted items are: ", items

    # sort bins by their rating
    bins = sorted(bins, key=get_bin_key, reverse=True)
    print "sorted bins are: ", bins

    add_dummy_fillers(items, bins, plan_data)

    print "after adding dummy fillers are: ", items, bins

    integer_soln(items, bins, max_val, plan_data)
    # sys.exit()

    # assignment = [-1] * len(items)
    # branch_and_bound(items, 0, bins, 0, assignment, 0, max_val, plan_data)
    print "max rating for non relaxed constraints is ", plan_data.max_rating, " with assignment ", \
        plan_data.final_assignment

    for idx, item in enumerate(items):
        items[idx][0] -= plan_data.AD_SPOT_GAP

    parsed_assignment = [
        [bins[bin_idx][2] * items[item_idx][0], bins[bin_idx][3], bins[bin_idx][1] * items[item_idx][0]]
        for item_idx, bin_idx in enumerate(plan_data.final_assignment)]

    items = [items[idx] + assignment for idx, assignment in enumerate(parsed_assignment)]
    items = sorted(items, key=get_item_idx)
    for item in items:
        del item[2]
    print "max rating for non relaxed constraints is ", plan_data.max_rating, " with assignment ", \
        items
    return items
