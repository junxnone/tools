import six
from google.cloud import translate_v2 as translate
from argparse import ArgumentParser


class google_translator():
    def __init__(self, target):
        self.translate_client = translate.Client()
        self.target = target

    def translate(self, text):
        if isinstance(text, six.binary_type):
            text = text.decode("utf-8")

        result = self.translate_client.translate(text,
                                                 target_language=self.target)
        return result

    def list_languages(self):
        results = self.translate_client.get_languages()

        for language in results:
            print(u"{name} ({language})".format(**language))


def build_argparser():
    parser = ArgumentParser()
    parser.add_argument("-i",
                        "--input",
                        help="input words",
                        required=False,
                        default='apple',
                        type=str)

    return parser


if __name__ == '__main__':
    args = build_argparser().parse_args()
    gt = google_translator('zh-cn')
    t_result = gt.translate(args.input)
    print(u"Text: {}".format(t_result["input"]))
    print(u"Translation: {}".format(t_result["translatedText"]))
    print(u"Detected source language: {}".format(
        t_result["detectedSourceLanguage"]))
