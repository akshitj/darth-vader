from parse_input import get_input
from parse_input import write_output
from globals import PlanData

# main function. first point of execution
if __name__ == "__main__":

    input_file_name = '/home/akshit/ad-planner/ad-planner-op.xls'

    # return
    plan_data = PlanData()
    get_input(input_file_name, plan_data)

    plan_data.get_max_ratings()

    write_output(input_file_name, "time-band.xls", plan_data)