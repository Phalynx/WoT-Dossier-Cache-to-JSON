###################################################
# World of Tanks Dossier Cache to JSON 7.5        #
# Initial version by Phalynx www.vbaddict.net/wot #
###################################################
import cPickle, struct, json, time, sys, os




def main():
	import cPickle, struct, json, time, sys, os
	
	global rawdata, sourcedata, structures
	
	filename_source = str(sys.argv[1])
	
	print '###### WoTDC2J 7.5'
	
	if len(sys.argv) == 3:
		print 'DEBUG mode enabled'
	
	print 'Processing ' + filename_source
	
	tanksdata = get_json_data("tanks.json")

	structures = get_json_data("structures.json")

	
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
			
	cachefile = open(filename_source, 'rb')

	try:
	  cacheobject = cPickle.load(cachefile)
	except: 
	  print "Unable to load data"

	if not 'cacheobject' in locals():
		sys.exit(1)

	if len(cacheobject) <> 2:
		sys.exit(1)
		
	dossierCache = cacheobject[1]
	
	tankitems = [(k, v) for k, v in dossierCache.items()]
	
	dossier = []
	dossier.append({
		"tankcount": len(tankitems), 
		"date": time.mktime(time.localtime()),
		"parser": 'http://www.vbaddict.net/wot', 
		"parserversion": 75
	})
	
	
	tanks = []
	for tankitem in tankitems:
	
	
		tankid = tankitem[0][1] //256
		countryid = ((tankitem[0][1] - tankid*256)-1) //16
		
		tanktitle = get_tank_title(tanksdata, countryid, tankid)

		#print tanktitle		

		data = tankitem[1][1]
		tankstruct = str(len(data)) + 'B'
		sourcedata = struct.unpack(tankstruct, data)
			
					
		rawdata = dict()
		for m in xrange(0,len(sourcedata)):
			rawdata[m] = sourcedata[m]
			
		
		tankversion = getdata("Tankversion", 0, 1) 
		
		if tankversion == 0: # Unknown
			continue
	
		if tankversion == 10: # Old
			continue
	
		
		if tankversion >= 20:
		
			# Data for company battles / Global War
			company = []
			
			if tankversion == 20:
				if getdata("Company", 161, 4) > 0:
					company = getdata_tank_specific(161)

			if tankversion == 22:
				if getdata("Company", 174, 4) > 0:
					company = getdata_tank_specific(174)

		
			# Currently unused as of WoT v0.7.4
			clan = []

			if tankversion == 20:
				if getdata("Clan", 213, 4) > 0:
					clan = getdata_tank_specific(213)

			if tankversion == 22:
				if getdata("Clan", 226, 4) > 0:
					clan = getdata_tank_specific(226)



		tankdata = getstructureddata("tankdata", tankversion)
		
		fragslist = getdata_fragslist(tankversion)
		
		series = getstructureddata("series", tankversion)
		
		special = getstructureddata("special", tankversion)
	
		battle = getstructureddata("battle", tankversion)
	
		major = getstructureddata("major", tankversion)
	
		epic = getstructureddata("epic", tankversion)
		
		unknown = getstructureddata("unknown", tankversion)


		
		common = {"countryid": countryid,
			"tankid": tankid,
			"tanktitle": tanktitle,
			"updated": tankitem[1][0],
			"lastBattleTime": tankitem[1][0],
			"basedonversion": tankversion
		}

			
		if tankversion >= 20:
			tank = {
				"common": common,
				"tankdata": tankdata,
				"unknown": unknown,
				"series": series,
				"battle": battle,
				"special": special,		
				"epic": epic,
				"major": major,
				"clan": clan,
				"company": company
				#"kills": fragslist
			}
		else:
			tank = {
				"common": common,
				"tankdata": tankdata,
				"unknown": unknown,
				"kills": fragslist
			}
			
	
		tanks.append({"tank": tank})
		
		if len(sys.argv) == 3:
			tanks.append({"rawdata": rawdata})
			

		
	dossier.append({"tanks": tanks})
		
	
	print 'Dumping to JSON'
	
	finalfile = open(filename_target, 'w')
	
	if len(sys.argv) == 3:
		finalfile.write(json.dumps(dossier, sort_keys=True, indent=4))
	else:
		finalfile.write(json.dumps(dossier))
	
	print 'Done!'
	sys.exit(0)



