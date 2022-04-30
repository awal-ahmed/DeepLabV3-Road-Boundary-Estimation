# -*- coding: utf-8 -*-
"""resnet50 with jaccard index loss and loss weight.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Wk74T8Q_MF5r_mX7lkgZJzxMhtqlvEt_
"""

from google.colab import drive
drive.mount('/content/drive')

"""**source:** https://www.kaggle.com/awalahmedfime/bacteria-segmentation/edit/run/42535923"""

import numpy as np
import pandas as pd
from PIL import Image
import os
import cv2
from tqdm import tqdm
import tensorflow as tf
import matplotlib.pyplot as plt
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow import keras

"""**Constants**"""

#Select loss
model_name = 'resnet50'                                 
loss_fucntion = 'jaccard_index'             
add_weight = 'Yes'

np.random.seed(41)
IMAGE_HEIGHT = 256
IMAGE_WIDTH = 256
BATCH_SIZE = 16
NUM_CLASSES = 3
IMG_PATH = '/content/drive/My Drive/Machine Learning/iccv09 3 class/train Image/'
MASK_PATH = '/content/drive/My Drive/Machine Learning/iccv09 3 class/mask/'
#LABEL_PATH = '../input/bacteria-detection-with-darkfield-microscopy/masks/'
IMG_SUB_PATH = '/content/drive/My Drive/Machine Learning/iccv09 3 class/train Image/Image/'
MASK_SUB_PATH = '/content/drive/My Drive/Machine Learning/iccv09 3 class/train One hot/One hot/'
ONEHOT_MASK = '/content/drive/My Drive/Machine Learning/iccv09 3 class/mask/mask'

"""Mask need to be onehot incoded

mask_files = os.listdir(MASK_SUB_PATH)
for mf in tqdm (mask_files):
    mask_img = cv2.imread(os.path.join(MASK_SUB_PATH, mf))
    mask_img = mask_img/255
    cv2.imwrite(os.path.join(ONEHOT_MASK, mf), mask_img)

Helper functions

**source:** https://github.com/keras-team/keras/issues/3059#issuecomment-364787723
"""

training_generation_args = dict(
     #width_shift_range=0.3,
     #height_shift_range=0.3,
    horizontal_flip=True,
    #vertical_flip=True,
    zoom_range=0.2,
    validation_split=0.1,
)
train_image_datagen = ImageDataGenerator(**training_generation_args)
train_label_datagen = ImageDataGenerator(**training_generation_args)

# data load
training_image_generator = train_image_datagen.flow_from_directory(
    IMG_PATH,
    target_size=(IMAGE_HEIGHT, IMAGE_WIDTH),
    class_mode=None,
    subset='training',
    batch_size=BATCH_SIZE,
    seed=1
)
training_label_generator = train_label_datagen.flow_from_directory(
    MASK_PATH,
    target_size=(IMAGE_HEIGHT, IMAGE_WIDTH),
    class_mode=None,
    subset='training',
    batch_size=BATCH_SIZE,
    # color_mode='grayscale',
    seed=1
)


# validation data load
validation_image_generator = train_image_datagen.flow_from_directory(
    IMG_PATH,
    target_size=(IMAGE_HEIGHT, IMAGE_WIDTH),
    class_mode=None,
    subset='validation',
    batch_size=BATCH_SIZE,
    seed=1
)
validation_label_generator = train_label_datagen.flow_from_directory(
    MASK_PATH,
    target_size=(IMAGE_HEIGHT, IMAGE_WIDTH),
    class_mode=None,
    subset='validation',
    batch_size=BATCH_SIZE,
    # color_mode='grayscale',
    seed=1
)

train_generator = zip(training_image_generator, training_label_generator)
validation_generator = zip(validation_image_generator, validation_label_generator)

"""**Class imblanace**
source:  https://stackoverflow.com/questions/52123670 
Keras model loss_weight: Keras - compile method
"""

loss_weights = {
    0: 0,
    1: 0,
    2:0
}
mask_files = os.listdir(ONEHOT_MASK)
for mf in tqdm(mask_files):
    mask_img = cv2.imread(os.path.join(ONEHOT_MASK, mf))
    classes = tf.argmax(mask_img, axis=-1).numpy()
    class_counts = np.unique(classes, return_counts=True)
    
    for c in range(len(class_counts[0])):
        loss_weights[class_counts[0][c]] += class_counts[1][c]

print(loss_weights)

total = sum(loss_weights.values())
for cl, v in loss_weights.items():
    # do inverse
    loss_weights[cl] = total / (v*3)
    
loss_weights

"""Create a modifier that is the same shape as output"""

w = [[loss_weights[0], loss_weights[1], loss_weights[2]]] * IMAGE_WIDTH
h = [w] * IMAGE_HEIGHT
loss_mod = np.array(h)

"""Model"""

