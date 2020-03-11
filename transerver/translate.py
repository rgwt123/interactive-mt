import argparse
import torch
from logging import getLogger
import os
from src.model import build_mt_model
from src.data.loader import load_data
from src.data.dictionary import EOS_WORD, PAD_WORD, UNK_WORD, BOS_WORD, Dictionary
from subprocess import check_output
import re
import fastBPE
#bpe = fastBPE.fastBPE('data_v2/fast.bpe.en', 'data_v2/fast.vocab.en')
#bpezh = fastBPE.fastBPE('data_v2/fast.bpe.zh', 'data_v2/fast.vocab.zh')
bpe = fastBPE.fastBPE('data_pe2zh/fast.bpe.pe', 'data_pe2zh/vocab.pe')
bpezh = fastBPE.fastBPE('data_pe2zh/fast.bpe.zh', 'data_pe2zh/vocab.zh')
import jieba
import time

logger = getLogger()
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

parser = argparse.ArgumentParser(description='Settings')
parser.add_argument("--reload_model", type=str, default='',
                    help="reload model")
parser.add_argument("--batch_size", type=int, default=1,
                    help="batch size")
parser.add_argument("--batch_size_tokens", type=int, default=-1,
                    help="batch size tokens")
parser.add_argument("--src_n_words", type=int, default=0,
                    help="data")
parser.add_argument("--tgt_n_words", type=int, default=0,
                    help="data")
parser.add_argument("--dropout", type=float, default=0,
                    help="Dropout")
parser.add_argument("--label-smoothing", type=float, default=0,
                    help="Label smoothing")
parser.add_argument("--attention", type=bool, default=True,
                    help="Use an attention mechanism")
parser.add_argument("--transformer", type=bool, default=True,
                    help="Use Transformer")
parser.add_argument("--lstm", type=bool, default=False,
                    help="Use LSTM")
parser.add_argument("--emb_dim", type=int, default=512,
                    help="Embedding layer size")
parser.add_argument("--n_enc_layers", type=int, default=6,
                    help="Number of layers in the encoders")
parser.add_argument("--n_dec_layers", type=int, default=6,
                    help="Number of layers in the decoders")
parser.add_argument("--hidden_dim", type=int, default=512,
                    help="Hidden layer size")

parser.add_argument("--transformer_ffn_emb_dim", type=int, default=4096,
                    help="Transformer fully-connected hidden dim size")
parser.add_argument("--attention_dropout", type=float, default=0,
                    help="attention_dropout")
parser.add_argument("--relu_dropout", type=float, default=0,
                    help="relu_dropout")
parser.add_argument("--encoder_attention_heads", type=int, default=8,
                    help="encoder_attention_heads")
parser.add_argument("--decoder_attention_heads", type=int, default=8,
                    help="decoder_attention_heads")
parser.add_argument("--encoder_normalize_before", type=bool, default=False,
                    help="encoder_normalize_before")
parser.add_argument("--decoder_normalize_before", type=bool, default=False,
                    help="decoder_normalize_before")
parser.add_argument("--share_encdec_emb", type=bool, default=False,
                    help="share encoder and decoder embedding")
parser.add_argument("--share_decpro_emb", type=bool, default=True,
                    help="share decoder input and project embedding")
parser.add_argument("--beam_size", type=int, default=4,
                    help="beam search size")
parser.add_argument("--length_penalty", type=float, default=1.0,
                    help="length penalty")
parser.add_argument("--clip_grad_norm", type=float, default=5.0,
                    help="clip grad norm")
parser.add_argument("--checkpoint_dir", type=str, default='all_models')
params = parser.parse_args()
params.gpu_num = 1
params.seed = 1234
params.reload_model = 'all_models/pe2zh_model_epoch4_update210000.pt'
params.src_dico = Dictionary.read_vocab('data_pe2zh/vocab.pe')
params.tgt_dico = Dictionary.read_vocab('data_pe2zh/vocab.zh')
params.eos_index = params.src_dico.index(EOS_WORD) # 1
params.pad_index = params.src_dico.index(PAD_WORD) # 2
params.unk_index = params.src_dico.index(UNK_WORD) # 3
params.bos_index = params.src_dico.index(BOS_WORD) # 0
params.src_n_words = len(params.src_dico)
params.tgt_n_words = len(params.tgt_dico)
encoder, decoder, _ = build_mt_model(params)
encoder.eval()
decoder.eval()


