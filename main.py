from quart import Quart, render_template, Markup, redirect, url_for, request, url_for
import feedparser
import re
import time
from datetime import timedelta, date, datetime, timezone
import timestring
import itertools
import random
from random import sample
import threading
from dateutil import parser
from dateutil.tz import *
import asyncio
import twint
import bs4
import sqlite3
import requests
from lxml import html
import pymsgbox


zipcodes = {'201': ('ET', 'US', 'New Jersey', '<a href="https://www.google.com/maps/place/Hackensack,+New+Jersey" rel="noreferrer" target="_blank">Hackensack</a> <a href="https://www.google.com/maps/place/Jersey+City,+New+Jersey" rel="noreferrer" target="_blank">Jersey City</a> <a href="https://www.google.com/maps/place/Union+City,+New+Jersey" rel="noreferrer" target="_blank">Union City</a> <a href="https://www.google.com/maps/place/Rutherford,+New+Jersey" rel="noreferrer" target="_blank">Rutherford</a> <a href="https://www.google.com/maps/place/Leonia,+New+Jersey" rel="noreferrer" target="_blank">Leonia</a>'),
        '202': ('ET', 'US', 'District of Columbia', '<a href="https://www.google.com/maps/place/District+of+Columbia" rel="noreferrer" target="_blank">All areas</a>'),
        '203': ('ET', 'US', 'Connecticut', '<a href="https://www.google.com/maps/place/Bridgeport,+Connecticut" rel="noreferrer" target="_blank">Bridgeport</a> <a href="https://www.google.com/maps/place/New+Haven,+Connecticut" rel="noreferrer" target="_blank">New Haven</a> <a href="https://www.google.com/maps/place/Stamford,+Connecticut" rel="noreferrer" target="_blank">Stamford</a> <a href="https://www.google.com/maps/place/Waterbury,+Connecticut" rel="noreferrer" target="_blank">Waterbury</a> <a href="https://www.google.com/maps/place/Norwalk,+Connecticut" rel="noreferrer" target="_blank">Norwalk</a> <a href="https://www.google.com/maps/place/Danbury,+Connecticut" rel="noreferrer" target="_blank">Danbury</a> <a href="https://www.google.com/maps/place/Greenwich,+Connecticut" rel="noreferrer" target="_blank">Greenwich</a>'),
        '204': ('CT', 'Ca', 'Manitoba', '<a href="https://www.google.com/maps/place/Manitoba" rel="noreferrer" target="_blank">All areas</a>'),
        '205': ('CT', 'US', 'Alabama', '<a href="https://www.google.com/maps/place/Birmingham,+Alabama" rel="noreferrer" target="_blank">Birmingham</a> <a href="https://www.google.com/maps/place/Huntsville,+Alabama" rel="noreferrer" target="_blank">Huntsville</a> <a href="https://www.google.com/maps/place/Tuscaloosa,+Alabama" rel="noreferrer" target="_blank">Tuscaloosa</a> <a href="https://www.google.com/maps/place/Anniston,+Alabama" rel="noreferrer" target="_blank">Anniston</a>'),
        '206': ('PT', 'US', 'Washington', '<a href="https://www.google.com/maps/place/Seattle,+Washington" rel="noreferrer" target="_blank">Seattle</a> <a href="https://www.google.com/maps/place/Everett,+Washington" rel="noreferrer" target="_blank">Everett</a>'),
        '207': ('ET', 'US', 'Maine', '<a href="https://www.google.com/maps/place/Maine" rel="noreferrer" target="_blank">All areas</a>'),
        '208': ('*MT, PT', 'US', 'Idaho', '<a href="https://www.google.com/maps/place/Idaho" rel="noreferrer" target="_blank">All areas</a>'),
        '209': ('PT', 'US', 'California', '<a href="https://www.google.com/maps/place/Stockton,+California" rel="noreferrer" target="_blank">Stockton</a> <a href="https://www.google.com/maps/place/Modesto,+California" rel="noreferrer" target="_blank">Modesto</a> <a href="https://www.google.com/maps/place/Merced,+California" rel="noreferrer" target="_blank">Merced</a> <a href="https://www.google.com/maps/place/Oakdale,+California" rel="noreferrer" target="_blank">Oakdale</a>'),
        '210': ('CT', 'US', 'Texas', '<a href="https://www.google.com/maps/place/San+Antonio,+Texas" rel="noreferrer" target="_blank">San Antonio</a>'),
        '212': ('ET', 'US', 'New York', '<a href="https://www.google.com/maps/place/New+York+City+-+Manhattan,+New+York" rel="noreferrer" target="_blank">New York City - Manhattan</a>'),
        '213': ('PT', 'US', 'California', '<a href="https://www.google.com/maps/place/Los+Angeles,+California" rel="noreferrer" target="_blank">Los Angeles</a> <a href="https://www.google.com/maps/place/Compton,+California" rel="noreferrer" target="_blank">Compton</a>'),
        '214': ('CT', 'US', 'Texas', '<a href="https://www.google.com/maps/place/Dallas,+Texas" rel="noreferrer" target="_blank">Dallas</a>'),
        '215': ('ET', 'US', 'Pennsylvania', '<a href="https://www.google.com/maps/place/Philadelphia,+Pennsylvania" rel="noreferrer" target="_blank">Philadelphia</a> <a href="https://www.google.com/maps/place/Lansdale,+Pennsylvania" rel="noreferrer" target="_blank">Lansdale</a> <a href="https://www.google.com/maps/place/Doylestown,+Pennsylvania" rel="noreferrer" target="_blank">Doylestown</a> <a href="https://www.google.com/maps/place/Newtown,+Pennsylvania" rel="noreferrer" target="_blank">Newtown</a> <a href="https://www.google.com/maps/place/Quakertown,+Pennsylvania" rel="noreferrer" target="_blank">Quakertown</a>'),
        '216': ('ET', 'US', 'Ohio', '<a href="https://www.google.com/maps/place/Cleveland,+Ohio" rel="noreferrer" target="_blank">Cleveland</a> <a href="https://www.google.com/maps/place/Terrace,+Ohio" rel="noreferrer" target="_blank">Terrace</a> <a href="https://www.google.com/maps/place/Independence,+Ohio" rel="noreferrer" target="_blank">Independence</a> <a href="https://www.google.com/maps/place/Montrose,+Ohio" rel="noreferrer" target="_blank">Montrose</a>'),
        '217': ('CT', 'US', 'Illinois', '<a href="https://www.google.com/maps/place/Springfield,+Illinois" rel="noreferrer" target="_blank">Springfield</a> <a href="https://www.google.com/maps/place/Champaign+Urbana,+Illinois" rel="noreferrer" target="_blank">Champaign Urbana</a> <a href="https://www.google.com/maps/place/Decatur,+Illinois" rel="noreferrer" target="_blank">Decatur</a> <a href="https://www.google.com/maps/place/Central+Illinois,+Illinois" rel="noreferrer" target="_blank">Central Illinois</a>'),
        '218': ('CT', 'US', 'Minnesota', '<a href="https://www.google.com/maps/place/Duluth,+Minnesota" rel="noreferrer" target="_blank">Duluth</a> <a href="https://www.google.com/maps/place/Virginia,+Minnesota" rel="noreferrer" target="_blank">Virginia</a> <a href="https://www.google.com/maps/place/Moorhead,+Minnesota" rel="noreferrer" target="_blank">Moorhead</a> <a href="https://www.google.com/maps/place/Brainerd,+Minnesota" rel="noreferrer" target="_blank">Brainerd</a> <a href="https://www.google.com/maps/place/Wadena,+Minnesota" rel="noreferrer" target="_blank">Wadena</a>'),
        '219': ('*ET, CT', 'US', 'Indiana', '<a href="https://www.google.com/maps/place/Gary,+Indiana" rel="noreferrer" target="_blank">Gary</a> <a href="https://www.google.com/maps/place/Hammond,+Indiana" rel="noreferrer" target="_blank">Hammond</a> <a href="https://www.google.com/maps/place/Merrillville,+Indiana" rel="noreferrer" target="_blank">Merrillville</a> <a href="https://www.google.com/maps/place/Portage,+Indiana" rel="noreferrer" target="_blank">Portage</a> <a href="https://www.google.com/maps/place/Michigan+City,+Indiana" rel="noreferrer" target="_blank">Michigan City</a> <a href="https://www.google.com/maps/place/Valparaiso,+Indiana" rel="noreferrer" target="_blank">Valparaiso</a>'),
        '224': ('CT', 'US', 'Illinois', '<a href="https://www.google.com/maps/place/Northbrook,+Illinois" rel="noreferrer" target="_blank">Northbrook</a> <a href="https://www.google.com/maps/place/Skokie,+Illinois" rel="noreferrer" target="_blank">Skokie</a> <a href="https://www.google.com/maps/place/Evanston,+Illinois" rel="noreferrer" target="_blank">Evanston</a> <a href="https://www.google.com/maps/place/Glenview,+Illinois" rel="noreferrer" target="_blank">Glenview</a> <a href="https://www.google.com/maps/place/Waukegan,+Illinois" rel="noreferrer" target="_blank">Waukegan</a> <a href="https://www.google.com/maps/place/Desplaines,+Illinois" rel="noreferrer" target="_blank">Desplaines</a> <a href="https://www.google.com/maps/place/Elk+Grove,+Illinois" rel="noreferrer" target="_blank">Elk Grove</a>'),
        '225': ('CT', 'US', 'Louisiana', '<a href="https://www.google.com/maps/place/Baton+Rouge,+Louisiana" rel="noreferrer" target="_blank">Baton Rouge and Surrounding Areas</a>'),
        '226': ('ET', 'Ca', 'Ontario', '<a href="https://www.google.com/maps/place/Ontario:+London+Area,+Ontario" rel="noreferrer" target="_blank">Ontario: London Area</a> <a href="https://www.google.com/maps/place/Kitchener,+Ontario" rel="noreferrer" target="_blank">Kitchener</a> <a href="https://www.google.com/maps/place/Cambridge,+Ontario" rel="noreferrer" target="_blank">Cambridge</a> <a href="https://www.google.com/maps/place/Windsor,+Ontario" rel="noreferrer" target="_blank">Windsor</a>'),
        '228': ('CT', 'US', 'Mississippi', '<a href="https://www.google.com/maps/place/Gulfport,+Mississippi" rel="noreferrer" target="_blank">Gulfport</a> <a href="https://www.google.com/maps/place/Biloxi,+Mississippi" rel="noreferrer" target="_blank">Biloxi</a> <a href="https://www.google.com/maps/place/Pascagoula,+Mississippi" rel="noreferrer" target="_blank">Pascagoula</a> <a href="https://www.google.com/maps/place/Bay+St.+Louis,+Mississippi" rel="noreferrer" target="_blank">Bay St. Louis</a>'),
        '229': ('ET', 'US', 'Georgia', '<a href="https://www.google.com/maps/place/Albany,+Georgia" rel="noreferrer" target="_blank">Albany</a> <a href="https://www.google.com/maps/place/Valdosta,+Georgia" rel="noreferrer" target="_blank">Valdosta</a> <a href="https://www.google.com/maps/place/Thomasville,+Georgia" rel="noreferrer" target="_blank">Thomasville</a> <a href="https://www.google.com/maps/place/Bainbridge,+Georgia" rel="noreferrer" target="_blank">Bainbridge</a> <a href="https://www.google.com/maps/place/Tifton,+Georgia" rel="noreferrer" target="_blank">Tifton</a> <a href="https://www.google.com/maps/place/Americus,+Georgia" rel="noreferrer" target="_blank">Americus</a> <a href="https://www.google.com/maps/place/Moultrie,+Georgia" rel="noreferrer" target="_blank">Moultrie</a> <a href="https://www.google.com/maps/place/Cordele,+Georgia" rel="noreferrer" target="_blank">Cordele</a>'),
        '231': ('ET', 'US', 'Michigan', '<a href="https://www.google.com/maps/place/Muskegon,+Michigan" rel="noreferrer" target="_blank">Muskegon</a> <a href="https://www.google.com/maps/place/Traverse+City,+Michigan" rel="noreferrer" target="_blank">Traverse City</a> <a href="https://www.google.com/maps/place/Big+Rapids,+Michigan" rel="noreferrer" target="_blank">Big Rapids</a> <a href="https://www.google.com/maps/place/Cadillac,+Michigan" rel="noreferrer" target="_blank">Cadillac</a> <a href="https://www.google.com/maps/place/Cheboygan,+Michigan" rel="noreferrer" target="_blank">Cheboygan</a>'),
        '234': ('ET', 'US', 'Ohio', '<a href="https://www.google.com/maps/place/Akron,+Ohio" rel="noreferrer" target="_blank">Akron</a> <a href="https://www.google.com/maps/place/Youngstown,+Ohio" rel="noreferrer" target="_blank">Youngstown</a> <a href="https://www.google.com/maps/place/Canton,+Ohio" rel="noreferrer" target="_blank">Canton</a> <a href="https://www.google.com/maps/place/Warren,+Ohio" rel="noreferrer" target="_blank">Warren</a> <a href="https://www.google.com/maps/place/Kent,+Ohio" rel="noreferrer" target="_blank">Kent</a> <a href="https://www.google.com/maps/place/Alliance,+Ohio" rel="noreferrer" target="_blank">Alliance</a> <a href="https://www.google.com/maps/place/Medina,+Ohio" rel="noreferrer" target="_blank">Medina</a> <a href="https://www.google.com/maps/place/New+Philadelphia,+Ohio" rel="noreferrer" target="_blank">New Philadelphia</a>'),
        '236': ('PT', 'Ca', 'British Columbia', '<a href="https://www.google.com/maps/place/Vancouver,+British+Columbia" rel="noreferrer" target="_blank">Vancouver</a> <a href="https://www.google.com/maps/place/Fraser+Valley,+British+Columbia" rel="noreferrer" target="_blank">Fraser Valley</a>'),
        '239': ('ET', 'US', 'Florida', '<a href="https://www.google.com/maps/place/Ft.+Myers,+Florida" rel="noreferrer" target="_blank">Ft. Myers</a> <a href="https://www.google.com/maps/place/Naples,+Florida" rel="noreferrer" target="_blank">Naples</a> <a href="https://www.google.com/maps/place/Cape+Coral,+Florida" rel="noreferrer" target="_blank">Cape Coral</a> <a href="https://www.google.com/maps/place/Bonita+Springs,+Florida" rel="noreferrer" target="_blank">Bonita Springs</a> <a href="https://www.google.com/maps/place/Immokalee,+Florida" rel="noreferrer" target="_blank">Immokalee</a> <a href="https://www.google.com/maps/place/Lehigh+Acres,+Florida" rel="noreferrer" target="_blank">Lehigh Acres</a> <a href="https://www.google.com/maps/place/Sanibel,+Florida" rel="noreferrer" target="_blank">Sanibel</a> <a href="https://www.google.com/maps/place/Captiva,+Florida" rel="noreferrer" target="_blank">Captiva</a> <a href="https://www.google.com/maps/place/Pine+Island,+Florida" rel="noreferrer" target="_blank">Pine Island</a>'),
        '240': ('ET', 'US', 'Maryland', '<a href="https://www.google.com/maps/place/Rockville,+Maryland" rel="noreferrer" target="_blank">Rockville</a> <a href="https://www.google.com/maps/place/Silver+Spring,+Maryland" rel="noreferrer" target="_blank">Silver Spring</a> <a href="https://www.google.com/maps/place/Bethesda,+Maryland" rel="noreferrer" target="_blank">Bethesda</a> <a href="https://www.google.com/maps/place/Gaithersburg,+Maryland" rel="noreferrer" target="_blank">Gaithersburg</a> <a href="https://www.google.com/maps/place/Frederick,+Maryland" rel="noreferrer" target="_blank">Frederick</a> <a href="https://www.google.com/maps/place/Laurel,+Maryland" rel="noreferrer" target="_blank">Laurel</a> <a href="https://www.google.com/maps/place/Hagerstown,+Maryland" rel="noreferrer" target="_blank">Hagerstown</a>'),
        '248': ('ET', 'US', 'Michigan', '<a href="https://www.google.com/maps/place/Troy,+Michigan" rel="noreferrer" target="_blank">Troy</a> <a href="https://www.google.com/maps/place/Pontiac,+Michigan" rel="noreferrer" target="_blank">Pontiac</a> <a href="https://www.google.com/maps/place/Royal+Oak,+Michigan" rel="noreferrer" target="_blank">Royal Oak</a> <a href="https://www.google.com/maps/place/Birmingham,+Michigan" rel="noreferrer" target="_blank">Birmingham</a> <a href="https://www.google.com/maps/place/Rochester,+Michigan" rel="noreferrer" target="_blank">Rochester</a> <a href="https://www.google.com/maps/place/Farmington+Hills,+Michigan" rel="noreferrer" target="_blank">Farmington Hills</a>'),
        '249': ('ET', 'Ca', 'Ontario', '<a href="https://www.google.com/maps/place/Greater+Sudbury,+Ontario" rel="noreferrer" target="_blank">Greater Sudbury</a> <a href="https://www.google.com/maps/place/Sault+Ste.+Marie,+Ontario" rel="noreferrer" target="_blank">Sault Ste. Marie</a> <a href="https://www.google.com/maps/place/North+Bay,+Ontario" rel="noreferrer" target="_blank">North Bay</a>'),
        '250': ('PT', 'Ca', 'British Columbia', '<a href="https://www.google.com/maps/place/British+Columbia:+Victoria,+British+Columbia" rel="noreferrer" target="_blank">British Columbia: Victoria</a> <a href="https://www.google.com/maps/place/Kamloops,+British+Columbia" rel="noreferrer" target="_blank">Kamloops</a> <a href="https://www.google.com/maps/place/Kelowna,+British+Columbia" rel="noreferrer" target="_blank">Kelowna</a> <a href="https://www.google.com/maps/place/Prince+George,+British+Columbia" rel="noreferrer" target="_blank">Prince George</a> <a href="https://www.google.com/maps/place/Nanaimo,+British+Columbia" rel="noreferrer" target="_blank">Nanaimo</a>'),
        '251': ('CT', 'US', 'Alabama', '<a href="https://www.google.com/maps/place/Mobile,+Alabama" rel="noreferrer" target="_blank">Mobile</a> <a href="https://www.google.com/maps/place/Prichard,+Alabama" rel="noreferrer" target="_blank">Prichard</a> <a href="https://www.google.com/maps/place/Tillmans+Corner,+Alabama" rel="noreferrer" target="_blank">Tillmans Corner</a> <a href="https://www.google.com/maps/place/Fairhope,+Alabama" rel="noreferrer" target="_blank">Fairhope</a> <a href="https://www.google.com/maps/place/Jackson,+Alabama" rel="noreferrer" target="_blank">Jackson</a> <a href="https://www.google.com/maps/place/Gulfshores,+Alabama" rel="noreferrer" target="_blank">Gulfshores</a>'),
        '252': ('ET', 'US', 'North Carolina', '<a href="https://www.google.com/maps/place/Greenville,+North+Carolina" rel="noreferrer" target="_blank">Greenville</a> <a href="https://www.google.com/maps/place/Rocky+Mount,+North+Carolina" rel="noreferrer" target="_blank">Rocky Mount</a> <a href="https://www.google.com/maps/place/Wilson,+North+Carolina" rel="noreferrer" target="_blank">Wilson</a> <a href="https://www.google.com/maps/place/New+Bern,+North+Carolina" rel="noreferrer" target="_blank">New Bern</a>'),
        '253': ('PT', 'US', 'Washington', '<a href="https://www.google.com/maps/place/Tacoma,+Washington" rel="noreferrer" target="_blank">Tacoma</a> <a href="https://www.google.com/maps/place/Kent,+Washington" rel="noreferrer" target="_blank">Kent</a> <a href="https://www.google.com/maps/place/Auburn,+Washington" rel="noreferrer" target="_blank">Auburn</a>'),
        '254': ('CT', 'US', 'Texas', '<a href="https://www.google.com/maps/place/Waco,+Texas" rel="noreferrer" target="_blank">Waco</a> <a href="https://www.google.com/maps/place/Killeen,+Texas" rel="noreferrer" target="_blank">Killeen</a> <a href="https://www.google.com/maps/place/Temple,+Texas" rel="noreferrer" target="_blank">Temple</a>'),
        '256': ('CT', 'US', 'Alabama', '<a href="https://www.google.com/maps/place/Huntsville,+Alabama" rel="noreferrer" target="_blank">Huntsville</a> <a href="https://www.google.com/maps/place/Anniston,+Alabama" rel="noreferrer" target="_blank">Anniston</a> <a href="https://www.google.com/maps/place/Decatur,+Alabama" rel="noreferrer" target="_blank">Decatur</a> <a href="https://www.google.com/maps/place/Gadsden,+Alabama" rel="noreferrer" target="_blank">Gadsden</a> <a href="https://www.google.com/maps/place/Florence,+Alabama" rel="noreferrer" target="_blank">Florence</a>'),
        '260': ('ET', 'US', 'Indiana', '<a href="https://www.google.com/maps/place/Fort+Wayne,+Indiana" rel="noreferrer" target="_blank">Fort Wayne</a> <a href="https://www.google.com/maps/place/Huntington,+Indiana" rel="noreferrer" target="_blank">Huntington</a> <a href="https://www.google.com/maps/place/Wabash,+Indiana" rel="noreferrer" target="_blank">Wabash</a> <a href="https://www.google.com/maps/place/Lagrange,+Indiana" rel="noreferrer" target="_blank">Lagrange</a>'),
        '262': ('CT', 'US', 'Wisconsin', '<a href="https://www.google.com/maps/place/Green+Bay,+Wisconsin" rel="noreferrer" target="_blank">Green Bay</a> <a href="https://www.google.com/maps/place/Appleton,+Wisconsin" rel="noreferrer" target="_blank">Appleton</a> <a href="https://www.google.com/maps/place/Racine,+Wisconsin" rel="noreferrer" target="_blank">Racine</a> <a href="https://www.google.com/maps/place/Kenosha,+Wisconsin" rel="noreferrer" target="_blank">Kenosha</a> <a href="https://www.google.com/maps/place/Oshkosh,+Wisconsin" rel="noreferrer" target="_blank">Oshkosh</a> <a href="https://www.google.com/maps/place/Waukesha,+Wisconsin" rel="noreferrer" target="_blank">Waukesha</a> <a href="https://www.google.com/maps/place/Menomonee+Falls,+Wisconsin" rel="noreferrer" target="_blank">Menomonee Falls</a> <a href="https://www.google.com/maps/place/West+Bend,+Wisconsin" rel="noreferrer" target="_blank">West Bend</a> <a href="https://www.google.com/maps/place/Sheboygan,+Wisconsin" rel="noreferrer" target="_blank">Sheboygan</a>'),
        '267': ('ET', 'US', 'Pennsylvania', '<a href="https://www.google.com/maps/place/Philadelphia,+Pennsylvania" rel="noreferrer" target="_blank">Philadelphia</a> <a href="https://www.google.com/maps/place/Lansdale,+Pennsylvania" rel="noreferrer" target="_blank">Lansdale</a> <a href="https://www.google.com/maps/place/Doylestown,+Pennsylvania" rel="noreferrer" target="_blank">Doylestown</a> <a href="https://www.google.com/maps/place/Newtown,+Pennsylvania" rel="noreferrer" target="_blank">Newtown</a> <a href="https://www.google.com/maps/place/Quakertown,+Pennsylvania" rel="noreferrer" target="_blank">Quakertown</a>'),
        '269': ('ET', 'US', 'Michigan', '<a href="https://www.google.com/maps/place/Kalamazoo,+Michigan" rel="noreferrer" target="_blank">Kalamazoo</a> <a href="https://www.google.com/maps/place/Battle+Creek,+Michigan" rel="noreferrer" target="_blank">Battle Creek</a> <a href="https://www.google.com/maps/place/St.+Joseph,+Michigan" rel="noreferrer" target="_blank">St. Joseph</a> <a href="https://www.google.com/maps/place/Three+Rivers,+Michigan" rel="noreferrer" target="_blank">Three Rivers</a> <a href="https://www.google.com/maps/place/South+Haven,+Michigan" rel="noreferrer" target="_blank">South Haven</a> <a href="https://www.google.com/maps/place/Benton+Harbor,+Michigan" rel="noreferrer" target="_blank">Benton Harbor</a> <a href="https://www.google.com/maps/place/Sturgis,+Michigan" rel="noreferrer" target="_blank">Sturgis</a> <a href="https://www.google.com/maps/place/Hastings,+Michigan" rel="noreferrer" target="_blank">Hastings</a>'),
        '270': ('*ET, CT', 'US', 'Kentucky', '<a href="https://www.google.com/maps/place/Bowling+Green,+Kentucky" rel="noreferrer" target="_blank">Bowling Green</a> <a href="https://www.google.com/maps/place/Paducah,+Kentucky" rel="noreferrer" target="_blank">Paducah</a> <a href="https://www.google.com/maps/place/Owensboro,+Kentucky" rel="noreferrer" target="_blank">Owensboro</a> <a href="https://www.google.com/maps/place/Hopkinsville,+Kentucky" rel="noreferrer" target="_blank">Hopkinsville</a>'),
        '272': ('ET', 'US', 'Pennsylvania', '<a href="https://www.google.com/maps/place/Williamsport+,+Pennsylvania" rel="noreferrer" target="_blank">Williamsport </a> <a href="https://www.google.com/maps/place/Scranton+,+Pennsylvania" rel="noreferrer" target="_blank">Scranton </a> <a href="https://www.google.com/maps/place/Wilkes-Barre+and+Monroe+County,+Pennsylvania" rel="noreferrer" target="_blank">Wilkes-Barre and Monroe County</a>'),
        '276': ('ET', 'US', 'Virginia', '<a href="https://www.google.com/maps/place/Martinsville,+Virginia" rel="noreferrer" target="_blank">Martinsville</a> <a href="https://www.google.com/maps/place/Abingdon,+Virginia" rel="noreferrer" target="_blank">Abingdon</a> <a href="https://www.google.com/maps/place/Wytheville,+Virginia" rel="noreferrer" target="_blank">Wytheville</a> <a href="https://www.google.com/maps/place/Bristol,+Virginia" rel="noreferrer" target="_blank">Bristol</a> <a href="https://www.google.com/maps/place/Marion,+Virginia" rel="noreferrer" target="_blank">Marion</a> <a href="https://www.google.com/maps/place/Collinsville,+Virginia" rel="noreferrer" target="_blank">Collinsville</a>'),
        '281': ('CT', 'US', 'Texas', '<a href="https://www.google.com/maps/place/Houston,+Texas" rel="noreferrer" target="_blank">Houston</a> <a href="https://www.google.com/maps/place/Sugar+Land,+Texas" rel="noreferrer" target="_blank">Sugar Land</a> <a href="https://www.google.com/maps/place/Buffalo,+Texas" rel="noreferrer" target="_blank">Buffalo</a> <a href="https://www.google.com/maps/place/Airline,+Texas" rel="noreferrer" target="_blank">Airline</a> <a href="https://www.google.com/maps/place/Greenspoint,+Texas" rel="noreferrer" target="_blank">Greenspoint</a> <a href="https://www.google.com/maps/place/Spring,+Texas" rel="noreferrer" target="_blank">Spring</a>'),
        '289': ('ET', 'Ca', 'Ontario', '<a href="https://www.google.com/maps/place/Ontario:+Hamilton,+Ontario" rel="noreferrer" target="_blank">Ontario: Hamilton</a> <a href="https://www.google.com/maps/place/Niagara+Falls,+Ontario" rel="noreferrer" target="_blank">Niagara Falls</a> <a href="https://www.google.com/maps/place/Markham,+Ontario" rel="noreferrer" target="_blank">Markham</a> <a href="https://www.google.com/maps/place/Mississauga,+Ontario" rel="noreferrer" target="_blank">Mississauga</a> <a href="https://www.google.com/maps/place/Brampton,+Ontario" rel="noreferrer" target="_blank">Brampton</a>'),
        '301': ('ET', 'US', 'Maryland', '<a href="https://www.google.com/maps/place/Rockville,+Maryland" rel="noreferrer" target="_blank">Rockville</a> <a href="https://www.google.com/maps/place/Silver+Spring,+Maryland" rel="noreferrer" target="_blank">Silver Spring</a> <a href="https://www.google.com/maps/place/Bethesda,+Maryland" rel="noreferrer" target="_blank">Bethesda</a> <a href="https://www.google.com/maps/place/Gaithersburg,+Maryland" rel="noreferrer" target="_blank">Gaithersburg</a> <a href="https://www.google.com/maps/place/Frederick,+Maryland" rel="noreferrer" target="_blank">Frederick</a> <a href="https://www.google.com/maps/place/Laurel,+Maryland" rel="noreferrer" target="_blank">Laurel</a> <a href="https://www.google.com/maps/place/Hagerstown,+Maryland" rel="noreferrer" target="_blank">Hagerstown</a>'),
        '302': ('ET', 'US', 'Delaware', '<a href="https://www.google.com/maps/place/Delaware" rel="noreferrer" target="_blank">All areas</a>'),
        '303': ('MT', 'US', 'Colorado', '<a href="https://www.google.com/maps/place/Denver,+Colorado" rel="noreferrer" target="_blank">Denver</a> <a href="https://www.google.com/maps/place/Littleton,+Colorado" rel="noreferrer" target="_blank">Littleton</a> <a href="https://www.google.com/maps/place/Englewood,+Colorado" rel="noreferrer" target="_blank">Englewood</a> <a href="https://www.google.com/maps/place/Arvada,+Colorado" rel="noreferrer" target="_blank">Arvada</a> <a href="https://www.google.com/maps/place/Boulder,+Colorado" rel="noreferrer" target="_blank">Boulder</a> <a href="https://www.google.com/maps/place/Aurora,+Colorado" rel="noreferrer" target="_blank">Aurora</a>'),
        '304': ('ET', 'US', 'West Virginia', '<a href="https://www.google.com/maps/place/West+Virginia" rel="noreferrer" target="_blank">All areas</a>'),
        '305': ('ET', 'US', 'Florida', '<a href="https://www.google.com/maps/place/Miami,+Florida" rel="noreferrer" target="_blank">Miami</a> <a href="https://www.google.com/maps/place/Perrine,+Florida" rel="noreferrer" target="_blank">Perrine</a> <a href="https://www.google.com/maps/place/Homestead,+Florida" rel="noreferrer" target="_blank">Homestead</a> <a href="https://www.google.com/maps/place/Florida+Keys,+Florida" rel="noreferrer" target="_blank">Florida Keys</a>'),
        '306': ('CT', 'Ca', 'Saskatchewan', '<a href="https://www.google.com/maps/place/Saskatchewan" rel="noreferrer" target="_blank">All areas</a>'),
        '307': ('MT', 'US', 'Wyoming', '<a href="https://www.google.com/maps/place/Wyoming" rel="noreferrer" target="_blank">All areas</a>'),
        '308': ('*CT, MT', 'US', 'Nebraska', '<a href="https://www.google.com/maps/place/Grand+Island,+Nebraska" rel="noreferrer" target="_blank">Grand Island</a> <a href="https://www.google.com/maps/place/Kearney,+Nebraska" rel="noreferrer" target="_blank">Kearney</a> <a href="https://www.google.com/maps/place/North+Platte,+Nebraska" rel="noreferrer" target="_blank">North Platte</a> <a href="https://www.google.com/maps/place/Scottsbluff,+Nebraska" rel="noreferrer" target="_blank">Scottsbluff</a>'),
        '309': ('CT', 'US', 'Illinois', '<a href="https://www.google.com/maps/place/Peoria,+Illinois" rel="noreferrer" target="_blank">Peoria</a> <a href="https://www.google.com/maps/place/Bloomington,+Illinois" rel="noreferrer" target="_blank">Bloomington</a> <a href="https://www.google.com/maps/place/Rock+Island,+Illinois" rel="noreferrer" target="_blank">Rock Island</a> <a href="https://www.google.com/maps/place/Galesburg,+Illinois" rel="noreferrer" target="_blank">Galesburg</a> <a href="https://www.google.com/maps/place/Macomb,+Illinois" rel="noreferrer" target="_blank">Macomb</a>'),
        '310': ('PT', 'US', 'California', '<a href="https://www.google.com/maps/place/Compton,+California" rel="noreferrer" target="_blank">Compton</a> <a href="https://www.google.com/maps/place/Santa+Monica,+California" rel="noreferrer" target="_blank">Santa Monica</a> <a href="https://www.google.com/maps/place/Beverly+Hills,+California" rel="noreferrer" target="_blank">Beverly Hills</a> <a href="https://www.google.com/maps/place/West+LA,+California" rel="noreferrer" target="_blank">West LA</a> <a href="https://www.google.com/maps/place/Inglewood,+California" rel="noreferrer" target="_blank">Inglewood</a> <a href="https://www.google.com/maps/place/Redondo,+California" rel="noreferrer" target="_blank">Redondo</a> <a href="https://www.google.com/maps/place/El+Segundo,+California" rel="noreferrer" target="_blank">El Segundo</a> <a href="https://www.google.com/maps/place/Culver+City,+California" rel="noreferrer" target="_blank">Culver City</a> <a href="https://www.google.com/maps/place/Torrance,+California" rel="noreferrer" target="_blank">Torrance</a>'),
        '312': ('CT', 'US', 'Illinois', '<a href="https://www.google.com/maps/place/Chicago,+Illinois" rel="noreferrer" target="_blank">Chicago</a> <a href="https://www.google.com/maps/place/Wheeling,+Illinois" rel="noreferrer" target="_blank">Wheeling</a>'),
        '313': ('ET', 'US', 'Michigan', '<a href="https://www.google.com/maps/place/Detroit,+Michigan" rel="noreferrer" target="_blank">Detroit</a> <a href="https://www.google.com/maps/place/Livonia,+Michigan" rel="noreferrer" target="_blank">Livonia</a> <a href="https://www.google.com/maps/place/Dearborn,+Michigan" rel="noreferrer" target="_blank">Dearborn</a>'),
        '314': ('CT', 'US', 'Missouri', '<a href="https://www.google.com/maps/place/Saint+Louis,+Missouri" rel="noreferrer" target="_blank">Saint Louis</a> <a href="https://www.google.com/maps/place/Ladue,+Missouri" rel="noreferrer" target="_blank">Ladue</a> <a href="https://www.google.com/maps/place/Kirkwood,+Missouri" rel="noreferrer" target="_blank">Kirkwood</a> <a href="https://www.google.com/maps/place/Creve+Coeur,+Missouri" rel="noreferrer" target="_blank">Creve Coeur</a> <a href="https://www.google.com/maps/place/Overland,+Missouri" rel="noreferrer" target="_blank">Overland</a> <a href="https://www.google.com/maps/place/Ferguson,+Missouri" rel="noreferrer" target="_blank">Ferguson</a>'),
        '315': ('ET', 'US', 'New York', '<a href="https://www.google.com/maps/place/Syracuse,+New+York" rel="noreferrer" target="_blank">Syracuse</a> <a href="https://www.google.com/maps/place/Utica,+New+York" rel="noreferrer" target="_blank">Utica</a> <a href="https://www.google.com/maps/place/Watertown,+New+York" rel="noreferrer" target="_blank">Watertown</a> <a href="https://www.google.com/maps/place/Rome,+New+York" rel="noreferrer" target="_blank">Rome</a>'),
        '316': ('CT', 'US', 'Kansas', '<a href="https://www.google.com/maps/place/Wichita,+Kansas" rel="noreferrer" target="_blank">Wichita</a> <a href="https://www.google.com/maps/place/Hutchinson,+Kansas" rel="noreferrer" target="_blank">Hutchinson</a>'),
        '317': ('ET', 'US', 'Indiana', '<a href="https://www.google.com/maps/place/Indianapolis,+Indiana" rel="noreferrer" target="_blank">Indianapolis</a> <a href="https://www.google.com/maps/place/Carmel,+Indiana" rel="noreferrer" target="_blank">Carmel</a> <a href="https://www.google.com/maps/place/Fishers,+Indiana" rel="noreferrer" target="_blank">Fishers</a> <a href="https://www.google.com/maps/place/Greenwood,+Indiana" rel="noreferrer" target="_blank">Greenwood</a>'),
        '318': ('CT', 'US', 'Louisiana', '<a href="https://www.google.com/maps/place/Shreveport,+Louisiana" rel="noreferrer" target="_blank">Shreveport</a> <a href="https://www.google.com/maps/place/Monroe,+Louisiana" rel="noreferrer" target="_blank">Monroe</a> <a href="https://www.google.com/maps/place/Alexandria,+Louisiana" rel="noreferrer" target="_blank">Alexandria</a> <a href="https://www.google.com/maps/place/Ruston,+Louisiana" rel="noreferrer" target="_blank">Ruston</a> <a href="https://www.google.com/maps/place/Natchitoches,+Louisiana" rel="noreferrer" target="_blank">Natchitoches</a>'),
        '319': ('CT', 'US', 'Iowa', '<a href="https://www.google.com/maps/place/Cedar+Rapids,+Iowa" rel="noreferrer" target="_blank">Cedar Rapids</a> <a href="https://www.google.com/maps/place/Iowa+City,+Iowa" rel="noreferrer" target="_blank">Iowa City</a> <a href="https://www.google.com/maps/place/Waterloo,+Iowa" rel="noreferrer" target="_blank">Waterloo</a> <a href="https://www.google.com/maps/place/Burlington,+Iowa" rel="noreferrer" target="_blank">Burlington</a>'),
        '320': ('CT', 'US', 'Minnesota', '<a href="https://www.google.com/maps/place/St.+Cloud,+Minnesota" rel="noreferrer" target="_blank">St. Cloud</a> <a href="https://www.google.com/maps/place/Alexandria,+Minnesota" rel="noreferrer" target="_blank">Alexandria</a> <a href="https://www.google.com/maps/place/Willmar,+Minnesota" rel="noreferrer" target="_blank">Willmar</a> <a href="https://www.google.com/maps/place/Little+Falls,+Minnesota" rel="noreferrer" target="_blank">Little Falls</a>'),
        '321': ('ET', 'US', 'Florida', '<a href="https://www.google.com/maps/place/Cocoa,+Florida" rel="noreferrer" target="_blank">Cocoa</a> <a href="https://www.google.com/maps/place/Melbourne,+Florida" rel="noreferrer" target="_blank">Melbourne</a> <a href="https://www.google.com/maps/place/Eau+Gallie,+Florida" rel="noreferrer" target="_blank">Eau Gallie</a> <a href="https://www.google.com/maps/place/Titusville,+Florida" rel="noreferrer" target="_blank">Titusville</a>'),
        '323': ('PT', 'US', 'California', '<a href="https://www.google.com/maps/place/Los+Angeles,+California" rel="noreferrer" target="_blank">Los Angeles</a> <a href="https://www.google.com/maps/place/Montebello,+California" rel="noreferrer" target="_blank">Montebello</a>'),
        '325': ('CT', 'US', 'Texas', '<a href="https://www.google.com/maps/place/Albilene,+Texas" rel="noreferrer" target="_blank">Albilene</a> <a href="https://www.google.com/maps/place/San+Angelo,+Texas" rel="noreferrer" target="_blank">San Angelo</a> <a href="https://www.google.com/maps/place/Brownwood,+Texas" rel="noreferrer" target="_blank">Brownwood</a> <a href="https://www.google.com/maps/place/Synder,+Texas" rel="noreferrer" target="_blank">Synder</a> <a href="https://www.google.com/maps/place/Sweetwater,+Texas" rel="noreferrer" target="_blank">Sweetwater</a>'),
        '330': ('ET', 'US', 'Ohio', '<a href="https://www.google.com/maps/place/Akron,+Ohio" rel="noreferrer" target="_blank">Akron</a> <a href="https://www.google.com/maps/place/Youngstown,+Ohio" rel="noreferrer" target="_blank">Youngstown</a> <a href="https://www.google.com/maps/place/Canton,+Ohio" rel="noreferrer" target="_blank">Canton</a> <a href="https://www.google.com/maps/place/Warren,+Ohio" rel="noreferrer" target="_blank">Warren</a> <a href="https://www.google.com/maps/place/Kent,+Ohio" rel="noreferrer" target="_blank">Kent</a> <a href="https://www.google.com/maps/place/Alliance,+Ohio" rel="noreferrer" target="_blank">Alliance</a> <a href="https://www.google.com/maps/place/Medina,+Ohio" rel="noreferrer" target="_blank">Medina</a> <a href="https://www.google.com/maps/place/New+Philadelphia,+Ohio" rel="noreferrer" target="_blank">New Philadelphia</a>'),
        '331': ('CT', 'US', 'Illinois', '<a href="https://www.google.com/maps/place/La+Grange,+Illinois" rel="noreferrer" target="_blank">La Grange</a> <a href="https://www.google.com/maps/place/Roselle,+Illinois" rel="noreferrer" target="_blank">Roselle</a> <a href="https://www.google.com/maps/place/Hinsdale,+Illinois" rel="noreferrer" target="_blank">Hinsdale</a> <a href="https://www.google.com/maps/place/Downers+Grove,+Illinois" rel="noreferrer" target="_blank">Downers Grove</a> <a href="https://www.google.com/maps/place/Naperville,+Illinois" rel="noreferrer" target="_blank">Naperville</a> <a href="https://www.google.com/maps/place/Lombard,+Illinois" rel="noreferrer" target="_blank">Lombard</a> <a href="https://www.google.com/maps/place/Elmhurst,+Illinois" rel="noreferrer" target="_blank">Elmhurst</a> <a href="https://www.google.com/maps/place/Aurora,+Illinois" rel="noreferrer" target="_blank">Aurora</a> <a href="https://www.google.com/maps/place/Wheaton,+Illinois" rel="noreferrer" target="_blank">Wheaton</a>'),
        '334': ('CT', 'US', 'Alabama', '<a href="https://www.google.com/maps/place/Montgomery,+Alabama" rel="noreferrer" target="_blank">Montgomery</a> <a href="https://www.google.com/maps/place/Dothan,+Alabama" rel="noreferrer" target="_blank">Dothan</a> <a href="https://www.google.com/maps/place/Auburn,+Alabama" rel="noreferrer" target="_blank">Auburn</a> <a href="https://www.google.com/maps/place/Selma,+Alabama" rel="noreferrer" target="_blank">Selma</a> <a href="https://www.google.com/maps/place/Opelika,+Alabama" rel="noreferrer" target="_blank">Opelika</a> <a href="https://www.google.com/maps/place/Phenix+City,+Alabama" rel="noreferrer" target="_blank">Phenix City</a> <a href="https://www.google.com/maps/place/Tuskegee,+Alabama" rel="noreferrer" target="_blank">Tuskegee</a>'),
        '336': ('ET', 'US', 'North Carolina', '<a href="https://www.google.com/maps/place/Greensboro,+North+Carolina" rel="noreferrer" target="_blank">Greensboro</a> <a href="https://www.google.com/maps/place/Winston+Salem,+North+Carolina" rel="noreferrer" target="_blank">Winston Salem</a> <a href="https://www.google.com/maps/place/Highpoint,+North+Carolina" rel="noreferrer" target="_blank">Highpoint</a> <a href="https://www.google.com/maps/place/Burlington,+North+Carolina" rel="noreferrer" target="_blank">Burlington</a> <a href="https://www.google.com/maps/place/Lexington,+North+Carolina" rel="noreferrer" target="_blank">Lexington</a> <a href="https://www.google.com/maps/place/Asheboro,+North+Carolina" rel="noreferrer" target="_blank">Asheboro</a> <a href="https://www.google.com/maps/place/Reidsville,+North+Carolina" rel="noreferrer" target="_blank">Reidsville</a>'),
        '337': ('CT', 'US', 'Louisiana', '<a href="https://www.google.com/maps/place/Lake+Charles,+Louisiana" rel="noreferrer" target="_blank">Lake Charles</a> <a href="https://www.google.com/maps/place/Lafayette,+Louisiana" rel="noreferrer" target="_blank">Lafayette</a> <a href="https://www.google.com/maps/place/New+Iberia,+Louisiana" rel="noreferrer" target="_blank">New Iberia</a> <a href="https://www.google.com/maps/place/Leesville,+Louisiana" rel="noreferrer" target="_blank">Leesville</a> <a href="https://www.google.com/maps/place/Opelousas,+Louisiana" rel="noreferrer" target="_blank">Opelousas</a> <a href="https://www.google.com/maps/place/Crowley,+Louisiana" rel="noreferrer" target="_blank">Crowley</a>'),
        '339': ('ET', 'US', 'Massachusetts', '<a href="https://www.google.com/maps/place/Waltham,+Massachusetts" rel="noreferrer" target="_blank">Waltham</a> <a href="https://www.google.com/maps/place/Lexington,+Massachusetts" rel="noreferrer" target="_blank">Lexington</a> <a href="https://www.google.com/maps/place/Burlinton,+Massachusetts" rel="noreferrer" target="_blank">Burlinton</a> <a href="https://www.google.com/maps/place/Dedham,+Massachusetts" rel="noreferrer" target="_blank">Dedham</a> <a href="https://www.google.com/maps/place/Woburn,+Massachusetts" rel="noreferrer" target="_blank">Woburn</a> <a href="https://www.google.com/maps/place/Lynn,+Massachusetts" rel="noreferrer" target="_blank">Lynn</a> <a href="https://www.google.com/maps/place/Malden,+Massachusetts" rel="noreferrer" target="_blank">Malden</a> <a href="https://www.google.com/maps/place/Saugus,+Massachusetts" rel="noreferrer" target="_blank">Saugus</a> <a href="https://www.google.com/maps/place/Reading,+Massachusetts" rel="noreferrer" target="_blank">Reading</a> <a href="https://www.google.com/maps/place/Braintree,+Massachusetts" rel="noreferrer" target="_blank">Braintree</a> <a href="https://www.google.com/maps/place/Wellesley,+Massachusetts" rel="noreferrer" target="_blank">Wellesley</a>'),
        '340': ('AT', 'US Virgin Islands', '', '<a href="https://www.google.com/maps/place/" rel="noreferrer" target="_blank">All areas</a>'),
        '343': ('ET', 'Ca', 'Ontario', '<a href="https://www.google.com/maps/place/Ottawa+metropolitan+area+and+southeastern+Ontario,+Ontario" rel="noreferrer" target="_blank">Ottawa metropolitan area and southeastern Ontario</a>'),
        '346': ('CT', 'US', 'Texas', '<a href="https://www.google.com/maps/place/Harris,+Texas" rel="noreferrer" target="_blank">Harris</a> <a href="https://www.google.com/maps/place/Fort+Bend,+Texas" rel="noreferrer" target="_blank">Fort Bend</a> <a href="https://www.google.com/maps/place/Waller,+Texas" rel="noreferrer" target="_blank">Waller</a> <a href="https://www.google.com/maps/place/Austin,+Texas" rel="noreferrer" target="_blank">Austin</a> <a href="https://www.google.com/maps/place/Montgomery,+Texas" rel="noreferrer" target="_blank">Montgomery</a> <a href="https://www.google.com/maps/place/San+Jacinto,+Texas" rel="noreferrer" target="_blank">San Jacinto</a> <a href="https://www.google.com/maps/place/Liberty,+Texas" rel="noreferrer" target="_blank">Liberty</a> <a href="https://www.google.com/maps/place/Chambers,+Texas" rel="noreferrer" target="_blank">Chambers</a> <a href="https://www.google.com/maps/place/Galveston+and+Brazoria+counties,+Texas" rel="noreferrer" target="_blank">Galveston and Brazoria counties</a>'),
        '347': ('ET', 'US', 'New York', '<a href="https://www.google.com/maps/place/Bronx,+New+York" rel="noreferrer" target="_blank">Bronx</a> <a href="https://www.google.com/maps/place/Brooklyn,+New+York" rel="noreferrer" target="_blank">Brooklyn</a> <a href="https://www.google.com/maps/place/Queens,+New+York" rel="noreferrer" target="_blank">Queens</a> <a href="https://www.google.com/maps/place/Staten+Island,+New+York" rel="noreferrer" target="_blank">Staten Island</a>'),
        '351': ('ET', 'US', 'Massachusetts', '<a href="https://www.google.com/maps/place/Lowell,+Massachusetts" rel="noreferrer" target="_blank">Lowell</a> <a href="https://www.google.com/maps/place/Lawrence,+Massachusetts" rel="noreferrer" target="_blank">Lawrence</a> <a href="https://www.google.com/maps/place/Billerica,+Massachusetts" rel="noreferrer" target="_blank">Billerica</a> <a href="https://www.google.com/maps/place/Concord,+Massachusetts" rel="noreferrer" target="_blank">Concord</a> <a href="https://www.google.com/maps/place/Wilmington,+Massachusetts" rel="noreferrer" target="_blank">Wilmington</a> <a href="https://www.google.com/maps/place/Sudbury,+Massachusetts" rel="noreferrer" target="_blank">Sudbury</a> <a href="https://www.google.com/maps/place/Fitchburg,+Massachusetts" rel="noreferrer" target="_blank">Fitchburg</a> <a href="https://www.google.com/maps/place/Peabody,+Massachusetts" rel="noreferrer" target="_blank">Peabody</a> <a href="https://www.google.com/maps/place/Andover,+Massachusetts" rel="noreferrer" target="_blank">Andover</a> <a href="https://www.google.com/maps/place/Beverly,+Massachusetts" rel="noreferrer" target="_blank">Beverly</a> <a href="https://www.google.com/maps/place/Danvers,+Massachusetts" rel="noreferrer" target="_blank">Danvers</a>'),
        '352': ('ET', 'US', 'Florida', '<a href="https://www.google.com/maps/place/Gainesville,+Florida" rel="noreferrer" target="_blank">Gainesville</a> <a href="https://www.google.com/maps/place/Ocala,+Florida" rel="noreferrer" target="_blank">Ocala</a> <a href="https://www.google.com/maps/place/Leesburg,+Florida" rel="noreferrer" target="_blank">Leesburg</a> <a href="https://www.google.com/maps/place/Brookville,+Florida" rel="noreferrer" target="_blank">Brookville</a>'),
        '360': ('PT', 'US', 'Washington', '<a href="https://www.google.com/maps/place/Vancouver,+Washington" rel="noreferrer" target="_blank">Vancouver</a> <a href="https://www.google.com/maps/place/Olympia,+Washington" rel="noreferrer" target="_blank">Olympia</a> <a href="https://www.google.com/maps/place/Bellingham,+Washington" rel="noreferrer" target="_blank">Bellingham</a> <a href="https://www.google.com/maps/place/Silverdale,+Washington" rel="noreferrer" target="_blank">Silverdale</a>'),
        '361': ('CT', 'US', 'Texas', '<a href="https://www.google.com/maps/place/Corpus+Christi,+Texas" rel="noreferrer" target="_blank">Corpus Christi</a> <a href="https://www.google.com/maps/place/Victoria,+Texas" rel="noreferrer" target="_blank">Victoria</a>'),
        '364': ('*ET, CT', 'US', 'Kentucky', '<a href="https://www.google.com/maps/place/Owensboro,+Kentucky" rel="noreferrer" target="_blank">Owensboro</a> <a href="https://www.google.com/maps/place/Paducah,+Kentucky" rel="noreferrer" target="_blank">Paducah</a> <a href="https://www.google.com/maps/place/Bowling+Green,+Kentucky" rel="noreferrer" target="_blank">Bowling Green</a> <a href="https://www.google.com/maps/place/Hopkinsville,+Kentucky" rel="noreferrer" target="_blank">Hopkinsville</a> <a href="https://www.google.com/maps/place/Henderson,+Kentucky" rel="noreferrer" target="_blank">Henderson</a> <a href="https://www.google.com/maps/place/Elizabethtown,+Kentucky" rel="noreferrer" target="_blank">Elizabethtown</a> <a href="https://www.google.com/maps/place/and+most+of+western+Kentucky,+Kentucky" rel="noreferrer" target="_blank">and most of western Kentucky</a>'),
        '365': ('ET', 'Ca', 'Ontario', '<a href="https://www.google.com/maps/place/Niagara+Falls+Region,+Ontario" rel="noreferrer" target="_blank">Niagara Falls Region</a> <a href="https://www.google.com/maps/place/Hamilton,+Ontario" rel="noreferrer" target="_blank">Hamilton</a> <a href="https://www.google.com/maps/place/St.+Catharines,+Ontario" rel="noreferrer" target="_blank">St. Catharines</a> <a href="https://www.google.com/maps/place/suburbs+of+the+Greater+Toronto+Area,+Ontario" rel="noreferrer" target="_blank">suburbs of the Greater Toronto Area</a> <a href="https://www.google.com/maps/place/and+southeastern+Ontario,+Ontario" rel="noreferrer" target="_blank">and southeastern Ontario</a>'),
        '385': ('MT', 'US', 'Utah', '<a href="https://www.google.com/maps/place/Salt+Lake+City,+Utah" rel="noreferrer" target="_blank">Salt Lake City</a> <a href="https://www.google.com/maps/place/Provo,+Utah" rel="noreferrer" target="_blank">Provo</a> <a href="https://www.google.com/maps/place/Ogden,+Utah" rel="noreferrer" target="_blank">Ogden</a> <a href="https://www.google.com/maps/place/Orem,+Utah" rel="noreferrer" target="_blank">Orem</a> <a href="https://www.google.com/maps/place/American+Fork,+Utah" rel="noreferrer" target="_blank">American Fork</a> <a href="https://www.google.com/maps/place/Spanish+Fork,+Utah" rel="noreferrer" target="_blank">Spanish Fork</a> <a href="https://www.google.com/maps/place/Bountiful,+Utah" rel="noreferrer" target="_blank">Bountiful</a> <a href="https://www.google.com/maps/place/Kaysville,+Utah" rel="noreferrer" target="_blank">Kaysville</a> <a href="https://www.google.com/maps/place/Morgan,+Utah" rel="noreferrer" target="_blank">Morgan</a>'),
        '386': ('ET', 'US', 'Florida', '<a href="https://www.google.com/maps/place/Daytona,+Florida" rel="noreferrer" target="_blank">Daytona</a> <a href="https://www.google.com/maps/place/Deland,+Florida" rel="noreferrer" target="_blank">Deland</a> <a href="https://www.google.com/maps/place/Lake+City,+Florida" rel="noreferrer" target="_blank">Lake City</a> <a href="https://www.google.com/maps/place/DeBary,+Florida" rel="noreferrer" target="_blank">DeBary</a> <a href="https://www.google.com/maps/place/Orange+City,+Florida" rel="noreferrer" target="_blank">Orange City</a> <a href="https://www.google.com/maps/place/New+Smyrna+Beach,+Florida" rel="noreferrer" target="_blank">New Smyrna Beach</a> <a href="https://www.google.com/maps/place/Palatka,+Florida" rel="noreferrer" target="_blank">Palatka</a> <a href="https://www.google.com/maps/place/Palm+Coast,+Florida" rel="noreferrer" target="_blank">Palm Coast</a>'),
        '401': ('ET', 'US', 'Rhode Island', '<a href="https://www.google.com/maps/place/Rhode+Island" rel="noreferrer" target="_blank">All areas</a>'),
        '402': ('CT', 'US', 'Nebraska', '<a href="https://www.google.com/maps/place/Lincoln,+Nebraska" rel="noreferrer" target="_blank">Lincoln</a> <a href="https://www.google.com/maps/place/Omaha,+Nebraska" rel="noreferrer" target="_blank">Omaha</a> <a href="https://www.google.com/maps/place/Norfolk,+Nebraska" rel="noreferrer" target="_blank">Norfolk</a> <a href="https://www.google.com/maps/place/Columbus,+Nebraska" rel="noreferrer" target="_blank">Columbus</a>'),
        '403': ('MT', 'Ca', 'Alberta', '<a href="https://www.google.com/maps/place/Calgary,+Alberta" rel="noreferrer" target="_blank">Calgary</a> <a href="https://www.google.com/maps/place/Lethbridge,+Alberta" rel="noreferrer" target="_blank">Lethbridge</a> <a href="https://www.google.com/maps/place/Banff,+Alberta" rel="noreferrer" target="_blank">Banff</a> <a href="https://www.google.com/maps/place/Medicine+Hat,+Alberta" rel="noreferrer" target="_blank">Medicine Hat</a> <a href="https://www.google.com/maps/place/Red+Deer,+Alberta" rel="noreferrer" target="_blank">Red Deer</a>'),
        '404': ('ET', 'US', 'Georgia', '<a href="https://www.google.com/maps/place/Atlanta,+Georgia" rel="noreferrer" target="_blank">Atlanta</a>'),
        '405': ('CT', 'US', 'Oklahoma', '<a href="https://www.google.com/maps/place/Oklahoma+City,+Oklahoma" rel="noreferrer" target="_blank">Oklahoma City</a> <a href="https://www.google.com/maps/place/Norman,+Oklahoma" rel="noreferrer" target="_blank">Norman</a> <a href="https://www.google.com/maps/place/Stillwater,+Oklahoma" rel="noreferrer" target="_blank">Stillwater</a> <a href="https://www.google.com/maps/place/Britton,+Oklahoma" rel="noreferrer" target="_blank">Britton</a> <a href="https://www.google.com/maps/place/Bethany,+Oklahoma" rel="noreferrer" target="_blank">Bethany</a> <a href="https://www.google.com/maps/place/Moore,+Oklahoma" rel="noreferrer" target="_blank">Moore</a>'),
        '406': ('MT', 'US', 'Montana', '<a href="https://www.google.com/maps/place/Montana" rel="noreferrer" target="_blank">All areas</a>'),
        '407': ('ET', 'US', 'Florida', '<a href="https://www.google.com/maps/place/Orlando,+Florida" rel="noreferrer" target="_blank">Orlando</a> <a href="https://www.google.com/maps/place/Winter+Park,+Florida" rel="noreferrer" target="_blank">Winter Park</a> <a href="https://www.google.com/maps/place/Kissimmee,+Florida" rel="noreferrer" target="_blank">Kissimmee</a> <a href="https://www.google.com/maps/place/Cocoa,+Florida" rel="noreferrer" target="_blank">Cocoa</a> <a href="https://www.google.com/maps/place/Lake+Buena+Vista,+Florida" rel="noreferrer" target="_blank">Lake Buena Vista</a> <a href="https://www.google.com/maps/place/Melbourne,+Florida" rel="noreferrer" target="_blank">Melbourne</a>'),
        '408': ('PT', 'US', 'California', '<a href="https://www.google.com/maps/place/San+Jose,+California" rel="noreferrer" target="_blank">San Jose</a> <a href="https://www.google.com/maps/place/Sunnyvale,+California" rel="noreferrer" target="_blank">Sunnyvale</a> <a href="https://www.google.com/maps/place/Campbell+Los+Gatos,+California" rel="noreferrer" target="_blank">Campbell Los Gatos</a> <a href="https://www.google.com/maps/place/Salinas,+California" rel="noreferrer" target="_blank">Salinas</a> <a href="https://www.google.com/maps/place/San+Martin,+California" rel="noreferrer" target="_blank">San Martin</a> <a href="https://www.google.com/maps/place/Saratoga,+California" rel="noreferrer" target="_blank">Saratoga</a> <a href="https://www.google.com/maps/place/Morgan+Hill,+California" rel="noreferrer" target="_blank">Morgan Hill</a> <a href="https://www.google.com/maps/place/Gilroy,+California" rel="noreferrer" target="_blank">Gilroy</a>'),
        '409': ('CT', 'US', 'Texas', '<a href="https://www.google.com/maps/place/Galveston,+Texas" rel="noreferrer" target="_blank">Galveston</a> <a href="https://www.google.com/maps/place/Beaumont,+Texas" rel="noreferrer" target="_blank">Beaumont</a> <a href="https://www.google.com/maps/place/Port+Arthur,+Texas" rel="noreferrer" target="_blank">Port Arthur</a> <a href="https://www.google.com/maps/place/Texas+City,+Texas" rel="noreferrer" target="_blank">Texas City</a> <a href="https://www.google.com/maps/place/Nederland,+Texas" rel="noreferrer" target="_blank">Nederland</a>'),
        '410': ('ET', 'US', 'Maryland', '<a href="https://www.google.com/maps/place/Baltimore,+Maryland" rel="noreferrer" target="_blank">Baltimore</a> <a href="https://www.google.com/maps/place/Annapolis,+Maryland" rel="noreferrer" target="_blank">Annapolis</a> <a href="https://www.google.com/maps/place/Towson,+Maryland" rel="noreferrer" target="_blank">Towson</a> <a href="https://www.google.com/maps/place/Catonsville,+Maryland" rel="noreferrer" target="_blank">Catonsville</a> <a href="https://www.google.com/maps/place/Glen+Burnie,+Maryland" rel="noreferrer" target="_blank">Glen Burnie</a>'),
        '412': ('ET', 'US', 'Pennsylvania', '<a href="https://www.google.com/maps/place/Pittsburgh,+Pennsylvania" rel="noreferrer" target="_blank">Pittsburgh</a>'),
        '413': ('ET', 'US', 'Massachusetts', '<a href="https://www.google.com/maps/place/Springfield,+Massachusetts" rel="noreferrer" target="_blank">Springfield</a> <a href="https://www.google.com/maps/place/Pittsfield,+Massachusetts" rel="noreferrer" target="_blank">Pittsfield</a> <a href="https://www.google.com/maps/place/Holyoke,+Massachusetts" rel="noreferrer" target="_blank">Holyoke</a> <a href="https://www.google.com/maps/place/Amherst,+Massachusetts" rel="noreferrer" target="_blank">Amherst</a>'),
        '414': ('CT', 'US', 'Wisconsin', '<a href="https://www.google.com/maps/place/Milwaukee,+Wisconsin" rel="noreferrer" target="_blank">Milwaukee</a> <a href="https://www.google.com/maps/place/Greendale,+Wisconsin" rel="noreferrer" target="_blank">Greendale</a> <a href="https://www.google.com/maps/place/Franklin,+Wisconsin" rel="noreferrer" target="_blank">Franklin</a> <a href="https://www.google.com/maps/place/Cudahy,+Wisconsin" rel="noreferrer" target="_blank">Cudahy</a> <a href="https://www.google.com/maps/place/St.+Francis,+Wisconsin" rel="noreferrer" target="_blank">St. Francis</a> <a href="https://www.google.com/maps/place/Brown+Deer,+Wisconsin" rel="noreferrer" target="_blank">Brown Deer</a> <a href="https://www.google.com/maps/place/Whitefish+Bay,+Wisconsin" rel="noreferrer" target="_blank">Whitefish Bay</a>'),
        '415': ('PT', 'US', 'California', '<a href="https://www.google.com/maps/place/San+Francisco,+California" rel="noreferrer" target="_blank">San Francisco</a>'),
        '416': ('ET', 'Ca', 'Ontario', '<a href="https://www.google.com/maps/place/Toronto,+Ontario" rel="noreferrer" target="_blank">Toronto</a>'),
        '417': ('CT', 'US', 'Missouri', '<a href="https://www.google.com/maps/place/Joplin,+Missouri" rel="noreferrer" target="_blank">Joplin</a> <a href="https://www.google.com/maps/place/Springfield,+Missouri" rel="noreferrer" target="_blank">Springfield</a> <a href="https://www.google.com/maps/place/Branson,+Missouri" rel="noreferrer" target="_blank">Branson</a> <a href="https://www.google.com/maps/place/Lebanon,+Missouri" rel="noreferrer" target="_blank">Lebanon</a>'),
        '418': ('ET', 'Ca', 'Quebec', '<a href="https://www.google.com/maps/place/Quebec,+Quebec" rel="noreferrer" target="_blank">Quebec</a>'),
        '419': ('ET', 'US', 'Ohio', '<a href="https://www.google.com/maps/place/Toledo,+Ohio" rel="noreferrer" target="_blank">Toledo</a> <a href="https://www.google.com/maps/place/Lima,+Ohio" rel="noreferrer" target="_blank">Lima</a> <a href="https://www.google.com/maps/place/Mansfield,+Ohio" rel="noreferrer" target="_blank">Mansfield</a> <a href="https://www.google.com/maps/place/Sandusky,+Ohio" rel="noreferrer" target="_blank">Sandusky</a> <a href="https://www.google.com/maps/place/Findlay,+Ohio" rel="noreferrer" target="_blank">Findlay</a>'),
        '423': ('*EST, CST', 'US', 'Tennessee', '<a href="https://www.google.com/maps/place/Chattanooga,+Tennessee" rel="noreferrer" target="_blank">Chattanooga</a> <a href="https://www.google.com/maps/place/Cleveland,+Tennessee" rel="noreferrer" target="_blank">Cleveland</a> <a href="https://www.google.com/maps/place/Johnson+City,+Tennessee" rel="noreferrer" target="_blank">Johnson City</a> <a href="https://www.google.com/maps/place/Bristol,+Tennessee" rel="noreferrer" target="_blank">Bristol</a> <a href="https://www.google.com/maps/place/Kingsport,+Tennessee" rel="noreferrer" target="_blank">Kingsport</a> <a href="https://www.google.com/maps/place/Athens,+Tennessee" rel="noreferrer" target="_blank">Athens</a> <a href="https://www.google.com/maps/place/Morristown,+Tennessee" rel="noreferrer" target="_blank">Morristown</a> <a href="https://www.google.com/maps/place/Greeneville,+Tennessee" rel="noreferrer" target="_blank">Greeneville</a>'),
        '424': ('PT', 'US', 'California', '<a href="https://www.google.com/maps/place/Compton,+California" rel="noreferrer" target="_blank">Compton</a> <a href="https://www.google.com/maps/place/Santa+Monica,+California" rel="noreferrer" target="_blank">Santa Monica</a> <a href="https://www.google.com/maps/place/Beverly+Hills,+California" rel="noreferrer" target="_blank">Beverly Hills</a> <a href="https://www.google.com/maps/place/West+LA,+California" rel="noreferrer" target="_blank">West LA</a> <a href="https://www.google.com/maps/place/Inglewood,+California" rel="noreferrer" target="_blank">Inglewood</a> <a href="https://www.google.com/maps/place/Redondo,+California" rel="noreferrer" target="_blank">Redondo</a> <a href="https://www.google.com/maps/place/El+Segundo,+California" rel="noreferrer" target="_blank">El Segundo</a> <a href="https://www.google.com/maps/place/Culver+City,+California" rel="noreferrer" target="_blank">Culver City</a> <a href="https://www.google.com/maps/place/Torrance,+California" rel="noreferrer" target="_blank">Torrance</a>'),
        '425': ('PT', 'US', 'Washington', '<a href="https://www.google.com/maps/place/Bothell,+Washington" rel="noreferrer" target="_blank">Bothell</a> <a href="https://www.google.com/maps/place/Everett,+Washington" rel="noreferrer" target="_blank">Everett</a> <a href="https://www.google.com/maps/place/Bellevue,+Washington" rel="noreferrer" target="_blank">Bellevue</a> <a href="https://www.google.com/maps/place/Kirkland,+Washington" rel="noreferrer" target="_blank">Kirkland</a> <a href="https://www.google.com/maps/place/Renton,+Washington" rel="noreferrer" target="_blank">Renton</a>'),
        '430': ('CT', 'US', 'Texas', '<a href="https://www.google.com/maps/place/Longview,+Texas" rel="noreferrer" target="_blank">Longview</a> <a href="https://www.google.com/maps/place/Tyler,+Texas" rel="noreferrer" target="_blank">Tyler</a> <a href="https://www.google.com/maps/place/Texarkana,+Texas" rel="noreferrer" target="_blank">Texarkana</a> <a href="https://www.google.com/maps/place/Paris,+Texas" rel="noreferrer" target="_blank">Paris</a> <a href="https://www.google.com/maps/place/Kilgore,+Texas" rel="noreferrer" target="_blank">Kilgore</a> <a href="https://www.google.com/maps/place/Sherman,+Texas" rel="noreferrer" target="_blank">Sherman</a> <a href="https://www.google.com/maps/place/Denison,+Texas" rel="noreferrer" target="_blank">Denison</a>'),
        '431': ('', 'Ca', 'Manitoba', '<a href="https://www.google.com/maps/place/Manitoba" rel="noreferrer" target="_blank">All areas</a>'),
        '432': ('CT', 'US', 'Texas', '<a href="https://www.google.com/maps/place/Midland,+Texas" rel="noreferrer" target="_blank">Midland</a> <a href="https://www.google.com/maps/place/Terminal,+Texas" rel="noreferrer" target="_blank">Terminal</a> <a href="https://www.google.com/maps/place/Odessa,+Texas" rel="noreferrer" target="_blank">Odessa</a> <a href="https://www.google.com/maps/place/Big+Spring,+Texas" rel="noreferrer" target="_blank">Big Spring</a> <a href="https://www.google.com/maps/place/Alpine,+Texas" rel="noreferrer" target="_blank">Alpine</a> <a href="https://www.google.com/maps/place/Pecos,+Texas" rel="noreferrer" target="_blank">Pecos</a> <a href="https://www.google.com/maps/place/Fort+Stockton,+Texas" rel="noreferrer" target="_blank">Fort Stockton</a>'),
        '434': ('ET', 'US', 'Virginia', '<a href="https://www.google.com/maps/place/Lynchburg,+Virginia" rel="noreferrer" target="_blank">Lynchburg</a> <a href="https://www.google.com/maps/place/Danville,+Virginia" rel="noreferrer" target="_blank">Danville</a> <a href="https://www.google.com/maps/place/Charlottesville,+Virginia" rel="noreferrer" target="_blank">Charlottesville</a> <a href="https://www.google.com/maps/place/Madison+Heights,+Virginia" rel="noreferrer" target="_blank">Madison Heights</a> <a href="https://www.google.com/maps/place/South+Boston,+Virginia" rel="noreferrer" target="_blank">South Boston</a>'),
        '435': ('MT', 'US', 'Utah', '<a href="https://www.google.com/maps/place/Logan,+Utah" rel="noreferrer" target="_blank">Logan</a> <a href="https://www.google.com/maps/place/St.+George,+Utah" rel="noreferrer" target="_blank">St. George</a> <a href="https://www.google.com/maps/place/Park+City,+Utah" rel="noreferrer" target="_blank">Park City</a> <a href="https://www.google.com/maps/place/Tooele,+Utah" rel="noreferrer" target="_blank">Tooele</a> <a href="https://www.google.com/maps/place/Brigham+City,+Utah" rel="noreferrer" target="_blank">Brigham City</a> <a href="https://www.google.com/maps/place/Richfield,+Utah" rel="noreferrer" target="_blank">Richfield</a> <a href="https://www.google.com/maps/place/Moab,+Utah" rel="noreferrer" target="_blank">Moab</a> <a href="https://www.google.com/maps/place/Blanding,+Utah" rel="noreferrer" target="_blank">Blanding</a>'),
        '437': ('ET', 'Ca', 'Ontario', '<a href="https://www.google.com/maps/place/Toronto+metropolitan+area,+Ontario" rel="noreferrer" target="_blank">Toronto metropolitan area</a>'),
        '438': ('ET', 'Ca', 'Quebec', '<a href="https://www.google.com/maps/place/Montreal+Area,+Quebec" rel="noreferrer" target="_blank">Montreal Area</a>'),
        '440': ('ET', 'US', 'Ohio', '<a href="https://www.google.com/maps/place/Willoughby,+Ohio" rel="noreferrer" target="_blank">Willoughby</a> <a href="https://www.google.com/maps/place/Hillcrest,+Ohio" rel="noreferrer" target="_blank">Hillcrest</a> <a href="https://www.google.com/maps/place/Trinity,+Ohio" rel="noreferrer" target="_blank">Trinity</a> <a href="https://www.google.com/maps/place/Lorain,+Ohio" rel="noreferrer" target="_blank">Lorain</a> <a href="https://www.google.com/maps/place/Elyria,+Ohio" rel="noreferrer" target="_blank">Elyria</a>'),
        '442': ('PT', 'US', 'California', '<a href="https://www.google.com/maps/place/Oceanside,+California" rel="noreferrer" target="_blank">Oceanside</a> <a href="https://www.google.com/maps/place/Palm+Springs,+California" rel="noreferrer" target="_blank">Palm Springs</a> <a href="https://www.google.com/maps/place/Victorville,+California" rel="noreferrer" target="_blank">Victorville</a> <a href="https://www.google.com/maps/place/Escondido,+California" rel="noreferrer" target="_blank">Escondido</a> <a href="https://www.google.com/maps/place/Vista,+California" rel="noreferrer" target="_blank">Vista</a> <a href="https://www.google.com/maps/place/Palm+Desert,+California" rel="noreferrer" target="_blank">Palm Desert</a>'),
        '443': ('ET', 'US', 'Maryland', '<a href="https://www.google.com/maps/place/Baltimore,+Maryland" rel="noreferrer" target="_blank">Baltimore</a> <a href="https://www.google.com/maps/place/Annapolis,+Maryland" rel="noreferrer" target="_blank">Annapolis</a> <a href="https://www.google.com/maps/place/Towson,+Maryland" rel="noreferrer" target="_blank">Towson</a> <a href="https://www.google.com/maps/place/Catonsville,+Maryland" rel="noreferrer" target="_blank">Catonsville</a> <a href="https://www.google.com/maps/place/Glen+Burnie,+Maryland" rel="noreferrer" target="_blank">Glen Burnie</a>'),
        '450': ('ET', 'Ca', 'Quebec', '<a href="https://www.google.com/maps/place/Quebec:+Laval,+Quebec" rel="noreferrer" target="_blank">Quebec: Laval</a> <a href="https://www.google.com/maps/place/Saint+Lambert,+Quebec" rel="noreferrer" target="_blank">Saint Lambert</a> <a href="https://www.google.com/maps/place/Longueuil,+Quebec" rel="noreferrer" target="_blank">Longueuil</a> <a href="https://www.google.com/maps/place/Sainte+Therese,+Quebec" rel="noreferrer" target="_blank">Sainte Therese</a>'),
        '458': ('MT, PT', 'US', 'Oregon', '<a href="https://www.google.com/maps/place/Eugene,+Oregon" rel="noreferrer" target="_blank">Eugene</a> <a href="https://www.google.com/maps/place/Medford,+Oregon" rel="noreferrer" target="_blank">Medford</a> <a href="https://www.google.com/maps/place/Bend,+Oregon" rel="noreferrer" target="_blank">Bend</a> <a href="https://www.google.com/maps/place/Pendleton,+Oregon" rel="noreferrer" target="_blank">Pendleton</a> <a href="https://www.google.com/maps/place/Corvallis,+Oregon" rel="noreferrer" target="_blank">Corvallis</a> <a href="https://www.google.com/maps/place/Ontario,+Oregon" rel="noreferrer" target="_blank">Ontario</a> <a href="https://www.google.com/maps/place/Burns;+excludes+the+Portland+metropolitan+area,+Oregon" rel="noreferrer" target="_blank">Burns; excludes the Portland metropolitan area</a>'),
        '469': ('CT', 'US', 'Texas', '<a href="https://www.google.com/maps/place/Dallas,+Texas" rel="noreferrer" target="_blank">Dallas</a> <a href="https://www.google.com/maps/place/Grand+Prairie,+Texas" rel="noreferrer" target="_blank">Grand Prairie</a> <a href="https://www.google.com/maps/place/Addison,+Texas" rel="noreferrer" target="_blank">Addison</a> <a href="https://www.google.com/maps/place/Irving,+Texas" rel="noreferrer" target="_blank">Irving</a> <a href="https://www.google.com/maps/place/Richardson,+Texas" rel="noreferrer" target="_blank">Richardson</a> <a href="https://www.google.com/maps/place/Plano,+Texas" rel="noreferrer" target="_blank">Plano</a> <a href="https://www.google.com/maps/place/Carrollton,+Texas" rel="noreferrer" target="_blank">Carrollton</a>'),
        '470': ('ET', 'US', 'Georgia', '<a href="https://www.google.com/maps/place/Atlanta,+Georgia" rel="noreferrer" target="_blank">Atlanta</a> <a href="https://www.google.com/maps/place/Norcross,+Georgia" rel="noreferrer" target="_blank">Norcross</a> <a href="https://www.google.com/maps/place/Chamblee,+Georgia" rel="noreferrer" target="_blank">Chamblee</a> <a href="https://www.google.com/maps/place/Smyrna,+Georgia" rel="noreferrer" target="_blank">Smyrna</a> <a href="https://www.google.com/maps/place/Tucker,+Georgia" rel="noreferrer" target="_blank">Tucker</a> <a href="https://www.google.com/maps/place/Marietta,+Georgia" rel="noreferrer" target="_blank">Marietta</a> <a href="https://www.google.com/maps/place/Alpharetta,+Georgia" rel="noreferrer" target="_blank">Alpharetta</a> <a href="https://www.google.com/maps/place/Gainesville,+Georgia" rel="noreferrer" target="_blank">Gainesville</a>'),
        '475': ('ET', 'US', 'Connecticut', '<a href="https://www.google.com/maps/place/Bridgeport,+Connecticut" rel="noreferrer" target="_blank">Bridgeport</a> <a href="https://www.google.com/maps/place/New+Haven,+Connecticut" rel="noreferrer" target="_blank">New Haven</a> <a href="https://www.google.com/maps/place/Stamford,+Connecticut" rel="noreferrer" target="_blank">Stamford</a> <a href="https://www.google.com/maps/place/Waterbury,+Connecticut" rel="noreferrer" target="_blank">Waterbury</a> <a href="https://www.google.com/maps/place/Norwalk,+Connecticut" rel="noreferrer" target="_blank">Norwalk</a> <a href="https://www.google.com/maps/place/Danbury,+Connecticut" rel="noreferrer" target="_blank">Danbury</a> <a href="https://www.google.com/maps/place/Greenwich,+Connecticut" rel="noreferrer" target="_blank">Greenwich</a>'),
        '478': ('ET', 'US', 'Georgia', '<a href="https://www.google.com/maps/place/Macon,+Georgia" rel="noreferrer" target="_blank">Macon</a> <a href="https://www.google.com/maps/place/Warner+Robbins,+Georgia" rel="noreferrer" target="_blank">Warner Robbins</a> <a href="https://www.google.com/maps/place/Dublin,+Georgia" rel="noreferrer" target="_blank">Dublin</a> <a href="https://www.google.com/maps/place/Milledgeville,+Georgia" rel="noreferrer" target="_blank">Milledgeville</a> <a href="https://www.google.com/maps/place/Forsyth,+Georgia" rel="noreferrer" target="_blank">Forsyth</a>'),
        '479': ('CT', 'US', 'Arkansas', '<a href="https://www.google.com/maps/place/Fort+Smith,+Arkansas" rel="noreferrer" target="_blank">Fort Smith</a> <a href="https://www.google.com/maps/place/Fayetteville,+Arkansas" rel="noreferrer" target="_blank">Fayetteville</a> <a href="https://www.google.com/maps/place/Rogers,+Arkansas" rel="noreferrer" target="_blank">Rogers</a> <a href="https://www.google.com/maps/place/Bentonville,+Arkansas" rel="noreferrer" target="_blank">Bentonville</a> <a href="https://www.google.com/maps/place/Russellville,+Arkansas" rel="noreferrer" target="_blank">Russellville</a>'),
        '480': ('MT', 'US', 'Arizona', '<a href="https://www.google.com/maps/place/Mesa,+Arizona" rel="noreferrer" target="_blank">Mesa</a> <a href="https://www.google.com/maps/place/Scottsdale,+Arizona" rel="noreferrer" target="_blank">Scottsdale</a> <a href="https://www.google.com/maps/place/Tempe,+Arizona" rel="noreferrer" target="_blank">Tempe</a> <a href="https://www.google.com/maps/place/Chandler,+Arizona" rel="noreferrer" target="_blank">Chandler</a> <a href="https://www.google.com/maps/place/Gilbert,+Arizona" rel="noreferrer" target="_blank">Gilbert</a>'),
        '484': ('ET', 'US', 'Pennsylvania', '<a href="https://www.google.com/maps/place/Allentown,+Pennsylvania" rel="noreferrer" target="_blank">Allentown</a> <a href="https://www.google.com/maps/place/Reading,+Pennsylvania" rel="noreferrer" target="_blank">Reading</a> <a href="https://www.google.com/maps/place/Bethlehem,+Pennsylvania" rel="noreferrer" target="_blank">Bethlehem</a> <a href="https://www.google.com/maps/place/West+Chester,+Pennsylvania" rel="noreferrer" target="_blank">West Chester</a> <a href="https://www.google.com/maps/place/Pottstown,+Pennsylvania" rel="noreferrer" target="_blank">Pottstown</a>'),
        '501': ('CT', 'US', 'Arkansas', '<a href="https://www.google.com/maps/place/Little+Rock,+Arkansas" rel="noreferrer" target="_blank">Little Rock</a> <a href="https://www.google.com/maps/place/Hot+Springs,+Arkansas" rel="noreferrer" target="_blank">Hot Springs</a>'),
        '502': ('ET', 'US', 'Kentucky', '<a href="https://www.google.com/maps/place/Louisville,+Kentucky" rel="noreferrer" target="_blank">Louisville</a> <a href="https://www.google.com/maps/place/Frankfort,+Kentucky" rel="noreferrer" target="_blank">Frankfort</a> <a href="https://www.google.com/maps/place/Fort+Knox,+Kentucky" rel="noreferrer" target="_blank">Fort Knox</a> <a href="https://www.google.com/maps/place/Pleasure+Ridge+Park,+Kentucky" rel="noreferrer" target="_blank">Pleasure Ridge Park</a>'),
        '503': ('PT', 'US', 'Oregon', '<a href="https://www.google.com/maps/place/Portland,+Oregon" rel="noreferrer" target="_blank">Portland</a> <a href="https://www.google.com/maps/place/Salem,+Oregon" rel="noreferrer" target="_blank">Salem</a> <a href="https://www.google.com/maps/place/Beaverton,+Oregon" rel="noreferrer" target="_blank">Beaverton</a> <a href="https://www.google.com/maps/place/Gresham,+Oregon" rel="noreferrer" target="_blank">Gresham</a> <a href="https://www.google.com/maps/place/Hillsboro,+Oregon" rel="noreferrer" target="_blank">Hillsboro</a>'),
        '504': ('CT', 'US', 'Louisiana', '<a href="https://www.google.com/maps/place/New+Orleans,+Louisiana" rel="noreferrer" target="_blank">New Orleans</a> <a href="https://www.google.com/maps/place/Metairie,+Louisiana" rel="noreferrer" target="_blank">Metairie</a> <a href="https://www.google.com/maps/place/Kenner,+Louisiana" rel="noreferrer" target="_blank">Kenner</a> <a href="https://www.google.com/maps/place/Chalmette,+Louisiana" rel="noreferrer" target="_blank">Chalmette</a>'),
        '505': ('MT', 'US', 'New Mexico', '<a href="https://www.google.com/maps/place/Albuquerque,+New+Mexico" rel="noreferrer" target="_blank">Albuquerque</a> <a href="https://www.google.com/maps/place/Bernalillo,+New+Mexico" rel="noreferrer" target="_blank">Bernalillo</a> <a href="https://www.google.com/maps/place/Farmington,+New+Mexico" rel="noreferrer" target="_blank">Farmington</a> <a href="https://www.google.com/maps/place/Gallup,+New+Mexico" rel="noreferrer" target="_blank">Gallup</a> <a href="https://www.google.com/maps/place/Grants,+New+Mexico" rel="noreferrer" target="_blank">Grants</a> <a href="https://www.google.com/maps/place/Las+Vegas,+New+Mexico" rel="noreferrer" target="_blank">Las Vegas</a> <a href="https://www.google.com/maps/place/Los+Alamos,+New+Mexico" rel="noreferrer" target="_blank">Los Alamos</a> <a href="https://www.google.com/maps/place/Rio+Rancho,+New+Mexico" rel="noreferrer" target="_blank">Rio Rancho</a> <a href="https://www.google.com/maps/place/Santa+Fe,+New+Mexico" rel="noreferrer" target="_blank">Santa Fe</a>'),
        '506': ('AT', 'Ca', 'New Brunswick', '<a href="https://www.google.com/maps/place/New+Brunswick" rel="noreferrer" target="_blank">All areas</a>'),
        '507': ('CT', 'US', 'Minnesota', '<a href="https://www.google.com/maps/place/Rochester,+Minnesota" rel="noreferrer" target="_blank">Rochester</a> <a href="https://www.google.com/maps/place/Mankato,+Minnesota" rel="noreferrer" target="_blank">Mankato</a> <a href="https://www.google.com/maps/place/Winona,+Minnesota" rel="noreferrer" target="_blank">Winona</a> <a href="https://www.google.com/maps/place/Faribault,+Minnesota" rel="noreferrer" target="_blank">Faribault</a> <a href="https://www.google.com/maps/place/Luverne,+Minnesota" rel="noreferrer" target="_blank">Luverne</a>'),
        '508': ('ET', 'US', 'Massachusetts', '<a href="https://www.google.com/maps/place/Worcester,+Massachusetts" rel="noreferrer" target="_blank">Worcester</a> <a href="https://www.google.com/maps/place/Framingham,+Massachusetts" rel="noreferrer" target="_blank">Framingham</a> <a href="https://www.google.com/maps/place/Brockton,+Massachusetts" rel="noreferrer" target="_blank">Brockton</a> <a href="https://www.google.com/maps/place/Plymouth,+Massachusetts" rel="noreferrer" target="_blank">Plymouth</a> <a href="https://www.google.com/maps/place/New+Bedford,+Massachusetts" rel="noreferrer" target="_blank">New Bedford</a> <a href="https://www.google.com/maps/place/Marlboro,+Massachusetts" rel="noreferrer" target="_blank">Marlboro</a> <a href="https://www.google.com/maps/place/Natick,+Massachusetts" rel="noreferrer" target="_blank">Natick</a> <a href="https://www.google.com/maps/place/Taunton,+Massachusetts" rel="noreferrer" target="_blank">Taunton</a> <a href="https://www.google.com/maps/place/Auburn,+Massachusetts" rel="noreferrer" target="_blank">Auburn</a> <a href="https://www.google.com/maps/place/Westboro,+Massachusetts" rel="noreferrer" target="_blank">Westboro</a> <a href="https://www.google.com/maps/place/Easton,+Massachusetts" rel="noreferrer" target="_blank">Easton</a>'),
        '509': ('PT', 'US', 'Washington', '<a href="https://www.google.com/maps/place/Spokane,+Washington" rel="noreferrer" target="_blank">Spokane</a> <a href="https://www.google.com/maps/place/Yakima,+Washington" rel="noreferrer" target="_blank">Yakima</a> <a href="https://www.google.com/maps/place/Walla+Walla,+Washington" rel="noreferrer" target="_blank">Walla Walla</a> <a href="https://www.google.com/maps/place/Pullman,+Washington" rel="noreferrer" target="_blank">Pullman</a> <a href="https://www.google.com/maps/place/Kenwick,+Washington" rel="noreferrer" target="_blank">Kenwick</a>'),
        '510': ('PT', 'US', 'California', '<a href="https://www.google.com/maps/place/Oakland,+California" rel="noreferrer" target="_blank">Oakland</a> <a href="https://www.google.com/maps/place/Fremont,+California" rel="noreferrer" target="_blank">Fremont</a> <a href="https://www.google.com/maps/place/Newark,+California" rel="noreferrer" target="_blank">Newark</a> <a href="https://www.google.com/maps/place/Hayward,+California" rel="noreferrer" target="_blank">Hayward</a> <a href="https://www.google.com/maps/place/Richmond,+California" rel="noreferrer" target="_blank">Richmond</a>'),
        '512': ('CT', 'US', 'Texas', '<a href="https://www.google.com/maps/place/Austin,+Texas" rel="noreferrer" target="_blank">Austin</a> <a href="https://www.google.com/maps/place/San+Marcos,+Texas" rel="noreferrer" target="_blank">San Marcos</a> <a href="https://www.google.com/maps/place/Round+Rock,+Texas" rel="noreferrer" target="_blank">Round Rock</a> <a href="https://www.google.com/maps/place/Dripping+Springs,+Texas" rel="noreferrer" target="_blank">Dripping Springs</a>'),
        '513': ('ET', 'US', 'Ohio', '<a href="https://www.google.com/maps/place/Cincinnati,+Ohio" rel="noreferrer" target="_blank">Cincinnati</a> <a href="https://www.google.com/maps/place/Hamilton,+Ohio" rel="noreferrer" target="_blank">Hamilton</a> <a href="https://www.google.com/maps/place/Clermont,+Ohio" rel="noreferrer" target="_blank">Clermont</a> <a href="https://www.google.com/maps/place/Middleton,+Ohio" rel="noreferrer" target="_blank">Middleton</a> <a href="https://www.google.com/maps/place/Mason,+Ohio" rel="noreferrer" target="_blank">Mason</a>'),
        '514': ('ET', 'Ca', 'Quebec', '<a href="https://www.google.com/maps/place/Montreal+Area,+Quebec" rel="noreferrer" target="_blank">Montreal Area</a>'),
        '515': ('CT', 'US', 'Iowa', '<a href="https://www.google.com/maps/place/Des+Moines,+Iowa" rel="noreferrer" target="_blank">Des Moines</a> <a href="https://www.google.com/maps/place/Ames,+Iowa" rel="noreferrer" target="_blank">Ames</a> <a href="https://www.google.com/maps/place/Jefferson,+Iowa" rel="noreferrer" target="_blank">Jefferson</a>'),
        '516': ('ET', 'US', 'New York', '<a href="https://www.google.com/maps/place/Nassau+County:+Hempstead,+New+York" rel="noreferrer" target="_blank">Nassau County: Hempstead</a> <a href="https://www.google.com/maps/place/Oceanside,+New+York" rel="noreferrer" target="_blank">Oceanside</a> <a href="https://www.google.com/maps/place/Freeport,+New+York" rel="noreferrer" target="_blank">Freeport</a> <a href="https://www.google.com/maps/place/Long+Beach,+New+York" rel="noreferrer" target="_blank">Long Beach</a> <a href="https://www.google.com/maps/place/Garden+City,+New+York" rel="noreferrer" target="_blank">Garden City</a> <a href="https://www.google.com/maps/place/Glen+Cove,+New+York" rel="noreferrer" target="_blank">Glen Cove</a> <a href="https://www.google.com/maps/place/Mineola,+New+York" rel="noreferrer" target="_blank">Mineola</a>'),
        '517': ('ET', 'US', 'Michigan', '<a href="https://www.google.com/maps/place/Lansing,+Michigan" rel="noreferrer" target="_blank">Lansing</a> <a href="https://www.google.com/maps/place/Bay+City,+Michigan" rel="noreferrer" target="_blank">Bay City</a> <a href="https://www.google.com/maps/place/Jackson,+Michigan" rel="noreferrer" target="_blank">Jackson</a> <a href="https://www.google.com/maps/place/Howell,+Michigan" rel="noreferrer" target="_blank">Howell</a> <a href="https://www.google.com/maps/place/Adrian,+Michigan" rel="noreferrer" target="_blank">Adrian</a>'),
        '518': ('ET', 'US', 'New York', '<a href="https://www.google.com/maps/place/Albany,+New+York" rel="noreferrer" target="_blank">Albany</a> <a href="https://www.google.com/maps/place/Schenectady,+New+York" rel="noreferrer" target="_blank">Schenectady</a> <a href="https://www.google.com/maps/place/Troy,+New+York" rel="noreferrer" target="_blank">Troy</a> <a href="https://www.google.com/maps/place/Glens+Falls,+New+York" rel="noreferrer" target="_blank">Glens Falls</a> <a href="https://www.google.com/maps/place/Saratoga+Springs,+New+York" rel="noreferrer" target="_blank">Saratoga Springs</a> <a href="https://www.google.com/maps/place/Lake+Placid,+New+York" rel="noreferrer" target="_blank">Lake Placid</a>'),
        '519': ('ET', 'Ca', 'Ontario', '<a href="https://www.google.com/maps/place/London+Area,+Ontario" rel="noreferrer" target="_blank">London Area</a> <a href="https://www.google.com/maps/place/Kitchener,+Ontario" rel="noreferrer" target="_blank">Kitchener</a> <a href="https://www.google.com/maps/place/Cambridge,+Ontario" rel="noreferrer" target="_blank">Cambridge</a> <a href="https://www.google.com/maps/place/Windsor,+Ontario" rel="noreferrer" target="_blank">Windsor</a>'),
        '520': ('MT', 'US', 'Arizona', '<a href="https://www.google.com/maps/place/Tucson,+Arizona" rel="noreferrer" target="_blank">Tucson</a> <a href="https://www.google.com/maps/place/Sierra+Vista,+Arizona" rel="noreferrer" target="_blank">Sierra Vista</a> <a href="https://www.google.com/maps/place/Nogales,+Arizona" rel="noreferrer" target="_blank">Nogales</a> <a href="https://www.google.com/maps/place/Douglass,+Arizona" rel="noreferrer" target="_blank">Douglass</a> <a href="https://www.google.com/maps/place/Bisbee,+Arizona" rel="noreferrer" target="_blank">Bisbee</a>'),
        '530': ('PT', 'US', 'California', '<a href="https://www.google.com/maps/place/Chico,+California" rel="noreferrer" target="_blank">Chico</a> <a href="https://www.google.com/maps/place/Redding,+California" rel="noreferrer" target="_blank">Redding</a> <a href="https://www.google.com/maps/place/Marysville,+California" rel="noreferrer" target="_blank">Marysville</a> <a href="https://www.google.com/maps/place/Auburn,+California" rel="noreferrer" target="_blank">Auburn</a> <a href="https://www.google.com/maps/place/Davis,+California" rel="noreferrer" target="_blank">Davis</a> <a href="https://www.google.com/maps/place/Placerville,+California" rel="noreferrer" target="_blank">Placerville</a>'),
        '531': ('CT', 'US', 'Nebraska', '<a href="https://www.google.com/maps/place/Omaha,+Nebraska" rel="noreferrer" target="_blank">Omaha</a> <a href="https://www.google.com/maps/place/Lincoln,+Nebraska" rel="noreferrer" target="_blank">Lincoln</a> <a href="https://www.google.com/maps/place/Norfolk,+Nebraska" rel="noreferrer" target="_blank">Norfolk</a> <a href="https://www.google.com/maps/place/Superior,+Nebraska" rel="noreferrer" target="_blank">Superior</a> <a href="https://www.google.com/maps/place/and+most+of+eastern+Nebraska,+Nebraska" rel="noreferrer" target="_blank">and most of eastern Nebraska</a>'),
        '534': ('CT', 'US', 'Wisconsin', '<a href="https://www.google.com/maps/place/Wausau,+Wisconsin" rel="noreferrer" target="_blank">Wausau</a> <a href="https://www.google.com/maps/place/Eau+Claire,+Wisconsin" rel="noreferrer" target="_blank">Eau Claire</a> <a href="https://www.google.com/maps/place/Rhinelander,+Wisconsin" rel="noreferrer" target="_blank">Rhinelander</a> <a href="https://www.google.com/maps/place/and+most+of+northern+Wisconsin,+Wisconsin" rel="noreferrer" target="_blank">and most of northern Wisconsin</a>'),
        '539': ('CT', 'US', 'Oklahoma', '<a href="https://www.google.com/maps/place/Tulsa,+Oklahoma" rel="noreferrer" target="_blank">Tulsa</a> <a href="https://www.google.com/maps/place/Bartlesville,+Oklahoma" rel="noreferrer" target="_blank">Bartlesville</a> <a href="https://www.google.com/maps/place/McAlester,+Oklahoma" rel="noreferrer" target="_blank">McAlester</a> <a href="https://www.google.com/maps/place/Muskogee,+Oklahoma" rel="noreferrer" target="_blank">Muskogee</a> <a href="https://www.google.com/maps/place/Henryetta+and+northeastern+Oklahoma,+Oklahoma" rel="noreferrer" target="_blank">Henryetta and northeastern Oklahoma</a>'),
        '540': ('ET', 'US', 'Virginia', '<a href="https://www.google.com/maps/place/Roanoke,+Virginia" rel="noreferrer" target="_blank">Roanoke</a> <a href="https://www.google.com/maps/place/Harrisonburg,+Virginia" rel="noreferrer" target="_blank">Harrisonburg</a> <a href="https://www.google.com/maps/place/Fredericksburg,+Virginia" rel="noreferrer" target="_blank">Fredericksburg</a> <a href="https://www.google.com/maps/place/Blacksburg,+Virginia" rel="noreferrer" target="_blank">Blacksburg</a> <a href="https://www.google.com/maps/place/Winchester,+Virginia" rel="noreferrer" target="_blank">Winchester</a> <a href="https://www.google.com/maps/place/Staunton,+Virginia" rel="noreferrer" target="_blank">Staunton</a> <a href="https://www.google.com/maps/place/Culpeper,+Virginia" rel="noreferrer" target="_blank">Culpeper</a>'),
        '541': ('*MT, PT', 'US', 'Oregon', '<a href="https://www.google.com/maps/place/Eugene,+Oregon" rel="noreferrer" target="_blank">Eugene</a> <a href="https://www.google.com/maps/place/Medford,+Oregon" rel="noreferrer" target="_blank">Medford</a> <a href="https://www.google.com/maps/place/Corvallis,+Oregon" rel="noreferrer" target="_blank">Corvallis</a> <a href="https://www.google.com/maps/place/Bend,+Oregon" rel="noreferrer" target="_blank">Bend</a> <a href="https://www.google.com/maps/place/Albany,+Oregon" rel="noreferrer" target="_blank">Albany</a> <a href="https://www.google.com/maps/place/Roseburg,+Oregon" rel="noreferrer" target="_blank">Roseburg</a> <a href="https://www.google.com/maps/place/Klamath+Falls,+Oregon" rel="noreferrer" target="_blank">Klamath Falls</a>'),
        '551': ('ET', 'US', 'New Jersey', '<a href="https://www.google.com/maps/place/Hackensack,+New+Jersey" rel="noreferrer" target="_blank">Hackensack</a> <a href="https://www.google.com/maps/place/Jersey+City,+New+Jersey" rel="noreferrer" target="_blank">Jersey City</a> <a href="https://www.google.com/maps/place/Union+City,+New+Jersey" rel="noreferrer" target="_blank">Union City</a> <a href="https://www.google.com/maps/place/Rutherford,+New+Jersey" rel="noreferrer" target="_blank">Rutherford</a> <a href="https://www.google.com/maps/place/Leonia,+New+Jersey" rel="noreferrer" target="_blank">Leonia</a>'),
        '559': ('PT', 'US', 'California', '<a href="https://www.google.com/maps/place/Fresno,+California" rel="noreferrer" target="_blank">Fresno</a> <a href="https://www.google.com/maps/place/Visalia,+California" rel="noreferrer" target="_blank">Visalia</a> <a href="https://www.google.com/maps/place/Madera,+California" rel="noreferrer" target="_blank">Madera</a> <a href="https://www.google.com/maps/place/San+Joaquin,+California" rel="noreferrer" target="_blank">San Joaquin</a> <a href="https://www.google.com/maps/place/Porterville,+California" rel="noreferrer" target="_blank">Porterville</a> <a href="https://www.google.com/maps/place/Hanford,+California" rel="noreferrer" target="_blank">Hanford</a>'),
        '561': ('ET', 'US', 'Florida', '<a href="https://www.google.com/maps/place/Palm+Beaches,+Florida" rel="noreferrer" target="_blank">Palm Beaches</a> <a href="https://www.google.com/maps/place/Boca+Raton,+Florida" rel="noreferrer" target="_blank">Boca Raton</a> <a href="https://www.google.com/maps/place/Boynton+Beach,+Florida" rel="noreferrer" target="_blank">Boynton Beach</a>'),
        '562': ('PT', 'US', 'California', '<a href="https://www.google.com/maps/place/Long+Beach,+California" rel="noreferrer" target="_blank">Long Beach</a> <a href="https://www.google.com/maps/place/Norwalk,+California" rel="noreferrer" target="_blank">Norwalk</a> <a href="https://www.google.com/maps/place/Alamitos,+California" rel="noreferrer" target="_blank">Alamitos</a> <a href="https://www.google.com/maps/place/Downey,+California" rel="noreferrer" target="_blank">Downey</a> <a href="https://www.google.com/maps/place/Whittier,+California" rel="noreferrer" target="_blank">Whittier</a> <a href="https://www.google.com/maps/place/Lakewood,+California" rel="noreferrer" target="_blank">Lakewood</a> <a href="https://www.google.com/maps/place/La+Habra,+California" rel="noreferrer" target="_blank">La Habra</a>'),
        '563': ('CT', 'US', 'Iowa', '<a href="https://www.google.com/maps/place/Davenport,+Iowa" rel="noreferrer" target="_blank">Davenport</a> <a href="https://www.google.com/maps/place/Dubuque,+Iowa" rel="noreferrer" target="_blank">Dubuque</a> <a href="https://www.google.com/maps/place/Clinton,+Iowa" rel="noreferrer" target="_blank">Clinton</a> <a href="https://www.google.com/maps/place/Muscatine,+Iowa" rel="noreferrer" target="_blank">Muscatine</a> <a href="https://www.google.com/maps/place/Decorah,+Iowa" rel="noreferrer" target="_blank">Decorah</a> <a href="https://www.google.com/maps/place/Manchester,+Iowa" rel="noreferrer" target="_blank">Manchester</a> <a href="https://www.google.com/maps/place/West+Union,+Iowa" rel="noreferrer" target="_blank">West Union</a>'),
        '567': ('ET', 'US', 'Ohio', '<a href="https://www.google.com/maps/place/Toledo,+Ohio" rel="noreferrer" target="_blank">Toledo</a> <a href="https://www.google.com/maps/place/Lima,+Ohio" rel="noreferrer" target="_blank">Lima</a> <a href="https://www.google.com/maps/place/Mansfield,+Ohio" rel="noreferrer" target="_blank">Mansfield</a> <a href="https://www.google.com/maps/place/Sandusky,+Ohio" rel="noreferrer" target="_blank">Sandusky</a> <a href="https://www.google.com/maps/place/Findlay,+Ohio" rel="noreferrer" target="_blank">Findlay</a>'),
        '570': ('ET', 'US', 'Pennsylvania', '<a href="https://www.google.com/maps/place/Williamsport+,+Pennsylvania" rel="noreferrer" target="_blank">Williamsport </a> <a href="https://www.google.com/maps/place/Scranton+,+Pennsylvania" rel="noreferrer" target="_blank">Scranton </a> <a href="https://www.google.com/maps/place/Wilkes-Barre+and+Monroe+County,+Pennsylvania" rel="noreferrer" target="_blank">Wilkes-Barre and Monroe County</a>'),
        '571': ('ET', 'US', 'Virginia', '<a href="https://www.google.com/maps/place/Arlington,+Virginia" rel="noreferrer" target="_blank">Arlington</a> <a href="https://www.google.com/maps/place/Alexandria,+Virginia" rel="noreferrer" target="_blank">Alexandria</a> <a href="https://www.google.com/maps/place/Fairfax,+Virginia" rel="noreferrer" target="_blank">Fairfax</a> <a href="https://www.google.com/maps/place/Falls+Church,+Virginia" rel="noreferrer" target="_blank">Falls Church</a> <a href="https://www.google.com/maps/place/Quantico,+Virginia" rel="noreferrer" target="_blank">Quantico</a> <a href="https://www.google.com/maps/place/Herndon,+Virginia" rel="noreferrer" target="_blank">Herndon</a> <a href="https://www.google.com/maps/place/Vienna,+Virginia" rel="noreferrer" target="_blank">Vienna</a>'),
        '573': ('CT', 'US', 'Missouri', '<a href="https://www.google.com/maps/place/Columbia,+Missouri" rel="noreferrer" target="_blank">Columbia</a> <a href="https://www.google.com/maps/place/Cape+Girardeau,+Missouri" rel="noreferrer" target="_blank">Cape Girardeau</a> <a href="https://www.google.com/maps/place/Jefferson+City,+Missouri" rel="noreferrer" target="_blank">Jefferson City</a>'),
        '574': ('*ET, CT', 'US', 'Indiana', '<a href="https://www.google.com/maps/place/South+Bend,+Indiana" rel="noreferrer" target="_blank">South Bend</a> <a href="https://www.google.com/maps/place/Elkhart,+Indiana" rel="noreferrer" target="_blank">Elkhart</a> <a href="https://www.google.com/maps/place/Mishawaka,+Indiana" rel="noreferrer" target="_blank">Mishawaka</a> <a href="https://www.google.com/maps/place/Granger,+Indiana" rel="noreferrer" target="_blank">Granger</a> <a href="https://www.google.com/maps/place/La+Porte,+Indiana" rel="noreferrer" target="_blank">La Porte</a>'),
        '575': ('MT', 'US', 'New Mexico', '<a href="https://www.google.com/maps/place/Alamogordo,+New+Mexico" rel="noreferrer" target="_blank">Alamogordo</a> <a href="https://www.google.com/maps/place/Carlsbad,+New+Mexico" rel="noreferrer" target="_blank">Carlsbad</a> <a href="https://www.google.com/maps/place/Clovis,+New+Mexico" rel="noreferrer" target="_blank">Clovis</a> <a href="https://www.google.com/maps/place/Deming,+New+Mexico" rel="noreferrer" target="_blank">Deming</a> <a href="https://www.google.com/maps/place/El+Rito,+New+Mexico" rel="noreferrer" target="_blank">El Rito</a> <a href="https://www.google.com/maps/place/Galina,+New+Mexico" rel="noreferrer" target="_blank">Galina</a> <a href="https://www.google.com/maps/place/Hatch,+New+Mexico" rel="noreferrer" target="_blank">Hatch</a> <a href="https://www.google.com/maps/place/Hobbs,+New+Mexico" rel="noreferrer" target="_blank">Hobbs</a> <a href="https://www.google.com/maps/place/Las+Cruces,+New+Mexico" rel="noreferrer" target="_blank">Las Cruces</a> <a href="https://www.google.com/maps/place/Penasco,+New+Mexico" rel="noreferrer" target="_blank">Penasco</a> <a href="https://www.google.com/maps/place/Raton,+New+Mexico" rel="noreferrer" target="_blank">Raton</a> <a href="https://www.google.com/maps/place/Taos,+New+Mexico" rel="noreferrer" target="_blank">Taos</a>'),
        '579': ('ET', 'Ca', 'Quebec', '<a href="https://www.google.com/maps/place/central+southern+Quebec+including+the+city+of+Laval+and+other+suburbs+of+Montreal+but+excluding+the+City+of+Montreal,+Quebec" rel="noreferrer" target="_blank">central southern Quebec including the city of Laval and other suburbs of Montreal but excluding the City of Montreal</a>'),
        '580': ('CT', 'US', 'Oklahoma', '<a href="https://www.google.com/maps/place/Lawton,+Oklahoma" rel="noreferrer" target="_blank">Lawton</a> <a href="https://www.google.com/maps/place/Enid,+Oklahoma" rel="noreferrer" target="_blank">Enid</a> <a href="https://www.google.com/maps/place/Ponca+City,+Oklahoma" rel="noreferrer" target="_blank">Ponca City</a> <a href="https://www.google.com/maps/place/Ardmore,+Oklahoma" rel="noreferrer" target="_blank">Ardmore</a> <a href="https://www.google.com/maps/place/Duncan,+Oklahoma" rel="noreferrer" target="_blank">Duncan</a>'),
        '581': ('ET', 'Ca', 'Quebec', '<a href="https://www.google.com/maps/place/Levis,+Quebec" rel="noreferrer" target="_blank">Levis</a> <a href="https://www.google.com/maps/place/Quebec+City,+Quebec" rel="noreferrer" target="_blank">Quebec City</a>'),
        '585': ('ET', 'US', 'New York', '<a href="https://www.google.com/maps/place/Rochester,+New+York" rel="noreferrer" target="_blank">Rochester</a> <a href="https://www.google.com/maps/place/East+Rochester,+New+York" rel="noreferrer" target="_blank">East Rochester</a> <a href="https://www.google.com/maps/place/Olean,+New+York" rel="noreferrer" target="_blank">Olean</a> <a href="https://www.google.com/maps/place/Batavia,+New+York" rel="noreferrer" target="_blank">Batavia</a> <a href="https://www.google.com/maps/place/Webster,+New+York" rel="noreferrer" target="_blank">Webster</a> <a href="https://www.google.com/maps/place/Fairport,+New+York" rel="noreferrer" target="_blank">Fairport</a> <a href="https://www.google.com/maps/place/Henrietta,+New+York" rel="noreferrer" target="_blank">Henrietta</a>'),
        '586': ('ET', 'US', 'Michigan', '<a href="https://www.google.com/maps/place/Warren,+Michigan" rel="noreferrer" target="_blank">Warren</a> <a href="https://www.google.com/maps/place/Mount+Clemens,+Michigan" rel="noreferrer" target="_blank">Mount Clemens</a> <a href="https://www.google.com/maps/place/Roseville,+Michigan" rel="noreferrer" target="_blank">Roseville</a> <a href="https://www.google.com/maps/place/Center+Line,+Michigan" rel="noreferrer" target="_blank">Center Line</a> <a href="https://www.google.com/maps/place/Utica,+Michigan" rel="noreferrer" target="_blank">Utica</a> <a href="https://www.google.com/maps/place/Romeo,+Michigan" rel="noreferrer" target="_blank">Romeo</a> <a href="https://www.google.com/maps/place/Richmond,+Michigan" rel="noreferrer" target="_blank">Richmond</a> <a href="https://www.google.com/maps/place/Washington,+Michigan" rel="noreferrer" target="_blank">Washington</a> <a href="https://www.google.com/maps/place/New+Baltimore,+Michigan" rel="noreferrer" target="_blank">New Baltimore</a>'),
        '587': ('MST', 'Ca', 'Alberta', '<a href="https://www.google.com/maps/place/Calgary,+Alberta" rel="noreferrer" target="_blank">Calgary</a> <a href="https://www.google.com/maps/place/Lethbridge,+Alberta" rel="noreferrer" target="_blank">Lethbridge</a> <a href="https://www.google.com/maps/place/Banff,+Alberta" rel="noreferrer" target="_blank">Banff</a> <a href="https://www.google.com/maps/place/Medicine+Hat,+Alberta" rel="noreferrer" target="_blank">Medicine Hat</a> <a href="https://www.google.com/maps/place/Red+Deer,+Alberta" rel="noreferrer" target="_blank">Red Deer</a> <a href="https://www.google.com/maps/place/Alberta:+Edmonton,+Alberta" rel="noreferrer" target="_blank">Alberta: Edmonton</a> <a href="https://www.google.com/maps/place/Fort+McMurray,+Alberta" rel="noreferrer" target="_blank">Fort McMurray</a> <a href="https://www.google.com/maps/place/Leduc,+Alberta" rel="noreferrer" target="_blank">Leduc</a> <a href="https://www.google.com/maps/place/Lloydminster,+Alberta" rel="noreferrer" target="_blank">Lloydminster</a> <a href="https://www.google.com/maps/place/Sherwood+Park,+Alberta" rel="noreferrer" target="_blank">Sherwood Park</a>'),
        '600': ('ET', 'Ca', '', '<a href="https://www.google.com/maps/place/Canadian+Services,+" rel="noreferrer" target="_blank">Canadian Services</a>'),
        '601': ('CT', 'US', 'Mississippi', '<a href="https://www.google.com/maps/place/Southern+Mississippi:+Jackson,+Mississippi" rel="noreferrer" target="_blank">Southern Mississippi: Jackson</a> <a href="https://www.google.com/maps/place/Hattiesburg,+Mississippi" rel="noreferrer" target="_blank">Hattiesburg</a> <a href="https://www.google.com/maps/place/Vicksburg,+Mississippi" rel="noreferrer" target="_blank">Vicksburg</a> <a href="https://www.google.com/maps/place/Meridian,+Mississippi" rel="noreferrer" target="_blank">Meridian</a>'),
        '602': ('MT', 'US', 'Arizona', '<a href="https://www.google.com/maps/place/Phoenix,+Arizona" rel="noreferrer" target="_blank">Phoenix</a>'),
        '603': ('ET', 'US', 'New Hampshire', '<a href="https://www.google.com/maps/place/New+Hampshire" rel="noreferrer" target="_blank">All areas</a>'),
        '604': ('PT', 'Ca', 'British Columbia', '<a href="https://www.google.com/maps/place/Vancouver,+British+Columbia" rel="noreferrer" target="_blank">Vancouver</a> <a href="https://www.google.com/maps/place/Richmond,+British+Columbia" rel="noreferrer" target="_blank">Richmond</a> <a href="https://www.google.com/maps/place/New+Westminster,+British+Columbia" rel="noreferrer" target="_blank">New Westminster</a>'),
        '605': ('*CT, MT', 'US', 'South Dakota', '<a href="https://www.google.com/maps/place/South+Dakota" rel="noreferrer" target="_blank">All areas</a>'),
        '606': ('*ET, CT', 'US', 'Kentucky', '<a href="https://www.google.com/maps/place/Ashland,+Kentucky" rel="noreferrer" target="_blank">Ashland</a> <a href="https://www.google.com/maps/place/Winchester,+Kentucky" rel="noreferrer" target="_blank">Winchester</a> <a href="https://www.google.com/maps/place/Pikeville,+Kentucky" rel="noreferrer" target="_blank">Pikeville</a> <a href="https://www.google.com/maps/place/Somerset,+Kentucky" rel="noreferrer" target="_blank">Somerset</a>'),
        '607': ('ET', 'US', 'New York', '<a href="https://www.google.com/maps/place/Elmira,+New+York" rel="noreferrer" target="_blank">Elmira</a> <a href="https://www.google.com/maps/place/Ithaca,+New+York" rel="noreferrer" target="_blank">Ithaca</a> <a href="https://www.google.com/maps/place/Stamford,+New+York" rel="noreferrer" target="_blank">Stamford</a> <a href="https://www.google.com/maps/place/Binghamton,+New+York" rel="noreferrer" target="_blank">Binghamton</a> <a href="https://www.google.com/maps/place/Endicott,+New+York" rel="noreferrer" target="_blank">Endicott</a> <a href="https://www.google.com/maps/place/Oneonta,+New+York" rel="noreferrer" target="_blank">Oneonta</a>'),
        '608': ('CT', 'US', 'Wisconsin', '<a href="https://www.google.com/maps/place/Madison,+Wisconsin" rel="noreferrer" target="_blank">Madison</a> <a href="https://www.google.com/maps/place/La+Crosse,+Wisconsin" rel="noreferrer" target="_blank">La Crosse</a> <a href="https://www.google.com/maps/place/Janesville,+Wisconsin" rel="noreferrer" target="_blank">Janesville</a> <a href="https://www.google.com/maps/place/Middleton,+Wisconsin" rel="noreferrer" target="_blank">Middleton</a> <a href="https://www.google.com/maps/place/Monroe,+Wisconsin" rel="noreferrer" target="_blank">Monroe</a> <a href="https://www.google.com/maps/place/Platteville,+Wisconsin" rel="noreferrer" target="_blank">Platteville</a> <a href="https://www.google.com/maps/place/Dodgeville,+Wisconsin" rel="noreferrer" target="_blank">Dodgeville</a>'),
        '609': ('ET', 'US', 'New Jersey', '<a href="https://www.google.com/maps/place/Atlantic+City,+New+Jersey" rel="noreferrer" target="_blank">Atlantic City</a> <a href="https://www.google.com/maps/place/Trenton,+New+Jersey" rel="noreferrer" target="_blank">Trenton</a> <a href="https://www.google.com/maps/place/Princeton,+New+Jersey" rel="noreferrer" target="_blank">Princeton</a> <a href="https://www.google.com/maps/place/Pleasantville,+New+Jersey" rel="noreferrer" target="_blank">Pleasantville</a> <a href="https://www.google.com/maps/place/Fort+Dix,+New+Jersey" rel="noreferrer" target="_blank">Fort Dix</a> <a href="https://www.google.com/maps/place/Lawrenceville,+New+Jersey" rel="noreferrer" target="_blank">Lawrenceville</a>'),
        '610': ('ET', 'US', 'Pennsylvania', '<a href="https://www.google.com/maps/place/Allentown,+Pennsylvania" rel="noreferrer" target="_blank">Allentown</a> <a href="https://www.google.com/maps/place/Reading,+Pennsylvania" rel="noreferrer" target="_blank">Reading</a> <a href="https://www.google.com/maps/place/Bethlehem,+Pennsylvania" rel="noreferrer" target="_blank">Bethlehem</a> <a href="https://www.google.com/maps/place/West+Chester,+Pennsylvania" rel="noreferrer" target="_blank">West Chester</a> <a href="https://www.google.com/maps/place/Pottstown,+Pennsylvania" rel="noreferrer" target="_blank">Pottstown</a>'),
        '612': ('CT', 'US', 'Minnesota', '<a href="https://www.google.com/maps/place/Minneapolis,+Minnesota" rel="noreferrer" target="_blank">Minneapolis</a> <a href="https://www.google.com/maps/place/Richfield,+Minnesota" rel="noreferrer" target="_blank">Richfield</a>'),
        '613': ('ET', 'Ca', 'Ontario', '<a href="https://www.google.com/maps/place/Ottawa,+Ontario" rel="noreferrer" target="_blank">Ottawa</a> <a href="https://www.google.com/maps/place/Kingston,+Ontario" rel="noreferrer" target="_blank">Kingston</a> <a href="https://www.google.com/maps/place/Belleville,+Ontario" rel="noreferrer" target="_blank">Belleville</a> <a href="https://www.google.com/maps/place/Cornwall,+Ontario" rel="noreferrer" target="_blank">Cornwall</a> <a href="https://www.google.com/maps/place/Kanata,+Ontario" rel="noreferrer" target="_blank">Kanata</a>'),
        '614': ('ET', 'US', 'Ohio', '<a href="https://www.google.com/maps/place/Columbus,+Ohio" rel="noreferrer" target="_blank">Columbus</a> <a href="https://www.google.com/maps/place/Worthington,+Ohio" rel="noreferrer" target="_blank">Worthington</a> <a href="https://www.google.com/maps/place/Dublin,+Ohio" rel="noreferrer" target="_blank">Dublin</a> <a href="https://www.google.com/maps/place/Reynoldsburg,+Ohio" rel="noreferrer" target="_blank">Reynoldsburg</a> <a href="https://www.google.com/maps/place/Westerville,+Ohio" rel="noreferrer" target="_blank">Westerville</a> <a href="https://www.google.com/maps/place/Gahanna,+Ohio" rel="noreferrer" target="_blank">Gahanna</a> <a href="https://www.google.com/maps/place/Hilliard,+Ohio" rel="noreferrer" target="_blank">Hilliard</a>'),
        '615': ('CT', 'US', 'Tennessee', '<a href="https://www.google.com/maps/place/Nashville,+Tennessee" rel="noreferrer" target="_blank">Nashville</a> <a href="https://www.google.com/maps/place/Mufreesboro,+Tennessee" rel="noreferrer" target="_blank">Mufreesboro</a> <a href="https://www.google.com/maps/place/Hendersonville,+Tennessee" rel="noreferrer" target="_blank">Hendersonville</a> <a href="https://www.google.com/maps/place/Frank,+Tennessee" rel="noreferrer" target="_blank">Frank</a>'),
        '616': ('ET', 'US', 'Michigan', '<a href="https://www.google.com/maps/place/Grand+Rapids,+Michigan" rel="noreferrer" target="_blank">Grand Rapids</a> <a href="https://www.google.com/maps/place/Holland,+Michigan" rel="noreferrer" target="_blank">Holland</a> <a href="https://www.google.com/maps/place/Grand+Haven,+Michigan" rel="noreferrer" target="_blank">Grand Haven</a> <a href="https://www.google.com/maps/place/Greenville,+Michigan" rel="noreferrer" target="_blank">Greenville</a> <a href="https://www.google.com/maps/place/Zeeland,+Michigan" rel="noreferrer" target="_blank">Zeeland</a> <a href="https://www.google.com/maps/place/Ionia,+Michigan" rel="noreferrer" target="_blank">Ionia</a>'),
        '617': ('ET', 'US', 'Massachusetts', '<a href="https://www.google.com/maps/place/Boston,+Massachusetts" rel="noreferrer" target="_blank">Boston</a> <a href="https://www.google.com/maps/place/Cambridge,+Massachusetts" rel="noreferrer" target="_blank">Cambridge</a> <a href="https://www.google.com/maps/place/Quincy,+Massachusetts" rel="noreferrer" target="_blank">Quincy</a> <a href="https://www.google.com/maps/place/Newton,+Massachusetts" rel="noreferrer" target="_blank">Newton</a> <a href="https://www.google.com/maps/place/Brookline,+Massachusetts" rel="noreferrer" target="_blank">Brookline</a> <a href="https://www.google.com/maps/place/Brighton,+Massachusetts" rel="noreferrer" target="_blank">Brighton</a> <a href="https://www.google.com/maps/place/Somerville,+Massachusetts" rel="noreferrer" target="_blank">Somerville</a> <a href="https://www.google.com/maps/place/Dorchester,+Massachusetts" rel="noreferrer" target="_blank">Dorchester</a> <a href="https://www.google.com/maps/place/Hyde+Park,+Massachusetts" rel="noreferrer" target="_blank">Hyde Park</a> <a href="https://www.google.com/maps/place/Jamaica+Plain,+Massachusetts" rel="noreferrer" target="_blank">Jamaica Plain</a>'),
        '618': ('CT', 'US', 'Illinois', '<a href="https://www.google.com/maps/place/Collinsville,+Illinois" rel="noreferrer" target="_blank">Collinsville</a> <a href="https://www.google.com/maps/place/Alton,+Illinois" rel="noreferrer" target="_blank">Alton</a> <a href="https://www.google.com/maps/place/Carbondale,+Illinois" rel="noreferrer" target="_blank">Carbondale</a> <a href="https://www.google.com/maps/place/Belleville,+Illinois" rel="noreferrer" target="_blank">Belleville</a> <a href="https://www.google.com/maps/place/Mount+Vernon,+Illinois" rel="noreferrer" target="_blank">Mount Vernon</a> <a href="https://www.google.com/maps/place/Centralia,+Illinois" rel="noreferrer" target="_blank">Centralia</a>'),
        '619': ('PT', 'US', 'California', '<a href="https://www.google.com/maps/place/San+Diego,+California" rel="noreferrer" target="_blank">San Diego</a> <a href="https://www.google.com/maps/place/Chula+Vista,+California" rel="noreferrer" target="_blank">Chula Vista</a> <a href="https://www.google.com/maps/place/El+Cajon,+California" rel="noreferrer" target="_blank">El Cajon</a> <a href="https://www.google.com/maps/place/La+Mesa,+California" rel="noreferrer" target="_blank">La Mesa</a> <a href="https://www.google.com/maps/place/National+City,+California" rel="noreferrer" target="_blank">National City</a> <a href="https://www.google.com/maps/place/Coronado,+California" rel="noreferrer" target="_blank">Coronado</a>'),
        '620': ('*CT, MT', 'US', 'Kansas', '<a href="https://www.google.com/maps/place/Hutchinson,+Kansas" rel="noreferrer" target="_blank">Hutchinson</a> <a href="https://www.google.com/maps/place/Emporia,+Kansas" rel="noreferrer" target="_blank">Emporia</a> <a href="https://www.google.com/maps/place/Liberal,+Kansas" rel="noreferrer" target="_blank">Liberal</a> <a href="https://www.google.com/maps/place/Pittsburg,+Kansas" rel="noreferrer" target="_blank">Pittsburg</a> <a href="https://www.google.com/maps/place/Dodge+City,+Kansas" rel="noreferrer" target="_blank">Dodge City</a> <a href="https://www.google.com/maps/place/Garden+City,+Kansas" rel="noreferrer" target="_blank">Garden City</a> <a href="https://www.google.com/maps/place/Coffeyville,+Kansas" rel="noreferrer" target="_blank">Coffeyville</a>'),
        '623': ('MST', 'US', 'Arizona', '<a href="https://www.google.com/maps/place/Glendale,+Arizona" rel="noreferrer" target="_blank">Glendale</a> <a href="https://www.google.com/maps/place/Sun+City,+Arizona" rel="noreferrer" target="_blank">Sun City</a> <a href="https://www.google.com/maps/place/Peoria,+Arizona" rel="noreferrer" target="_blank">Peoria</a>'),
        '626': ('PT', 'US', 'California', '<a href="https://www.google.com/maps/place/Pasadena,+California" rel="noreferrer" target="_blank">Pasadena</a> <a href="https://www.google.com/maps/place/Alhambra,+California" rel="noreferrer" target="_blank">Alhambra</a> <a href="https://www.google.com/maps/place/Covina,+California" rel="noreferrer" target="_blank">Covina</a> <a href="https://www.google.com/maps/place/El+Monte,+California" rel="noreferrer" target="_blank">El Monte</a> <a href="https://www.google.com/maps/place/La+Puenta,+California" rel="noreferrer" target="_blank">La Puenta</a>'),
        '630': ('CT', 'US', 'Illinois', '<a href="https://www.google.com/maps/place/La+Grange,+Illinois" rel="noreferrer" target="_blank">La Grange</a> <a href="https://www.google.com/maps/place/Roselle,+Illinois" rel="noreferrer" target="_blank">Roselle</a> <a href="https://www.google.com/maps/place/Hinsdale,+Illinois" rel="noreferrer" target="_blank">Hinsdale</a> <a href="https://www.google.com/maps/place/Downers+Grove,+Illinois" rel="noreferrer" target="_blank">Downers Grove</a> <a href="https://www.google.com/maps/place/Naperville,+Illinois" rel="noreferrer" target="_blank">Naperville</a> <a href="https://www.google.com/maps/place/Lombard,+Illinois" rel="noreferrer" target="_blank">Lombard</a> <a href="https://www.google.com/maps/place/Elmhurst,+Illinois" rel="noreferrer" target="_blank">Elmhurst</a> <a href="https://www.google.com/maps/place/Aurora,+Illinois" rel="noreferrer" target="_blank">Aurora</a> <a href="https://www.google.com/maps/place/Wheaton,+Illinois" rel="noreferrer" target="_blank">Wheaton</a>'),
        '631': ('ET', 'US', 'New York', '<a href="https://www.google.com/maps/place/Suffolk+County:+Brentwood,+New+York" rel="noreferrer" target="_blank">Suffolk County: Brentwood</a> <a href="https://www.google.com/maps/place/Farmingdale,+New+York" rel="noreferrer" target="_blank">Farmingdale</a> <a href="https://www.google.com/maps/place/Central+Islip,+New+York" rel="noreferrer" target="_blank">Central Islip</a> <a href="https://www.google.com/maps/place/Riverhead,+New+York" rel="noreferrer" target="_blank">Riverhead</a> <a href="https://www.google.com/maps/place/Huntington,+New+York" rel="noreferrer" target="_blank">Huntington</a> <a href="https://www.google.com/maps/place/Deer+Park,+New+York" rel="noreferrer" target="_blank">Deer Park</a> <a href="https://www.google.com/maps/place/Amityville,+New+York" rel="noreferrer" target="_blank">Amityville</a> <a href="https://www.google.com/maps/place/Lindenhurst,+New+York" rel="noreferrer" target="_blank">Lindenhurst</a>'),
        '636': ('CT', 'US', 'Missouri', '<a href="https://www.google.com/maps/place/St.+Charles,+Missouri" rel="noreferrer" target="_blank">St. Charles</a> <a href="https://www.google.com/maps/place/Fenton,+Missouri" rel="noreferrer" target="_blank">Fenton</a> <a href="https://www.google.com/maps/place/Harvester,+Missouri" rel="noreferrer" target="_blank">Harvester</a> <a href="https://www.google.com/maps/place/Chesterfield,+Missouri" rel="noreferrer" target="_blank">Chesterfield</a> <a href="https://www.google.com/maps/place/Manchester,+Missouri" rel="noreferrer" target="_blank">Manchester</a>'),
        '639': ('CT', 'Ca', 'Saskatchewan', '<a href="https://www.google.com/maps/place/Saskatchewan" rel="noreferrer" target="_blank">All areas</a>'),
        '641': ('CT', 'US', 'Iowa', '<a href="https://www.google.com/maps/place/Fairfield,+Iowa" rel="noreferrer" target="_blank">Fairfield</a> <a href="https://www.google.com/maps/place/Mason+City,+Iowa" rel="noreferrer" target="_blank">Mason City</a> <a href="https://www.google.com/maps/place/Grinnell,+Iowa" rel="noreferrer" target="_blank">Grinnell</a> <a href="https://www.google.com/maps/place/Newton,+Iowa" rel="noreferrer" target="_blank">Newton</a> <a href="https://www.google.com/maps/place/Knoxville,+Iowa" rel="noreferrer" target="_blank">Knoxville</a>'),
        '646': ('ET', 'US', 'New York', '<a href="https://www.google.com/maps/place/Manhattan,+New+York" rel="noreferrer" target="_blank">Manhattan</a>'),
        '647': ('ET', 'Ca', 'Ontario', '<a href="https://www.google.com/maps/place/Toronto,+Ontario" rel="noreferrer" target="_blank">Toronto</a>'),
        '650': ('PT', 'US', 'California', '<a href="https://www.google.com/maps/place/South+San+Francisco,+California" rel="noreferrer" target="_blank">South San Francisco</a> <a href="https://www.google.com/maps/place/Palo+Alto,+California" rel="noreferrer" target="_blank">Palo Alto</a> <a href="https://www.google.com/maps/place/San+Mateo,+California" rel="noreferrer" target="_blank">San Mateo</a> <a href="https://www.google.com/maps/place/Mountain+View,+California" rel="noreferrer" target="_blank">Mountain View</a> <a href="https://www.google.com/maps/place/Redwood+City,+California" rel="noreferrer" target="_blank">Redwood City</a>'),
        '651': ('CT', 'US', 'Minnesota', '<a href="https://www.google.com/maps/place/St.+Paul,+Minnesota" rel="noreferrer" target="_blank">St. Paul</a> <a href="https://www.google.com/maps/place/Redwing,+Minnesota" rel="noreferrer" target="_blank">Redwing</a> <a href="https://www.google.com/maps/place/Farmington,+Minnesota" rel="noreferrer" target="_blank">Farmington</a> <a href="https://www.google.com/maps/place/Eagan,+Minnesota" rel="noreferrer" target="_blank">Eagan</a> <a href="https://www.google.com/maps/place/Lino+Lakes,+Minnesota" rel="noreferrer" target="_blank">Lino Lakes</a> <a href="https://www.google.com/maps/place/North+Branch,+Minnesota" rel="noreferrer" target="_blank">North Branch</a> <a href="https://www.google.com/maps/place/Roseville+Valley,+Minnesota" rel="noreferrer" target="_blank">Roseville Valley</a>'),
        '657': ('PT', 'US', 'California', '<a href="https://www.google.com/maps/place/Anaheim,+California" rel="noreferrer" target="_blank">Anaheim</a> <a href="https://www.google.com/maps/place/Santa+Anna,+California" rel="noreferrer" target="_blank">Santa Anna</a>'),
        '660': ('CT', 'US', 'Missouri', '<a href="https://www.google.com/maps/place/Warrensburg,+Missouri" rel="noreferrer" target="_blank">Warrensburg</a> <a href="https://www.google.com/maps/place/Kirksville,+Missouri" rel="noreferrer" target="_blank">Kirksville</a> <a href="https://www.google.com/maps/place/Sedalia,+Missouri" rel="noreferrer" target="_blank">Sedalia</a> <a href="https://www.google.com/maps/place/Chillicothe,+Missouri" rel="noreferrer" target="_blank">Chillicothe</a> <a href="https://www.google.com/maps/place/Moberly,+Missouri" rel="noreferrer" target="_blank">Moberly</a> <a href="https://www.google.com/maps/place/Marshall,+Missouri" rel="noreferrer" target="_blank">Marshall</a>'),
        '661': ('PT', 'US', 'California', '<a href="https://www.google.com/maps/place/Bakersfield,+California" rel="noreferrer" target="_blank">Bakersfield</a> <a href="https://www.google.com/maps/place/Santa+Clarita,+California" rel="noreferrer" target="_blank">Santa Clarita</a> <a href="https://www.google.com/maps/place/Palmdale,+California" rel="noreferrer" target="_blank">Palmdale</a> <a href="https://www.google.com/maps/place/Simi+Valley,+California" rel="noreferrer" target="_blank">Simi Valley</a>'),
        '662': ('CT', 'US', 'Mississippi', '<a href="https://www.google.com/maps/place/Tupelo,+Mississippi" rel="noreferrer" target="_blank">Tupelo</a> <a href="https://www.google.com/maps/place/Columbus,+Mississippi" rel="noreferrer" target="_blank">Columbus</a> <a href="https://www.google.com/maps/place/Greenwood,+Mississippi" rel="noreferrer" target="_blank">Greenwood</a> <a href="https://www.google.com/maps/place/Greenville,+Mississippi" rel="noreferrer" target="_blank">Greenville</a> <a href="https://www.google.com/maps/place/Oxford,+Mississippi" rel="noreferrer" target="_blank">Oxford</a>'),
        '667': ('ET', 'US', 'Maryland', '<a href="https://www.google.com/maps/place/,+Maryland" rel="noreferrer" target="_blank"></a>'),
        '669': ('PT', 'US', 'California', '<a href="https://www.google.com/maps/place/San+Jose,+California" rel="noreferrer" target="_blank">San Jose</a>'),
        '678': ('ET', 'US', 'Georgia', '<a href="https://www.google.com/maps/place/Atlanta,+Georgia" rel="noreferrer" target="_blank">Atlanta</a> <a href="https://www.google.com/maps/place/Norcross,+Georgia" rel="noreferrer" target="_blank">Norcross</a> <a href="https://www.google.com/maps/place/Chamblee,+Georgia" rel="noreferrer" target="_blank">Chamblee</a> <a href="https://www.google.com/maps/place/Smyrna,+Georgia" rel="noreferrer" target="_blank">Smyrna</a> <a href="https://www.google.com/maps/place/Tucker,+Georgia" rel="noreferrer" target="_blank">Tucker</a> <a href="https://www.google.com/maps/place/Marietta,+Georgia" rel="noreferrer" target="_blank">Marietta</a> <a href="https://www.google.com/maps/place/Alpharetta,+Georgia" rel="noreferrer" target="_blank">Alpharetta</a> <a href="https://www.google.com/maps/place/Gainesville,+Georgia" rel="noreferrer" target="_blank">Gainesville</a>'),
        '681': ('ET', 'US', 'West Virginia', '<a href="https://www.google.com/maps/place/West+Virginia" rel="noreferrer" target="_blank">All areas</a>'),
        '682': ('CT', 'US', 'Texas', '<a href="https://www.google.com/maps/place/Fort+Worth,+Texas" rel="noreferrer" target="_blank">Fort Worth</a> <a href="https://www.google.com/maps/place/Arlington,+Texas" rel="noreferrer" target="_blank">Arlington</a> <a href="https://www.google.com/maps/place/Euless,+Texas" rel="noreferrer" target="_blank">Euless</a> <a href="https://www.google.com/maps/place/Grapevine,+Texas" rel="noreferrer" target="_blank">Grapevine</a>'),
        '701': ('*CT, MT', 'US', 'North Dakota', '<a href="https://www.google.com/maps/place/North+Dakota" rel="noreferrer" target="_blank">All areas</a>'),
        '702': ('PT', 'US', 'Nevada', '<a href="https://www.google.com/maps/place/Las+Vegas,+Nevada" rel="noreferrer" target="_blank">Las Vegas and surrounding areas</a>'),
        '703': ('ET', 'US', 'Virginia', '<a href="https://www.google.com/maps/place/Arlington,+Virginia" rel="noreferrer" target="_blank">Arlington</a> <a href="https://www.google.com/maps/place/Alexandria,+Virginia" rel="noreferrer" target="_blank">Alexandria</a> <a href="https://www.google.com/maps/place/Fairfax,+Virginia" rel="noreferrer" target="_blank">Fairfax</a> <a href="https://www.google.com/maps/place/Falls+Church,+Virginia" rel="noreferrer" target="_blank">Falls Church</a> <a href="https://www.google.com/maps/place/Quantico,+Virginia" rel="noreferrer" target="_blank">Quantico</a> <a href="https://www.google.com/maps/place/Herndon,+Virginia" rel="noreferrer" target="_blank">Herndon</a> <a href="https://www.google.com/maps/place/Vienna,+Virginia" rel="noreferrer" target="_blank">Vienna</a>'),
        '704': ('ET', 'US', 'North Carolina', '<a href="https://www.google.com/maps/place/Charlotte,+North+Carolina" rel="noreferrer" target="_blank">Charlotte</a> <a href="https://www.google.com/maps/place/Asheville,+North+Carolina" rel="noreferrer" target="_blank">Asheville</a> <a href="https://www.google.com/maps/place/Gastonia,+North+Carolina" rel="noreferrer" target="_blank">Gastonia</a> <a href="https://www.google.com/maps/place/Concord,+North+Carolina" rel="noreferrer" target="_blank">Concord</a> <a href="https://www.google.com/maps/place/Statesville,+North+Carolina" rel="noreferrer" target="_blank">Statesville</a> <a href="https://www.google.com/maps/place/Salisbury,+North+Carolina" rel="noreferrer" target="_blank">Salisbury</a> <a href="https://www.google.com/maps/place/Shelby,+North+Carolina" rel="noreferrer" target="_blank">Shelby</a> <a href="https://www.google.com/maps/place/Monroe,+North+Carolina" rel="noreferrer" target="_blank">Monroe</a>'),
        '705': ('ET', 'Ca', 'Ontario', '<a href="https://www.google.com/maps/place/North+Bay,+Ontario" rel="noreferrer" target="_blank">North Bay</a> <a href="https://www.google.com/maps/place/Sault+Sainte+Marie,+Ontario" rel="noreferrer" target="_blank">Sault Sainte Marie</a>'),
        '706': ('ET', 'US', 'Georgia', '<a href="https://www.google.com/maps/place/Augusta,+Georgia" rel="noreferrer" target="_blank">Augusta</a> <a href="https://www.google.com/maps/place/Columbus,+Georgia" rel="noreferrer" target="_blank">Columbus</a> <a href="https://www.google.com/maps/place/Athens,+Georgia" rel="noreferrer" target="_blank">Athens</a> <a href="https://www.google.com/maps/place/Rome,+Georgia" rel="noreferrer" target="_blank">Rome</a> <a href="https://www.google.com/maps/place/Dalton,+Georgia" rel="noreferrer" target="_blank">Dalton</a>'),
        '707': ('PT', 'US', 'California', '<a href="https://www.google.com/maps/place/Eureka,+California" rel="noreferrer" target="_blank">Eureka</a> <a href="https://www.google.com/maps/place/Napa,+California" rel="noreferrer" target="_blank">Napa</a> <a href="https://www.google.com/maps/place/Santa+Rosa,+California" rel="noreferrer" target="_blank">Santa Rosa</a> <a href="https://www.google.com/maps/place/Petaluma,+California" rel="noreferrer" target="_blank">Petaluma</a> <a href="https://www.google.com/maps/place/Vallejo,+California" rel="noreferrer" target="_blank">Vallejo</a>'),
        '708': ('CT', 'US', 'Illinois', '<a href="https://www.google.com/maps/place/Oak+Brook,+Illinois" rel="noreferrer" target="_blank">Oak Brook</a> <a href="https://www.google.com/maps/place/Calumet+City,+Illinois" rel="noreferrer" target="_blank">Calumet City</a> <a href="https://www.google.com/maps/place/Harvey,+Illinois" rel="noreferrer" target="_blank">Harvey</a>'),
        '709': ('NT, AST', 'Ca', 'Newfoundland and Labrador', '<a href="https://www.google.com/maps/place/Newfoundland+and+Labrador" rel="noreferrer" target="_blank">All areas</a>'),
        '712': ('CT', 'US', 'Iowa', '<a href="https://www.google.com/maps/place/Sioux+City,+Iowa" rel="noreferrer" target="_blank">Sioux City</a> <a href="https://www.google.com/maps/place/Council+Bluffs,+Iowa" rel="noreferrer" target="_blank">Council Bluffs</a> <a href="https://www.google.com/maps/place/Spencer,+Iowa" rel="noreferrer" target="_blank">Spencer</a> <a href="https://www.google.com/maps/place/Cherokee,+Iowa" rel="noreferrer" target="_blank">Cherokee</a> <a href="https://www.google.com/maps/place/Denison,+Iowa" rel="noreferrer" target="_blank">Denison</a>'),
        '713': ('CT', 'US', 'Texas', '<a href="https://www.google.com/maps/place/Houston,+Texas" rel="noreferrer" target="_blank">Houston</a>'),
        '714': ('PT', 'US', 'California', '<a href="https://www.google.com/maps/place/Anaheim,+California" rel="noreferrer" target="_blank">Anaheim</a> <a href="https://www.google.com/maps/place/Santa+Anna,+California" rel="noreferrer" target="_blank">Santa Anna</a>'),
        '715': ('CT', 'US', 'Wisconsin', '<a href="https://www.google.com/maps/place/Eau+Claire,+Wisconsin" rel="noreferrer" target="_blank">Eau Claire</a> <a href="https://www.google.com/maps/place/Wausau,+Wisconsin" rel="noreferrer" target="_blank">Wausau</a> <a href="https://www.google.com/maps/place/Stevens+Point,+Wisconsin" rel="noreferrer" target="_blank">Stevens Point</a> <a href="https://www.google.com/maps/place/Superior,+Wisconsin" rel="noreferrer" target="_blank">Superior</a>'),
        '716': ('ET', 'US', 'New York', '<a href="https://www.google.com/maps/place/Buffalo,+New+York" rel="noreferrer" target="_blank">Buffalo</a> <a href="https://www.google.com/maps/place/Niagara+Falls,+New+York" rel="noreferrer" target="_blank">Niagara Falls</a> <a href="https://www.google.com/maps/place/Tonawanda,+New+York" rel="noreferrer" target="_blank">Tonawanda</a> <a href="https://www.google.com/maps/place/Williamsville,+New+York" rel="noreferrer" target="_blank">Williamsville</a> <a href="https://www.google.com/maps/place/Jamestown,+New+York" rel="noreferrer" target="_blank">Jamestown</a> <a href="https://www.google.com/maps/place/Lancaster,+New+York" rel="noreferrer" target="_blank">Lancaster</a>'),
        '717': ('ET', 'US', 'Pennsylvania', '<a href="https://www.google.com/maps/place/Harrisburg,+Pennsylvania" rel="noreferrer" target="_blank">Harrisburg</a> <a href="https://www.google.com/maps/place/York,+Pennsylvania" rel="noreferrer" target="_blank">York</a> <a href="https://www.google.com/maps/place/Lancaster,+Pennsylvania" rel="noreferrer" target="_blank">Lancaster</a>'),
        '718': ('ET', 'US', 'New York', '<a href="https://www.google.com/maps/place/Bronx,+New+York" rel="noreferrer" target="_blank">Bronx</a> <a href="https://www.google.com/maps/place/Brooklyn,+New+York" rel="noreferrer" target="_blank">Brooklyn</a> <a href="https://www.google.com/maps/place/Queens,+New+York" rel="noreferrer" target="_blank">Queens</a> <a href="https://www.google.com/maps/place/Staten+Island,+New+York" rel="noreferrer" target="_blank">Staten Island</a>'),
        '719': ('MT', 'US', 'Colorado', '<a href="https://www.google.com/maps/place/Colorado+Springs,+Colorado" rel="noreferrer" target="_blank">Colorado Springs</a> <a href="https://www.google.com/maps/place/Pueblo,+Colorado" rel="noreferrer" target="_blank">Pueblo</a> <a href="https://www.google.com/maps/place/Lamar,+Colorado" rel="noreferrer" target="_blank">Lamar</a>'),
        '720': ('MT', 'US', 'Colorado', '<a href="https://www.google.com/maps/place/Denver,+Colorado" rel="noreferrer" target="_blank">Denver</a> <a href="https://www.google.com/maps/place/Littleton,+Colorado" rel="noreferrer" target="_blank">Littleton</a> <a href="https://www.google.com/maps/place/Englewood,+Colorado" rel="noreferrer" target="_blank">Englewood</a> <a href="https://www.google.com/maps/place/Arvada,+Colorado" rel="noreferrer" target="_blank">Arvada</a> <a href="https://www.google.com/maps/place/Boulder,+Colorado" rel="noreferrer" target="_blank">Boulder</a> <a href="https://www.google.com/maps/place/Aurora,+Colorado" rel="noreferrer" target="_blank">Aurora</a>'),
        '724': ('ET', 'US', 'Pennsylvania', '<a href="https://www.google.com/maps/place/Greensburg,+Pennsylvania" rel="noreferrer" target="_blank">Greensburg</a> <a href="https://www.google.com/maps/place/Uniontown,+Pennsylvania" rel="noreferrer" target="_blank">Uniontown</a> <a href="https://www.google.com/maps/place/Butler,+Pennsylvania" rel="noreferrer" target="_blank">Butler</a> <a href="https://www.google.com/maps/place/Washington,+Pennsylvania" rel="noreferrer" target="_blank">Washington</a> <a href="https://www.google.com/maps/place/New+Castle,+Pennsylvania" rel="noreferrer" target="_blank">New Castle</a> <a href="https://www.google.com/maps/place/Indiana,+Pennsylvania" rel="noreferrer" target="_blank">Indiana</a>'),
        '725': ('PT', 'US', 'Nevada', '<a href="https://www.google.com/maps/place/Clark+County,+Nevada" rel="noreferrer" target="_blank">almost all of Clark County</a> <a href="https://www.google.com/maps/place/including+all+of+the+Las+Vegas+Valley,+Nevada" rel="noreferrer" target="_blank">including all of the Las Vegas Valley</a> <a href="https://www.google.com/maps/place/including+Henderson+and+Boulder+City,+Nevada" rel="noreferrer" target="_blank">including Henderson and Boulder City</a>'),
        '727': ('ET', 'US', 'Florida', '<a href="https://www.google.com/maps/place/Clearwater,+Florida" rel="noreferrer" target="_blank">Clearwater</a> <a href="https://www.google.com/maps/place/St.+Petersburg,+Florida" rel="noreferrer" target="_blank">St. Petersburg</a> <a href="https://www.google.com/maps/place/New+Port+Richey,+Florida" rel="noreferrer" target="_blank">New Port Richey</a> <a href="https://www.google.com/maps/place/Tarpon+Springs,+Florida" rel="noreferrer" target="_blank">Tarpon Springs</a>'),
        '731': ('CT', 'US', 'Tennessee', '<a href="https://www.google.com/maps/place/Jackson,+Tennessee" rel="noreferrer" target="_blank">Jackson</a> <a href="https://www.google.com/maps/place/Dyersburg,+Tennessee" rel="noreferrer" target="_blank">Dyersburg</a> <a href="https://www.google.com/maps/place/Union+City,+Tennessee" rel="noreferrer" target="_blank">Union City</a> <a href="https://www.google.com/maps/place/Paris,+Tennessee" rel="noreferrer" target="_blank">Paris</a> <a href="https://www.google.com/maps/place/Brownsville,+Tennessee" rel="noreferrer" target="_blank">Brownsville</a>'),
        '732': ('ET', 'US', 'New Jersey', '<a href="https://www.google.com/maps/place/New+Brunswick,+New+Jersey" rel="noreferrer" target="_blank">New Brunswick</a> <a href="https://www.google.com/maps/place/Metuchen,+New+Jersey" rel="noreferrer" target="_blank">Metuchen</a> <a href="https://www.google.com/maps/place/Rahway,+New+Jersey" rel="noreferrer" target="_blank">Rahway</a> <a href="https://www.google.com/maps/place/Perth+Amboy,+New+Jersey" rel="noreferrer" target="_blank">Perth Amboy</a> <a href="https://www.google.com/maps/place/Toms+River,+New+Jersey" rel="noreferrer" target="_blank">Toms River</a> <a href="https://www.google.com/maps/place/Bound+Brook,+New+Jersey" rel="noreferrer" target="_blank">Bound Brook</a>'),
        '734': ('ET', 'US', 'Michigan', '<a href="https://www.google.com/maps/place/Ann+Arbor,+Michigan" rel="noreferrer" target="_blank">Ann Arbor</a> <a href="https://www.google.com/maps/place/Livonia,+Michigan" rel="noreferrer" target="_blank">Livonia</a> <a href="https://www.google.com/maps/place/Wayne,+Michigan" rel="noreferrer" target="_blank">Wayne</a> <a href="https://www.google.com/maps/place/Wyandotte,+Michigan" rel="noreferrer" target="_blank">Wyandotte</a> <a href="https://www.google.com/maps/place/Ypsilanti,+Michigan" rel="noreferrer" target="_blank">Ypsilanti</a> <a href="https://www.google.com/maps/place/Plymouth,+Michigan" rel="noreferrer" target="_blank">Plymouth</a> <a href="https://www.google.com/maps/place/Monroe,+Michigan" rel="noreferrer" target="_blank">Monroe</a>'),
        '737': ('CT', 'US', 'Texas', '<a href="https://www.google.com/maps/place/Houston,+Texas" rel="noreferrer" target="_blank">Houston</a>'),
        '740': ('ET', 'US', 'Ohio', '<a href="https://www.google.com/maps/place/Portsmouth,+Ohio" rel="noreferrer" target="_blank">Portsmouth</a> <a href="https://www.google.com/maps/place/Newark,+Ohio" rel="noreferrer" target="_blank">Newark</a> <a href="https://www.google.com/maps/place/Zanesville,+Ohio" rel="noreferrer" target="_blank">Zanesville</a> <a href="https://www.google.com/maps/place/Wheeling,+Ohio" rel="noreferrer" target="_blank">Wheeling</a> <a href="https://www.google.com/maps/place/Steubenville,+Ohio" rel="noreferrer" target="_blank">Steubenville</a>'),
        '747': ('PT', 'US', 'California', '<a href="https://www.google.com/maps/place/Van+Nuys,+California" rel="noreferrer" target="_blank">Van Nuys</a> <a href="https://www.google.com/maps/place/Canoga+Park,+California" rel="noreferrer" target="_blank">Canoga Park</a> <a href="https://www.google.com/maps/place/Burbank,+California" rel="noreferrer" target="_blank">Burbank</a> <a href="https://www.google.com/maps/place/San+Fernando,+California" rel="noreferrer" target="_blank">San Fernando</a> <a href="https://www.google.com/maps/place/Glendale,+California" rel="noreferrer" target="_blank">Glendale</a> <a href="https://www.google.com/maps/place/N.+Hollywood,+California" rel="noreferrer" target="_blank">N. Hollywood</a>'),
        '754': ('ET', 'US', 'Florida', '<a href="https://www.google.com/maps/place/Fort+Lauderdale,+Florida" rel="noreferrer" target="_blank">Fort Lauderdale</a> <a href="https://www.google.com/maps/place/Hollywood,+Florida" rel="noreferrer" target="_blank">Hollywood</a> <a href="https://www.google.com/maps/place/Pompano+Beach,+Florida" rel="noreferrer" target="_blank">Pompano Beach</a> <a href="https://www.google.com/maps/place/Deerfield+Beach,+Florida" rel="noreferrer" target="_blank">Deerfield Beach</a> <a href="https://www.google.com/maps/place/Coral+Springs,+Florida" rel="noreferrer" target="_blank">Coral Springs</a>'),
        '757': ('ET', 'US', 'Virginia', '<a href="https://www.google.com/maps/place/Norfolk,+Virginia" rel="noreferrer" target="_blank">Norfolk</a> <a href="https://www.google.com/maps/place/Newport+News,+Virginia" rel="noreferrer" target="_blank">Newport News</a> <a href="https://www.google.com/maps/place/Williamsburgh,+Virginia" rel="noreferrer" target="_blank">Williamsburgh</a>'),
        '760': ('PT', 'US', 'California', '<a href="https://www.google.com/maps/place/Oceanside,+California" rel="noreferrer" target="_blank">Oceanside</a> <a href="https://www.google.com/maps/place/Palm+Springs,+California" rel="noreferrer" target="_blank">Palm Springs</a> <a href="https://www.google.com/maps/place/Victorville,+California" rel="noreferrer" target="_blank">Victorville</a> <a href="https://www.google.com/maps/place/Escondido,+California" rel="noreferrer" target="_blank">Escondido</a> <a href="https://www.google.com/maps/place/Vista,+California" rel="noreferrer" target="_blank">Vista</a> <a href="https://www.google.com/maps/place/Palm+Desert,+California" rel="noreferrer" target="_blank">Palm Desert</a>'),
        '762': ('ET', 'US', 'Georgia', '<a href="https://www.google.com/maps/place/Augusta,+Georgia" rel="noreferrer" target="_blank">Augusta</a> <a href="https://www.google.com/maps/place/Columbus,+Georgia" rel="noreferrer" target="_blank">Columbus</a> <a href="https://www.google.com/maps/place/Athens,+Georgia" rel="noreferrer" target="_blank">Athens</a> <a href="https://www.google.com/maps/place/Rome,+Georgia" rel="noreferrer" target="_blank">Rome</a> <a href="https://www.google.com/maps/place/Dalton,+Georgia" rel="noreferrer" target="_blank">Dalton</a>'),
        '763': ('CT', 'US', 'Minnesota', '<a href="https://www.google.com/maps/place/Brooklyn+Park,+Minnesota" rel="noreferrer" target="_blank">Brooklyn Park</a> <a href="https://www.google.com/maps/place/Coon+Rapids,+Minnesota" rel="noreferrer" target="_blank">Coon Rapids</a> <a href="https://www.google.com/maps/place/Maple+Grove,+Minnesota" rel="noreferrer" target="_blank">Maple Grove</a> <a href="https://www.google.com/maps/place/Plymouth,+Minnesota" rel="noreferrer" target="_blank">Plymouth</a> <a href="https://www.google.com/maps/place/Cambridge,+Minnesota" rel="noreferrer" target="_blank">Cambridge</a> <a href="https://www.google.com/maps/place/Blaine,+Minnesota" rel="noreferrer" target="_blank">Blaine</a> <a href="https://www.google.com/maps/place/Anoka,+Minnesota" rel="noreferrer" target="_blank">Anoka</a>'),
        '765': ('ET', 'US', 'Indiana', '<a href="https://www.google.com/maps/place/Lafayette,+Indiana" rel="noreferrer" target="_blank">Lafayette</a> <a href="https://www.google.com/maps/place/Muncie,+Indiana" rel="noreferrer" target="_blank">Muncie</a> <a href="https://www.google.com/maps/place/Kokomo,+Indiana" rel="noreferrer" target="_blank">Kokomo</a> <a href="https://www.google.com/maps/place/Anderson,+Indiana" rel="noreferrer" target="_blank">Anderson</a> <a href="https://www.google.com/maps/place/Richmond,+Indiana" rel="noreferrer" target="_blank">Richmond</a> <a href="https://www.google.com/maps/place/Marion,+Indiana" rel="noreferrer" target="_blank">Marion</a>'),
        '769': ('CT', 'US', 'Mississippi', '<a href="https://www.google.com/maps/place/Jackson,+Mississippi" rel="noreferrer" target="_blank">Jackson</a> <a href="https://www.google.com/maps/place/Hattiesburg,+Mississippi" rel="noreferrer" target="_blank">Hattiesburg</a> <a href="https://www.google.com/maps/place/Vicksburg,+Mississippi" rel="noreferrer" target="_blank">Vicksburg</a> <a href="https://www.google.com/maps/place/Meridian,+Mississippi" rel="noreferrer" target="_blank">Meridian</a>'),
        '770': ('ET', 'US', 'Georgia', '<a href="https://www.google.com/maps/place/Norcross,+Georgia" rel="noreferrer" target="_blank">Norcross</a> <a href="https://www.google.com/maps/place/Chamblee,+Georgia" rel="noreferrer" target="_blank">Chamblee</a> <a href="https://www.google.com/maps/place/Smyrna,+Georgia" rel="noreferrer" target="_blank">Smyrna</a> <a href="https://www.google.com/maps/place/Tucker,+Georgia" rel="noreferrer" target="_blank">Tucker</a> <a href="https://www.google.com/maps/place/Marietta,+Georgia" rel="noreferrer" target="_blank">Marietta</a> <a href="https://www.google.com/maps/place/Alpharetta,+Georgia" rel="noreferrer" target="_blank">Alpharetta</a> <a href="https://www.google.com/maps/place/Gainesville,+Georgia" rel="noreferrer" target="_blank">Gainesville</a>'),
        '772': ('ET', 'US', 'Florida', '<a href="https://www.google.com/maps/place/Vero+Beach,+Florida" rel="noreferrer" target="_blank">Vero Beach</a> <a href="https://www.google.com/maps/place/Port+St.+Lucie,+Florida" rel="noreferrer" target="_blank">Port St. Lucie</a> <a href="https://www.google.com/maps/place/Stuart,+Florida" rel="noreferrer" target="_blank">Stuart</a> <a href="https://www.google.com/maps/place/Fort+Pierce,+Florida" rel="noreferrer" target="_blank">Fort Pierce</a> <a href="https://www.google.com/maps/place/Sebastian,+Florida" rel="noreferrer" target="_blank">Sebastian</a> <a href="https://www.google.com/maps/place/Hobe+Sound,+Florida" rel="noreferrer" target="_blank">Hobe Sound</a> <a href="https://www.google.com/maps/place/Jensen+Beach,+Florida" rel="noreferrer" target="_blank">Jensen Beach</a> <a href="https://www.google.com/maps/place/Indiantown,+Florida" rel="noreferrer" target="_blank">Indiantown</a>'),
        '773': ('CT', 'US', 'Illinois', '<a href="https://www.google.com/maps/place/Chicago,+Illinois" rel="noreferrer" target="_blank">Chicago</a>'),
        '774': ('ET', 'US', 'Massachusetts', '<a href="https://www.google.com/maps/place/Worcester,+Massachusetts" rel="noreferrer" target="_blank">Worcester</a> <a href="https://www.google.com/maps/place/Framingham,+Massachusetts" rel="noreferrer" target="_blank">Framingham</a> <a href="https://www.google.com/maps/place/Brockton,+Massachusetts" rel="noreferrer" target="_blank">Brockton</a> <a href="https://www.google.com/maps/place/Plymouth,+Massachusetts" rel="noreferrer" target="_blank">Plymouth</a> <a href="https://www.google.com/maps/place/New+Bedford,+Massachusetts" rel="noreferrer" target="_blank">New Bedford</a> <a href="https://www.google.com/maps/place/Marlboro,+Massachusetts" rel="noreferrer" target="_blank">Marlboro</a> <a href="https://www.google.com/maps/place/Natick,+Massachusetts" rel="noreferrer" target="_blank">Natick</a> <a href="https://www.google.com/maps/place/Taunton,+Massachusetts" rel="noreferrer" target="_blank">Taunton</a> <a href="https://www.google.com/maps/place/Auburn,+Massachusetts" rel="noreferrer" target="_blank">Auburn</a> <a href="https://www.google.com/maps/place/Westboro,+Massachusetts" rel="noreferrer" target="_blank">Westboro</a> <a href="https://www.google.com/maps/place/Easton,+Massachusetts" rel="noreferrer" target="_blank">Easton</a>'),
        '775': ('PT', 'US', 'Nevada', '<a href="https://www.google.com/maps/place/Reno,+Nevada" rel="noreferrer" target="_blank">Reno</a> <a href="https://www.google.com/maps/place/Carson+City,+Nevada" rel="noreferrer" target="_blank">Carson City</a>'),
        '778': ('PT', 'Ca', 'British Columbia', '<a href="https://www.google.com/maps/place/Vancouver,+British+Columbia" rel="noreferrer" target="_blank">Vancouver</a> <a href="https://www.google.com/maps/place/Richmond,+British+Columbia" rel="noreferrer" target="_blank">Richmond</a> <a href="https://www.google.com/maps/place/New+Westminster,+British+Columbia" rel="noreferrer" target="_blank">New Westminster</a>'),
        '779': ('CT', 'US', 'Illinois', '<a href="https://www.google.com/maps/place/La+Salle,+Illinois" rel="noreferrer" target="_blank">La Salle</a> <a href="https://www.google.com/maps/place/Joliet,+Illinois" rel="noreferrer" target="_blank">Joliet</a> <a href="https://www.google.com/maps/place/Rockford,+Illinois" rel="noreferrer" target="_blank">Rockford</a> <a href="https://www.google.com/maps/place/DeKalb,+Illinois" rel="noreferrer" target="_blank">DeKalb</a>'),
        '780': ('MT', 'Ca', 'Alberta', '<a href="https://www.google.com/maps/place/Edmonton,+Alberta" rel="noreferrer" target="_blank">Edmonton</a> <a href="https://www.google.com/maps/place/Fort+McMurray,+Alberta" rel="noreferrer" target="_blank">Fort McMurray</a> <a href="https://www.google.com/maps/place/Leduc,+Alberta" rel="noreferrer" target="_blank">Leduc</a> <a href="https://www.google.com/maps/place/Lloydminster,+Alberta" rel="noreferrer" target="_blank">Lloydminster</a> <a href="https://www.google.com/maps/place/Sherwood+Park,+Alberta" rel="noreferrer" target="_blank">Sherwood Park</a>'),
        '781': ('ET', 'US', 'Massachusetts', '<a href="https://www.google.com/maps/place/Waltham,+Massachusetts" rel="noreferrer" target="_blank">Waltham</a> <a href="https://www.google.com/maps/place/Lexington,+Massachusetts" rel="noreferrer" target="_blank">Lexington</a> <a href="https://www.google.com/maps/place/Burlinton,+Massachusetts" rel="noreferrer" target="_blank">Burlinton</a> <a href="https://www.google.com/maps/place/Dedham,+Massachusetts" rel="noreferrer" target="_blank">Dedham</a> <a href="https://www.google.com/maps/place/Woburn,+Massachusetts" rel="noreferrer" target="_blank">Woburn</a> <a href="https://www.google.com/maps/place/Lynn,+Massachusetts" rel="noreferrer" target="_blank">Lynn</a> <a href="https://www.google.com/maps/place/Malden,+Massachusetts" rel="noreferrer" target="_blank">Malden</a> <a href="https://www.google.com/maps/place/Saugus,+Massachusetts" rel="noreferrer" target="_blank">Saugus</a> <a href="https://www.google.com/maps/place/Reading,+Massachusetts" rel="noreferrer" target="_blank">Reading</a> <a href="https://www.google.com/maps/place/Braintree,+Massachusetts" rel="noreferrer" target="_blank">Braintree</a> <a href="https://www.google.com/maps/place/Wellesley,+Massachusetts" rel="noreferrer" target="_blank">Wellesley</a>'),
        '785': ('*CT, MT', 'US', 'Kansas', '<a href="https://www.google.com/maps/place/Topeka,+Kansas" rel="noreferrer" target="_blank">Topeka</a> <a href="https://www.google.com/maps/place/Lawrence,+Kansas" rel="noreferrer" target="_blank">Lawrence</a> <a href="https://www.google.com/maps/place/Manhattan,+Kansas" rel="noreferrer" target="_blank">Manhattan</a> <a href="https://www.google.com/maps/place/Salina,+Kansas" rel="noreferrer" target="_blank">Salina</a> <a href="https://www.google.com/maps/place/Junction,+Kansas" rel="noreferrer" target="_blank">Junction</a>'),
        '786': ('ET', 'US', 'Florida', '<a href="https://www.google.com/maps/place/Miami,+Florida" rel="noreferrer" target="_blank">Miami</a> <a href="https://www.google.com/maps/place/Perrine,+Florida" rel="noreferrer" target="_blank">Perrine</a> <a href="https://www.google.com/maps/place/Homestead,+Florida" rel="noreferrer" target="_blank">Homestead</a> <a href="https://www.google.com/maps/place/Florida+Keys,+Florida" rel="noreferrer" target="_blank">Florida Keys</a>'),
        '801': ('MST', 'US', 'Utah', '<a href="https://www.google.com/maps/place/Salt+Lake+City,+Utah" rel="noreferrer" target="_blank">Salt Lake City</a> <a href="https://www.google.com/maps/place/Provo,+Utah" rel="noreferrer" target="_blank">Provo</a> <a href="https://www.google.com/maps/place/Ogden,+Utah" rel="noreferrer" target="_blank">Ogden</a> <a href="https://www.google.com/maps/place/Orem,+Utah" rel="noreferrer" target="_blank">Orem</a> <a href="https://www.google.com/maps/place/American+Fork,+Utah" rel="noreferrer" target="_blank">American Fork</a> <a href="https://www.google.com/maps/place/Spanish+Fork,+Utah" rel="noreferrer" target="_blank">Spanish Fork</a> <a href="https://www.google.com/maps/place/Bountiful,+Utah" rel="noreferrer" target="_blank">Bountiful</a> <a href="https://www.google.com/maps/place/Kaysville,+Utah" rel="noreferrer" target="_blank">Kaysville</a> <a href="https://www.google.com/maps/place/Morgan,+Utah" rel="noreferrer" target="_blank">Morgan</a>'),
        '802': ('ET', 'US', 'Vermont', '<a href="https://www.google.com/maps/place/Vermont" rel="noreferrer" target="_blank">All areas</a>'),
        '803': ('ET', 'US', 'South Carolina', '<a href="https://www.google.com/maps/place/Columbia,+South+Carolina" rel="noreferrer" target="_blank">Columbia</a>'),
        '804': ('ET', 'US', 'Virginia', '<a href="https://www.google.com/maps/place/Richmond,+Virginia" rel="noreferrer" target="_blank">Richmond</a> <a href="https://www.google.com/maps/place/Lynchburg,+Virginia" rel="noreferrer" target="_blank">Lynchburg</a> <a href="https://www.google.com/maps/place/Petersburg,+Virginia" rel="noreferrer" target="_blank">Petersburg</a>'),
        '805': ('PT', 'US', 'California', '<a href="https://www.google.com/maps/place/Santa+Barbara,+California" rel="noreferrer" target="_blank">Santa Barbara</a> <a href="https://www.google.com/maps/place/Thousand+Oaks,+California" rel="noreferrer" target="_blank">Thousand Oaks</a> <a href="https://www.google.com/maps/place/San+Luis+Obispo,+California" rel="noreferrer" target="_blank">San Luis Obispo</a> <a href="https://www.google.com/maps/place/Ventura,+California" rel="noreferrer" target="_blank">Ventura</a> <a href="https://www.google.com/maps/place/Oxnard,+California" rel="noreferrer" target="_blank">Oxnard</a> <a href="https://www.google.com/maps/place/Simi+Valley,+California" rel="noreferrer" target="_blank">Simi Valley</a>'),
        '806': ('CT', 'US', 'Texas', '<a href="https://www.google.com/maps/place/Amarillo,+Texas" rel="noreferrer" target="_blank">Amarillo</a> <a href="https://www.google.com/maps/place/Lubbock,+Texas" rel="noreferrer" target="_blank">Lubbock</a>'),
        '807': ('*ET, CT', 'Ca', 'Ontario', '<a href="https://www.google.com/maps/place/Western+Ontario:+Thunder+Bay,+Ontario" rel="noreferrer" target="_blank">Western Ontario: Thunder Bay</a>'),
        '808': ('(UTC-10)', 'US', 'Hawaii', '<a href="https://www.google.com/maps/place/Hawaii" rel="noreferrer" target="_blank">All areas</a>'),
        '810': ('ET', 'US', 'Michigan', '<a href="https://www.google.com/maps/place/Flint,+Michigan" rel="noreferrer" target="_blank">Flint</a> <a href="https://www.google.com/maps/place/Port+Huron,+Michigan" rel="noreferrer" target="_blank">Port Huron</a> <a href="https://www.google.com/maps/place/Lapeer,+Michigan" rel="noreferrer" target="_blank">Lapeer</a> <a href="https://www.google.com/maps/place/Brighton,+Michigan" rel="noreferrer" target="_blank">Brighton</a> <a href="https://www.google.com/maps/place/Sandusky,+Michigan" rel="noreferrer" target="_blank">Sandusky</a>'),
        '812': ('*ET, CT', 'US', 'Indiana', '<a href="https://www.google.com/maps/place/Evansville,+Indiana" rel="noreferrer" target="_blank">Evansville</a> <a href="https://www.google.com/maps/place/Bloomington,+Indiana" rel="noreferrer" target="_blank">Bloomington</a> <a href="https://www.google.com/maps/place/Terre+Haute,+Indiana" rel="noreferrer" target="_blank">Terre Haute</a> <a href="https://www.google.com/maps/place/New+Albany,+Indiana" rel="noreferrer" target="_blank">New Albany</a>'),
        '813': ('ET', 'US', 'Florida', '<a href="https://www.google.com/maps/place/Tampa,+Florida" rel="noreferrer" target="_blank">Tampa</a>'),
        '814': ('ET', 'US', 'Pennsylvania', '<a href="https://www.google.com/maps/place/Erie+to+Johnstown+to+Breezewood,+Pennsylvania" rel="noreferrer" target="_blank">Erie to Johnstown to Breezewood</a> <a href="https://www.google.com/maps/place/State+College+and+Potter+County,+Pennsylvania" rel="noreferrer" target="_blank">State College and Potter County</a>'),
        '815': ('CT', 'US', 'Illinois', '<a href="https://www.google.com/maps/place/La+Salle,+Illinois" rel="noreferrer" target="_blank">La Salle</a> <a href="https://www.google.com/maps/place/Joliet,+Illinois" rel="noreferrer" target="_blank">Joliet</a> <a href="https://www.google.com/maps/place/Rockford,+Illinois" rel="noreferrer" target="_blank">Rockford</a> <a href="https://www.google.com/maps/place/DeKalb,+Illinois" rel="noreferrer" target="_blank">DeKalb</a>'),
        '816': ('CT', 'US', 'Missouri', '<a href="https://www.google.com/maps/place/Kansas+City,+Missouri" rel="noreferrer" target="_blank">Kansas City</a> <a href="https://www.google.com/maps/place/Saint+Joseph,+Missouri" rel="noreferrer" target="_blank">Saint Joseph</a> <a href="https://www.google.com/maps/place/Independence,+Missouri" rel="noreferrer" target="_blank">Independence</a> <a href="https://www.google.com/maps/place/Gladstone,+Missouri" rel="noreferrer" target="_blank">Gladstone</a>'),
        '817': ('CT', 'US', 'Texas', '<a href="https://www.google.com/maps/place/Fort+Worth,+Texas" rel="noreferrer" target="_blank">Fort Worth</a> <a href="https://www.google.com/maps/place/Arlington,+Texas" rel="noreferrer" target="_blank">Arlington</a> <a href="https://www.google.com/maps/place/Euless,+Texas" rel="noreferrer" target="_blank">Euless</a> <a href="https://www.google.com/maps/place/Grapevine,+Texas" rel="noreferrer" target="_blank">Grapevine</a>'),
        '818': ('PT', 'US', 'California', '<a href="https://www.google.com/maps/place/Van+Nuys,+California" rel="noreferrer" target="_blank">Van Nuys</a> <a href="https://www.google.com/maps/place/Canoga+Park,+California" rel="noreferrer" target="_blank">Canoga Park</a> <a href="https://www.google.com/maps/place/Burbank,+California" rel="noreferrer" target="_blank">Burbank</a> <a href="https://www.google.com/maps/place/San+Fernando,+California" rel="noreferrer" target="_blank">San Fernando</a> <a href="https://www.google.com/maps/place/Glendale,+California" rel="noreferrer" target="_blank">Glendale</a> <a href="https://www.google.com/maps/place/N.+Hollywood,+California" rel="noreferrer" target="_blank">N. Hollywood</a>'),
        '819': ('ET', 'Ca', 'Quebec', '<a href="https://www.google.com/maps/place/Hull,+Quebec" rel="noreferrer" target="_blank">Hull</a> <a href="https://www.google.com/maps/place/Sherbrooke,+Quebec" rel="noreferrer" target="_blank">Sherbrooke</a> <a href="https://www.google.com/maps/place/Trois-Riviers,+Quebec" rel="noreferrer" target="_blank">Trois-Riviers</a> <a href="https://www.google.com/maps/place/Gatineau,+Quebec" rel="noreferrer" target="_blank">Gatineau</a>'),
        '828': ('ET', 'US', 'North Carolina', '<a href="https://www.google.com/maps/place/Asheville,+North+Carolina" rel="noreferrer" target="_blank">Asheville</a> <a href="https://www.google.com/maps/place/Hickory,+North+Carolina" rel="noreferrer" target="_blank">Hickory</a> <a href="https://www.google.com/maps/place/Morganton,+North+Carolina" rel="noreferrer" target="_blank">Morganton</a> <a href="https://www.google.com/maps/place/Hendersonville,+North+Carolina" rel="noreferrer" target="_blank">Hendersonville</a> <a href="https://www.google.com/maps/place/Lenoir,+North+Carolina" rel="noreferrer" target="_blank">Lenoir</a> <a href="https://www.google.com/maps/place/Boone,+North+Carolina" rel="noreferrer" target="_blank">Boone</a> <a href="https://www.google.com/maps/place/Andrews,+North+Carolina" rel="noreferrer" target="_blank">Andrews</a> <a href="https://www.google.com/maps/place/Murphy,+North+Carolina" rel="noreferrer" target="_blank">Murphy</a> <a href="https://www.google.com/maps/place/Marble,+North+Carolina" rel="noreferrer" target="_blank">Marble</a>'),
        '830': ('CT', 'US', 'Texas', '<a href="https://www.google.com/maps/place/New+Braunfels,+Texas" rel="noreferrer" target="_blank">New Braunfels</a> <a href="https://www.google.com/maps/place/Del+Rio,+Texas" rel="noreferrer" target="_blank">Del Rio</a> <a href="https://www.google.com/maps/place/Seguin,+Texas" rel="noreferrer" target="_blank">Seguin</a> <a href="https://www.google.com/maps/place/Kerrville,+Texas" rel="noreferrer" target="_blank">Kerrville</a> <a href="https://www.google.com/maps/place/Eagle+Pass,+Texas" rel="noreferrer" target="_blank">Eagle Pass</a> <a href="https://www.google.com/maps/place/Fredericksburg,+Texas" rel="noreferrer" target="_blank">Fredericksburg</a>'),
        '831': ('PT', 'US', 'California', '<a href="https://www.google.com/maps/place/Monterey,+California" rel="noreferrer" target="_blank">Monterey</a> <a href="https://www.google.com/maps/place/Santa+Cruz,+California" rel="noreferrer" target="_blank">Santa Cruz</a> <a href="https://www.google.com/maps/place/Salinas,+California" rel="noreferrer" target="_blank">Salinas</a> <a href="https://www.google.com/maps/place/Hollister,+California" rel="noreferrer" target="_blank">Hollister</a> <a href="https://www.google.com/maps/place/Aptos,+California" rel="noreferrer" target="_blank">Aptos</a> <a href="https://www.google.com/maps/place/Carmel,+California" rel="noreferrer" target="_blank">Carmel</a>'),
        '832': ('CT', 'US', 'Texas', '<a href="https://www.google.com/maps/place/Houston,+Texas" rel="noreferrer" target="_blank">Houston</a> <a href="https://www.google.com/maps/place/Sugar+Land,+Texas" rel="noreferrer" target="_blank">Sugar Land</a> <a href="https://www.google.com/maps/place/Buffalo,+Texas" rel="noreferrer" target="_blank">Buffalo</a> <a href="https://www.google.com/maps/place/Airline,+Texas" rel="noreferrer" target="_blank">Airline</a> <a href="https://www.google.com/maps/place/Greenspoint,+Texas" rel="noreferrer" target="_blank">Greenspoint</a> <a href="https://www.google.com/maps/place/Spring,+Texas" rel="noreferrer" target="_blank">Spring</a>'),
        '843': ('ET', 'US', 'South Carolina', '<a href="https://www.google.com/maps/place/Charleston,+South+Carolina" rel="noreferrer" target="_blank">Charleston</a> <a href="https://www.google.com/maps/place/Florence,+South+Carolina" rel="noreferrer" target="_blank">Florence</a> <a href="https://www.google.com/maps/place/Myrtle+Beach,+South+Carolina" rel="noreferrer" target="_blank">Myrtle Beach</a> <a href="https://www.google.com/maps/place/Hilton+Head,+South+Carolina" rel="noreferrer" target="_blank">Hilton Head</a>'),
        '845': ('ET', 'US', 'New York', '<a href="https://www.google.com/maps/place/Poughkeepsie,+New+York" rel="noreferrer" target="_blank">Poughkeepsie</a> <a href="https://www.google.com/maps/place/Spring+Valley,+New+York" rel="noreferrer" target="_blank">Spring Valley</a> <a href="https://www.google.com/maps/place/Newburgh,+New+York" rel="noreferrer" target="_blank">Newburgh</a> <a href="https://www.google.com/maps/place/Kingston,+New+York" rel="noreferrer" target="_blank">Kingston</a> <a href="https://www.google.com/maps/place/Nyack,+New+York" rel="noreferrer" target="_blank">Nyack</a> <a href="https://www.google.com/maps/place/Middletown,+New+York" rel="noreferrer" target="_blank">Middletown</a> <a href="https://www.google.com/maps/place/Brewster,+New+York" rel="noreferrer" target="_blank">Brewster</a> <a href="https://www.google.com/maps/place/Pearl+River,+New+York" rel="noreferrer" target="_blank">Pearl River</a>'),
        '847': ('CT', 'US', 'Illinois', '<a href="https://www.google.com/maps/place/Northbrook,+Illinois" rel="noreferrer" target="_blank">Northbrook</a> <a href="https://www.google.com/maps/place/Skokie,+Illinois" rel="noreferrer" target="_blank">Skokie</a> <a href="https://www.google.com/maps/place/Evanston,+Illinois" rel="noreferrer" target="_blank">Evanston</a> <a href="https://www.google.com/maps/place/Glenview,+Illinois" rel="noreferrer" target="_blank">Glenview</a> <a href="https://www.google.com/maps/place/Waukegan,+Illinois" rel="noreferrer" target="_blank">Waukegan</a> <a href="https://www.google.com/maps/place/Desplaines,+Illinois" rel="noreferrer" target="_blank">Desplaines</a> <a href="https://www.google.com/maps/place/Elk+Grove,+Illinois" rel="noreferrer" target="_blank">Elk Grove</a>'),
        '848': ('ET', 'US', 'New Jersey', '<a href="https://www.google.com/maps/place/New+Brunswick,+New+Jersey" rel="noreferrer" target="_blank">New Brunswick</a> <a href="https://www.google.com/maps/place/Metuchen,+New+Jersey" rel="noreferrer" target="_blank">Metuchen</a> <a href="https://www.google.com/maps/place/Rahway,+New+Jersey" rel="noreferrer" target="_blank">Rahway</a> <a href="https://www.google.com/maps/place/Perth+Amboy,+New+Jersey" rel="noreferrer" target="_blank">Perth Amboy</a> <a href="https://www.google.com/maps/place/Toms+River,+New+Jersey" rel="noreferrer" target="_blank">Toms River</a> <a href="https://www.google.com/maps/place/Bound+Brook,+New+Jersey" rel="noreferrer" target="_blank">Bound Brook</a>'),
        '850': ('*ET, CT', 'US', 'Florida', '<a href="https://www.google.com/maps/place/Tallahassee,+Florida" rel="noreferrer" target="_blank">Tallahassee</a> <a href="https://www.google.com/maps/place/Pensacola,+Florida" rel="noreferrer" target="_blank">Pensacola</a> <a href="https://www.google.com/maps/place/Fort+Walton+Beach,+Florida" rel="noreferrer" target="_blank">Fort Walton Beach</a> <a href="https://www.google.com/maps/place/Panama+City,+Florida" rel="noreferrer" target="_blank">Panama City</a>'),
        '856': ('ET', 'US', 'New Jersey', '<a href="https://www.google.com/maps/place/Camden,+New+Jersey" rel="noreferrer" target="_blank">Camden</a> <a href="https://www.google.com/maps/place/Haddonfield,+New+Jersey" rel="noreferrer" target="_blank">Haddonfield</a> <a href="https://www.google.com/maps/place/Moorestown,+New+Jersey" rel="noreferrer" target="_blank">Moorestown</a> <a href="https://www.google.com/maps/place/Merchantville,+New+Jersey" rel="noreferrer" target="_blank">Merchantville</a> <a href="https://www.google.com/maps/place/Vineland,+New+Jersey" rel="noreferrer" target="_blank">Vineland</a> <a href="https://www.google.com/maps/place/Laurel+Springs,+New+Jersey" rel="noreferrer" target="_blank">Laurel Springs</a>'),
        '857': ('ET', 'US', 'Massachusetts', '<a href="https://www.google.com/maps/place/Boston,+Massachusetts" rel="noreferrer" target="_blank">Boston</a> <a href="https://www.google.com/maps/place/Cambridge,+Massachusetts" rel="noreferrer" target="_blank">Cambridge</a> <a href="https://www.google.com/maps/place/Quincy,+Massachusetts" rel="noreferrer" target="_blank">Quincy</a> <a href="https://www.google.com/maps/place/Newton,+Massachusetts" rel="noreferrer" target="_blank">Newton</a> <a href="https://www.google.com/maps/place/Brookline,+Massachusetts" rel="noreferrer" target="_blank">Brookline</a> <a href="https://www.google.com/maps/place/Brighton,+Massachusetts" rel="noreferrer" target="_blank">Brighton</a> <a href="https://www.google.com/maps/place/Somerville,+Massachusetts" rel="noreferrer" target="_blank">Somerville</a> <a href="https://www.google.com/maps/place/Dorchester,+Massachusetts" rel="noreferrer" target="_blank">Dorchester</a> <a href="https://www.google.com/maps/place/Hyde+Park,+Massachusetts" rel="noreferrer" target="_blank">Hyde Park</a> <a href="https://www.google.com/maps/place/Jamaica+Plain,+Massachusetts" rel="noreferrer" target="_blank">Jamaica Plain</a>'),
        '858': ('PT', 'US', 'California', '<a href="https://www.google.com/maps/place/La+Jolla,+California" rel="noreferrer" target="_blank">La Jolla</a> <a href="https://www.google.com/maps/place/Rancho+Bernardo,+California" rel="noreferrer" target="_blank">Rancho Bernardo</a> <a href="https://www.google.com/maps/place/del+Mar,+California" rel="noreferrer" target="_blank">del Mar</a> <a href="https://www.google.com/maps/place/Poway,+California" rel="noreferrer" target="_blank">Poway</a> <a href="https://www.google.com/maps/place/Rancho+Penasquitos,+California" rel="noreferrer" target="_blank">Rancho Penasquitos</a> <a href="https://www.google.com/maps/place/Rancho+Santa+Fe,+California" rel="noreferrer" target="_blank">Rancho Santa Fe</a>'),
        '859': ('ET', 'US', 'Kentucky', '<a href="https://www.google.com/maps/place/Lexington,+Kentucky" rel="noreferrer" target="_blank">Lexington</a> <a href="https://www.google.com/maps/place/Covington,+Kentucky" rel="noreferrer" target="_blank">Covington</a> <a href="https://www.google.com/maps/place/Boone,+Kentucky" rel="noreferrer" target="_blank">Boone</a> <a href="https://www.google.com/maps/place/Winchester,+Kentucky" rel="noreferrer" target="_blank">Winchester</a> <a href="https://www.google.com/maps/place/Richmond,+Kentucky" rel="noreferrer" target="_blank">Richmond</a> <a href="https://www.google.com/maps/place/Danville,+Kentucky" rel="noreferrer" target="_blank">Danville</a> <a href="https://www.google.com/maps/place/Mount+Sterling,+Kentucky" rel="noreferrer" target="_blank">Mount Sterling</a>'),
        '860': ('ET', 'US', 'Connecticut', '<a href="https://www.google.com/maps/place/Hartford,+Connecticut" rel="noreferrer" target="_blank">Hartford</a> <a href="https://www.google.com/maps/place/New+London,+Connecticut" rel="noreferrer" target="_blank">New London</a> <a href="https://www.google.com/maps/place/Norwich,+Connecticut" rel="noreferrer" target="_blank">Norwich</a> <a href="https://www.google.com/maps/place/Middletown,+Connecticut" rel="noreferrer" target="_blank">Middletown</a> <a href="https://www.google.com/maps/place/Bristol,+Connecticut" rel="noreferrer" target="_blank">Bristol</a>'),
        '862': ('ET', 'US', 'New Jersey', '<a href="https://www.google.com/maps/place/Newark,+New+Jersey" rel="noreferrer" target="_blank">Newark</a> <a href="https://www.google.com/maps/place/Morristown,+New+Jersey" rel="noreferrer" target="_blank">Morristown</a> <a href="https://www.google.com/maps/place/Paterson,+New+Jersey" rel="noreferrer" target="_blank">Paterson</a> <a href="https://www.google.com/maps/place/Passaic,+New+Jersey" rel="noreferrer" target="_blank">Passaic</a> <a href="https://www.google.com/maps/place/Orange,+New+Jersey" rel="noreferrer" target="_blank">Orange</a> <a href="https://www.google.com/maps/place/Bloomfield,+New+Jersey" rel="noreferrer" target="_blank">Bloomfield</a> <a href="https://www.google.com/maps/place/Caldwell,+New+Jersey" rel="noreferrer" target="_blank">Caldwell</a> <a href="https://www.google.com/maps/place/Whippany,+New+Jersey" rel="noreferrer" target="_blank">Whippany</a>'),
        '863': ('ET', 'US', 'Florida', '<a href="https://www.google.com/maps/place/Lakeland,+Florida" rel="noreferrer" target="_blank">Lakeland</a> <a href="https://www.google.com/maps/place/Winter+Haven,+Florida" rel="noreferrer" target="_blank">Winter Haven</a> <a href="https://www.google.com/maps/place/Lake+Wales,+Florida" rel="noreferrer" target="_blank">Lake Wales</a> <a href="https://www.google.com/maps/place/Sebring,+Florida" rel="noreferrer" target="_blank">Sebring</a> <a href="https://www.google.com/maps/place/Haines+City,+Florida" rel="noreferrer" target="_blank">Haines City</a> <a href="https://www.google.com/maps/place/Bartow,+Florida" rel="noreferrer" target="_blank">Bartow</a> <a href="https://www.google.com/maps/place/Avon+Park,+Florida" rel="noreferrer" target="_blank">Avon Park</a> <a href="https://www.google.com/maps/place/Okeechobee,+Florida" rel="noreferrer" target="_blank">Okeechobee</a> <a href="https://www.google.com/maps/place/Wachula,+Florida" rel="noreferrer" target="_blank">Wachula</a>'),
        '864': ('ET', 'US', 'South Carolina', '<a href="https://www.google.com/maps/place/Greenville,+South+Carolina" rel="noreferrer" target="_blank">Greenville</a> <a href="https://www.google.com/maps/place/Spartanburg,+South+Carolina" rel="noreferrer" target="_blank">Spartanburg</a> <a href="https://www.google.com/maps/place/Anderson,+South+Carolina" rel="noreferrer" target="_blank">Anderson</a>'),
        '865': ('ET', 'US', 'Tennessee', '<a href="https://www.google.com/maps/place/Knoxville,+Tennessee" rel="noreferrer" target="_blank">Knoxville</a> <a href="https://www.google.com/maps/place/Maryville,+Tennessee" rel="noreferrer" target="_blank">Maryville</a> <a href="https://www.google.com/maps/place/Oak+Ridge,+Tennessee" rel="noreferrer" target="_blank">Oak Ridge</a> <a href="https://www.google.com/maps/place/Sevierville,+Tennessee" rel="noreferrer" target="_blank">Sevierville</a> <a href="https://www.google.com/maps/place/Gatlinburg,+Tennessee" rel="noreferrer" target="_blank">Gatlinburg</a> <a href="https://www.google.com/maps/place/Concord,+Tennessee" rel="noreferrer" target="_blank">Concord</a> <a href="https://www.google.com/maps/place/Powell,+Tennessee" rel="noreferrer" target="_blank">Powell</a>'),
        '867': ('*CT, MT, PT', 'Ca', 'Yukon, Northwest Territories, and Nunavut', '<a href="https://www.google.com/maps/place/Whitehorse,+Yukon,+Northwest+Territories,+and+Nunavut" rel="noreferrer" target="_blank">Whitehorse</a> <a href="https://www.google.com/maps/place/Yellow+Knife,+Yukon,+Northwest+Territories,+and+Nunavut" rel="noreferrer" target="_blank">Yellow Knife</a> <a href="https://www.google.com/maps/place/Nunavut,+Yukon,+Northwest+Territories,+and+Nunavut" rel="noreferrer" target="_blank">Nunavut</a>'),
        '870': ('CT', 'US', 'Arkansas', '<a href="https://www.google.com/maps/place/Texarkana,+Arkansas" rel="noreferrer" target="_blank">Texarkana</a> <a href="https://www.google.com/maps/place/Jonesboro,+Arkansas" rel="noreferrer" target="_blank">Jonesboro</a> <a href="https://www.google.com/maps/place/Pine+Bluff,+Arkansas" rel="noreferrer" target="_blank">Pine Bluff</a> <a href="https://www.google.com/maps/place/El+Dorado,+Arkansas" rel="noreferrer" target="_blank">El Dorado</a>'),
        '872': ('CT', 'US', 'Illinois', '<a href="https://www.google.com/maps/place/Chicago+(Downtown+area),+Illinois" rel="noreferrer" target="_blank">Chicago (Downtown area)</a> <a href="https://www.google.com/maps/place/Wheeling,+Illinois" rel="noreferrer" target="_blank">Wheeling</a>'),
        '873': ('ET', 'Ca', 'Quebec', '<a href="https://www.google.com/maps/place/,+Quebec" rel="noreferrer" target="_blank"></a>'),
        '878': ('ET', 'US', 'Pennsylvania', '<a href="https://www.google.com/maps/place/Pittsburgh,+Pennsylvania" rel="noreferrer" target="_blank">Pittsburgh</a> <a href="https://www.google.com/maps/place/Greensburg,+Pennsylvania" rel="noreferrer" target="_blank">Greensburg</a> <a href="https://www.google.com/maps/place/Uniontown,+Pennsylvania" rel="noreferrer" target="_blank">Uniontown</a> <a href="https://www.google.com/maps/place/Butler,+Pennsylvania" rel="noreferrer" target="_blank">Butler</a> <a href="https://www.google.com/maps/place/Washington,+Pennsylvania" rel="noreferrer" target="_blank">Washington</a> <a href="https://www.google.com/maps/place/New+Castle,+Pennsylvania" rel="noreferrer" target="_blank">New Castle</a> <a href="https://www.google.com/maps/place/Indiana,+Pennsylvania" rel="noreferrer" target="_blank">Indiana</a>'),
        '901': ('CT', 'US', 'Tennessee', '<a href="https://www.google.com/maps/place/Memphis,+Tennessee" rel="noreferrer" target="_blank">Memphis</a> <a href="https://www.google.com/maps/place/Collierville,+Tennessee" rel="noreferrer" target="_blank">Collierville</a>'),
        '902': ('AT', 'Ca', 'Nova Scotia, Prince Edward Island', '<a href="https://www.google.com/maps/place/Nova+Scotia,+Prince+Edward+Island" rel="noreferrer" target="_blank">All areas</a>'),
        '903': ('CT', 'US', 'Texas', '<a href="https://www.google.com/maps/place/Longview,+Texas" rel="noreferrer" target="_blank">Longview</a> <a href="https://www.google.com/maps/place/Tyler,+Texas" rel="noreferrer" target="_blank">Tyler</a> <a href="https://www.google.com/maps/place/Texarkana,+Texas" rel="noreferrer" target="_blank">Texarkana</a> <a href="https://www.google.com/maps/place/Paris,+Texas" rel="noreferrer" target="_blank">Paris</a> <a href="https://www.google.com/maps/place/Kilgore,+Texas" rel="noreferrer" target="_blank">Kilgore</a> <a href="https://www.google.com/maps/place/Sherman,+Texas" rel="noreferrer" target="_blank">Sherman</a> <a href="https://www.google.com/maps/place/Denison,+Texas" rel="noreferrer" target="_blank">Denison</a>'),
        '904': ('ET', 'US', 'Florida', '<a href="https://www.google.com/maps/place/Jacksonville,+Florida" rel="noreferrer" target="_blank">Jacksonville</a> <a href="https://www.google.com/maps/place/Saint+Augustine,+Florida" rel="noreferrer" target="_blank">Saint Augustine</a> <a href="https://www.google.com/maps/place/Orange+Park,+Florida" rel="noreferrer" target="_blank">Orange Park</a> <a href="https://www.google.com/maps/place/Fernandina+Beach,+Florida" rel="noreferrer" target="_blank">Fernandina Beach</a>'),
        '905': ('ET', 'Ca', 'Ontario', '<a href="https://www.google.com/maps/place/Hamilton,+Ontario" rel="noreferrer" target="_blank">Hamilton</a> <a href="https://www.google.com/maps/place/Niagara+Falls,+Ontario" rel="noreferrer" target="_blank">Niagara Falls</a> <a href="https://www.google.com/maps/place/Markham,+Ontario" rel="noreferrer" target="_blank">Markham</a> <a href="https://www.google.com/maps/place/Mississauga,+Ontario" rel="noreferrer" target="_blank">Mississauga</a> <a href="https://www.google.com/maps/place/Brampton,+Ontario" rel="noreferrer" target="_blank">Brampton</a>'),
        '906': ('*ET, CT', 'US', 'Michigan', '<a href="https://www.google.com/maps/place/Marquette,+Michigan" rel="noreferrer" target="_blank">Marquette</a> <a href="https://www.google.com/maps/place/Iron+Mountain,+Michigan" rel="noreferrer" target="_blank">Iron Mountain</a> <a href="https://www.google.com/maps/place/Houghton,+Michigan" rel="noreferrer" target="_blank">Houghton</a> <a href="https://www.google.com/maps/place/Sault+Ste+Marie,+Michigan" rel="noreferrer" target="_blank">Sault Ste Marie</a>'),
        '907': ('(UTC-9)', 'US', 'Alaska', '<a href="https://www.google.com/maps/place/Alaska" rel="noreferrer" target="_blank">All areas</a>'),
        '908': ('ET', 'US', 'New Jersey', '<a href="https://www.google.com/maps/place/Elizabeth,+New+Jersey" rel="noreferrer" target="_blank">Elizabeth</a> <a href="https://www.google.com/maps/place/New+Brunswick,+New+Jersey" rel="noreferrer" target="_blank">New Brunswick</a> <a href="https://www.google.com/maps/place/Somerville,+New+Jersey" rel="noreferrer" target="_blank">Somerville</a> <a href="https://www.google.com/maps/place/Freehold,+New+Jersey" rel="noreferrer" target="_blank">Freehold</a> <a href="https://www.google.com/maps/place/Unionville,+New+Jersey" rel="noreferrer" target="_blank">Unionville</a> <a href="https://www.google.com/maps/place/Plainfield,+New+Jersey" rel="noreferrer" target="_blank">Plainfield</a>'),
        '909': ('PT', 'US', 'California', '<a href="https://www.google.com/maps/place/San+Bernardino,+California" rel="noreferrer" target="_blank">San Bernardino</a> <a href="https://www.google.com/maps/place/Ontario,+California" rel="noreferrer" target="_blank">Ontario</a> <a href="https://www.google.com/maps/place/Upland,+California" rel="noreferrer" target="_blank">Upland</a> <a href="https://www.google.com/maps/place/Pomona,+California" rel="noreferrer" target="_blank">Pomona</a> <a href="https://www.google.com/maps/place/Riverside,+California" rel="noreferrer" target="_blank">Riverside</a> <a href="https://www.google.com/maps/place/Colton,+California" rel="noreferrer" target="_blank">Colton</a> <a href="https://www.google.com/maps/place/Chino,+California" rel="noreferrer" target="_blank">Chino</a>'),
        '910': ('ET', 'US', 'North Carolina', '<a href="https://www.google.com/maps/place/Fayetteville,+North+Carolina" rel="noreferrer" target="_blank">Fayetteville</a> <a href="https://www.google.com/maps/place/Wilmington,+North+Carolina" rel="noreferrer" target="_blank">Wilmington</a> <a href="https://www.google.com/maps/place/Jacksonville,+North+Carolina" rel="noreferrer" target="_blank">Jacksonville</a> <a href="https://www.google.com/maps/place/Lumberton,+North+Carolina" rel="noreferrer" target="_blank">Lumberton</a> <a href="https://www.google.com/maps/place/Laurinburg,+North+Carolina" rel="noreferrer" target="_blank">Laurinburg</a> <a href="https://www.google.com/maps/place/Southern+Pines,+North+Carolina" rel="noreferrer" target="_blank">Southern Pines</a>'),
        '912': ('ET', 'US', 'Georgia', '<a href="https://www.google.com/maps/place/Savannah,+Georgia" rel="noreferrer" target="_blank">Savannah</a> <a href="https://www.google.com/maps/place/Macon,+Georgia" rel="noreferrer" target="_blank">Macon</a> <a href="https://www.google.com/maps/place/Waycross,+Georgia" rel="noreferrer" target="_blank">Waycross</a> <a href="https://www.google.com/maps/place/Brunswick,+Georgia" rel="noreferrer" target="_blank">Brunswick</a> <a href="https://www.google.com/maps/place/Statesboro,+Georgia" rel="noreferrer" target="_blank">Statesboro</a> <a href="https://www.google.com/maps/place/Vidalia,+Georgia" rel="noreferrer" target="_blank">Vidalia</a>'),
        '913': ('CT', 'US', 'Kansas', '<a href="https://www.google.com/maps/place/Melrose,+Kansas" rel="noreferrer" target="_blank">Melrose</a> <a href="https://www.google.com/maps/place/Kansas+City,+Kansas" rel="noreferrer" target="_blank">Kansas City</a>'),
        '914': ('ET', 'US', 'New York', '<a href="https://www.google.com/maps/place/Westchester,+New+York" rel="noreferrer" target="_blank">Westchester</a> <a href="https://www.google.com/maps/place/Monroe,+New+York" rel="noreferrer" target="_blank">Monroe</a> <a href="https://www.google.com/maps/place/Mount+Vernon,+New+York" rel="noreferrer" target="_blank">Mount Vernon</a> <a href="https://www.google.com/maps/place/Mount+Kisco,+New+York" rel="noreferrer" target="_blank">Mount Kisco</a> <a href="https://www.google.com/maps/place/Pleasantville,+New+York" rel="noreferrer" target="_blank">Pleasantville</a>'),
        '915': ('*CT, MT', 'US', 'Texas', '<a href="https://www.google.com/maps/place/El+Paso,+Texas" rel="noreferrer" target="_blank">El Paso</a> <a href="https://www.google.com/maps/place/Socorro,+Texas" rel="noreferrer" target="_blank">Socorro</a> <a href="https://www.google.com/maps/place/Fabens,+Texas" rel="noreferrer" target="_blank">Fabens</a> <a href="https://www.google.com/maps/place/Dell+City,+Texas" rel="noreferrer" target="_blank">Dell City</a> <a href="https://www.google.com/maps/place/Van+Horn,+Texas" rel="noreferrer" target="_blank">Van Horn</a> <a href="https://www.google.com/maps/place/Fort+Bliss,+Texas" rel="noreferrer" target="_blank">Fort Bliss</a>'),
        '916': ('PT', 'US', 'California', '<a href="https://www.google.com/maps/place/Sacramento,+California" rel="noreferrer" target="_blank">Sacramento</a> <a href="https://www.google.com/maps/place/Roseville,+California" rel="noreferrer" target="_blank">Roseville</a> <a href="https://www.google.com/maps/place/Fair+Oaks,+California" rel="noreferrer" target="_blank">Fair Oaks</a> <a href="https://www.google.com/maps/place/Folsom,+California" rel="noreferrer" target="_blank">Folsom</a> <a href="https://www.google.com/maps/place/Elk+Grove,+California" rel="noreferrer" target="_blank">Elk Grove</a> <a href="https://www.google.com/maps/place/South+Placer,+California" rel="noreferrer" target="_blank">South Placer</a>'),
        '917': ('ET', 'US', 'New York', '<a href="https://www.google.com/maps/place/New+York+City+(Manhattan+only),+New+York" rel="noreferrer" target="_blank">New York City (Manhattan only)</a> <a href="https://www.google.com/maps/place/New+York+City+(Bronx,+New+York" rel="noreferrer" target="_blank">New York City (Bronx</a> <a href="https://www.google.com/maps/place/Brooklyn,+New+York" rel="noreferrer" target="_blank">Brooklyn</a> <a href="https://www.google.com/maps/place/Queens,+New+York" rel="noreferrer" target="_blank">Queens</a> <a href="https://www.google.com/maps/place/Staten+Island),+New+York" rel="noreferrer" target="_blank">Staten Island)</a>'),
        '918': ('CT', 'US', 'Oklahoma', '<a href="https://www.google.com/maps/place/Tulsa,+Oklahoma" rel="noreferrer" target="_blank">Tulsa</a> <a href="https://www.google.com/maps/place/Broken+Arrow,+Oklahoma" rel="noreferrer" target="_blank">Broken Arrow</a> <a href="https://www.google.com/maps/place/Muskogee,+Oklahoma" rel="noreferrer" target="_blank">Muskogee</a> <a href="https://www.google.com/maps/place/Bartlesville,+Oklahoma" rel="noreferrer" target="_blank">Bartlesville</a> <a href="https://www.google.com/maps/place/McAlester,+Oklahoma" rel="noreferrer" target="_blank">McAlester</a>'),
        '919': ('ET', 'US', 'North Carolina', '<a href="https://www.google.com/maps/place/Raleigh,+North+Carolina" rel="noreferrer" target="_blank">Raleigh</a> <a href="https://www.google.com/maps/place/Durham,+North+Carolina" rel="noreferrer" target="_blank">Durham</a> <a href="https://www.google.com/maps/place/Cary,+North+Carolina" rel="noreferrer" target="_blank">Cary</a> <a href="https://www.google.com/maps/place/Chapel+Hill,+North+Carolina" rel="noreferrer" target="_blank">Chapel Hill</a> <a href="https://www.google.com/maps/place/Goldsboro,+North+Carolina" rel="noreferrer" target="_blank">Goldsboro</a> <a href="https://www.google.com/maps/place/Apex,+North+Carolina" rel="noreferrer" target="_blank">Apex</a> <a href="https://www.google.com/maps/place/Sanford,+North+Carolina" rel="noreferrer" target="_blank">Sanford</a> <a href="https://www.google.com/maps/place/Wake+Forest,+North+Carolina" rel="noreferrer" target="_blank">Wake Forest</a>'),
        '920': ('CT', 'US', 'Wisconsin', '<a href="https://www.google.com/maps/place/Green+Bay,+Wisconsin" rel="noreferrer" target="_blank">Green Bay</a> <a href="https://www.google.com/maps/place/Appleton,+Wisconsin" rel="noreferrer" target="_blank">Appleton</a> <a href="https://www.google.com/maps/place/Racine,+Wisconsin" rel="noreferrer" target="_blank">Racine</a> <a href="https://www.google.com/maps/place/Fond+du+Lac,+Wisconsin" rel="noreferrer" target="_blank">Fond du Lac</a> <a href="https://www.google.com/maps/place/Oshkosh,+Wisconsin" rel="noreferrer" target="_blank">Oshkosh</a> <a href="https://www.google.com/maps/place/Sheboygan,+Wisconsin" rel="noreferrer" target="_blank">Sheboygan</a>'),
        '925': ('PT', 'US', 'California', '<a href="https://www.google.com/maps/place/Walnut+Creek,+California" rel="noreferrer" target="_blank">Walnut Creek</a> <a href="https://www.google.com/maps/place/Pleasanton,+California" rel="noreferrer" target="_blank">Pleasanton</a> <a href="https://www.google.com/maps/place/Concord,+California" rel="noreferrer" target="_blank">Concord</a> <a href="https://www.google.com/maps/place/Livermore,+California" rel="noreferrer" target="_blank">Livermore</a> <a href="https://www.google.com/maps/place/Bishop+Ranch,+California" rel="noreferrer" target="_blank">Bishop Ranch</a> <a href="https://www.google.com/maps/place/Danville,+California" rel="noreferrer" target="_blank">Danville</a> <a href="https://www.google.com/maps/place/Antioch,+California" rel="noreferrer" target="_blank">Antioch</a>'),
        '928': ('MT', 'US', 'Arizona', '<a href="https://www.google.com/maps/place/Yuma,+Arizona" rel="noreferrer" target="_blank">Yuma</a> <a href="https://www.google.com/maps/place/Flagstaff,+Arizona" rel="noreferrer" target="_blank">Flagstaff</a> <a href="https://www.google.com/maps/place/Prescott,+Arizona" rel="noreferrer" target="_blank">Prescott</a> <a href="https://www.google.com/maps/place/Sedona,+Arizona" rel="noreferrer" target="_blank">Sedona</a> <a href="https://www.google.com/maps/place/Bullhead+City,+Arizona" rel="noreferrer" target="_blank">Bullhead City</a> <a href="https://www.google.com/maps/place/Kingman,+Arizona" rel="noreferrer" target="_blank">Kingman</a> <a href="https://www.google.com/maps/place/Lake+Havasu+City,+Arizona" rel="noreferrer" target="_blank">Lake Havasu City</a>'),
        '929': ('ET', 'US', 'New York', '<a href="https://www.google.com/maps/place/,+New+York" rel="noreferrer" target="_blank"></a>'),
        '931': ('ET, CT', 'US', 'Tennessee', '<a href="https://www.google.com/maps/place/Clarksville,+Tennessee" rel="noreferrer" target="_blank">Clarksville</a> <a href="https://www.google.com/maps/place/Shelbyville,+Tennessee" rel="noreferrer" target="_blank">Shelbyville</a> <a href="https://www.google.com/maps/place/Cookeville,+Tennessee" rel="noreferrer" target="_blank">Cookeville</a> <a href="https://www.google.com/maps/place/Columbia,+Tennessee" rel="noreferrer" target="_blank">Columbia</a>'),
        '936': ('CT', 'US', 'Texas', '<a href="https://www.google.com/maps/place/Conroe,+Texas" rel="noreferrer" target="_blank">Conroe</a> <a href="https://www.google.com/maps/place/Nacogdoches,+Texas" rel="noreferrer" target="_blank">Nacogdoches</a> <a href="https://www.google.com/maps/place/Huntsville,+Texas" rel="noreferrer" target="_blank">Huntsville</a> <a href="https://www.google.com/maps/place/Lufkin,+Texas" rel="noreferrer" target="_blank">Lufkin</a> <a href="https://www.google.com/maps/place/Madisonville,+Texas" rel="noreferrer" target="_blank">Madisonville</a>'),
        '937': ('ET', 'US', 'Ohio', '<a href="https://www.google.com/maps/place/Dayton,+Ohio" rel="noreferrer" target="_blank">Dayton</a> <a href="https://www.google.com/maps/place/Springfield,+Ohio" rel="noreferrer" target="_blank">Springfield</a> <a href="https://www.google.com/maps/place/Bellefontaine,+Ohio" rel="noreferrer" target="_blank">Bellefontaine</a> <a href="https://www.google.com/maps/place/Beavercreek,+Ohio" rel="noreferrer" target="_blank">Beavercreek</a> <a href="https://www.google.com/maps/place/Franklin,+Ohio" rel="noreferrer" target="_blank">Franklin</a>'),
        '938': ('CT', 'US', 'Alabama', '<a href="https://www.google.com/maps/place/Huntsville,+Alabama" rel="noreferrer" target="_blank">Huntsville</a> <a href="https://www.google.com/maps/place/Anniston,+Alabama" rel="noreferrer" target="_blank">Anniston</a> <a href="https://www.google.com/maps/place/Cullman,+Alabama" rel="noreferrer" target="_blank">Cullman</a> <a href="https://www.google.com/maps/place/Decatur,+Alabama" rel="noreferrer" target="_blank">Decatur</a> <a href="https://www.google.com/maps/place/Florence,+Alabama" rel="noreferrer" target="_blank">Florence</a> <a href="https://www.google.com/maps/place/Fort+Payne,+Alabama" rel="noreferrer" target="_blank">Fort Payne</a> <a href="https://www.google.com/maps/place/Gadsden,+Alabama" rel="noreferrer" target="_blank">Gadsden</a> <a href="https://www.google.com/maps/place/Madison,+Alabama" rel="noreferrer" target="_blank">Madison</a> <a href="https://www.google.com/maps/place/Sheffield,+Alabama" rel="noreferrer" target="_blank">Sheffield</a> <a href="https://www.google.com/maps/place/Tuscumbia,+Alabama" rel="noreferrer" target="_blank">Tuscumbia</a>'),
        '940': ('CT', 'US', 'Texas', '<a href="https://www.google.com/maps/place/Wichita+Falls,+Texas" rel="noreferrer" target="_blank">Wichita Falls</a> <a href="https://www.google.com/maps/place/Denton,+Texas" rel="noreferrer" target="_blank">Denton</a> <a href="https://www.google.com/maps/place/Gainesville,+Texas" rel="noreferrer" target="_blank">Gainesville</a>'),
        '941': ('ET', 'US', 'Florida', '<a href="https://www.google.com/maps/place/Sarasota,+Florida" rel="noreferrer" target="_blank">Sarasota</a> <a href="https://www.google.com/maps/place/Bradenton,+Florida" rel="noreferrer" target="_blank">Bradenton</a> <a href="https://www.google.com/maps/place/Venice,+Florida" rel="noreferrer" target="_blank">Venice</a> <a href="https://www.google.com/maps/place/Port+Charlotte,+Florida" rel="noreferrer" target="_blank">Port Charlotte</a> <a href="https://www.google.com/maps/place/Punta+Gorda,+Florida" rel="noreferrer" target="_blank">Punta Gorda</a>'),
        '947': ('ET', 'US', 'Michigan', '<a href="https://www.google.com/maps/place/Troy,+Michigan" rel="noreferrer" target="_blank">Troy</a> <a href="https://www.google.com/maps/place/Pontiac,+Michigan" rel="noreferrer" target="_blank">Pontiac</a> <a href="https://www.google.com/maps/place/Royal+Oak,+Michigan" rel="noreferrer" target="_blank">Royal Oak</a> <a href="https://www.google.com/maps/place/Birmingham,+Michigan" rel="noreferrer" target="_blank">Birmingham</a> <a href="https://www.google.com/maps/place/Rochester,+Michigan" rel="noreferrer" target="_blank">Rochester</a> <a href="https://www.google.com/maps/place/Farmington+Hills,+Michigan" rel="noreferrer" target="_blank">Farmington Hills</a>'),
        '949': ('PT', 'US', 'California', '<a href="https://www.google.com/maps/place/Irvine,+California" rel="noreferrer" target="_blank">Irvine</a> <a href="https://www.google.com/maps/place/Saddleback+Valley,+California" rel="noreferrer" target="_blank">Saddleback Valley</a> <a href="https://www.google.com/maps/place/Newport+Beach,+California" rel="noreferrer" target="_blank">Newport Beach</a> <a href="https://www.google.com/maps/place/Capistrano+Valley,+California" rel="noreferrer" target="_blank">Capistrano Valley</a> <a href="https://www.google.com/maps/place/Laguna+Beach,+California" rel="noreferrer" target="_blank">Laguna Beach</a>'),
        '951': ('PT', 'US', 'California', '<a href="https://www.google.com/maps/place/Riverside,+California" rel="noreferrer" target="_blank">Riverside</a> <a href="https://www.google.com/maps/place/Corona,+California" rel="noreferrer" target="_blank">Corona</a> <a href="https://www.google.com/maps/place/Temecula,+California" rel="noreferrer" target="_blank">Temecula</a> <a href="https://www.google.com/maps/place/Arlington,+California" rel="noreferrer" target="_blank">Arlington</a> <a href="https://www.google.com/maps/place/Hemet,+California" rel="noreferrer" target="_blank">Hemet</a> <a href="https://www.google.com/maps/place/Moreno+Valley,+California" rel="noreferrer" target="_blank">Moreno Valley</a> <a href="https://www.google.com/maps/place/Murietta,+California" rel="noreferrer" target="_blank">Murietta</a> <a href="https://www.google.com/maps/place/Sun+City,+California" rel="noreferrer" target="_blank">Sun City</a> <a href="https://www.google.com/maps/place/Elsinore,+California" rel="noreferrer" target="_blank">Elsinore</a>'),
        '952': ('CT', 'US', 'Minnesota', '<a href="https://www.google.com/maps/place/Bloomington,+Minnesota" rel="noreferrer" target="_blank">Bloomington</a> <a href="https://www.google.com/maps/place/Burnsville,+Minnesota" rel="noreferrer" target="_blank">Burnsville</a> <a href="https://www.google.com/maps/place/Eden+Prairie,+Minnesota" rel="noreferrer" target="_blank">Eden Prairie</a> <a href="https://www.google.com/maps/place/Minnetonka,+Minnesota" rel="noreferrer" target="_blank">Minnetonka</a> <a href="https://www.google.com/maps/place/Edina,+Minnesota" rel="noreferrer" target="_blank">Edina</a> <a href="https://www.google.com/maps/place/St.+Louis+Park,+Minnesota" rel="noreferrer" target="_blank">St. Louis Park</a> <a href="https://www.google.com/maps/place/Apple+Valley,+Minnesota" rel="noreferrer" target="_blank">Apple Valley</a>'),
        '954': ('ET', 'US', 'Florida', '<a href="https://www.google.com/maps/place/Fort+Lauderdale,+Florida" rel="noreferrer" target="_blank">Fort Lauderdale</a> <a href="https://www.google.com/maps/place/Hollywood,+Florida" rel="noreferrer" target="_blank">Hollywood</a> <a href="https://www.google.com/maps/place/Pompano+Beach,+Florida" rel="noreferrer" target="_blank">Pompano Beach</a> <a href="https://www.google.com/maps/place/Deerfield+Beach,+Florida" rel="noreferrer" target="_blank">Deerfield Beach</a> <a href="https://www.google.com/maps/place/Coral+Springs,+Florida" rel="noreferrer" target="_blank">Coral Springs</a>'),
        '956': ('CT', 'US', 'Texas', '<a href="https://www.google.com/maps/place/Brownsville,+Texas" rel="noreferrer" target="_blank">Brownsville</a> <a href="https://www.google.com/maps/place/Laredo,+Texas" rel="noreferrer" target="_blank">Laredo</a> <a href="https://www.google.com/maps/place/McAllen,+Texas" rel="noreferrer" target="_blank">McAllen</a> <a href="https://www.google.com/maps/place/Harlingen,+Texas" rel="noreferrer" target="_blank">Harlingen</a> <a href="https://www.google.com/maps/place/Edinburg,+Texas" rel="noreferrer" target="_blank">Edinburg</a>'),
        '970': ('MT', 'US', 'Colorado', '<a href="https://www.google.com/maps/place/Fort+Collins,+Colorado" rel="noreferrer" target="_blank">Fort Collins</a> <a href="https://www.google.com/maps/place/Greeley,+Colorado" rel="noreferrer" target="_blank">Greeley</a> <a href="https://www.google.com/maps/place/Grand+Junction,+Colorado" rel="noreferrer" target="_blank">Grand Junction</a> <a href="https://www.google.com/maps/place/Loveland,+Colorado" rel="noreferrer" target="_blank">Loveland</a> <a href="https://www.google.com/maps/place/Durango,+Colorado" rel="noreferrer" target="_blank">Durango</a> <a href="https://www.google.com/maps/place/Vail,+Colorado" rel="noreferrer" target="_blank">Vail</a>'),
        '971': ('PT', 'US', 'Oregon', '<a href="https://www.google.com/maps/place/Portland,+Oregon" rel="noreferrer" target="_blank">Portland</a> <a href="https://www.google.com/maps/place/Salem,+Oregon" rel="noreferrer" target="_blank">Salem</a> <a href="https://www.google.com/maps/place/Beaverton,+Oregon" rel="noreferrer" target="_blank">Beaverton</a> <a href="https://www.google.com/maps/place/Gresham,+Oregon" rel="noreferrer" target="_blank">Gresham</a> <a href="https://www.google.com/maps/place/Hillsboro,+Oregon" rel="noreferrer" target="_blank">Hillsboro</a>'),
        '972': ('CT', 'US', 'Texas', '<a href="https://www.google.com/maps/place/Grand+Prairie,+Texas" rel="noreferrer" target="_blank">Grand Prairie</a> <a href="https://www.google.com/maps/place/Addison,+Texas" rel="noreferrer" target="_blank">Addison</a> <a href="https://www.google.com/maps/place/Irving,+Texas" rel="noreferrer" target="_blank">Irving</a> <a href="https://www.google.com/maps/place/Richardson,+Texas" rel="noreferrer" target="_blank">Richardson</a> <a href="https://www.google.com/maps/place/Plano,+Texas" rel="noreferrer" target="_blank">Plano</a> <a href="https://www.google.com/maps/place/Carrollton,+Texas" rel="noreferrer" target="_blank">Carrollton</a>'),
        '973': ('ET', 'US', 'New Jersey', '<a href="https://www.google.com/maps/place/Newark,+New+Jersey" rel="noreferrer" target="_blank">Newark</a> <a href="https://www.google.com/maps/place/Morristown,+New+Jersey" rel="noreferrer" target="_blank">Morristown</a> <a href="https://www.google.com/maps/place/Paterson,+New+Jersey" rel="noreferrer" target="_blank">Paterson</a> <a href="https://www.google.com/maps/place/Passaic,+New+Jersey" rel="noreferrer" target="_blank">Passaic</a> <a href="https://www.google.com/maps/place/Orange,+New+Jersey" rel="noreferrer" target="_blank">Orange</a> <a href="https://www.google.com/maps/place/Bloomfield,+New+Jersey" rel="noreferrer" target="_blank">Bloomfield</a> <a href="https://www.google.com/maps/place/Caldwell,+New+Jersey" rel="noreferrer" target="_blank">Caldwell</a> <a href="https://www.google.com/maps/place/Whippany,+New+Jersey" rel="noreferrer" target="_blank">Whippany</a>'),
        '978': ('ET', 'US', 'Massachusetts', '<a href="https://www.google.com/maps/place/Lowell,+Massachusetts" rel="noreferrer" target="_blank">Lowell</a> <a href="https://www.google.com/maps/place/Lawrence,+Massachusetts" rel="noreferrer" target="_blank">Lawrence</a> <a href="https://www.google.com/maps/place/Billerica,+Massachusetts" rel="noreferrer" target="_blank">Billerica</a> <a href="https://www.google.com/maps/place/Concord,+Massachusetts" rel="noreferrer" target="_blank">Concord</a> <a href="https://www.google.com/maps/place/Wilmington,+Massachusetts" rel="noreferrer" target="_blank">Wilmington</a> <a href="https://www.google.com/maps/place/Sudbury,+Massachusetts" rel="noreferrer" target="_blank">Sudbury</a> <a href="https://www.google.com/maps/place/Fitchburg,+Massachusetts" rel="noreferrer" target="_blank">Fitchburg</a> <a href="https://www.google.com/maps/place/Peabody,+Massachusetts" rel="noreferrer" target="_blank">Peabody</a> <a href="https://www.google.com/maps/place/Andover,+Massachusetts" rel="noreferrer" target="_blank">Andover</a> <a href="https://www.google.com/maps/place/Beverly,+Massachusetts" rel="noreferrer" target="_blank">Beverly</a> <a href="https://www.google.com/maps/place/Danvers,+Massachusetts" rel="noreferrer" target="_blank">Danvers</a>'),
        '979': ('CT', 'US', 'Texas', '<a href="https://www.google.com/maps/place/Bryan,+Texas" rel="noreferrer" target="_blank">Bryan</a> <a href="https://www.google.com/maps/place/Lake+Jackson,+Texas" rel="noreferrer" target="_blank">Lake Jackson</a> <a href="https://www.google.com/maps/place/Freeport,+Texas" rel="noreferrer" target="_blank">Freeport</a> <a href="https://www.google.com/maps/place/Brenham,+Texas" rel="noreferrer" target="_blank">Brenham</a> <a href="https://www.google.com/maps/place/Bay+City,+Texas" rel="noreferrer" target="_blank">Bay City</a> <a href="https://www.google.com/maps/place/El+Campo,+Texas" rel="noreferrer" target="_blank">El Campo</a>'),
        '980': ('ET', 'US', 'North Carolina', '<a href="https://www.google.com/maps/place/Charlotte,+North+Carolina" rel="noreferrer" target="_blank">Charlotte</a> <a href="https://www.google.com/maps/place/Asheville,+North+Carolina" rel="noreferrer" target="_blank">Asheville</a> <a href="https://www.google.com/maps/place/Gastonia,+North+Carolina" rel="noreferrer" target="_blank">Gastonia</a> <a href="https://www.google.com/maps/place/Concord,+North+Carolina" rel="noreferrer" target="_blank">Concord</a> <a href="https://www.google.com/maps/place/Statesville,+North+Carolina" rel="noreferrer" target="_blank">Statesville</a> <a href="https://www.google.com/maps/place/Salisbury,+North+Carolina" rel="noreferrer" target="_blank">Salisbury</a> <a href="https://www.google.com/maps/place/Shelby,+North+Carolina" rel="noreferrer" target="_blank">Shelby</a> <a href="https://www.google.com/maps/place/Monroe,+North+Carolina" rel="noreferrer" target="_blank">Monroe</a>'),
        '984': ('ET', 'US', 'North Carolina', '<a href="https://www.google.com/maps/place/Raleigh,+North+Carolina" rel="noreferrer" target="_blank">Raleigh</a>'),
        '985': ('CT', 'US', 'Louisiana', '<a href="https://www.google.com/maps/place/Houma,+Louisiana" rel="noreferrer" target="_blank">Houma</a> <a href="https://www.google.com/maps/place/Slidell,+Louisiana" rel="noreferrer" target="_blank">Slidell</a> <a href="https://www.google.com/maps/place/Hammond,+Louisiana" rel="noreferrer" target="_blank">Hammond</a> <a href="https://www.google.com/maps/place/Morgan+City,+Louisiana" rel="noreferrer" target="_blank">Morgan City</a> <a href="https://www.google.com/maps/place/Mandeville,+Louisiana" rel="noreferrer" target="_blank">Mandeville</a> <a href="https://www.google.com/maps/place/Covington,+Louisiana" rel="noreferrer" target="_blank">Covington</a> <a href="https://www.google.com/maps/place/Thibodaux,+Louisiana" rel="noreferrer" target="_blank">Thibodaux</a> <a href="https://www.google.com/maps/place/Bogalusa,+Louisiana" rel="noreferrer" target="_blank">Bogalusa</a> <a href="https://www.google.com/maps/place/St.+Charles,+Louisiana" rel="noreferrer" target="_blank">St. Charles</a>'),
        '989': ('ET', 'US', 'Michigan', '<a href="https://www.google.com/maps/place/Saginaw,+Michigan" rel="noreferrer" target="_blank">Saginaw</a> <a href="https://www.google.com/maps/place/Bay+City,+Michigan" rel="noreferrer" target="_blank">Bay City</a> <a href="https://www.google.com/maps/place/Midland,+Michigan" rel="noreferrer" target="_blank">Midland</a> <a href="https://www.google.com/maps/place/Mount+Pleasant,+Michigan" rel="noreferrer" target="_blank">Mount Pleasant</a>'),
        '800': ('', 'US', 'Toll-free', ''),
        '888': ('', 'US', 'Toll-free', ''),
        '877': ('', 'US', 'Toll-free', ''),
        '844': ('', 'US', 'Toll-free', ''),
        '855': ('', 'US', 'Toll-free', ''),
        '866': ('', 'US', 'Toll-free', '')}

