import subprocess

def prepare(INPUT, OUTPUT):
	input_new = INPUT + ".new"
	subprocess.call(['touch', input_new])
	bashCommand = "cat " + INPUT + " | sed 's/\\([^\\]\\):[^ ,	]*\\( \\|,\\|$\\)/\\1\\2/g' | \
	sed 's/\\\\:/:/g' | sed 's/~ *//g' | sed 's/ *,/,/g' | sed 's/ *$//' > " + input_new

	subprocess.run(bashCommand, shell=True)
	
	# remove everything after first column
	subprocess.run("nawk '{print $1}' " + input_new + " > " + OUTPUT, shell=True)
	return

INPUT = ''
OUTPUT = ''

# subprocess.call(['touch', OUTPUT])

prepare(INPUT, OUTPUT)