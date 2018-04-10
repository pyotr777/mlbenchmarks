import argparse, time, json

import torch
import torch.nn as nn
from torch.autograd import Variable
from torch.nn.utils.rnn import pack_padded_sequence

from tensorboardX import SummaryWriter

from src.data import load_mscoco, collate_gen_train, collate_gen_test
from src.model import ImgEncoder, Converter, CapGenerator
from src.util import save_checkpoint

torch.manual_seed(1)

def train(args, cfg):
    writer = SummaryWriter(comment=args.logger_comment)
    print("Logdir:",writer.file_writer.get_logdir())

    lr = 0
    if args.learning_rate is not None:
        lr = args.learning_rate
    else:
        lr = cfg['learning_rate']

    weight_decay = 0
    if args.weight_decay is not None:
        weight_decay = args.weight_decay
    else:
        weight_decay = cfg['weight_decay']

    loss_target = args.loss_target

    batch_size = 0
    if args.batch_size is not None:
        batch_size  = args.batch_size
    else:
        batch_size = cfg['batch_size']
    print("Hyper-parameters:\nBS={} LR={} WD={}".format(batch_size,lr,weight_decay))

    limit = None
    if args.use_samples > 0:
        limit = args.use_samples
    else:
        if "use_samples" in cfg:
            limit = cfg["use_samples"]

    print("Other parameters:\nTarget loss level={}, samples used={}".format(loss_target, limit))

    # Load data
    start_time = time.time()
    train_loader = torch.utils.data.DataLoader(
            load_mscoco(args.image_dir, args.train_file),
            batch_size = batch_size,
            shuffle=args.shuffle,
            collate_fn=collate_gen_train,
            num_workers=args.num_workers)
    if args.early_stopping:
        val_loader = torch.utils.data.DataLoader(
            load_mscoco(args.image_dir, args.val_file, dataset_type='test'),
            batch_size = batch_size,
            shuffle=False,
            collate_fn=collate_gen_test,
            num_workers=args.num_workers)


    # Set model
    model_name = "resnet50"
    if args.model:
        model_name = args.model

    print('Set model',model_name)
    encoder = ImgEncoder(model_name)
    # encoder = torch.nn.DataParallel(encoder).cuda()  # It only slows the learning process down.
    converter = Converter(cfg['img_dim'], cfg['hidden_dim'], cfg['num_layers'])
    generator = CapGenerator(
            cfg['embed_dim'],
            cfg['hidden_dim'],
            cfg['vocab_size'],
            cfg['num_layers'])
    if args.cuda:
        encoder.cuda()
        converter.cuda()
        generator.cuda()


    converter_optimizer = torch.optim.Adam(
            converter.parameters(),
            lr = lr,
            weight_decay = weight_decay)
    generator_optimizer = torch.optim.Adam(
            generator.parameters(),
            lr = lr,
            weight_decay = weight_decay)
    if cfg['scheduler_step_size']:
        converter_scheduler = torch.optim.lr_scheduler.StepLR(converter_optimizer, step_size=cfg['scheduler_step_size'], gamma=cfg['scheduler_gamma'])
        generator_scheduler = torch.optim.lr_scheduler.StepLR(generator_optimizer, step_size=cfg['scheduler_step_size'], gamma=cfg['scheduler_gamma'])
    criterion = nn.CrossEntropyLoss()

    # training
    print('Train model')
    cnt = 0
    best_score = 0.0
    maxsamples = 0
    score = 0
    if limit is not None:
        maxsamples = limit
        print("Using",maxsamples,"samples.")
    print('epoch, time (s), loss')
    timelimit_reached = False
    base_time = time.time()
    time_limit = args.time_limit
    print("Time limit:",time_limit)
    i = 0 # epoch counter
    while not timelimit_reached:
        start_time = time.time()
        loss_epoch = 0.0
        for j, (v, c_input, c_target, lengths) in enumerate(train_loader):
            samples = j * batch_size
            if maxsamples > 0 and samples > maxsamples:
                #print("epoch break at",samples,"samples")
                break
            v = Variable(v, requires_grad=False)
            c_input = Variable(c_input, requires_grad=False)
            c_target = Variable(c_target, requires_grad=False)
            if args.cuda:
                v, c_input, c_target = v.cuda(), c_input.cuda(), c_target.cuda()

            #encoder_optimizer.zero_grad()
            converter_optimizer.zero_grad()
            generator_optimizer.zero_grad()

            encoded_v = converter(encoder(v))
            outputs = generator(encoded_v, c_input, lengths)

            targets = pack_padded_sequence(c_target, lengths, batch_first=True)
            loss = criterion(outputs, targets.data)
            loss.backward()
            if cfg['max_norm'] > 0:
                torch.nn.utils.clip_grad_norm(converter.parameters(), cfg['max_norm'])
                torch.nn.utils.clip_grad_norm(generator.parameters(), cfg['max_norm'])
            #encoder_optimizer.step()
            converter_optimizer.step()
            generator_optimizer.step()

            loss_epoch += loss.data[0]
            loss_epoch = loss_epoch/2
            cnt += 1
            writer.add_scalar('Train/loss_iter', loss.data[0], cnt)


        writer.add_scalar('Train/loss_epoch', loss_epoch, i+1)
        print('{:d}, {:f}, {:f}'.format(i+1, time.time() - start_time, loss_epoch))
        if cfg['scheduler_step_size']:
            converter_scheduler.step()
            generator_scheduler.step()

        # Stop when max target loss or max epoch count is reached
        if loss_target is not None:
            if loss_epoch <= loss_target:
                print("Target loss reached.")
                break

        # Check execution time limit
        if time_limit is not None:
            elapsed = time.time() - base_time
            if elapsed >= time_limit:
                print("Time limit reached")
                timelimit_reached = True
            else:
                print("Elapsed: {}s".format(elapsed))

        i += 1

