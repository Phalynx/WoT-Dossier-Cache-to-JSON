###################################################
# World of Tanks Dossier Cache to JSON            #
# Initial version by Phalynx www.vbaddict.net     #
###################################################
import struct, json, time, sys, os
	
def usage():
	print str(sys.argv[0]) + " dossierfilename.dat [options]"
	print 'Options:'
	print '-f Formats the JSON to be more human readable'
	print '-r Export all fields with their values and recognized names'
	print '-k Dont export Frags'
	print '-s Server Mode, disable writing of timestamp, enable logging'


def main():
	
	import struct, json, time, sys, os, shutil, datetime, base64

	parserversion = "0.9.2.1"
	
	global rawdata, tupledata, data, structures, numoffrags
	global filename_source, filename_target
	global option_server, option_format, option_tanks
	
	filename_source = ""
	option_raw = 0
	option_format = 0
	option_server = 0
	option_frags = 1
	option_tanks = 0
	
	for argument in sys.argv:
		#print "--+++++ " + str(argument)
		if argument == "-s":
			option_server = 1
			#print '-- SERVER mode enabled'
		elif argument == "-r":
			option_raw = 1
			#print '-- RAW mode enabled'
		elif argument == "-f":
			option_format = 1
			#print '-- FORMAT mode enabled'
		elif argument == "-k":
			option_frags = 0
			#print '-- FRAGS will be excluded'
		elif argument == "-t":
			option_tanks = 1
			#print '-- TANK info will be included'

	filename_source = sys.argv[1]
	
	if filename_source == "":
		usage()
		sys.exit(2)
		
	printmessage('############################################')
	printmessage('###### WoTDC2J ' + parserversion)
	

	printmessage('Processing ' + filename_source)
	

	if not os.path.exists(filename_source) or not os.path.isfile(filename_source) or not os.access(filename_source, os.R_OK):
		catch_fatal('Dossier file does not exists')
		sys.exit(1)

	if os.path.getsize(filename_source) == 0:
		catch_fatal('Dossier file size is zero')
		sys.exit(1)
		
	filename_target = os.path.splitext(filename_source)[0]
	filename_target = filename_target + '.json'

	if os.path.exists(filename_target) and os.path.isfile(filename_target) and os.access(filename_target, os.R_OK):
		try:
			os.remove(filename_target)
		except:
			catch_fatal('Cannot remove target file ' + filename_target)

			
	cachefile = open(filename_source, 'rb')

	try:
		from SafeUnpickler import SafeUnpickler
		dossierversion, dossierCache = SafeUnpickler.load(cachefile)
	except Exception, e:
		exitwitherror('Dossier cannot be read (pickle could not be read) ' + e.message)

	if not 'dossierCache' in locals():
		exitwitherror('Dossier cannot be read (dossierCache does not exist)')

	printmessage("Dossier version " + str(dossierversion))
	
	tankitems = [(k, v) for k, v in dossierCache.items()]

	dossier = dict()
		
	dossierheader = dict()
	dossierheader['dossierversion'] = str(dossierversion)
	dossierheader['parser'] = 'http://www.vbaddict.net'
	dossierheader['parserversion'] = parserversion
	dossierheader['tankcount'] = len(tankitems)
	

	
	base32name = "?;?"
	if option_server == 0:
		try:
			base32name = base64.b32decode(os.path.splitext(filename_source)[0].replace('.\\', ''))
		except Exception, e:
			if e.message != 'Incorrect padding':
				printmessage('cannot decode filename ' + os.path.splitext(filename_source)[0] + ': ' + e.message)


	dossierheader['server'] = base32name.split(';', 1)[0];
	dossierheader['username'] = base32name.split(';', 1)[1];
	
	
	if option_server == 0:
		dossierheader['date'] = time.mktime(time.localtime())

	tanksdata = dict()
	if option_server == 0 or option_tanks == 1:
		tanksdata = get_json_data("tanks.json")
	
	structures = load_structures()
	
	tanks = dict()
	tanks_v2 = dict()
	
	battleCount_15 = 0
	battleCount_7 = 0
	battleCount_historical = 0
	battleCount_company = 0
	battleCount_clan = 0
	battleCount_fortBattles = 0
	battleCount_fortSorties = 0
	
	for tankitem in tankitems:
		
		if len(tankitem) < 2:
			printmessage('Invalid tankdata')
			continue

		if len(tankitem[0]) < 2:
			printmessage('Invalid tankdata')
			continue
			
		rawdata = dict()
		data = tankitem[1][1]
		tankstruct = str(len(data)) + 'B'
		tupledata = struct.unpack(tankstruct, data)
		tankversion = getdata("tankversion", 0, 1)
		
		#if tankversion != 85:
		#write_to_log("Tankversion " + str(tankversion))
			#continue
		
		if tankversion not in structures:
				try:
					write_to_log('unsupported tankversion ' + str(tankversion))
					printmessage('unsupported tankversion ' + str(tankversion))
					continue				
				except Exception, e:
					printmessage('unsupported tankversion ' + str(tankversion) + ' (' + e.message + ')')
					continue

		if not isinstance(tankitem[0][1], (int)):
			printmessage('Invalid tankdata')
			continue
	
		try:
			tankid = tankitem[0][1] >> 8 & 65535
		except Exception, e:
			exitwitherror('cannot get tankid ' + e.message)
			continue

			
		try:
			countryid = tankitem[0][1] >> 4 & 15
		except Exception, e:
			exitwitherror('cannot get countryid ' + e.message)
			continue

		#if tankid==234 and countryid==1:
		#	continue
		
		for m in xrange(0,len(tupledata)):
			rawdata[m] = tupledata[m]
		
		if len(tupledata) == 0:
			continue

		if option_server == 0:
			tanktitle = get_tank_data(tanksdata, countryid, tankid, "title")
		else:
			tanktitle = str(countryid) + '_' + str(tankid)

		fragslist = []
		if tankversion >= 65:
			tank_v2 = dict()
			
			
			if tankversion == 65:
				blocks = ('a15x15', 'a15x15_2', 'clan', 'clan2', 'company', 'company2', 'a7x7', 'achievements', 'frags', 'total', 'max15x15', 'max7x7')
				
			if tankversion == 69:
				blocks = ('a15x15', 'a15x15_2', 'clan', 'clan2', 'company', 'company2', 'a7x7', 'achievements', 'frags', 'total', 'max15x15', 'max7x7', 'playerInscriptions', 'playerEmblems', 'camouflages', 'compensation', 'achievements7x7')

			if tankversion == 77:
				blocks = ('a15x15', 'a15x15_2', 'clan', 'clan2', 'company', 'company2', 'a7x7', 'achievements', 'frags', 'total', 'max15x15', 'max7x7', 'playerInscriptions', 'playerEmblems', 'camouflages', 'compensation', 'achievements7x7', 'historical', 'maxHistorical') #, 'historicalAchievements', 'uniqueAchievements'

			if tankversion == 81:
				blocks = ('a15x15', 'a15x15_2', 'clan', 'clan2', 'company', 'company2', 'a7x7', 'achievements', 'frags', 'total', 'max15x15', 'max7x7', 'playerInscriptions', 'playerEmblems', 'camouflages', 'compensation', 'achievements7x7', 'historical', 'maxHistorical', 'historicalAchievements', 'fortBattles', 'maxFort', 'fortSorties', 'maxSorties', 'fortAchievements')

			if tankversion == 85:
				blocks = ('a15x15', 'a15x15_2', 'clan', 'clan2', 'company', 'company2', 'a7x7', 'achievements', 'frags', 'total', 'max15x15', 'max7x7', 'playerInscriptions', 'playerEmblems', 'camouflages', 'compensation', 'achievements7x7', 'historical', 'maxHistorical', 'historicalAchievements', 'fortBattles', 'maxFort', 'fortSorties', 'maxSorties', 'fortAchievements', 'singleAchievements', 'clanAchievements')
			
			blockcount = len(list(blocks))+1
			#print blockcount
			newbaseoffset = (blockcount * 2)
			header = struct.unpack_from('<' + 'H' * blockcount, data)
			blocksizes = list(header[1:])
			blocknumber = 0
			numoffrags_list = 0
			numoffrags_a15x15 = 0
			numoffrags_a7x7 = 0
			numoffrags_historical = 0
			numoffrags_fortBattles = 0
			numoffrags_fortSorties = 0
			
			for blockname in blocks:
				

				if blocksizes[blocknumber] > 0:
					if blockname == 'frags':
							fmt = '<' + 'IH' * (blocksizes[blocknumber]/6)
							fragsdata = struct.unpack_from(fmt, data, newbaseoffset)
							
						 	for x in range(0, blocksizes[blocknumber]):
						 		rawdata[newbaseoffset+x] = str(tupledata[newbaseoffset+x]) + " / Frags; "

							index = 0
							for i in xrange((blocksizes[blocknumber]/6)):
								compDescr, amount = (fragsdata[index], fragsdata[index + 1])
								numoffrags_list += amount	
								frag_countryid, frag_tankid, frag_tanktitle = get_tank_details(compDescr, tanksdata)
								tankfrag = [frag_countryid, frag_tankid, amount, frag_tanktitle]
								fragslist.append(tankfrag)
								index += 2
						
							newbaseoffset += blocksizes[blocknumber]
							if option_frags == 1:
								tank_v2['fragslist'] = fragslist
						
					else:
						oldbaseoffset = newbaseoffset
						structureddata = getstructureddata(blockname, tankversion, newbaseoffset)
						structureddata = keepCompatibility(structureddata)
						newbaseoffset = oldbaseoffset+blocksizes[blocknumber]
						tank_v2[blockname] = structureddata

				blocknumber +=1
		
			if contains_block('company', tank_v2):
				if 'battlesCount' in tank_v2['company']:
					battleCount_company += tank_v2['company']['battlesCount']
			
			if contains_block('clan', tank_v2):
				if 'battlesCount' in tank_v2['clan']:
					battleCount_company += tank_v2['clan']['battlesCount']

			if contains_block('a15x15', tank_v2):
				
				if 'battlesCount' in tank_v2['a15x15']:
					battleCount_15 += tank_v2['a15x15']['battlesCount']
					
				if 'frags' in tank_v2['a15x15']:
					numoffrags_a15x15 = int(tank_v2['a15x15']['frags'])

			if contains_block('a7x7', tank_v2):
				
				if 'battlesCount' in tank_v2['a7x7']:
					battleCount_7 += tank_v2['a7x7']['battlesCount']
				
				if 'frags' in tank_v2['a7x7']:
					numoffrags_a7x7 = int(tank_v2['a7x7']['frags'])
			
			if contains_block('historical', tank_v2):
				
				if 'battlesCount' in tank_v2['historical']:
					battleCount_historical += tank_v2['historical']['battlesCount']
				
				if 'frags' in tank_v2['historical']:
					numoffrags_historical = int(tank_v2['historical']['frags'])

			if contains_block('fortBattles', tank_v2):
				
				if 'battlesCount' in tank_v2['fortBattles']:
					battleCount_fortBattles += tank_v2['fortBattles']['battlesCount']
				
				if 'frags' in tank_v2['fortBattles']:
					numoffrags_fortBattles = int(tank_v2['fortBattles']['frags'])
					
			if contains_block('fortSorties', tank_v2):
				
				if 'battlesCount' in tank_v2['fortSorties']:
					battleCount_fortSorties += tank_v2['fortSorties']['battlesCount']
				
				if 'frags' in tank_v2['fortSorties']:
					numoffrags_fortSorties = int(tank_v2['fortSorties']['frags'])
					
			if option_frags == 1:

				try:
					if numoffrags_list <> (numoffrags_a15x15 + numoffrags_a7x7 + numoffrags_historical + numoffrags_fortBattles + numoffrags_fortSorties):
						printmessage('Wrong number of frags. ' + str(numoffrags_list) + ' = ' + str(numoffrags_a15x15) + ' + ' + str(numoffrags_a7x7) + ' + ' + str(numoffrags_historical) + ' + ' + str(numoffrags_fortBattles) + ' + ' + str(numoffrags_fortSorties))
				except Exception, e:
						write_to_log('Error processing frags: ' + e.message)
		
			
				
			tank_v2['common'] = {"countryid": countryid,
				"tankid": tankid,
				"tanktitle": tanktitle,
				"compactDescr": tankitem[0][1],
				"type": get_tank_data(tanksdata, countryid, tankid, "type"),
				"premium": get_tank_data(tanksdata, countryid, tankid, "premium"),
				"tier": get_tank_data(tanksdata, countryid, tankid, "tier"),
				"updated": tankitem[1][0],
				"updatedR": datetime.datetime.fromtimestamp(int(tankitem[1][0])).strftime('%Y-%m-%d %H:%M:%S'),
				"creationTime": tank_v2['total']['creationTime'],
				"creationTimeR": datetime.datetime.fromtimestamp(int(tank_v2['total']['creationTime'])).strftime('%Y-%m-%d %H:%M:%S'),
				"lastBattleTime": tank_v2['total']['lastBattleTime'],
				"lastBattleTimeR": datetime.datetime.fromtimestamp(int(tank_v2['total']['lastBattleTime'])).strftime('%Y-%m-%d %H:%M:%S'),
				"basedonversion": tankversion,
				"frags":  numoffrags_a15x15,
				"frags_7x7":  numoffrags_a7x7,
				"frags_historical":  numoffrags_historical,
				"frags_compare": numoffrags_list,
				"has_15x15": contains_block("a15x15", tank_v2),
				"has_7x7": contains_block("a7x7", tank_v2),
				"has_historical": contains_block("historical", tank_v2),
				"has_clan": contains_block("clan", tank_v2),
				"has_company": contains_block("company", tank_v2),
				"has_fort": contains_block("fortBattles", tank_v2),
				"has_sortie": contains_block("fortSorties", tank_v2)
				
			
				
				
			}
			
			if option_raw == 1:
				tank_v2['rawdata'] = rawdata

			tanks_v2[tanktitle] = tank_v2
			
			
		if tankversion < 65:
			if tankversion >= 20:
				company = getstructureddata("company", tankversion)
				battleCount_company += company['battlesCount']
				clan = getstructureddata("clan", tankversion)
				battleCount_clan += clan['battlesCount']
			
			numoffrags = 0
	
			structure = getstructureddata("structure", tankversion)


			
			if 'fragspos' not in structure:
				write_to_log('tankversion ' + str(tankversion) + ' not in JSON')
				continue
			
			if option_frags == 1 and tankversion >= 17:
				fragslist = getdata_fragslist(tankversion, tanksdata, structure['fragspos'])
	
			tankdata = getstructureddata("tankdata", tankversion)
			battleCount_15 += tankdata['battlesCount']
	
			if not "creationTime" in tankdata:
				tankdata['creationTime'] = 1356998400
	
			common = {"countryid": countryid,
				"tankid": tankid,
				"tanktitle": tanktitle,
				"compactDescr": tankitem[0][1],
				"type": get_tank_data(tanksdata, countryid, tankid, "type"),
				"premium": get_tank_data(tanksdata, countryid, tankid, "premium"),
				"tier": get_tank_data(tanksdata, countryid, tankid, "tier"),
				"updated": tankitem[1][0],
				"updatedR": datetime.datetime.fromtimestamp(int(tankitem[1][0])).strftime('%Y-%m-%d %H:%M:%S'),
				"creationTime": tankdata['creationTime'],
				"creationTimeR": datetime.datetime.fromtimestamp(int(tankdata['creationTime'])).strftime('%Y-%m-%d %H:%M:%S'),
				"lastBattleTime": tankdata['lastBattleTime'],
				"lastBattleTimeR": datetime.datetime.fromtimestamp(int(tankdata['lastBattleTime'])).strftime('%Y-%m-%d %H:%M:%S'),
				"basedonversion": tankversion,
				"frags": tankdata['frags'],
				"frags_compare": numoffrags
			}
	
			if option_frags == 1 and tankversion >= 17:
				try:
					if tankdata['frags'] <> numoffrags:
						printmessage('Wrong number of frags!')
				except Exception, e:
						write_to_log('Error processing frags: ' + e.message)
	
			series = getstructureddata("series", tankversion)
	
			special = getstructureddata("special", tankversion)
	
			battle = getstructureddata("battle", tankversion)
	
			major = getstructureddata("major", tankversion)
	
			epic = getstructureddata("epic", tankversion)
	
	
	
			tank = dict()
			
			tank['tankdata'] = tankdata
			tank['common'] = common
	
			if tankversion >= 20:
				tank['series'] = series
				tank['battle'] = battle
				tank['special'] = special
				tank['epic'] = epic
				tank['major'] = major
				tank['clan'] = clan
				tank['company'] = company
				
			if option_frags == 1:
				tank['kills'] = fragslist
			
			if option_raw == 1:
				tank['rawdata'] = rawdata
			
			tanks[tanktitle] = tank
			#tanks = sorted(tanks.values())

	
	dossierheader['battleCount_15'] = battleCount_15	
	dossierheader['battleCount_7'] = battleCount_7
	dossierheader['battleCount_historical'] = battleCount_historical
	dossierheader['battleCount_company'] = battleCount_company
	dossierheader['battleCount_clan'] = battleCount_clan

	dossierheader['result'] = "ok"
	dossierheader['message'] = "ok"
	
	dossier['header'] = dossierheader
	dossier['tanks'] = tanks
	dossier['tanks_v2'] = tanks_v2

	dumpjson(dossier)

	printmessage('###### Done!')
	printmessage('')
	sys.exit(0)
	
	
