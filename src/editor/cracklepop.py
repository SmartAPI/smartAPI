def cracklepop(stop=101):
	for n in xrange(1,stop):
		print "CracklePop"*(not n % 15) or
			"Crackle"*(not n % 3) or
			"Pop"*(not n % 5) or
			n
