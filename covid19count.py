#!/usr/bin/env python3

import regex as re
from datetime import datetime
from typing import List

import numpy as np
import click
import matplotlib.pyplot as plt
import xlrd
import requests
import urllib.request
from bs4 import BeautifulSoup


def load_data(regions: List[str]):
    url = "https://www.ecdc.europa.eu/en/publications-data/download-todays-data-geographic-distribution-covid-19-cases-worldwide"

    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    xls_link_box = soup.find("a", href=re.compile(r".+\.xls"))
    xls_url = xls_link_box["href"]

    urllib.request.urlretrieve(xls_url, "./covid_count.xls")
    wb_obj = xlrd.open_workbook("./covid_count.xls")
    xl_sheet = wb_obj.sheet_by_index(0)

    date = lambda x: datetime.fromordinal(
        datetime(1900, 1, 1).toordinal() + int(x.value) - 2
    )
    dates = list(map(date, xl_sheet.col(0)[1:]))
    countries = list(map(lambda x: x.value.lower(), xl_sheet.col(1)[1:]))
    counts = list(map(lambda x: x.value, xl_sheet.col(2)[1:]))

    data = {}
    for date, count, country in reversed(list(zip(dates, counts, countries))):
        if country not in data:
            data[country] = {"dates": [date], "counts": [count]}
        else:
            data[country]["dates"].append(date)
            data[country]["counts"].append(count)
    return data


@click.command()
@click.argument("regions", nargs=-1, required=True)
@click.option("--log", "-l", default=False)
@click.option("--fit", default=False, help="Fit an exponential function to the data")
def plot_data(regions: List[str], log: bool, fit: bool):
    if fit:
        raise NotImplementedError

    data = load_data(regions)
    f = plt.figure(figsize=(7, 4))
    ax = f.add_subplot(111)
    ax.yaxis.tick_right()
    ax.yaxis.set_label_position("right")
    for region in regions:
        plt.plot(data[region]["dates"], np.cumsum(data[region]["counts"]), linewidth=3)

    end_date = data[regions[0]]["dates"][-1].date()
    plt.legend(regions)
    plt.ylabel("Number of confirmed cases")
    if log:
        plt.yscale("log")
    plt.title("Confirmed cases per country as of " + str(end_date))
    plt.savefig("./plot.svg")
    plt.show()


if __name__ == "__main__":
    plot_data()
