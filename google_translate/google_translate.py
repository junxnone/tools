import six
from google.cloud import translate_v2 as translate
from google.cloud import translate_v2 as translate
from google.cloud import storage
from argparse import ArgumentParser


def translate_text(target, text):
    from google.cloud import translate_v2 as translate

    translate_client = translate.Client()

    if isinstance(text, six.binary_type):
        text = text.decode("utf-8")

    result = translate_client.translate(text, target_language=target)
    return result


def translate_en2cn(text):
    return translate_text('zh-cn', text)


def list_languages():

    translate_client = translate.Client()

    results = translate_client.get_languages()

    for language in results:
        print(u"{name} ({language})".format(**language))


def implicit():
    storage_client = storage.Client()

    buckets = list(storage_client.list_buckets())
    print(buckets)


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
    t_result = translate_en2cn(args.input)
    print(u"Text: {}".format(t_result["input"]))
    print(u"Translation: {}".format(t_result["translatedText"]))
    print(u"Detected source language: {}".format(
        t_result["detectedSourceLanguage"]))
