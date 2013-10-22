###################################################
# World of Tanks Dossier Cache to JSON            #
# Initial version by Phalynx www.vbaddict.net/wot #
###################################################
import cPickle, struct, json, time, sys, os
	
def usage():
	print str(sys.argv[0]) + " dossierfilename.dat [options]"
	print 'Options:'
	print '-f Formats the JSON to be more human readable'
	print '-r Export all fields with their values and recognized names'
	print '-k Dont export Frags'
	print '-s Server Mode, disable writing of timestamp, enable logging'


def main():
	
	import cPickle, struct, json, time, sys, os, shutil, datetime, base64

	parserversion = "0.8.9.0"
	
	global rawdata, tupledata, data, structures, numoffrags, working_directory
	global filename_source, filename_target
	global option_server, option_format
	
	filename_source = ""
	option_raw = 0
	option_format = 0
	option_server = 0
	option_frags = 1
	
	for argument in sys.argv:
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
		elif argument != sys.argv[0]:
			filename_source = argument
	
	if filename_source == "":
		usage()
		sys.exit(2)
	printmessage('############################################')
	printmessage('###### WoTDC2J ' + parserversion)
	
	working_directory = os.path.dirname(os.path.realpath(__file__))
	
	printmessage('Processing ' + filename_source)
	
	tanksdata = dict()
	
	if option_server == 0:
		tanksdata = get_json_data("tanks.json")

	structures = get_json_data("structures_18.json")
	structures = structures + get_json_data("structures_20.json")
	structures = structures + get_json_data("structures_22.json")
	structures = structures + get_json_data("structures_24.json")
	structures = structures + get_json_data("structures_26.json")
	structures = structures + get_json_data("structures_27.json")
	structures = structures + get_json_data("structures_28.json")
	structures = structures + get_json_data("structures_29.json")
	structures = structures + get_json_data("structures_65.json")

	if not os.path.exists(filename_source) or not os.path.isfile(filename_source) or not os.access(filename_source, os.R_OK):
		catch_fatal('Dossier file does not exists!')
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
	  cacheobject = cPickle.load(cachefile)
	except Exception, e:
		exitwitherror('Dossier cannot be read (pickle could not be read) ' + e.message)

	if not 'cacheobject' in locals():
		exitwitherror('Dossier cannot be read (cacheobject does not exist)')

	if len(cacheobject) <> 2:
		exitwitherror('Dossier cannot be read (cacheobject empty')

	dossierCache = cacheobject[1]
	printmessage("Dossier version " + str(cacheobject[0]))
	
	tankitems = [(k, v) for k, v in dossierCache.items()]

	dossier = dict()
		
	dossierheader = dict()
	dossierheader['dossierversion'] = str(cacheobject[0])
	dossierheader['parser'] = 'http://www.vbaddict.net/wot'
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
	
	tanks = dict()
	tanks_v2 = dict()
	
	for tankitem in tankitems:

		

		try:
			tankid = tankitem[0][1] >> 8 & 65535
		except Exception, e:
			exitwitherror('cannot get tankid ' + e.message)

			
		try:
			countryid = tankitem[0][1] >> 4 & 15
		except Exception, e:
			exitwitherror('cannot get countryid ' + e.message)

		data = tankitem[1][1]
		tankstruct = str(len(data)) + 'B'
		tupledata = struct.unpack(tankstruct, data)


		rawdata = dict()
		for m in xrange(0,len(tupledata)):
			rawdata[m] = tupledata[m]
		
		if len(tupledata) == 0:
			continue

		tankversion = getdata("tankversion", 0, 1)
	
		#if (tankversion<65):
		#	continue


		if tankversion < 17: # Old
			if tankversion > 0:
				
				try:
					if option_server == 0:
						write_to_log(get_tank_data(tanksdata, countryid, tankid, "title") + ", unsupported tankversion " + str(tankversion))
					
					printmessage('unsupported tankversion')
					continue				
				except Exception, e:
					printmessage('unsupported tankversion' + e.message)
					continue



		if option_server == 0:
			tanktitle = get_tank_data(tanksdata, countryid, tankid, "title")
		else:
			tanktitle = str(countryid) + '_' + str(tankid)

		if tankversion >= 65:
			tank_v2 = dict()
			blocks = ('a15x15', 'a15x15_2', 'clan', 'clan2', 'company', 'company2', 'a7x7', 'achievements', 'frags', 'total', 'max15x15', 'max7x7')
			blockcount = len(list(blocks))+1
			newbaseoffset = (blockcount * 2)
			header = struct.unpack_from('<' + 'H' * blockcount, data)
			blocksizes = list(header[1:])
			blocknumber = 0
			fragslist = []
			numoffrags_list = 0
			numoffrags_a15x15 = 0
			
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
								countryid, tankid, tankname = get_tank_details(compDescr, tanksdata)
								tankfrag = [countryid, tankid, amount, tankname]
								fragslist.append(tankfrag)
								index += 2
						
							newbaseoffset += blocksizes[blocknumber]
							if option_frags == 1:
								tank_v2['fragslist'] = fragslist
						
					else:
						oldbaseoffset = newbaseoffset
						structureddata = getstructureddata(blockname, tankversion, newbaseoffset)
						newbaseoffset = oldbaseoffset+blocksizes[blocknumber]
						tank_v2[blockname] = structureddata

				blocknumber +=1
		
		
			if option_frags == 1:

				if contains_block('a15x15', tank_v2):
					numoffrags_a15x15 = int(tank_v2['a15x15']['frags'])

				try:
					if numoffrags_list <> numoffrags_a15x15:
						printmessage('Wrong number of frags. ' + str(numoffrags_list) + ' / ' + str(numoffrags_a15x15))
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
				"frags_compare": numoffrags_list,
				"has_15x15": contains_block("a15x15", tank_v2),
				"has_7x7": contains_block("a7x7", tank_v2),
				"has_clan": contains_block("clan", tank_v2),
				"has_company": contains_block("company", tank_v2)
				
			}
			
			if option_raw == 1:
				tank_v2['rawdata'] = rawdata

			tanks_v2[tanktitle] = tank_v2
			
			
		if tankversion < 65:
			if tankversion >= 20:
				company = getstructureddata("company", tankversion, 0)
				clan = getstructureddata("clan", tankversion, 0)
			
			numoffrags = 0
	
			structure = getstructureddata("structure", tankversion, 0)
			
			if 'fragspos' not in structure:
				write_to_log('tankversion ' + str(tankversion) + ' not in JSON')
				continue
			
			if option_frags == 1:
				fragslist = getdata_fragslist(tankversion, tanksdata, structure['fragspos'])
	
			tankdata = getstructureddata("tankdata", tankversion, 0)
	
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
	
			if option_frags == 1:
				try:
					if tankdata['frags'] <> numoffrags:
						printmessage('Wrong number of frags!')
				except Exception, e:
						write_to_log('Error processing frags: ' + e.message)
	
			series = getstructureddata("series", tankversion, 0)
	
			special = getstructureddata("special", tankversion, 0)
	
			battle = getstructureddata("battle", tankversion, 0)
	
			major = getstructureddata("major", tankversion, 0)
	
			epic = getstructureddata("epic", tankversion, 0)
	
	
	
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

		
		

	dossierheader['result'] = "ok"
	dossierheader['message'] = "ok"
	
	dossier['header'] = dossierheader
	dossier['tanks'] = tanks
	dossier['tanks_v2'] = tanks_v2

	dumpjson(dossier)

	printmessage('###### Done!')
	printmessage('')
	sys.exit(0)
	


