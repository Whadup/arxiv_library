"""Main Job for identifying all equations, translating them to standalone latex,
compiling latex to pdf and converting pdf to png.
Store everything in a neat folder structure"""
import os

import argparse
import logging
import traceback

from multiprocessing import Pool
from tqdm import tqdm


import arxiv_lib.png_compile as png_compile
import arxiv_lib.preprocessing as preprocessing
import arxiv_lib.formula_parser as formula_parser
from arxiv_lib.multiprocessing_logging import install_mp_handler
from arxiv_lib.tempfs import check_tempfs_status, write_tmpfs_to_disk
import arxiv_lib.helpers as h
import config as c



def extract_gzs(tar_archive):
	"""Extract all gz archives and rm comments in tex-sources"""
	for gzip, name in preprocessing.iterate_tar(tar_archive):
		preprocessing.extract_gz(gzip, name)


def extract_from_arxiv_dir(arxiv_dir):
	"""Extract formulas, important packages and macros from tex-sources.
	Then compile pngs of the formulas."""

	#critical section start
	check_tempfs_status(pngs=True, equations=True)
	#critical section end

	try:
		arxiv_dir = os.path.join(c.TEX_LOCATION, arxiv_dir)
		main_file = preprocessing.find_main(arxiv_dir)

		if main_file is None:
			return

		resolved = preprocessing.resolve(main_file, arxiv_dir, arxiv_dir)
		preample = preprocessing.extract_preamble(resolved)
		sections = preprocessing.sectionize(resolved)
		output_file_path = os.path.join(c.FORMULA_LOCATION, os.path.basename(arxiv_dir) + ".txt")

		formula_counter = 0
		with open(output_file_path, 'a') as output_file:
			output_file.write(c.BEGIN_PREAMBLE + "\n")
			output_file.write(preample + "\n")
			output_file.write(c.END_PREAMBLE + "\n")

			for section_name, section_content in sections.items():
				output_file.write("**" + section_name + "**\n")

				for eq in env_parser.extract_envs(section_content):
					# rm newlines and carriage returns
					# eq = eq.replace('\n', ' ').replace('\r', '')
					# output_file.write("$$"+ eq + "$$\n")
					formula_counter += 1

		# the file is not needed if no equations were extracted
		if formula_counter == 0:
			os.remove(output_file_path)
		else:
			png_compile.compile_eqs_in_paper(output_file_path)
	except Exception:
		logging.warning(traceback.format_exc() + "in file %s", main_file)

def main():
	"""Main job"""
	parser = argparse.ArgumentParser(description='Extract formulas from arxiv tar archive')
	# Number of the run
	parser.add_argument('no', type=int)
	parser.add_argument("--partition", type=int, default=1)
	parser.add_argument("--total_partitions", type=int, default=1)
	args = parser.parse_args()
	log_file = "routine{}{}-{}.log".format(args.no, args.partition, args.total_partitions)
	logging.basicConfig(filename=log_file, level=logging.WARNING)
	h.assure_dir_exists(c.FORMULA_LOCATION)
	h.assure_dir_exists(c.PNG_LOCATION)
	h.assure_dir_exists(c.TEX_LOCATION)
	install_mp_handler()
	full_workload = os.listdir(c.TEX_LOCATION)
	workload = full_workload[args.partition-1::args.total_partitions]
	with Pool(c.NUM_WORKERS) as pool:
		results = pool.imap(extract_from_arxiv_dir, workload)
		results = list(tqdm(results))
	write_tmpfs_to_disk(equations=True, pngs=True)

if __name__ == '__main__':
	main()
