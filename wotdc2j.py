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
	dossier.append({"tankcount": len(tankitems)})
	dossier.append({"date": time.mktime(time.localtime())})
	dossier.append({"parser": 'http://www.vbaddict.net/wot'})
	dossier.append({"parserversion": 1})
	
	tanks = []
	for tankitem in tankitems:
	
	
		tankid = tankitem[0][1] //256
		countryid = ((tankitem[0][1] - tankid*256)-1) //16
		
		data = tankitem[1][1]
		tankstruct = str(len(data)) + 'B'
		sourcedata = struct.unpack(tankstruct, data)
			
		
		tank = []
		
		tank.append({"countryid": countryid})
		tank.append({"tankid": tankid})
		tank.append({"updated": tankitem[1][0]})
		tank.append({"basedonversion": getdata(sourcedata, 0, 1)})
		
		raw = []
		for m in xrange(0,len(sourcedata)):
			raw.append({m: sourcedata[m]})
		
		if getdata(sourcedata, 0, 1) == 0:
			continue
	
	
		if getdata(sourcedata, 0, 1) < 20:
			pre7 = 1
		else:
			pre7 = 0
			
	
		
		tankdata = getdata_tank(sourcedata)
		tankdata.append({"lastBattleTime": tankitem[1][0]})
	
	
	
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
	data.append({"sniperSeries": getdata(sourcedata, 79, 2)})
	data.append({"maxSniperSeries": getdata(sourcedata, 81, 2)})
	data.append({"invincibleSeries": getdata(sourcedata, 83, 1)})
	data.append({"maxInvincibleSeries": getdata(sourcedata, 84, 1)})
	data.append({"diehardSeries": getdata(sourcedata, 85, 1)})
	data.append({"maxDiehardSeries": getdata(sourcedata, 86, 1)})
	data.append({"killingSeries": getdata(sourcedata, 87, 1)})
	data.append({"maxKillingSeries": getdata(sourcedata, 88, 1)})
	data.append({"piercingSeries": getdata(sourcedata, 89, 1)})
	data.append({"maxPiercingSeries": getdata(sourcedata, 90, 1)})
	
	return data


def getdata_special(sourcedata):
	data = []
	data.append({"beasthunter": getdata(sourcedata, 145, 2)})
	data.append({"mousebane": getdata(sourcedata, 147, 2)})
	data.append({"tankExpert": getdata(sourcedata, 149, 1)})
	data.append({"sniper": getdata(sourcedata, 150, 1)})
	data.append({"invincible": getdata(sourcedata, 151, 1)})
	data.append({"diehard": getdata(sourcedata, 152, 1)})
	data.append({"raider": getdata(sourcedata, 153, 2)})
	data.append({"handOfDeath": getdata(sourcedata, 155, 1)})
	data.append({"armorPiercer": getdata(sourcedata, 156, 1)})
	data.append({"kamikaze": getdata(sourcedata, 157, 2)})
	data.append({"lumberjack": getdata(sourcedata, 159, 1)})
	data.append({"markOfMastery": getdata(sourcedata, 160, 1)})

	return data

def getdata_battle(sourcedata):
	data = []
	data.append({"battleHeroes": getdata(sourcedata, 91, 2)})
	data.append({"warrior": getdata(sourcedata, 93, 2)})
	data.append({"invader": getdata(sourcedata, 95, 2)})
	data.append({"sniper": getdata(sourcedata, 97, 2)})
	data.append({"defender": getdata(sourcedata, 99, 2)})
	data.append({"steelwall": getdata(sourcedata, 101, 2)})
	data.append({"supporter": getdata(sourcedata, 103, 2)})
	data.append({"scout": getdata(sourcedata, 105, 2)})
	data.append({"evileye": getdata(sourcedata, 107, 2)})

	return data