def get_current_working_path():
	#workaround for py2exe
	import sys, os
	
	try:
		if hasattr(sys, "frozen"):
			return os.path.dirname(unicode(sys.executable, sys.getfilesystemencoding( )))
		else:
			return sys.path[0]
	except Exception, e:
		print e.message

############################################################################################################################

def contains_block(blockname, blockdata):
	
	if blockname in blockdata:
		return 1
	
	return 0


def get_tank_details(compDescr, tanksdata):

	tankid = compDescr >> 8 & 65535
	countryid = compDescr >> 4 & 15
		
	if option_server == 0 or option_tanks == 1:
		tankname = get_tank_data(tanksdata, countryid, tankid, "title")
	else:
		tankname = "-"	

	return countryid, tankid, tankname


def printmessage(message):
	global option_server
	
	if option_server == 0:
		print message


def exitwitherror(message):
	catch_fatal(message)
	dossier = dict()
	dossierheader = dict()
	dossierheader['result'] = "error"
	dossierheader['message'] = message
	dossier['header'] = dossierheader
	dumpjson(dossier)
	sys.exit(1)


def dumpjson(dossier):
	global option_format, option_server, filename_target
	
	try:
		
		if option_server == 0:
			finalfile = open(filename_target, 'w')
		
			if option_format == 1:
				finalfile.write(json.dumps(dossier, sort_keys=True, indent=4))
			else:
				finalfile.write(json.dumps(dossier))
		else:
			print json.dumps(dossier)
	except Exception, e:
		printmessage(e)
		

