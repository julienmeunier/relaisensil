#-*-coding: utf-8 -*-

INDIVIDUAL = 'IND'
TEAM = 'GRP'

PRICE_ONLINE = 'PRE'
PRICE_DAY = 'J'

CASH = 'ESP'
CHEQUE = 'CHQ'
PAYPAL = 'PAY'
UNKNOWN = 'N/A'

MALE = 'H'
FEMALE = 'F'

STUDENT = 'STD'
STUDENT_ENSIL = 'ENSIL'
OLDER_ENSIL = 'AAEE'
CHALLENGE = 'CHA'
ADULT = 'ADT'

POUSSIN = 'Poussin'
PUPILLE = 'Pupille'
BENJAMIN = 'Benjamin'
MINIME = 'Minime'
CADET = 'Cadet'
JUNIOR = 'Junior'
ESPOIR = 'Espoir'
SENOIR = 'Senior'
V1 = 'Vétéran 1'
V2 = 'Vétéran 2'
V3 = 'Vétéran 3'
V4 = 'Vétéran 4'

CATEGORIES = [POUSSIN, PUPILLE, BENJAMIN, MINIME, CADET, JUNIOR,
              ESPOIR, SENOIR, V1, V2, V3, V4]

RANGE_TEAM = {}
RANGE_TEAM[1] = (100, 199)
RANGE_TEAM[2] = (200, 299)
RANGE_TEAM[3] = (300, 399)
RANGE_INDIVIDUAL = (500, 799)
