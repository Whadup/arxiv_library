import logging
import pipeline_woall
import pipeline_wothr
import io_pkg.paths

logging.basicConfig(filename='/home/jan/arxiv_lib/pipeline.log')

io_pkg.paths.set_path('json_location', '/home/jan/arxiv_lib/json')
io_pkg.paths.set_path('tar_location', '/home/jan/arxiv_lib/tars')
io_pkg.paths.set_path('tmp_tar', '/home/jan/arxiv_lib/temp')
io_pkg.paths.set_path('file_dict_location', '/home/jan/arxiv_lib/filedicts')

pipeline_woall.pipeline(tar_dir='/home/jan/arxiv_lib/tars', json_dir='/home/jan/arxiv_lib/json')

# pipeline_wothr.pipeline(tar_dir='/home/jan/arxiv_lib/tars', json_dir='/home/jan/arxiv_lib/json')
