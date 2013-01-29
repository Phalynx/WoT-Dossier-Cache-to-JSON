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
	print '-k Dont export Kills/Frags'
	print '-s Server Mode, disable writing of timestamp, enable logging'


def main():
	
	import cPickle, struct, json, time, sys, os, shutil, datetime, base64
	
	parserversion = "0.8.3.0"

	print '###### WoTDC2J ' + parserversion

	global rawdata, sourcedata, structures, numofkills, filename_source, working_directory, option_server
	option_raw = 0
	option_format = 0
	option_server = 0
	option_frags = 1
	
	working_directory = os.path.dirname(os.path.realpath(__file__))
	
	if len(sys.argv) == 1:
		usage()
		sys.exit(2)

	for argument in sys.argv:
		if argument == "-r":
			option_raw = 1
			print '-- RAW mode enabled'
		elif argument == "-f":
			option_format = 1
			print '-- FORMAT mode enabled'
		elif argument == "-s":
			option_server = 1
			print '-- SERVER mode enabled'
		elif argument == "-k":
			option_frags = 0
			print '-- KILLS/FRAGS will be excluded'

	filename_source = str(sys.argv[1])

	print 'Processing ' + filename_source
	
	tanksdata = dict()
	
	if option_server == 0:
		tanksdata = get_json_data("tanks.json")

	structures = get_json_data("structures_18.json")
	structures = structures + get_json_data("structures_20.json")
	structures = structures + get_json_data("structures_22.json")
	structures = structures + get_json_data("structures_24.json")
	structures = structures + get_json_data("structures_26.json")

	


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
		catch_fatal('Dossier cannot be read (pickle could not be read) ' + e.message)
		sys.exit(1)

	if not 'cacheobject' in locals():
		catch_fatal('Dossier cannot be read (cacheobject does not exist)')
		sys.exit(1)

	if len(cacheobject) <> 2:
		catch_fatal('Dossier cannot be read (cacheobject empty')
		sys.exit(1)

	dossierCache = cacheobject[1]
	#print dossierCache
	tankitems = [(k, v) for k, v in dossierCache.items()]

	dossier = dict()
		
	dossierheader = dict()
	dossierheader['tankcount'] = len(tankitems)
	dossierheader['parser'] = 'http://www.vbaddict.net/wot'
	dossierheader['parserversion'] = parserversion
	dossierheader['tankcount'] = len(tankitems)

	
	base32name = "?;?"
	try:
		base32name = base64.b32decode(os.path.splitext(filename_source)[0].replace('.\\', ''))
	except Exception, e:
		# nothing
		print 'cannot decode filename ' + os.path.splitext(filename_source)[0] + ': ' + e.message

	dossierheader['server'] = base32name.split(';', 1)[0];
	dossierheader['username'] = base32name.split(';', 1)[1];

	
	if option_server == 0:
		dossierheader['date'] = time.mktime(time.localtime())
	
	
	dossier['header'] = dossierheader
	


	tanks = dict()
	for tankitem in tankitems:


		try:
			tankid = tankitem[0][1] //256
		except Exception, e:
			catch_fatal('cannot get tankid ' + e.message)
			sys.exit(1)
			
		try:
			countryid = ((tankitem[0][1] - tankid*256)-1) //16
		except Exception, e:
			catch_fatal('cannot get countryid ' + e.message)
			sys.exit(1)
		

		data = tankitem[1][1]
		tankstruct = str(len(data)) + 'B'
		sourcedata = struct.unpack(tankstruct, data)


		rawdata = dict()
		for m in xrange(0,len(sourcedata)):
			rawdata[m] = sourcedata[m]
		
		if len(sourcedata) == 0:
			continue

		tankversion = getdata("tankversion", 0, 1)
		#tankversion = tankversion - 1
		#rawdata[0] = str(tankversion) + " / " + str(tankversion) +  "; tankversion"
	
		#print "V: " + str(tankversion)
	
		if tankversion < 17: # Old
			if tankversion > 0:
				
				try:
					if option_server == 0:
						print get_tank_data(tanksdata, countryid, tankid, "title") + ", unsupported tankversion " + str(tankversion)
					catch_fatal('unsupported tankversion')
					continue				
				except Exception, e:
					catch_fatal('unsupported tankversion' + e.message)
					continue

		if tankversion >= 20:
			company = getstructureddata("company", tankversion)
			clan = getstructureddata("clan", tankversion)
		
		numofkills = 0

		#getdata("fragspos", structureitem['offset'], structureitem['length'])
		structure = getstructureddata("structure", tankversion)
		#print structure['fragspos']
		fragslist = getdata_fragslist(tankversion, tanksdata, structure['fragspos'])

		tankdata = getstructureddata("tankdata", tankversion)

		try:
			if tankdata['frags'] <> numofkills:
				print 'Wrong number of kills!'
		except Exception, e:
				print 'Frags does not exists!'

		series = getstructureddata("series", tankversion)

		special = getstructureddata("special", tankversion)

		battle = getstructureddata("battle", tankversion)

		major = getstructureddata("major", tankversion)

		epic = getstructureddata("epic", tankversion)

		if option_server == 0:
			tanktitle = get_tank_data(tanksdata, countryid, tankid, "title")
		else:
			tanktitle = str(countryid) + '_' + str(tankid)
			
		#"lastBattleTime_": tankitem[1][0],
		common = {"countryid": countryid,
			"tankid": tankid,
			"tanktitle": tanktitle,
			"type": get_tank_data(tanksdata, countryid, tankid, "type"),
			"premium": get_tank_data(tanksdata, countryid, tankid, "premium"),
			"tier": get_tank_data(tanksdata, countryid, tankid, "tier"),
			"updated": tankitem[1][0],
			"lastBattleTime": getdata("lastBattleTime", 2, 4),
			"lastBattleTimeR": datetime.datetime.fromtimestamp(int(getdata("lastBattleTime", 2, 4))).strftime('%Y-%m-%d %H:%M:%S'),
			"basedonversion": tankversion,
			"frags": tankdata['frags'],
			"frags_compare": numofkills
		}



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

		
		


	dossier['tanks'] = tanks

	finalfile = open(filename_target, 'w')

	if option_format == 1:
		finalfile.write(json.dumps(dossier, sort_keys=True, indent=4))
	else:
		finalfile.write(json.dumps(dossier))

	print '###### Done!'
	print ''
	sys.exit(0)
	


