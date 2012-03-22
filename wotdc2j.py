###################################################
# World of Tanks Dossier Cache to JSON            #
# Initial version by Phalynx www.vbaddict.net/wot #
###################################################


def main():
	import cPickle, struct, json, time, sys, os
	
	filename_source = str(sys.argv[1])
	print 'Processing ' + filename_source
	
	
	#os.path.isfile(filename)
	
	if os.path.exists(filename_source) and os.path.isfile(filename_source) and os.access(filename_source, os.R_OK):
		print "File exists and is readable"
	else:
		print "File does not exists!"
		sys.exit(1)
	
	filename_target = os.path.splitext(filename_source)[0]
	filename_target = filename_target + '.json'
	
	if os.path.exists(filename_target) and os.path.isfile(filename_target) and os.access(filename_target, os.R_OK):
		print "Target File exists and is readable"
		os.remove(filename_target)
		
	
	cachefile = open (filename_source, 'rb')
	cacheobject = cPickle.load(cachefile)
	
	dossierCache = cacheobject[1]
	
	tankitems = [(k, v) for k, v in dossierCache.items()]
	
	dossier = []
	dossier.append({
		"tankcount": len(tankitems), 
		"date": time.mktime(time.localtime()),
		"parser": 'http://www.vbaddict.net/wot', 
		"parserversion": 2
	})
	
	tanks = []
	for tankitem in tankitems:
	
	
		tankid = tankitem[0][1] //256
		countryid = ((tankitem[0][1] - tankid*256)-1) //16
		
		data = tankitem[1][1]
		tankstruct = str(len(data)) + 'B'
		sourcedata = struct.unpack(tankstruct, data)
			
		

		


		
		raw = []
		for m in xrange(0,len(sourcedata)):
			raw.append({m: sourcedata[m]})
		
		if getdata(sourcedata, 0, 1) == 0:
			continue
	
	
		if getdata(sourcedata, 0, 1) < 20:
			pre7 = 1
		else:
			pre7 = 0
			
		tank = []
		tank.append({"countryid": countryid,
			"tankid": tankid,
			"updated": tankitem[1][0],
			"lastBattleTime": tankitem[1][0],
			"basedonversion": getdata(sourcedata, 0, 1)
		})
		
		tankdata = getdata_tank(sourcedata)

	
	
	
		fragslist = []
		
		if pre7 == 1:
			offset = 138
		else:
			offset = 269
		
		if len(sourcedata) > offset:
	
			numfrags = getdata(sourcedata, offset-2, 2)
		
			if numfrags > 0:			
				for m in xrange(0,numfrags):
		
					tankoffset = offset + m*4
					killoffset = offset + numfrags*4+m*2
		
					ptankid = getdata(sourcedata, tankoffset, 2)
					amount = getdata(sourcedata, killoffset, 2)
					
					tankid = ptankid //256
					countryid = ((ptankid - tankid*256)-1) //16
					
					tankill = [countryid, tankid, amount]
					fragslist.append(tankill)
				
		if pre7 == 0:
		
			company = []
			if getdata(sourcedata, 161, 4) > 0:
				company = getdata_tank_specific(sourcedata, 161)
		
			clan = []
			if getdata(sourcedata, 213, 4) > 0:
				clan = getdata_tank_specific(sourcedata, 213)
	
			
			#print offset+51 = 264
		
		
			
			series = getdata_series(sourcedata)
			
			special = getdata_special(sourcedata)
			
			battle = getdata_battle(sourcedata)
		
			major = getdata_major(sourcedata)
			
			epic = getdata_epic(sourcedata)

		
	
		
		tank.append({"tankdata": tankdata})
		tank.append({"kills": fragslist})
			
		if pre7 == 0:
			tank.append({"series": series})
			tank.append({"battle": battle})
			tank.append({"special": special})		
			tank.append({"epic": epic})
			tank.append({"major": major})
			tank.append({"clan": clan})
			tank.append({"company": company})
	
		#tank.append({"raw": raw})
		
		
		tanks.append({"tank": tank})
		
	dossier.append(tanks)
		
	
	print 'Dumping to JSON'
	
	f = open(filename_target, 'w')
	
	if len(sys.argv) == 3:
		f.write(json.dumps(dossier, sort_keys=True, indent=4))
	else:
		f.write(json.dumps(dossier))
	
	print 'Done!'
	sys.exit(0)



############################################################################################################################



def getdata_series(sourcedata):
	data = []
	data.append({"sniperSeries": getdata(sourcedata, 79, 2),
		"maxSniperSeries": getdata(sourcedata, 81, 2),
		"invincibleSeries": getdata(sourcedata, 83, 1),
		"maxInvincibleSeries": getdata(sourcedata, 84, 1),
		"diehardSeries": getdata(sourcedata, 85, 1),
		"maxDiehardSeries": getdata(sourcedata, 86, 1),
		"killingSeries": getdata(sourcedata, 87, 1),
		"maxKillingSeries": getdata(sourcedata, 88, 1),
		"piercingSeries": getdata(sourcedata, 89, 1),
		"maxPiercingSeries": getdata(sourcedata, 90, 1)
	})
	
	return data


def getdata_special(sourcedata):
	data = []
	data.append({"beasthunter": getdata(sourcedata, 145, 2),
		"mousebane": getdata(sourcedata, 147, 2),
		"tankExpert": getdata(sourcedata, 149, 1),
		"sniper": getdata(sourcedata, 150, 1),
		"invincible": getdata(sourcedata, 151, 1),
		"diehard": getdata(sourcedata, 152, 1),
		"raider": getdata(sourcedata, 153, 2),
		"handOfDeath": getdata(sourcedata, 155, 1),
		"armorPiercer": getdata(sourcedata, 156, 1),
		"kamikaze": getdata(sourcedata, 157, 2),
		"lumberjack": getdata(sourcedata, 159, 1),
		"markOfMastery": getdata(sourcedata, 160, 1),
	})
	
	return data

