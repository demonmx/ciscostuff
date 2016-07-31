#!/bin/python
#
# this code extract the configuration of all context's on an asa box
# stores the config as <ip>_<context>.conf 
# it uses a table called "firewallcitos" (yea i know, dummy name) where you define the ip's of the 
# physical asa boxes.
# you need to define the account & mypass variables
# its assumed that every box uses the same account and pass and the "en" pass is the same as mypass
#
# you can modify the "exect" script stating the relevant "expect" & "send" pairs on add_expect_pairs function
#
# Adrian de los Santos
# demon@demon.com.mx

import pexpect
import sys
import re

global commands_list, account, mypass
commands_list=[]

account="myaccount"
mypass="mypass"

def add_expect_pairs(expect_part, send_part):
	global commands_list
	command_dict = { 'type' : 'expect', 'command' : expect_part }
	commands_list.append(command_dict)
	command_dict = { 'type' : 'sendline', 'command' : send_part }
	commands_list.append(command_dict)

def grab_config(destination_ip, commands_list, description):
	#description="main"
	#destination_ip="10.55.33.136"
	#account="cayala"
	#mypass="l0m15m0"
	sw_abort=0

	#print " ---- GETTING IP :"  + destination_ip + " --------"

	composer="ssh " + account + "@" + destination_ip
	#print "spawing " + composer
	child = pexpect.spawn(composer)
	#child.logfile = sys.stdout
	fp = open("fw_" + destination_ip + "_" + description + ".conf","w")

	returnval = child.expect (["Are you sure you want to continue connecting","password",pexpect.EOF,pexpect.TIMEOUT])
	#print child.before
	#print child.after 
	if returnval == 0:
		#RSA key message presented for SSH
		child.sendline ("yes")
		child.expect ("ssword:")
		child.sendline (mypass+"\n")
	elif returnval == 1:
		#There is no RSA key presented to SSH
		#child.expect ("ssword:")
		child.sendline (mypass+"\n")
		#print child.after 
		#print child.before
	elif returnval == 2:
		print ("\nEOF - Cannot connect to host " + destination_ip)
		child.sendcontrol("c")
		sw_abort=1
	elif returnval == 3:
		print ("\nTIMEOUT - Cannot connect to host " + destination_ip)
		child.sendcontrol("c")
		sw_abort=1


	if sw_abort == 1:
		print "aborted"

	commands_size=len(commands_list)
	#print "total " + str(commands_size) + " commands "

	counter=0;
	for dict in commands_list:

  		kind=dict['type']
		cmd=dict['command']
		counter += 1

		#print "kind: " + kind + "value " + ">" + cmd + "<<<<<<<<<"

		#if (commands_size - 1 ) == counter:
		#	fp.write(child.before)

		if kind == "expect":
			child.expect(cmd)
		elif kind == "sendline":
			child.sendline(cmd)

	fp.write(child.before)
	fp.close()


def main(get_config_ip):
	global commands_list
	commands_list=[]
	add_expect_pairs("/act.*> ","en")
	add_expect_pairs("word",mypass)
	add_expect_pairs("/act.*# ","conf t")
	add_expect_pairs("#","no pager")
	add_expect_pairs("# ","exit")
	# 
	add_expect_pairs("/act.*# ","changeto system")
	add_expect_pairs("/act.*# ","show run context")
	add_expect_pairs("/act.*# ","exit")
	print "getting ----------------------- " + get_config_ip + " main config "

	grab_config(get_config_ip, commands_list, "main")

	# open the main file an loop thru contexts
	full_config_file=open(get_config_ip + "_main.conf","r").read()

	lines_config_file=full_config_file.split('\n')

	context_list=[]
	for line in lines_config_file:
		found_context=False

		if re.match("^context ", line):
			array_line=line.split(' ')
			context_list.append(array_line[1].rstrip())
			found_context=True

	for contexto in context_list:
			commands_list=[]
			add_expect_pairs("/act.*>","en")
			add_expect_pairs("word",mypass)
			add_expect_pairs("/act.*# ","conf t")
			add_expect_pairs("#","no pager")
			add_expect_pairs("# ","exit")
			# 
			add_expect_pairs("/act.*# ","changeto context "+contexto)
			add_expect_pairs("/act.*# ","show run")
			add_expect_pairs("/act.*# ","exit")
			print "getting ----------------------- " + get_config_ip + " context " + contexto
			grab_config(get_config_ip, commands_list, contexto)


# la la la la main stuff here

firewallcitos=[ "192.168.1.1", 
		        "192.168.10.1",
	            "192.168.10.2"]

for firewallcito in firewallcitos:
	main(firewallcito)