RSS_URLS = [
    'http://buyandsellhair.com/ad-category/hair-for-sale/feed/',
    'http://abileneguntrader.com/feed/?post_type=ad_listing',
    'http://absolute-forum.com/external.php?type=RSS2&forumids=11',
    'http://battlebornclassifieds.com/feed/?post_type=ad_listing',
    'http://cnc-professional-forum.com/external.php?s=8bdcccc2c6dd232d54e0f1284004a6d5&type=RSS2&forumids=159',
    'https://siouxcityjournal.com/ads/?f=rss&s=start_time&sd=asc',
    'https://fremonttribune.com/ads/?f=rss&s=start_time&sd=asc',
    'https://www.pantagraph.com/ads/?f=rss&s=start_time&sd=asc',
    'https://classifieds.villages-news.com/feed?post_type=ad_listing',
    'http://eaaforums.org/external.php?type=RSS2&forumids=15',
    'http://fishsniffer.com/forums/external.php?type=RSS2&forumids=14',
    'http://forestryforum.com/board/index.php?action=.xml;board=21;type=rss',
    'http://forum.grrrr8.net/external.php?s=7692bae2d7b333ecb6a51181560d6503&type=RSS2&forumids=97',
    'http://forums.13x.com/index.php?forums/bikes-for-sale.48/index.rss',
    'http://forums.pcper.com/external.php?s=129e0b02e9c3beee4ccb56299bab6530&type=RSS2&forumids=3',
    'http://forums.roadbikereview.com/external.php?type=RSS2&forumids=131',
    'http://jamboards.com/forums/longboard-surf-buy-sell-trade.8/index.rss',
    'http://motownmuscle.com/forums/external.php?type=RSS2&forumids=8',
    'http://news.thesunontheweb.com/current/classifieds/feed',
    'http://onlinehairaffair.com/feed/?post_type=ad_listing',
    'http://wetpixel.com/forums/index.php?app=core&module=global&section=rss&type=forums&id=1',
    'http://willysforsale.com/ad-category/willys-civilian-jeep-models/feed/',
    'http://www.acmoc.org/bb/external.php?s=0b1715d7632dcc742cedc667e9e66486&type=RSS2&forumids=5',
    'http://www.arrowheadology.com/forums/external.php?type=RSS2&forumids=29',
    'http://www.bigpumpkins.com/RSS/MessageBoard.rss?2',
    'http://www.birdphotographers.net/forums/external.php?s=2eeee583073d57c89087044aa836a0cf&type=RSS2&forumids=14',
    'http://www.cavediver.net/forum/external.php?type=RSS2&forumids=9',
    'http://www.cowboyway.com/classifieds/rss_listings.php',
    'http://www.fountainpennetwork.com/forum/index.php/rss/classifieds/',
    'http://www.gatewaycobraclub.com/forums/external.php?s=cfabd0a8f95a3139c00277acac89dc85&type=RSS2&forumids=16',
    'http://www.houstonfishbox.com/vforums/external.php?s=82097de59ba12d883c116678f933c7a1&type=RSS2&forumids=93',
    'http://www.insect-deal.com/rss.php?cmd=syndication&subcmd=productauctions&sid=10&version=2.0&limit=25',
    'http://www.kentuckyhunting.net/forum/classifieds.28/index.rss',
    'http://www.kyclassifieds.com/ad-category/appliances/feed/',
    'http://www.kyclassifieds.com/ad-category/farm-animals/feed/',
    'http://www.kyclassifieds.com/ad-category/musical-instruments/feed/',
    'http://www.kyclassifieds.com/ad-category/rv-campers/feed/',
    'http://www.kyclassifieds.com/ad-category/wanted/feed/',
    'http://www.lancisti.net/forum/external.php?s=ac2e128ead9eeb1f49ad6547d7ca0b66&type=RSS2&forumids=24',
    'http://www.manitoulinmall.com/feed/?post_type=ad_listing',
    'http://www.muppetcentral.com/forum/forums/puppets-for-sale/index.rss',
    'http://www.nobleforums.com/external.php?s=9dc1a2515fcddee9af12fa723c2d2ee9&type=RSS2&forumids=9',
    'http://www.pyrofan.com/forum/external.php?s=dde75e8e655cd5e8f697d4fa7b83b392&type=RSS2&forumids=104',
    'http://www.ranchero.us/forum/index.php?forums/ranchero-parts-wanted.7/index.rss',
    'http://www.ranchero.us/forum/index.php?forums/rancheros-for-sale.5/index.rss',
    'http://www.rednewsonline.com/feed/?post_type=ad_listing',
    'http://www.spyderlovers.com/forums/external.php?s=48235bbf8d49381d67369e632b12ed3a&type=RSS2&forumids=7',
    'http://www.trackforum.com/forums/external.php?s=cdb9bf32ad21d8ddc92b9e96daf6e6c4&type=RSS2&forumids=28',
    'http://www.treasurenet.com/forums/external.php?type=RSS2&forumids=200',
    'http://www.v8buick.com/index.php?forums/cars-wanted.46/index.rss',
    'http://www.v8buick.com/index.php?forums/parts-for-sale.44/index.rss',
    'http://www.ybw.com/forums/external.php?type=RSS2&forumids=18',
    'https://americandrivingsociety.org/Members/Classifieds/ctl/RSS/mid/21884/evl/0/CategoryID/62/CategoryName/For-Sale',
    'https://austincountybuyandsell.com/feed/?post_type=ad_listing',
    'https://cadillacmagazine.com/forums/forums/for-sale-wanted.4/index.rss',
    'https://classifiedscachevalley.com/feed/?post_type=ad_listing',
    'https://community.cardboardconnection.com/forums/external?type=rss2&nodeid=26',
    'https://dronesflip.com/feed/?post_type=ad_listing',
    'https://emtlife.com/forums/for-sale.30/index.rss',
    'https://www.hemmings.com/rss/keyword.xml',
    'https://equipifieds.com/ad-category/mining/feed/',
    'https://forum.dealerrefresh.com/forums/automotive-industry-jobs-classifieds.47/index.rss',
    'https://forum.dealerrefresh.com/forums/im-angry-and-need-to-gripe.21/index.rss',
    'https://forum.dealerrefresh.com/forums/im-available-for-hire.58/index.rss',
    'https://forum.dealerrefresh.com/forums/webinars-broadcasts-live-broadcast-podcasts.82/index.rss',
    'https://forum.missouriquiltco.com/external.php?type=RSS2&forumids=26',
    'https://forum.xnxx.com/forums/personals.5/index.rss',
    'https://forums.collectors.com/categories/buy-sell-trade-u-s-coins/feed.rss',
    'https://forums.sixpackspeak.com/external.php?s=cd34e48f84175485d87c51e566dc9207&type=RSS2&forumids=8',
    'https://forums.watchuseek.com/external.php?type=RSS2&forumids=31',
    'https://forums.woodnet.net/syndication.php?fid=4',
    'https://fpgeeks.com/forum/external.php?type=RSS2&forumids=8',
    'https://goldenskate.com/forum/external.php?s=1d62060ce3ca5784210500c8c99d166a&type=RSS2&forumids=115',
    'https://hairopia.com/ad-category/hair-for-sale/feed/',
    'https://kalspage.com/feed/?post_type=ad_listing',
    'https://nikonites.com/external.php?type=RSS2&forumids=80',
    'https://forum.n2td.org/index.php?forums/parts-and-accessories/index.rss',
    'https://forum.n2td.org/index.php?forums/track-days-for-sale-or-wanted/index.rss',
    'https://3drpilots.com/forums/classifieds.13/index.rss',
    'https://www.kingdaddycaddy.com/forums/cars-for-sale.29/index.rss',
    'http://classifieds.reviewjournal.com/nv/pets-livestock/rss.xml?lat=36.17497&lng=-115.13722',
    'http://classifieds.reviewjournal.com/nv/merchandise/rss.xml?lat=36.17497&lng=-115.13722',
    'https://p8ntballer-forums.com/forums/for-sale.55/index.rss',
    'https://purdue.forums.rivals.com/forums/free-board-ticket-forum.14/index.rss',
    'https://stolen911.com/stolen-property/recovered-property/feed/',
    'https://teamtac.org/e107/e107_plugins/rss_menu/rss.php?6.2',
    'https://theadminzone.com/forums/classifieds.29/index.rss',
    'https://thefactoryfiveforum.com/external.php?s=43ec0bb9e61d5161daefe608492c41f5&type=RSS2&forumids=33',
    'https://thefactoryfiveforum.com/external.php?type=RSS2&forumids=32',
    'https://useddogwheelchairs.com/feed/?post_type=ad_listing',
    'https://weldingweb.com/external.php?type=RSS2&forumids=42',
    'https://www.aapc.com/memberarea/forums/external.php?type=RSS2&forumids=457&s=bb02c1a80078bdff2ac555048bb791b1',
    'https://www.antique-bottles.net/external.php?s=0ec473dd7203cc15898cae75a923a627&type=RSS2&forumids=12',
    'https://www.autotechnician.org/classifieds/feed/',
    'https://www.bayoushooter.com/forums/external.php?s=89ac84a8344f1058b0e1db6631a226b8&type=RSS2&forumids=12',
    'https://www.bimmerforums.com/forum/external.php?s=5ee0118bf0ad6e68f3791553189bca17&type=RSS2&forumids=369',
    'https://www.bookweb.org/taxonomy/term/152/feed',
    'https://www.buysaleandtrade.com/rss_listings.php',
    'https://www.cloudynights.com/rss/classifieds/',
    'https://www.cointalk.com/forums/for-sale/index.rss',
    'https://www.cointalk.com/forums/wanted/index.rss',
    'https://www.collegenet.com/elect/app/app?service=SyndicationService&sp=2&sp=SSYND_RSS_2_0&sp=0',
    'https://www.farms.com/Portals/_default/RSS_Portal/Classifieds_All.xml',
    'https://www.filmgearclassifieds.com/feed/?post_type=ad_listing',
    'https://www.halloweenforum.com/external.php?type=RSS2&forumids=148',
    'https://www.hammockforums.net/forum/external.php?s=39034741b184c0be0aee34d58682ec54&type=RSS2&forumids=154',
    'https://www.hammockforums.net/forum/external.php?s=39034741b184c0be0aee34d58682ec54&type=RSS2&forumids=29',
    'https://www.hipforums.com/forum/forum/165-for-sale-or-trade/index.rss',
    'https://www.hipforums.com/forum/forum/166-help-wanted/index.rss',
    'https://www.indianmotorcycles.net/forums/parts-for-sale-wanted.23/index.rss ',
    'https://www.kiastinger.org/forum/external.php?s=55f25ba9fda15f389c4f8e67fa724c2b&type=RSS2&forumids=7',
    'https://www.lawnsite.com/forums/marketplace.51/index.rss',
    'https://www.longhorncattlesociety.com/news/rss.xml',
    'https://www.lpsg.com/forums/personal-ads.38/index.rss',
    'https://www.marcopoloownersclub.com/index.php?forums/2nd-hand-accessories-for-sale.18/index.rss',
    'https://www.n-ssa.net/vbforum/external.php?type=RSS2&forumids=7',
    'https://www.oldminibikes.com/forum/external.php?type=RSS2&forumids=68&s=d52a4d2e9f806634eeb5ef45891e82fc',
    'https://www.ppfacorner.com/external.php?s=1da18afb2fa7808e675f02599b05a797&type=RSS2&forumids=9',
    'https://www.practicalmachinist.com/vb/external.php?type=RSS2&forumids=12',
    'https://www.practicalmachinist.com/vb/external.php?type=RSS2&forumids=40',
    'https://www.belltreeforums.com/external.php?s=58afd96d65e859e198ff5fa432c5bf71&type=RSS2&forumids=81',
    'http://www.muppetcentral.com/forum/forums/puppets-for-sale/index.rss',
    'http://jeffersoncountypost.com/?feed=rss2&cat=61',
    'https://www.farmanddairy.com/classifieds/feed',
    'http://www.blackforestbroadcasting.com/?feed=rss2',
    'https://www.rokslide.com/forums/external.php?type=RSS2&forumids=88',
    'https://www.salmonfishingforum.com/forums/external.php?type=RSS2&forumids=34&s=8d9435b1db47d165a1c57ee9d0f69ebe',
    'https://www.slingshotcommunity.com/forums/Sales-Trades-Wanted/index.rss',
    'https://www.talkclassical.com/external.php?type=RSS2&forumids=26',
    'https://www.taxidermy.net/forums/4/index.rss',
    'https://www.thefastlaneforum.com/community/forums/fastlane-marketplace.64/index.rss',
    'https://www.thehackersparadise.com/forum/external.php?type=RSS2&forumids=25',
    'https://www.themerchantette.com/feed/?post_type=ad_listing',
    'https://www.thetruckersreport.com/truckingindustryforum/forums/315/index.rss',
    'https://www.ummah.com/forum/external?type=rss2&nodeid=79',
    'http://abileneguntrader.com/feed/?post_type=ad_listing',
    'http://jamboards.com/forums/longboard-surf-buy-sell-trade.8/index.rss',
    'http://motownmuscle.com/forums/external.php?type=RSS2&forumids=8',
    'http://www.acmoc.org/bb/external.php?s=0b1715d7632dcc742cedc667e9e66486&type=RSS2&forumids=5',
    'http://www.nobleforums.com/external.php?s=9dc1a2515fcddee9af12fa723c2d2ee9&type=RSS2&forumids=9',
    'http://www.ranchero.us/forum/index.php?forums/rancheros-for-sale.5/index.rss',
    'https://classifiedscachevalley.com/feed/?post_type=ad_listing',
    'https://forums.sixpackspeak.com/external.php?s=cd34e48f84175485d87c51e566dc9207&type=RSS2&forumids=8',
    'https://www.buysaleandtrade.com/rss_listings.php',
    'https://www.cadillacforums.com/forums/external.php?type=RSS2',
    'https://www.flyinggiants.com/forums/external.php?type=RSS2',
    'https://www.indianmotorcycles.net/forums/parts-for-sale-wanted.23/index.rss',
    'http://www.bayarearidersforum.com/forums/external.php?type=RSS2&forumids=74',
    'http://www.bayarearidersforum.com/forums/external.php?type=RSS2&forumids=104',
    'http://www.bayarearidersforum.com/forums/external.php?type=RSS2&forumids=10',
    'http://doityourselfchristmas.com/forums/external.php?type=RSS2&forumids=25',
    'https://www.f150ecoboost.net/forum/external.php?type=RSS2&forumids=23',
    'http://www.reduser.net/forum/external.php?type=RSS2&forumids=69',
    'http://forum.pafoa.org/external.php?type=RSS2&forumids=7',
    'https://www.theflyfishingforum.com/forums/external.php?type=RSS2&forumids=88',
    'https://www.badgerandblade.com/forum/forums/buy-sell-trade.246/index.rss',
    'https://www.farmforum.net/classifieds/?f=rss&s=start_time&sd=asc',
    'http://www.centerpintalk.com/forum/external.php?type=RSS2&forumids=9',
    'https://www.clubsnap.com/forums/buy-sell-other-camera-brands-formats.117/index.rss',
    'https://tvwbb.com/external.php?type=RSS2&forumids=106',
    'https://www.icscc.com/forums/external.php?type=RSS2&forumids=10',
    'https://bantamtalk.com/index.php?forums/city-for-sale-or-wanted.29/index.rss',
    'https://cafesaxophone.com/forums/saxophones-for-sale/index.rss',
    'https://saddlehunter.com/community/index.php?forums/classifieds.18.rss',
    'http://www.mtbnj.com/forum/forums/bikes-for-sale.20/index.rss',
    'https://threads.dappered.com/external.php?type=RSS2&forumids=18',
    'https://www.cyclechat.net/forums/exchange-free.23/index.rss']

