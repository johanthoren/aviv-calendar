# aviv-calendar
## Goal: 
Tries to find out what day it is according to biblical time keeping.
## Installation:
The software is now available as a pip package. Install with: `pip install aviv`. This will install all dependencies needed.
## Direct Usage:
`python main.py --location <city> [--country <country>] [--geocoder <google|astral>] [--year <YYYY> --month <MM> --day <DD> --hour <HH>]`
### Comments on direct usage:
When using year, month, day or hour unused options will default to 2018, 1, 1 and 12 respectively. If you want to know the CURRENT data, don't specify any of these. main.py defaults to showing the CURRENT data for JERUSALEM, ISRAEL.
## Example:
```
python main.py --location Skepplanda --geocoder google
Location ...............................
City:                         Skepplanda
Country:                          Sweden

Biblical ...............................
Short (ISO) Date:             6017-11-20

Year:                               6017
Month:                              11th
Month (traditional name):          Shvat
Day of month:                       20th

Weekday:                             4th

Weekly Sabbath:                       No
Feast Day:                            No
Holy Day of rest:                     No

Gregorian ..............................
Short (ISO) Date:             2018-02-06

Year:                               2018
Month:                          February
Day of month:                         06

Weekday:                         Tuesday

Time:                           18:59:01

Solar info .............................
Daylight:                             No
Sun has set:                         Yes
Time of sunset:                 16:47:31
```
<!-- ### Screenshot: -->
<!-- ![aviv-calendar screenshot](https://www.avivcalendar.com/img/screenshot_2.png) -->
## Definitions:
The aviv-calendar project is based on the following ideas:
* The day starts at sundown.
* The month starts when the first sliver of the new moon is sighted in the land of Israel.
* The year starts on the first new moon AFTER the barley is reported to be aviv in the land of Israel.
* The year does NOT start on Rosh Hashana. See above.
* The year count is 240 years ahead of the rabbinical count. i.e 5777 is 6017, but it does not end with the sighting of the new moon on Tishri 1, instead it ends when the barley is aviv. See above.
### Comment on the definitions:
Since this calendar is not a purely mathematical calendar, such as the Gregorian calendar or the traditional Rabbinic calendar, it cannot rely on math alone. It needs to be tied to different services on the web to get updates on the new moon sighting as well as the status of the barley in Israel.

It also needs a trusted database of reported sightings from Israel. See aviv/hist_data.py for this.
## Contributing:
This project is in massive need of testing. Don't be shy to post a bug issue or to create a pull-request. Dates that are giving the wrong information needs to be bug-reported so that I can correct any errors in the calculations.

It's worth noting that this is my 'learning-by-doing-project' to learn python. In other words, please contribute and don't feel shy about pointing out obvious errors or style related issues. Please create an issue or a pull-request.
## Donations:
If you want to contribute financially it's much appreciated, and needed.
### Paypal:
You can find my Paypal account [here](https://www.paypal.me/johanthoren).
