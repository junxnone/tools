import os
import sys
import cv2
import numpy as np
from argparse import ArgumentParser


def build_argparser():
    parser = ArgumentParser()
    parser.add_argument("-i",
                        "--input",
                        help="input image path",
                        required=True,
                        default='input',
                        type=str)
    parser.add_argument("-o",
                        "--output",
                        help="output path",
                        required=False,
                        default='out.avi',
                        type=str)
    parser.add_argument("-vh",
                        "--height",
                        help="video height",
                        required=False,
                        default=1080,
                        type=int)
    parser.add_argument("-vw",
                        "--width",
                        help="video width",
                        required=False,
                        default=1920,
                        type=int)
    parser.add_argument("-vf",
                        "--fps",
                        help="video fps",
                        required=False,
                        default=25,
                        type=int)
    parser.add_argument("-vp",
                        "--padding",
                        help="video padding",
                        required=False,
                        default=False,
                        type=bool)
    return parser


if __name__ == '__main__':
    args = build_argparser().parse_args()
    if not os.path.exists(args.input):
        log.error('invalid input image path')
        sys.exit(1)
    if not os.path.isdir(args.input):
        log.error('invalid input image path')
        sys.exit(1)

    img_path_list = []
    for img_name in sorted(os.listdir(args.input)):
        img_path = os.path.join(args.input, img_name)
        img_path_list.append(img_path)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    writer = cv2.VideoWriter(args.output, fourcc, args.fps,
                             (args.width, args.height))

    for img_path in img_path_list:
        img = cv2.imread(img_path)
        if args.padding is True:
            pad_img = np.zeros((args.height, args.width, 3), dtype=np.uint8)
            h, w, _ = img.shape
            pad_img[:h, :w, :] = img[:h, :w, :]
            img = pad_img
        else:
            img = cv2.resize(img, (args.width, args.height))

        writer.write(img)
    writer.release()
