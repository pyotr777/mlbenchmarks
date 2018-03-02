from __future__ import print_function
import argparse

import chainer
import chainer.links as L
from chainer import training
from chainer.training import extensions
from chainer.training import triggers

from chainer.datasets import get_cifar10
from chainer.datasets import get_cifar100

import models.VGG
import cupy as cp
import random
import numpy as np

def main():

    parser = argparse.ArgumentParser(description='Chainer CIFAR example:')
    parser.add_argument('--dataset', '-d', default='cifar10',
                        help='The dataset to use: cifar10 or cifar100')
    parser.add_argument('--batchsize', '-b', type=int, default=64,
                        help='Number of images in each mini-batch')
    parser.add_argument('--learnrate', '-l', type=float, default=0.05,
                        help='Learning rate for SGD')
    parser.add_argument('--epoch', '-e', type=int, default=100,
                        help='Number of sweeps over the dataset to train')
    parser.add_argument('--gpu', '-g', type=int, default=0,
                        help='GPU ID (negative value indicates CPU)')
    parser.add_argument('--out', '-o', default='result',
                        help='Directory to output the result')
    parser.add_argument('--resume', '-r', default='',
                        help='Resume the training from snapshot')
    parser.add_argument('--early-stopping', type=str,
                        help='Metric to watch for early stopping')
    parser.add_argument('--host', type=str, help='Host name (used in log file name)')
    parser.add_argument('--debug', action='store_true', help='Log timing info')
    parser.add_argument('--accuracy', type=float, default=1, help='Log timing info')
    args = parser.parse_args()

    print('GPU: {}'.format(args.gpu))
    print('# Minibatch-size: {}'.format(args.batchsize))
    print('# epoch: {}'.format(args.epoch))


    chainer.global_config.cudnn_deterministic = True
    seed=0
    random.seed(seed)
    np.random.seed(seed)
    cp.random.seed(seed)
    print("Deterministic")
    #print("Non-Deterministic")


    # Set up a neural network to train.
    # Classifier reports softmax cross entropy loss and accuracy at every
    # iteration, which will be used by the PrintReport extension below.
    if args.dataset == 'cifar10':
        print('Using CIFAR10 dataset.')
        class_labels = 10
        train, test = get_cifar10()
    elif args.dataset == 'cifar100':
        print('Using CIFAR100 dataset.')
        class_labels = 100
        train, test = get_cifar100()
    else:
        raise RuntimeError('Invalid dataset choice.')


    print('')

    model = L.Classifier(models.VGG.VGG(class_labels))
    if args.gpu >= 0:
        # Make a specified GPU current
        chainer.cuda.get_device_from_id(args.gpu).use()
        model.to_gpu()  # Copy the model to the GPU

    optimizer = chainer.optimizers.MomentumSGD(args.learnrate)
    optimizer.setup(model)
    optimizer.add_hook(chainer.optimizer.WeightDecay(5e-4))


    train_iter = chainer.iterators.SerialIterator(train, args.batchsize)
    test_iter = chainer.iterators.SerialIterator(test, args.batchsize,
                                                 repeat=False, shuffle=False)

    #stop_trigger = (args.epoch, 'epoch')
    if args.epoch:
        epoch = args.epoch
        stop_trigger = StopTrigger('validation/main/accuracy',args.accuracy,max_epoch=epoch)
    else:
        stop_trigger = StopTrigger('validation/main/accuracy',args.accuracy)
    # Early stopping option
    # if args.early_stopping:
    #     stop_trigger = triggers.EarlyStoppingTrigger(
    #         monitor=args.early_stopping, verbose=True,
    #         max_trigger=(args.epoch, 'epoch'))

    # Set up a trainer
    updater = training.StandardUpdater(train_iter, optimizer, device=args.gpu)
    trainer = training.Trainer(updater, stop_trigger, out=args.out)

    # Evaluate the model with the test dataset for each epoch
    trainer.extend(extensions.Evaluator(test_iter, model, device=args.gpu))

    # Reduce the learning rate by half every 25 epochs.
    trainer.extend(extensions.ExponentialShift('lr', 0.5),
                   trigger=(25, 'epoch'))

    # Dump a computational graph from 'loss' variable at the first iteration
    # The "main" refers to the target link of the "main" optimizer.
    #trainer.extend(extensions.dump_graph('main/loss'))

    # Take a snapshot at each epoch
    #trainer.extend(extensions.snapshot(), trigger=(args.epoch, 'epoch'))

    # Write a log of evaluation statistics for each epoch
    trainer.extend(extensions.LogReport())

    # Print selected entries of the log to stdout
    # Here "main" refers to the target link of the "main" optimizer again, and
    # "validation" refers to the default name of the Evaluator extension.
    # Entries other than 'epoch' are reported by the Classifier link, called by
    # either the updater or the evaluator.
    trainer.extend(extensions.PrintReport(
        ['epoch', 'main/loss', 'validation/main/loss',
         'main/accuracy', 'validation/main/accuracy', 'elapsed_time']))

    # Print a progress bar to stdout
    # NOTE: If you use the EarlyStoppingTrigger,
    #       training_length is needed to set
    #       because trainer.stop_trigger is not normal interval trigger.
    #trainer.extend(extensions.ProgressBar(
    #    training_length=(args.epoch, 'epoch')))

    if args.resume:
        # Resume from a snapshot
        chainer.serializers.load_npz(args.resume, trainer)

    # Run the training
    trainer.run()


class StopTrigger(object):

    def __init__(self,key = "validation/main/accuracy",threshold=1,max_epoch=100):
        self.key = key
        self.threshold = threshold
        self.max_epoch = max_epoch
        print("Stop by threshold:",key,">=",threshold)

    def __call__(self, trainer):
        if self.key in trainer.observation:
            #print("Observing:",trainer.observation[self.key],"threshold:",self.threshold)
            #print("Epoch",trainer.updater.epoch_detail)
            if trainer.observation[self.key] >= self.threshold:
                print("Threshold",self.threshold,"reached by",self.key)
                return True
            if trainer.updater.epoch_detail >= self.max_epoch:
                print("Max epoch count reached")
                return True
        return False

if __name__ == '__main__':
    main()
