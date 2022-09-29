from google.colab import drive
import tensorflow as tf
from tensorflow import keras
from keras import layers

drive.mount('/content/drive')
%cd /content/drive/MyDrive/專題實驗/training_dataset/


imgSize = (224, 224)
batchSize = 32

# set the training dataset
train_ds = tf.keras.preprocessing.image_dataset_from_directory(
    "train",
    validation_split = 0.1,
    subset = "training",
    seed = 1337,
    image_size = imgSize,
    batch_size = batchSize,
)

# set the validation dataset
val_ds = tf.keras.preprocessing.image_dataset_from_directory(
    "validation",
    validation_split = 0.9,
    subset = "validation",
    seed = 1337,
    image_size = imgSize,
    batch_size = batchSize,
)

# set the data augmentation
data_augmentation = keras.Sequential(
    [
        layers.RandomFlip("horizontal"),
        layers.RandomRotation(0.1),
        layers.Rescaling(0.7),
        layers.Rescaling(0.8),
        layers.RandomTranslation((-0.2, 0.3), (-0.2, 0.3)),
    ]
)

# set the training model
def setModel(inputSize, typeNum):
    input = keras.Input(shape = inputSize)
    x = data_augmentation(input)
    x = layers.Rescaling(1.0 / 255)(x)
    x = layers.Conv2D(32, 3, strides=2, padding="same")(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation("relu")(x)
    x = layers.Conv2D(64, 3, padding="same")(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation("relu")(x)
    previous_block_activation = x

    for size in [128, 256, 512, 728]:
        x = layers.Activation("relu")(x)
        x = layers.SeparableConv2D(size, 3, padding="same")(x)
        x = layers.BatchNormalization()(x)
        x = layers.Activation("relu")(x)
        x = layers.SeparableConv2D(size, 3, padding="same")(x)
        x = layers.BatchNormalization()(x)
        x = layers.MaxPooling2D(3, strides=2, padding="same")(x)
        residual = layers.Conv2D(size, 1, strides=2, padding="same")(
            previous_block_activation
        )
        x = layers.add([x, residual])
        previous_block_activation = x

    x = layers.SeparableConv2D(1024, 3, padding="same")(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation("relu")(x)
    x = layers.GlobalAveragePooling2D()(x)
    activation = "sigmoid"
    units = 1

    x = layers.Dropout(0.2)(x)
    output = layers.Dense(units, activation=activation)(x)
    return keras.Model(input, output)


model = setModel(imgSize + (3,), 2)
keras.utils.plot_model(model, show_shapes=True)

epochs = 50
callbacks = [keras.callbacks.ModelCheckpoint("save_at_{epoch}.h5"),]
model.compile(
    optimizer=keras.optimizers.Adam(1e-3),
    loss="binary_crossentropy",
    metrics=["accuracy"],
)

model.fit(
    train_ds,
    epochs = epochs,
    callbacks = callbacks,
    validation_data = val_ds,
)

# save the final model and weights
model.save('model.hdf5')
model.save_weights('model_weights.h5')