first = ['Michael', 'Christopher', 'Jason', 'David', 'James', 'Matthew', 'Joshua', 'John', 'Robert', 'Joseph',
         'Daniel', 'Brian', 'Justin', 'William', 'Ryan', 'Eric', 'Nicholas', 'Jeremy', 'Andrew', 'Timothy', 'Jonathan',
         'Adam', 'Kevin', 'Anthony', 'Thomas', 'Richard', 'Jeffrey', 'Steven', 'Charles', 'Brandon', 'Mark', 'Benjamin',
         'Scott',
         'Aaron', 'Paul', 'Nathan', 'Travis', 'Patrick', 'Chad', 'Stephen', 'Kenneth', 'Gregory', 'Jacob', 'Dustin',
         'Jesse', 'Jose',
         'Shawn', 'Sean', 'Bryan', 'Derek', 'Bradley', 'Edward', 'Donald', 'Samuel', 'Peter', 'Keith', 'Kyle', 'Ronald',
         'Juan',
         'George', 'Jared', 'Douglas', 'Gary', 'Erik', 'Phillip', 'Joel', 'Raymond', 'Corey', 'Shane', 'Larry',
         'Marcus', 'Zachary',
         'Craig', 'Derrick', 'Todd', 'Jeremiah', 'Carlos', 'Antonio', 'Shaun', 'Dennis', 'Frank', 'Philip', 'Cory',
         'Brent',
         'Nathaniel', 'Gabriel', 'Randy', 'Luis', 'Curtis', 'Jeffery', 'Alexander', 'Russell', 'Casey', 'Jerry',
         'Wesley',
         'Brett', 'Luke', 'Lucas', 'Seth', 'Billy', 'Terry', 'Carl', 'Mario', 'Ian', 'Jamie', 'Troy', 'Victor', 'Bobby',
         'Tony',
         'Vincent', 'Jesus', 'Alan', 'Johnny', 'Tyler', 'Adrian', 'Brad', 'Ricardo', 'Marc', 'Christian', 'Danny',
         'Rodney', 'Ricky',
         'Martin', 'Allen', 'Jimmy', 'Lee', 'Jon', 'Willie', 'Lawrence', 'Miguel', 'Clinton', 'Micheal', 'Andre',
         'Roger',
         'Henry', 'Randall', 'Kristopher', 'Walter', 'Jorge', 'Joe', 'Jay', 'Albert', 'Cody', 'Manuel', 'Roberto',
         'Wayne', 'Arthur',
         'Gerald', 'Jermaine', 'Isaac', 'Louis', 'Lance', 'Roy', 'Francisco', 'Trevor', 'Alex', 'Bruce', 'Evan',
         'Jordan',
         'Jack', 'Frederick', 'Maurice', 'Darren', 'Mitchell', 'Ruben', 'Reginald', 'Darrell', 'Jaime', 'Hector',
         'Omar', 'Jonathon',
         'Angel', 'Ronnie', 'Johnathan', 'Barry', 'Oscar', 'Eddie', 'Jerome', 'Terrance', 'Ernest', 'Neil', 'Damien',
         'Mathew',
         'Shannon', 'Calvin', 'Javier', 'Edwin', 'Alejandro', 'Eugene', 'Garrett', 'Raul', 'Kurt', 'Clint', 'Clayton',
         'Leonard',
         'Fernando', 'Tommy', 'Dale', 'Geoffrey', 'Marvin']

