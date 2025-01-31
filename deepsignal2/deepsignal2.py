#!/usr/bin/python
from __future__ import absolute_import

import sys
import argparse

from .utils.process_utils import str2bool
from .utils.process_utils import display_args


def main_extraction(args):
    from .extract_features import extract_features

    display_args(args)

    fast5_dir = args.fast5_dir
    is_recursive = str2bool(args.recursively)

    corrected_group = args.corrected_group
    basecall_subgroup = args.basecall_subgroup
    normalize_method = args.normalize_method

    reference_path = args.reference_path
    is_dna = str2bool(args.is_dna)
    write_path = args.write_path
    w_is_dir = str2bool(args.w_is_dir)
    w_batch_num = args.w_batch_num

    kmer_len = args.seq_len
    signals_len = args.signal_len
    motifs = args.motifs
    mod_loc = args.mod_loc
    methy_label = args.methy_label
    position_file = args.positions

    nproc = args.nproc
    f5_batch_size = args.f5_batch_size

    extract_features(fast5_dir, is_recursive, reference_path, is_dna,
                     f5_batch_size, write_path, nproc, corrected_group, basecall_subgroup,
                     normalize_method, motifs, mod_loc, kmer_len, signals_len, methy_label,
                     position_file, w_is_dir, w_batch_num)


def main_call_mods(args):
    from .call_modifications import call_mods

    display_args(args)
    call_mods(args)


def main_train(args):
    from .train import train
    import time

    print("[main]start..")
    total_start = time.time()

    display_args(args)
    train(args)

    endtime = time.time()
    print("[main]costs {} seconds".format(endtime - total_start))


