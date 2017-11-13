# -*- coding: utf-8 -*-

import yaml
import sys
import os

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

np.random.seed(1337)  # For Reproducibility
sys.setrecursionlimit(1000000)
# set parameters:
cpu_count = multiprocessing.cpu_count()

word2vec_size = 100  # 神经网络单元的个数
word2vec_iter = 1  # ideally more..
word2vec_min_count = 10  # 统计数小余10的话，忽略
word2vec_window = 7  # 窗口为7：前3后3

batch_size = 32
epochs = 4
input_length = 50  # 每个句子input_length个单词


# 加载训练文件
def load_data():
    base_path = '../data/sentiment_lstm/'

    pos = []
    with open(os.path.join(base_path, 'pos.txt')) as f:
        for line in f:
            pos.append(line)

    neg = []
    with open(os.path.join(base_path, 'neg.txt')) as f:
        for line in f.readlines():
            neg.append(line)

    x = np.concatenate((np.array(pos), np.array(neg)))
    y = np.concatenate((np.ones(len(pos), dtype=int), np.zeros(len(neg), dtype=int)))

    return x, y


# 对句子经行分词，并去掉换行符
def cut_word(text):
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
        sentences_idx = sequence.pad_sequences(sentences_idx, maxlen=input_length)
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
    word_idx, word_vec, sentences_idx = create_dict(model=model, data=sentences)
    return word_idx, word_vec, sentences_idx


def preprocess_lstm(word_idx, word_vec, sentences_idx, y):
    n_symbols = len(word_idx) + 1  # 所有单词的索引数，频数小于10的词语索引为0，也作为一个单词，所以加1
    embedding_weights = np.zeros((n_symbols, word2vec_size))  # 索引为0的词语，词向量全为0
    print('embedding_weights shape:', embedding_weights.shape)

    for word, index in word_idx.items():  # 从索引为1的词语开始，对每个词语对应其词向量
        embedding_weights[index, :] = word_vec[word]

    x_train, x_test, y_train, y_test = train_test_split(sentences_idx, y, test_size=0.2)
    return n_symbols, embedding_weights, x_train, y_train, x_test, y_test


# 定义网络结构
def train_lstm(n_symbols, embedding_weights, x_train, y_train, x_test, y_test):
    print('Defining a Simple Keras Model...')

    print('x_train shape:', x_train.shape)
    print('y_train shape:', y_train.shape)
    model = Sequential()  # or Graph or whatever
    # Embedding Param Count: 8308[单词数+1] * 100[维度]
    model.add(Embedding(output_dim=word2vec_size,
                        input_dim=n_symbols,
                        mask_zero=True,
                        weights=[embedding_weights],
                        input_length=input_length))  # Adding Input Length
    '''
    cell 的权重是共享的，那么一层的 LSTM 的参数有多少个？假设 num_units 是128，输入是28位的，那么根据上面的第二点，
    可以得到，四个小黄框的参数一共有 （128+28）*（128*4），也就是156 * 512，可以看看 TensorFlow 的最简单的 LSTM 的案例，
    中间层的参数就是这样，不过还要加上输出的时候的激活函数的参数，假设是10个类的话，就是128*10的 W 参数和10个bias 参数
    '''
    # LSTM Param Count: (100[词向量个数] + 1[bias] + 50[反馈]) * 50[隐藏层个数] * 4[4个网络] = 30200
    model.add(LSTM(units=50, activation='sigmoid', recurrent_activation='hard_sigmoid'))
    model.add(Dropout(0.5))
    model.add(Dense(1))
    model.add(Activation('sigmoid'))

    model.summary()

    print('Compiling the Model...')
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

    print("Training the Model...")
    model.fit(x_train, y_train, batch_size=batch_size, epochs=epochs, verbose=1,
              validation_data=(x_test, y_test))

    print("Evaluate the Model...")
    score = model.evaluate(x_test, y_test, batch_size=batch_size)

    yaml_string = model.to_yaml()
    with open('../model/lstm.yml', 'w') as outfile:
        outfile.write(yaml.dump(yaml_string, default_flow_style=True))
    model.save_weights('../model/lstm.h5')
    print('Test score:', score)


def input_transform(txt):
    data = [txt]
    sentences = cut_word(data)

    model = Word2Vec.load('../model/Word2vec_model.pkl')
    _, _, sentences_idx = create_dict(model, sentences)
    return sentences_idx


def predict_lstm(texts):
    print('loading model......')
    with open('../model/lstm.yml', 'r') as f:
        yaml_string = yaml.load(f)
    model = model_from_yaml(yaml_string)

    print('loading weights......')
    model.load_weights('../model/lstm.h5')
    model.compile(loss='binary_crossentropy',
                  optimizer='adam', metrics=['accuracy'])
    model.summary()

    for txt in texts:
        data = input_transform(txt)
        # print data
        result = model.predict_classes(data)
        if result[0][0] == 1:
            print(txt, 1)
        else:
            print(txt, 0)


# 训练模型，并保存
def train():
    print('Loading Data...')
    x, y = load_data()
    print("load_data:", len(x), len(y))

    # sentences = [['first', 'sentence'], ['second', 'sentence']]
    print('Tokenising...')
    sentences = cut_word(x)
    print("cut_word:", len(sentences))

    print('Training a Word2vec model...')
    word_idx, word_vec, sentences_idx = train_word2vec(sentences)

    print('Setting up Arrays for Keras Embedding Layer...')
    n_symbols, embedding_weights, x_train, y_train, x_test, y_test = preprocess_lstm(word_idx,
                                                                                     word_vec, sentences_idx, y)
    train_lstm(n_symbols, embedding_weights, x_train, y_train, x_test, y_test)


if __name__ == '__main__':

    if(1):
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

    predict_lstm(pred_data)