last = ['Banks', 'Jackson', 'Mosley', 'Dorsey', 'Gaines', 'Rivers', 'Mack', 'Singleton', 'Williams', 'Branch',
        'Robinson',
        'Ware', 'Coleman', 'Roberson', 'Harris', 'Glover', 'Houston', 'Mcneil', 'Hinton', 'Hampton', 'Flowers', 'Sims',
        'Wiggins', 'Mays', 'Dixon', 'Franklin', 'Jones', 'Tate', 'Randolph', 'Grant', 'Holmes', 'Love', 'Green',
        'Frazier',
        'Jenkins', 'Gamble', 'Hines', 'Holloway', 'Simmons', 'Fields', 'Stokes', 'Carter', 'Bryant', 'Woods', 'Brown',
        'Curry',
        'Byrd', 'Walker', 'Mcknight', 'Lewis', 'Johnson', 'Woodard', 'Walton', 'Henderson', 'Richardson', 'Brooks',
        'Hunter',
        'Ingram', 'Hawkins', 'Reid', 'Haynes', 'Bullock', 'Sanders', 'Calhoun', 'Miles', 'Bell', 'Mcclain', 'Hardy',
        'Mathis',
        'Mitchell', 'Ford', 'Watkins', 'Dickerson', 'Neal', 'Butler', 'Davis', 'Tyler', 'Mcgee', 'Boone', 'Pollard',
        'Pitts', 'Knox',
        'Edwards', 'Wilkins', 'Pittman', 'Boyd', 'Nixon', 'Griffin', 'Stevenson', 'Solomon', 'Matthews', 'Turner',
        'Sampson',
        'Monroe', 'Wilkerson', 'Henry', 'Howard', 'Oneal', 'Bradford', 'Hill', 'Wiley', 'Floyd', 'Barnes', 'Clarke',
        'Wade',
        'Blackwell', 'Owens', 'Gibbs', 'Reese', 'Mccall', 'Taylor', 'Ellison', 'Francis', 'Freeman', 'White', 'Wright',
        'Copeland',
        'Gordon', 'Logan', 'Gilmore', 'Middleton', 'Beasley', 'Dudley', 'Pugh', 'Chambers', 'Moore', 'Watson', 'Oliver',
        'Terry',
        'Thornton', 'Dennis', 'Collier', 'Mccoy', 'Marshall', 'Hudson', 'Mckenzie', 'Hicks', 'Giles', 'Burton',
        'Malone', 'Powell',
        'Patterson', 'Harper', 'Spears', 'Saunders', 'Caldwell', 'Bridges', 'Montgomery', 'Greene', 'Atkins', 'Austin',
        'Wilson',
        'Cooper', 'Sheppard', 'Dawson', 'Strong', 'Allen', 'Rollins', 'Odom', 'Evans', 'Townsend', 'Walls', 'Watts',
        'Mclean',
        'Prince', 'Waller', 'Lindsey', 'Clayton', 'Mason', 'Crawford', 'Mcmillan', 'Porter', 'Bradley', 'Perry', 'Gray',
        'Mckinney',
        'Hodge', 'Parks', 'Cobb', 'Norman', 'Harvey', 'Moss', 'Parker', 'Daniel', 'Hayes', 'Benton', 'Maddox',
        'Perkins',
        'Mcdowell', 'Stewart', 'Young', 'Harrison', 'Bass', 'Wallace', 'Cannon', 'Tucker', 'Garrett', 'Graves', 'Nash',
        'Galloway']

