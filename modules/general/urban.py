import json
import glados
import urllib.request
import urllib.parse

UD_URL = 'http://api.urbandictionary.com/v0/define?term='


class Urban(glados.Module):

    def get_help_list(self):
        return [
            glados.Help('urban', '<term>', 'Look up a term on urban dictionary.')
        ]

    @staticmethod
    def get_def(word):
        url = UD_URL + urllib.parse.quote(word)
        resp = json.loads(urllib.request.urlopen(url).read().decode("utf-8"))
        if resp['result_type'] == 'no_results':
            definition = 'Definition {} not found!'.format(word)
        else:
            try:
                item = resp['list'][0]['definition']
                thumbsup = resp['list'][0]['thumbs_up']
                thumbsdown = resp['list'][0]['thumbs_down']
                points = str(int(thumbsup) - int(thumbsdown))
                definition = 'Definition: ' + str(item) + ' >> Points: ' + points + ' (03' + str(thumbsup) + '|05' + str(thumbsdown) + ')'
            except IndexError:
                definition = ('Definition entry %s does'
                              'not exist for \'%s\'.' % (1, word))
        return definition

    @glados.Module.commands('urban', 'ud')
    def urban(self, message, content):
        if content == '':
            yield from self.provide_help('urban', message)
            return
        definition = self.get_def(content)
        yield from self.client.send_message(message.channel, definition)