############################################################################################################################
def catch_fatal(message):
	import shutil
	
	write_to_log(message)

	if os.path.exists(filename_source) and os.path.isfile(filename_source) and os.access(filename_source, os.R_OK):
		try:
			shutil.copyfile(filename_source, filename_source + '.backup')
			#write_to_log('File has been saved for further analyzing : ' + filename_source + '.backup')
		except Exception, e:
			write_to_log('Cannot create backup: ' + filename_source + '.backup ' + e.message)
		  


def write_to_log(logtext):
	import datetime, os
	
	global working_directory, option_server
	
	print logtext
	now = datetime.datetime.now()
	
	#try:
	#working_directory
	
	if option_server == 1:
		logFile = open("/var/log/wotdc2j/wotdc2j.log", "a+b")
		logFile.write(str(now.strftime("%Y-%m-%d %H:%M:%S")) + " # " + str(logtext) + " # " + str(filename_source) + "\r\n")
		logFile.close()
	#except:
		#print "Cannot write to wotdc2j.log"
		

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

	return "-"


def getdata_fragslist(tankversion, tanksdata, offset):

	global sourcedata, numofkills

	fragslist = []

	offset = offset + 2

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
				numofkills = numofkills + amount
				
				if option_server == 0:
					tankname = get_tank_data(tanksdata, countryid, tankid, "title")
				else:
					tankname = "-"					
					
				tankill = [countryid, tankid, amount, tankname]
				fragslist.append(tankill)

	return fragslist


def getdata(name, startoffset, offsetlength):

	global rawdata, sourcedata

	if len(sourcedata)<startoffset+offsetlength:

		return 0

	if offsetlength == 1:

		value = sourcedata[startoffset]

		rawdata[startoffset] = str(value) + " / " + str(sourcedata[startoffset]) +  "; " + name

		return value

	elif offsetlength == 2:

		value = sourcedata[startoffset] + 256*sourcedata[startoffset+1]

		rawdata[startoffset] = str(value) + " / " + str(sourcedata[startoffset]) +  "; " + name
		rawdata[startoffset+1] = str(value) + " / " + str(sourcedata[startoffset+1]) +  "; " + name

		return value

	elif offsetlength == 3:

		value = sourcedata[startoffset] + 256*sourcedata[startoffset+1] + 256*256*sourcedata[startoffset+2]

		rawdata[startoffset] = str(value) + " / " + str(sourcedata[startoffset]) + "; " + name
		rawdata[startoffset+1] = str(value) + " / " + str(sourcedata[startoffset+1]) +  "; " + name
		rawdata[startoffset+2] = str(value) + " / " + str(sourcedata[startoffset+2]) +  "; " + name

		return value

	elif offsetlength == 4:

		value = sourcedata[startoffset] + 256*sourcedata[startoffset+1] + 256*256*sourcedata[startoffset+2] + 256*256*256*sourcedata[startoffset+3]

		rawdata[startoffset] = str(value) + " / " + str(sourcedata[startoffset]) +  "; " + name
		rawdata[startoffset+1] = str(value) + " / " + str(sourcedata[startoffset+1]) +  "; " + name
		rawdata[startoffset+2] = str(value) + " / " + str(sourcedata[startoffset+2]) +  "; " + name
		rawdata[startoffset+3] = str(value) + " / " + str(sourcedata[startoffset+3]) +  "; " + name

		return value

	else:
	  return 0



if __name__ == '__main__':
	main()