company = ['Exxon Mobil', 'General Motors', 'Chevron', 'General Electric', 'Boeing',
           'International Business Machines', 'Johnson & Johnson', 'Procter & Gamble', 'PepsiCo', 'DowDuPont',
           'Archer Daniels Midland',
           'United Technologies', 'Pfizer', 'Lockheed Martin', 'Caterpillar', 'Honeywell International', 'Merck',
           'Coca-Cola',
           'ConocoPhillips', '3M', 'General Dynamics', 'Deere', 'Abbott Laboratories', 'Kraft Heinz',
           'Northrop Grumman', 'Raytheon',
           'International Paper', 'Eli Lilly', 'Whirlpool', 'Bristol-Myers Squibb', 'Cummins', 'Altria Group', 'Paccar',
           'Kimberly-Clark',
           'General Mills', 'Colgate-Palmolive', 'Goodyear Tire & Rubber', 'PPG Industries', 'Textron', 'Arconic',
           'Kellogg',
           'Hormel Foods', 'Crown Holdings', 'Campbell Soup', 'Hershey', 'Dana', 'Weyerhaeuser', 'Owens-Illinois',
           'Owens Corning',
           'Motorola Solutions', 'Rockwell Automation', 'Wal-Mart Stores, Inc', 'Exxon Mobil Corporation',
           'Chevron Corporation',
           'Berkshire Hathaway Inc.', 'Apple Inc.', 'General Motors Company', 'Phillips 66', 'General Electric Company',
           'Ford Motor Company',
           'CVS Health', 'McKesson Corporation', 'AT&T', 'Valero Marketing and Supply Company', 'UnitedHealth Group',
           'Verizon Communications Inc.', 'AmerisourceBergen', 'Federal National Mortgage Association (Fannie Mae)',
           'Costco Wholesale Corporation', 'Hewlett-Packard', 'The Kroger Co.', 'JPMorgan Chase & Co.',
           'Express Scripts Holding Company',
           'International Business Machines Corporation', 'Marathon Petroleum Company', 'Cardinal Health',
           'The Boeing Company', 'Citigroup Incorporated',
           'Wells Fargo & Company', 'Microsoft Corporation', 'The Procter & Gamble Company', 'The Home Depot, Inc',
           'Archer Daniels Midland Company', 'Walgreens', 'Target Corporation, Inc.', 'Anthem, Inc.', 'MetLife Inc.',
           'Google, Inc.', 'State Farm Insurance',
           'Freddie Mac', 'Comcast Corporation', 'PepsiCo, Inc.', 'American International Group (AIG)',
           'United Parcel Service, Inc.', 'The Dow Chemical Company', 'Aetna, Inc.', "Lowe's Companies, Inc.",
           'Energy Transfer Partners, L.P.',
           'Caterpillar Inc.', 'Prudential Financial, Incorporated', 'Pfizer Incorporated', 'The Walt Disney Company',
           'Humana Inc.',
           'Enterprise Products Partners L.P.', 'Cisco Systems, Inc.', 'SYSCO Corporation', 'Ingram Micro Inc.',
           'The Coca-Cola Company', 'Lockheed Martin Corporation', 'FedEx Corporation', 'Johnson Controls, Inc.',
           'Plains All American Pipeline, L.P.', 'World Fuel Services Corporation', 'CHS, Inc.', 'American Airlines',
           'Merck & Co., Inc.',
           'Best Buy Co. Inc.', 'Delta Air Lines, Inc.', 'Honeywell', 'Honeywell International Inc.',
           'HCA Holdings, Inc.',
           'Goldman Sachs', 'Andeavor, Inc.', 'Liberty Mutual Insurance Company', 'United Continental Holdings',
           'New York Life Insurance Company', 'Oracle Corporation', 'Morgan Stanley', 'Tyson Foods, Inc.',
           'Safeway, Inc.',
           'Nationwide Mutual Insurance Company', 'John Deere Company', 'DuPont', 'American Express Company',
           'Allstate Insurance Company',
           'CIGNA Corporation', 'Mondelez International Inc', 'TIAA-CREF', 'INTL FCStone Inc.',
           'Massachusetts Mutual Financial Group',
           'DIRECTV', 'Halliburton Company', '21st Century Fox', '3M Company', 'Sears Holdings Corporation',
           'General Dynamics Corporation', 'Publix Super Markets, Inc.', 'Philip Morris International', 'Edward Jones',
           'Avery Dennison Corporation', 'NetApp, Inc.', 'Discovery Communications, Inc.', 'Harley-Davidson, Inc.',
           'Sanmina Corporation',
           'Trinity Industries, Inc.', 'J.B. Hunt Transport Services, Incorporated', 'The Charles Schwab Corporation',
           'Erie Indemnity Company',
           'Dr Pepper Snapple Group', 'Ameren Corporation', 'Mattel, Inc.',
           'Laboratory Corporation of America Holdings',
           'Gannett Co., Inc.', 'General Cable Corporation', 'A-Mark Precious Metals, Inc.',
           'Graybar Electric Inc.', 'Vistra Energy', 'MRC Global Inc.', 'Enbridge Inc.',
           'Asbury Automotive Group, Inc.',
           'Packaging Corporation of America', 'Windstream Communications', 'PULTEGROUP, INC.',
           'JetBlue Airways Corporation', 'Newell Brands',
           'XPO Logistics, Inc.', 'Calumet Specialty Products Partners L.P.', 'Expedia',
           'American Financial Group, Inc.',
           'Tractor Supply Company', 'United Rentals, Inc.', 'Ingredion Incorporated', 'Navient Solutions, LLC',
           'St. Jude Medical, Inc.',
           'The J. M. Smucker Company', 'Western Union Company', 'The Clorox Company',
           'The H V Food Products Company', 'Domtar Corp.', 'Kelly Services, Inc.',
           'Old Republic International Corporation',
           'Advanced Micro Devices, Inc.', 'Netflix, Inc.', 'Booz Allen Hamilton Inc.', 'IQVIA, Inc',
           'Wynn Resorts, Limited',
           'Jones Lang LaSalle Incorporated', 'Regions Financial Corporation', 'CH2M HILL',
           'Western & Southern Financial Group',
           'Lithia Motors, Inc.', 'Host Hotels & Resorts, Inc.', 'Harman International Industries, Inc.',
           'Amphenol Corporation',
           'Avis Budget Group', 'Essendant, Inc.', 'Hanesbrands Inc.', 'Kindred Healthcare, Inc.',
           'Arris International, plc.',
           'Insight Enterprises, Inc.', 'Alliance Data Systems Corporation', 'Lifepoint Health',
           'Pioneer Natural Resources Co.',
           'Wyndham Worldwide Corp.', 'Alleghany Corp.', 'Big Lots Inc.', 'Momentive Performance Materials Inc',
           'Markel Corporation',
           'Noble Energy, Inc.', 'Leidos Holding, Inc.', 'Rockwell Collins, Inc.', 'Airgas Inc', 'Sprague Resources LP',
           'YRC WorldWide Inc.', 'The Hanover Insurance Group, Inc.', 'Fiserv, Inc.', 'Lorillard Licensing Company LLC',
           'American Tire Distributors', 'ABM Industries Inc.', 'Sonoco Products Co.', 'Harris Corporation',
           'Telephone & Data Systems Inc',
           'Linn Energy, LLC.', 'Raymond James Financial, Inc.', 'Berry Global Group, Inc.', 'SCANA Corporation',
           'Regency Energy Partners LP', 'Cincinnati Financial Corporation', 'Atmos Energy Corporation',
           'Flowserve Corporation',
           'Simon Property Group, Inc.', 'Constellation Brands, Inc.', 'Quad Graphics, Inc.', 'Neiman Marcus',
           'Bemis Company, Inc.',
           'Coach, Inc.', 'Continental Resources, Inc.']