def getdata_battle(sourcedata):
	data = []
	data.append({"battleHeroes": getdata(sourcedata, 91, 2),
		"warrior": getdata(sourcedata, 93, 2),
		"invader": getdata(sourcedata, 95, 2),
		"sniper": getdata(sourcedata, 97, 2),
		"defender": getdata(sourcedata, 99, 2),
		"steelwall": getdata(sourcedata, 101, 2),
		"supporter": getdata(sourcedata, 103, 2),
		"scout": getdata(sourcedata, 105, 2),
		"evileye": getdata(sourcedata, 107, 2),
	})
	
	return data

def getdata_major(sourcedata):
	data = []
	data.append({"Kay": getdata(sourcedata, 109, 1),
		"Carius": getdata(sourcedata, 110, 1),
		"Knispel": getdata(sourcedata, 111, 1),
		"Poppel": getdata(sourcedata, 112, 1),
		"Abrams": getdata(sourcedata, 113, 1),
		"LeClerc": getdata(sourcedata, 114, 1),
		"Lavrinenko": getdata(sourcedata, 115, 1),
		"Ekins": getdata(sourcedata, 116, 1),
	})
	
	return data


def getdata_epic(sourcedata):
	data = []
	data.append({"Wittmann": getdata(sourcedata, 117, 2),
		"Orlik": getdata(sourcedata, 119, 2),
		"Oskin": getdata(sourcedata, 121, 2),
		"Halonen": getdata(sourcedata, 123, 2),
		"Burda": getdata(sourcedata, 125, 2),
		"Billotte": getdata(sourcedata, 127, 2),
		"Kolobanov": getdata(sourcedata, 129, 2),
		"Fadin": getdata(sourcedata, 131, 2),
		"HeroesOfRassenai": getdata(sourcedata, 133, 2),
		"DeLaglanda": getdata(sourcedata, 135, 2),
		"TamadaYoshio": getdata(sourcedata, 137, 2),
		"Erohin": getdata(sourcedata, 139, 2),
		"Horoshilov": getdata(sourcedata, 141, 2),
		"Lister": getdata(sourcedata, 143, 2),
	})
	
	return data


def getdata_tank(sourcedata):
	data = []
	data.append({"battleLifeTime": getdata(sourcedata, 6, 4),
		"maxFrags": getdata(sourcedata, 10, 1),
		"xp": getdata(sourcedata, 11, 4),
		"maxXP": getdata(sourcedata, 15, 2),
		"battlesCount": getdata(sourcedata, 17, 4),
		"wins": getdata(sourcedata, 21, 4),
		"losses": getdata(sourcedata, 25, 4),
		"survivedBattles": getdata(sourcedata, 29, 4),
		"winAndSurvived": getdata(sourcedata, 33, 4),
		"frags": getdata(sourcedata, 37, 4),
		"frags8p": getdata(sourcedata, 41, 4),
		"fragsBeast": getdata(sourcedata, 45, 4),
		"shots": getdata(sourcedata, 49, 4),
		"hits": getdata(sourcedata, 53, 4),
		"spotted": getdata(sourcedata, 57, 4),
		"damageDealt": getdata(sourcedata, 61, 4),
		"damageReceived": getdata(sourcedata, 65, 4),
		"treesCut": getdata(sourcedata, 69, 2),
		"capturePoints": getdata(sourcedata, 71, 4),
		"droppedCapturePoints": getdata(sourcedata, 75, 4),
	})
	
	return data
	
	
	
def getdata_tank_specific(sourcedata, offset):
	data = []
	data.append({"xp": getdata(sourcedata, offset, 4),
		"battlesCount": getdata(sourcedata, offset+4, 4),
		"wins": getdata(sourcedata, offset+8, 4),
		"losses": getdata(sourcedata, offset+12, 4),
		"survivedBattles": getdata(sourcedata, offset+16, 4),
		"frags": getdata(sourcedata, offset+20, 4),
		"shots": getdata(sourcedata, offset+24, 4),
		"hits": getdata(sourcedata, offset+28, 4),
		"spotted": getdata(sourcedata, offset+32, 4),
		"damageDealt": getdata(sourcedata, offset+36, 4),
		"damageReceived": getdata(sourcedata, offset+40, 4),
		"capturePoints": getdata(sourcedata, offset+44, 4),
		"droppedCapturePoints": getdata(sourcedata, offset+48, 4),
	})
	
	return data

	
def getdata(sourcedata, startoffset, offsetlength):

	if len(sourcedata)<startoffset+offsetlength:
		return 0

	if offsetlength == 1:
		return sourcedata[startoffset]
	elif offsetlength == 2:
	  return sourcedata[startoffset] + 256*sourcedata[startoffset+1]
	elif offsetlength == 3:
	  return sourcedata[startoffset] + 256*sourcedata[startoffset+1] + 256*265*sourcedata[startoffset+2]
	elif offsetlength == 4:
	  return sourcedata[startoffset] + 256*sourcedata[startoffset+1] + 256*265*sourcedata[startoffset+2] + 256*256*265*sourcedata[startoffset+3]
	else:
	  return 0

	
	
	
if __name__ == '__main__':
	main()
