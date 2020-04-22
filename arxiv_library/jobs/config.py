"""
Constants like file paths
"""

MACROS_DEF = ["newcommand", "renewcommand"]

PACKAGE_DEF = "usepackage"

ENCODINGS = ['utf-8', 'cp1252']

NUM_WORKERS = 6 

DEF = "\\def"

LET = "\\let"

DOC_TEMPLATE = r'''document'''

FORBIDDEN_SEC_CHARS = ['/', '{', '}', '$', '^', '\\', "\'", "`", "\""]

TAR_LOCATION = "/rdata/pfahler/arxiv"

# GZIPS_LOCATION = "/home/schill/ramdisk/gzs"

RAMDISK = "/ramdisk"

TEX_LOCATION = "/home/fpdmws2018/arxiv/only_tex_wo_comms/"

PNG_LOCATION = "/ramdisk/pngs"

FORMULA_LOCATION = "/home/fpdmws2018/arxiv/txt_files/"

JSON_LOCATION = "/home/schill/arxiv/json_db/"

PICKLE_LOCATION = "/ramdisk/pickle"

CITATION_LOCATION = "/ramdisk/citations"

PERSISTENT_DISKS = ["/rdata/pfahler/arxiv_processed/",
					"/data/pfahler/arxiv_processed/",
					"/data/d1/pfahler/arxiv_processed"]

PNG_POSTFIX = "pngs"

FORMULA_POSTFIX = "txt_formulas"

CITATION_POSTFIX = "citations"

MODEL_POSTFIX = "models"

PICKLE_POSTFIX = "pickle"

META_DATA_POSTFIX = "meta_data"

# Size of data chunk that is moved from tmpfs to persistent disk.
CHUNK_SIZE = 4 * 1024**3 # 4G
