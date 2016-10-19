from solver import get_max_rating


class PlanData:
    # constants
    BIN_CAPACITY = 0
    AD_SPOT_GAP = 0
    BOUND_TREE = False
    ENABLE_GAP_CONSTRAINT = False

    # variables
    iter_count = 0
    bins = []
    margin = 0
    items = []
    max_rating = -1
    final_assignment = []
    iter_count = 0
    avl_cur = 0

    def get_availiable_currency(self):
        total_revenue = sum([item[1] for item in self.items])
        self.avl_cur = total_revenue * (1 - self.margin / 100.0)
        print total_revenue, self.avl_cur

    def get_max_ratings(self):
        get_max_rating(self.bins[:], self.items[:], self.avl_cur, self)
        print "total nodes visited are ", self.iter_count

    def __init__(self):
        # ad allowed in each time band
        self.BIN_CAPACITY = 180
        self.AD_SPOT_GAP = 30

        # rate, rating
        self.bins = [(5000, 0), (8000, 0.03), (13632, 0.09), (14000, 0.09), (20000, 0.16), (21000, 0.17)]
        self.bins = [list(bin) for bin in self.bins]

        # add duration to bins
        self.bins = [[self.BIN_CAPACITY] + bin for bin in self.bins]

        # duration, revenue
        self.items = [
            (15, 40269),
            (55, 123470),
            (60, 115419),
            (30, 61400),
            (30, 33450)
        ]

        self.items = [list(item) for item in self.items]

        # percentage
        self.margin = 10

        self.get_availiable_currency()

        # make bin cost per second
        for idx, bin in enumerate(self.bins):
            self.bins[idx][1] /= 10
