import parse_input
from globals import PlanData
from globals import TimeBands
from globals import dayparts

# main function. first point of execution
if __name__ == "__main__":

    # input_file_name = '/home/akshit/ad-planner/ad-planner-op.xls'
    input_file_name = '/home/akshit/Downloads/ZT-2016-10-24-plan-1-intermediate-21-10-2016--14-7-48.xls'
    time_bands_file = 'time-bands.csv'

    # return
    plan_data = dict()
    day_parts = dayparts[:]

    tb = TimeBands()
    tb.load_from_file(time_bands_file)

    for day_part in day_parts:
        plan_data[day_part] = PlanData(daypart_name=day_part)
        parse_input.get_input(input_file_name, day_part, plan_data[day_part])
        plan_data[day_part].fill_bins(tb.time_bands_map[day_part])
        plan_data[day_part].get_max_ratings()
        print "-----------------------------------------------------------------------------------------------------"

    parse_input.write_output(input_file_name, "time-band.xls", plan_data)