def preprocess(s ,iszh=False, table=None):
    # moses tools chain
    # norm punc, tokenize, ...

    # tokenize
    if not iszh:
        s = check_output("perl tools/mosesdecoder/scripts/tokenizer/remove-non-printing-char.perl  | perl tools/mosesdecoder/scripts/tokenizer/tokenizer.perl -l en -no-escape -q -protected data_pe2zh/protected.en", input=s, encoding='utf-8', shell=True)
        s = s.strip()
        logger.debug('after tokenizer: %s', s)
        
    else:
        s = ' '.join(jieba.cut(s.strip()))
        logger.debug('after tokenizer: %s', s)
    
    replacement = []
    # process replace with table
    if table is not None and not iszh:
        tokens_source = s.split()
        length_source = len(tokens_source)
        i = 0
        while i < length_source:
            for j in range(i+6,i,-1):
                if j > length_source:
                    continue
                ngram_source = ' '.join(tokens_source[i:j])
                if ngram_source in table:
                    ngram_target = table[ngram_source]
                    replacement.append(ngram_target)
                    tokens_source[i] = '$TAG'
                    for k in range(i+1,j):
                        tokens_source[k] = ''
                    i = j-1
                    break
            i += 1
        s = ' '.join([x for x in tokens_source if len(x)>0])

    # bpe
    if not iszh:
        s = bpe.apply([s])[0]
    else:
        s = bpezh.apply([s])[0]
    
    logger.debug('after bpe: %s', s)
    return s.strip(), replacement

def postprocess(s):
    logger.debug('after translate: %s', s)
    s = check_output("sed 's/@@ //g' | perl tools/mosesdecoder/scripts/tokenizer/detokenizer.perl", input=s, encoding='utf-8', shell=True)
    logger.debug('after detoken: %s', s)
    return s.strip()

def translate_onesentence(onesent, prefix="", table=None):
    if len(onesent) == 0:
        return ""
    t1 = time.time()
    s, replacement = preprocess(onesent, iszh=False, table=table)
    logger.debug('preprocss time: %s', time.time()-t1)
    t1 = time.time()
    s = s.split()
    sentence_s = []
    for w in s:
        word_id = params.src_dico.index(w, no_unk=False)
        if word_id < 4 and word_id != params.src_dico.unk_index:
            logger.warning('Found unexpected special word "%s" (%i)!!' % (w, word_id))
            continue
        sentence_s.append(word_id)
        
    sentence_s = torch.LongTensor([sentence_s])
    length_s = torch.LongTensor([len(sentence_s[0]) + 2])
    temp_length = len(sentence_s[0])+2
    temp = torch.LongTensor(temp_length, 1).fill_(params.pad_index)
    temp[0] = params.bos_index
    temp[1:temp_length - 1, 0].copy_(sentence_s[0])
    temp[temp_length - 1, 0] = params.eos_index
    sentence_s = temp
    sentence_s = sentence_s.cuda()
    
    logger.debug('build tensor time: %s', time.time()-t1)
    t1 = time.time()
    
    encoded = encoder(sentence_s, length_s)
    
    logger.debug('encoder time: %s', time.time()-t1)
    t1 = time.time()
    
    if len(prefix) > 0:
        sp, _ = preprocess(prefix, iszh=True)
        sp = sp.split()
        sentence_sp = []
        for w in sp:
            word_id = params.tgt_dico.index(w, no_unk=False)
            if word_id < 4 and word_id != params.tgt_dico.unk_index:
                logger.warning('Found unexpected special word "%s" (%i)!!' % (w, word_id))
                continue
            sentence_sp.append(word_id)
            
        sentence_sp = torch.LongTensor([sentence_sp])
        sentence_sp = sentence_sp.cuda()
        sentence_t, length_t, _ = decoder.generate(encoded, prefix_tokens=sentence_sp)
    else:
        sentence_t, length_t, _ = decoder.generate(encoded)
    sentence_t = params.tgt_dico.idx2string(sentence_t[:, 0])
    
    logger.debug('decoder beamsearch time: %s', time.time()-t1)
    t1 = time.time()
    if len(replacement) > 0:
        for one_replacement in replacement:
            if '$TAG' in sentence_t:
                sentence_t = sentence_t.replace('$TAG', one_replacement, 1)

    s = postprocess(sentence_t)
    
    logger.debug('postprocss time: %s', time.time()-t1)
    t1 = time.time()
    
    return s
