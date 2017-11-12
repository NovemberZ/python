# -*- coding: utf-8 -*-

import yaml
import sys

from sklearn.model_selection import train_test_split
import multiprocessing
import numpy as np
from gensim.models.word2vec import Word2Vec
from gensim.corpora.dictionary import Dictionary

from keras.preprocessing import sequence
from keras.models import Sequential
from keras.layers.embeddings import Embedding
from keras.layers.recurrent import LSTM
from keras.layers.core import Dense, Dropout, Activation
from keras.models import model_from_yaml

import jieba
import pandas as pd

np.random.seed(1337)  # For Reproducibility
sys.setrecursionlimit(1000000)
# set parameters:
cpu_count = multiprocessing.cpu_count()

word2vec_size = 100
word2vec_iter = 1  # ideally more..
word2vec_min_count = 10
word2vec_window = 7

maxlen = 100

batch_size = 32
n_epoch = 4
input_length = 100


# 加载训练文件
def load_data():
    neg = pd.read_excel('../data/sentiment_lstm/neg.xls', header=None, index=None)
    pos = pd.read_excel('../data/sentiment_lstm/pos.xls', header=None, index=None)

    data = np.concatenate((pos[0], neg[0]))
    y = np.concatenate((np.ones(len(pos), dtype=int), np.zeros(len(neg), dtype=int)))

    return data, y


# 对句子经行分词，并去掉换行符
def cut_sentence(text):
    ''' Simple Parser converting each document to lower-case, then
        removing the breaks for new lines and finally splitting on the
        whitespace
    '''
    text = [jieba.lcut(document.replace('\n', '')) for document in text]
    return text


# 创建词语字典，并返回每个词语的索引，词向量，以及每个句子所对应的词语索引
def create_dict(model=None, data=None):
    ''' Function does are number of Jobs:
        1- Creates a word to index mapping
        2- Creates a word to vector mapping
        3- Transforms the Training and Testing Dictionaries
    '''
    if (data is not None) and (model is not None):
        gensim_dict = Dictionary()
        gensim_dict.doc2bow(model.wv.vocab.keys(), allow_update=True)

        word_idx = {v: k + 1 for k, v in gensim_dict.items()}  # 所有频数超过10的词语的索引
        word_vec = {word: model[word] for word in word_idx.keys()}  # 所有频数超过10的词语的词向量

        # Words become integers
        sentences_idx = []
        for sentence in data:
            sentence_idx = []
            for word in sentence:
                try:
                    sentence_idx.append(word_idx[word])
                except Exception as e:
                    sentence_idx.append(0)
                sentences_idx.append(sentence_idx)

        # 每个句子所含词语对应的索引，所以句子中含有频数小于10的词语，索引为0
        sentences_idx = sequence.pad_sequences(sentences_idx, maxlen=maxlen)
        return word_idx, word_vec, sentences_idx
    else:
        print('No data provided...')


# 创建词语字典，并返回每个词语的索引，词向量，以及每个句子所对应的词语索引
def train_word2vec(sentences):
    model = Word2Vec(size=word2vec_size,
                     min_count=word2vec_min_count,
                     window=word2vec_window,
                     workers=cpu_count,
                     iter=word2vec_iter)
    model.build_vocab(sentences)

    model.train(sentences, total_examples=model.corpus_count, epochs=model.iter)

    model.save('../model/Word2vec_model.pkl')
    word_idx, word_vec, sentences_idx = create_dict(model=model, combined=sentences)
    return word_idx, word_vec, sentences_idx


def preprocess_lstm(word_idx, word_vec, sentences_idx, y):
    n_symbols = len(word_idx) + 1  # 所有单词的索引数，频数小于10的词语索引为0，也作为一个单词，所以加1
    embedding_weights = np.zeros((n_symbols, word2vec_size))  # 索引为0的词语，词向量全为0
    for word, index in word_idx.items():  # 从索引为1的词语开始，对每个词语对应其词向量
        embedding_weights[index, :] = word_vec[word]
    x_train, x_test, y_train, y_test = train_test_split(sentences_idx, y, test_size=0.2)
    print(x_train.shape, y_train.shape)
    return n_symbols, embedding_weights, x_train, y_train, x_test, y_test