#        if i >= args.first_save and i % args.save_step == 0:
    best_score, score = save_checkpoint(args, cfg, i, j, cnt,
            encoder, converter, generator,
            converter_optimizer, generator_optimizer,
            val_loader, best_score)
    writer.add_scalar('Val/score', score, cnt)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--image_dir', type=str, default='./data/mscoco',
                        help='directory for resized images')
    parser.add_argument('--num_workers', type=int, default=8)
    parser.add_argument('--disable_cuda', action='store_true',
                    help='Disable CUDA')

    # for training
    parser.add_argument('--train_file', type=str, default='./data/train.enc.json',
                        help='directory for resized images')
    parser.add_argument('--model_dir', type=str, default='./model/gen',
                        help='path for saving trained models')
    parser.add_argument('--model_file', type=str, default='model',
                        help='path for saving trained models')
    parser.add_argument('--config_file', type=str, default='./config/model_gen.json',
                        help='path for saving trained models')
    parser.add_argument('--disable_shuffle', action='store_true',
                        help='Disable dataset shuffle')
    parser.add_argument('--max_epoch', type=int, default=10000,
                        help='dimension of word embedding vectors')
    parser.add_argument('--first_save', type=int , default=5,
                        help='step size for saving trained models')
    parser.add_argument('--save_step', type=int , default=5000,
                        help='step size for saving trained models')
    parser.add_argument('--logger_comment', type=str, default='_gen')
    parser.add_argument('-l','--learning_rate', type=float, default=0.0002)
    parser.add_argument('--weight_decay', type=float, default=0.0001)
    parser.add_argument('--model',type=str,default="resnet152")
    parser.add_argument('--use_samples',type=int, default=0, help="Limit number of samples to use for test and training")
    parser.add_argument('--loss_target', type=float, default=None)
    parser.add_argument('--time_limit', type=int, default=1800, help="Execution time limit in seconds")

    # for generate
    parser.add_argument('--val_file', type=str, default='./data/val.enc.json',
                        help='directory for resized images')
    parser.add_argument('--output_dir', type=str, default='./result/gen' ,
                        help='path for saving trained models')
    parser.add_argument('--early_stopping', action='store_true',
                        help='Disable dataset shuffle')
    parser.add_argument('--max_length', type=int, default=40)
    parser.add_argument('--batch_size', type=int, default=20)
    parser.add_argument('--metric_base', type=str, default='CIDEr')
    parser.add_argument('--beam_size', type=int, default=5)

    args = parser.parse_args()
    args.cuda = not args.disable_cuda and torch.cuda.is_available()
    args.shuffle = not args.disable_shuffle

    with open(args.config_file, 'r') as f:
        cfg = json.load(f)

    print(args)
    print(cfg)

    train(args, cfg)
