from collections import namedtuple
DamageEvent = namedtuple('DamageEvent', ['shotID',
 'time',
 'damage',
 'distance',
 'circularVisionRadius',
 'reasonCode',
 'damageFlag',
 'targetSpeed'])