############################################################################################################################
def getstructureddata(category, tankversion):

	global sourcedata, structures
	
	returndata = dict()

	for structureitem in structures:
		if category == structureitem['category']:
			if tankversion == structureitem['version']:
				returndata[structureitem['name']] = getdata(category + " " + structureitem['name'], structureitem['offset'], structureitem['length'])

	return returndata
		
	
def get_json_data(filename):
	import json, time, sys, os
	if os.path.exists(filename) and os.path.isfile(filename) and os.access(filename, os.R_OK):
		print filename + " exists and is readable"
	else:
		print filename + " does not exists!"
		sys.exit(1)
	
	file_json = open(filename, 'r')

	file_data = json.load(file_json)
	file_json.close()

	return file_data



def get_tank_title(tanksdata, countryid, tankid):

	for tankdata in tanksdata:
		if tankdata['countryid'] == countryid:
			if tankdata['tankid'] == tankid:
				return tankdata['title']
			
	return "unknown"


def getdata_fragslist(tankversion):

	global sourcedata		

	fragslist = []
	
	if tankversion < 20:
		offset = 138

	if tankversion == 20:
		offset = 269

	if tankversion == 22:
		offset = 282
	
	if len(sourcedata) > offset:

		numfrags = getdata("Kill number of frags", offset-2, 2)
	
		if numfrags > 0:			
			for m in xrange(0, numfrags):
	
				tankoffset = offset + m*4
				killoffset = offset + numfrags*4+m*2
	
				ptankid = getdata("Kill tankid", tankoffset, 2)
				amount = getdata("kill amount", killoffset, 2)
				
				tankid = ptankid //256
				countryid = ((ptankid - tankid*256)-1) //16
				
				tankill = [countryid, tankid, amount]
				fragslist.append(tankill)

	return fragslist


	
	
	
def getdata_tank_specific(offset):
	
	global sourcedata
	
	data = []
	data = {"xp": getdata("Tankdata xp", offset, 4),
		"battlesCount": getdata("Tankdata battlesCount", offset+4, 4),
		"wins": getdata("Tankdata wins", offset+8, 4),
		"losses": getdata("Tankdata losses", offset+12, 4),
		"survivedBattles": getdata("Tankdata survivedBattles", offset+16, 4),
		"frags": getdata("Tankdata frags", offset+20, 4),
		"shots": getdata("Tankdata shots", offset+24, 4),
		"hits": getdata("Tankdata hits", offset+28, 4),
		"spotted": getdata("Tankdata spotted", offset+32, 4),
		"damageDealt": getdata("Tankdata damageDealt", offset+36, 4),
		"damageReceived": getdata("Tankdata damageReceived", offset+40, 4),
		"capturePoints": getdata("Tankdata capturePoints", offset+44, 4),
		"droppedCapturePoints": getdata("Tankdata droppedCapturePoints", offset+48, 4),
	}
	
	return data

	
def getdata(name, startoffset, offsetlength):

	global rawdata, sourcedata

	if len(sourcedata)<startoffset+offsetlength:
		
		return 0

	if offsetlength == 1:
				
		value = sourcedata[startoffset]
		
		rawdata[startoffset] = str(value) + ";" + name
		
		#print str(startoffset) + ";" + str(value) + ";" + name

		return value 
		
	elif offsetlength == 2:
		
		value = sourcedata[startoffset] + 256*sourcedata[startoffset+1] 
		
		rawdata[startoffset] = str(value) + ";" + name
		rawdata[startoffset+1] = str(value) + ";" + name

		return value 

	elif offsetlength == 3:
		
		value = sourcedata[startoffset] + 256*sourcedata[startoffset+1] + 256*256*sourcedata[startoffset+2]
		
		rawdata[startoffset] = str(value) + ";" + name
		rawdata[startoffset+1] = str(value) + ";" + name
		rawdata[startoffset+2] = str(value) + ";" + name

		return value 

	elif offsetlength == 4:
		
		value = sourcedata[startoffset] + 256*sourcedata[startoffset+1] + 256*256*sourcedata[startoffset+2] + 256*256*256*sourcedata[startoffset+3]

		rawdata[startoffset] = str(value) + ";" + name
		rawdata[startoffset+1] = str(value) + ";" + name
		rawdata[startoffset+2] = str(value) + ";" + name
		rawdata[startoffset+3] = str(value) + ";" + name
		
		return value
		
	else:
	  return 0

	
		
if __name__ == '__main__':
	main()
