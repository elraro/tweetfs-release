from bitstring import BitArray
import os, sys
from glob import glob
import re

from util import assert_type

class Concealer(object):
    def __init__(self):
        self.context = 2
        self.model = self.create_model()
        self.size = len(self.model)
        print str(self.size)
        print "----"

    def create_model(self):
        print 'creating model phrases',
        sys.stdout.flush()
        filenames = glob(os.path.expanduser('./texts/*.txt'))
        text = ' '.join(map(lambda fn: open(fn, 'r').read(), filenames))

        print 'loading file into model... '
        sys.stdout.flush()

        model = text.split(".")
        model = [re.sub('[^A-Za-z0-9 ]+', '', phrase.lstrip().rstrip()) for phrase in model]
        #model = [phrase.lstrip().rstrip().replace("\r\n", "\n").replace("\n\n", "\n").replace("\n\n\n", "\n").replace("\n\n\n\n", "\n") for phrase in model]
        model = [((phrase[:70] + '..') if len(phrase) > 70 else phrase) for phrase in model]
        print 'done'
        return model

    def conceal(self, cleartext, do_test=True):
        assert_type(cleartext, BitArray, 'conceal input')
        byte_text = cleartext.tobytes()
        ciphertext = []
        for i in range(0, len(byte_text), 2):
            try:
                ciphertext.append(self.model[int(str(ord(byte_text[i])*1000 + ord(byte_text[i + 1])))])
            except IndexError:
                ciphertext.append(self.model[int(str(ord(byte_text[i])))])
        if do_test:
            sink = open('/dev/null', 'w')
            out, err  = sys.stdout, sys.stderr
            sys.stdout, sys.stderr = sink, sink
            test = self.reveal(ciphertext, do_test=False)
            sys.stdout, sys.stderr = out, err
            sink.close()
            if test != cleartext:
                raise RuntimeError('conceal+reveal did not produce expected output')
        print 'concealed cleartext, output is %s bytes' % len(ciphertext)
        return ciphertext

    def reveal(self, ciphertext, do_test=True):
        cleartext = ""
        for i in range(0, len(ciphertext)):
            phrase = ciphertext[i]
            value = self.model.index(phrase)
            size = len(str(value))
            if size >= 4:
                number1 = str(value)[:-3]
                number2 = str(value)[-3:]
                cleartext += chr(int(number1)).encode("hex") + chr(int(number2)).encode("hex")
            else:
                if value == 0 and i != len(ciphertext)-1:
                    cleartext += chr(value).encode("hex") + chr(value).encode("hex")
                elif value == 0 and i == len(ciphertext)-1:
                    cleartext += chr(value).encode("hex")
                else:
                    cleartext += chr(0).encode("hex") + chr(value).encode("hex")
        cleartext = '0x' + cleartext
        cleartext = BitArray(cleartext)
        assert_type(cleartext, BitArray, 'reveal output')
        if do_test:
            sink = open('/dev/null', 'w')
            out, err  = sys.stdout, sys.stderr
            sys.stdout, sys.stderr = sink, sink
            test = self.conceal(cleartext, do_test=False)
            sys.stdout, sys.stderr = out, err
            sink.close()
            if test != ciphertext:
                raise RuntimeError('reveal+conceal did not produce expected output')
        print 'revealed ciphertext, output is %s bytes' % len(cleartext)
        return cleartext