def AtrousSpatialPyramidPooling(input_shape):

  inputs = tf.keras.Input(input_shape[-3:]);
  # global pooling
  results = tf.keras.layers.Lambda(lambda x: tf.math.reduce_mean(x, [1,2], keepdims = True))(inputs);
  results = tf.keras.layers.Conv2D(256, kernel_size = (1,1), padding = 'same', kernel_initializer = tf.keras.initializers.he_normal(), use_bias = False)(results);
  results = tf.keras.layers.BatchNormalization()(results);
  results = tf.keras.layers.ReLU()(results);
  pool = tf.keras.layers.UpSampling2D(size = (input_shape[-3] // results.shape[1], input_shape[-2] // results.shape[2]), interpolation = 'bilinear')(results);
  results = tf.keras.layers.Conv2D(256, kernel_size = (1,1), dilation_rate = 1, padding = 'same', kernel_initializer = tf.keras.initializers.he_normal(), use_bias = False)(inputs);
  results = tf.keras.layers.BatchNormalization()(results);
  dilated_1 = tf.keras.layers.ReLU()(results);
  results = tf.keras.layers.Conv2D(256, kernel_size = (3,3), dilation_rate = 6, padding = 'same', kernel_initializer = tf.keras.initializers.he_normal(), use_bias = False)(inputs);
  results = tf.keras.layers.BatchNormalization()(results);
  dilated_6 = tf.keras.layers.ReLU()(results);
  results = tf.keras.layers.Conv2D(256, kernel_size = (3,3), dilation_rate = 12, padding = 'same', kernel_initializer = tf.keras.initializers.he_normal(), use_bias = False)(inputs);
  results = tf.keras.layers.BatchNormalization()(results);
  dilated_12 = tf.keras.layers.ReLU()(results);
  results = tf.keras.layers.Conv2D(256, kernel_size = (3,3), dilation_rate = 18, padding = 'same', kernel_initializer = tf.keras.initializers.he_normal(), use_bias = False)(inputs);
  results = tf.keras.layers.BatchNormalization()(results);
  dilated_18 = tf.keras.layers.ReLU()(results);
  results = tf.keras.layers.Concatenate(axis = -1)([dilated_1, dilated_6, dilated_12, dilated_18, pool]);
  results = tf.keras.layers.Conv2D(256, kernel_size = (1,1), dilation_rate = 1, padding = 'same', kernel_initializer = tf.keras.initializers.he_normal(), use_bias = False)(results);
  results = tf.keras.layers.BatchNormalization()(results);
  results = tf.keras.layers.ReLU()(results);
  return tf.keras.Model(inputs = inputs, outputs = results);

input_shape = (IMAGE_HEIGHT, IMAGE_WIDTH, 3)

inputs = tf.keras.Input(input_shape[-3:]);

model_name = 'resnet50'
resnet50 = tf.keras.applications.ResNet50(input_tensor = inputs, weights = 'imagenet', include_top = False);
results = resnet50.get_layer('conv4_block6_2_relu').output;
results = AtrousSpatialPyramidPooling(results.shape[-3:])(results);
a = tf.keras.layers.UpSampling2D(size = (input_shape[-3] // 4 // results.shape[1], input_shape[-2] // 4 // results.shape[2]), interpolation = 'bilinear')(results);
results = resnet50.get_layer('conv2_block3_2_relu').output;
results = tf.keras.layers.Conv2D(48, kernel_size = (1,1), padding = 'same', kernel_initializer = tf.keras.initializers.he_normal(), use_bias = False)(results);
results = tf.keras.layers.BatchNormalization()(results);
b = tf.keras.layers.ReLU()(results);
results = tf.keras.layers.Concatenate(axis = -1)([a, b]);
results = tf.keras.layers.Conv2D(256, kernel_size = (3,3), padding = 'same', activation = 'relu', kernel_initializer = tf.keras.initializers.he_normal(), use_bias = False)(results);
results = tf.keras.layers.BatchNormalization()(results);
results = tf.keras.layers.ReLU()(results);
results = tf.keras.layers.Conv2D(32, kernel_size = (3,3), padding = 'same', activation = 'relu', kernel_initializer = tf.keras.initializers.he_normal(), use_bias = False)(results);
results = tf.keras.layers.BatchNormalization()(results);
results = tf.keras.layers.ReLU()(results);
results = tf.keras.layers.UpSampling2D(size = (input_shape[-3] // results.shape[1], input_shape[-2] // results.shape[2]), interpolation = 'bilinear')(results);
output1 = tf.keras.layers.Conv2D(3, kernel_size = (1,1), padding = 'same', activation = 'softmax')(results);

model = tf.keras.Model(inputs = [inputs], outputs = [output1])
#model = DeeplabV3Plus((274,256,256,3),9);

#model.summary()

from keras import backend as K

def jaccard_index(y_true, y_pred, smooth=1):
    intersection = K.sum(K.abs(y_true * y_pred), axis=-1)
    sum_ = K.sum(K.abs(y_true) + K.abs(y_pred), axis=-1)
    jac = (intersection + smooth) / (sum_ - intersection + smooth)
    #return (1 - jac) * smooth
    return jac

def jaccard_index_loss(y_true, y_pred, smooth=1):
    return (1 - jaccard_index(y_true, y_pred)) * smooth

# Jaccard Index loss with weight
model.compile(optimizer='adam',
              loss=jaccard_index_loss,
              metrics=[jaccard_index],
              loss_weights=loss_mod)

ACCURACY_THRESHOLD = 0.0
class myCallback(tf.keras.callbacks.Callback): 
    def on_epoch_end(self, epoch, logs={}): 
        global ACCURACY_THRESHOLD
        if(logs.get('jaccard_index') > ACCURACY_THRESHOLD ):
            ACCURACY_THRESHOLD = logs.get('jaccard_index')
            model.save("/content/drive/MyDrive/Machine Learning/iccv09 3 class/"+model_name+"_"+loss_fucntion+"_loss_"+add_weight+".h5")
callbacks = myCallback()

model_history = model.fit(train_generator,
                          epochs=100,
                          steps_per_epoch=training_image_generator.samples // BATCH_SIZE,
                          #shuffle=True,
                          validation_data=validation_generator,
                          validation_steps=validation_image_generator.samples // BATCH_SIZE,
                          callbacks=[callbacks])

#save history
np.save("/content/drive/MyDrive/Machine Learning/iccv09 3 class/"+model_name+"_"+loss_fucntion+"_loss_"+add_weight+".npy",model_history.history)
hist_df = pd.DataFrame(model_history.history) 
hist_csv_file = "/content/drive/MyDrive/Machine Learning/iccv09 3 class/"+model_name+"_"+loss_fucntion+"_loss_"+add_weight+".csv"
with open(hist_csv_file, mode='w') as f:
    hist_df.to_csv(f)

#Reload model
modelFile = "/content/drive/MyDrive/Machine Learning/iccv09 3 class/"+model_name+"_"+loss_fucntion+"_loss_"+add_weight+".h5"
model = keras.models.load_model(modelFile, custom_objects={'jaccard_index_loss': jaccard_index_loss, 'jaccard_index':jaccard_index})

test1 = "/content/drive/My Drive/Machine Learning/iccv09 3 class/Out pic"
out = "/content/drive/MyDrive/Machine Learning/"+model_name+"_"+loss_fucntion+"_loss_"+add_weight+"/"
if os.path.exists(out) is False:
  os.mkdir(out)
mask_files = os.listdir(test1)
for mf in tqdm (mask_files):
    img = cv2.imread(os.path.join(test1, mf) )
    #print(img.shape)
    img =  cv2.resize(img, (256, 256))
    img=np.expand_dims(img, 0)
    img = model.predict(img)
    img =  np.squeeze(img)
    img1 = np.zeros(( IMAGE_HEIGHT , IMAGE_WIDTH, 3), dtype= np.int)
    for i in range(256):
      for j in range(256):
          img1[i][j][np.argmax(img[i][j])]=1
    cv2.imwrite(os.path.join(out, mf), img1)

mask_files = os.listdir(out)
for mf in tqdm (mask_files):
  img = cv2.imread(os.path.join(out, mf) )
  img = img*255
  cv2.imwrite(os.path.join(out, mf), cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

test_p = "/content/drive/My Drive/Machine Learning/iccv09 3 class/test Image/"
test_m = "/content/drive/My Drive/Machine Learning/iccv09 3 class/test one hot/"


tst_fies = os.listdir(test_m)
tst_fies.sort()
test= np.zeros((len(tst_fies), IMAGE_HEIGHT , IMAGE_WIDTH, 3), dtype= np.bool)
for n, mf in tqdm(enumerate(tst_fies), total=len(tst_fies)):
  img = cv2.imread(os.path.join(test_m, mf) )
  img = cv2.resize(img, (256, 256))
  img = img / 255
  test[n] = img


acc = []
pre = []
rec = []
f_me = []
test_files = os.listdir(test_p)
test_files.sort()
for n, mf in tqdm(enumerate(test_files), total=len(test_files)):
  img = cv2.imread(os.path.join(test_p, mf) )
  img =  cv2.resize(img, (256, 256))
  img=np.expand_dims(img, 0)
  img = model.predict(img)
  img =  np.squeeze(img)
  img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
  img = img > .5
  test1 = test[n]
  TP = tf.math.count_nonzero(img * test1)
  TN = tf.math.count_nonzero((img - 1) * (test1 - 1))
  FP = tf.math.count_nonzero(img * (test1 - 1))
  FN = tf.math.count_nonzero((img - 1) * test1)
  accuracy = (TP + TN) / (TP + TN + FP + FN)
  precision = TP / (TP + FP)
  recall = TP / (TP + FN)
  f1 = 2 * precision * recall / (precision + recall)
  acc.append(accuracy)
  pre.append(precision)
  rec.append(recall)
  f_me.append(f1)

print("Mean")

print(sum(rec)/len(tst_fies))
print(sum(pre)/len(tst_fies))
print(sum(acc)/len(tst_fies))
print(sum(f_me)/len(tst_fies))

print("SD")

print(np.std(rec))
print(np.std(pre))
print(np.std(acc))
print(np.std(f_me))