#
# Script Name: table_to_fasta.R
# Purpose of script: Convert table into fasta
# Licence: MIT
# Usage: Rscript table_to_fasta.R [options]
#
# Options:
#
#   -i INPUT, --input=INPUT           [required]
#	Table to convert into fasta
#
#   -d DELIM, --delim=DELIM           [required]
#   	Single character used to separate fields in the table
#   
#   -n SEQ_NAME, --col_seqname=SEQ_NAME           [required]
#   	The column name containing the sequence names, that will be used as headers in the fasta
#   
#   -s SEQUENCE, --col_seq=SEQUENCE           [default: 'sequence']
#   	The column name containing the sequence
#
#   -u UNIQ_IDS, --uniq_ids=UNIQ_IDS            [default: FALSE]
#	Return unduplicated identifiers/headers if TRUE
#   
#   -e EXTENDED_FASTA, --extended_fasta=EXTENDED_FASTA            [default: FALSE]
#	Return a extended OBITools fasta if TRUE
#   
#   -t NCBI_TAXID, --ncbi_taxid=TAXID            [optional]
#	The column name containing the NCBI taxid 
#
#   -f FOWARD_PRIMER, --fwd=FORWARD_PRIMER            [optional]
#	Add the forward primer to the sequence
#
#   -r REVERSE_PRIMER, --rev=REVERSE_PRIMER           [optional]
#	Add the reverse primer to the sequence
#   
#   -o OUTPUT_PATH, --output_folder=OUTPUT_PATH           [default: '.']
#   	Path to the folder where you want to save the fasta file
#   
#   -h, --help
#   	Show this help message and exit
#

#_libs
suppressMessages(library(tidyverse))
library(optparse)
suppressMessages(library(phylotools))
library(taxizedb)

#_args
get_args <- function() {
  option_list <- list(
    optparse::make_option(c("-i", "--input"), type = "character", default = NULL, help = "Table to convert into fasta"),
    optparse::make_option(c("-d", "--delim"), type = "character", default = NULL, help = "Single character used to separate fields in the table"),
    optparse::make_option(c("-n", "--col_seqname"), type = "character", default = NULL, metavar = "SEQ_NAME",
                          help = "The column name containing the sequence names, that will be used as headers in the fasta"),
    optparse::make_option(c("-s", "--col_seq"), type = "character", default = "sequence", metavar = "SEQUENCE",
                          help = "The column name containing the sequence"),
    optparse::make_option(c("-u", "--uniq_ids"), type = "logical", default = FALSE,
                          help = "return unduplicated identifiers/headers if TRUE"),
    optparse::make_option(c("-e", "--extended_fasta"), type = "logical", default = FALSE,
                          help = "return a extended OBITools fasta if TRUE"),
    optparse::make_option(c("-t", "--ncbi_taxid"), type = "character", default = NULL,  metavar = "TAXID",
			  help = "The column name containing the NCBI taxid"),
    optparse::make_option(c("-f", "--fwd"), type = "character", default = NULL, metavar = "FORWARD_PRIMER",
                          help = "add the forward primer to the sequence"),
    optparse::make_option(c("-r", "--rev"), type = "character", default = NULL, metavar = "REVERSE_PRIMER",
                          help = "add the reverse primer to the sequence"),
    optparse::make_option(c("-o", "--output_folder"), type = "character", default = ".", metavar = "OUTPUT_PATH",
                          help = "Path to the folder where you want to save the fasta file")
  )
  opt_parser <- optparse::OptionParser(option_list = option_list)
  opt <- optparse::parse_args(opt_parser)

  # missing option
  if (is.null(opt$input)) {
    optparse::print_help(opt_parser)
    stop("Arg --input [-i] is required")
  }
  if (is.null(opt$delim)) {
    optparse::print_help(opt_parser)
    stop("Arg --delim [-d] is required")
  }
  if (is.null(opt$col_seqname)) {
    optparse::print_help(opt_parser)
    stop("Arg --col_seqname [-n] is required")
  }
  if (is.null(opt$col_seq)) {
    optparse::print_help(opt_parser)
    stop("Arg --col_seq [-s] is required")
  }
  return(opt)
}

#_main
main <- function() {
  # Read arguments
  args <- get_args()
  # Convert table
  table2fasta(table_file = args$input, sep = args$delim, col_sname = args$col_seqname,
              col_seq = args$col_seq, col_taxid = args$ncbi_taxid, uniq_ids = args$uniq_ids,
	      extended_fasta = args$extended_fasta, fwd = args$fwd, rev = args$rev,
              output_folder = args$output_folder)
}

#_fun
table2fasta <- function(table_file, sep, col_sname, col_seq, col_taxid, uniq_ids = FALSE, extended_fasta = FALSE, fwd, rev, output_folder) {
  col <- c(col_sname, col_seq, col_taxid)
  table <- readr::read_delim(file = table_file, delim = sep, col_select = all_of(col), show_col_types=FALSE) |> 
    setNames(c("seq.name", "seq.text", col_taxid)) |>
    dplyr::mutate(seq.text = paste0(fwd, seq.text, rev))
  if (uniq_ids) {
    table <- dereplicate_ids(table)
  }
  if (extended_fasta){
    table <- add_ncbi_taxid(table, taxid = col_taxid)
  }
  out <- file.path(output_folder, sub("\\..*", ".fasta", basename(table_file)))
  phylotools::dat2fasta(dat = table, outfile = out)
}

add_ncbi_taxid <- function(table, taxid){
  if (!is.null(taxid)) {
    tb_w_taxid <- table |>
      tidyr::unite(seq.name, c(seq.name, matches(taxid)), sep = " taxid=") |>
      dplyr::mutate(seq.name = sub("$", ";", seq.name))
  } else {
  taxa <- stringr::word(string = unique(table$seq.name), start = 1, end = 1,sep = "\\.")
  tb_taxid <- taxizedb::name2taxid(taxa, out_type = "summary")
  tb_w_taxid <- table |>
    dplyr::mutate(taxa = stringr::word(string = seq.name, start = 1, end = 1,sep = "\\.")) |>
    dplyr::left_join(y = tb_taxid, by = dplyr::join_by(taxa == name), multiple = "last") |>
    tidyr::unite(seq.name, c(seq.name, id), sep = " taxid=") |>
    dplyr::mutate(seq.name = sub("$", ";", seq.name))
  }
  return(tb_w_taxid)
}

dereplicate_ids <- function(table){
  table |>
    dplyr::group_by(seq.name) |>
    dplyr::mutate(n = dplyr::row_number()) |>
    tidyr::unite(seq.name, c(seq.name, n), sep = ".") |>
    dplyr::ungroup()
}

if (!interactive()) {
  main()
}
