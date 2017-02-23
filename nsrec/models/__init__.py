import tensorflow as tf
from nsrec.models.nsr_model import CNNNSREvalModel
from nsrec.models.nsr_length_model import CNNLengthTrainModel
from nsrec.models.mnist_model import CNNMnistTrainModel
from nsrec.models.model_config import CNNNSRModelConfig, CNNNSRInferModelConfig, CNNGeneralModelConfig
from nsrec.models.nsr_bbox_model import CNNBBoxTrainModel, CNNBBoxInferModel, CNNBBoxToExportModel
from nsrec.models.nsr_model import CNNNSREvalModel, CNNNSRTrainModel, RNNTrainModel, RNNEvalModel, CNNNSRInferenceModel, \
  CNNNSRToExportModel


def create_model(flags, mode='train'):
  assert mode in ['train', 'eval', 'inference', 'to_export']

  model_clz = {
    'bbox-train': CNNBBoxTrainModel,
    'bbox-inference': CNNBBoxInferModel,
    'bbox-to_export': CNNBBoxToExportModel,
    'length-train': CNNLengthTrainModel,
    'length-eval': CNNNSREvalModel,
    'mnist-train': CNNMnistTrainModel,
    'all-train': CNNNSRTrainModel,
    'all-train-rnn': RNNTrainModel,
    'all-eval': CNNNSREvalModel,
    'all-eval-rnn': RNNEvalModel,
    'all-inference': CNNNSRInferenceModel,
    'all-to_export': CNNNSRToExportModel
  }

  key = '%s-%s' % (flags.model_type, mode)
  if flags.rnn:
    key = key + '-rnn'
    tf.logging.info('using rnn')

  if key not in model_clz:
    raise Exception('Unimplemented model: model_type=%s, mode=%s' % (flags.model_type, mode))

  params_dict = {
    'net_type': flags.net_type,
    'gray_scale': flags.gray_scale
  }

  if flags.model_type in ['length', 'all', 'bbox']:
    params_dict.update({'max_number_length': flags.max_number_length})
    if mode in ['train', 'eval']:
      params_dict.update({
        'num_preprocess_threads': flags.num_preprocess_threads,
        'data_file_path': flags.data_file_path,
        'batch_size': flags.batch_size,
      })
      config = CNNNSRModelConfig(**params_dict)
    else:
      config = CNNNSRInferModelConfig(**params_dict)
  else:
    params_dict.update({
      'num_classes': 10,
      'batch_size': flags.batch_size,
    })
    config = CNNGeneralModelConfig(**params_dict)

  tf.logging.info('using config: %s', config)
  return model_clz[key](config)