occupation = ['Accountant', 'Architect', 'Computer Systems Analyst', 'Disaster relief insurance claims adjuster',
              'Economist', 'Engineer', 'Forester', 'Graphic designer', 'Hotel manager', 'Industrial designer',
              'Interior designer', 'Land surveyor', 'Landscape Architect', 'Lawyer', 'Librarian',
              'Management consultant', 'Mathematician',
              'Range conservationist', 'Research assistant', 'Scientific technician',
              'Social worker', 'Sylviculturist', 'Teacher', 'Seminary',
              'Technical publications writer', 'Urban planner', 'Vocational counselor', 'Dentist', 'Dietitian',
              'Medical laboratory technologist', 'Nutritionist',
              'Occupational therapist', 'Pharmacist', 'Physiotherapist/ physical therapist', 'Psychologist',
              'Recreational therapist',
              'Registered nurse', 'Veterinarian', 'Agriculturist', 'Animal breeder', 'Animal scientist', 'Apiculturist',
              'Astronomer',
              'Biochemist', 'Biologist', 'Chemist', 'Dairy scientist', 'Entomologist', 'Epidemiologist', 'Geochemist',
              'Geologist', 'Geophysicist', 'Horticulturist', 'Meteorologist', 'Pharmacologist', 'Physicist',
              'Plant Breeder',
              'Poultry scientist', 'Soil scientist', 'Zoologist', 'Software Developer', 'Data Scientist',
              'Devops Engineer', 'Marketing Manager',
              'Occupational Therapist', 'HR Manager', 'Electrical Engineer', 'Strategy Manager', 'Mobile Developer',
              'Product Manager',
              'Manufacturing Engineer', 'Compliance Manager', 'Finance Manager', 'Risk Manager',
              'Business Development Manager',
              'Front End Engineer', 'Site Reliability Engineer', 'Mechanical Engineer', 'Analytics Manager',
              'Tax Manager',
              'Creative Manager', 'Software Engineer', 'Hardware Engineer', 'Corporate Recruiter', 'QA Manager',
              'Physician Assistant',
              'Database Administrator', 'UX Designer', 'Nursing Manager', 'Engagement Manager',
              'Solutions Architect', 'Process Engineer', 'Reliability Engineer', 'Data Engineer', 'Operations Manager',
              'Speech Language Pathologist', 'Communications Manager', 'Audit Manager', 'Data Analyst',
              'Systems Analyst', 'Facilities Manager',
              'Strategic Account Manager', 'Business Intelligence Developer', 'Business Analyst',
              'Accounting Manager', 'UI Developer', 'Executive Assistant', 'Management Consultant', 'Project Manager',
              'Nurse Practitioner', 'HR Generalist']

