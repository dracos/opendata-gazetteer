import re
from django.contrib.gis.db import models

PLACE_TYPES = (
    ('A', 'Non-Roman antiquity'),
    ('F', 'Forest or wood'),
    ('FM', 'Farm'),
    ('H', 'Large hill feature or mountains'),
    ('R', 'Roman antiquity'),
    ('C', 'City'),
    ('T', 'Town'),
    ('O', 'Other settlements'),
    ('W', 'Water features'),
    ('X', 'Other (private houses, buildings, airports, marshes)'),
)

COUNTIES = (
    ('AB', 'Aberdeenshire'),
    ('AG', 'Angus'),
    ('AN', 'Aberdeen City'),
    ('AR', 'Argyll and Bute'),
    ('BA', 'Bradford'),
    ('BB', 'Blackburn with Darwen'),
    ('BC', 'Bracknell Forest'),
    ('BD', 'Barking & Dagenham'),
    ('BE', 'Bridgend'),
    ('BF', 'Bedfordshire'),
    ('BG', 'Blaenau Gwent'),
    ('BH', 'City of Brighton and Hove'),
    ('BI', 'Birmingham'),
    ('BL', 'Barnsley'),
    ('BM', 'Buckinghamshire'),
    ('BN', 'Barnet'),
    ('BO', 'Bolton'),
    ('BP', 'Blackpool'),
    ('BR', 'Bromley'),
    ('BS', 'Bath and North East Somerset'),
    ('BT', 'Brent'),
    ('BU', 'Bournemouth'),
    ('BX', 'Bexley'),
    ('BY', 'Bury'),
    ('BZ', 'City of Bristol'),
    ('CA', 'Calderdale'),
    ('CB', 'Cambridgeshire'),
    ('CD', 'Cardiff'),
    ('CE', 'Ceredigion'),
    ('CF', 'Caerphilly'),
    ('CH', 'Cheshire'),
    ('CL', 'Clackmannanshire'),
    ('CM', 'Camden'),
    ('CN', 'Cornwall'),
    ('CT', 'Carmarthenshire'),
    ('CU', 'Cumbria'),
    ('CV', 'Coventry'),
    ('CW', 'Conwy'),
    ('CY', 'Croydon'),
    ('DB', 'City of Derby'),
    ('DD', 'Dundee City'),
    ('DE', 'Denbighshire'),
    ('DG', 'Dumfries and Galloway'),
    ('DL', 'Darlington'),
    ('DN', 'Devon'),
    ('DR', 'Doncaster'),
    ('DT', 'Dorset'),
    ('DU', 'Durham'),
    ('DY', 'Derbyshire'),
    ('DZ', 'Dudley'),
    ('EA', 'East Ayrshire'),
    ('EB', 'City of Edinburgh'),
    ('ED', 'East Dunbartonshire'),
    ('EG', 'Ealing'),
    ('EL', 'East Lothian'),
    ('EN', 'Enfield'),
    ('ER', 'East Renfrewshire'),
    ('ES', 'East Sussex'),
    ('EX', 'Essex'),
    ('EY', 'East Riding of Yorkshire'),
    ('FA', 'Falkirk'),
    ('FF', 'Fife'),
    ('FL', 'Flintshire'),
    ('GH', 'Gateshead'),
    ('GL', 'Glasgow City'),
    ('GR', 'Gloucestershire'),
    ('GW', 'Greenwich'),
    ('GY', 'Gwynedd'),
    ('HA', 'Halton'),
    ('HD', 'Hertfordshire'),
    ('HE', 'Herefordshire'),
    ('HF', 'Hammersmith & Fulham'),
    ('HG', 'Haringey'),
    ('HI', 'Hillingdon'),
    ('HL', 'Highland'),
    ('HN', 'Hackney'),
    ('HP', 'Hampshire'),
    ('HR', 'Harrow'),
    ('HS', 'Hounslow'),
    ('HT', 'Hartlepool'),
    ('HV', 'Havering'),
    ('IA', 'Isle of Anglesey'),
    ('IL', 'Islington'),
    ('IM', 'Isle of Man'),
    ('IN', 'Inverclyde'),
    ('IS', 'Isles of Scilly'),
    ('IV', 'City of Inverness'),
    ('IW', 'Isle of Wight'),
    ('KC', 'Royal Borough of Kensington & Chelsea'),
    ('KG', 'Kingston upon Thames'),
    ('KH', 'City of Kingston upon Hull'),
    ('KL', 'Kirklees'),
    ('KN', 'Knowsley'),
    ('KT', 'Kent'),
    ('LA', 'Lancashire'),
    ('LB', 'Lambeth'),
    ('LC', 'City of Leicester'),
    ('LD', 'Leeds'),
    ('LL', 'Lincolnshire'),
    ('LN', 'Luton'),
    ('LO', 'City of London'),
    ('LP', 'Liverpool'),
    ('LS', 'Lewisham'),
    ('LT', 'Leicestershire'),
    ('MA', 'Manchester'),
    ('MB', 'Middlesbrough'),
    ('ME', 'Medway'),
    ('MI', 'Midlothian'),
    ('MK', 'Milton Keynes'),
    ('MM', 'Monmouthshire'),
    ('MO', 'Moray'),
    ('MR', 'Merton'),
    ('MT', 'Merthyr Tydfil'),
    ('NA', 'North Ayrshire'),
    ('NC', 'North East Lincolnshire'),
    ('ND', 'Northumberland'),
    ('NE', 'Newport'),
    ('NG', 'City of Nottingham'),
    ('NH', 'Newham'),
    ('NI', 'North Lincolnshire'),
    ('NK', 'Norfolk'),
    ('NL', 'North Lanarkshire'),
    ('NN', 'Northamptonshire'),
    ('NP', 'Neath Port Talbot'),
    ('NR', 'North Tyneside'),
    ('NS', 'North Somerset'),
    ('NT', 'Nottinghamshire'),
    ('NW', 'Newcastle upon Tyne'),
    ('NY', 'North Yorkshire'),
    ('OH', 'Oldham'),
    ('OK', 'Orkney Islands'),
    ('ON', 'Oxfordshire'),
    ('PB', 'Pembrokeshire'),
    ('PE', 'City of Peterborough'),
    ('PK', 'Perth and Kinross'),
    ('PL', 'Poole'),
    ('PO', 'City of Portsmouth'),
    ('PW', 'Powys'),
    ('PY', 'City of Plymouth'),
    ('RB', 'Redbridge'),
    ('RC', 'Redcar & Cleveland'),
    ('RD', 'Rochdale'),
    ('RE', 'Renfrewshire'),
    ('RG', 'Reading'),
    ('RH', 'Rhondda, Cynon, Taff'),
    ('RL', 'Rutland'),
    ('RO', 'Rotherham'),
    ('RT', 'Richmond upon Thames'),
    ('SA', 'Sandwell'),
    ('SB', 'Scottish Borders'),
    ('SC', 'Salford'),
    ('SD', 'Swindon'),
    ('SE', 'Sefton'),
    ('SF', 'Staffordshire'),
    ('SG', 'South Gloucestershire'),
    ('SH', 'Shropshire'),
    ('SI', 'Shetland Islands'),
    ('SJ', 'City of Stoke-on-Trent'),
    ('SK', 'Suffolk'),
    ('SL', 'South Lanarkshire'),
    ('SM', 'Stockton-on-Tees'),
    ('SN', 'St Helens'),
    ('SO', 'City of Southampton'),
    ('SP', 'Sheffield'),
    ('SQ', 'Solihull'),
    ('SR', 'Stirling'),
    ('SS', 'Swansea'),
    ('ST', 'Somerset'),
    ('SU', 'Surrey'),
    ('SV', 'Sunderland'),
    ('SW', 'Southwark'),
    ('SX', 'South Ayrshire'),
    ('SY', 'South Tyneside'),
    ('SZ', 'Sutton'),
    ('TB', 'Torbay'),
    ('TF', 'Torfaen'),
    ('TH', 'Tower Hamlets'),
    ('TR', 'Trafford'),
    ('TS', 'Tameside'),
    ('TU', 'Thurrock'),
    ('VG', 'The Vale of Glamorgan'),
    ('WA', 'Walsall'),
    ('WB', 'West Berkshire'),
    ('WC', 'Windsor and Maidenhead'),
    ('WD', 'West Dunbartonshire'),
    ('WE', 'Wakefield'),
    ('WF', 'Waltham Forest'),
    ('WG', 'Warrington'),
    ('WH', 'City of Wolverhampton'),
    ('WI', 'Na h-Eileanan an Iar'),
    ('WJ', 'Wokingham'),
    ('WK', 'Warwickshire'),
    ('WL', 'West Lothian'),
    ('WM', 'City of Westminster'),
    ('WN', 'Wigan'),
    ('WO', 'Worcestershire'),
    ('WP', 'Telford and Wrekin'),
    ('WR', 'Wirral'),
    ('WS', 'West Sussex'),
    ('WT', 'Wiltshire'),
    ('WW', 'Wandsworth'),
    ('WX', 'Wrexham'),
    ('YK', 'York'),
    ('YS', 'Southend-on-Sea'),
    ('YT', 'Slough'),
    ('YY', 'Stockport'),
)
counties = {}
for c in COUNTIES:
    counties[c[0]] = c[1]

