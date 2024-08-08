import polars as pl
from mywcscraper import get_toilet_info

# Get info for all pages in MYWC
toilet_info = get_toilet_info()

# Turn it into a dataframe; export as CSV
df = pl.DataFrame(toilet_info)
df.write_csv("toilet_data.csv")