############################################################################################################################

def contains_block(blockname, blockdata):
	
	if blockname in blockdata:
		return 1
	
	return 0


def get_tank_details(compDescr, tanksdata):

	tankid = compDescr >> 8 & 65535
	countryid = compDescr >> 4 & 15
		
	if option_server == 0:
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
		
	write_to_log("ERROR: " + str(message))


def write_to_log(logtext):
	global working_directory, option_server
	import datetime, os
	
	printmessage(logtext)
	now = datetime.datetime.now()
	
	#working_directory
	if option_server == 1:
		try:
			logFile = open("/var/log/wotdc2j/wotdc2j.log", "a+b")
			logFile.write(str(now.strftime("%Y-%m-%d %H:%M:%S")) + " # " + str(logtext) + " # " + str(filename_source) + "\r\n")
			logFile.close()
		except:
			printmessage("Cannot write to wotdc2j.log")
		

def getstructureddata(category, tankversion, baseoffset):
	global sourcedata, structures

	returndata = dict()

	for structureitem in structures:
		if category == structureitem['category']:
			if tankversion == structureitem['version']:
				offset = structureitem['offset']
				if baseoffset > 0:
					offset += baseoffset
				returndata[structureitem['name']] = getdata(category + " " + structureitem['name'], offset, structureitem['length'])

	return returndata

def get_json_data(filename):
	import json, time, sys, os
	
	#os.chdir(os.getcwd())
	os.chdir(sys.path[0])
	
	
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

	if option_server == 0:
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




if __name__ == '__main__':
	main()