numbers = {'one': '1', 'two': '2', 'three': '3', 'four': '4', 'five': '5', 'six': '6', 'seven': '7', 'eight': '8',
           'nine': '9', 'zero': '0'}
telephone = '(\()?((?(1)\d{3}(?=\))|\d{3}(?!\))))\)?[ -.](\d{3})[ -.]?(\d{4})[ .,]?'
link_library = []
twitter_accounts = []
giant = []
repeat = []
conn = sqlite3.connect('tutorial.db', check_same_thread=False)
c = conn.cursor()

####Twitter scraper
def getusernames():
    threading.Timer(60.0, getusernames).start()
    rightnow = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rightnow = datetime.strptime(rightnow, "%Y-%m-%d %H:%M:%S")
    keywords = ['wow', 'bullshit', 'worst', 'hate', 'literally', 'fuck', 'unacceptable', 'rude']
    companies = ['@VZWSupport', '@GoDaddyHelp', '@HumanaHelp', '@walmarthelp', '@KiaConsumerCare',
                 '@HyattConcierge', '@United', '@TMobileHelp', '@ATTCares', '@USAirways', '@avis', '@CoxHelp', '@Hertz',
                 '@Uber_Support', '@comcastcares', '@Ask_Spectrum', '@AmericanAir', '@Delta', '@SpiritAirlines',
                 '@JetBlue', '@SouthwestAir', '@AskCapitalOne']
    sevenhours = datetime.now(timezone.utc) - timedelta(1)  # subtract 7 hours
    sevenhours = sevenhours.strftime("%Y-%m-%d")
    randomcompanies = sample(companies, 2)
    for company in randomcompanies:
        for keyword in keywords:
            dufflebag = twint.Config()
            dufflebag.Since = str(sevenhours)
            dufflebag.To = company
            dufflebag.Limit = 20
            dufflebag.Store_object = True
            dufflebag.Search = keyword
            asyncio.set_event_loop(asyncio.new_event_loop())
            twint.run.Search(dufflebag)
    tweets_as_objects = twint.output.tweets_object
    for tweet in tweets_as_objects:
        timeposted = tweet.datestamp + ' ' + tweet.timestamp
        timeposted = datetime.strptime(timeposted, "%Y-%m-%d %H:%M:%S")
        diff = rightnow - timeposted
        days = diff.days
        seconds = diff.seconds
        total = (days * 86400)+seconds
        if total < 3600 * 6 and tweet.link not in repeat:
            repeat.append(tweet.link)
            time.sleep(.1)
            lookupnames(tweet)

