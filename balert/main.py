#! /usr/bin/python
from sys import argv, exit, version_info
from Voice import Voice
from BatteryStatus import Battery
from Config import Config
import argparse
import logging
import subprocess
import os

if version_info >= (3,):
    import pickle
else:
    import cPickle as pickle


def setupCron():
    try:
        location_f = subprocess.Popen("whereis \
        balert", shell=True, stdout=subprocess.PIPE).stdout.read().\
            strip().split(':')[1].strip()
        cmd = subprocess.Popen("crontab -l", shell=True,
                               stdout=subprocess.PIPE).stdout.read()
        if not ('balert' in cmd):
            cmd += "*/10 * * * * " + location_f + "\n"
            tmp = open("/tmp/temp_cron.impossible", 'w')
            tmp.write(cmd)
            tmp.close()
            subprocess.Popen("crontab /tmp/temp_cron.impossible", shell=True)
            logging.info("Successfully set up the cron job.")
            print "Ok"  # Do not remove this line ever!
    except:
        logging.debug("Error writing the cron job.")


def extract(func):
    def read():
        cf = Config()    # create config object
        cf_data = cf.load_pickle()
        args = func()
        if args.rate:
            cf_data["RATE"] = args.rate
        if args.vol:
            cf_data["VOL"] = args.vol
        if args.lang:
            cf_data["LANG"] = args.lang
        if args.msg:
            cf_data["MSG"] = args.msg
        if args.charge:
            cf_data["CHARGE"] = args.charge
        cf.set_pickle(cf_data)
        return cf, cf_data
    return read


@extract
def parse():
    parser = argparse.ArgumentParser(description=" \
             Listen the voice of your battery whenever she is low!", epilog="\
             Author:tushar.rishav@gmail.com")
    parser.add_argument("-r", "--rate", help="Rate of speaking.(100-200)",
                        type=int)
    parser.add_argument("-v", "--vol", help="Volume of speaking.(1.0)",
                        type=str)
    parser.add_argument("-l", "--lang", help="Language speaking.(1.0)",
                        type=str)
    parser.add_argument("-m", "--msg", help="Alert message of your own",
                        type=str)
    parser.add_argument("-c", "--charge", help="Decide the critical charge\
    level", type=int)
    args = parser.parse_args()
    return args


def main():
    logging.getLogger().setLevel(logging.DEBUG)
    cf, cf_data = parse()
    if len(argv) == 1:
        pass
    al = Voice()
    battery_instance = Battery()    # READ BATTERY
    charge_info = battery_instance.get_low_battery_warning_level()
    logging.debug(charge_info)
    if charge_info[0] == 0 and charge_info[1]:
        add_msg = " All cool! %d Percent remaining" % charge_info[1]
    elif charge_info[0] == 1:
        add_msg = " Low Battery! %d Percent remaining" % charge_info[1]
        logging.info(cf_data["MSG"]+add_msg)
        cf.set_pickle(cf_data)
        al.speak(add_msg)
    else:
        add_msg = " Battery is Charging!"
    setupCron()

if __name__ == "__main__":
    main()
