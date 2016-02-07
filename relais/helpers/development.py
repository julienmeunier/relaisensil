import datetime
import random

import names

from relais import constants
from relais.models import TSHIRT_CHOICES, Runner, School

def create_fake_runner(category, indiv, school_name=None, num=None):
    is_male = bool(random.getrandbits(1))
    tshirt = TSHIRT_CHOICES[random.randint(0, 3)][0]
    year = random.randint(1950, 2000)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    birthday = datetime.datetime(year, month, day)
    school=None
    if is_male:
        gender = 'male'
        g = constants.MALE
    else:
        gender = 'female'
        g = constants.FEMALE
    if indiv:
        range_num = constants.RANGE_INDIVIDUAL
        time = datetime.time(minute=random.randint(30, 59), second=random.randint(0, 59))
    else:
        if num == 1:
            range_num = constants.RANGE_TEAM[1]
            time = datetime.time(minute=random.randint(10, 20), second=random.randint(0, 59))
        elif num == 2:
            range_num = constants.RANGE_TEAM[2]
            time = datetime.time(minute=random.randint(20, 40), second=random.randint(0, 59))
        else:
            range_num = constants.RANGE_TEAM[3]
            time = datetime.time(minute=random.randint(30, 59), second=random.randint(0, 59))
    if school_name:
        school = School.objects.get_or_create(name=school_name)[0]
    r = Runner(first_name=names.get_first_name(gender=gender), last_name=names.get_last_name(),
               gender=g, birthday=birthday, time=time, canicross=False, legal_status=True, certificat=True,
               tshirt=tshirt, school=school)
    r.update_num(range_num)
    r.save()
    return r