# aviv-calendar
## Goal: 
Tries to find out what day it is according to biblical time keeping.
## Status:
Right now it does nothing, except give you the current biblical day
of week as well as telling you if it's a weekly Sabbath or not.
## Dependencies:
Depends on *astral*. Install with `pip install astral`.
## Definitions:
The aviv-calendar project is based on the following ideas:
* The day starts at sundown.
* The month starts when the first sliver of the new moon is sighted in the land of Israel.
* The year starts on the first new moon AFTER the barley is reported to be aviv in the land of Israel.
* The year does NOT start on Rosh Hashana. See above.
* The year count is 240 years ahead of the rabbinical count. i.e 5777 is 6017, but it does not end on Tishri 1, instead it ends when the barley is sighted, see above.
### Comment on the definitions:
Since this calendar is not a purely mathematical calendar, such as the Gregorian calendar or the traditional Rabbinic calendar, it cannot rely on math alone. It needs to be tied to different services on the web to get updates on the new moon sighting as well as the status of the barley in Israel.
