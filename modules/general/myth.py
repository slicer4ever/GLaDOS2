import glados
import os
import codecs
import re
import random


class Myth(glados.Module):

    def setup_memory(self):
        memory = self.get_memory()
        memory['data path'] = os.path.join(self.get_config_dir(), 'myths')
        if not os.path.exists(memory['data path']):
            os.makedirs(memory['data path'])

        memory['data file'] = os.path.join(memory['data path'], 'myths.txt')

    def get_help_list(self):
        return [
            glados.Help('myth', '[ID]', 'Returns a random myth. Botmods can specify an ID.'),
            glados.Help('addmyth', '<text>', 'Adds a myth to the mythical database'),
            glados.Help('delmyth', '<ID> [ID 2] [ID 3]...', 'Delete offending myths'),
            glados.Help('mythstats', '', 'Displays statistics on myths')
        ]

    @glados.Module.commands('addmyth')
    def addmyth(self, message, content):
        if content == '':
            yield from self.provide_help('addmyth', message)
            return

        author = message.author.name

        if len(content) < 10:
            yield from self.client.send_message(message.channel, 'Good myths are longer')
            return ()

        new_id = 1
        memory = self.get_memory()
        if os.path.isfile(memory['data file']):
            with codecs.open(memory['data file'], 'r', encoding='utf-8') as f:
                lines = [x for x in f.readlines() if len(x) > 2]
                if len(lines) > 0:
                    last_line = lines[-1]
                    parts = self.__extract_parts(last_line)
                    new_id = int(parts[0]) + 1

        with codecs.open(memory['data file'], 'a', encoding='utf-8') as f:
            content = content.replace('\n', '\\n')
            f.write('{}:{}:{}\n'.format(new_id, content, author))

        yield from self.client.send_message(message.channel, 'Myth #{} added.'.format(new_id))

    @glados.Module.commands('delmyth')
    def delmyth(self, message, content):
        if content == '':
            yield from self.provide_help('delmyth', message)
            return

        is_mod = message.author.id in self.settings['moderators']['IDs'] or \
                 len(set(x.name for x in message.author.roles).intersection(
                     set(self.settings['moderators']['roles']))) > 0
        if not is_mod and not message.author.id in self.settings['admins']['IDs']:
            yield from self.client.send_message(message.channel, 'Only botmods can delete myths')
            return ()

        memory = self.get_memory()
        if not os.path.isfile(memory['data file']):
            yield from self.client.send_message(message.channel, 'Myth dB does not exist')
            return

        with codecs.open(memory['data file'], 'r', encoding='utf-8') as f:
            lines = f.readlines()
            replace_lines = list()
            if len(lines) == 0:
                yield from self.client.send_message(message.channel, 'All myths have been deleted')
                return ()
            for line in lines:
                parts = self.__extract_parts(line)
                if not parts[0] in content.split():
                    replace_lines.append(line)
                    continue
                offender = parts[2]
                deleter = message.author.name
                yield from self.client.send_message(message.channel, 'Myth #{} by {} was deleted by {}'.format(
                    parts[0], offender, deleter))

        # overwrite with filtered list of lines
        with codecs.open(memory['data file'], 'w', encoding='utf-8') as f:
            f.writelines(replace_lines)

    @glados.Module.commands('myth')
    def myth(self, message, content):
        memory = self.get_memory()
        with codecs.open(memory['data file'], 'r', encoding='utf-8') as f:
            lines = f.readlines()

        if len(lines) == 0:
            yield from self.client.send_message(message.channel, 'No myths in dB')
            return

        # Extract a specific ID if you are a botmod
        if len(content) > 0:
            is_mod = message.author.id in self.settings['moderators']['IDs'] or \
                     len(set(x.name for x in message.author.roles).intersection(
                         set(self.settings['moderators']['roles']))) > 0
            if not is_mod and not message.author.id in self.settings['admins']['IDs']:
                yield from self.client.send_message(message.channel, 'Only botmods can pass IDs')
                return ()

            line = ''
            for l in lines:
                parts = self.__extract_parts(l)
                if parts[0] == content.strip():
                    line = l
                    break
            if line == '':
                yield from self.client.send_message(message.channel, 'Myth #{} does not exist'.format(content.strip()))
                return
        else:
            line = random.choice(lines)

        parts = self.__extract_parts(line)
        line = 'Myth #{}: "{}" -- *Submitted by {}*'.format(parts[0], parts[1], parts[2])

        yield from self.client.send_message(message.channel, line)

    @glados.Module.commands('mythstats')
    def mythstats(self, message, content):
        memory = self.get_memory()
        if os.path.isfile(memory['data file']):
            with codecs.open(memory['data file'], 'r', encoding='utf-8') as f:
                lines = [x for x in f.readlines() if len(x) > 2]
                count = len(lines)
                last_id = count
                if len(lines) > 0:
                    last_line = lines[-1]
                    parts = self.__extract_parts(last_line)
                    last_id = int(parts[0])
            yield from self.client.send_message(message.channel, 'There are {} active myths submitted ({} were deleted)'.format(count, last_id - count))
        else:
            yield from self.client.send_message(message.channel, 'No myths.')

    def __extract_parts(self, line):
        mentioned_ids = [x.strip('<@!>') for x in re.findall('<@!?[0-9]+>', line)]
        for id in mentioned_ids:
            for member in self.client.get_all_members():
                if member.id == id:
                    line = line.replace('<@{}>'.format(id), member.name).replace('<@!{}>'.format(id), member.name)
                    break

        bad_parts = line.split(':')
        parts = [
            bad_parts[0],
            ':'.join(bad_parts[1:-1]),
            bad_parts[-1].strip()
        ]

        parts[1] = parts[1].replace('\\n', '\n')
        return parts
