from PIL import Image
import struct


def read_image(from_filename, to_path):
  f = open(from_filename, 'rb')

  index = 0
  buf = f.read()

  f.close()

  magic, images, rows, columns = struct.unpack_from('>IIII', buf, index)
  index += struct.calcsize('>IIII')

  for i in range(images):
    image = Image.new('L', (columns, rows))
    for x in range(rows):
      for y in range(columns):
        image.putpixel((y, x), int(struct.unpack_from('>B', buf, index)[0]))
        index += struct.calcsize('>B')
    print('save ' + str(i) + 'image')
    image.save(to_path + '/' + str(i) + '.png')


def read_label(from_filename, to_filename):
  f = open(from_filename, 'rb')
  index = 0
  buf = f.read()

  f.close()

  magic, labels = struct.unpack_from('>II', buf, index)
  index += struct.calcsize('>II')

  labelArr = [0] * labels
  #labelArr = [0] * 2000

  for x in range(labels):
    labelArr[x] = int(struct.unpack_from('>B', buf, index)[0])
    index += struct.calcsize('>B')

  save = open(to_filename, 'w')

  save.write(','.join(map(lambda x: str(x), labelArr)))
  save.write('\n')

  save.close()
  print('save labels success')


def read_image_to_list(from_filename):
  f = open(from_filename, 'rb')

  index = 0
  buf = f.read()

  f.close()

  magic, images, rows, columns = struct.unpack_from('>IIII', buf, index)
  index += struct.calcsize('>IIII')

  imgs_list = []
  for i in range(images):
    image = Image.new('L', (columns, rows))
    img_list = []
    for x in range(rows):
      row_list = []
      for y in range(columns):
        row_list.append(int(struct.unpack_from('>B', buf, index)[0]))
        index += struct.calcsize('>B')
      img_list.append(row_list)
    print('read ' + str(i) + ' image')
    imgs_list.append(img_list)
  print("images size = ", len(imgs_list))

  return imgs_list


def read_label_to_list(from_filename):
  f = open(from_filename, 'rb')
  index = 0
  buf = f.read()

  f.close()

  magic, labels = struct.unpack_from('>II', buf, index)
  index += struct.calcsize('>II')

  label_list = []
  for x in range(labels):
    label_list.append(int(struct.unpack_from('>B', buf, index)[0]))
    index += struct.calcsize('>B')

  print('labels size =', len(label_list))
  return label_list


def load_data():
  x_train = read_image_to_list('../data/mnist/train-images-idx3-ubyte')
  y_train = read_label_to_list('../data/mnist/train-labels-idx1-ubyte')

  x_test = read_image_to_list('../data/mnist/t10k-images-idx3-ubyte')
  y_test = read_label_to_list('../data/mnist/t10k-labels-idx1-ubyte')

  return (x_train, y_train), (x_test, y_test)


if __name__ == '__main__':
  # read_image('../data/mnist/train-images-idx3-ubyte', '../data/mnist/train')
  # read_label('../data/mnist/train-labels-idx1-ubyte', '../data/mnist/train_label.txt')

  # read_image('../data/mnist/t10k-images-idx3-ubyte', '../data/mnist/test')
  # read_label('../data/mnist/t10k-labels-idx1-ubyte', '../data/mnist/test_label.txt')

  read_image_to_list('../data/mnist/t10k-images-idx3-ubyte')
