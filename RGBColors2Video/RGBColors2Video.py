import cv2
import numpy as np
from itertools import permutations
from argparse import ArgumentParser


def build_argparser():
    parser = ArgumentParser()
    parser.add_argument("-o",
                        "--output",
                        help="output path",
                        required=False,
                        default='out.avi',
                        type=str)
    parser.add_argument("-vw",
                        "--width",
                        help="Video Width",
                        required=False,
                        default=1920,
                        type=int)
    parser.add_argument("-vh",
                        "--height",
                        help="Video Height",
                        required=False,
                        default=1080,
                        type=int)
    parser.add_argument("-vf",
                        "--fps",
                        help="Video FPS",
                        required=False,
                        default=25,
                        type=int)
    return parser


if __name__ == '__main__':
    args = build_argparser().parse_args()
    vw = args.width
    vh = args.height
    th = 50
    vfps = args.fps

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    vwriter = cv2.VideoWriter(args.output, fourcc, vfps, (vw, vh))

    clist = list(permutations([0, 1, 2], 3))
    for (c1, c2, c3) in clist:
        img = np.zeros((vh, vw, 3), np.uint8)
        for ci in range(766):
            rvi = ci if ci <= 255 else 255
            gvi = ci % 255 if ci > 255 else 0
            gvi = 255 if ci >= 510 else gvi
            bvi = ci % 510 if ci > 510 else 0

            img[:, :, c1] = bvi
            img[:, :, c2] = gvi
            img[:, :, c3] = rvi
            text_str = f'R={img[0,0,2]} G={img[0,0,1]} B={img[0,0,0]}'
            img[:th, :, :] = 0
            cv2.putText(img, text_str, (10, 40), cv2.FONT_HERSHEY_DUPLEX, 1,
                        (255, 255, 255), 2)
            vwriter.write(img)
    vwriter.release()
