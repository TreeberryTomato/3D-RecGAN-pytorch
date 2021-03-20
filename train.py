import argparse
import collections
import torch
import numpy as np
import data_loader.data_loaders as module_data
import loss.loss as module_loss
import model.metric as module_metric
import model.model as module_arch
from parse_config import ConfigParser
from trainer import Trainer


# fix random seeds for reproducibility
SEED = 123
torch.manual_seed(SEED)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False
np.random.seed(SEED)

def main(config):
    logger = config.get_logger('train')

    # setup data_loader instances
    data_loader = config.init_obj('data_loader', module_data)
    valid_data_loader = config.init_obj('test_data_loader', module_data)
    
    # build model architecture, then print to console
    model = config.init_obj('arch', module_arch)

    # get function handles of loss and metrics
    criterion = getattr(module_loss, config['loss'])
    metrics = [getattr(module_metric, met) for met in config['metrics']]

    # build optimizer, learning rate scheduler. delete every lines containing lr_scheduler for disabling scheduler
    trainable_params = filter(lambda p: p.requires_grad, model.parameters())
    
    Generator_opt = config.init_obj('optimizer', torch.optim, model.unet.parameters())
    Discriminator_opt = config.init_obj('optimizer', torch.optim, model.discriminator.parameters())
        

    lr_scheduler_G = config.init_obj('lr_scheduler', torch.optim.lr_scheduler, Generator_opt)
    lr_scheduler_D = config.init_obj('lr_scheduler', torch.optim.lr_scheduler, Discriminator_opt)

    trainer = Trainer(model, criterion, metrics, Generator_opt,Discriminator_opt,
                      config=config,
                      data_loader=data_loader,
                      valid_data_loader=valid_data_loader,
                      lr_scheduler_G=lr_scheduler_G,lr_scheduler_D=lr_scheduler_D)
    trainer.train()


if __name__ == '__main__':
    args = argparse.ArgumentParser(description='PyTorch Template')
    args.add_argument('-c', '--config', default="config.json", type=str,
                      help='config file path (default: None)')
    args.add_argument('-r', '--resume', default=None, type=str,
                      help='path to latest checkpoint (default: None)')
    args.add_argument('-d', '--device', default=None, type=str,
                      help='indices of GPUs to enable (default: all)')
    args.add_argument('-l', '--log', default='None', type=str,
                    help='log name')
    # args.add_argument('--local_rank', default=0, type=int,help='device')
    
    # custom cli options to modify configuration from default values given in json file.
    CustomArgs = collections.namedtuple('CustomArgs', 'flags type target')
    options = [
        CustomArgs(['--lr', '--learning_rate'], type=float, target='optimizer;args;lr'),
        CustomArgs(['--bs', '--batch_size'], type=int, target='data_loader;args;batch_size'),
        
    ]
    config = ConfigParser.from_args(args, options)
    # print(config.config.keys())
    # print('###########')
    # print(config.__dict__)
    # exit()
    main(config)
