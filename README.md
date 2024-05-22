# BIG DATA PROJECT

![Logo Project.](dashboard/assets/logo.png)

Repository of PYBD (Python for Big Data), an EPITA course.

## Table of Contents

- [Installation](#installation)
- [Methodology](#methodology)
- [Dashboard](#dashboard)

## Installation

Clone the project repository, then follow the instructions below:

```sh
# Go to the project root
cd bigdata

# [All in One]
# Directly Download, Extract and Run docker images
make all

# === OR === #
# Make a directory with the path: docker/data/
mkdir docker/data

# Put the boursorama data inside "docker/data/"
unzip boursorama.zip docker/data/

# Launch our app and write the data inside SQL database
make
```

/!\ 

EPITA's computers using podman, some docker functionnalities may crash during the first start. It usually happen after the docker images and boursorama.tar download (when the analyzer's job begins ~10min after the ```make all``` command). If so, just ```Ctrl-C``` and run the ```make``` command again.

The analyzer should take ~45min to process the data on school computers.

/!\

## Methodology

### Data Reading


Firstly, regarding file reading, we opted to process the data in descending order based on the date. Indeed, some companies have changed their names multiple times since their creation while retaining the same symbol. Therefore, we always keep the latest recorded name as the company's name. Since data reading is a tedious and time-consuming task, we decided to parallelize functions to the maximum extent possible to facilitate insertions into the tables.

### Data Handling


Many modifications had to be made to the raw data for their insertion into the database, such as :

- The suffixes like `'(s)'` and `'(c)'` have been removed from the stock values to simplify adding them to the database, which imposes restrictions on column types. Now, values must be expressed in numeric form rather than as strings.

- To avoid exceeding the limit of numeric types, we capped values that exceed the maximum limit at the maximum threshold.

- We were instructed not to delete existing tables or data, but only to add to them. That's why we decided to add the `std` and `mean` columns to the `daystocks` table, which will make it easier for us to visualize the data on the dashboard later. Additionally, with the provided data, some companies are not listed in the default financial markets provided in the `markets` table. Since the IDs of the financial markets initially present start from index 1, we decided to associate the `market` for the unlisted companies with default index 0.

- To reduce the size of the data, we have decided to remove identical values from a horizontal segment, except for the first and last occurrence, in order to maintain an identical graph while having less data. This allowed us to reduce the number of rows in the stocks table from 367 million to 90 million.
## Dashboard

![Dashboard Presentation GIF](dashboard/assets/dashboard.gif)

Above, a GIF of our project dashboard.

### Features

This dashboard includes numerous features:

- A progress bar representing the status of the analyzer part, which fill all the SQL tables.
- The selection of one or more actions (up to 6 maximum) can be displayed simultaneously on the dashboard.

-  The graphical representation of stock data can be linear, area and candle sticks.
- The representation of volumes associated with stocks can be displayed only when a single stock is selected.
- Buttons below the graph allow switching to logarithmic scale or displaying Bollinger Bands.
- A filter by market and eligibility (Boursorma/PEAPME)
- The summary of the latest day recorded (the highest value, the lowest value, the opening value, the closing value, and the volume of shares traded) that can follow the user when the page is scrolled.

- A table representing the historical values of a stock by day.
- A pie chart representing the value of user investments. When companies are selected, allow the user to choose the number of shares held. The total investment value is divided graphically based on the number and value of each share.