def main():
    parser = argparse.ArgumentParser(prog='deepsignal2',
                                     description="detecting base modifications from Nanopore sequencing reads, "
                                                 "deepsignal2 contains four modules:\n"
                                                 "\t%(prog)s call_mods: call modifications\n"
                                                 "\t%(prog)s extract: extract features from corrected (tombo) "
                                                 "fast5s for training or testing\n"
                                                 "\t%(prog)s train: train a model, need two independent "
                                                 "datasets for training and validating",
                                     formatter_class=argparse.RawTextHelpFormatter)

    subparsers = parser.add_subparsers(title="modules", help='deepsignal2 modules, use -h/--help for help')
    sub_call_mods = subparsers.add_parser("call_mods", description="call modifications")
    sub_extract = subparsers.add_parser("extract", description="extract features from corrected (tombo) fast5s for "
                                                               "training or testing."
                                                               "\nIt is suggested that running this module 1 flowcell "
                                                               "a time, or a group of flowcells a time, "
                                                               "if the whole data is extremely large.")
    sub_train = subparsers.add_parser("train", description="train a model, need two independent datasets for training "
                                                           "and validating")

    # sub_extract ============================================================================
    se_input = sub_extract.add_argument_group("INPUT")
    se_input.add_argument("--fast5_dir", "-i", action="store", type=str,
                          required=True,
                          help="the directory of fast5 files")
    se_input.add_argument("--recursively", "-r", action="store", type=str, required=False,
                          default='yes',
                          help='is to find fast5 files from fast5_dir recursively. '
                               'default true, t, yes, 1')
    se_input.add_argument("--corrected_group", action="store", type=str, required=False,
                          default='RawGenomeCorrected_000',
                          help='the corrected_group of fast5 files after '
                               'tombo re-squiggle. default RawGenomeCorrected_000')
    se_input.add_argument("--basecall_subgroup", action="store", type=str, required=False,
                          default='BaseCalled_template',
                          help='the corrected subgroup of fast5 files. default BaseCalled_template')
    se_input.add_argument("--reference_path", action="store",
                          type=str, required=True,
                          help="the reference file to be used, usually is a .fa file")
    se_input.add_argument("--is_dna", action="store", type=str, required=False,
                          default='yes',
                          help='whether the fast5 files from DNA sample or not. '
                               'default true, t, yes, 1. '
                               'set this option to no/false/0 if '
                               'the fast5 files are from RNA sample.')

    se_extraction = sub_extract.add_argument_group("EXTRACTION")
    se_extraction.add_argument("--normalize_method", action="store", type=str, choices=["mad", "zscore"],
                               default="mad", required=False,
                               help="the way for normalizing signals in read level. "
                                    "mad or zscore, default mad")
    se_extraction.add_argument("--methy_label", action="store", type=int,
                               choices=[1, 0], required=False, default=1,
                               help="the label of the interested modified bases, this is for training."
                                    " 0 or 1, default 1")
    se_extraction.add_argument("--seq_len", action="store",
                               type=int, required=False, default=17,
                               help="len of kmer. default 17")
    se_extraction.add_argument("--signal_len", action="store",
                               type=int, required=False, default=16,
                               help="the number of signals of one base to be used in deepsignal2, default 16")
    se_extraction.add_argument("--motifs", action="store", type=str,
                               required=False, default='CG',
                               help='motif seq to be extracted, default: CG. '
                                    'can be multi motifs splited by comma '
                                    '(no space allowed in the input str), '
                                    'or use IUPAC alphabet, '
                                    'the mod_loc of all motifs must be '
                                    'the same')
    se_extraction.add_argument("--mod_loc", action="store", type=int, required=False, default=0,
                               help='0-based location of the targeted base in the motif, default 0')
    # se_extraction.add_argument("--region", action="store", type=str,
    #                            required=False, default=None,
    #                            help="region of interest, e.g.: chr1:0-10000, default None, "
    #                                 "for the whole region")
    se_extraction.add_argument("--positions", action="store", type=str,
                               required=False, default=None,
                               help="file with a list of positions interested (must be formatted as tab-separated file"
                                    " with chromosome, position (in fwd strand), and strand. motifs/mod_loc are still "
                                    "need to be set. --positions is used to narrow down the range of the trageted "
                                    "motif locs. default None")

    se_output = sub_extract.add_argument_group("OUTPUT")
    se_output.add_argument("--write_path", "-o", action="store",
                           type=str, required=True,
                           help='file path to save the features')
    se_output.add_argument("--w_is_dir", action="store",
                           type=str, required=False, default="no",
                           help='if using a dir to save features into multiple files')
    se_output.add_argument("--w_batch_num", action="store",
                           type=int, required=False, default=200,
                           help='features batch num to save in a single writed file when --is_dir is true')

    sub_extract.add_argument("--nproc", "-p", action="store", type=int, default=1,
                             required=False,
                             help="number of processes to be used, default 1")
    sub_extract.add_argument("--f5_batch_size", action="store", type=int, default=100,
                             required=False,
                             help="number of files to be processed by each process one time, default 100")

    sub_extract.set_defaults(func=main_extraction)

    # sub_call_mods =============================================================================================
    sc_input = sub_call_mods.add_argument_group("INPUT")
    sc_input.add_argument("--input_path", "-i", action="store", type=str,
                          required=True,
                          help="the input path, can be a signal_feature file from extract_features.py, "
                               "or a directory of fast5 files. If a directory of fast5 files is provided, "
                               "args in FAST5_EXTRACTION should (reference_path must) be provided.")

    sc_call = sub_call_mods.add_argument_group("CALL")
    sc_call.add_argument("--model_path", "-m", action="store", type=str, required=True,
                         help="file path of the trained model (.ckpt)")

    # model input
    sc_call.add_argument('--model_type', type=str, default="both_bilstm",
                         choices=["both_bilstm", "seq_bilstm", "signal_bilstm"],
                         required=False,
                         help="type of model to use, 'both_bilstm', 'seq_bilstm' or 'signal_bilstm', "
                              "'both_bilstm' means to use both seq and signal bilstm, default: both_bilstm")
    sc_call.add_argument('--seq_len', type=int, default=17, required=False,
                         help="len of kmer. default 17")
    sc_call.add_argument('--signal_len', type=int, default=16, required=False,
                         help="signal num of one base, default 16")

    # model param
    sc_call.add_argument('--layernum1', type=int, default=3,
                         required=False, help="lstm layer num for combined feature, default 3")
    sc_call.add_argument('--layernum2', type=int, default=1,
                         required=False, help="lstm layer num for seq feature (and for signal feature too), default 1")
    sc_call.add_argument('--class_num', type=int, default=2, required=False)
    sc_call.add_argument('--dropout_rate', type=float, default=0, required=False)
    sc_call.add_argument('--n_vocab', type=int, default=16, required=False,
                         help="base_seq vocab_size (15 base kinds from iupac)")
    sc_call.add_argument('--n_embed', type=int, default=4, required=False,
                         help="base_seq embedding_size")
    sc_call.add_argument('--is_base', type=str, default="yes", required=False,
                         help="is using base features in seq model, default yes")
    sc_call.add_argument('--is_signallen', type=str, default="yes", required=False,
                         help="is using signal length feature of each base in seq model, default yes")

    sc_call.add_argument("--batch_size", "-b", default=512, type=int, required=False,
                         action="store", help="batch size, default 512")

    # BiLSTM model param
    sc_call.add_argument('--hid_rnn', type=int, default=256, required=False,
                         help="BiLSTM hidden_size for combined feature")

    sc_output = sub_call_mods.add_argument_group("OUTPUT")
    sc_output.add_argument("--result_file", "-o", action="store", type=str, required=True,
                           help="the file path to save the predicted result")

    sc_f5 = sub_call_mods.add_argument_group("FAST5_EXTRACTION")
    sc_f5.add_argument("--recursively", "-r", action="store", type=str, required=False,
                       default='yes', help='is to find fast5 files from fast5 dir recursively. '
                                           'default true, t, yes, 1')
    sc_f5.add_argument("--corrected_group", action="store", type=str, required=False,
                       default='RawGenomeCorrected_000',
                       help='the corrected_group of fast5 files after '
                            'tombo re-squiggle. default RawGenomeCorrected_000')
    sc_f5.add_argument("--basecall_subgroup", action="store", type=str, required=False,
                       default='BaseCalled_template',
                       help='the corrected subgroup of fast5 files. default BaseCalled_template')
    sc_f5.add_argument("--reference_path", action="store",
                       type=str, required=False,
                       help="the reference file to be used, usually is a .fa file")
    sc_f5.add_argument("--is_dna", action="store", type=str, required=False,
                       default='yes',
                       help='whether the fast5 files from DNA sample or not. '
                            'default true, t, yes, 1. '
                            'setting this option to no/false/0 means '
                            'the fast5 files are from RNA sample.')
    sc_f5.add_argument("--normalize_method", action="store", type=str, choices=["mad", "zscore"],
                       default="mad", required=False,
                       help="the way for normalizing signals in read level. "
                            "mad or zscore, default mad")
    # sc_f5.add_argument("--methy_label", action="store", type=int,
    #                    choices=[1, 0], required=False, default=1,
    #                    help="the label of the interested modified bases, this is for training."
    #                         " 0 or 1, default 1")
    sc_f5.add_argument("--motifs", action="store", type=str,
                       required=False, default='CG',
                       help='motif seq to be extracted, default: CG. '
                            'can be multi motifs splited by comma '
                            '(no space allowed in the input str), '
                            'or use IUPAC alphabet, '
                            'the mod_loc of all motifs must be '
                            'the same')
    sc_f5.add_argument("--mod_loc", action="store", type=int, required=False, default=0,
                       help='0-based location of the targeted base in the motif, default 0')
    sc_f5.add_argument("--f5_batch_size", action="store", type=int, default=20,
                       required=False,
                       help="number of files to be processed by each process one time, default 20")
    sc_f5.add_argument("--positions", action="store", type=str,
                       required=False, default=None,
                       help="file with a list of positions interested (must be formatted as tab-separated file"
                            " with chromosome, position (in fwd strand), and strand. motifs/mod_loc are still "
                            "need to be set. --positions is used to narrow down the range of the trageted "
                            "motif locs. default None")

    sub_call_mods.add_argument("--nproc", "-p", action="store", type=int, default=10,
                               required=False, help="number of processes to be used, default 10.")
    sub_call_mods.add_argument("--nproc_gpu", action="store", type=int, default=2,
                               required=False, help="number of processes to use gpu (if gpu is available), "
                                                    "1 or a number less than nproc-1, no more than "
                                                    "nproc/4 is suggested. default 2.")

    sub_call_mods.set_defaults(func=main_call_mods)

    # sub_train =====================================================================================
    st_input = sub_train.add_argument_group("INPUT")
    st_input.add_argument('--train_file', type=str, required=True)
    st_input.add_argument('--valid_file', type=str, required=True)

    st_output = sub_train.add_argument_group("OUTPUT")
    st_output.add_argument('--model_dir', type=str, required=True)

    st_train = sub_train.add_argument_group("TRAIN")
    # model input
    st_train.add_argument('--model_type', type=str, default="both_bilstm",
                          choices=["both_bilstm", "seq_bilstm", "signal_bilstm"],
                          required=False,
                          help="type of model to use, 'both_bilstm', 'seq_bilstm' or 'signal_bilstm', "
                               "'both_bilstm' means to use both seq and signal bilstm, default: both_bilstm")
    st_train.add_argument('--seq_len', type=int, default=17, required=False,
                          help="len of kmer. default 17")
    st_train.add_argument('--signal_len', type=int, default=16, required=False,
                          help="the number of signals of one base to be used in deepsignal2, default 16")
    # model param
    st_train.add_argument('--layernum1', type=int, default=3,
                          required=False, help="lstm layer num for combined feature, default 3")
    st_train.add_argument('--layernum2', type=int, default=1,
                          required=False, help="lstm layer num for seq feature (and for signal feature too), default 1")
    st_train.add_argument('--class_num', type=int, default=2, required=False)
    st_train.add_argument('--dropout_rate', type=float, default=0.5, required=False)
    st_train.add_argument('--n_vocab', type=int, default=16, required=False,
                          help="base_seq vocab_size (15 base kinds from iupac)")
    st_train.add_argument('--n_embed', type=int, default=4, required=False,
                          help="base_seq embedding_size")
    st_train.add_argument('--is_base', type=str, default="yes", required=False,
                          help="is using base features in seq model, default yes")
    st_train.add_argument('--is_signallen', type=str, default="yes", required=False,
                          help="is using signal length feature of each base in seq model, default yes")
    # BiLSTM model param
    st_train.add_argument('--hid_rnn', type=int, default=256, required=False,
                          help="BiLSTM hidden_size for combined feature")
    # model training
    st_train.add_argument('--optim_type', type=str, default="Adam", choices=["Adam", "RMSprop", "SGD"],
                          required=False, help="type of optimizer to use, 'Adam' or 'SGD' or 'RMSprop', default Adam")
    st_train.add_argument('--batch_size', type=int, default=512, required=False)
    st_train.add_argument('--lr', type=float, default=0.001, required=False)
    st_train.add_argument("--max_epoch_num", action="store", default=10, type=int,
                          required=False, help="max epoch num, default 10")
    st_train.add_argument("--min_epoch_num", action="store", default=5, type=int,
                          required=False, help="min epoch num, default 5")
    st_train.add_argument('--step_interval', type=int, default=100, required=False)

    st_train.add_argument('--pos_weight', type=float, default=1.0, required=False)
    st_train.add_argument('--init_model', type=str, default=None, required=False,
                          help="pre-trained model parameters to load before training")
    # st_train.add_argument('--seed', type=int, default=1234,
    #                        help='random seed')
    # else
    st_train.add_argument('--tmpdir', type=str, default="/tmp", required=False)

    sub_train.set_defaults(func=main_train)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    sys.exit(main())
