
max_rating = -1
iter_count = 0

def branch_and_bound(items, cur_item_idx, bins, cur_val, assignment, cur_cost, max_cost):
    if cur_item_idx >= len(items):
        global iter_count
        iter_count += 1
        # we have reached leaf
        global max_rating
        if cur_val > max_rating:
            max_rating = cur_val
            print "rating increased to ", cur_val, " with assignment ", assignment, " cost: ", cur_cost
        return

    cur_item = items[cur_item_idx]

    # try to fit item into every bin
    for idx, bin in enumerate(bins):
        # check space is remaining
        if bin[0] < cur_item[0]:
            continue

        bins[idx][0] -= cur_item[0]
        assignment[cur_item_idx] = idx
        cur_val += cur_item[0] * bin[2]
        cur_cost += bin[1] * cur_item[0]

        if cur_cost <= max_cost:
            branch_and_bound(items, cur_item_idx + 1, bins, cur_val, assignment, cur_cost, max_cost)

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


def get_max_rating(bins, items, max_val):
    # reorder items according to duration
    items = sorted(items, key=get_item_key, reverse=True)
    print "sorted items are: ", items

    # sort bins by their rating
    bins = sorted(bins, key=get_bin_key, reverse=True)
    print "sorted bins are: ", bins

    assignment = [-1] * len(items)
    branch_and_bound(items, 0, bins, 0, assignment, 0, max_val)

# main function. first point of execution
if __name__ == "__main__":

    # rate, rating
    bins = [(5000, 0), (8000, 0.03), (13632, 0.09), (14000, 0.09), (20000, 0.16), (21000, 0.17)]
    bins = [list(bin) for bin in bins]

    # ad allowed in each time band
    BIN_CAPACITY = 80

    # duration, revenue
    items = [
        (15, 40269),
        (55, 123470),
        (60, 115419),
        (30, 61400),
        (30, 33450)
    ]
    items = [list(item) for item in items]

    # percentage
    margin = 10

    total_revenue = sum([item[1] for item in items])
    avl_cur = total_revenue*(1 - margin/100.0)
    print total_revenue, avl_cur

    # add duration to bins
    bins = [ [BIN_CAPACITY] + bin for bin in bins]

    # make bin cost per second
    for idx, bin in enumerate(bins):
        bins[idx][1] /= 10

    print "bins are: ", bins

    no_bins = len(bins)
    no_items = len(items)

    get_max_rating(bins, items, avl_cur)

    print "total leaf paths visited are ", iter_count