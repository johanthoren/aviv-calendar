# aviv-calendar
## Goal: 
Tries to find out what day it is according to biblical time keeping.
## Usage:
`./core.py --location <city> [--country <country>] [--geocoder <google|astral>]`
## Status:
Right now it does a few things when called upon:
* It gives you a lot of current data on your chosen location.
### Screenshot:
![aviv-calendar screenshot](https://www.avivcalendar.com/img/screenshot_2.png)
## Dependencies:
Depends on *astral*. Install with `pip install astral`.
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
It's worth noting that this is my 'learning-by-doing-project' to learn python. In other words, please contribute and don't feel shy about pointing out obvious errors or style related issues. Please create an issue or a pull-request.
## Donations:
If you want to contribute financially it's much appreciated, and needed.
### Paypal:
You can find my Paypal account [here](https://www.paypal.me/johanthoren).
