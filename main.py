'''
This file will be the entry point to build all your plots.

It should read data from 'data_organized' to do the plots.
You may still do some data organization such as joins, column filtering,
and other types of calculations. But, the focus should be on generating
glorious plots from data that is mostly preprocessed and organized already.
'''

import pandas as pd
from preprocess_data import pre_process_registration
from preprocess_data import pre_process_fuel_stations
from preprocess_data import pre_process_Electric_Vehicle_Population, pre_process_population
from helper import level_by_month, line_plotly, top_ten_plotly, level_by_month_plotly, growth_of_ev_plotly, geo_plotly, proportion_of_ev_plotly,vrt_by_countyfuelTypes_plotly
from helper import proportion_of_ev, growth_of_ev, vrt_by_countyfuelTypes, interactive, geo, top_ten, proportion_of_ev_plotly2, top_ten_plotly4, geo_plotly5, top_ten_plotly4



#from preprocess_data import pre_process_staes_provnces

def main():
    # pre_process_Electric_Vehicle_Population()
    # pre_process_registration()
    # pre_process_fuel_stations()
    # pre_process_population()
    # level_by_month()
    # proportion_of_ev()
    # growth_of_ev()
    # vrt_by_countyfuelTypes()
    interactive()
    # geo()
    # top_ten()
    line_plotly()
    top_ten_plotly()
    top_ten_plotly4()
    # top_ten_plotly2()
    # top_ten_plotly4()

    level_by_month_plotly()
    growth_of_ev_plotly()
    # geo_plotly2()
    geo_plotly5()
    geo_plotly()
    proportion_of_ev_plotly()
    proportion_of_ev_plotly2()
    vrt_by_countyfuelTypes_plotly()
    # population()
    # merge_population_and_registration()
    # pre_process_staes_provnces()
    

if __name__ == '__main__':
    main()
    