def catch_fatal(message):
	global option_server
	import shutil
		
	write_to_log("WOTDC2J: " + str(message))


def write_to_log(logtext):
	global option_server
	import datetime, os
	
	printmessage(logtext)
	now = datetime.datetime.now()
	
	if option_server == 1:
		try:
			logFile = open("/var/log/wotdc2j/wotdc2j.log", "a+b")
			logFile.write(str(now.strftime("%Y-%m-%d %H:%M:%S")) + " # " + str(logtext) + " # " + str(filename_source) + "\r\n")
			logFile.close()
		except:
			printmessage("Cannot write to wotdc2j.log")


def getstructureddata(category, tankversion, baseoffset=0):
	
	returndata = dict()
	
	if tankversion in structures:
		if category in structures[tankversion]:
			for item in structures[tankversion][category]:
				returndata[item['name']] = getdata(category + " " + item['name'], item['offset']+baseoffset, item['length'])
	
	return returndata


def keepCompatibility(structureddata):
	# Compatibility with older versions
	# Some names changed in WoT 0.9.0
		
	if 'directHits' in structureddata:
		structureddata['hits'] = structureddata['directHits']
		
	if 'explosionHits' in structureddata:
		structureddata['he_hits'] = structureddata['explosionHits']
		
	if 'piercings' in structureddata:
		structureddata['pierced'] = structureddata['piercings']
				
	if 'explosionHitsReceived' in structureddata:
		structureddata['heHitsReceived'] = structureddata['explosionHitsReceived']
		
	if 'directHitsReceived' in structureddata:
		structureddata['shotsReceived'] = structureddata['directHitsReceived']
		
	if 'noDamageDirectHitsReceived' in structureddata:
		structureddata['noDamageShotsReceived'] = structureddata['noDamageDirectHitsReceived']
		

	return structureddata




