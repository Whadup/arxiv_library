"""Functionality for writing results stored on the ramdisk to a persistent disk"""
import os
import shutil
import time
import logging
from datetime import datetime as dt
from multiprocessing import Manager
import arxiv_lib.helpers as h
import config as c

MANAGER = Manager()
# pylint: disable=no-member
DISK_WRITER_LOCK = MANAGER.Lock()


def check_tempfs_status(equations=False, pngs=False, citations=False, pickles=False):
	"""blocks until is is made sure that the tempfs has enough free space.
	If disk usage is above the quota, the data is moved to the perstitant
	storage."""
	DISK_WRITER_LOCK.acquire()
	_, used, _ = shutil.disk_usage(c.RAMDISK)
	if used > c.CHUNK_SIZE:
		print("wait!")
		# wait for the other processes to finish
		time.sleep(120)
		print("move!")
		start = dt.now()
		logging.warning("Full tmpfs. Writing to persistent disk. Time: %s", start)
		write_tmpfs_to_disk(equations=equations, pngs=pngs, citations=citations, pickles=pickles)
		end = dt.now()
		diff = end - start
		logging.warning("Finished copying and cleaning tmpfs. Time needed for copy process: %s", diff)
	DISK_WRITER_LOCK.release()

def write_tmpfs_to_disk(equations=False, pngs=False, citations=False, pickles=False):
	""" Write files txt and pngs files that are currently
	in tmpfs memory on a persistent disk and removes all
	files from tmpfs."""
	disk = select_free_disk()

	if equations:
		# move txt files with extracted formulas
		os.chdir(c.FORMULA_LOCATION)
		formula_output_dir = os.path.join(disk, c.FORMULA_POSTFIX)
		h.assure_dir_exists(formula_output_dir)

		for txt in os.listdir():
			shutil.move(txt, formula_output_dir)
		shutil.rmtree(c.FORMULA_LOCATION, ignore_errors=True)
		h.assure_dir_exists(c.FORMULA_LOCATION)
	if pickles:
		# move txt files with extracted formulas
		os.chdir(c.PICKLE_LOCATION)
		pickle_output_dir = os.path.join(disk, c.PICKLE_POSTFIX)
		h.assure_dir_exists(pickle_output_dir)

		for pickle in os.listdir():
			if pickle.endswith(".pickle"):
				shutil.move(pickle, pickle_output_dir)
		shutil.rmtree(c.PICKLE_LOCATION, ignore_errors=True)
		h.assure_dir_exists(c.PICKLE_LOCATION)
	if citations:
		# move txt files with extracted formulas
		os.chdir(c.CITATION_LOCATION)
		formula_output_dir = os.path.join(disk, c.CITATION_POSTFIX)
		h.assure_dir_exists(formula_output_dir)

		for txt in os.listdir():
			shutil.move(txt, formula_output_dir)
		shutil.rmtree(c.CITATION_LOCATION, ignore_errors=True)
		h.assure_dir_exists(c.CITATION_LOCATION)
	if pngs:
		# move png files from extracted formulas
		os.chdir(c.PNG_LOCATION)
		png_output_dir = os.path.join(disk, c.PNG_POSTFIX)
		h.assure_dir_exists(png_output_dir)

		for arxiv_dir in os.listdir():
			os.chdir(arxiv_dir)
			persistent_arxiv_dir = os.path.join(png_output_dir, arxiv_dir)
			h.assure_dir_exists(persistent_arxiv_dir)

			for file in os.listdir():
				if file.endswith('.png'):
					shutil.move(file, persistent_arxiv_dir)

			os.chdir(c.PNG_LOCATION)
		shutil.rmtree(c.PNG_LOCATION, ignore_errors=True)
		h.assure_dir_exists(c.PNG_LOCATION)
	# remove the rest of the files directorywise


def select_free_disk():
	"""If there are more than one PERSISTENT DISKs, select a free one."""
	for disk in c.PERSISTENT_DISKS:
		_, _, avail = shutil.disk_usage(disk)
		if avail >= c.CHUNK_SIZE:
			return disk
	return c.PERSISTENT_DISKS[0]