# 定义网络结构
def train_lstm(n_symbols, embedding_weights, x_train, y_train, x_test, y_test):
    print('Defining a Simple Keras Model...')

    model = Sequential()  # or Graph or whatever
    model.add(Embedding(output_dim=word2vec_size,
                        input_dim=n_symbols,
                        mask_zero=True,
                        weights=[embedding_weights],
                        input_length=input_length))  # Adding Input Length
    model.add(LSTM(output_dim=50, activation='sigmoid', inner_activation='hard_sigmoid'))
    model.add(Dropout(0.5))
    model.add(Dense(1))
    model.add(Activation('sigmoid'))

    print('Compiling the Model...')
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

    print("Training the Model...")
    model.fit(x_train, y_train, batch_size=batch_size, epochs=n_epoch, verbose=1,
              validation_data=(x_test, y_test))

    print("Evaluate the Model...")
    score = model.evaluate(x_test, y_test, batch_size=batch_size)

    yaml_string = model.to_yaml()
    with open('../model/lstm.yml', 'w') as outfile:
        outfile.write(yaml.dump(yaml_string, default_flow_style=True))
    model.save_weights('../model/lstm.h5')
    print('Test score:', score)


# 训练模型，并保存
def train():
    print('Loading Data...')
    data, y = load_data()
    print("load_data:", len(data), len(y))

    # sentences = [['first', 'sentence'], ['second', 'sentence']]
    print('Tokenising...')
    sentences = cut_sentence(data)
    print("cut_sentence:", len(sentences))

    print('Training a Word2vec model...')
    word_idx, word_vec, sentences_idx = train_word2vec(sentences)

    print('Setting up Arrays for Keras Embedding Layer...')
    n_symbols, embedding_weights, x_train, y_train, x_test, y_test = preprocess_lstm(word_idx,
                                                                                     word_vec, sentences_idx, y)
    print(x_train.shape, y_train.shape)
    train_lstm(n_symbols, embedding_weights, x_train, y_train, x_test, y_test)


def input_transform(txt):
    words = jieba.lcut(txt)
    words = np.array(words).reshape(1, -1)
    model = Word2Vec.load('../model/Word2vec_model.pkl')
    _, _, sentences_idx = create_dict(model, words)
    return sentences_idx


def lstm_predict(txt):
    print('loading model......')
    with open('../model/lstm.yml', 'r') as f:
        yaml_string = yaml.load(f)
    model = model_from_yaml(yaml_string)

    print('loading weights......')
    model.load_weights('../model/lstm.h5')
    model.compile(loss='binary_crossentropy',
                  optimizer='adam', metrics=['accuracy'])
    data = input_transform(txt)
    data.reshape(1, -1)
    # print data
    result = model.predict_classes(data)
    if result[0][0] == 1:
        print(txt, 1)
    else:
        print(txt, 0)


if __name__ == '__main__':

    if(0):
        train()

    pred_data = ['电池充完了电连手机都打不开.简直烂的要命.真是金玉其外,败絮其中!连5号电池都不如',
                 '不错的手机，从3米高的地方摔下去都没坏，质量非常好',
                 '酒店的环境非常好，价格也便宜，值得推荐'
                 '手机质量太差了，傻逼店家，赚黑心钱，以后再也不会买了',
                 '我是傻逼',
                 '你是傻逼',
                 '屏幕较差，拍照也很粗糙。',
                 '质量不错，是正品 ，安装师傅也很好，才要了83元材料费',
                 '东西非常不错，安装师傅很负责人，装的也很漂亮，精致，谢谢安装师傅！']

    for txt in pred_data:
        lstm_predict(txt)