def getdata_major(sourcedata):
	data = []
	data.append({"Kay": getdata(sourcedata, 109, 1)})
	data.append({"Carius": getdata(sourcedata, 110, 1)})
	data.append({"Knispel": getdata(sourcedata, 111, 1)})
	data.append({"Poppel": getdata(sourcedata, 112, 1)})
	data.append({"Abrams": getdata(sourcedata, 113, 1)})
	data.append({"LeClerc": getdata(sourcedata, 114, 1)})
	data.append({"Lavrinenko": getdata(sourcedata, 115, 1)})
	data.append({"Ekins": getdata(sourcedata, 116, 1)})
	
	return data


def getdata_epic(sourcedata):
	data = []
	data.append({"Wittmann": getdata(sourcedata, 117, 2)})
	data.append({"Orlik": getdata(sourcedata, 119, 2)})
	data.append({"Oskin": getdata(sourcedata, 121, 2)})
	data.append({"Halonen": getdata(sourcedata, 123, 2)})
	data.append({"Burda": getdata(sourcedata, 125, 2)})
	data.append({"Billotte": getdata(sourcedata, 127, 2)})
	data.append({"Kolobanov": getdata(sourcedata, 129, 2)})
	data.append({"Fadin": getdata(sourcedata, 131, 2)})
	data.append({"HeroesOfRassenai": getdata(sourcedata, 133, 2)})
	data.append({"DeLaglanda": getdata(sourcedata, 135, 2)})
	data.append({"TamadaYoshio": getdata(sourcedata, 137, 2)})
	data.append({"Erohin": getdata(sourcedata, 139, 2)})
	data.append({"Horoshilov": getdata(sourcedata, 141, 2)})
	data.append({"Lister": getdata(sourcedata, 143, 2)})

	return data


def getdata_tank(sourcedata):
	data = []
	data.append({"battleLifeTime": getdata(sourcedata, 6, 4)})
	data.append({"maxFrags": getdata(sourcedata, 10, 1)})
	data.append({"xp": getdata(sourcedata, 11, 4)})
	data.append({"maxXP": getdata(sourcedata, 15, 2)})
	data.append({"battlesCount": getdata(sourcedata, 17, 4)})
	data.append({"wins": getdata(sourcedata, 21, 4)})
	data.append({"losses": getdata(sourcedata, 25, 4)})
	data.append({"survivedBattles": getdata(sourcedata, 29, 4)})
	data.append({"winAndSurvived": getdata(sourcedata, 33, 4)})
	data.append({"frags": getdata(sourcedata, 37, 4)})
	data.append({"frags8p": getdata(sourcedata, 41, 4)})
	data.append({"fragsBeast": getdata(sourcedata, 45, 4)})
	data.append({"shots": getdata(sourcedata, 49, 4)})
	data.append({"hits": getdata(sourcedata, 53, 4)})
	data.append({"spotted": getdata(sourcedata, 57, 4)})
	data.append({"damageDealt": getdata(sourcedata, 61, 4)})
	data.append({"damageReceived": getdata(sourcedata, 65, 4)})
	data.append({"treesCut": getdata(sourcedata, 69, 2)})
	data.append({"capturePoints": getdata(sourcedata, 71, 4)})
	data.append({"droppedCapturePoints": getdata(sourcedata, 75, 4)})
	
	return data
	
	
	
def getdata_tank_specific(sourcedata, offset):
	data = []
	data.append({"xp": getdata(sourcedata, offset, 4)})
	data.append({"battlesCount": getdata(sourcedata, offset+4, 4)})
	data.append({"wins": getdata(sourcedata, offset+8, 4)})
	data.append({"losses": getdata(sourcedata, offset+12, 4)})
	data.append({"survivedBattles": getdata(sourcedata, offset+16, 4)})
	data.append({"frags": getdata(sourcedata, offset+20, 4)})
	data.append({"shots": getdata(sourcedata, offset+24, 4)})
	data.append({"hits": getdata(sourcedata, offset+28, 4)})
	data.append({"spotted": getdata(sourcedata, offset+32, 4)})
	data.append({"damageDealt": getdata(sourcedata, offset+36, 4)})
	data.append({"damageReceived": getdata(sourcedata, offset+40, 4)})
	data.append({"capturePoints": getdata(sourcedata, offset+44, 4)})
	data.append({"droppedCapturePoints": getdata(sourcedata, offset+48, 4)})
	
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