def get_json_data(filename):
	import json, time, sys, os
	

	current_working_path = get_current_working_path()

	os.chdir(current_working_path)
	
	if not os.path.exists(filename) or not os.path.isfile(filename) or not os.access(filename, os.R_OK):
		catch_fatal(filename + " does not exists!")
		sys.exit(1)

	file_json = open(filename, 'r')

	try:
		file_data = json.load(file_json)
	except Exception, e:
		catch_fatal(filename + " cannot be loaded as JSON: " + e.message)
		sys.exit(1)
		
		
	file_json.close()

	return file_data



def get_tank_data(tanksdata, countryid, tankid, dataname):

	if option_server == 0 or option_tanks == 1:
		for tankdata in tanksdata:
			if tankdata['countryid'] == countryid:
				if tankdata['tankid'] == tankid:
					return tankdata[dataname]
	
	if dataname == 'title':
		return 'unknown_' + str(countryid) + '_' + str(tankid)


	return "-"


def getdata_fragslist(tankversion, tanksdata, offset):
	global tupledata, numoffrags

	fragslist = []

	offset = offset + 2

	if len(tupledata) > offset:

		numfrags = getdata("Number of frags", offset-2, 2)

		if numfrags > 0:
			for m in xrange(0, numfrags):

				tankoffset = offset + m*4
				fragoffset = offset + numfrags*4+m*2

				compDescr = getdata("Frag tankid", tankoffset, 2)
				amount = getdata("Frag amount", fragoffset, 2)

				countryid, tankid, tankname = get_tank_details(compDescr, tanksdata)
				numoffrags = numoffrags + amount
				
				
				tankfrag = [countryid, tankid, amount, tankname]
				fragslist.append(tankfrag)

	return fragslist


def getdata(name, startoffset, offsetlength):
	global rawdata, tupledata, data

	if len(data)<startoffset+offsetlength:
		return 0
	
	structformat = 'H'

	if offsetlength==1:
		structformat = 'B'

	if offsetlength==2:
		structformat = 'H'
		
	if offsetlength==4:
		structformat = 'I'

	value = struct.unpack_from('<' + structformat, data, startoffset)[0]
 	
 	for x in range(0, offsetlength):
 		rawdata[startoffset+x] = str(tupledata[startoffset+x]) + " / " + str(value) +  "; " + name

	
 	return value


def load_structures():
	
	structures = dict()
	
	load_versions = [10,17,18,20,22,24,26,27,28,29,65,69,77,81,85];
	for version in load_versions:
		jsondata = get_json_data('structures_'+str(version)+'.json')
		structures[version] = dict()
		for item in jsondata:
			category = item['category']
			if category not in structures[version]:
				structures[version][category] = list()
			structures[version][category].append(item)
	
	return structures


if __name__ == '__main__':
	main()