class Postcode(models.Model):
    name = models.CharField(max_length=7, db_index=True)
    location = models.PointField(srid=27700)

    objects = models.GeoManager()

    def __unicode__(self):
        return self.get_name_display()

    def get_name_display(self):
        return re.sub('(...)$', r' \1', self.name)

class Place(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    tile_ref = models.CharField(max_length=6)
    location = models.PointField(srid=27700)
    county = models.CharField(max_length=2, choices=COUNTIES)
    type = models.CharField(max_length=2, choices=PLACE_TYPES)
    os_map = models.CharField(max_length=12)

    objects = models.GeoManager()

    def __unicode__(self):
        return u'%s, %s' % (self.name, self.get_county_display())

    def get_type_display(self):
        for type in PLACE_TYPES:
            if self.type == type[0]:
                return type[1]
        return None

    def get_county_display(self):
        return counties[self.county]

class Road(models.Model):
    name = models.CharField(max_length=100)
    number = models.CharField(max_length=10)
    centre = models.PointField(srid=27700)
    min = models.PointField(srid=27700)
    max = models.PointField(srid=27700)
    settlement = models.CharField(max_length=40)
    locality = models.CharField(max_length=60)
    county = models.CharField(max_length=50)
    council = models.CharField(max_length=50)
    tile10k = models.CharField(max_length=6)
    tile25k = models.CharField(max_length=4)

    objects = models.GeoManager()

    def __unicode__(self):
        if self.name and self.number:
            out = '%s (%s)' % (self.get_name_display(), self.number)
        elif self.name:
            out = self.get_name_display()
        elif self.number:
            out = self.number
        out += ', %s' % self.locality
        if self.settlement:
            out += ', %s' % self.get_settlement_display()
        return out

    def get_settlement_display(self):
        return re.sub("([a-z])'([A-Z])", lambda m: m.group(0).lower(), self.settlement.title())

    def get_name_display(self):
        return re.sub("([a-z])'([A-Z])", lambda m: m.group(0).lower(), self.name.title())

