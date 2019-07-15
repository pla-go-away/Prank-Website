Monitors 100+ forums for phone numbers in the Classifieds.
Collects Twitter complainers with ICANN data
Returns Florida registered voters who turn 21 and 55 today
Coupled with FullContact (needs API token on line 1078)
Uses Quart (not Flask due to threading).  Templates may not be up to date.

Random ramblings
Zip code dict (lines 22 – 363)
	This is used on the forum page to give you the location of the poster, and a local meetup spot.

RSS_URLS (lines 365-532) links used to get the forum phone numbers 

First, last, company , occupation (534 – 718)
	Random profile generator in the sidebar in case the pranker is caught off guard

Twitter
Runs every hour and only keeps those within the past 6(?) hours.
Names are found through the module Twint, which uses multithreading – hence why the framework is Quart and not Flask. Essentially the same thing.
If you want FullContact (it’s an astounding, free social media … for a lack of better words .. doxing tool) that will pull up the twitter complainer’s other accounts, line 1078 is where the new API goes.