app = Quart(__name__)

def create_table():
    c.execute("CREATE TABLE IF NOT EXISTS stuffToPlot(tweet TEXT, username TEXT, mentions TEXT, link UNIQUE, website TEXT, timeposted TEXT, telephone TEXT, formated_telephone TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS rss(title TEXT, name TEXT, phone UNIQUE, link TEXT, forum TEXT, description TEXT, hashtags TEXT, zone TEXT, ztwo[2] TEXT, zthree TEXT, timestamp TEXT)")

def lookupnames(tweet):
    topdomain = ['ebay.com', 'facebook.com', 'twitter.com', 'twitch.tv', 'http:', 'bit.ly', 'youtube.com', 'linkedin.com',
                 'open.spotify.com', 'about.me', 'ar.linkedin.com','qanon.pub', 'medium.com', 'mixer.com', 'iheart.com', 'instagram.com']
    userlink = tweet.link.split('status')[0]
    userlink = userlink.lower()
    dontcrawlagain = []
    if userlink not in dontcrawlagain:
        dontcrawlagain.append(userlink)
        time.sleep(.3)
        res = requests.get(userlink)
        soup = bs4.BeautifulSoup(res.text, 'html.parser')
        website = 'no'
        try:
            for span in soup.find_all('span', class_='ProfileHeaderCard-urlText u-dir'):
                website = span.find('a').get("title")
                website = website.replace('www.', '')
                website = website.replace('http://', '')
                website = website.replace('https://', '')
                website = website.split('/')[0].lower()
                combined = '\t'.join(topdomain)
                timeposted = tweet.datestamp + ' ' + tweet.timestamp
                timeposted = datetime.strptime(timeposted, "%Y-%m-%d %H:%M:%S")
        except:
            pass
        if website is not 'no' and website not in combined:
            username = tweet.username
            mentions = str(tweet.mentions)
            link = tweet.link
            tweet = tweet.tweet
            url = "https://domainbigdata.com/" + website
            res = requests.get(url)
            soup = bs4.BeautifulSoup(res.text, 'html.parser')
            try:
                bucket = soup.find("tr", id="trRegistrantTel")
                telephone = bucket.findChildren()[1].text
                telephone = telephone.replace('+1.','1+')
                formated_telephone = telephone.replace('1+','')
                c.execute("INSERT OR IGNORE INTO stuffToPlot VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (tweet, username, mentions, link, website, timeposted, telephone, formated_telephone))
                conn.commit()
            except:
                pass

def cleantwitter():
    threading.Timer(3600.0, cleantwitter).start()
    c.execute('SELECT * FROM stuffToPlot ORDER BY timeposted DESC')
    data = c.fetchall()
    for row in data:
        timed = parser.parse(row[5])
        if timed < datetime.now() - timedelta(hours=5):
            c.execute("DELETE FROM stuffToPlot WHERE timeposted=?", (timed,))
    conn.commit()

####RSS CLassifieds
def getfeed():
    threading.Timer(70.0, getfeed).start()
    try:
        feeds = []
        list = sample(RSS_URLS, 4)
        [feeds.append(feedparser.parse(url)) for url in list]
        timenow = datetime.now(timezone.utc)
        for d in feeds:
            time.sleep(.1)
            try:
                forum = d.feed.title
            except:
                try:
                    forum = d.title
                except:
                    forum = 'forum'
            try:
                title = d.entries
            except:
                try:
                    for d in feeds.feed:
                        title = d.entries
                except:
                    break
            for t in title:
                try:
                    link = t.link
                except:
                    try:
                        link = t.list(link)
                    except:
                        break
                timestamp = parser.parse(t.published)
                if link not in link_library:
                    link_library.append(link)
                    diff = timenow - timestamp
                    days = diff.days
                    seconds = diff.seconds
                    total = (days * 86400) + seconds
                    if total < 3600 * 24:
                        getphone(t, forum, timestamp)
    except:
        pass

def find_replace_multi(string, dictionary):
    for item in dictionary.keys():
        # sub item for item's paired value in string
        string = re.sub(item, dictionary[item], string, flags=re.IGNORECASE)
        string = re.sub(r'(\d)\s+(\d)', r'\1\2', string)
    return string

def getphone(t, forum, timestamp):
    try:
        a = t.summary
    except:
        try:
            a = t.content
        except:
            pass
    if a:
        description = re.sub(r'<.+?>', ' ', a, flags=re.DOTALL)
        description = re.sub(r'http\S+ ', r'', description)
        description = re.sub(r'www.\S+ ', r'', description)
        description = re.sub(r'[^\x00-\x7f]', r'', description)
        b = description
        for key in numbers:
            if key in b:
                b = find_replace_multi(b, numbers)
        match = re.search(telephone, str(b))
        if match:
            description = description.replace('br /', ' ')
            description = description.replace('&#039;', "'")
            description = description.replace('&lt;', '')
            description = description.replace('&nbsp;', '')
            description = description.replace('&gt;', '')
            description = description.strip()
            description = description[:300]
            phone = match.group()
            phone = [int(s) for s in phone if s.isdigit()]
            phone = ''.join(map(str, phone))
            if not len(phone) == 10:
                print('oops')
                pass
            zip = 'zip'
            title = 'title'
            link = 'link'
            zip = phone[:3]
            zipcode = zipcodes.get(zip)
            if not zipcode:
                zipcode = 'unknown'
            zone = zipcode[1]
            ztwo = zipcode[2]
            zthree = zipcode[3]

            try:
                name = t.author.upper()
            except:
                name = "Nope"
            title = t.title.upper()
            link = t.link
            prettydate = timestamp.strftime('%b %d, %I:%M%p')
            c.execute("INSERT OR IGNORE INTO rss VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (title, name, phone, link, forum, description, prettydate, zone, ztwo, zthree, timestamp))
            clean()

def clean():
    c.execute('SELECT * FROM rss ORDER BY timestamp DESC')
    data = c.fetchall()
    for row in data:
        timed = parser.parse(row[-1])
        if timed < datetime.now() - timedelta(hours=24):
            c.execute("DELETE FROM rss WHERE timestamp=?", (timed,))
    conn.commit()

def socialmedia(profile):

    time.sleep(3)
    getsocialmedia(data)

@app.route("/")
def home():
    time_utc = datetime.now(timezone.utc)
    time_et = (time_utc + timedelta(hours=-4)).strftime("%b %d, %I:%M %p")
    time_ct = (time_utc + timedelta(hours=-5)).strftime("%b %d, %I:%M %p")
    time_mt = (time_utc + timedelta(hours=-6)).strftime("%b %d, %I:%M %p")
    time_pt = (time_utc + timedelta(hours=-7)).strftime("%b %d, %I:%M %p")
    time_ht = (time_utc + timedelta(hours=-9)).strftime("%b %d, %I:%M %p")
    time_utc = time_utc.strftime("%b %d, %I:%M %p")
    global first, last, occupation, company
    firstd = random.choice(first)
    lastd = random.choice(last)
    occupationd = random.choice(occupation)
    companyd = random.choice(company)

    return render_template('index.html', **locals())

@app.route('/twitter')
def twitter():
    time_utc = datetime.now(timezone.utc)
    time_et = (time_utc + timedelta(hours=-4)).strftime("%b %d, %I:%M %p")
    time_ct = (time_utc + timedelta(hours=-5)).strftime("%b %d, %I:%M %p")
    time_mt = (time_utc + timedelta(hours=-6)).strftime("%b %d, %I:%M %p")
    time_pt = (time_utc + timedelta(hours=-7)).strftime("%b %d, %I:%M %p")
    time_ht = (time_utc + timedelta(hours=-9)).strftime("%b %d, %I:%M %p")
    time_utc = time_utc.strftime("%b %d, %I:%M %p")
    final = []
    res = c.execute("SELECT * FROM stuffToPlot")
    d = c.fetchall()
    b = [list(x) for x in d]
    for t in b:
        old = parser.parse(t[5])
        diff = datetime.now() - old
        theminutes = diff.total_seconds() / 60
        days = diff.days * 1440
        totalminutes = theminutes + days
        if totalminutes > 60:
            diffhours = totalminutes / 60
            if diffhours <= 2:
                difference = str(int(diffhours)) + ' hour ago'
            else:
                difference = str(int(diffhours)) + ' hours ago'
        else:
            difference = str(int(totalminutes)) + ' minutes ago'
        a = t
        a.append(totalminutes)
        a.append(difference)
        final.append(a)
    twitter_accountss = sorted(final, key=lambda x: x[5], reverse=True)
    global first, last, occupation, company
    firstd = random.choice(first)
    lastd = random.choice(last)
    occupationd = random.choice(occupation)
    companyd = random.choice(company)
    return render_template("twitter.html", **locals())

@app.route("/classifieds")
def classifieds():
    global first, last, occupation, company
    numberofrss = len(RSS_URLS)
    newgiant = []
    time_utc = datetime.now(timezone.utc)
    time_et = (time_utc + timedelta(hours=-4)).strftime("%b %d, %I:%M %p")
    time_ct = (time_utc + timedelta(hours=-5)).strftime("%b %d, %I:%M %p")
    time_mt = (time_utc + timedelta(hours=-6)).strftime("%b %d, %I:%M %p")
    time_pt = (time_utc + timedelta(hours=-7)).strftime("%b %d, %I:%M %p")
    time_ht = (time_utc + timedelta(hours=-9)).strftime("%b %d, %I:%M %p")
    time_utc = time_utc.strftime("%b %d, %I:%M %p")
    res = c.execute("SELECT * FROM rss")
    data = c.fetchall()
    giant = [list(x) for x in data]
    for g in giant:
        old = parser.parse(g[-1])
        diff = datetime.now(timezone.utc) - old
        theminutes = diff.total_seconds() / 60
        days = diff.days * 1440
        totalminutes = theminutes + days
        if totalminutes > 60:
            L1 = list(g)
            diffhours = totalminutes / 60
            if diffhours <= 2:
                L1[6] = str(int(diffhours)) + ' hour ago'
                L1[9] = Markup(g[9])
            else:
                L1[6] = str(int(diffhours)) + ' hours ago'
                L1[9] = Markup(g[9])
            h = tuple(L1)
        else:
            L1 = list(g)
            L1[6] = str(int(totalminutes)) + ' minutes ago'
            L1[9] = Markup(g[9])
            h = tuple(L1)
        newgiant.append(h)

    giantd = sorted(newgiant, key=lambda x: x[-1], reverse=True)
    firstd = random.choice(first)
    lastd = random.choice(last)
    occupationd = random.choice(occupation)
    companyd = random.choice(company)
    return render_template('tables.html', **locals())

@app.route("/getTime", methods=['GET'])
def getTime():
    already_called = request.args.get("time")
    res = c.execute("select * from stuffToPlot")
    for row in res:
        c.execute("DELETE FROM stuffToPlot WHERE link=?", (already_called,))
        global repeat
        repeat.insert(0, already_called)
        repeat = repeat[:75]
        return repeat

@app.route("/getRSS", methods=['GET'])
def getRSS():

    already_called = request.args.get("getRSS")
    res = c.execute("select * from rss")
    for row in res:
        c.execute("DELETE FROM rss WHERE phone=?", (already_called,))
        global link_library
        link_library.insert(0, already_called)
        link_library = link_library[:75]
        return link_library

@app.route("/twitter/<userID>", methods=['GET'])
def profile(userID):
    userID = userID
    time_utc = datetime.now(timezone.utc)
    time_et = (time_utc + timedelta(hours=-4)).strftime("%b %d, %I:%M %p")
    time_ct = (time_utc + timedelta(hours=-5)).strftime("%b %d, %I:%M %p")
    time_mt = (time_utc + timedelta(hours=-6)).strftime("%b %d, %I:%M %p")
    time_pt = (time_utc + timedelta(hours=-7)).strftime("%b %d, %I:%M %p")
    time_ht = (time_utc + timedelta(hours=-9)).strftime("%b %d, %I:%M %p")
    time_utc = time_utc.strftime("%b %d, %I:%M %p")
    profile = request.args.get("profile")
    headers = {'X-FullContact-APIKey': '###############'}
    params = (('email', 'bart@fullcontact.com'))
    r = requests.get('https://api.fullcontact.com/v2/person.json?twitter='+userID, headers=headers)
    data = r.json()
    try:
        location = data['demographics']['locationDeduced']['deducedLocation']
    except:
        pass
    media = []
    try:
        social_media = data['socialProfiles']
        for social in social_media:
            socialtype = social['type']
            socialurl = social['url']
            socialbio = ' '
            followers = ''
            following = ''
            try:
                socialbio = social['bio']
            except:
                pass
            try:
                followers = social['following']
            except:
                pass
            try:
                following = social['followers']
            except:
                pass

            sbucket = socialtype, socialurl, socialbio, followers, following
            media.append(sbucket)
    except:
        pass
    pictures = []
    try:
        photos = data['photos']
        for photo in photos:
            url  = photo['url']
            source = photo['typeName']
            bucket = source, url
            pictures.append(bucket)
    except:
        pass

    feet = []
    try:
        scores = data['digitalFootprint']['scores']
        topics = data['digitalFootprint']['topics']
        for s in scores:
            a = s['value']
            a = str(a).lstrip()
            feet.append(a)
        for t in topics:
            a = t['value']
            a = str(a).lstrip()
            feet.append(a)

    except:
        pass
    try:
        age = location = data['demographics']['age']
    except:
        pass
    actuallyemploed = []
    try:
        organizations = data['organizations']
        for org in organizations:
            orgname = ''
            orgdate = ''
            orgtitle = ''
            orgstatus = ''
            try:
                orgname = org['name']

            except:
                pass
            try:
                orgdate = org['startDate']
            except:
                pass
            try:
                orgtitle = org['title']
            except:
                pass
            try:
                orgstatus = org['current']
            except:
                pass
            bucket = orgname, orgdate, orgtitle, orgstatus

            actuallyemploed.append(bucket)
    except:
        pass
    try:
        full_name = data['contactInfo']['fullName']
    except:
        pass
    web = []
    try:
        websites = data['contactInfo']['websites']
        for w in websites:
            linky = w['url']
            web.append(linky)
    except:
        pass


    return render_template('profile.html', **locals())

@app.route("/craigslist")
def craigslist():

    def __init__(self, start_url, base_url):
            self.session = requests.Session()
            self.base_url = base_url
            self.start_url = start_url
            print('clise')
    def scrape(self):
            page = self.session.get(self.start_url).text
            tree = html.fromstring(page)
            for row in tree.xpath('.//li[@class="result-row"]'):
                try:
                    link = row.xpath(".//a[contains(concat(' ', @class, ' '), ' hdrlnk ')]/@href")[0]
                    self.title = row.xpath(".//a")[1].text
                    self.date = row.xpath(".//time/@title")
                    yield self.process_search_result(link)
                except:
                    pass
    def process_search_result(self, link):
            page = self.session.get(link).text
            tree = html.fromstring(page)
            try:
                contact_info_link = self.base_url + \
                                    tree.xpath('//section[@id="postingbody"]//a[@class="showcontact"]/@href')[0]
                return link
                # phone_number = self.get_contact_info(contact_info_link)

            except IndexError:
                phone_number = ""
            print(link)
            return link, self.date, self.title

    city = pymsgbox.prompt('City as it appears in the CraigsList URL prefix\nex: https://XXXXXXXX.craigslist.org/', 'Craigslist Hunter', default='southjersey')
    search_type = pymsgbox.confirm('What section are we going to search?', 'Confirm nuke', ['For Sale', 'Housing', 'Community', 'Jobs', 'Services'])
    base_url = "https://" + city + ".craigslist.com"
    myDict = {'For Sale': 'sss',
              'Housing': 'hhh',
              'Community': 'ccc',
              'Jobs': 'jjj',
              'Services': 'bbb'}

    start_url = base_url + "/search/" + myDict.get(search_type)
    pymsgbox.alert(text="Alright, it's in the works. Page will load shortly.", title="You're Welcome", button='OK')
    scrape(start_url, base_url)
    print(result)
    return render_template('craigslist.html', **locals())

create_table()
#getusernames()
#cleantwitter()
#getfeed()

#c.close
#conn.close()

if __name__ == '__main__':
    app.run()
