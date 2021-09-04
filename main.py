#!/usr/bin/env python3
import os
import sys
import subprocess
import getopt

def run_command(cmd):
	return subprocess.run(cmd, capture_output=True, text=True).stdout.strip('\n')

def usage():
	"""
	Prints usage/help text.
	"""
	print(f'Usage: {sys.argv[0]} [OPTION]... FILE...')

def get_clip_length(file: str):
	"""
	Returns the length of an audio / video file in seconds.
	"""
	# Check if the file is actually a file (and not a directory)
	# and whether the user has write access.
	if not (os.path.isfile(file) and os.access(file, os.R_OK)):
		raise NameError(f'The file {file} is either invalid or cannot be read!')

	leng = run_command(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', '-sexagesimal', file])
	return leng

def parse_length(time: str):
	"""
	For manually specified time values.
	Parse a "hh:mm:ss" string into seconds. Decimals at the end will be respected.
	For example, "02:43:47.784" will return 9827.784
	"""

	# Unpack the time string.
	length_split: list = time.split(':')

	# The length string should contain hours, minutes and seconds even if the file
	# is only 5 seconds long for consistency. If it contains more parts (for
	# example, because the user only passed seconds and minutes) or if it somehow
	# got longer (for example, through a typo), raise an error.
	if len(length_split) != 3:
		raise ValueError('Your time string seems to not be made of three parts!\n            It must be formated like "hh:mm:ss.ms"!\n            Hours and milliseconds can have any length.')

	# Convert each string from length_split into a number.
	# The reason why *all* numbers are converted to decimal numbers here instead
	# of only the seconds is that they are checked later on to allow for more
	# human-firendly error messages.
	length_split_num = []
	for i in length_split:
		length_split_num += [float(i)]

	# If any number here is negative, something must be really, really wrong :)
	for i in length_split_num:
		if i < 0:
			raise ValueError('Your clip cannot have a negative length!')

	# Assign hours, minutes and seconds to seperate variables for better readability.
	hours   = length_split_num[0]
	minutes = length_split_num[1]
	seconds = length_split_num[2]

	# Hours / minutes must be whole numbers, otherwise it's a sign that the minutes / seconds were counted incorrectly.
	if not hours.is_integer():
		raise ValueError('Hours must be a whole number!')
	hours = int(hours)

	if not minutes.is_integer():
		raise ValueError('Minutes must be a whole number!')
	minutes = int(minutes)

	# Minutes / seconds must be below 59, otherwise it's a sign that the hours / minutes were counted incorrectly.
	if minutes > 59:
		raise ValueError('Minutes must be less than 59!')

	if seconds > 59:
		raise ValueError('Seconds must be less than 59!')

	# Now it's save to calculate the true length in seconds.
	true_length = (hours * 3600) + (minutes * 60) + seconds

	#return (hours, minutes, seconds)
	return true_length

def main(*argv: str):
	args: str = argv[0][1:]
	opts, args = getopt.gnu_getopt(args, ':ht:f:')

	for o, a in opts:
		if o in '-h':
			usage()
		elif o == '-t':
			print(f'Input time:      {a}')
			print(f'Time in seconds: {str(parse_length(a))}')
		elif o == '-f':
			leng = get_clip_length(a)
			print(f'Length of file (human readable): {leng}')
			print(f'Length of file (in seconds):     {str(parse_length(leng))}')

if __name__ == '__main__':
	main(sys.argv)