from solver import get_max_rating
from solver import integer_soln
import parse_input
import sys

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
    daypart_name = "Untitled"

    def get_availiable_currency(self):
        total_revenue = sum([item[1] for item in self.items])
        self.avl_cur = total_revenue * (1 - self.margin / 100.0)
        print total_revenue, self.avl_cur

    def get_max_ratings(self):
        self.final_assignment = get_max_rating(self.bins[:], self.items[:], self.avl_cur, self)
        print "total nodes visited are ", self.iter_count

    def fill_items(self, spot_lengths, revenue):
        self.items = []
        for idx in range(len(revenue)):
            self.items += [[spot_lengths[idx], revenue[idx]]]
        self.get_availiable_currency()

    def set_margin(self, margin_percentage):
        self.margin = margin_percentage
        self.get_availiable_currency()

    def fill_bins(self, time_bands):
        self.bins = []
        self.bins = [[self.BIN_CAPACITY, bin[1]/10, bin[2], bin[0]] for bin in time_bands]
        print self.bins

    def __init__(self, daypart_name):
        self.daypart_name = daypart_name
        # ad allowed in each time band
        self.BIN_CAPACITY = 180

        if self.ENABLE_GAP_CONSTRAINT:
            self.AD_SPOT_GAP = 30
        else:
            self.AD_SPOT_GAP = 0

        self.margin = 10

        # rate, rating
        # self.bins = [(5000, 0, "9:00-9:30"), (8000, 0.03, "9:30-10:00"), (13632, 0.09, "10:00-10:30"),
        #              (14000, 0.09, "10:30-11:00"), (20000, 0.16, "11:00-11:30"), (21000, 0.17, "11:30-12:00")]
        # self.bins = [list(bin) for bin in self.bins]

        # add duration to bins
        # self.bins = [[self.BIN_CAPACITY] + bin for bin in self.bins]

        # duration, revenue
        # self.items = [
        #     (15, 40269),
        #     (55, 123470),
        #     (60, 115419),
        #     (30, 61400),
        #     (30, 33450)
        # ]

        # self.items = [list(item) for item in self.items]

        # percentage

        # self.get_availiable_currency()

        # make bin cost per second
        # for idx, bin in enumerate(self.bins):
        #     self.bins[idx][1] /= 10


class TimeBand:
    rating_per_second = 0
    cost_per_second = 0
    time_slot_l = 0
    time_slot_u = 30
    capacity = 0
    daypart = "Untitled"

dayparts = ["Morning", "Afternoon", "Evening", "Night"]


class TimeBands:
    time_bands_map = dict()

    def load_from_file(self, file_name):
        time_bands = parse_input.get_time_bands(file_name, dayparts)
        self.time_bands_map = time_bands

    def __init__(self):
        return
