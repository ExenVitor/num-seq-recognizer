import os

import tensorflow as tf

from nsrec.cnn_model import CNNNSRModelConfig, CNNNSRTrainModel, CNNLengthTrainModel, CNNMnistTrainModel, \
  CNNGeneralModelConfig, create_model

FLAGS = tf.app.flags.FLAGS

tf.flags.DEFINE_integer("log_every_n_steps", 1,
                        "Frequency at which loss and global step are logged.")
tf.flags.DEFINE_integer("number_of_steps", 5000, "Number of training steps.")
tf.flags.DEFINE_integer("batch_size", 32, "Batch size.")

default_metadata_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data/train/metadata.pickle')
tf.flags.DEFINE_string("metadata_file_path", default_metadata_file_path, "Meta data file path.")

tf.flags.DEFINE_integer("save_summaries_secs", 5, "Save summaries per secs.")

tf.flags.DEFINE_integer("save_interval_secs", 180, "Save model per secs.")

tf.flags.DEFINE_string("net_type", "lenet", "Which net to use: lenet or alexnet")

tf.flags.DEFINE_integer("max_number_length", 5, "Max number length.")

tf.flags.DEFINE_string("cnn_model_type", "all",
                       "Model type. mnist: mnist model; all: approximate all numbers; length: only approximate length")

tf.flags.DEFINE_string("optimizer", "SGD", "Optimizer: SGD")

tf.flags.DEFINE_float("learning_rate", 0.05, "Learning rate")

tf.flags.DEFINE_integer("max_checkpoints_to_keep", 5, "Max checkpoints to keep")

tf.flags.DEFINE_string("data_dir_path", None, "Train data path")

current_dir = os.path.dirname(os.path.abspath(__file__))
train_dir = os.path.join(current_dir, '../output/train')


def learning_rate_fn(batch_size):
  num_epochs_per_decay = 8.0
  learning_rate = tf.constant(FLAGS.learning_rate)
  num_batches_per_epoch = (10000 / batch_size)
  decay_steps = int(num_batches_per_epoch * num_epochs_per_decay)

  def learning_rate_decay_fn(learning_rate, global_step):
    return tf.train.exponential_decay(
      learning_rate,
      global_step,
      decay_steps=decay_steps,
      decay_rate=0.5,
      staircase=True)

  return learning_rate, learning_rate_decay_fn


def main(unused_argv):
  if not os.path.exists(train_dir):
    tf.logging.info("Creating training directory: %s", train_dir)
    os.makedirs(train_dir)

  g = tf.Graph()
  with g.as_default():
    model = create_model(FLAGS)
    model.build()

    learning_rate, learning_rate_decay_fn = learning_rate_fn(model.config.batch_size)

    train_op = tf.contrib.layers.optimize_loss(
      loss=model.total_loss,
      global_step=model.global_step,
      learning_rate=learning_rate,
      learning_rate_decay_fn=learning_rate_decay_fn,
      optimizer=FLAGS.optimizer)

    saver = tf.train.Saver(max_to_keep=FLAGS.max_checkpoints_to_keep)

  tf.contrib.slim.learning.train(
    train_op,
    train_dir,
    log_every_n_steps=FLAGS.log_every_n_steps,
    graph=g,
    global_step=model.global_step,
    number_of_steps=FLAGS.number_of_steps,
    save_interval_secs=FLAGS.save_interval_secs,
    save_summaries_secs=FLAGS.save_summaries_secs,
    saver=saver)

if __name__ == '__main__':
  tf.app.run()
